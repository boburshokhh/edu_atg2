# Django Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend_django files first (includes requirements.txt)
COPY backend_django/ /app/

# Copy migrations from repo root (for bootstrap_db)
COPY migrations/ /app/migrations/

# Install Python dependencies
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Install common Django dependencies if requirements.txt doesn't exist
RUN pip install --no-cache-dir \
    django \
    djangorestframework \
    django-cors-headers \
    "psycopg[binary]" \
    boto3 \
    PyJWT \
    python-dotenv \
    gunicorn \
    ldap3 || true

# Copy and set permissions for entrypoint script
COPY backend_django/docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Run entrypoint
CMD ["/app/entrypoint.sh"]

