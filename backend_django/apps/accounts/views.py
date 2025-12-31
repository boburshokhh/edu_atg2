from __future__ import annotations

import logging
import re
import time
import uuid
from datetime import timedelta
from typing import Optional

from botocore.exceptions import ClientError
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, models, transaction
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.accounts.jwt_utils import JwtError, JwtUserPayload, sign_access, sign_refresh, verify_refresh
from apps.accounts.models import LdapTempSession, User, UserProfile, UserSession
from apps.accounts.serializers import (
    LoginSerializer,
    LogoutSerializer,
    ProfileUpdateSerializer,
    RefreshSerializer,
    RegisterProfileSerializer,
)
from apps.files.minio_client import presign_get, s3_client

logger = logging.getLogger(__name__)


def _sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage in MinIO"""
    # Remove path components
    filename = filename.split("/")[-1].split("\\")[-1]
    # Remove special characters, keep only alphanumeric, dots, hyphens, underscores
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    # Limit length
    return filename[:100]


def _normalize_username(raw: str) -> str:
    """
    Normalize login identifier to a stable username key.
    Supports inputs like:
    - user@domain.com -> user
    - DOMAIN\\user -> user
    - user -> user
    """
    if not raw:
        return ""
    name = raw.strip()
    if "@" in name:
        name = name.split("@", 1)[0]
    if "\\" in name:
        name = name.split("\\")[-1]
    return name.strip()


def _profile_is_complete(user: User, profile: Optional[UserProfile]) -> bool:
    """
    Registration completion criteria:
    - full_name (either in profile or in users table)
    - email (either in profile or in users table)
    - phone (profile)
    - position (profile.position)
    Note: company/station is optional and not required for profile completion
    """
    if not profile:
        return False

    full_name = (profile.full_name or user.full_name or "").strip()
    email = (profile.email or user.email or "").strip()
    phone = (profile.phone or "").strip()
    position = (profile.position or "").strip()

    # Company/station is optional, so we don't check it
    return bool(full_name and email and phone and position)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        t0 = time.perf_counter()
        try:
            ser = LoginSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            username = ser.validated_data["username"]
            password = ser.validated_data["password"]

            user = None
            ldap_user_info = None

            # Try LDAP authentication first if enabled
            if getattr(settings, 'LDAP_ENABLED', False):
                t_ldap0 = time.perf_counter()
                try:
                    from apps.accounts.ldap_utils import authenticate_ldap
                    logger.info(f"[LDAP] Attempting LDAP authentication for user: {username}")
                    ldap_user_info = authenticate_ldap(username, password)
                    logger.info(
                        "[Perf][Login] step=ldap_auth ms=%d username=%s",
                        int((time.perf_counter() - t_ldap0) * 1000),
                        username,
                    )
                    
                    if ldap_user_info:
                        logger.info(f"[LDAP] Authentication successful for user: {username}")
                        # LDAP authentication successful
                        # Try to get or create user in database
                        t_db0 = time.perf_counter()

                        ldap_email_raw = (ldap_user_info.get("email") or "").strip()
                        ldap_email = ldap_email_raw[:100] if ldap_email_raw else ""

                        canonical_username = (_normalize_username(username) or username or "").strip()[:50]
                        provided_username = (username or "").strip()[:50]

                        # Find by email first (prevents duplicate users when login identifier changes).
                        user = None
                        if ldap_email:
                            user = User.objects.filter(email__iexact=ldap_email, is_active=True).first()
                        if not user and provided_username:
                            user = User.objects.filter(username=provided_username, is_active=True).first()
                        if not user and canonical_username and canonical_username != provided_username:
                            user = User.objects.filter(username=canonical_username, is_active=True).first()

                        logger.info(
                            "[Perf][Login] step=db_find_user ms=%d username=%s found=%s",
                            int((time.perf_counter() - t_db0) * 1000),
                            username,
                            bool(user),
                        )

                        if user:
                            logger.info(f"[LDAP] Found existing user in DB: id={user.id} username={user.username}")

                            desired_username = canonical_username or provided_username
                            update_fields = []

                            # Best-effort: normalize stored username (no-op if it would conflict).
                            if desired_username and user.username != desired_username:
                                if not User.objects.filter(username=desired_username).exclude(id=user.id).exists():
                                    user.username = desired_username
                                    update_fields.append("username")

                            if ldap_user_info.get("full_name") and not (user.full_name and user.full_name.strip()):
                                user.full_name = (ldap_user_info.get("full_name") or "")[:100]
                                update_fields.append("full_name")

                            if ldap_email and not (user.email and user.email.strip()):
                                user.email = ldap_email
                                update_fields.append("email")

                            if update_fields:
                                update_fields.append("updated_at")
                                t_save0 = time.perf_counter()
                                user.save(update_fields=update_fields)
                                logger.info(
                                    "[Perf][Login] step=db_update_user ms=%d username=%s fields=%s",
                                    int((time.perf_counter() - t_save0) * 1000),
                                    username,
                                    ",".join(update_fields),
                                )

                            # Backfill profile with LDAP defaults (only if missing).
                            try:
                                profile = UserProfile.objects.filter(id=user.id).first()
                                ldap_full_name = (ldap_user_info.get("full_name") or user.full_name or user.username or "")[:255]
                                ldap_profile_email = (ldap_email_raw or user.email or "")[:255]
                                ldap_phone = (ldap_user_info.get("phone") or "")[:50]
                                ldap_department = (ldap_user_info.get("department") or "")[:255]
                                ldap_position = (ldap_user_info.get("position") or "")[:255]
                                
                                if not profile:
                                    UserProfile.objects.create(
                                        id=user,
                                        full_name=ldap_full_name or None,
                                        email=ldap_profile_email or None,
                                        phone=ldap_phone or None,
                                        position=ldap_position or None,
                                        bio=ldap_department or None,
                                    )
                                else:
                                    profile_updates = {}
                                    if ldap_full_name and not (profile.full_name and profile.full_name.strip()):
                                        profile_updates["full_name"] = ldap_full_name
                                    if ldap_profile_email and not (profile.email and profile.email.strip()):
                                        profile_updates["email"] = ldap_profile_email
                                    if ldap_phone and not (profile.phone and profile.phone.strip()):
                                        profile_updates["phone"] = ldap_phone
                                    if ldap_position and not (profile.position and profile.position.strip()):
                                        profile_updates["position"] = ldap_position
                                    if ldap_department and not (profile.bio and profile.bio.strip()):
                                        profile_updates["bio"] = ldap_department
                                    if profile_updates:
                                        UserProfile.objects.filter(id=user.id).update(**profile_updates)
                            except Exception as profile_err:
                                logger.warning(f"[LDAP] Could not backfill user profile: {profile_err}")

                        else:
                            # IMPORTANT: do NOT create a user record on first LDAP login.
                            # Create a temporary LDAP session, and only create `users` on registration submit.
                            logger.info(f"[LDAP] User not found in DB, creating ldap_temp_session: {username}")

                            temp_payload_role = self._determine_role_from_ldap(ldap_user_info)
                            temp_id = None
                            refresh_token = None

                            # Issue tokens for temp identity: sub="temp:<uuid>"
                            temp_id = str(uuid.uuid4())
                            temp_sub = f"temp:{temp_id}"
                            temp_payload = JwtUserPayload(sub=temp_sub, username=provided_username or canonical_username or username, role=temp_payload_role)
                            access_token = sign_access(temp_payload)
                            refresh_token, _sid = sign_refresh(temp_payload)

                            # Store temp session (store full refresh token so refresh/logout can validate)
                            expires_at = timezone.now() + timedelta(seconds=settings.REFRESH_TTL_SEC)
                            LdapTempSession.objects.create(
                                id=temp_id,
                                ldap_email=(ldap_email_raw or "")[:100],
                                ldap_username=(provided_username or canonical_username or username)[:50],
                                ldap_full_name=(ldap_user_info.get("full_name") or "")[:100] or None,
                                ldap_phone=(ldap_user_info.get("phone") or "")[:50] or None,
                                ldap_department=(ldap_user_info.get("department") or "")[:255] or None,
                                ldap_position=(ldap_user_info.get("position") or "")[:255] or None,
                                ldap_groups=ldap_user_info.get("groups", []) or [],
                                session_token=refresh_token,
                                expires_at=expires_at,
                            )

                            response_data = {
                                "token": access_token,
                                "refreshToken": refresh_token,
                                "user": {
                                    "id": temp_id,
                                    "username": (provided_username or canonical_username or username)[:50],
                                    "role": temp_payload_role,
                                    "full_name": (ldap_user_info.get("full_name") or (provided_username or username))[:100],
                                    "email": (ldap_email_raw or ""),
                                },
                                "expiresIn": settings.ACCESS_TTL_SEC,
                                "requires_registration": True,
                            }
                            logger.info(f"[Auth] Temp LDAP login OK, requires registration: {username}")
                            return JsonResponse(response_data)
                    else:
                        logger.info(f"[LDAP] Authentication failed for user: {username}")
                except ImportError as e:
                    logger.error(f"[LDAP] Import error: {e}. ldap3 may not be installed.")
                except Exception as ldap_err:
                    logger.error(f"[LDAP] Error during LDAP authentication: {ldap_err}")
                    # Continue to database authentication
            else:
                logger.debug("[Auth] LDAP is not enabled, using database authentication")

            # Fallback to database authentication if LDAP failed or disabled
            if not user:
                logger.info(f"[Auth] Attempting database authentication for user: {username}")
                try:
                    t_db0 = time.perf_counter()
                    user = User.objects.get(username=username, is_active=True)
                    logger.info(
                        "[Perf][Login] step=db_get_user ms=%d username=%s",
                        int((time.perf_counter() - t_db0) * 1000),
                        username,
                    )
                    logger.info(f"[Auth] Found user in database: {username}")
                    
                    if not user.check_password(password):
                        logger.warning(f"[Auth] Invalid password for user: {username}")
                        return JsonResponse({"error": "Invalid credentials"}, status=401)
                    
                    logger.info(f"[Auth] Database authentication successful for user: {username}")
                except User.DoesNotExist:
                    logger.warning(f"[Auth] User not found in database: {username}")
                    return JsonResponse({"error": "Invalid credentials"}, status=401)

            # Generate tokens
            t_jwt0 = time.perf_counter()
            payload = JwtUserPayload(sub=str(user.id), username=user.username, role=user.role)
            access_token = sign_access(payload)
            refresh_token, _sid = sign_refresh(payload)
            logger.info(
                "[Perf][Login] step=sign_jwt ms=%d username=%s",
                int((time.perf_counter() - t_jwt0) * 1000),
                username,
            )

            expires_at = timezone.now() + timedelta(seconds=settings.REFRESH_TTL_SEC)
            t_sess0 = time.perf_counter()
            # Truncate values to fit database constraints
            # session_token is VARCHAR(255) in database, but JWT tokens can be longer
            session_token = refresh_token[:255] if refresh_token else ""
            # user_agent is TEXT in schema but may have constraints in actual DB
            user_agent = request.META.get("HTTP_USER_AGENT", "") or ""
            user_agent = user_agent[:255] if user_agent else ""
            UserSession.objects.create(
                id=_sid,
                user=user,
                session_token=session_token,
                expires_at=expires_at,
                ip_address=request.META.get("REMOTE_ADDR"),
                user_agent=user_agent,
            )
            logger.info(
                "[Perf][Login] step=db_create_session ms=%d username=%s",
                int((time.perf_counter() - t_sess0) * 1000),
                username,
            )

            logger.info(f"[Auth] Login successful for user: {username}")
            
            # Get user profile if exists
            try:
                t_prof0 = time.perf_counter()
                profile = UserProfile.objects.filter(id=user.id).first()
                logger.info(
                    "[Perf][Login] step=db_get_profile ms=%d username=%s",
                    int((time.perf_counter() - t_prof0) * 1000),
                    username,
                )
                user_full_name = profile.full_name if profile and profile.full_name else user.full_name or user.username
                user_email = profile.email if profile and profile.email else user.email or f'{user.username}@example.com'
            except Exception:
                user_full_name = user.full_name or user.username
                user_email = user.email or f'{user.username}@example.com'
            
            # IMPORTANT: If user already exists in users table, they should NOT be required to register again
            # requires_registration should only be True for temp LDAP sessions (handled earlier in the code)
            # For existing users in DB, always set requires_registration = False
            requires_registration = False
            
            response_data = {
                "token": access_token,
                "refreshToken": refresh_token,
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "role": user.role,
                    "full_name": user_full_name,
                    "email": user_email,
                },
                "expiresIn": settings.ACCESS_TTL_SEC,
            }
            
            # Note: requires_registration is only set to True for temp LDAP sessions (see line 232)
            # Existing users in DB should never be required to register again
            logger.info(f"[Auth] User {username} is existing user in DB, registration not required")

            logger.info(
                "[Perf][Login] step=total ms=%d username=%s",
                int((time.perf_counter() - t0) * 1000),
                username,
            )
            return JsonResponse(response_data)
        except Exception as e:
            logger.error(f"[Auth] Unexpected error during login: {e}", exc_info=True)
            return JsonResponse({"error": f"Internal server error: {str(e)}"}, status=500)

    def _determine_role_from_ldap(self, ldap_user_info: dict) -> str:
        """Determine user role from LDAP groups"""
        groups = ldap_user_info.get('groups', [])
        
        # Check for admin group
        admin_groups = ['admin', 'administrators', 'admins', 'domain admins']
        for group in groups:
            if group.lower() in [ag.lower() for ag in admin_groups]:
                return 'admin'
        
        # Check for instructor group
        instructor_groups = ['instructor', 'instructors', 'teachers', 'trainers']
        for group in groups:
            if group.lower() in [ig.lower() for ig in instructor_groups]:
                return 'instructor'
        
        # Default to user
        return 'user'
    
    def _check_profile_incomplete(self, user: User, profile: UserProfile = None) -> bool:
        """Check if user profile is incomplete (missing required fields for registration)"""
        return not _profile_is_complete(user, profile)


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = RefreshSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        refresh_token = ser.validated_data["refreshToken"]

        try:
            decoded = verify_refresh(refresh_token)
        except JwtError:
            return JsonResponse({"error": "Invalid token"}, status=401)

        # Temporary LDAP session refresh
        sub = decoded.get("sub") or ""
        if isinstance(sub, str) and sub.startswith("temp:"):
            temp = (
                LdapTempSession.objects.filter(session_token=refresh_token, expires_at__gt=timezone.now())
                .first()
            )
            if not temp:
                return JsonResponse({"error": "Session expired"}, status=401)
            payload = JwtUserPayload(sub=sub, username=decoded.get("username") or temp.ldap_username, role=decoded.get("role") or "user")
            access_token = sign_access(payload)
            return JsonResponse({"token": access_token, "expiresIn": settings.ACCESS_TTL_SEC})

        # Truncate token to 255 chars to match database constraint
        session_token = refresh_token[:255] if refresh_token else ""
        session = (
            UserSession.objects.filter(session_token=session_token, expires_at__gt=timezone.now())
            .select_related("user")
            .first()
        )
        if not session:
            return JsonResponse({"error": "Session expired"}, status=401)

        user = session.user
        payload = JwtUserPayload(sub=str(user.id), username=user.username, role=user.role)
        access_token = sign_access(payload)
        return JsonResponse({"token": access_token, "expiresIn": settings.ACCESS_TTL_SEC})


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = LogoutSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        refresh_token = ser.validated_data["refreshToken"]
        # Temp LDAP session logout
        try:
            decoded = verify_refresh(refresh_token)
            sub = decoded.get("sub") or ""
            if isinstance(sub, str) and sub.startswith("temp:"):
                LdapTempSession.objects.filter(session_token=refresh_token).delete()
                return JsonResponse({"success": True})
        except Exception:
            pass
        # Truncate token to 255 chars to match database constraint
        session_token = refresh_token[:255] if refresh_token else ""
        UserSession.objects.filter(session_token=session_token).delete()
        return JsonResponse({"success": True})


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Keep compatibility with Node: { user: payload }
        payload = getattr(request, "jwt", None)
        if not payload:
            payload = {"sub": str(request.user.id), "username": request.user.username, "role": request.user.role}
        return JsonResponse({"user": payload})


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user: User = request.user
        profile = UserProfile.objects.filter(id=user.id).first()
        
        # Generate presigned URL for avatar if it's stored in MinIO
        avatar_url = None
        avatar_key = None
        if profile and profile.avatar_url:
            # Store the MinIO key
            avatar_key = profile.avatar_url
            # If avatar_url is a MinIO key (starts with avatars/), generate presigned URL
            if profile.avatar_url.startswith("avatars/"):
                try:
                    avatar_url = presign_get(profile.avatar_url, expires_in=60 * 60 * 24 * 7)
                except Exception as e:
                    logger.warning(f"[MyProfileView] Failed to generate presigned URL for avatar: {e}")
                    avatar_url = None
            else:
                # If it's already a URL, use it as is
                avatar_url = profile.avatar_url
        
        data = {
            "id": str(user.id),
            "username": user.username,
            "role": user.role,
            "full_name": (profile.full_name if profile else user.full_name),
            "email": (profile.email if profile else user.email),
            "avatar_url": avatar_url,
            "avatar_key": avatar_key,  # MinIO key for caching
            "company": profile.company if profile else None,
            "position": profile.position if profile else None,
            "phone": profile.phone if profile else None,
            "bio": profile.bio if profile else None,
            "language": profile.language if profile else "ru",
            "email_notifications": profile.email_notifications if profile else True,
            "push_notifications": profile.push_notifications if profile else True,
            "weekly_report": profile.weekly_report if profile else False,
        }
        return JsonResponse({"data": data})

    def put(self, request):
        user: User = request.user
        ser = ProfileUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        updates = ser.validated_data

        with transaction.atomic():
            # Optional: keep users table in sync for base fields
            base_update = {}
            if "full_name" in updates:
                base_update["full_name"] = updates.get("full_name") or None
            if "email" in updates:
                base_update["email"] = updates.get("email") or None
            if base_update:
                User.objects.filter(id=user.id).update(**base_update)

            profile_defaults = {
                "full_name": updates.get("full_name", None),
                "email": updates.get("email", None),
                "company": updates.get("company", None),
                "position": updates.get("position", None),
                "phone": updates.get("phone", None),
                "bio": updates.get("bio", None),
                "language": updates.get("language", "ru") or "ru",
                "email_notifications": updates.get("email_notifications", True),
                "push_notifications": updates.get("push_notifications", True),
                "weekly_report": updates.get("weekly_report", False),
                "avatar_url": updates.get("avatar_url", None),
            }

            UserProfile.objects.update_or_create(id=user, defaults=profile_defaults)

        return JsonResponse({"success": True})


class UploadAvatarView(APIView):
    """Upload user avatar image to MinIO and update profile"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user: User = request.user
        
        if "file" not in request.FILES:
            return JsonResponse({"error": "No file provided"}, status=400)
        
        file_obj = request.FILES["file"]
        content_type = getattr(file_obj, "content_type", None) or "application/octet-stream"
        
        # Validate file type
        if not content_type.startswith("image/"):
            return JsonResponse({"error": "Only image files are allowed"}, status=400)
        
        # Validate file size (max 5MB for avatars)
        max_size = 5 * 1024 * 1024  # 5MB
        if getattr(file_obj, "size", 0) > max_size:
            return JsonResponse({"error": "File is too large (max 5MB)"}, status=400)
        
        # Generate safe filename
        safe_name = _sanitize_filename(getattr(file_obj, "name", "avatar"))
        # Use user ID in key to avoid conflicts
        key = f"avatars/{user.id}/{int(time.time())}_{safe_name}"
        
        # Upload to MinIO
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
            logger.error(f"[UploadAvatar] MinIO upload failed for user {user.id}: {code} - {message}")
            return JsonResponse({"error": f"Upload failed: {code} - {message}"}, status=500)
        
        # Update user profile with MinIO key
        with transaction.atomic():
            profile, created = UserProfile.objects.get_or_create(id=user.id)
            # Delete old avatar from MinIO if exists
            if profile.avatar_url and profile.avatar_url.startswith("avatars/"):
                try:
                    old_key = profile.avatar_url
                    client.delete_object(Bucket=settings.MINIO_BUCKET, Key=old_key)
                    logger.info(f"[UploadAvatar] Deleted old avatar: {old_key}")
                except Exception as e:
                    logger.warning(f"[UploadAvatar] Could not delete old avatar: {e}")
            
            profile.avatar_url = key
            profile.save(update_fields=["avatar_url"])
        
        # Generate presigned URL for immediate display
        try:
            url = presign_get(key, expires_in=60 * 60 * 24 * 7, response_content_type=content_type)
        except Exception as e:
            logger.error(f"[UploadAvatar] Failed to generate presigned URL: {e}")
            url = None
        
        logger.info(f"[UploadAvatar] Avatar uploaded successfully for user {user.id}: {key}")
        
        return JsonResponse({
            "success": True,
            "key": key,
            "url": url,
            "message": "Avatar uploaded successfully"
        })


