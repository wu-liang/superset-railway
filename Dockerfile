FROM apache/superset:${TAG:-6.0.0}

# Switch to root user for installation
USER root

# Set Playwright environment variable for browser path
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/playwright-browsers

# Install system FreeTDS and OpenSSL dev libraries for building pymssql from source.
# Superset 6.0 uses Debian Trixie with OpenSSL 3.5, which breaks pre-built pymssql wheels.
RUN apt-get update && \
    apt-get install -y --no-install-recommends freetds-dev libssl-dev libkrb5-dev gcc && \
    rm -rf /var/lib/apt/lists/*

# Configure FreeTDS for Azure SQL: require TDS 7.4 and encryption
RUN printf '[global]\ntds version = 7.4\nencryption = require\n' > /etc/freetds/freetds.conf
ENV FREETDSCONF=/etc/freetds/freetds.conf

# Activate virtual environment and install required packages
# pymssql is built from source (--no-binary) to link against system FreeTDS/OpenSSL
RUN . /app/.venv/bin/activate && \
    uv pip install --no-binary pymssql \
    # Database driver for PostgreSQL (replace with mysqlclient for MySQL)
    psycopg2-binary \
    # Database driver for Microsoft SQL Server (built from source for TLS compatibility)
    pymssql \
    # Authentication for SSO
    Authlib \
    # Excel file upload support
    openpyxl \
    # PDF generation for alerts and reports
    Pillow \
    # Screenshot generation for alerts, reports, and thumbnails
    playwright \
    # Celery for asynchronous tasks
    celery \
    # Redis for caching and Celery broker
    redis \
    && \
    # Install Playwright dependencies and Chromium browser (required for Superset)
    playwright install-deps && \
    PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/playwright-browsers playwright install chromium

COPY /config/superset_init.sh ./superset_init.sh
RUN chmod +x ./superset_init.sh

COPY /config/superset_config.py /app/
ENV SUPERSET_CONFIG_PATH /app/superset_config.py
ENV SECRET_KEY $SECRET_KEY

USER superset
