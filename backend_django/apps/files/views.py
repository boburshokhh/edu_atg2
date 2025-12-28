from __future__ import annotations

import mimetypes
import re

from botocore.exceptions import ClientError
from django.conf import settings
from django.http import JsonResponse, StreamingHttpResponse
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.files.hls import is_ffmpeg_available, transcode_mp4_to_hls
from apps.files.minio_client import presign_get, presign_put, s3_client
from apps.files.models import VideoTranscodeJob
from apps.stations.views import IsAdmin


_RANGE_RE = re.compile(r"bytes=(\d+)-(\d+)?")


class PresignDownloadView(APIView):
    # Presigned GET links are used for public pages (stations, materials previews).
    # Keep other file operations authenticated.
    permission_classes = [AllowAny]

    def get(self, request):
        import logging
        logger = logging.getLogger(__name__)
        
        key = request.query_params.get("key")
        if not key:
            return JsonResponse({"error": "Missing key"}, status=400)
        
        # Normalize key: remove leading slashes
        key = key.lstrip("/")
        
        try:
            content_type = request.query_params.get("contentType") or None
            expires_in = int(request.query_params.get("expiresIn") or 60 * 60 * 24 * 7)
            
            # Validate expires_in to prevent too large values
            if expires_in > 60 * 60 * 24 * 7:  # Max 7 days
                expires_in = 60 * 60 * 24 * 7
            
            logger.debug(f"[Presign] Generating presigned URL for key: {key}, expires_in: {expires_in}")
            url = presign_get(key, expires_in=expires_in, response_content_type=content_type)
            
            if not url:
                logger.error(f"[Presign] Failed to generate presigned URL for key: {key}")
                return JsonResponse({"error": "Failed to generate presigned URL"}, status=500)
            
            logger.debug(f"[Presign] Successfully generated presigned URL for key: {key}")
            return JsonResponse({"url": url})
            
        except ClientError as e:
            code = (e.response.get("Error") or {}).get("Code")
            message = (e.response.get("Error") or {}).get("Message", "Unknown error")
            logger.error(f"[Presign] MinIO ClientError for key {key}: {code} - {message}")
            
            if code in ("NoSuchKey", "404", "NotFound"):
                return JsonResponse({"error": "File not found"}, status=404)
            elif code == "InvalidAccessKeyId":
                return JsonResponse({
                    "error": "MinIO configuration error. Please check MINIO_ACCESS_KEY and MINIO_SECRET_KEY."
                }, status=500)
            elif code == "SignatureDoesNotMatch":
                return JsonResponse({
                    "error": "MinIO authentication error. Please check MINIO_SECRET_KEY."
                }, status=500)
            else:
                return JsonResponse({"error": f"MinIO error: {code} - {message}"}, status=500)
                
        except ValueError as e:
            logger.error(f"[Presign] Invalid parameter for key {key}: {e}")
            return JsonResponse({"error": f"Invalid parameter: {str(e)}"}, status=400)
            
        except Exception as e:
            logger.exception(f"[Presign] Unexpected error for key {key}: {e}")
            return JsonResponse({"error": "Internal server error"}, status=500)


class PresignUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        key = request.data.get("key")
        if not key:
            return JsonResponse({"error": "Missing key"}, status=400)
        content_type = request.data.get("contentType") or None
        expires_in = int(request.data.get("expiresIn") or 900)
        url = presign_put(key, content_type=content_type, expires_in=expires_in)
        return JsonResponse({"url": url})


class FolderContentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        prefix = (request.query_params.get("prefix") or "").lstrip("/")
        clean_prefix = prefix.rstrip("/")
        list_prefix = f"{clean_prefix}/" if clean_prefix else ""

        client = s3_client()
        response = client.list_objects_v2(
            Bucket=settings.MINIO_BUCKET,
            Prefix=list_prefix,
            Delimiter="/",
            MaxKeys=1000,
        )

        folders = []
        for cp in response.get("CommonPrefixes", []) or []:
            p = (cp.get("Prefix") or "").rstrip("/")
            name = p.split("/")[-1] if p else ""
            if not name:
                continue
            folders.append({"name": name, "path": p, "isFolder": True})

        files = []
        for item in response.get("Contents", []) or []:
            key = item.get("Key")
            if not key or key.endswith("/"):
                continue
            file_name = key.split("/")[-1]
            content_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
            url = presign_get(key, expires_in=60 * 60 * 24 * 7, response_content_type=content_type)
            files.append(
                {
                    "objectName": key,
                    "fileName": file_name,
                    "originalName": file_name,
                    "original_name": file_name,
                    "size": item.get("Size"),
                    "file_size": item.get("Size"),
                    "type": content_type,
                    "url": url,
                    "file_url": url,
                    "lastModified": item.get("LastModified"),
                    "uploaded_at": item.get("LastModified"),
                }
            )

        return JsonResponse({"folders": folders, "files": files})


