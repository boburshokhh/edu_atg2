from __future__ import annotations

from django.http import JsonResponse
from django.db import connection, transaction
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.views import APIView

from apps.courses.models import (
    CourseProgram,
    CourseProgramLearningOutcome,
    CourseProgramRequirement,
    CourseProgramTargetAudience,
    CourseProgramLesson,
    CourseProgramTopic,
    CourseProgramLessonTest,
    FinalTest,
)
from apps.stations.models import (
    Department,
    Station,
    StationEquipment,
    StationGasSupplySource,
    StationNormativeDoc,
    StationPhoto,
    StationPromoVideo,
    StationSafetySystem,
    StationSafetySystemFeature,
    StationSpecification,
)
from apps.stations.serializers import (
    DepartmentSerializer,
    StationEquipmentSerializer,
    StationGasSupplySourceSerializer,
    StationNormativeDocSerializer,
    StationPhotoSerializer,
    StationSafetySystemFeatureSerializer,
    StationSafetySystemSerializer,
    StationSerializer,
    StationSpecificationSerializer,
)

import uuid


def _topic_belongs_to_station(station_id: int, topic_id: int) -> bool:
    with connection.cursor() as cur:
        cur.execute(
            """
            select 1
            from course_program_topics t
            join course_program_lessons l on l.id = t.course_program_lesson_id
            join course_programs p on p.id = l.course_program_id
            where p.station_id = %s and t.id = %s
            limit 1
            """,
            [station_id, topic_id],
        )
        return cur.fetchone() is not None


def _topic_file_belongs_to_station(station_id: int, file_id: int) -> bool:
    with connection.cursor() as cur:
        cur.execute(
            """
            select 1
            from course_program_topic_files f
            join course_program_topics t on t.id = f.course_program_topic_id
            join course_program_lessons l on l.id = t.course_program_lesson_id
            join course_programs p on p.id = l.course_program_id
            where p.station_id = %s and f.id = %s
            limit 1
            """,
            [station_id, file_id],
        )
        return cur.fetchone() is not None


def _serialize_course_program(program: CourseProgram) -> dict:
    outcomes = list(
        CourseProgramLearningOutcome.objects.filter(course_program_id=program.id)
        .order_by("order_index", "id")
        .values_list("outcome_text", flat=True)
    )
    requirements = list(
        CourseProgramRequirement.objects.filter(course_program_id=program.id)
        .order_by("order_index", "id")
        .values_list("requirement_text", flat=True)
    )
    target_audience = list(
        CourseProgramTargetAudience.objects.filter(course_program_id=program.id)
        .order_by("order_index", "id")
        .values_list("audience_text", flat=True)
    )

    final_test = (
        FinalTest.objects.filter(course_program_id=program.id, is_active=True)
        .order_by("id")
        .values("title", "questions_count")
        .first()
    )

    lessons = list(
        CourseProgramLesson.objects.filter(course_program_id=program.id, is_active=True)
        .order_by("order_index", "id")
        .values("id", "lesson_key", "title", "duration", "order_index")
    )
    lesson_ids = [l["id"] for l in lessons]

    topics = []
    if lesson_ids:
        # Use direct database column name since ForeignKey has custom db_column
        topics = list(
            CourseProgramTopic.objects.filter(lesson__id__in=lesson_ids, is_active=True)
            .order_by("lesson__id", "order_index", "id")
            .values("id", "lesson__id", "topic_key", "code", "title", "duration", "order_index")
        )
        # Rename lesson__id to lesson_id for compatibility with rest of code
        for t in topics:
            t["lesson_id"] = t.pop("lesson__id")

    topic_ids = [t["id"] for t in topics]
    files_by_topic: dict[int, list[dict]] = {}
    if topic_ids:
        with connection.cursor() as cur:
            cur.execute(
                """
                select
                    id,
                    course_program_topic_id,
                    title,
                    original_name,
                    object_key,
                    file_type,
                    is_main,
                    order_index,
                    file_size,
                    mime_type
                from course_program_topic_files
                where is_active = true and course_program_topic_id = any(%s)
                order by course_program_topic_id, order_index, id
                """,
                [topic_ids],
            )
            for (
                file_id,
                cpt_id,
                title,
                original_name,
                object_key,
                file_type,
                is_main,
                order_index,
                file_size,
                mime_type,
            ) in cur.fetchall():
                files_by_topic.setdefault(cpt_id, []).append(
                    {
                        "id": file_id,
                        "title": title or "",
                        "originalName": original_name,
                        "objectKey": object_key,
                        "fileType": file_type,
                        "isMain": bool(is_main),
                        "orderIndex": int(order_index or 0),
                        "fileSize": file_size,
                        "mimeType": mime_type,
                    }
                )

    topics_by_lesson: dict[int, list[dict]] = {}
    for t in topics:
        topics_by_lesson.setdefault(t["lesson_id"], []).append(
            {
                "id": t["id"],
                "topicKey": t["topic_key"],
                "code": t["code"],
                "title": t["title"],
                "duration": t["duration"],
                "orderIndex": t["order_index"],
                "files": files_by_topic.get(t["id"], []),
            }
        )

    # Get lesson tests
    lesson_tests_by_lesson: dict[int, dict] = {}
    if lesson_ids:
        lesson_tests = list(
            CourseProgramLessonTest.objects.filter(lesson__id__in=lesson_ids, is_active=True)
            .order_by("lesson__id", "id")
            .values("id", "lesson__id", "title", "questions_count")
        )
        for lt in lesson_tests:
            lesson_tests_by_lesson[lt["lesson__id"]] = {
                "title": lt["title"],
                "questionsCount": lt["questions_count"],
            }

    lessons_out = []
    for l in lessons:
        lesson_test = lesson_tests_by_lesson.get(l["id"])
        lessons_out.append(
            {
                "id": l["id"],
                "lessonKey": l["lesson_key"],
                "title": l["title"],
                "duration": l["duration"],
                "orderIndex": l["order_index"],
                "topics": topics_by_lesson.get(l["id"], []),
                "test": lesson_test if lesson_test else None,
            }
        )

    course_program = {
        "id": program.id,
        "stationId": program.station_id,
        "title": program.title,
        "description": program.description,
        "duration": program.duration,
        "format": program.format,
        "isActive": program.is_active,
        "orderIndex": program.order_index,
        "topicsCount": program.topics_count,
        "lessonsCount": program.lessons_count,
        "testsCount": program.tests_count,
        "learningOutcomes": outcomes,
        "requirements": requirements,
        "targetAudience": target_audience,
        "finalTest": (
            {"title": final_test["title"], "questionsCount": final_test["questions_count"]}
            if final_test
            else None
        ),
        "lessons": lessons_out,
    }

    return course_program


class IsAdmin(IsAuthenticated):
    """Permission class to check if user is admin"""

    def has_permission(self, request, view):
        import logging
        logger = logging.getLogger(__name__)
        
        auth_header = request.headers.get('Authorization', 'None')
        logger.info(f"[IsAdmin] Checking permission. User: {request.user}, Auth header: {auth_header[:50]}...")
        
        # Check authentication first
        if not request.user or not hasattr(request.user, 'id'):
            logger.warning(f"[IsAdmin] User not authenticated. User: {request.user}")
            raise AuthenticationFailed("Учетные данные не были предоставлены.")
            
        if not hasattr(request.user, 'role'):
            logger.warning(f"[IsAdmin] User {request.user.id} has no 'role' attribute")
            raise PermissionDenied("Пользователь не имеет роли.")
            
        is_admin = request.user.role == "admin"
        logger.info(f"[IsAdmin] User {request.user.id} role: {request.user.role}, Is admin: {is_admin}")
        
        if not is_admin:
            raise PermissionDenied("Требуется роль администратора.")
            
        return True


class StationsListView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request):
        rows = list(
            Station.objects.all()
            .order_by("id")
            .values(
                "id",
                "name",
                "short_name",
                "description",
                "image",
                "tech_map_image",
                "power",
                "commission_date",
                "courses_count",
                "status",
                "location",
                "type",
                "design_capacity",
                "gas_pressure",
                "distance_from_border",
                "pipeline_diameter",
                "input_pressure",
                "output_pressure",
                "parallel_lines",
            )
        )
        return JsonResponse({"data": rows})


class StationDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, id: int):
        station = Station.objects.filter(id=id).values().first()
        if not station:
            return JsonResponse({"error": "Station not found"}, status=404)

        equipment = list(StationEquipment.objects.filter(station_id=id).order_by("order_index").values())
        specs = list(StationSpecification.objects.filter(station_id=id).order_by("order_index").values())
        safety = list(StationSafetySystem.objects.filter(station_id=id).order_by("order_index").values())
        gas_sources = list(StationGasSupplySource.objects.filter(station_id=id).order_by("order_index").values())
        photos = list(StationPhoto.objects.filter(station_id=id).order_by("order_index").values())
        docs = list(StationNormativeDoc.objects.filter(station_id=id).values())
        
        # Add features to safety systems (with full data including IDs)
        for safety_system in safety:
            safety_id = safety_system["id"]
            features = list(
                StationSafetySystemFeature.objects.filter(safety_system_id=safety_id)
                .order_by("order_index")
                .values("id", "feature_name", "order_index")
            )
            safety_system["features"] = features
            # Also keep feature_names array for backward compatibility
            safety_system["feature_names"] = [f["feature_name"] for f in features]

        return JsonResponse({
            "station": station,
            "equipment": equipment,
            "specs": specs,
            "safety": safety,
            "gas_sources": gas_sources,
            "photos": photos,
            "normativeDocs": docs,
        })


class StationCourseProgramView(APIView):
    """
    Public endpoint used by StationCourses/LessonViewer.
    Returns course program structure for a station.
    """

    permission_classes = [AllowAny]

    def get(self, _request, id: int):
        program = (
            CourseProgram.objects.filter(station_id=id, is_active=True)
            # Prefer the newest active program (avoid older empty duplicates)
            .order_by("-updated_at", "-id")
            .first()
        )
        if not program:
            return JsonResponse({"courseProgram": None})

        return JsonResponse({"courseProgram": _serialize_course_program(program)})


