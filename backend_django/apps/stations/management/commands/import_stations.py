import json
import os
import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.stations.models import (
    Station,
    StationEquipment,
    StationGasSupplySource,
    StationSafetySystem,
    StationSafetySystemFeature,
    StationSpecification,
)


class Command(BaseCommand):
    help = "Import stations data from stationsData.js file into database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default=None,
            help="Path to stationsData.js file (default: ../src/data/stationsData.js relative to backend_django)",
        )
        parser.add_argument(
            "--update",
            action="store_true",
            help="Update existing stations instead of skipping them",
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        update_existing = options["update"]

        # Resolve path relative to project root
        # Command is in: backend_django/apps/stations/management/commands/
        # Project root is: backend_django/../ (one level up)
        command_dir = Path(__file__).resolve().parent
        backend_dir = command_dir.parent.parent.parent.parent  # backend_django/
        project_root = backend_dir.parent  # project root
        
        if file_path:
            full_path = Path(file_path)
            if not full_path.is_absolute():
                full_path = project_root / file_path
        else:
            # Default path: ../src/data/stationsData.js from backend_django
            full_path = project_root / "src" / "data" / "stationsData.js"

        if not full_path.exists():
            self.stdout.write(self.style.ERROR(f"File not found: {full_path}"))
            self.stdout.write(f"Looking for file at: {full_path}")
            return

        self.stdout.write(f"Reading file: {full_path}")

        # Try to parse as JavaScript and extract data
        stations_data = self.parse_js_file(full_path)

        if not stations_data:
            self.stdout.write(self.style.ERROR("Failed to parse stations data"))
            return

        self.stdout.write(f"Found {len(stations_data)} stations to import")

        imported = 0
        updated = 0
        skipped = 0
        errors = 0

        for station_id, station_data in stations_data.items():
            try:
                with transaction.atomic():
                    result = self.import_station(station_data, update_existing)
                    if result == "created":
                        imported += 1
                        self.stdout.write(self.style.SUCCESS(f"[OK] Imported station: {station_data.get('name')}"))
                    elif result == "updated":
                        updated += 1
                        self.stdout.write(self.style.WARNING(f"[UPD] Updated station: {station_data.get('name')}"))
                    else:
                        skipped += 1
                        self.stdout.write(f"- Skipped station: {station_data.get('name')} (already exists)")
            except Exception as e:
                errors += 1
                self.stdout.write(
                    self.style.ERROR(f"[ERR] Error importing station {station_data.get('name')}: {str(e)}")
                )

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Import completed:"))
        self.stdout.write(f"  Imported: {imported}")
        self.stdout.write(f"  Updated: {updated}")
        self.stdout.write(f"  Skipped: {skipped}")
        self.stdout.write(f"  Errors: {errors}")

    def parse_js_file(self, file_path):
        """Parse JavaScript file and extract stationsData object"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Try to extract the stationsData object using regex
        # Look for export const stationsData = { ... } (multiline, non-greedy until closing brace)
        # We need to match balanced braces
        pattern = r"export\s+const\s+stationsData\s*=\s*\{"
        match_start = re.search(pattern, content, re.MULTILINE)
        
        if not match_start:
            # Try without export
            pattern = r"const\s+stationsData\s*=\s*\{"
            match_start = re.search(pattern, content, re.MULTILINE)

        if not match_start:
            self.stdout.write(self.style.ERROR("Could not find stationsData object in file"))
            return None

        # Find the matching closing brace
        # match_start.end() points to the character after the opening brace
        start_pos = match_start.end() - 1  # Position of opening brace
        brace_count = 0
        pos = start_pos
        in_string = False
        string_char = None
        escape_next = False
        
        while pos < len(content):
            char = content[pos]
            
            if escape_next:
                escape_next = False
                pos += 1
                continue
                
            if char == '\\':
                escape_next = True
                pos += 1
                continue
                
            if not in_string:
                if char in ('"', "'"):
                    in_string = True
                    string_char = char
                elif char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Found matching closing brace
                        end_pos = pos + 1
                        js_object = content[start_pos:end_pos]
                        break
            else:
                if char == string_char:
                    in_string = False
                    string_char = None
                    
            pos += 1
        else:
            self.stdout.write(self.style.ERROR("Could not find matching closing brace"))
            return None

        # Convert JavaScript object to valid JSON
        # This is a simplified converter - for production consider using a proper JS parser
        
        # Remove comments (both // and /* */)
        js_object = re.sub(r"//.*?$", "", js_object, flags=re.MULTILINE)
        js_object = re.sub(r"/\*.*?\*/", "", js_object, flags=re.DOTALL)
        
        # Replace single-quoted strings with double-quoted strings
        # Handle strings more carefully - replace single-quoted strings
        def fix_string(match):
            # Get the string content (without quotes)
            str_content = match.group(1)
            # Escape any double quotes and backslashes in the content
            str_content = str_content.replace('\\', '\\\\').replace('"', '\\"')
            # Handle escaped single quotes - they should stay as \'
            return f'"{str_content}"'
        
        # Replace single-quoted strings (handling escaped quotes)
        # This regex matches: '...' where ... can contain escaped quotes \'
        js_object = re.sub(r"'((?:[^'\\]|\\.)*)'", fix_string, js_object)
        
        # Fix trailing commas (before } or ])
        js_object = re.sub(r",(\s*[}\]])", r"\1", js_object)
        
        # Fix unquoted keys (JavaScript allows unquoted keys, JSON doesn't)
        # Match word characters or numbers followed by colon (but not already quoted or in a string)
        # First handle numeric keys (like "1:", "2:")
        js_object = re.sub(r'([{,]\s*)(\d+)\s*:', r'\1"\2":', js_object)
        # Then handle word keys
        js_object = re.sub(r'([{,]\s*)([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:', r'\1"\2":', js_object)

        try:
            # Try to parse as JSON
            data = json.loads(js_object)
            return data
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.WARNING(f"JSON parse error: {e}"))
            self.stdout.write("Attempting to use alternative parsing...")
            # Fallback: manual parsing for common cases
            return self.manual_parse(content)

    def manual_parse(self, content):
        """Manual parsing fallback for JavaScript object"""
        # This is a simplified parser - for production, consider using a proper JS parser
        stations = {}
        # Extract each station block
        pattern = r"(\d+):\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}"
        matches = re.finditer(pattern, content, re.DOTALL)

        for match in matches:
            station_id = int(match.group(1))
            station_content = match.group(2)
            # This is a very basic parser - you may need to enhance it
            # For now, return None to indicate parsing failed
            pass

        return None

    def import_station(self, data, update_existing=False):
        """Import a single station with all related data"""
        # Map JavaScript keys to database fields
        station_data = {
            "name": data.get("name", ""),
            "short_name": data.get("shortName", ""),
            "description": data.get("description"),
            "image": data.get("image"),
            "tech_map_image": data.get("techMapImage"),
            "power": data.get("power"),
            "commission_date": data.get("commissionDate"),
            "courses_count": data.get("coursesCount", 0),
            "status": data.get("status", "active"),
            "location": data.get("location"),
            "type": data.get("type"),
            "design_capacity": data.get("designCapacity"),
            "gas_pressure": data.get("gasPressure"),
            "distance_from_border": data.get("distanceFromBorder"),
            "pipeline_diameter": data.get("pipelineDiameter"),
            "input_pressure": data.get("inputPressure"),
            "output_pressure": data.get("outputPressure"),
            "parallel_lines": data.get("parallelLines"),
        }

        # Check if station exists
        station_id = data.get("id")
        existing_station = None
        if station_id:
            try:
                existing_station = Station.objects.get(id=station_id)
            except Station.DoesNotExist:
                pass

        if existing_station:
            if update_existing:
                # Update existing station
                for key, value in station_data.items():
                    setattr(existing_station, key, value)
                existing_station.save()
                station = existing_station
                result = "updated"
            else:
                # Skip existing station
                return "skipped"
        else:
            # Create new station
            if station_id:
                station_data["id"] = station_id
            station = Station.objects.create(**station_data)
            result = "created"

        # Import equipment
        equipment_list = data.get("equipment", [])
        for idx, eq_data in enumerate(equipment_list):
            StationEquipment.objects.update_or_create(
                station=station,
                name=eq_data.get("name", ""),
                defaults={
                    "model": eq_data.get("model"),
                    "manufacturer": eq_data.get("manufacturer"),
                    "quantity": eq_data.get("quantity", 1),
                    "power": eq_data.get("power"),
                    "description": eq_data.get("description"),
                    "order_index": idx,
                },
            )

        # Import specifications
        specs_list = data.get("specifications", [])
        for idx, spec_data in enumerate(specs_list):
            StationSpecification.objects.update_or_create(
                station=station,
                category=spec_data.get("category", ""),
                defaults={
                    "value": spec_data.get("value"),
                    "unit": spec_data.get("unit"),
                    "description": spec_data.get("description"),
                    "order_index": idx,
                },
            )

        # Import gas supply sources
        gas_sources = data.get("gasSupplySources", [])
        for idx, source_name in enumerate(gas_sources):
            StationGasSupplySource.objects.update_or_create(
                station=station,
                source_name=source_name,
                defaults={"order_index": idx},
            )

        # Import safety systems
        safety_systems = data.get("safetySystems", [])
        for idx, safety_data in enumerate(safety_systems):
            safety_system, _ = StationSafetySystem.objects.update_or_create(
                station=station,
                name=safety_data.get("name", ""),
                defaults={
                    "description": safety_data.get("description"),
                    "manufacturer": safety_data.get("manufacturer"),
                    "order_index": idx,
                },
            )

            # Import safety system features
            features = safety_data.get("features", [])
            for feat_idx, feature_name in enumerate(features):
                StationSafetySystemFeature.objects.update_or_create(
                    safety_system=safety_system,
                    feature_name=feature_name,
                    defaults={"order_index": feat_idx},
                )

        return result

