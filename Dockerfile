FROM apache/superset:${TAG:-6.0.0}

# Switch to root user for installation
USER root

# Set Playwright environment variable for browser path
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/playwright-browsers

# Install Microsoft ODBC Driver 18 for SQL Server (Azure SQL compatible).
# Superset 6.0 uses Debian Trixie with OpenSSL 3.5 which breaks pymssql's TLS handshake,
# so we use Microsoft's official ODBC driver instead.
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl gnupg2 && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

# Activate virtual environment and install required packages
RUN . /app/.venv/bin/activate && \
    uv pip install \
    # Fix sqlglot CEILING->CEIL bug in Superset 6.0 (github.com/apache/superset/issues/37778)
    "sqlglot>=28.10.0,<29" \
    # Database driver for PostgreSQL (replace with mysqlclient for MySQL)
    psycopg2-binary \
    # Database driver for Microsoft SQL Server (via ODBC Driver 18)
    pyodbc \
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