class StationCourseProgramUpdateView(APIView):
    """
    Admin endpoint: update program metadata + outcomes/requirements/audience + lesson/topic structure.
    Keys (lessonKey/topicKey) are stable identifiers and must remain unchanged once created.
    """

    permission_classes = [IsAdmin]

    def put(self, request, id: int):
        data = request.data or {}

        with transaction.atomic():
            program_id = data.get("id") or data.get("programId") or data.get("program_id")
            program = None
            if program_id:
                program = CourseProgram.objects.filter(id=program_id, station_id=id).first()

            if not program:
                # pick any program for station (prefer active)
                program = (
                    CourseProgram.objects.filter(station_id=id, is_active=True)
                    .order_by("-updated_at", "-id")
                    .first()
                ) or CourseProgram.objects.filter(station_id=id).order_by("id").first()

            if not program:
                program = CourseProgram.objects.create(
                    station_id=id,
                    title=data.get("title") or f"Программа обучения станции {id}",
                    description=data.get("description") or "",
                    duration=data.get("duration") or "",
                    format=data.get("format") or "Онлайн",
                    is_active=bool(data.get("isActive", True)),
                    order_index=int(data.get("orderIndex") or 0),
                )
            else:
                # update metadata
                for field, key in [
                    ("title", "title"),
                    ("description", "description"),
                    ("duration", "duration"),
                    ("format", "format"),
                ]:
                    if key in data:
                        setattr(program, field, data.get(key))
                if "isActive" in data:
                    program.is_active = bool(data.get("isActive"))
                if "orderIndex" in data:
                    program.order_index = int(data.get("orderIndex") or 0)
                program.save()

            # Ensure only one active program per station (prevents duplicates)
            if getattr(program, "is_active", False):
                CourseProgram.objects.filter(station_id=id, is_active=True).exclude(id=program.id).update(
                    is_active=False
                )

            # Replace learning outcomes / requirements / target audience lists
            if "learningOutcomes" in data:
                CourseProgramLearningOutcome.objects.filter(course_program_id=program.id).delete()
                for idx, text in enumerate(data.get("learningOutcomes") or []):
                    if not str(text).strip():
                        continue
                    CourseProgramLearningOutcome.objects.create(
                        course_program_id=program.id,
                        outcome_text=str(text).strip(),
                        order_index=idx,
                    )

            if "requirements" in data:
                CourseProgramRequirement.objects.filter(course_program_id=program.id).delete()
                for idx, text in enumerate(data.get("requirements") or []):
                    if not str(text).strip():
                        continue
                    CourseProgramRequirement.objects.create(
                        course_program_id=program.id,
                        requirement_text=str(text).strip(),
                        order_index=idx,
                    )

            if "targetAudience" in data:
                CourseProgramTargetAudience.objects.filter(course_program_id=program.id).delete()
                for idx, text in enumerate(data.get("targetAudience") or []):
                    if not str(text).strip():
                        continue
                    CourseProgramTargetAudience.objects.create(
                        course_program_id=program.id,
                        audience_text=str(text).strip(),
                        order_index=idx,
                    )

            # Optional final test (single)
            if "finalTest" in data:
                final_data = data.get("finalTest")
                FinalTest.objects.filter(course_program_id=program.id).delete()
                if isinstance(final_data, dict) and final_data.get("title"):
                    FinalTest.objects.create(
                        course_program_id=program.id,
                        title=str(final_data.get("title")),
                        questions_count=int(final_data.get("questionsCount") or final_data.get("questions") or 0),
                        is_active=bool(final_data.get("isActive", True)),
                    )

            # Lessons/topics structure
            if "lessons" in data:
                incoming_lessons = data.get("lessons") or []
                existing_lessons = list(CourseProgramLesson.objects.filter(course_program_id=program.id))
                existing_by_key = {l.lesson_key: l for l in existing_lessons if l.lesson_key}
                keep_lesson_keys: set[str] = set()

                for lesson_payload in incoming_lessons:
                    if not isinstance(lesson_payload, dict):
                        continue
                    lesson_key = lesson_payload.get("lessonKey") or lesson_payload.get("lesson_key")
                    if not lesson_key:
                        lesson_key = f"lesson_{uuid.uuid4().hex}"

                    keep_lesson_keys.add(lesson_key)

                    lesson_obj = existing_by_key.get(lesson_key)
                    if not lesson_obj:
                        lesson_obj = CourseProgramLesson.objects.create(
                            course_program_id=program.id,
                            lesson_key=lesson_key,
                            title=str(lesson_payload.get("title") or ""),
                            duration=lesson_payload.get("duration") or None,
                            order_index=int(lesson_payload.get("orderIndex") or lesson_payload.get("order_index") or 0),
                            is_active=bool(lesson_payload.get("isActive", True)),
                        )
                    else:
                        if "title" in lesson_payload:
                            lesson_obj.title = str(lesson_payload.get("title") or "")
                        if "duration" in lesson_payload:
                            lesson_obj.duration = lesson_payload.get("duration") or None
                        if "orderIndex" in lesson_payload or "order_index" in lesson_payload:
                            lesson_obj.order_index = int(
                                lesson_payload.get("orderIndex") or lesson_payload.get("order_index") or 0
                            )
                        if "isActive" in lesson_payload:
                            lesson_obj.is_active = bool(lesson_payload.get("isActive"))
                        lesson_obj.save()

                    # topics per lesson
                    if "topics" in lesson_payload:
                        incoming_topics = lesson_payload.get("topics") or []
                        existing_topics = list(
                            CourseProgramTopic.objects.filter(lesson=lesson_obj)
                        )
                        existing_topics_by_key = {t.topic_key: t for t in existing_topics if t.topic_key}
                        keep_topic_keys: set[str] = set()

                        for topic_payload in incoming_topics:
                            if not isinstance(topic_payload, dict):
                                continue
                            topic_key = topic_payload.get("topicKey") or topic_payload.get("topic_key")
                            if not topic_key:
                                topic_key = f"topic_{uuid.uuid4().hex}"

                            keep_topic_keys.add(topic_key)
                            topic_obj = existing_topics_by_key.get(topic_key)

                            if not topic_obj:
                                CourseProgramTopic.objects.create(
                                    lesson=lesson_obj,
                                    topic_key=topic_key,
                                    code=topic_payload.get("code") or None,
                                    title=str(topic_payload.get("title") or ""),
                                    duration=topic_payload.get("duration") or None,
                                    order_index=int(topic_payload.get("orderIndex") or topic_payload.get("order_index") or 0),
                                    is_active=bool(topic_payload.get("isActive", True)),
                                )
                            else:
                                if "code" in topic_payload:
                                    topic_obj.code = topic_payload.get("code") or None
                                if "title" in topic_payload:
                                    topic_obj.title = str(topic_payload.get("title") or "")
                                if "duration" in topic_payload:
                                    topic_obj.duration = topic_payload.get("duration") or None
                                if "orderIndex" in topic_payload or "order_index" in topic_payload:
                                    topic_obj.order_index = int(
                                        topic_payload.get("orderIndex") or topic_payload.get("order_index") or 0
                                    )
                                if "isActive" in topic_payload:
                                    topic_obj.is_active = bool(topic_payload.get("isActive"))
                                topic_obj.save()

                        # soft-deactivate removed topics
                        (
                            CourseProgramTopic.objects.filter(lesson=lesson_obj)
                            .exclude(topic_key__in=list(keep_topic_keys))
                            .update(is_active=False)
                        )

                    # Lesson test
                    if "test" in lesson_payload:
                        test_data = lesson_payload.get("test")
                        CourseProgramLessonTest.objects.filter(lesson=lesson_obj).delete()
                        if isinstance(test_data, dict) and test_data.get("title"):
                            CourseProgramLessonTest.objects.create(
                                lesson=lesson_obj,
                                title=str(test_data.get("title")),
                                questions_count=int(test_data.get("questionsCount") or test_data.get("questions") or 0),
                                is_active=bool(test_data.get("isActive", True)),
                            )
                    elif "test" in lesson_payload and lesson_payload.get("test") is None:
                        # Explicitly remove test if test is null
                        CourseProgramLessonTest.objects.filter(lesson=lesson_obj).delete()

                # soft-deactivate removed lessons (and their topics via cascade? keep topics but inactive)
                (
                    CourseProgramLesson.objects.filter(course_program_id=program.id)
                    .exclude(lesson_key__in=list(keep_lesson_keys))
                    .update(is_active=False)
                )

        return JsonResponse({"courseProgram": _serialize_course_program(program)})


