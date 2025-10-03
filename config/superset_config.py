import os
from typing import Optional
from celery.schedules import crontab

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
SQLALCHEMY_DATABASE_URI = env_str(
    "DATABASE_URL",
    "postgresql+psycopg2://superset:superset@db:5432/superset",
)

# Disable SQLAlchemy event system that is not used by Superset and costs overhead.
SQLALCHEMY_TRACK_MODIFICATIONS = False

# If running behind a reverse proxy (Railway, Nginx, Cloudflare, etc.), enable this
# so Superset respects X-Forwarded-* headers for scheme/host.
ENABLE_PROXY_FIX = True

# Logging level for Superset (DEBUG for detailed logs during troubleshooting)
SUPERSET_LOG_LEVEL = env_str("SUPERSET_LOG_LEVEL", "INFO")


# =============================
# Feature flags
# =============================
FEATURE_FLAGS = {
    # Embedded dashboards / SDK (shows "Embed dashboard" menu)
    "EMBEDDED_SUPERSET": True,
    "TAGGING_SYSTEM": True,
    "ENABLE_TEMPLATE_PROCESSING": True,

    # Alerts & Reports
    "ALERT_REPORTS": True,

    # Thumbnails & screenshots via Playwright (needs Chromium deps in your image)
    "THUMBNAILS": True,
    "THUMBNAILS_SQLA_LISTENERS": True,
    "PLAYWRIGHT_REPORTS_AND_THUMBNAILS": True,
    "ALLOW_UPLOAD_CSV": True,  # Enables CSV upload
    "ALLOW_UPLOAD_EXCEL": True,  # Enables Excel upload (.xlsx, .xls)
}


# =============================
# Caching & Rate Limiting (Redis)
# =============================
# Use the same Redis for caches, Celery, and rate-limit storage.
REDIS_URL = env_str("REDIS_URL", "redis://redis:6379/0")

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
    imports = (
        "superset.sql_lab",
        "superset.tasks.scheduler",
    )
    worker_prefetch_multiplier = 10
    task_acks_late = True
    task_annotations = {
        "sql_lab.get_sql_results": {
            "rate_limit": "100/s",
        },
    }
    beat_schedule = {
        "reports.scheduler": {
            "task": "reports.scheduler",
            "schedule": crontab(minute="*", hour="*"),
        },
        "reports.prune_log": {
            "task": "reports.prune_log",
            "schedule": crontab(minute=0, hour=0),
        },
    }

# Tell Superset to use the CeleryConfig above
CELERY_CONFIG = CeleryConfig

SCREENSHOT_LOCATE_WAIT = 100
SCREENSHOT_LOAD_WAIT = 600

# Slack configuration
SLACK_API_TOKEN = "xoxb-"

# =============================
# Email (for Alerts/Reports) - optional
# =============================
# Set EMAIL_NOTIFICATIONS=True and configure SMTP_* if you need emails.
EMAIL_NOTIFICATIONS = env_str("EMAIL_NOTIFICATIONS", "False").lower() == "true"
SMTP_HOST = env_str("SMTP_HOST")
SMTP_PORT = env_int("SMTP_PORT", 587)
SMTP_USER = env_str("SMTP_USER")
SMTP_PASSWORD = env_str("SMTP_PASSWORD")
SMTP_MAIL_FROM = env_str("SMTP_MAIL_FROM", "no-reply@example.com")

# =============================
# Thumbnails / Playwright base URL
# =============================
WEBDRIVER_BASEURL = env_str("WEBDRIVER_BASEURL")
WEBDRIVER_BASEURL_USER_FRIENDLY = env_str("WEBDRIVER_BASEURL_USER_FRIENDLY")

# =============================
# Embedded: guest token settings
# =============================
# Your backend service should use this secret to exchange a short-lived JWT for a Superset guest token.
# Keep this secret safe and strong.
GUEST_TOKEN_JWT_SECRET = env_str("GUEST_TOKEN_JWT_SECRET", "")
GUEST_TOKEN_JWT_ALGO = "HS256"
# Assign the minimal role the embedded user should have (consider creating a custom, read-only role).
GUEST_ROLE_NAME = env_str("GUEST_ROLE_NAME", "Gamma")
# Token lifetime in seconds
GUEST_TOKEN_EXP_SECONDS = env_int("GUEST_TOKEN_EXP_SECONDS", "600")
# Audience validation for JWT guest tokens (string or callable; None disables validation)
GUEST_TOKEN_JWT_AUDIENCE = env_str("GUEST_TOKEN_JWT_AUDIENCE", None)

# =============================
# Security headers / CSP for embedding (environment-driven)
# =============================
# Control Talisman (security headers) via environment variables to avoid rebuilding images for CSP changes.
# Example in Railway:
#   TALISMAN_ENABLED=True
#   FRAME_ANCESTORS="https://frontend.example.com,https://*.up.railway.app"
TALISMAN_ENABLED = env_str("TALISMAN_ENABLED", "True").lower() == "true"

frame_ancestors_env = env_str("FRAME_ANCESTORS", "")
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
MAPBOX_API_KEY = env_str("MAPBOX_API_KEY", "")
