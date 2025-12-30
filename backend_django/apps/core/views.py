from __future__ import annotations

import re
import time

from botocore.exceptions import ClientError
from django.conf import settings
from django.db import connection
from django.http import JsonResponse
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.core.models import HeroSliderImage, SiteSettings
from apps.files.minio_client import presign_get, s3_client


class IsAdmin(IsAuthenticated):
    """Permission class to check if user is admin (duplicated to avoid cross-app imports)."""

    def has_permission(self, request, view):
        from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

        if not request.user or not hasattr(request.user, "id"):
            raise AuthenticationFailed("Учетные данные не были предоставлены.")
        if not hasattr(request.user, "role"):
            raise PermissionDenied("Пользователь не имеет роли.")
        if request.user.role != "admin":
            raise PermissionDenied("Требуется роль администратора.")
        return True


def _ensure_site_settings_row() -> SiteSettings | None:
    """
    Ensure singleton row exists. Returns SiteSettings or None if table doesn't exist yet.
    """
    try:
        row = SiteSettings.objects.filter(id=1).first()
        if row:
            return row
        return SiteSettings.objects.create(id=1)
    except Exception:
        # likely table doesn't exist yet
        return None


def _create_table_if_missing():
    """
    Best-effort schema bootstrap. This repo often uses managed=False models and
    management commands instead of migrations.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS site_settings (
                id INTEGER PRIMARY KEY,
                hero_background_image VARCHAR(500),
                created_at TIMESTAMP DEFAULT NOW(),
                updated_at TIMESTAMP DEFAULT NOW()
            );
            """
        )
        cursor.execute("INSERT INTO site_settings (id) VALUES (1) ON CONFLICT (id) DO NOTHING;")


def _sanitize_filename(name: str) -> str:
    name = (name or "image").strip()
    name = name.replace("\\", "_").replace("/", "_")
    name = re.sub(r"[^a-zA-Z0-9.\-_]+", "_", name)
    name = re.sub(r"_+", "_", name)
    return name[:120] or "image"


class HeroImageView(APIView):
    """
    GET  /site/hero-image     (AllowAny) -> { image_key, url }
    PUT  /site/hero-image     (IsAdmin)  -> accepts either:
      - multipart/form-data with file
      - JSON { key: "hero/..." } to bind already uploaded object
    """

    def get(self, _request):
        row = _ensure_site_settings_row()
        if not row:
            # Table not created yet: return fallback
            return JsonResponse({"image_key": None, "url": None})

        key = (row.hero_background_image or "").lstrip("/") or None
        if not key:
            return JsonResponse({"image_key": None, "url": None})

        try:
            url = presign_get(key, expires_in=60 * 60 * 24 * 7)
            return JsonResponse({"image_key": key, "url": url})
        except ClientError:
            # If object missing or minio issue, do not break public page
            return JsonResponse({"image_key": key, "url": None})

    def put(self, request):
        self.permission_classes = [IsAdmin]
        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                return JsonResponse({"error": "Forbidden"}, status=403)

        # Ensure schema exists (best-effort)
        _create_table_if_missing()
        row = _ensure_site_settings_row()
        if not row:
            return JsonResponse({"error": "Site settings not initialized"}, status=500)

        file_obj = request.FILES.get("file")
        key_from_body = request.data.get("key")

        if file_obj is None and not key_from_body:
            return JsonResponse({"error": "Missing file or key"}, status=400)

        # Case A: file upload via backend
        if file_obj is not None:
            content_type = getattr(file_obj, "content_type", None) or "application/octet-stream"
            if not content_type.startswith("image/"):
                return JsonResponse({"error": "Only image uploads are allowed"}, status=400)

            max_size = 20 * 1024 * 1024  # 20MB
            if getattr(file_obj, "size", 0) > max_size:
                return JsonResponse({"error": "File is too large (max 20MB)"}, status=400)

            safe_name = _sanitize_filename(getattr(file_obj, "name", "image"))
            key = f"hero/{int(time.time())}_{safe_name}"

            client = s3_client()
            try:
                client.upload_fileobj(
                    file_obj,
                    settings.MINIO_BUCKET,
                    key,
                    ExtraArgs={"ContentType": content_type},
                )
            except ClientError as e:
                code = (e.response.get("Error") or {}).get("Code")
                message = (e.response.get("Error") or {}).get("Message", "Upload failed")
                return JsonResponse({"error": f"Upload failed: {code} - {message}"}, status=500)

            row.hero_background_image = key
            row.save(update_fields=["hero_background_image"])

            url = presign_get(key, expires_in=60 * 60 * 24 * 7, response_content_type=content_type)
            return JsonResponse({"ok": True, "image_key": key, "url": url})

        # Case B: bind existing MinIO object key
        key = str(key_from_body).lstrip("/")
        if not key.startswith("hero/"):
            return JsonResponse({"error": "Key must start with 'hero/'"}, status=400)

        row.hero_background_image = key
        row.save(update_fields=["hero_background_image"])
        url = presign_get(key, expires_in=60 * 60 * 24 * 7)
        return JsonResponse({"ok": True, "image_key": key, "url": url})


class HeroSliderView(APIView):
    """
    GET  /site/hero-slider     (AllowAny) -> { items: [{ id, key, url, orderIndex }] }
    PUT  /site/hero-slider     (IsAdmin)  -> { keys: ["hero/...", ...] } replace all
    """

    permission_classes = [AllowAny]

    def get(self, _request):
        try:
            # Check if table exists by trying a simple query
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM hero_slider_images LIMIT 1")
        except Exception:
            # Table doesn't exist yet
            return JsonResponse({"items": []})

        try:
            items = list(
                HeroSliderImage.objects.filter(is_active=True)
                .order_by("order_index", "id")
                .values("id", "key", "order_index")
            )
            result = []
            for item in items:
                key = (item["key"] or "").lstrip("/")
                if not key:
                    continue
                try:
                    url = presign_get(key, expires_in=60 * 60 * 24 * 7)
                except (ClientError, Exception) as e:
                    # If presigned URL fails, skip this item
                    continue
                result.append(
                    {
                        "id": item["id"],
                        "key": key,
                        "url": url,
                        "orderIndex": item["order_index"],
                    }
                )
            return JsonResponse({"items": result})
        except Exception as e:
            # Log error but return empty list to not break frontend
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error loading hero slider: {e}")
            return JsonResponse({"items": []})

    def put(self, request):
        self.permission_classes = [IsAdmin]
        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                return JsonResponse({"error": "Forbidden"}, status=403)

        keys = request.data.get("keys", [])
        if not isinstance(keys, list):
            return JsonResponse({"error": "keys must be a list"}, status=400)

        # Validate all keys
        validated_keys = []
        for key in keys:
            key_str = str(key).lstrip("/")
            if not key_str.startswith("hero/"):
                return JsonResponse({"error": f"Key must start with 'hero/': {key_str}"}, status=400)
            validated_keys.append(key_str)

        # Ensure table exists
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM hero_slider_images LIMIT 1")
        except Exception:
            # Table doesn't exist, create it
            try:
                from pathlib import Path
                sql_path = Path(__file__).resolve().parents[1] / "management" / "hero_slider_schema.sql"
                if sql_path.exists():
                    sql = sql_path.read_text(encoding="utf-8")
                    with connection.cursor() as cursor:
                        cursor.execute(sql)
                else:
                    # Fallback: create table directly
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS hero_slider_images (
                                id SERIAL PRIMARY KEY,
                                key VARCHAR(500) NOT NULL,
                                order_index INTEGER DEFAULT 0,
                                is_active BOOLEAN DEFAULT TRUE,
                                created_at TIMESTAMP DEFAULT NOW(),
                                updated_at TIMESTAMP DEFAULT NOW()
                            );
                            CREATE INDEX IF NOT EXISTS idx_hero_slider_order ON hero_slider_images(order_index, is_active);
                        """)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to create hero_slider_images table: {e}")
                return JsonResponse({"error": "Database table not initialized. Please run: python manage.py apply_hero_slider_schema"}, status=500)

        # Atomic replace: delete all, then insert new ones
        try:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM hero_slider_images;")
                for idx, key in enumerate(validated_keys):
                    cursor.execute(
                        """
                        INSERT INTO hero_slider_images (key, order_index, is_active, created_at, updated_at)
                        VALUES (%s, %s, TRUE, NOW(), NOW())
                        """,
                        [key, idx],
                    )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating hero slider: {e}")
            return JsonResponse({"error": "Database error"}, status=500)

        # Return updated list
        try:
            items = list(
                HeroSliderImage.objects.filter(is_active=True)
                .order_by("order_index", "id")
                .values("id", "key", "order_index")
            )
            result = []
            for item in items:
                key = (item["key"] or "").lstrip("/")
                if not key:
                    continue
                try:
                    url = presign_get(key, expires_in=60 * 60 * 24 * 7)
                except (ClientError, Exception):
                    url = None
                result.append(
                    {
                        "id": item["id"],
                        "key": key,
                        "url": url,
                        "orderIndex": item["order_index"],
                    }
                )
            return JsonResponse({"ok": True, "items": result})
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error returning hero slider list after update: {e}")
            # Return success with empty list if we can't fetch
            return JsonResponse({"ok": True, "items": []})


class HeroSliderUploadView(APIView):
    """
    POST /site/hero-slider/upload  (IsAdmin) -> multipart/form-data with files[]
    Returns: { uploaded: [{ key, url }] }
    """

    permission_classes = [IsAdmin]

    def post(self, request):
        files = request.FILES.getlist("files[]") or request.FILES.getlist("files")
        if not files:
            return JsonResponse({"error": "No files provided"}, status=400)

        max_size = 20 * 1024 * 1024  # 20MB per file
        uploaded = []

        client = s3_client()
        for file_obj in files:
            content_type = getattr(file_obj, "content_type", None) or "application/octet-stream"
            if not content_type.startswith("image/"):
                continue  # Skip non-images

            if getattr(file_obj, "size", 0) > max_size:
                continue  # Skip too large files

            safe_name = _sanitize_filename(getattr(file_obj, "name", "image"))
            key = f"hero/{int(time.time())}_{safe_name}"

            try:
                client.upload_fileobj(
                    file_obj,
                    settings.MINIO_BUCKET,
                    key,
                    ExtraArgs={"ContentType": content_type},
                )
                url = presign_get(key, expires_in=60 * 60 * 24 * 7, response_content_type=content_type)
                uploaded.append({"key": key, "url": url})
            except ClientError as e:
                code = (e.response.get("Error") or {}).get("Code")
                message = (e.response.get("Error") or {}).get("Message", "Upload failed")
                # Log but continue with other files
                continue

        if not uploaded:
            return JsonResponse({"error": "No files were uploaded"}, status=400)

        return JsonResponse({"uploaded": uploaded})


class HeroSliderLoadFromPublicView(APIView):
    """
    POST /site/hero-slider/load-from-public  (IsAdmin) -> Load images from public/slider folder
    Returns: { uploaded: [{ key, url }], count: int }
    """

    permission_classes = [IsAdmin]

    def post(self, request):
        from pathlib import Path
        import os
        from django.conf import settings

        # Try to find public/slider folder
        # Path could be relative to project root or absolute
        possible_paths = [
            Path("/app/public/slider"),  # Docker container path (mounted volume)
            Path(__file__).resolve().parents[3] / "public" / "slider",  # From backend_django/apps/core/views.py -> edu_atg/public/slider
            Path(__file__).resolve().parents[4] / "public" / "slider",  # Alternative depth
            Path("/app/../public/slider"),  # Alternative Docker path
        ]

        slider_path = None
        for path in possible_paths:
            if path.exists() and path.is_dir():
                slider_path = path
                break

        if not slider_path:
            return JsonResponse({"error": "public/slider folder not found"}, status=404)

        # Find all image files
        image_extensions = {".webp", ".jpg", ".jpeg", ".png", ".gif"}
        image_files = []
        for file_path in slider_path.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                image_files.append(file_path)

        if not image_files:
            return JsonResponse({"error": "No image files found in public/slider"}, status=404)

        # Upload to MinIO
        client = s3_client()
        uploaded = []
        max_size = 20 * 1024 * 1024  # 20MB

        for file_path in image_files:
            try:
                file_size = file_path.stat().st_size
                if file_size > max_size:
                    continue  # Skip too large files

                # Determine content type
                ext = file_path.suffix.lower()
                content_type_map = {
                    ".webp": "image/webp",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".png": "image/png",
                    ".gif": "image/gif",
                }
                content_type = content_type_map.get(ext, "image/webp")

                # Create key
                safe_name = _sanitize_filename(file_path.name)
                key = f"hero/{int(time.time())}_{safe_name}"

                # Upload file
                with open(file_path, "rb") as f:
                    client.upload_fileobj(
                        f,
                        settings.MINIO_BUCKET,
                        key,
                        ExtraArgs={"ContentType": content_type},
                    )

                url = presign_get(key, expires_in=60 * 60 * 24 * 7, response_content_type=content_type)
                uploaded.append({"key": key, "url": url})

            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error uploading {file_path.name}: {e}")
                continue

        if not uploaded:
            return JsonResponse({"error": "No files were uploaded"}, status=400)

        return JsonResponse({"uploaded": uploaded, "count": len(uploaded)})