class StationCourseProgramTopicFilesView(APIView):
    """
    Public: list files for a course program topic.
    """

    permission_classes = [AllowAny]

    def get(self, _request, id: int, topic_id: int):
        if not _topic_belongs_to_station(id, topic_id):
            return JsonResponse({"error": "Topic not found"}, status=404)

        with connection.cursor() as cur:
            cur.execute(
                """
                select
                    id,
                    title,
                    original_name,
                    object_key,
                    file_type,
                    is_main,
                    order_index,
                    file_size,
                    mime_type,
                    is_active
                from course_program_topic_files
                where course_program_topic_id = %s
                order by order_index, id
                """,
                [topic_id],
            )
            rows = []
            for (
                file_id,
                title,
                original_name,
                object_key,
                file_type,
                is_main,
                order_index,
                file_size,
                mime_type,
                is_active,
            ) in cur.fetchall():
                rows.append(
                    {
                        "id": file_id,
                        "title": title or "",
                        "originalName": original_name,
                        "objectKey": object_key,
                        "fileType": file_type,
                        "isMain": bool(is_main),
                        "orderIndex": int(order_index or 0),
                        "fileSize": file_size,
                        "mimeType": mime_type,
                        "isActive": bool(is_active),
                    }
                )

        return JsonResponse({"data": rows})


class StationCourseProgramTopicFileCreateView(APIView):
    """
    Admin: create a file record for a topic (file is uploaded to MinIO separately).
    Payload: { title?, originalName, objectKey, fileType: pdf|video|document, isMain?, orderIndex?, fileSize?, mimeType? }
    """

    permission_classes = [IsAdmin]

    def post(self, request, id: int, topic_id: int):
        if not _topic_belongs_to_station(id, topic_id):
            return JsonResponse({"error": "Topic not found"}, status=404)

        data = request.data or {}
        original_name = (data.get("originalName") or data.get("original_name") or "").strip()
        object_key = (data.get("objectKey") or data.get("object_key") or "").lstrip("/")
        file_type = (data.get("fileType") or data.get("file_type") or "").strip().lower()
        title = (data.get("title") or "").strip()
        is_main = bool(data.get("isMain") or data.get("is_main") or False)
        order_index = int(data.get("orderIndex") or data.get("order_index") or 0)
        file_size = data.get("fileSize") or data.get("file_size")
        mime_type = data.get("mimeType") or data.get("mime_type")

        if not original_name:
            return JsonResponse({"error": "Missing originalName"}, status=400)
        if not object_key:
            return JsonResponse({"error": "Missing objectKey"}, status=400)
        if file_type not in ("pdf", "video", "document"):
            return JsonResponse({"error": "Invalid fileType"}, status=400)
        # Only PDF files can be marked as main
        if is_main and file_type != "pdf":
            is_main = False

        with transaction.atomic():
            # Allow multiple main files per topic (removed single-main restriction)

            with connection.cursor() as cur:
                cur.execute(
                    """
                    insert into course_program_topic_files
                      (course_program_topic_id, title, original_name, object_key, file_type, is_main, order_index, file_size, mime_type, is_active)
                    values
                      (%s, %s, %s, %s, %s, %s, %s, %s, %s, true)
                    returning id
                    """,
                    [topic_id, title or None, original_name, object_key, file_type, is_main, order_index, file_size, mime_type],
                )
                new_id = cur.fetchone()[0]

        return JsonResponse(
            {
                "data": {
                    "id": new_id,
                    "title": title,
                    "originalName": original_name,
                    "objectKey": object_key,
                    "fileType": file_type,
                    "isMain": is_main,
                    "orderIndex": order_index,
                    "fileSize": file_size,
                    "mimeType": mime_type,
                    "isActive": True,
                }
            }
        )


