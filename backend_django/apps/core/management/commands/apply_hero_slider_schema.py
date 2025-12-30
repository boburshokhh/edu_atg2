from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Create hero_slider_images table for storing multiple hero background images (slider)."

    def handle(self, *args, **options):
        sql_path = Path(__file__).resolve().parents[1] / "hero_slider_schema.sql"
        sql = sql_path.read_text(encoding="utf-8")

        with connection.cursor() as cursor:
            cursor.execute(sql)

        self.stdout.write(self.style.SUCCESS("hero_slider_images schema applied (or already present)."))

