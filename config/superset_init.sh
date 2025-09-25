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
exec /usr/bin/run-server.sh
