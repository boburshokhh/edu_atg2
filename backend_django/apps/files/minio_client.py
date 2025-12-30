from __future__ import annotations

import time
import uuid
from urllib.parse import urlparse

import boto3
from botocore.config import Config
from django.conf import settings


def _endpoint_url() -> str:
    # boto3 expects scheme://host:port
    return settings.MINIO_ENDPOINT


def _is_ssl(endpoint: str) -> bool:
    return urlparse(endpoint).scheme == "https"


def s3_client():
    endpoint = _endpoint_url()
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        region_name="us-east-1",
        use_ssl=_is_ssl(endpoint),
        config=Config(s3={"addressing_style": "path"}),
    )


def presign_get(key: str, expires_in: int = 60 * 60 * 24 * 7, response_content_type: str | None = None) -> str:
    """
    Generate presigned URL for downloading object from MinIO.
    
    Args:
        key: Object key in MinIO bucket
        expires_in: URL expiration time in seconds (default: 7 days)
        response_content_type: Optional content type override
        
    Returns:
        Presigned URL string (with public endpoint if configured)
        
    Raises:
        ClientError: If MinIO operation fails
        ValueError: If key is empty or invalid
    """
    import logging
    logger = logging.getLogger(__name__)
    
    if not key or not key.strip():
        raise ValueError("Key cannot be empty")
    
    # Normalize key: remove leading slashes
    key = key.lstrip("/")
    
    try:
        params: dict = {"Bucket": settings.MINIO_BUCKET, "Key": key}
        if response_content_type:
            params["ResponseContentType"] = response_content_type
        
        # Validate expires_in
        if expires_in <= 0:
            expires_in = 60 * 60 * 24 * 7  # Default to 7 days
        if expires_in > 60 * 60 * 24 * 7:  # Max 7 days
            expires_in = 60 * 60 * 24 * 7
        
        client = s3_client()
        
        # #region agent log
        import json
        try:
            with open(r'c:\Users\user\Desktop\edu_atg\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    "id": f"log_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                    "timestamp": int(time.time() * 1000),
                    "location": "minio_client.py:presign_get",
                    "message": "Before generating presigned URL",
                    "data": {
                        "key": key,
                        "minio_endpoint": getattr(settings, 'MINIO_ENDPOINT', 'NOT_SET'),
                        "minio_public_endpoint": getattr(settings, 'MINIO_PUBLIC_ENDPOINT', 'NOT_SET'),
                        "hypothesisId": "A"
                    },
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "A"
                }) + '\n')
        except Exception as log_err:
            pass
        # #endregion
        
        url = client.generate_presigned_url("get_object", Params=params, ExpiresIn=expires_in)
        
        # #region agent log
        try:
            with open(r'c:\Users\user\Desktop\edu_atg\.cursor\debug.log', 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    "id": f"log_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                    "timestamp": int(time.time() * 1000),
                    "location": "minio_client.py:presign_get",
                    "message": "After generating presigned URL (before replacement)",
                    "data": {
                        "original_url": url[:200] if url else None,
                        "hypothesisId": "A"
                    },
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": "A"
                }) + '\n')
        except Exception as log_err:
            pass
        # #endregion
        
        # Replace internal endpoint with public endpoint if configured
        # This is needed because presigned URLs are used by browsers which cannot
        # resolve internal Docker hostnames like "minio:9000"
        minio_public_endpoint = getattr(settings, 'MINIO_PUBLIC_ENDPOINT', None)
        if minio_public_endpoint and url:
            from urllib.parse import urlparse, urlunparse
            parsed_internal = urlparse(settings.MINIO_ENDPOINT)
            parsed_public = urlparse(minio_public_endpoint)
            parsed_url = urlparse(url)
            
            # Replace hostname and scheme if public endpoint is configured
            if parsed_internal.netloc != parsed_public.netloc:
                new_netloc = parsed_public.netloc
                new_scheme = parsed_public.scheme
                url = urlunparse((
                    new_scheme,
                    new_netloc,
                    parsed_url.path,
                    parsed_url.params,
                    parsed_url.query,
                    parsed_url.fragment
                ))
                
                # #region agent log
                try:
                    with open(r'c:\Users\user\Desktop\edu_atg\.cursor\debug.log', 'a', encoding='utf-8') as f:
                        f.write(json.dumps({
                            "id": f"log_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                            "timestamp": int(time.time() * 1000),
                            "location": "minio_client.py:presign_get",
                            "message": "After replacing endpoint with public URL",
                            "data": {
                                "final_url": url[:200] if url else None,
                                "replaced_from": parsed_internal.netloc,
                                "replaced_to": new_netloc,
                                "hypothesisId": "C"
                            },
                            "sessionId": "debug-session",
                            "runId": "run1",
                            "hypothesisId": "C"
                        }) + '\n')
                except Exception as log_err:
                    pass
                # #endregion
        
        if not url:
            logger.error(f"[presign_get] Failed to generate URL for key: {key}")
            raise ValueError("Failed to generate presigned URL")
        
        return url
    except Exception as e:
        logger.error(f"[presign_get] Error generating presigned URL for key {key}: {e}")
        raise


def presign_put(key: str, content_type: str | None = None, expires_in: int = 900) -> str:
    params: dict = {"Bucket": settings.MINIO_BUCKET, "Key": key}
    if content_type:
        params["ContentType"] = content_type
    return s3_client().generate_presigned_url("put_object", Params=params, ExpiresIn=expires_in)











