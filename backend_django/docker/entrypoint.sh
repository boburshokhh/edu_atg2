#!/usr/bin/env sh
set -eu

echo "Waiting for Postgres..."
python - <<'PY'
import os
import time
import psycopg

host = os.getenv("POSTGRES_HOST", "postgres")
port = int(os.getenv("POSTGRES_PORT", "5432"))
name = os.getenv("POSTGRES_DB", "atg_edu")
user = os.getenv("POSTGRES_USER", "admin")
password = os.getenv("POSTGRES_PASSWORD", "1602atgbobur")

for i in range(60):
    try:
        with psycopg.connect(host=host, port=port, dbname=name, user=user, password=password, connect_timeout=3):
            print("Postgres is up")
            break
    except Exception as e:
        time.sleep(1)
else:
    raise SystemExit("Postgres not ready")
PY

echo "Running database bootstrap..."
python manage.py bootstrap_db || echo "Bootstrap failed or already done"

echo "Starting API..."
exec gunicorn atg_backend.wsgi:application -b 0.0.0.0:8000 --workers 2 --threads 4 --timeout 120



