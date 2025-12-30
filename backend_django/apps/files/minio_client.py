from __future__ import annotations

import os
import time
import uuid
from urllib.parse import urlparse

import boto3
from botocore.config import Config
from django.conf import settings


def env(key: str, default: str = None) -> str | None:
    """Get environment variable with default"""
    return os.getenv(key, default)


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
        
        # Log before generation - check settings
        minio_public_endpoint_check = getattr(settings, 'MINIO_PUBLIC_ENDPOINT', 'NOT_SET')
        logger.info(f"[presign_get] ========== START presign_get ==========")
        logger.info(f"[presign_get] Generating presigned URL for key: {key}")
        logger.info(f"[presign_get] MINIO_ENDPOINT: {settings.MINIO_ENDPOINT}")
        logger.info(f"[presign_get] MINIO_PUBLIC_ENDPOINT from settings: {minio_public_endpoint_check}")
        logger.info(f"[presign_get] Type of MINIO_PUBLIC_ENDPOINT: {type(minio_public_endpoint_check)}")
        
        url = client.generate_presigned_url("get_object", Params=params, ExpiresIn=expires_in)
        
        # Log after generation
        logger.info(f"[presign_get] Generated presigned URL (before replacement): {url[:200] if url else 'None'}...")
        
        # IMPORTANT: Do NOT replace hostname in presigned URLs!
        # Presigned URLs are signed with the hostname, so changing it invalidates the signature.
        # Instead, return URL with original hostname - frontend will use /api/minio/ proxy
        # which preserves the Host header (proxy_set_header Host minio:9000 in nginx.conf)
        # 
        # The frontend getFrontendUrl() function will convert http://minio:9000/... to /api/minio/...
        # and nginx will proxy it to MinIO with correct Host header, preserving the signature.
        
        logger.info(f"[presign_get] Returning presigned URL with original hostname (frontend will use /api/minio/ proxy)")
        logger.info(f"[presign_get] URL will be converted by frontend getFrontendUrl() to use /api/minio/ proxy")
        
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











