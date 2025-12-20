from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.courses.models import (
    CourseProgram,
    CourseProgramLearningOutcome,
    CourseProgramRequirement,
    CourseProgramTargetAudience,
    CourseProgramLesson,
    CourseProgramTopic,
    FinalTest,
)


class Command(BaseCommand):
    help = "Import station course programs from a generated seed JSON file."

    def add_arguments(self, parser):
        parser.add_argument(
            "--seed-file",
            default="backend_django/apps/courses/seed/course_program_seed.json",
            help="Path to seed JSON (relative to repo root).",
        )
        parser.add_argument(
            "--station-id",
            type=int,
            default=None,
            help="Optional: import only one station_id.",
        )

    def handle(self, *args, **options):
        seed_file = options["seed_file"]
        station_id_filter = options["station_id"]

        repo_root = Path(__file__).resolve().parents[5]
        seed_path = (repo_root / seed_file).resolve()

        if not seed_path.exists():
            raise SystemExit(f"Seed file not found: {seed_path}")

        payload = json.loads(seed_path.read_text(encoding="utf-8"))
        stations = payload.get("stations") or []

        if station_id_filter:
            stations = [s for s in stations if int(s.get("stationId") or 0) == int(station_id_filter)]

        if not stations:
            self.stdout.write("No stations to import.")
            return

        with transaction.atomic():
            for entry in stations:
                station_id = int(entry.get("stationId") or 0)
                program = entry.get("program") or {}
                if not station_id or not program:
                    continue

                self._import_station_program(station_id, program)

        self.stdout.write(self.style.SUCCESS(f"Imported programs: {len(stations)}"))

    def _import_station_program(self, station_id: int, program: dict):
        title = program.get("title") or f"Программа обучения станции {station_id}"

        cp = (
            CourseProgram.objects.filter(station_id=station_id, is_active=True)
            .order_by("order_index", "id")
            .first()
        ) or CourseProgram.objects.filter(station_id=station_id).order_by("id").first()

        if not cp:
            cp = CourseProgram.objects.create(
                station_id=station_id,
                title=title,
                description=program.get("description") or "",
                duration=program.get("duration") or "",
                format=program.get("format") or "Онлайн",
                is_active=bool(program.get("isActive", True)),
                order_index=int(program.get("orderIndex") or 0),
            )
        else:
            cp.title = title
            cp.description = program.get("description") or ""
            cp.duration = program.get("duration") or ""
            cp.format = program.get("format") or "Онлайн"
            cp.is_active = bool(program.get("isActive", True))
            cp.order_index = int(program.get("orderIndex") or 0)
            cp.save()

        # Replace lists
        CourseProgramLearningOutcome.objects.filter(course_program_id=cp.id).delete()
        for idx, text in enumerate(program.get("learningOutcomes") or []):
            if not str(text).strip():
                continue
            CourseProgramLearningOutcome.objects.create(
                course_program_id=cp.id,
                outcome_text=str(text).strip(),
                order_index=idx,
            )

        CourseProgramRequirement.objects.filter(course_program_id=cp.id).delete()
        for idx, text in enumerate(program.get("requirements") or []):
            if not str(text).strip():
                continue
            CourseProgramRequirement.objects.create(
                course_program_id=cp.id,
                requirement_text=str(text).strip(),
                order_index=idx,
            )

        CourseProgramTargetAudience.objects.filter(course_program_id=cp.id).delete()
        for idx, text in enumerate(program.get("targetAudience") or []):
            if not str(text).strip():
                continue
            CourseProgramTargetAudience.objects.create(
                course_program_id=cp.id,
                audience_text=str(text).strip(),
                order_index=idx,
            )

        # Final test (optional)
        FinalTest.objects.filter(course_program_id=cp.id).delete()
        final_test = program.get("finalTest")
        if isinstance(final_test, dict) and final_test.get("title"):
            FinalTest.objects.create(
                course_program_id=cp.id,
                title=str(final_test.get("title")),
                questions_count=int(final_test.get("questionsCount") or final_test.get("questions") or 0),
                is_active=bool(final_test.get("isActive", True)),
            )

        # Lessons/topics
        incoming_lessons = program.get("lessons") or []
        existing_lessons = list(CourseProgramLesson.objects.filter(course_program_id=cp.id))
        existing_by_key = {l.lesson_key: l for l in existing_lessons if l.lesson_key}
        keep_lesson_keys: set[str] = set()

        for lesson_payload in incoming_lessons:
            if not isinstance(lesson_payload, dict):
                continue
            lesson_key = lesson_payload.get("lessonKey") or lesson_payload.get("lesson_key")
            if not lesson_key:
                continue

            keep_lesson_keys.add(lesson_key)
            lesson_obj = existing_by_key.get(lesson_key)

            if not lesson_obj:
                lesson_obj = CourseProgramLesson.objects.create(
                    course_program_id=cp.id,
                    lesson_key=lesson_key,
                    title=str(lesson_payload.get("title") or ""),
                    duration=lesson_payload.get("duration") or None,
                    order_index=int(lesson_payload.get("orderIndex") or lesson_payload.get("order_index") or 0),
                    is_active=bool(lesson_payload.get("isActive", True)),
                )
            else:
                lesson_obj.title = str(lesson_payload.get("title") or "")
                lesson_obj.duration = lesson_payload.get("duration") or None
                lesson_obj.order_index = int(lesson_payload.get("orderIndex") or lesson_payload.get("order_index") or 0)
                lesson_obj.is_active = bool(lesson_payload.get("isActive", True))
                lesson_obj.save()

            # topics
            incoming_topics = lesson_payload.get("topics") or []
            existing_topics = list(CourseProgramTopic.objects.filter(lesson_id=lesson_obj.id))
            existing_topics_by_key = {t.topic_key: t for t in existing_topics if t.topic_key}
            keep_topic_keys: set[str] = set()

            for topic_payload in incoming_topics:
                if not isinstance(topic_payload, dict):
                    continue
                topic_key = topic_payload.get("topicKey") or topic_payload.get("topic_key")
                if not topic_key:
                    continue
                keep_topic_keys.add(topic_key)
                topic_obj = existing_topics_by_key.get(topic_key)
                if not topic_obj:
                    CourseProgramTopic.objects.create(
                        lesson_id=lesson_obj.id,
                        topic_key=topic_key,
                        code=topic_payload.get("code") or None,
                        title=str(topic_payload.get("title") or ""),
                        duration=topic_payload.get("duration") or None,
                        order_index=int(topic_payload.get("orderIndex") or topic_payload.get("order_index") or 0),
                        is_active=bool(topic_payload.get("isActive", True)),
                    )
                else:
                    topic_obj.code = topic_payload.get("code") or None
                    topic_obj.title = str(topic_payload.get("title") or "")
                    topic_obj.duration = topic_payload.get("duration") or None
                    topic_obj.order_index = int(topic_payload.get("orderIndex") or topic_payload.get("order_index") or 0)
                    topic_obj.is_active = bool(topic_payload.get("isActive", True))
                    topic_obj.save()

            CourseProgramTopic.objects.filter(lesson_id=lesson_obj.id).exclude(
                topic_key__in=list(keep_topic_keys)
            ).update(is_active=False)

        CourseProgramLesson.objects.filter(course_program_id=cp.id).exclude(
            lesson_key__in=list(keep_lesson_keys)
        ).update(is_active=False)


