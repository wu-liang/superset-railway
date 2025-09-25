#!/usr/bin/env bash
set -euo pipefail

echo "[init] Starting Superset init..."

# --- Database migrations ---
echo "[init] Upgrading Superset metastore..."
superset db upgrade

# --- Bootstrap admin (optional, idempotent) ---
if [[ -n "${ADMIN_USERNAME:-}" && -n "${ADMIN_PASSWORD:-}" && -n "${ADMIN_EMAIL:-}" ]]; then
  echo "[init] Ensuring admin user '${ADMIN_USERNAME}' exists..."
  superset fab create-admin \
    --username "$ADMIN_USERNAME" \
    --firstname "Admin" \
    --lastname "User" \
    --email "$ADMIN_EMAIL" \
    --password "$ADMIN_PASSWORD" || true
else
  echo "[init] Skipping admin bootstrap (ADMIN_* not fully set)."
fi

# --- Initialize roles, permissions, etc. ---
echo "[init] Running 'superset init'..."
superset init

# --- Start web server (becomes PID 1) ---
echo "[init] Launching web server on [::]:${PORT:-8088}..."

HYPHEN_SYMBOL='-'

exec gunicorn \
    --bind "[::]:${PORT:-8088}" \
    --access-logfile "${ACCESS_LOG_FILE:-$HYPHEN_SYMBOL}" \
    --error-logfile "${ERROR_LOG_FILE:-$HYPHEN_SYMBOL}" \
    --workers ${SERVER_WORKER_AMOUNT:-1} \
    --worker-class ${SERVER_WORKER_CLASS:-gthread} \
    --threads ${SERVER_THREADS_AMOUNT:-20} \
    --log-level "${GUNICORN_LOGLEVEL:-info}" \
    --timeout ${GUNICORN_TIMEOUT:-60} \
    --keep-alive ${GUNICORN_KEEPALIVE:-2} \
    --max-requests ${WORKER_MAX_REQUESTS:-0} \
    --max-requests-jitter ${WORKER_MAX_REQUESTS_JITTER:-0} \
    --limit-request-line ${SERVER_LIMIT_REQUEST_LINE:-0} \
    --limit-request-field_size ${SERVER_LIMIT_REQUEST_FIELD_SIZE:-0} \
    "${FLASK_APP}"
