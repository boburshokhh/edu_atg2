from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = "Apply incremental schema for video transcode jobs (safe/idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema-file",
            default="migrations/video_transcode_jobs.sql",
            help="Path to SQL file (relative to repo root).",
        )

    def handle(self, *args, **options):
        schema_file = options["schema_file"]

        # backend_django/apps/files/management/commands -> backend_django -> repo root
        repo_root = Path(__file__).resolve().parents[5]
        sql_path = (repo_root / schema_file).resolve()

        if not sql_path.exists():
            raise SystemExit(f"Schema file not found: {sql_path}")

        sql = sql_path.read_text(encoding="utf-8")
        self.stdout.write(f"Applying schema file: {sql_path}")

        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(sql)

        self.stdout.write(self.style.SUCCESS("Video transcode jobs schema applied."))


