from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import connection, transaction


class Command(BaseCommand):
    help = "Bootstrap DB schema by executing migrations/complete_database_schema.sql (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--schema-file",
            default="migrations/complete_database_schema.sql",
            help="Path to SQL schema file (relative to repo root).",
        )

    def handle(self, *args, **options):
        schema_file = options["schema_file"]

        # Resolve repo root as: backend_django/apps/core/management/commands -> backend_django -> repo root
        repo_root = Path(__file__).resolve().parents[5]
        sql_path = (repo_root / schema_file).resolve()

        if not sql_path.exists():
            raise SystemExit(f"Schema file not found: {sql_path}")

        self.stdout.write(f"Using schema file: {sql_path}")

        with connection.cursor() as cur:
            cur.execute(
                "SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='users' LIMIT 1"
            )
            already = cur.fetchone() is not None

        if already:
            self.stdout.write(self.style.SUCCESS("Schema already present (users table exists). Skipping."))
            return

        sql = sql_path.read_text(encoding="utf-8")

        # Execute as a whole script. The file is written with semicolons and is idempotent via IF NOT EXISTS.
        self.stdout.write("Applying schema...")
        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(sql)

        self.stdout.write(self.style.SUCCESS("Schema applied successfully."))











