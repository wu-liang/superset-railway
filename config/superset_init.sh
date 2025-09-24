#!/bin/bash
set -e

# Upgrading Superset metastore
superset db upgrade

# 
if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_PASSWORD" ] && [ -n "$ADMIN_EMAIL" ]; then
  superset fab create-admin \
    --username "$ADMIN_USERNAME" \
    --firstname "Admin" \
    --lastname "User" \
    --email "$ADMIN_EMAIL" \
    --password "$ADMIN_PASSWORD" || true
fi

# setup roles and permissions
superset init 

# Starting server
/bin/sh -c /usr/bin/run-server.sh