class StationCourseProgramTopicFileUpdateView(APIView):
    """
    Admin: update file record metadata (and main flag).
    """

    permission_classes = [IsAdmin]

    def put(self, request, id: int, topic_id: int, file_id: int):
        if not _topic_belongs_to_station(id, topic_id):
            return JsonResponse({"error": "Topic not found"}, status=404)
        if not _topic_file_belongs_to_station(id, file_id):
            return JsonResponse({"error": "File not found"}, status=404)
        # Ensure file belongs to this topic
        with connection.cursor() as cur:
            cur.execute(
                "select 1 from course_program_topic_files where id=%s and course_program_topic_id=%s limit 1",
                [file_id, topic_id],
            )
            if cur.fetchone() is None:
                return JsonResponse({"error": "File not found"}, status=404)

        data = request.data or {}
        title = data.get("title")
        order_index = data.get("orderIndex") or data.get("order_index")
        is_main = data.get("isMain") if "isMain" in data else data.get("is_main")
        is_active = data.get("isActive") if "isActive" in data else data.get("is_active")

        with transaction.atomic():
            # Read current topic_id and file_type for main handling
            with connection.cursor() as cur:
                cur.execute(
                    "select course_program_topic_id, file_type from course_program_topic_files where id = %s",
                    [file_id],
                )
                row = cur.fetchone()
                if not row:
                    return JsonResponse({"error": "File not found"}, status=404)
                topic_id, file_type = row

            if is_main is not None:
                is_main_bool = bool(is_main)
                # Only PDF files can be marked as main
                if is_main_bool and str(file_type) != "pdf":
                    is_main_bool = False
                # Allow multiple main files per topic (removed single-main restriction)
            else:
                is_main_bool = None

            sets = []
            params = []
            if title is not None:
                sets.append("title = %s")
                params.append(str(title))
            if order_index is not None:
                sets.append("order_index = %s")
                params.append(int(order_index or 0))
            if is_active is not None:
                sets.append("is_active = %s")
                params.append(bool(is_active))
            if is_main_bool is not None:
                sets.append("is_main = %s")
                params.append(is_main_bool)

            if sets:
                with connection.cursor() as cur:
                    cur.execute(
                        f"update course_program_topic_files set {', '.join(sets)}, updated_at = CURRENT_TIMESTAMP where id = %s",
                        [*params, file_id],
                    )

        return JsonResponse({"ok": True})


class StationCourseProgramTopicFileDeleteView(APIView):
    """
    Admin: delete record (soft-delete), optionally delete MinIO object.
    """

    permission_classes = [IsAdmin]

    def delete(self, request, id: int, topic_id: int, file_id: int):
        if not _topic_belongs_to_station(id, topic_id):
            return JsonResponse({"error": "Topic not found"}, status=404)
        if not _topic_file_belongs_to_station(id, file_id):
            return JsonResponse({"error": "File not found"}, status=404)
        with connection.cursor() as cur:
            cur.execute(
                "select 1 from course_program_topic_files where id=%s and course_program_topic_id=%s limit 1",
                [file_id, topic_id],
            )
            if cur.fetchone() is None:
                return JsonResponse({"error": "File not found"}, status=404)

        delete_object = (request.query_params.get("deleteObject") or "0") in ("1", "true", "True", "yes", "YES")

        with transaction.atomic():
            with connection.cursor() as cur:
                cur.execute(
                    "select object_key from course_program_topic_files where id = %s",
                    [file_id],
                )
                row = cur.fetchone()
                object_key = row[0] if row else None

            with connection.cursor() as cur:
                cur.execute(
                    "update course_program_topic_files set is_active = false, updated_at = CURRENT_TIMESTAMP where id = %s",
                    [file_id],
                )

        if delete_object and object_key:
            try:
                from django.conf import settings
                from apps.files.minio_client import s3_client

                s3_client().delete_object(Bucket=settings.MINIO_BUCKET, Key=str(object_key))
            except Exception:
                pass

        return JsonResponse({"ok": True, "deleted": True, "objectKey": object_key})


class StationPromoVideoView(APIView):
    """
    Public: return active promo video metadata (object key).
    Frontend will request presigned GET for playback (supports Range in browser).
    """

    permission_classes = [AllowAny]

    def get(self, _request, id: int):
        row = (
            StationPromoVideo.objects.filter(station_id=id, is_active=True)
            .order_by("-updated_at", "-id")
            .values("id", "station_id", "title", "object_key")
            .first()
        )
        if not row:
            return JsonResponse({"video": None})
        return JsonResponse(
            {
                "video": {
                    "id": row["id"],
                    "stationId": row["station_id"],
                    "title": row.get("title") or "",
                    "objectKey": row["object_key"],
                }
            }
        )


