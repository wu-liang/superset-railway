import os
from typing import Optional

# -----------------------------
# Helpers: safe env parsing
# -----------------------------
def env_str(name: str, default: Optional[str] = None) -> Optional[str]:
    v = os.getenv(name)
    return v if (v is not None and v.strip() != "") else default

def env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    try:
        return int(v)
    except (TypeError, ValueError):
        return default

def env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return str(v).strip().lower() in {"1", "true", "yes", "on"}

# =============================
# Core security & database
# =============================
SECRET_KEY = env_str("SECRET_KEY", "CHANGE_ME_TO_A_LONG_RANDOM_STRING")

# Main metadata database for Superset (Postgres recommended in production).
# Railway Postgres plugin usually injects DATABASE_URL automatically.
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg2://superset:superset@db:5432/superset",
)

# Disable SQLAlchemy event system that is not used by Superset and costs overhead.
SQLALCHEMY_TRACK_MODIFICATIONS = False

# If running behind a reverse proxy (Railway, Nginx, Cloudflare, etc.), enable this
# so Superset respects X-Forwarded-* headers for scheme/host.
ENABLE_PROXY_FIX = True


# =============================
# Feature flags
# =============================
FEATURE_FLAGS = {
    # Embedded dashboards / SDK (shows "Embed dashboard" menu)
    "EMBEDDED_SUPERSET": True,

    # Alerts & Reports
    "ALERT_REPORTS": True,

    # Thumbnails & screenshots via Playwright (needs Chromium deps in your image)
    "THUMBNAILS": True,
    "THUMBNAILS_SQLA_LISTENERS": True,
    "PLAYWRIGHT_REPORTS_AND_THUMBNAILS": True,
}


# =============================
# Caching & Rate Limiting (Redis)
# =============================
# Use the same Redis for caches, Celery, and rate-limit storage.
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")

CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 300,
    "CACHE_KEY_PREFIX": "superset_cache",
    "CACHE_REDIS_URL": REDIS_URL,
}

EXPLORE_FORM_DATA_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,
    "CACHE_KEY_PREFIX": "superset_explore_cache",
    "CACHE_REDIS_URL": REDIS_URL,
}

DATA_CACHE_CONFIG = {
    "CACHE_TYPE": "RedisCache",
    "CACHE_DEFAULT_TIMEOUT": 86400,
    "CACHE_KEY_PREFIX": "superset_data_cache",
    "CACHE_REDIS_URL": REDIS_URL,
}

# Flask-Limiter backend. Using memory:// in production is NOT recommended.
RATELIMIT_STORAGE_URI = REDIS_URL or "memory://"


# =============================
# Celery (async tasks, SQL Lab, Alerts/Reports)
# =============================
class CeleryConfig:
    broker_url = REDIS_URL
    result_backend = REDIS_URL
    # Reasonable defaults for small containers
    worker_prefetch_multiplier = 1
    task_acks_late = True
    task_annotations = {
        # Example rate limit for heavy tasks
        "sql_lab.get_sql_results": {"rate_limit": "100/s"},
    }
    # Define beat_schedule here if you need periodic Celery tasks

# Tell Superset to use the CeleryConfig above
CELERY_CONFIG = CeleryConfig


# =============================
# Email (for Alerts/Reports) - optional
# =============================
# Set EMAIL_NOTIFICATIONS=True and configure SMTP_* if you need emails.
EMAIL_NOTIFICATIONS = os.getenv("EMAIL_NOTIFICATIONS", "False").lower() == "true"
SMTP_HOST = env_str("SMTP_HOST")
SMTP_PORT = env_int("SMTP_PORT", 587)
SMTP_USER = env_str("SMTP_USER")
SMTP_PASSWORD = env_str("SMTP_PASSWORD")
SMTP_MAIL_FROM = env_str("SMTP_MAIL_FROM", "no-reply@example.com")

# =============================
# Thumbnails / Playwright base URL
# =============================
# Use your public Railway URL (or custom domain) so Playwright can reach the site
PUBLIC_BASE_URL = env_str("WEBDRIVER_BASEURL") or env_str("PUBLIC_BASE_URL")

# Fallbacks (helpful in local/dev)
if not PUBLIC_BASE_URL:
    # Construct a local URL for dev; Railway will set PORT dynamically, but
    # thumbnails should use the public domain in production (above).
    port = env_str("PORT") or env_str("SUPERSET_PORT") or "8088"
    PUBLIC_BASE_URL = f"http://127.0.0.1:{port}"

# Superset uses this for screenshots / thumbnails / alerts
WEBDRIVER_BASEURL = PUBLIC_BASE_URL

# Allow headless login for thumbnails (matches your bootstrap admin)
THUMBNAIL_SELENIUM_USER = env_str("THUMBNAIL_SELENIUM_USER", env_str("ADMIN_USERNAME"))
THUMBNAIL_SELENIUM_PASSWORD = env_str("THUMBNAIL_SELENIUM_PASSWORD", env_str("ADMIN_PASSWORD"))
ENABLE_THUMBNAILS = env_bool("ENABLE_THUMBNAILS", True)

# =============================
# Embedded: guest token settings
# =============================
# Your backend service should use this secret to exchange a short-lived JWT for a Superset guest token.
# Keep this secret safe and strong.
GUEST_TOKEN_JWT_SECRET = os.getenv("GUEST_TOKEN_JWT_SECRET", "")
GUEST_TOKEN_JWT_ALGO = "HS256"
# Assign the minimal role the embedded user should have (consider creating a custom, read-only role).
GUEST_ROLE_NAME = os.getenv("GUEST_ROLE_NAME", "Gamma")
# Token lifetime in seconds
GUEST_TOKEN_EXP_SECONDS = int(os.getenv("GUEST_TOKEN_EXP_SECONDS", "600"))


# =============================
# Security headers / CSP for embedding (environment-driven)
# =============================
# Control Talisman (security headers) via environment variables to avoid rebuilding images for CSP changes.
# Example in Railway:
#   TALISMAN_ENABLED=True
#   FRAME_ANCESTORS="https://frontend.example.com,https://*.up.railway.app"
TALISMAN_ENABLED = os.getenv("TALISMAN_ENABLED", "True").lower() == "true"

frame_ancestors_env = os.getenv("FRAME_ANCESTORS", "")
frame_ancestors_list = [x.strip() for x in frame_ancestors_env.split(",") if x.strip()]

TALISMAN_CONFIG = {
    "content_security_policy": {
        # Allow the hosts that are permitted to frame Superset.
        # Fallback to "'self'" if not set.
        "frame-ancestors": frame_ancestors_list or ["'self'"],
    },
    # If you still hit X-Frame-Options issues, you can disable it below (use with caution).
    # "frame_options": None,
}


# =============================
# Optional: Mapbox API key
# =============================
# MAPBOX_API_KEY = os.getenv("MAPBOX_API_KEY", "")
