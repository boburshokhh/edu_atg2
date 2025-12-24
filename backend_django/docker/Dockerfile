# Django Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (only curl for healthcheck)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . /app/

# Copy migrations from repo root if they exist (for bootstrap_db)
# Note: migrations should be in the parent directory when build context is backend_django
# If migrations are in the same directory, this will work
COPY ../migrations/ /app/migrations/ 2>/dev/null || true
RUN if [ ! -d /app/migrations ] || [ -z "$(ls -A /app/migrations 2>/dev/null)" ]; then \
      echo "Warning: migrations directory not found or empty"; \
    fi

# Set permissions for entrypoint script
RUN chmod +x /app/docker/entrypoint.sh

# Expose port
EXPOSE 8000

# Run entrypoint
CMD ["/app/docker/entrypoint.sh"]

