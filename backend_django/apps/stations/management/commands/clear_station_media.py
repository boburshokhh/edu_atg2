from __future__ import annotations

import sys

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.stations.models import Station


class Command(BaseCommand):
    help = "Clear legacy station media fields (image, tech_map_image) to stop loading old MinIO/static assets."

    def add_arguments(self, parser):
        parser.add_argument(
            "--only-legacy",
            action="store_true",
            help="Clear only rows that look like legacy paths (stations/*, tex_kart/*, *.jpg/png, etc.).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show how many rows would be changed without updating.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        # Windows console safety
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

        only_legacy: bool = bool(options["only_legacy"])
        dry_run: bool = bool(options["dry_run"])

        qs = Station.objects.all()
        if only_legacy:
            from django.db.models import Q

            legacy_q = (
                Q(image__startswith="stations/")
                | Q(image__startswith="/stations/")
                | Q(image__icontains="stations/")
                | Q(image__iendswith=".jpg")
                | Q(image__iendswith=".jpeg")
                | Q(image__iendswith=".png")
                | Q(tech_map_image__startswith="tex_kart/")
                | Q(tech_map_image__startswith="/tex_kart/")
                | Q(tech_map_image__icontains="tex_kart/")
                | Q(tech_map_image__iendswith=".jpg")
                | Q(tech_map_image__iendswith=".jpeg")
                | Q(tech_map_image__iendswith=".png")
            )
            qs = Station.objects.filter(legacy_q)

        total = qs.count()
        if dry_run:
            self.stdout.write(f"[dry-run] Would clear media fields for {total} station(s).")
            return

        updated = qs.update(image=None, tech_map_image=None)
        self.stdout.write(f"Cleared media fields for {updated} station(s).")


