import os
from celery import Celery
from flask_caching import Cache

# Enable features for alerts, reports, and thumbnails
FEATURE_FLAGS = {
    'ALERT_REPORTS': True,  # Enable alerts and reports
    'PLAYWRIGHT_REPORTS_AND_THUMBNAILS': True,  # Enable Playwright screenshots
    'THUMBNAILS': True,  # Enable thumbnail generation
    'THUMBNAILS_SQLA_LISTENERS': True,  # Enable thumbnail listeners
}

# Celery configuration for async tasks and scheduling
class CeleryConfig:
    # Redis as broker (injected via REDIS_URL environment variable)
    broker_url = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    imports = (
        'superset.sql_lab',
        'superset.tasks.thumbnails',  # Thumbnail tasks
        'superset.tasks.scheduler'
    )
    # Redis as result backend
    result_backend = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    worker_prefetch_multiplier = 10
    task_acks_late = True
    # Beat schedule storage (uses metadata database by default)
    beat_schedule_database = os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql+psycopg2://superset:superset@db:5432/superset')

CELERY_CONFIG = CeleryConfig

# Cache configuration using Redis
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,  # 24 hours (set to -1 to disable)
    'CACHE_KEY_PREFIX': 'superset_metadata_cache',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://redis:6379/0')
}

FILTER_STATE_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,
    'CACHE_KEY_PREFIX': 'superset_filter_cache',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://redis:6379/0')
}

EXPLORE_FORM_DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,
    'CACHE_KEY_PREFIX': 'superset_explore_cache',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://redis:6379/0')
}

DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 86400,
    'CACHE_KEY_PREFIX': 'superset_data_cache',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL', 'redis://redis:6379/0')
}

# Rate limiting storage using Redis
RATELIMIT_STORAGE_URI = os.environ.get('REDIS_URL', 'redis://redis:6379/0')

# Database URI (injected via DATABASE_URL environment variable, with official default fallback)
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://superset:superset@db:5432/superset')

# Secret key for Superset (injected via SECRET_KEY environment variable, official name)
SECRET_KEY = os.environ.get('SECRET_KEY', 'tests')  # Replace with strong key in production