class StationPromoVideoUpdateView(APIView):
    """
    Admin: set/replace promo video for a station.
    Payload: { title?: str, objectKey: str }
    """

    permission_classes = [IsAdmin]

    def put(self, request, id: int):
        data = request.data or {}
        object_key = (data.get("objectKey") or data.get("object_key") or "").lstrip("/")
        if not object_key:
            return JsonResponse({"error": "Missing objectKey"}, status=400)
        title = data.get("title") or ""

        with transaction.atomic():
            # deactivate existing active promo video
            StationPromoVideo.objects.filter(station_id=id, is_active=True).update(is_active=False)
            video = StationPromoVideo.objects.create(
                station_id=id,
                title=title,
                object_key=object_key,
                is_active=True,
            )

        return JsonResponse(
            {
                "video": {
                    "id": video.id,
                    "stationId": id,
                    "title": video.title or "",
                    "objectKey": video.object_key,
                }
            }
        )


class StationPromoVideoDeleteView(APIView):
    """
    Admin: delete promo video record (optionally also delete object from MinIO via ?deleteObject=1).
    """

    permission_classes = [IsAdmin]

    def delete(self, request, id: int):
        delete_object = (request.query_params.get("deleteObject") or "0") in ("1", "true", "True", "yes", "YES")

        video = (
            StationPromoVideo.objects.filter(station_id=id, is_active=True)
            .order_by("-updated_at", "-id")
            .first()
        )
        if not video:
            return JsonResponse({"ok": True, "deleted": False})

        object_key = video.object_key
        with transaction.atomic():
            video.delete()

        if delete_object:
            try:
                from django.conf import settings
                from apps.files.minio_client import s3_client

                s3_client().delete_object(Bucket=settings.MINIO_BUCKET, Key=object_key)
            except Exception:
                # keep delete idempotent
                pass

        return JsonResponse({"ok": True, "deleted": True, "objectKey": object_key})


class StationEquipmentView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, id: int):
        rows = list(StationEquipment.objects.filter(station_id=id).order_by("order_index").values())
        return JsonResponse({"data": rows})


class StationSpecsView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, id: int):
        rows = list(StationSpecification.objects.filter(station_id=id).order_by("order_index").values())
        return JsonResponse({"data": rows})


class StationSafetyView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, id: int):
        rows = list(StationSafetySystem.objects.filter(station_id=id).order_by("order_index").values())
        return JsonResponse({"data": rows})


# CRUD Views for Stations
class StationCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = StationSerializer(data=request.data)
        if serializer.is_valid():
            station = serializer.save()
            return JsonResponse(StationSerializer(station).data, status=201)
        return JsonResponse(serializer.errors, status=400)


class StationUpdateView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, id: int):
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[StationUpdateView] User: {request.user}, Authenticated: {request.user.is_authenticated if hasattr(request.user, 'is_authenticated') else 'N/A'}")
        logger.info(f"[StationUpdateView] Auth header: {request.headers.get('Authorization', 'None')[:50]}")
        
        try:
            station = Station.objects.get(id=id)
        except Station.DoesNotExist:
            return JsonResponse({"error": "Station not found"}, status=404)

        serializer = StationSerializer(station, data=request.data, partial=True)
        if serializer.is_valid():
            station = serializer.save()
            
            # Automatically create/update StationPhoto records for image and tech_map_image
            self._sync_station_photos(station, request.data)
            
            return JsonResponse(StationSerializer(station).data)
        return JsonResponse(serializer.errors, status=400)
    
    def _sync_station_photos(self, station, data):
        """Create or update StationPhoto records for image and tech_map_image"""
        # Handle station image (view: 'station_image')
        if 'image' in data and data['image']:
            self._create_or_update_photo(
                station=station,
                view='station_image',
                image_url=data['image'],
                title='Фото станции'
            )
        
        # Handle tech map image (view: 'tech_map_image')
        if 'tech_map_image' in data and data['tech_map_image']:
            self._create_or_update_photo(
                station=station,
                view='tech_map_image',
                image_url=data['tech_map_image'],
                title='Техническая карта'
            )
    
    def _create_or_update_photo(self, station, view, image_url, title):
        """Create or update a StationPhoto record"""
        try:
            # Try to find existing photo with this view type
            photo = StationPhoto.objects.filter(station_id=station.id, view=view).first()
            
            if photo:
                # Update existing photo
                photo.image_url = image_url
                photo.title = title
                photo.save()
            else:
                # Create new photo
                StationPhoto.objects.create(
                    station=station,
                    view=view,
                    image_url=image_url,
                    title=title,
                    order_index=0
                )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[StationUpdateView] Error syncing photo (view={view}): {e}")


class StationDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id: int):
        try:
            station = Station.objects.get(id=id)
        except Station.DoesNotExist:
            return JsonResponse({"error": "Station not found"}, status=404)

        station.delete()
        return JsonResponse({"success": True}, status=200)


# CRUD Views for Equipment
class StationEquipmentCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id: int):
        try:
            Station.objects.get(id=id)
        except Station.DoesNotExist:
            return JsonResponse({"error": "Station not found"}, status=404)

        data = request.data.copy()
        data["station"] = id
        serializer = StationEquipmentSerializer(data=data)
        if serializer.is_valid():
            equipment = serializer.save()
            return JsonResponse(StationEquipmentSerializer(equipment).data, status=201)
        return JsonResponse(serializer.errors, status=400)