class StreamObjectView(APIView):
    """
    Secure streaming endpoint for PDF and other files from MinIO.
    Requires authentication and supports Range requests for efficient PDF.js loading.
    """
    permission_classes = [IsAuthenticated]

    def options(self, request, key: str):
        """Handle CORS preflight requests"""
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        response["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Range, Authorization, Content-Type"
        response["Access-Control-Max-Age"] = "86400"
        return response

    def get(self, request, key: str):
        import logging
        import urllib.parse
        logger = logging.getLogger(__name__)
        
        # Декодируем ключ из URL (frontend использует encodeURIComponent)
        try:
            # Django автоматически декодирует URL, но нужно обработать специальные случаи
            key = urllib.parse.unquote(key)
            key = key.lstrip("/")
        except Exception as e:
            logger.error(f"[StreamObjectView] Error decoding key: {e}")
            return JsonResponse({"error": "Invalid key format"}, status=400)
        
        if not key:
            return JsonResponse({"error": "Missing key"}, status=400)
        
        logger.debug(f"[StreamObjectView] Streaming file: {key}")
        
        client = s3_client()
        range_header = request.headers.get("Range")

        extra = {}
        status_code = 200
        content_range = None

        # Поддержка Range requests для PDF.js (partial content)
        if range_header:
            m = _RANGE_RE.match(range_header)
            if m:
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) is not None else None
                extra["Range"] = f"bytes={start}-{'' if end is None else end}"
                status_code = 206
                logger.debug(f"[StreamObjectView] Range request: {start}-{end}")

        try:
            # Получаем объект из MinIO
            obj = client.get_object(Bucket=settings.MINIO_BUCKET, Key=key, **extra)
        except ClientError as e:
            code = (e.response.get("Error") or {}).get("Code")
            logger.error(f"[StreamObjectView] MinIO error for key {key}: {code}")
            if code in ("NoSuchKey", "404", "NotFound"):
                return JsonResponse({"error": "File not found"}, status=404)
            return JsonResponse({"error": "Failed to retrieve file"}, status=500)
        except Exception as e:
            logger.exception(f"[StreamObjectView] Unexpected error for key {key}: {e}")
            return JsonResponse({"error": "Internal server error"}, status=500)

        body = obj["Body"]
        
        # Определяем Content-Type: приоритет у метаданных MinIO, затем по расширению
        content_type = obj.get("ContentType")
        if not content_type or content_type == "binary/octet-stream":
            # Определяем по расширению файла
            guessed_type, _ = mimetypes.guess_type(key)
            if guessed_type:
                content_type = guessed_type
            elif key.lower().endswith('.pdf'):
                content_type = "application/pdf"
            else:
                content_type = "application/octet-stream"
        
        content_length = obj.get("ContentLength")

        # Вычисляем Content-Range для partial content responses
        total_size = None
        if status_code == 206:
            try:
                head = client.head_object(Bucket=settings.MINIO_BUCKET, Key=key)
                total_size = head.get("ContentLength")
            except Exception:
                total_size = content_length

        if status_code == 206 and total_size is not None and range_header:
            m = _RANGE_RE.match(range_header)
            if m:
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) is not None else (total_size - 1)
                content_range = f"bytes {start}-{end}/{total_size}"

        # Создаем streaming response
        resp = StreamingHttpResponse(body, status=status_code, content_type=content_type)
        
        # Заголовки для поддержки Range requests и кэширования
        resp["Accept-Ranges"] = "bytes"
        if content_length is not None:
            resp["Content-Length"] = str(content_length)
        if content_range:
            resp["Content-Range"] = content_range
        
        # CORS заголовки для streaming responses (важно для PDF.js)
        resp["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        resp["Access-Control-Allow-Methods"] = "GET, HEAD, OPTIONS"
        resp["Access-Control-Allow-Headers"] = "Range, Authorization, Content-Type"
        resp["Access-Control-Expose-Headers"] = "Content-Length, Content-Range, Accept-Ranges"
        
        # Кэширование для оптимизации (не кэшируем PDF для безопасности)
        if content_type == "application/pdf":
            resp["Cache-Control"] = "private, no-cache, no-store, must-revalidate"
            resp["Pragma"] = "no-cache"
            resp["Expires"] = "0"
        else:
            resp["Cache-Control"] = "public, max-age=3600"
        
        logger.debug(f"[StreamObjectView] Streaming {content_type} file: {key}, size: {content_length}")
        return resp


class HlsObjectView(APIView):
    """
    Public proxy for HLS playlists and segments stored in MinIO.
    Important: HLS playlists contain relative segment URLs; presigned URLs break that,
    so we serve via a stable Django path that can resolve relative references.
    """

    permission_classes = [AllowAny]

    def get(self, request, key: str):
        key = key.lstrip("/")
        client = s3_client()
        range_header = request.headers.get("Range")

        extra = {}
        status_code = 200
        content_range = None

        if range_header:
            m = _RANGE_RE.match(range_header)
            if m:
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) is not None else None
                extra["Range"] = f"bytes={start}-{'' if end is None else end}"
                status_code = 206

        try:
            obj = client.get_object(Bucket=settings.MINIO_BUCKET, Key=key, **extra)
        except ClientError as e:
            code = (e.response.get("Error") or {}).get("Code")
            if code in ("NoSuchKey", "404", "NotFound"):
                return JsonResponse({"error": "Not found"}, status=404)
            return JsonResponse({"error": "Not found"}, status=404)

        body = obj["Body"]
        content_type = obj.get("ContentType") or mimetypes.guess_type(key)[0] or "application/octet-stream"
        content_length = obj.get("ContentLength")

        total_size = None
        try:
            head = client.head_object(Bucket=settings.MINIO_BUCKET, Key=key)
            total_size = head.get("ContentLength")
        except Exception:
            total_size = None

        if status_code == 206 and total_size is not None and range_header:
            m = _RANGE_RE.match(range_header)
            if m:
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) is not None else (total_size - 1)
                content_range = f"bytes {start}-{end}/{total_size}"

        resp = StreamingHttpResponse(body, status=status_code, content_type=content_type)
        resp["Accept-Ranges"] = "bytes"
        if content_length is not None:
            resp["Content-Length"] = str(content_length)
        if content_range:
            resp["Content-Range"] = content_range
        # Allow browsers to cache segments for better UX on slow networks
        resp["Cache-Control"] = "public, max-age=3600"
        return resp


