from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import models, transaction
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.views import APIView

from apps.accounts.jwt_utils import JwtError, JwtUserPayload, JwtPendingRegistrationPayload, sign_access, sign_refresh, verify_refresh, sign_pending_registration
from apps.accounts.authentication import PendingRegistrationAuthentication, AccessJWTAuthentication, SessionTokenAuthentication
from apps.accounts.models import User, UserProfile, UserSession
from apps.accounts.serializers import (
    LoginSerializer,
    LogoutSerializer,
    ProfileUpdateSerializer,
    RefreshSerializer,
    RegisterProfileSerializer,
)

logger = logging.getLogger(__name__)


class PendingRegistrationOrAuthenticated(BasePermission):
    """Allow access for authenticated users or pending registration tokens"""
    
    def has_permission(self, request, view):
        # Check if we have pending registration data (set by PendingRegistrationAuthentication)
        if hasattr(request, 'pending_registration_data'):
            return True
        
        # Check if user is authenticated (normal flow)
        if request.user and hasattr(request.user, 'is_authenticated'):
            if request.user.is_authenticated:
                return True
        
        return False


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
    - company/station (profile.company)
    - position (profile.position)
    """
    if not profile:
        return False

    full_name = (profile.full_name or user.full_name or "").strip()
    email = (profile.email or user.email or "").strip()
    phone = (profile.phone or "").strip()
    company = (profile.company or "").strip()
    position = (profile.position or "").strip()

    return bool(full_name and email and phone and company and position)


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
                            # User doesn't exist - don't create yet, store LDAP data in pending registration token
                            logger.info(f"[LDAP] User not found in DB, creating pending registration token: {username}")
                            
                            # Prepare LDAP data for pending registration
                            ldap_full_name = (ldap_user_info.get("full_name") or username or "")[:100]
                            ldap_email_final = (ldap_email or f"{provided_username}@example.com")[:100]
                            ldap_phone = (ldap_user_info.get("phone") or "")[:50]
                            ldap_department = (ldap_user_info.get("department") or "")[:255]
                            ldap_position = (ldap_user_info.get("position") or "")[:255]
                            ldap_role = self._determine_role_from_ldap(ldap_user_info)
                            
                            # Create pending registration token with LDAP data
                            pending_payload = JwtPendingRegistrationPayload(
                                username=(canonical_username or provided_username)[:50],
                                email=ldap_email_final,
                                full_name=ldap_full_name,
                                phone=ldap_phone,
                                department=ldap_department,
                                position=ldap_position,
                                role=ldap_role
                            )
                            
                            pending_token, pending_sid = sign_pending_registration(pending_payload)
                            
                            # Store pending registration session (without user_id, since user doesn't exist yet)
                            expires_at = timezone.now() + timedelta(seconds=settings.REFRESH_TTL_SEC)
                            session_token = pending_token[:255] if pending_token else ""
                            user_agent = request.META.get("HTTP_USER_AGENT", "") or ""
                            user_agent = user_agent[:255] if user_agent else ""
                            
                            # Create a temporary session entry (we'll need to handle this differently)
                            # For now, we'll return the token and let registration endpoint create the user
                            
                            logger.info(f"[LDAP] Created pending registration token for: {username}")
                            
                            # Return response with pending registration token
                            response_data = {
                                "token": pending_token,  # Use pending token as access token
                                "refreshToken": pending_token,
                                "user": {
                                    "id": None,  # No user ID yet
                                    "username": pending_payload.username,
                                    "role": pending_payload.role,
                                    "full_name": pending_payload.full_name,
                                    "email": pending_payload.email,
                                },
                                "expiresIn": settings.ACCESS_TTL_SEC,
                                "requires_registration": True,
                                "pending_registration": True,  # Flag to indicate this is a pending registration
                            }
                            
                            logger.info(
                                "[Perf][Login] step=total ms=%d username=%s",
                                int((time.perf_counter() - t0) * 1000),
                                username,
                            )
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
            
            # Check if profile is complete (required for first-time LDAP users)
            requires_registration = not _profile_is_complete(user, profile)
            
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
            
            # Add requires_registration flag if profile is incomplete
            if requires_registration:
                response_data["requires_registration"] = True
                logger.info(f"[Auth] User {username} requires profile registration")

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
        data = {
            "id": str(user.id),
            "username": user.username,
            "role": user.role,
            "full_name": (profile.full_name if profile else user.full_name),
            "email": (profile.email if profile else user.email),
            "avatar_url": profile.avatar_url if profile else None,
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
            }

            UserProfile.objects.update_or_create(id=user, defaults=profile_defaults)

        return JsonResponse({"success": True})


class RegisterProfileView(APIView):
    """View for first-time user registration (completing profile)"""
    authentication_classes = [
        PendingRegistrationAuthentication,  # Check pending registration tokens first
        SessionTokenAuthentication,  # Then check normal sessions
        AccessJWTAuthentication,  # Then check JWT tokens
    ]
    permission_classes = [PendingRegistrationOrAuthenticated]

    def get(self, request):
        """Get existing profile data for editing"""
        # Check if this is a pending registration
        if hasattr(request, 'pending_registration_data'):
            pending_data = request.pending_registration_data
            logger.info(f"[Register] Getting profile data for pending registration: {pending_data.get('username')}")
            
            # Return LDAP data for pre-filling form
            data = {
                "full_name": pending_data.get("full_name", ""),
                "email": pending_data.get("email", ""),
                "phone": pending_data.get("phone", ""),
                "station_id": None,
                "position": pending_data.get("position", ""),
                "department": pending_data.get("department", ""),
            }
            
            logger.info(f"[Register] Returning pending registration data: {data}")
            return JsonResponse({"data": data, "profile_complete": False})
        
        user: User = request.user
        logger.info(f"[Register] Getting profile data for user: {user.username}")
        
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
        ser = RegisterProfileSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        
        full_name = ser.validated_data["full_name"]
        phone = ser.validated_data["phone"]
        station_id = ser.validated_data["station_id"]
        position = ser.validated_data["position"]  # Job title
        department = ser.validated_data["department"]
        
        # Check if this is a pending registration (user doesn't exist yet)
        if hasattr(request, 'pending_registration_data'):
            pending_data = request.pending_registration_data
            logger.info(f"[Register] Creating new user from pending registration: {pending_data.get('username')}")
            
            # Get station name from database
            try:
                from apps.stations.models import Station
                station = Station.objects.get(id=station_id)
                company = station.name  # Use station name as company
            except Station.DoesNotExist:
                logger.error(f"[Register] Station with id {station_id} not found")
                return JsonResponse({"error": "Station not found"}, status=400)
            
            # Get data from pending registration (LDAP)
            username = pending_data.get("username", "")[:50]
            email = pending_data.get("email", "")[:100]
            ldap_full_name = pending_data.get("full_name", "")[:100]
            ldap_phone = pending_data.get("phone", "")[:50]
            ldap_department = pending_data.get("department", "")[:255]
            ldap_position = pending_data.get("position", "")[:255]
            role = pending_data.get("role", "user")
            
            # Use form data, fallback to LDAP data if form data is empty
            final_full_name = (full_name or ldap_full_name or username)[:100]
            final_phone = (phone or ldap_phone)[:50]
            final_position = (position or ldap_position)[:255]
            final_department = (department or ldap_department)[:255]
            
            with transaction.atomic():
                # Create user (NOW, after registration form is filled)
                user = User.objects.create(
                    username=username,
                    password=make_password(""),  # LDAP users don't need password in DB
                    full_name=final_full_name,
                    email=email,
                    role=role,
                    is_active=True,
                )
                logger.info(f"[Register] Created user: {user.id} username={user.username}")
                
                # Create user profile
                UserProfile.objects.create(
                    id=user,
                    full_name=final_full_name[:255],
                    email=email[:255],
                    phone=final_phone,
                    company=company,
                    position=final_position,
                    bio=final_department,
                )
                
                # Create session for the newly created user
                payload = JwtUserPayload(sub=str(user.id), username=user.username, role=user.role)
                access_token = sign_access(payload)
                refresh_token, _sid = sign_refresh(payload)
                
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
                
                logger.info(f"[Register] Profile and user created successfully: {user.username}")
                return JsonResponse({
                    "success": True,
                    "message": "Profile registered successfully",
                    "token": access_token,  # Return new token for the created user
                    "refreshToken": refresh_token,
                    "user": {
                        "id": str(user.id),
                        "username": user.username,
                        "role": user.role,
                        "full_name": user.full_name,
                        "email": user.email,
                    }
                })
        
        # Existing user flow (update existing profile)
        user: User = request.user
        email = user.email or f'{user.username}@example.com'
        
        # Get station name from database
        try:
            from apps.stations.models import Station
            station = Station.objects.get(id=station_id)
            company = station.name  # Use station name as company
        except Station.DoesNotExist:
            logger.error(f"[Register] Station with id {station_id} not found")
            return JsonResponse({"error": "Station not found"}, status=400)
        
        logger.info(f"[Register] Saving profile for user: {user.username}, station: {company}")
        
        with transaction.atomic():
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
                "company": company,  # Station name from database
                "position": position,
                "bio": department,  # Store department in bio field
            }
            
            UserProfile.objects.update_or_create(id=user, defaults=profile_defaults)
        
        logger.info(f"[Register] Profile saved successfully for user: {user.username}")
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
