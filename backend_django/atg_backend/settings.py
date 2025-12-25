import os
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from backend_django directory
env_path = BASE_DIR / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback: try env.txt (for backward compatibility)
    env_txt_path = BASE_DIR / 'env.txt'
    if env_txt_path.exists():
        load_dotenv(env_txt_path)


def env(key: str, *args, **kwargs) -> str | None:
    """
    Get environment variable.
    
    Usage:
        env("REQUIRED_VAR")  # Raises error if not set
        env("OPTIONAL_VAR", None)  # Returns None if not set
        env("VAR_WITH_DEFAULT", "default_value")  # Returns default if not set
    
    Args:
        key: Environment variable name
        *args: Optional default value (first arg)
    
    Returns:
        Environment variable value or default
    """
    default = args[0] if args else kwargs.get('default', ...)
    val = os.getenv(key)
    if val is None:
        if default is ...:  # No default provided - variable is required
            raise RuntimeError(f"Missing required env var: {key}")
        return default  # Return default (can be None for optional vars)
    return val


DEBUG = env("DJANGO_DEBUG", "0") in ("1", "true", "True", "yes", "YES")
SECRET_KEY = env("DJANGO_SECRET_KEY", "dev-insecure-secret-change-me")

ALLOWED_HOSTS = [h.strip() for h in env("DJANGO_ALLOWED_HOSTS", "*").split(",") if h.strip()]

INSTALLED_APPS = [
    "corsheaders",
    "rest_framework",
    "apps.core",
    "apps.accounts",
    "apps.stations",
    "apps.courses",
    "apps.files",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "atg_backend.urls"

TEMPLATES = []
WSGI_APPLICATION = "atg_backend.wsgi.application"
ASGI_APPLICATION = "atg_backend.asgi.application"

# Database configuration - support DATABASE_URL or individual settings
database_url = env("DATABASE_URL", None)
if database_url:
    # Parse DATABASE_URL: postgresql://user:password@host:port/database
    parsed = urlparse(database_url)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": parsed.path[1:],  # Remove leading '/'
            "USER": parsed.username,
            "PASSWORD": parsed.password,
            "HOST": parsed.hostname,
            "PORT": parsed.port or "5432",
            "CONN_MAX_AGE": int(env("POSTGRES_CONN_MAX_AGE", "60")),
        }
    }
else:
    # Use individual settings
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env("POSTGRES_DB", "atg"),
            "USER": env("POSTGRES_USER", "atg"),
            "PASSWORD": env("POSTGRES_PASSWORD", "atg"),
            "HOST": env("POSTGRES_HOST", "postgres"),
            "PORT": env("POSTGRES_PORT", "5432"),
            "CONN_MAX_AGE": int(env("POSTGRES_CONN_MAX_AGE", "60")),
        }
    }

LANGUAGE_CODE = "ru"
TIME_ZONE = env("TZ", "UTC")
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS
cors_origins = [o.strip() for o in env("CORS_ORIGINS", "*").split(",") if o.strip()]
if cors_origins == ["*"]:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = cors_origins

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.accounts.authentication.SessionTokenAuthentication",
        "apps.accounts.authentication.AccessJWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    # We do not use django.contrib.auth; keep unauthenticated user/token as None
    # to avoid importing Django's auth/contenttypes models.
    "UNAUTHENTICATED_USER": None,
    "UNAUTHENTICATED_TOKEN": None,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# JWT
JWT_ACCESS_SECRET = env("JWT_ACCESS_SECRET", "dev-access-secret-change-me")
JWT_REFRESH_SECRET = env("JWT_REFRESH_SECRET", "dev-refresh-secret-change-me")
ACCESS_TTL_SEC = int(env("ACCESS_TTL_SEC", "900"))
REFRESH_TTL_SEC = int(env("REFRESH_TTL_SEC", "1209600"))  # 14 days

# MinIO
# IMPORTANT: Update MINIO_ACCESS_KEY and MINIO_SECRET_KEY in .env file
# with your actual MinIO server credentials to avoid InvalidAccessKeyId errors
MINIO_ENDPOINT = env("MINIO_ENDPOINT", "http://192.168.32.100:9000")
MINIO_BUCKET = env("MINIO_BUCKET", "atgedu")
MINIO_ACCESS_KEY = env("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = env("MINIO_SECRET_KEY", "minioadmin")

# LDAP
LDAP_ENABLED = env("LDAP_ENABLED", "false").lower() in ("true", "1", "yes")
LDAP_SERVER = env("LDAP_SERVER", "ldap://localhost:389")
LDAP_BASE_DN = env("LDAP_BASE_DN", "dc=example,dc=com")
LDAP_USER_DN = env("LDAP_USER_DN", "cn=admin,dc=example,dc=com")
LDAP_USER_PASSWORD = env("LDAP_USER_PASSWORD", "")
LDAP_USER_SEARCH_BASE = env("LDAP_USER_SEARCH_BASE", "ou=users,dc=example,dc=com")
LDAP_USER_SEARCH_FILTER = env("LDAP_USER_SEARCH_FILTER", "(uid={username})")
LDAP_GROUP_SEARCH_BASE = env("LDAP_GROUP_SEARCH_BASE", "ou=groups,dc=example,dc=com")
LDAP_REQUIRE_GROUP = env("LDAP_REQUIRE_GROUP", "")
LDAP_USE_TLS = env("LDAP_USE_TLS", "false").lower() in ("true", "1", "yes")
LDAP_TLS_CA_FILE = env("LDAP_TLS_CA_FILE", "")
# LDAP Timeouts (in seconds, must be integers)
# Defaults increased because real LDAP/AD often responds slower than 5s (especially on first bind/search).
LDAP_CONNECT_TIMEOUT_SEC = int(env("LDAP_CONNECT_TIMEOUT_SEC", "15"))
LDAP_RECEIVE_TIMEOUT_SEC = int(env("LDAP_RECEIVE_TIMEOUT_SEC", "15"))
LDAP_SEARCH_TIME_LIMIT_SEC = int(env("LDAP_SEARCH_TIME_LIMIT_SEC", "15"))


