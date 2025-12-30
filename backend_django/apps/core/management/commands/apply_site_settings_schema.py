from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Create site_settings table (singleton) used for site-wide configuration such as Hero background image."

    def handle(self, *args, **options):
        sql_path = Path(__file__).resolve().parents[1] / "site_settings_schema.sql"
        sql = sql_path.read_text(encoding="utf-8")

        with connection.cursor() as cursor:
            cursor.execute(sql)

        self.stdout.write(self.style.SUCCESS("site_settings schema applied (or already present)."))


