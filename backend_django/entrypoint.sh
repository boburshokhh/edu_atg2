#!/usr/bin/env sh
set -e

export DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-atg_backend.settings}

echo "Waiting for Postgres..."
python - <<'PY'
import os, time
try:
    import psycopg
    connect = psycopg.connect
except Exception:
    connect = None

host = os.getenv("POSTGRES_HOST", "postgres")
port = int(os.getenv("POSTGRES_PORT", "5432"))
db = os.getenv("POSTGRES_DB", "atg_edu")
user = os.getenv("POSTGRES_USER", "admin")
pwd = os.getenv("POSTGRES_PASSWORD", "admin")

for i in range(60):
    try:
        if connect is None:
            raise RuntimeError("psycopg not installed")
        c = connect(host=host, port=port, dbname=db, user=user, password=pwd, connect_timeout=3)
        c.close()
        print("Postgres is up")
        break
    except Exception as e:
        if i == 59:
            raise
        time.sleep(1)
PY

echo "Migrations..."
python manage.py migrate --noinput

echo "Ensure MinIO bucket exists..."
python - <<'PY'
from botocore.exceptions import ClientError
from django.conf import settings
import django

django.setup()

from apps.files.minio_client import s3_client

client = s3_client()
bucket = settings.MINIO_BUCKET
try:
    client.head_bucket(Bucket=bucket)
    print("Bucket exists:", bucket)
except ClientError:
    client.create_bucket(Bucket=bucket)
    print("Bucket created:", bucket)
PY

echo "Starting Gunicorn..."
exec gunicorn atg_backend.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --threads 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -


