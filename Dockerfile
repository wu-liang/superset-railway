FROM apache/superset:${TAG:-5.0.0}

# Switch to root user for installation
USER root

# Set Playwright environment variable for browser path
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/local/share/playwright-browsers

# Activate virtual environment and install required packages
RUN . /app/.venv/bin/activate && \
    uv pip install \
    # Database driver for PostgreSQL (replace with mysqlclient for MySQL)
    psycopg2-binary \
    # Database driver for Microsoft SQL Server
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
