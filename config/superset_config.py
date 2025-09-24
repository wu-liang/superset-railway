import os

# =============================
# Core security & database
# =============================
# Secret key for signing cookies and CSRF tokens. MUST be a strong random value in production.
SECRET_KEY = os.environ.get("SECRET_KEY", "CHANGE_ME_TO_A_LONG_RANDOM_STRING")

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
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_STARTTLS = os.getenv("SMTP_STARTTLS", "True").lower() == "true"
SMTP_SSL = os.getenv("SMTP_SSL", "False").lower() == "true"
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_MAIL_FROM = os.getenv("SMTP_MAIL_FROM", "no-reply@example.com")


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
