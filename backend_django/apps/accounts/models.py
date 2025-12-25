import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.db import models


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    username = models.CharField(max_length=50, unique=True)
    # Keep Django-friendly field name, but map to existing column name
    password = models.CharField(max_length=255, db_column="password_hash")
    full_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    role = models.CharField(
        max_length=20,
        default="user",
        choices=(("admin", "admin"), ("user", "user"), ("instructor", "instructor")),
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "users"
        managed = False

    @property
    def is_authenticated(self) -> bool:
        return True

    def set_password(self, raw_password: str) -> None:
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        # Backward-compat: support legacy plaintext passwords from earlier prototype DB
        hashed = self.password or ""
        if hashed.startswith(("pbkdf2_", "bcrypt$", "argon2$", "scrypt$")):
            return check_password(raw_password, hashed)
        if hashed == raw_password:
            # Upgrade on successful legacy login
            self.set_password(raw_password)
            try:
                self.save(update_fields=["password", "updated_at"])
            except Exception:
                # Best-effort; do not block login on upgrade failure
                pass
            return True
        return False


class UserProfile(models.Model):
    id = models.OneToOneField(User, primary_key=True, db_column="id", on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    avatar_url = models.TextField(null=True, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    language = models.CharField(max_length=10, default="ru")
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    weekly_report = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"
        managed = False


class UserSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, db_column="user_id", on_delete=models.CASCADE)
    session_token = models.TextField(unique=True)  # JWT tokens can be longer than 255 chars
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "user_sessions"
        managed = False


class LdapTempSession(models.Model):
    """
    Temporary LDAP session used during first-time registration.
    Records are created on successful LDAP bind when the user does NOT exist in `users` yet.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    ldap_email = models.CharField(max_length=100)
    ldap_username = models.CharField(max_length=50)
    ldap_full_name = models.CharField(max_length=100, null=True, blank=True)
    ldap_phone = models.CharField(max_length=50, null=True, blank=True)
    ldap_department = models.CharField(max_length=255, null=True, blank=True)
    ldap_position = models.CharField(max_length=255, null=True, blank=True)
    ldap_groups = models.JSONField(null=True, blank=True)
    session_token = models.TextField(unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ldap_temp_sessions"
        managed = False





