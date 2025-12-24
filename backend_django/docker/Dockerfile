# Django Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (only curl for healthcheck)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY backend_django/requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend_django/ /app/

# Copy migrations from repo root (for bootstrap_db)
COPY migrations/ /app/migrations/

# Set permissions for entrypoint script
RUN chmod +x /app/docker/entrypoint.sh

# Expose port
EXPOSE 8000

# Run entrypoint
CMD ["/app/docker/entrypoint.sh"]

