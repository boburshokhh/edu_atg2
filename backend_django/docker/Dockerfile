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

# Copy and set permissions for entrypoint script
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Run entrypoint
CMD ["/app/entrypoint.sh"]

