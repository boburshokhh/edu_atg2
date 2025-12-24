#!/usr/bin/env sh
set -e

echo "Waiting for Postgres..."
python - <<'PY'
import os
import time
import sys

# psycopg2-binary 3.x uses psycopg module
try:
    import psycopg
    connect_func = psycopg.connect
except ImportError:
    try:
        # Fallback to psycopg2 for older versions
        import psycopg2
        connect_func = psycopg2.connect
    except ImportError:
        print("ERROR: Neither psycopg nor psycopg2 is installed!")
        sys.exit(1)

host = os.getenv("POSTGRES_HOST", "postgres")
port = int(os.getenv("POSTGRES_PORT", "5432"))
name = os.getenv("POSTGRES_DB", "atg")
user = os.getenv("POSTGRES_USER", "atg")
password = os.getenv("POSTGRES_PASSWORD", "atg")

max_attempts = 60
for i in range(max_attempts):
    try:
        conn = connect_func(
            host=host,
            port=port,
            dbname=name,
            user=user,
            password=password,
            connect_timeout=3
        )
        conn.close()
        print("Postgres is up")
        break
    except Exception as e:
        if i < max_attempts - 1:
            print(f"Waiting for postgres... ({i+1}/{max_attempts})")
            time.sleep(1)
        else:
            print(f"Postgres connection failed: {e}")
            sys.exit(1)
PY

echo "Running migrations..."
set +e
python manage.py migrate --noinput
MIGRATE_EXIT=$?
set -e
if [ $MIGRATE_EXIT -ne 0 ]; then
    echo "WARNING: Migrations failed (exit code: $MIGRATE_EXIT), but continuing..."
fi

echo "Running database bootstrap..."
set +e
python manage.py bootstrap_db
BOOTSTRAP_EXIT=$?
set -e
if [ $BOOTSTRAP_EXIT -ne 0 ]; then
    echo "WARNING: Bootstrap failed (exit code: $BOOTSTRAP_EXIT), but continuing..."
fi

echo "Starting API server..."
exec gunicorn atg_backend.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info