class TranscodeHlsView(APIView):
    """
    Admin endpoint: create an async HLS transcode job for an uploaded MP4 in MinIO.
    It updates the target record (promo_video or topic_file) when finished.
    """

    permission_classes = [IsAdmin]

    def post(self, request):
        if not is_ffmpeg_available():
            return JsonResponse(
                {
                    "error": "ffmpeg is not installed on the backend host. Install ffmpeg and restart the backend to enable HLS transcoding."
                },
                status=501,
            )
        target_type = request.data.get("targetType")
        target_id = request.data.get("targetId")
        station_id = request.data.get("stationId")
        source_key = request.data.get("sourceKey")

        if not target_type or not target_id or not source_key:
            return JsonResponse({"error": "Missing targetType/targetId/sourceKey"}, status=400)

        try:
            target_id = int(target_id)
        except Exception:
            return JsonResponse({"error": "Invalid targetId"}, status=400)

        station_id_int = None
        if station_id is not None:
            try:
                station_id_int = int(station_id)
            except Exception:
                station_id_int = None

        job = VideoTranscodeJob.objects.create(
            target_type=str(target_type),
            target_id=target_id,
            station_id=station_id_int,
            source_object_key=str(source_key).lstrip("/"),
            status="queued",
        )

        # Determine output prefix (stable; HLS playlists need relative URLs)
        output_prefix = f"videos/hls/{job.target_type}/{job.target_id}/{job.id}"

        import threading
        import traceback

        def _run():
            try:
                VideoTranscodeJob.objects.filter(id=job.id).update(status="processing")
                master_key = transcode_mp4_to_hls(job.source_object_key, output_prefix)

                # Update target DB record
                if job.target_type == "promo_video" and job.station_id:
                    from apps.stations.models import StationPromoVideo

                    StationPromoVideo.objects.filter(station_id=job.station_id, is_active=True).update(
                        object_key=master_key
                    )
                elif job.target_type == "topic_file":
                    from apps.courses.models import CourseProgramTopicFile

                    CourseProgramTopicFile.objects.filter(id=job.target_id).update(
                        object_key=master_key,
                        mime_type="application/vnd.apple.mpegurl",
                    )

                VideoTranscodeJob.objects.filter(id=job.id).update(
                    status="done",
                    master_object_key=master_key,
                    error=None,
                )
            except Exception as e:
                VideoTranscodeJob.objects.filter(id=job.id).update(
                    status="failed",
                    error=str(e)[:4000],
                )
                traceback.print_exc()

        threading.Thread(target=_run, daemon=True).start()

        return JsonResponse(
            {
                "jobId": job.id,
                "status": job.status,
                "outputPrefix": output_prefix,
            }
        )