class RegisterProfileView(APIView):
    """View for first-time user registration (completing profile)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get existing profile data for editing"""
        # Can be a real DB user or a temporary LDAP session user
        user = request.user
        logger.info(f"[Register] Getting profile data for user: {user.username}")

        temp_session = getattr(request, "ldap_temp_session", None)
        if temp_session is not None:
            data = {
                "full_name": temp_session.ldap_full_name or "",
                "phone": temp_session.ldap_phone or "",
                "station_id": None,
                "position": temp_session.ldap_position or "",
                "department": temp_session.ldap_department or "",
            }
            return JsonResponse({"data": data, "profile_complete": False})
        
        profile = UserProfile.objects.filter(id=user.id).first()
        logger.debug(f"[Register] Profile found: {profile is not None}")
        
        # Try to find station_id by company name
        station_id = None
        if profile and profile.company:
            try:
                from apps.stations.models import Station
                # Try exact match first
                station = Station.objects.filter(name=profile.company).first()
                if not station:
                    # Try case-insensitive match
                    station = Station.objects.filter(name__iexact=profile.company).first()
                if station:
                    station_id = station.id
                    logger.info(f"[Register] Found station_id: {station_id} for company: {profile.company}")
                else:
                    logger.warning(f"[Register] Station not found for company: {profile.company}")
            except Exception as e:
                logger.warning(f"[Register] Could not find station by company name: {e}")
        
        # Get full_name from profile or user (user may have data from LDAP)
        full_name = ""
        if profile and profile.full_name:
            full_name = profile.full_name
            logger.debug(f"[Register] Using full_name from profile: {full_name}")
        elif user.full_name:
            full_name = user.full_name
            logger.debug(f"[Register] Using full_name from user: {full_name}")
        
        # Get phone, position, and department from profile
        phone = profile.phone if profile else ""
        position = profile.position if profile else ""
        # Department хранится в bio (так как в БД нет отдельного поля department)
        department = profile.bio if profile else ""
        email = ""
        if profile and profile.email:
            email = profile.email
        elif user.email:
            email = user.email
        
        profile_complete = _profile_is_complete(user, profile)
        
        data = {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "station_id": station_id,
            "position": position,
            "department": department,
        }
        
        logger.info(f"[Register] Returning profile data: {data}")
        return JsonResponse({"data": data, "profile_complete": profile_complete})

    def post(self, request):
        """Save user profile with required fields (full_name, phone, station_id, position)"""
        user = request.user
        ser = RegisterProfileSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        
        full_name = ser.validated_data["full_name"]
        phone = ser.validated_data["phone"]
        station_id = ser.validated_data.get("station_id")  # Optional field
        position = ser.validated_data["position"]  # Job title
        department = ser.validated_data["department"]
        
        # Get station name from database (before checking temp_session)
        company = None
        if station_id is not None:
            try:
                from apps.stations.models import Station
                station = Station.objects.get(id=station_id)
                company = station.name  # Use station name as company
            except Station.DoesNotExist:
                logger.error(f"[Register] Station with id {station_id} not found")
                return JsonResponse({"error": "Station not found"}, status=400)
        
        # Check if this is a temporary LDAP session (first-time registration)
        temp_session = getattr(request, "ldap_temp_session", None)
        
        # Get email - from temp_session if available, otherwise from user
        if temp_session is not None:
            email = (temp_session.ldap_email or "").strip()[:100]
            if not email:
                return JsonResponse({"error": "LDAP email is missing"}, status=400)
        else:
            # Regular user - get email from user object (may not have email attribute if it's a mock)
            email = getattr(user, "email", None) or f'{user.username}@example.com'
        
        # Если станция не выбрана и есть LDAP сессия, используем отдел из LDAP
        # Если пользователь ввел отдел вручную, используем его, иначе берем из LDAP
        final_department = department
        # Если отдел не указан (пустая строка или None) и есть LDAP сессия, используем отдел из LDAP
        if (not final_department or not final_department.strip()) and temp_session and temp_session.ldap_department:
            final_department = temp_session.ldap_department
            logger.info(f"[Register] Using LDAP department: {final_department} (station not selected or department not provided)")
        
        logger.info(f"[Register] Saving profile for user: {user.username}, station: {company or 'Not selected'}, department: {final_department or 'Not provided'}")
        
        # Track if we created new tokens (for temp session -> real user conversion)
        access_token = None
        refresh_token = None
        
        with transaction.atomic():
            if temp_session is not None:
                # Create real user now (ONLY after registration).
                # Enforce email uniqueness; DB has a unique index (lower(email)).
                # Email already extracted above

                # If user already exists by email, stop (no duplicates).
                existing = User.objects.filter(email__iexact=email, is_active=True).first()
                if existing:
                    # Also cleanup temp session to avoid dangling records
                    LdapTempSession.objects.filter(id=temp_session.id).delete()
                    return JsonResponse({"error": "User with this email already exists"}, status=409)

                desired_username = (temp_session.ldap_username or _normalize_username(temp_session.ldap_email) or "user")[:50]
                if User.objects.filter(username=desired_username).exists():
                    desired_username = (desired_username[:40] + "_" + str(temp_session.id).split("-")[0])[:50]

                role = "user"
                try:
                    role = LoginView()._determine_role_from_ldap({"groups": temp_session.ldap_groups or []})
                except Exception:
                    role = "user"

                try:
                    user = User.objects.create(
                        username=desired_username,
                        password=make_password(str(uuid.uuid4())),  # not used for LDAP, but required
                        full_name=(full_name or "")[:100],
                        email=email,
                        role=role,
                        is_active=True,
                    )
                except IntegrityError:
                    return JsonResponse({"error": "Duplicate email or username"}, status=409)

                # Create login session for the new user (real refresh/session in user_sessions)
                payload = JwtUserPayload(sub=str(user.id), username=user.username, role=user.role)
                access_token = sign_access(payload)
                refresh_token, _sid = sign_refresh(payload)
                # Tokens are now set in outer scope
                expires_at = timezone.now() + timedelta(seconds=settings.REFRESH_TTL_SEC)
                session_token = refresh_token[:255] if refresh_token else ""
                user_agent = request.META.get("HTTP_USER_AGENT", "") or ""
                user_agent = user_agent[:255] if user_agent else ""
                UserSession.objects.create(
                    id=_sid,
                    user=user,
                    session_token=session_token,
                    expires_at=expires_at,
                    ip_address=request.META.get("REMOTE_ADDR"),
                    user_agent=user_agent,
                )

                # Remove temp session
                LdapTempSession.objects.filter(id=temp_session.id).delete()

            # Update user table
            User.objects.filter(id=user.id).update(
                full_name=full_name,
                updated_at=timezone.now()
            )
            
            # Create or update user profile
            profile_defaults = {
                "full_name": full_name,
                "email": email,
                "phone": phone,
                "company": company,  # Station name from database (None if not selected)
                "position": position,
                "bio": final_department,  # Store department in bio field (from LDAP if station not selected)
            }
            
            UserProfile.objects.update_or_create(id=user, defaults=profile_defaults)
        
        logger.info(f"[Register] Profile saved successfully for user: {user.username}")
        # If temp session was used, return fresh tokens for the newly created user
        if access_token and refresh_token:
            return JsonResponse(
                {
                    "success": True,
                    "message": "Profile registered successfully",
                    "token": access_token,
                    "refreshToken": refresh_token,
                    "user": {
                        "id": str(user.id),
                        "username": user.username,
                        "role": user.role,
                        "full_name": full_name,
                        "email": email,
                    },
                }
            )
        return JsonResponse({"success": True, "message": "Profile registered successfully"})


class MyStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.courses.models import Certificate, UserCourse

        user: User = request.user

        qs = UserCourse.objects.filter(user_id=user.id)
        active_courses = qs.filter(progress_percent__lt=100).count()
        completed_courses = qs.filter(progress_percent=100).count()
        total_progress = qs.aggregate(s=models.Sum("progress_percent")).get("s") or 0

        certs = list(
            Certificate.objects.filter(user_id=user.id)
            .order_by("-issued_at")
            .values("id", "title", "issued_at")
        )

        return JsonResponse(
            {"stats": {"active_courses": active_courses, "completed_courses": completed_courses, "total_progress": total_progress}, "certificates": certs}
        )


class LDAPTestView(APIView):
    """Test LDAP connection and authentication"""
    permission_classes = [AllowAny]

    def get(self, request):
        """Get LDAP configuration (without sensitive data)"""
        ldap_enabled = getattr(settings, 'LDAP_ENABLED', False)
        
        if not ldap_enabled:
            return JsonResponse({
                "success": False,
                "message": "LDAP is not enabled",
                "config": None
            })
        
        # Check if ldap3 is available
        try:
            from apps.accounts.ldap_utils import LDAP_AVAILABLE
            if not LDAP_AVAILABLE:
                return JsonResponse({
                    "success": False,
                    "message": "ldap3 package is not installed",
                    "config": {
                        "server": getattr(settings, 'LDAP_SERVER', ''),
                        "base_dn": getattr(settings, 'LDAP_BASE_DN', ''),
                        "enabled": True
                    }
                })
        except ImportError:
            return JsonResponse({
                "success": False,
                "message": "LDAP utilities not available",
                "config": None
            })
        
        return JsonResponse({
            "success": True,
            "message": "LDAP Configuration loaded",
            "config": {
                "server": getattr(settings, 'LDAP_SERVER', ''),
                "base_dn": getattr(settings, 'LDAP_BASE_DN', ''),
                "user_search_base": getattr(settings, 'LDAP_USER_SEARCH_BASE', ''),
                "user_search_filter": getattr(settings, 'LDAP_USER_SEARCH_FILTER', ''),
                "enabled": True
            }
        })

    def post(self, request):
        """Test LDAP authentication with provided credentials"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return JsonResponse({
                "success": False,
                "message": "Username and password are required"
            }, status=400)
        
        ldap_enabled = getattr(settings, 'LDAP_ENABLED', False)
        if not ldap_enabled:
            return JsonResponse({
                "success": False,
                "message": "LDAP is not enabled"
            }, status=400)
        
        try:
            from apps.accounts.ldap_utils import authenticate_ldap, LDAP_AVAILABLE
            
            if not LDAP_AVAILABLE:
                return JsonResponse({
                    "success": False,
                    "message": "ldap3 package is not installed. Install with: pip install ldap3"
                }, status=500)
            
            logger.info(f"[LDAP Test] Testing authentication for user: {username}")
            user_info = authenticate_ldap(username, password)
            
            if user_info:
                logger.info(f"[LDAP Test] Authentication successful for: {username}")
                return JsonResponse({
                    "success": True,
                    "message": "Authentication successful!",
                    "user": {
                        "username": user_info.get('username'),
                        "email": user_info.get('email'),
                        "full_name": user_info.get('full_name'),
                        "groups": user_info.get('groups', [])
                    }
                })
            else:
                logger.info(f"[LDAP Test] Authentication failed for: {username}")
                return JsonResponse({
                    "success": False,
                    "message": "Invalid username or password"
                }, status=401)
                
        except Exception as e:
            logger.error(f"[LDAP Test] Error: {e}", exc_info=True)
            return JsonResponse({
                "success": False,
                "message": f"LDAP error: {str(e)}",
                "debug": str(e) if settings.DEBUG else None
            }, status=500)
