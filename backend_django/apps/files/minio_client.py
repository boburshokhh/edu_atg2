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
        
        # Replace internal endpoint with public endpoint if configured
        # This is needed because presigned URLs are used by browsers which cannot
        # resolve internal Docker hostnames like "minio:9000"
        if url:
            from urllib.parse import urlparse, urlunparse
            parsed_url = urlparse(url)
            parsed_internal = urlparse(settings.MINIO_ENDPOINT)
            
            # Get public endpoint from settings (already auto-configured in settings.py)
            minio_public_endpoint = getattr(settings, 'MINIO_PUBLIC_ENDPOINT', None)
            logger.info(f"[presign_get] === ENDPOINT REPLACEMENT DEBUG ===")
            logger.info(f"[presign_get] MINIO_ENDPOINT: {settings.MINIO_ENDPOINT}")
            logger.info(f"[presign_get] MINIO_PUBLIC_ENDPOINT from settings: {minio_public_endpoint}")
            logger.info(f"[presign_get] URL netloc (from boto3): {parsed_url.netloc}")
            logger.info(f"[presign_get] Internal netloc: {parsed_internal.netloc}")
            
            # Force replacement if URL contains "minio" (internal Docker hostname)
            # This is a safety check in case MINIO_PUBLIC_ENDPOINT is not configured
            url_contains_minio = 'minio' in parsed_url.netloc.lower()
            
            if minio_public_endpoint:
                parsed_public = urlparse(minio_public_endpoint)
                logger.info(f"[presign_get] Public endpoint parsed - netloc: {parsed_public.netloc}, scheme: {parsed_public.scheme}")
                
                # Replace if:
                # 1. Public endpoint differs from URL's current netloc, OR
                # 2. URL contains "minio" (internal Docker hostname) - force replacement
                should_replace = (
                    (parsed_public.netloc and parsed_public.netloc != parsed_url.netloc) or
                    url_contains_minio
                )
                
                if should_replace and parsed_public.netloc:
                    new_netloc = parsed_public.netloc
                    new_scheme = parsed_public.scheme
                    old_url = url
                    url = urlunparse((
                        new_scheme,
                        new_netloc,
                        parsed_url.path,
                        parsed_url.params,
                        parsed_url.query,
                        parsed_url.fragment
                    ))
                    
                    logger.info(f"[presign_get] ✅ SUCCESS: Replaced endpoint: {parsed_url.netloc} -> {new_netloc}")
                    logger.info(f"[presign_get] Final URL (first 200 chars): {url[:200] if url else 'None'}...")
                    logger.info(f"[presign_get] === ENDPOINT REPLACEMENT COMPLETE ===")
                else:
                    logger.warning(f"[presign_get] ⚠️ Replacement SKIPPED - public netloc: {parsed_public.netloc}, URL netloc: {parsed_url.netloc}, url_contains_minio: {url_contains_minio}")
            elif url_contains_minio:
                # URL contains "minio" but no public endpoint configured - use hardcoded default
                logger.warning(f"[presign_get] ⚠️ URL contains 'minio' but MINIO_PUBLIC_ENDPOINT not set! Using hardcoded default.")
                default_public = "http://192.168.32.100:9000"
                parsed_default = urlparse(default_public)
                url = urlunparse((
                    parsed_default.scheme,
                    parsed_default.netloc,
                    parsed_url.path,
                    parsed_url.params,
                    parsed_url.query,
                    parsed_url.fragment
                ))
                logger.info(f"[presign_get] ✅ FORCED replacement using default: {parsed_url.netloc} -> {parsed_default.netloc}")
            else:
                logger.error(f"[presign_get] ❌ ERROR: No public endpoint configured - cannot replace internal hostname!")
                logger.error(f"[presign_get] MINIO_PUBLIC_ENDPOINT is None or not set in settings!")
        
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











