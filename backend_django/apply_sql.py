import os
import django
from django.db import connection

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "atg_backend.settings")
django.setup()

try:
    with open("migrations/create_station_extras.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    with connection.cursor() as cursor:
        cursor.execute(sql)
        print("SQL executed successfully.")
except Exception as e:
    print(f"Error executing SQL: {e}")

