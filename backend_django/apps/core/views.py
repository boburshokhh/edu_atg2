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

        # Atomic replace: delete all, then insert new ones
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

        # Return updated list
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
            except ClientError:
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