class StationEquipmentUpdateView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, id: int, equipment_id: int):
        try:
            equipment = StationEquipment.objects.get(id=equipment_id, station_id=id)
        except StationEquipment.DoesNotExist:
            return JsonResponse({"error": "Equipment not found"}, status=404)

        serializer = StationEquipmentSerializer(equipment, data=request.data, partial=True)
        if serializer.is_valid():
            equipment = serializer.save()
            return JsonResponse(StationEquipmentSerializer(equipment).data)
        return JsonResponse(serializer.errors, status=400)


class StationEquipmentDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id: int, equipment_id: int):
        try:
            equipment = StationEquipment.objects.get(id=equipment_id, station_id=id)
        except StationEquipment.DoesNotExist:
            return JsonResponse({"error": "Equipment not found"}, status=404)

        equipment.delete()
        return JsonResponse({"success": True}, status=200)


# CRUD Views for Specifications
class StationSpecificationCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id: int):
        try:
            Station.objects.get(id=id)
        except Station.DoesNotExist:
            return JsonResponse({"error": "Station not found"}, status=404)

        data = request.data.copy()
        data["station"] = id
        serializer = StationSpecificationSerializer(data=data)
        if serializer.is_valid():
            spec = serializer.save()
            return JsonResponse(StationSpecificationSerializer(spec).data, status=201)
        return JsonResponse(serializer.errors, status=400)


class StationSpecificationUpdateView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, id: int, spec_id: int):
        try:
            spec = StationSpecification.objects.get(id=spec_id, station_id=id)
        except StationSpecification.DoesNotExist:
            return JsonResponse({"error": "Specification not found"}, status=404)

        serializer = StationSpecificationSerializer(spec, data=request.data, partial=True)
        if serializer.is_valid():
            spec = serializer.save()
            return JsonResponse(StationSpecificationSerializer(spec).data)
        return JsonResponse(serializer.errors, status=400)


class StationSpecificationDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id: int, spec_id: int):
        try:
            spec = StationSpecification.objects.get(id=spec_id, station_id=id)
        except StationSpecification.DoesNotExist:
            return JsonResponse({"error": "Specification not found"}, status=404)

        spec.delete()
        return JsonResponse({"success": True}, status=200)


# CRUD Views for Safety Systems
class StationSafetySystemCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id: int):
        try:
            Station.objects.get(id=id)
        except Station.DoesNotExist:
            return JsonResponse({"error": "Station not found"}, status=404)

        data = request.data.copy()
        data["station"] = id
        serializer = StationSafetySystemSerializer(data=data)
        if serializer.is_valid():
            safety = serializer.save()
            return JsonResponse(StationSafetySystemSerializer(safety).data, status=201)
        return JsonResponse(serializer.errors, status=400)


class StationSafetySystemUpdateView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, id: int, safety_id: int):
        try:
            safety = StationSafetySystem.objects.get(id=safety_id, station_id=id)
        except StationSafetySystem.DoesNotExist:
            return JsonResponse({"error": "Safety system not found"}, status=404)

        serializer = StationSafetySystemSerializer(safety, data=request.data, partial=True)
        if serializer.is_valid():
            safety = serializer.save()
            return JsonResponse(StationSafetySystemSerializer(safety).data)
        return JsonResponse(serializer.errors, status=400)


class StationSafetySystemDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id: int, safety_id: int):
        try:
            safety = StationSafetySystem.objects.get(id=safety_id, station_id=id)
        except StationSafetySystem.DoesNotExist:
            return JsonResponse({"error": "Safety system not found"}, status=404)

        safety.delete()
        return JsonResponse({"success": True}, status=200)


# CRUD Views for Safety System Features
class StationSafetySystemFeatureCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id: int, safety_id: int):
        try:
            safety = StationSafetySystem.objects.get(id=safety_id, station_id=id)
        except StationSafetySystem.DoesNotExist:
            return JsonResponse({"error": "Safety system not found"}, status=404)

        data = request.data.copy()
        data["safety_system"] = safety_id
        serializer = StationSafetySystemFeatureSerializer(data=data)
        if serializer.is_valid():
            feature = serializer.save()
            return JsonResponse(StationSafetySystemFeatureSerializer(feature).data, status=201)
        return JsonResponse(serializer.errors, status=400)


class StationSafetySystemFeatureUpdateView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, id: int, safety_id: int, feature_id: int):
        try:
            safety = StationSafetySystem.objects.get(id=safety_id, station_id=id)
            feature = StationSafetySystemFeature.objects.get(id=feature_id, safety_system_id=safety_id)
        except (StationSafetySystem.DoesNotExist, StationSafetySystemFeature.DoesNotExist):
            return JsonResponse({"error": "Feature not found"}, status=404)

        serializer = StationSafetySystemFeatureSerializer(feature, data=request.data, partial=True)
        if serializer.is_valid():
            feature = serializer.save()
            return JsonResponse(StationSafetySystemFeatureSerializer(feature).data)
        return JsonResponse(serializer.errors, status=400)


class StationSafetySystemFeatureDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id: int, safety_id: int, feature_id: int):
        try:
            safety = StationSafetySystem.objects.get(id=safety_id, station_id=id)
            feature = StationSafetySystemFeature.objects.get(id=feature_id, safety_system_id=safety_id)
        except (StationSafetySystem.DoesNotExist, StationSafetySystemFeature.DoesNotExist):
            return JsonResponse({"error": "Feature not found"}, status=404)

        feature.delete()
        return JsonResponse({"success": True}, status=200)


