# Django Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file (if exists)
COPY requirements.txt* ./

# Install Python dependencies
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Install common Django dependencies if requirements.txt doesn't exist
RUN pip install --no-cache-dir \
    django \
    djangorestframework \
    django-cors-headers \
    psycopg2-binary \
    boto3 \
    PyJWT \
    python-dotenv \
    gunicorn \
    ldap3 || true

# Copy project files
COPY . .

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Wait for postgres\n\
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT 1" > /dev/null 2>&1; do\n\
  echo "Waiting for postgres..."\n\
  sleep 1\n\
done\n\
\n\
# Run migrations\n\
python manage.py migrate --noinput || true\n\
\n\
# Collect static files\n\
python manage.py collectstatic --noinput || true\n\
\n\
# Start server\n\
exec gunicorn atg_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Run entrypoint
CMD ["/app/entrypoint.sh"]