class TranscodeJobView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, job_id: int):
        job = VideoTranscodeJob.objects.filter(id=job_id).values(
            "id",
            "target_type",
            "target_id",
            "station_id",
            "source_object_key",
            "master_object_key",
            "status",
            "error",
        ).first()
        if not job:
            return JsonResponse({"error": "Not found"}, status=404)
        return JsonResponse({"job": job})


class ExistsObjectView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        key = (request.query_params.get("key") or "").lstrip("/")
        if not key:
            return JsonResponse({"error": "Missing key"}, status=400)

        client = s3_client()
        try:
            head = client.head_object(Bucket=settings.MINIO_BUCKET, Key=key)
        except ClientError as e:
            code = (e.response.get("Error") or {}).get("Code")
            if code in ("NoSuchKey", "404", "NotFound"):
                return JsonResponse({"exists": False}, status=404)
            return JsonResponse({"error": "Failed to check object"}, status=500)

        return JsonResponse(
            {
                "exists": True,
                "key": key,
                "contentType": head.get("ContentType"),
                "size": head.get("ContentLength"),
                "lastModified": head.get("LastModified"),
                "etag": head.get("ETag"),
            }
        )


class DeleteObjectView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        key = (request.query_params.get("key") or "").lstrip("/")
        if not key:
            return JsonResponse({"error": "Missing key"}, status=400)

        client = s3_client()
        try:
            client.delete_object(Bucket=settings.MINIO_BUCKET, Key=key)
        except ClientError as e:
            code = (e.response.get("Error") or {}).get("Code")
            if code in ("NoSuchKey", "404", "NotFound"):
                # idempotent delete
                return JsonResponse({"ok": True, "deleted": False})
            return JsonResponse({"error": "Failed to delete object"}, status=500)

        return JsonResponse({"ok": True, "deleted": True})


class DirectUploadView(APIView):
    """Direct file upload through Django backend (bypasses presigned URL issues)"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        key = request.data.get("key")
        if not key:
            return JsonResponse({"error": "Missing key"}, status=400)

        if "file" not in request.FILES:
            return JsonResponse({"error": "Missing file"}, status=400)

        file_obj = request.FILES["file"]
        content_type = request.data.get("contentType") or file_obj.content_type or "application/octet-stream"

        client = s3_client()
        try:
            client.upload_fileobj(
                file_obj,
                settings.MINIO_BUCKET,
                key,
                ExtraArgs={"ContentType": content_type},
            )
            return JsonResponse({"ok": True, "key": key})
        except ClientError as e:
            code = (e.response.get("Error") or {}).get("Code")
            message = (e.response.get("Error") or {}).get("Message", "Upload failed")
            
            # Provide helpful error message for credential issues
            if code == "InvalidAccessKeyId":
                error_msg = (
                    f"MinIO credentials error: {message}. "
                    "Please check MINIO_ACCESS_KEY and MINIO_SECRET_KEY in backend_django/.env file. "
                    "See docs/MINIO_CREDENTIALS_SETUP.md for instructions."
                )
            elif code == "SignatureDoesNotMatch":
                error_msg = (
                    f"MinIO credentials error: {message}. "
                    "Please check MINIO_SECRET_KEY in backend_django/.env file."
                )
            else:
                error_msg = f"Upload failed: {code} - {message}"
            
            return JsonResponse({"error": error_msg}, status=500)


