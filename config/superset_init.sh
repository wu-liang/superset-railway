#!/usr/bin/env bash
set -euo pipefail

echo "[init] Starting Superset init..."

# Bind Gunicorn to the Railway-assigned port (fallback to 8088 for local/dev)
export SUPERSET_BIND_ADDRESS="${SUPERSET_BIND_ADDRESS:-::}"  # Changed to :: for IPv6
export SUPERSET_PORT="${PORT:-${SUPERSET_PORT:-8088}}"

echo "[init] Will bind to ${SUPERSET_BIND_ADDRESS}:${SUPERSET_PORT}"

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
echo "[init] Launching web server..."
exec /usr/bin/run-server.sh