# CRUD Views for Gas Supply Sources
class StationGasSupplySourceView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, id: int):
        rows = list(StationGasSupplySource.objects.filter(station_id=id).order_by("order_index").values())
        return JsonResponse({"data": rows})


class StationGasSupplySourceCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id: int):
        try:
            Station.objects.get(id=id)
        except Station.DoesNotExist:
            return JsonResponse({"error": "Station not found"}, status=404)

        data = request.data.copy()
        data["station"] = id
        serializer = StationGasSupplySourceSerializer(data=data)
        if serializer.is_valid():
            source = serializer.save()
            return JsonResponse(StationGasSupplySourceSerializer(source).data, status=201)
        return JsonResponse(serializer.errors, status=400)


class StationGasSupplySourceUpdateView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, id: int, source_id: int):
        try:
            source = StationGasSupplySource.objects.get(id=source_id, station_id=id)
        except StationGasSupplySource.DoesNotExist:
            return JsonResponse({"error": "Gas supply source not found"}, status=404)

        serializer = StationGasSupplySourceSerializer(source, data=request.data, partial=True)
        if serializer.is_valid():
            source = serializer.save()
            return JsonResponse(StationGasSupplySourceSerializer(source).data)
        return JsonResponse(serializer.errors, status=400)


class StationGasSupplySourceDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id: int, source_id: int):
        try:
            source = StationGasSupplySource.objects.get(id=source_id, station_id=id)
        except StationGasSupplySource.DoesNotExist:
            return JsonResponse({"error": "Gas supply source not found"}, status=404)

        source.delete()
        return JsonResponse({"success": True}, status=200)


# CRUD Views for Photos
class StationPhotoCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id: int):
        try:
            Station.objects.get(id=id)
        except Station.DoesNotExist:
            return JsonResponse({"error": "Station not found"}, status=404)

        data = request.data.copy()
        data["station"] = id
        serializer = StationPhotoSerializer(data=data)
        if serializer.is_valid():
            photo = serializer.save()
            return JsonResponse(StationPhotoSerializer(photo).data, status=201)
        return JsonResponse(serializer.errors, status=400)


class StationPhotoUpdateView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, id: int, photo_id: int):
        try:
            photo = StationPhoto.objects.get(id=photo_id, station_id=id)
        except StationPhoto.DoesNotExist:
            return JsonResponse({"error": "Photo not found"}, status=404)

        serializer = StationPhotoSerializer(photo, data=request.data, partial=True)
        if serializer.is_valid():
            photo = serializer.save()
            return JsonResponse(StationPhotoSerializer(photo).data)
        return JsonResponse(serializer.errors, status=400)


class StationPhotoDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id: int, photo_id: int):
        try:
            photo = StationPhoto.objects.get(id=photo_id, station_id=id)
        except StationPhoto.DoesNotExist:
            return JsonResponse({"error": "Photo not found"}, status=404)

        photo.delete()
        return JsonResponse({"success": True}, status=200)


# CRUD Views for Normative Docs
class StationNormativeDocCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, id: int):
        try:
            Station.objects.get(id=id)
        except Station.DoesNotExist:
            return JsonResponse({"error": "Station not found"}, status=404)

        data = request.data.copy()
        data["station"] = id
        serializer = StationNormativeDocSerializer(data=data)
        if serializer.is_valid():
            doc = serializer.save()
            return JsonResponse(StationNormativeDocSerializer(doc).data, status=201)
        return JsonResponse(serializer.errors, status=400)


class StationNormativeDocDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id: int, doc_id: int):
        try:
            doc = StationNormativeDoc.objects.get(id=doc_id, station_id=id)
        except StationNormativeDoc.DoesNotExist:
            return JsonResponse({"error": "Document not found"}, status=404)

        doc.delete()
        return JsonResponse({"success": True}, status=200)


# ============================================================================
# DEPARTMENTS API
# ============================================================================

class DepartmentsListView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request):
        rows = list(
            Department.objects.all()
            .order_by("id")
            .values(
                "id",
                "name",  # Legacy field
                "short_name",
                "description",  # Legacy field
                "name_ru",
                "name_en",
                "description_ru",
                "description_en",
                "image",
                "status",
            )
        )
        return JsonResponse({"data": rows})


class DepartmentDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, id: int):
        department = Department.objects.filter(id=id).values().first()
        if not department:
            return JsonResponse({"error": "Department not found"}, status=404)
        return JsonResponse({"data": department})


class DepartmentCreateView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = DepartmentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                department = serializer.save()
                # Refresh from database to get all fields including timestamps
                department.refresh_from_db()
                return JsonResponse(DepartmentSerializer(department).data, status=201)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        return JsonResponse(serializer.errors, status=400)


class DepartmentUpdateView(APIView):
    permission_classes = [IsAdmin]

    def put(self, request, id: int):
        try:
            department = Department.objects.get(id=id)
        except Department.DoesNotExist:
            return JsonResponse({"error": "Department not found"}, status=404)

        serializer = DepartmentSerializer(department, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                serializer.save()
                # Refresh from database to get updated timestamps
                department.refresh_from_db()
                return JsonResponse(DepartmentSerializer(department).data)
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        return JsonResponse(serializer.errors, status=400)


class DepartmentDeleteView(APIView):
    permission_classes = [IsAdmin]

    def delete(self, request, id: int):
        try:
            department = Department.objects.get(id=id)
        except Department.DoesNotExist:
            return JsonResponse({"error": "Department not found"}, status=404)

        department.delete()
        return JsonResponse({"success": True}, status=200)
