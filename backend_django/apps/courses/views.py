from __future__ import annotations

import json
from datetime import timedelta
from django.db import transaction, models
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.courses.models import (
    Course,
    CourseProgram,
    UserCourse,
    UserCourseProgram,
    UserCourseMaterial,
    CourseComment,
    CourseProgramLessonTest,
    CourseProgramLesson,
    CourseProgramTopic,
    FinalTest,
    TestQuestion,
    TestQuestionOption,
    TestResult,
)
from django.db import connection
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from apps.accounts.models import User, UserProfile, UserSession
from apps.stations.models import Station
from apps.files.minio_client import presign_get


class IsAdmin(IsAuthenticated):
    """Permission class to check if user is admin"""

    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, "id"):
            raise AuthenticationFailed("Учетные данные не были предоставлены.")
        if not hasattr(request.user, "role"):
            raise PermissionDenied("Пользователь не имеет роли.")
        if request.user.role != "admin":
            raise PermissionDenied("Требуется роль администратора.")
        return True


class CoursesByStationView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, stationId: int):
        rows = list(
            Course.objects.filter(station_id=stationId, is_active=True)
            .order_by("-created_at")
            .values("id", "title", "description", "station_id", "duration_hours", "level", "is_active", "icon")
        )
        return JsonResponse({"data": rows})


class CourseDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, courseId: str):
        course = Course.objects.filter(id=courseId).values().first()
        if not course:
            return JsonResponse({"error": "Course not found"}, status=404)
        programs = list(
            CourseProgram.objects.filter(station_id=course["station_id"]).order_by("order_index").values()
        )
        return JsonResponse({"course": course, "programs": programs})


class CourseProgramsView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, courseId: str):
        course = Course.objects.filter(id=courseId).values("station_id").first()
        if not course:
            return JsonResponse({"error": "Course not found"}, status=404)
        programs = list(CourseProgram.objects.filter(station_id=course["station_id"]).order_by("order_index").values())
        return JsonResponse({"data": programs})


class EnrollCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, courseId: str):
        user_id = request.user.id
        now = timezone.now()
        with transaction.atomic():
            UserCourse.objects.get_or_create(
                user_id=user_id,
                course_id=courseId,
                defaults={
                    "progress_percent": 0,
                    "status": "in_progress",
                    "started_at": now,
                },
            )
        return JsonResponse({"success": True})


def _get_course_program_material_totals(course_program_id: int) -> dict:
    lesson_ids = list(
        CourseProgramLesson.objects.filter(course_program_id=course_program_id).values_list("id", flat=True)
    )
    if not lesson_ids:
        return {"total_units": 0, "topics": 0, "files": 0, "tests": 0}

    topics_count = (
        CourseProgramTopic.objects.filter(lesson_id__in=lesson_ids, is_active=True).count()
    )

    files_count = 0
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM course_program_topic_files f
            JOIN course_program_topics t ON t.id = f.course_program_topic_id
            JOIN course_program_lessons l ON l.id = t.course_program_lesson_id
            WHERE l.course_program_id = %s AND f.is_active = true
            """,
            [course_program_id],
        )
        files_count = cursor.fetchone()[0]

    lesson_tests_count = CourseProgramLessonTest.objects.filter(
        lesson_id__in=lesson_ids, is_active=True
    ).count()
    final_tests_count = FinalTest.objects.filter(
        course_program_id=course_program_id, is_active=True
    ).count()
    tests_count = lesson_tests_count + final_tests_count

    materials_count = files_count if files_count > 0 else topics_count
    total_units = materials_count + tests_count
    return {
        "total_units": total_units,
        "topics": topics_count,
        "files": files_count,
        "tests": tests_count,
    }


def _resolve_avatar_url(avatar_url: str | None) -> str | None:
    if not avatar_url:
        return None
    if avatar_url.startswith("avatars/"):
        try:
            return presign_get(avatar_url, expires_in=60 * 60 * 24 * 7)
        except Exception:
            return None
    return avatar_url


def _get_active_users_count(days: int = 30) -> int:
    since = timezone.now() - timedelta(days=days)
    session_users = UserSession.objects.filter(last_activity__gte=since).values("user_id").distinct().count()
    if session_users > 0:
        return session_users
    return UserCourseProgram.objects.filter(last_activity__gte=since).values("user_id").distinct().count()


def _get_material_counts_by_type_for_course(course_program_id: int) -> dict:
    totals = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
    lesson_ids = list(
        CourseProgramLesson.objects.filter(course_program_id=course_program_id).values_list("id", flat=True)
    )
    if lesson_ids:
        topics_count = CourseProgramTopic.objects.filter(lesson_id__in=lesson_ids, is_active=True).count()
        totals["text"] = topics_count
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT f.file_type, COUNT(*)
                FROM course_program_topic_files f
                JOIN course_program_topics t ON t.id = f.course_program_topic_id
                JOIN course_program_lessons l ON l.id = t.course_program_lesson_id
                WHERE l.course_program_id = %s AND f.is_active = true
                GROUP BY f.file_type
                """,
                [course_program_id],
            )
            for file_type, count in cursor.fetchall():
                if file_type == "video":
                    totals["video"] += count
                elif file_type == "pdf":
                    totals["pdf"] += count
                else:
                    totals["presentation"] += count

        totals["test"] = CourseProgramLessonTest.objects.filter(
            lesson_id__in=lesson_ids, is_active=True
        ).count() + FinalTest.objects.filter(course_program_id=course_program_id, is_active=True).count()
    return totals


def _get_course_test_score_stats(course_program_id: int) -> dict:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT AVG(r.score) AS avg_score, COUNT(*) AS total_attempts,
                   SUM(CASE WHEN r.is_passed THEN 1 ELSE 0 END) AS passed_count
            FROM test_results r
            LEFT JOIN course_program_lesson_tests lt ON lt.id = r.test_id AND r.test_type = 'lesson'
            LEFT JOIN course_program_lessons l ON l.id = lt.course_program_lesson_id
            LEFT JOIN final_tests ft ON ft.id = r.test_id AND r.test_type = 'final'
            WHERE (l.course_program_id = %s OR ft.course_program_id = %s)
            """,
            [course_program_id, course_program_id],
        )
        row = cursor.fetchone()
        avg_score = float(row[0]) if row and row[0] is not None else 0
        total_attempts = int(row[1]) if row and row[1] is not None else 0
        passed_count = int(row[2]) if row and row[2] is not None else 0
        pass_rate = round((passed_count / total_attempts) * 100, 2) if total_attempts else 0
        return {
            "average_score": round(avg_score, 2),
            "total_attempts": total_attempts,
            "pass_rate": pass_rate,
        }


def _build_activity_timeline(days: int = 30, course_program_id: int | None = None, user_id: str | None = None) -> list[dict]:
    since = timezone.now().date() - timedelta(days=days - 1)
    dates = [since + timedelta(days=i) for i in range(days)]
    timeline = {d.isoformat(): {"date": d.isoformat(), "enrollments": 0, "completions": 0, "materials_viewed": 0} for d in dates}

    def _fetch_counts(table: str, date_column: str, label: str):
        where_parts = [f"{date_column} >= %s"]
        params = [since]
        if course_program_id is not None:
            where_parts.append("course_program_id = %s")
            params.append(course_program_id)
        if user_id is not None:
            where_parts.append("user_id = %s")
            params.append(user_id)

        where_sql = " AND ".join(where_parts)
        query = f"""
            SELECT DATE({date_column}) AS day, COUNT(*)
            FROM {table}
            WHERE {where_sql}
            GROUP BY day
            ORDER BY day
        """
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            for day, count in cursor.fetchall():
                day_key = day.isoformat()
                if day_key in timeline:
                    timeline[day_key][label] = int(count)

    _fetch_counts("user_course_programs", "created_at", "enrollments")
    _fetch_counts("user_course_programs", "completed_at", "completions")
    _fetch_counts("user_course_materials", "viewed_at", "materials_viewed")

    return list(timeline.values())


def _build_station_activity_timeline(days: int, station_id: int) -> list[dict]:
    program_ids = list(
        CourseProgram.objects.filter(station_id=station_id).values_list("id", flat=True)
    )
    since = timezone.now().date() - timedelta(days=days - 1)
    dates = [since + timedelta(days=i) for i in range(days)]
    timeline = {d.isoformat(): {"date": d.isoformat(), "enrollments": 0, "completions": 0, "materials_viewed": 0} for d in dates}

    if not program_ids:
        return list(timeline.values())

    def _fetch_counts(table: str, date_column: str, label: str):
        query = f"""
            SELECT DATE({date_column}) AS day, COUNT(*)
            FROM {table}
            WHERE {date_column} >= %s AND course_program_id IN %s
            GROUP BY day
            ORDER BY day
        """
        with connection.cursor() as cursor:
            cursor.execute(query, [since, tuple(program_ids)])
            for day, count in cursor.fetchall():
                day_key = day.isoformat()
                if day_key in timeline:
                    timeline[day_key][label] = int(count)

    _fetch_counts("user_course_programs", "created_at", "enrollments")
    _fetch_counts("user_course_programs", "completed_at", "completions")
    _fetch_counts("user_course_materials", "viewed_at", "materials_viewed")

    return list(timeline.values())


class EnrollCourseProgramView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, courseProgramId: int):
        user_id = request.user.id
        now = timezone.now()
        with transaction.atomic():
            enrollment, created = UserCourseProgram.objects.get_or_create(
                user_id=user_id,
                course_program_id=courseProgramId,
                defaults={
                    "progress_percent": 0,
                    "status": "in_progress",
                    "started_at": now,
                },
            )
        return JsonResponse(
            {
                "success": True,
                "created": created,
                "data": {
                    "course_program_id": enrollment.course_program_id,
                    "progress_percent": enrollment.progress_percent,
                    "status": enrollment.status,
                    "started_at": enrollment.started_at.isoformat() if enrollment.started_at else None,
                    "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None,
                },
            }
        )


class CourseProgramProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, courseProgramId: int):
        user_id = request.user.id
        enrollment = UserCourseProgram.objects.filter(
            user_id=user_id, course_program_id=courseProgramId
        ).first()
        if not enrollment:
            return JsonResponse({"error": "Enrollment not found"}, status=404)

        totals = _get_course_program_material_totals(courseProgramId)
        completed_count = UserCourseMaterial.objects.filter(
            user_id=user_id, course_program_id=courseProgramId, is_completed=True
        ).count()

        total_units = totals["total_units"]
        progress_percent = (
            min(100, round((completed_count / total_units) * 100))
            if total_units > 0
            else enrollment.progress_percent
        )

        if progress_percent != enrollment.progress_percent:
            enrollment.progress_percent = progress_percent
        if progress_percent >= 100 and enrollment.status != "completed":
            enrollment.status = "completed"
            enrollment.completed_at = timezone.now()
        elif progress_percent > 0 and enrollment.status == "not_started":
            enrollment.status = "in_progress"
            if not enrollment.started_at:
                enrollment.started_at = timezone.now()
        enrollment.last_activity = timezone.now()
        enrollment.save(update_fields=["progress_percent", "status", "completed_at", "started_at", "last_activity"])

        return JsonResponse(
            {
                "data": {
                    "course_program_id": enrollment.course_program_id,
                    "progress_percent": enrollment.progress_percent,
                    "status": enrollment.status,
                    "started_at": enrollment.started_at.isoformat() if enrollment.started_at else None,
                    "completed_at": enrollment.completed_at.isoformat() if enrollment.completed_at else None,
                    "totals": totals,
                    "completed_units": completed_count,
                }
            }
        )


class CourseProgramMaterialCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, courseProgramId: int):
        user_id = request.user.id
        material_type = request.data.get("material_type")
        material_key = request.data.get("material_key")

        if not material_type or not material_key:
            return JsonResponse({"error": "material_type and material_key are required"}, status=400)

        with transaction.atomic():
            material, _created = UserCourseMaterial.objects.get_or_create(
                user_id=user_id,
                course_program_id=courseProgramId,
                material_type=material_type,
                material_key=material_key,
                defaults={
                    "is_completed": True,
                    "viewed_at": timezone.now(),
                },
            )
            if not material.is_completed:
                material.is_completed = True
                material.viewed_at = timezone.now()
                material.save(update_fields=["is_completed", "viewed_at"])

        return CourseProgramProgressView().get(request, courseProgramId)


class MyCourseProgramsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        enrollments = list(
            UserCourseProgram.objects.filter(user_id=user_id).order_by("-last_activity").values(
                "course_program_id",
                "progress_percent",
                "status",
                "started_at",
                "completed_at",
                "last_activity",
            )
        )
        program_ids = [e["course_program_id"] for e in enrollments]
        programs = {
            p["id"]: p
            for p in CourseProgram.objects.filter(id__in=program_ids).values(
                "id", "title", "description", "station_id", "duration", "lessons_count", "topics_count", "tests_count"
            )
        }

        data = []
        for e in enrollments:
            program = programs.get(e["course_program_id"])
            if not program:
                continue
            data.append(
                {
                    **e,
                    "course_program": program,
                }
            )

        return JsonResponse({"data": data})


class MyCourseProgramsStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        enrollments = UserCourseProgram.objects.filter(user_id=user_id)
        active_courses = enrollments.filter(status="in_progress").count()
        completed_courses = enrollments.filter(status="completed").count()

        material_counts = UserCourseMaterial.objects.filter(
            user_id=user_id, is_completed=True
        ).values("material_type")
        counts_by_type = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
        for row in material_counts.annotate(count=models.Count("id")):
            counts_by_type[row["material_type"]] = row["count"]

        test_scores = TestResult.objects.filter(user_id=user_id).values_list("score", flat=True)
        avg_score = round(sum(test_scores) / len(test_scores), 2) if test_scores else 0

        return JsonResponse(
            {
                "data": {
                    "active_courses": active_courses,
                    "completed_courses": completed_courses,
                    "materials": counts_by_type,
                    "average_test_score": avg_score,
                }
            }
        )


class AdminAnalyticsOverviewView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        total_users = User.objects.count()
        active_users = _get_active_users_count(30)
        total_course_programs = CourseProgram.objects.count()
        total_enrollments = UserCourseProgram.objects.count()
        active_enrollments = UserCourseProgram.objects.filter(status="in_progress").count()
        completed_enrollments = UserCourseProgram.objects.filter(status="completed").count()
        total_materials_viewed = UserCourseMaterial.objects.filter(is_completed=True).count()

        avg_progress = UserCourseProgram.objects.aggregate(avg=models.Avg("progress_percent")).get("avg") or 0
        avg_test_score = TestResult.objects.aggregate(avg=models.Avg("score")).get("avg") or 0

        materials_by_type = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
        for row in UserCourseMaterial.objects.filter(is_completed=True).values("material_type").annotate(count=models.Count("id")):
            materials_by_type[row["material_type"]] = row["count"]

        enrollments_by_status = {
            "not_started": UserCourseProgram.objects.filter(status="not_started").count(),
            "in_progress": active_enrollments,
            "completed": completed_enrollments,
        }

        activity_timeline = _build_activity_timeline(30)

        return JsonResponse(
            {
                "data": {
                    "total_users": total_users,
                    "active_users": active_users,
                    "total_course_programs": total_course_programs,
                    "total_enrollments": total_enrollments,
                    "active_enrollments": active_enrollments,
                    "completed_enrollments": completed_enrollments,
                    "total_materials_viewed": total_materials_viewed,
                    "average_progress": round(float(avg_progress), 2),
                    "average_test_score": round(float(avg_test_score), 2),
                    "materials_by_type": materials_by_type,
                    "enrollments_by_status": enrollments_by_status,
                    "activity_timeline": activity_timeline,
                }
            }
        )


class AdminAnalyticsStationsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        stations = list(Station.objects.all().values("id", "name", "short_name", "status"))

        program_counts = {
            row["station_id"]: row["count"]
            for row in CourseProgram.objects.values("station_id").annotate(count=models.Count("id"))
        }

        enrollment_stats = {}
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT cp.station_id,
                       COUNT(*) AS total,
                       SUM(CASE WHEN ucp.status = 'in_progress' THEN 1 ELSE 0 END) AS active,
                       SUM(CASE WHEN ucp.status = 'completed' THEN 1 ELSE 0 END) AS completed,
                       AVG(ucp.progress_percent) AS avg_progress,
                       SUM(ucp.hours_studied) AS total_hours,
                       COUNT(DISTINCT ucp.user_id) AS unique_users,
                       MAX(ucp.last_activity) AS last_activity
                FROM user_course_programs ucp
                JOIN course_programs cp ON cp.id = ucp.course_program_id
                GROUP BY cp.station_id
                """
            )
            for row in cursor.fetchall():
                (
                    station_id,
                    total,
                    active,
                    completed,
                    avg_progress,
                    total_hours,
                    unique_users,
                    last_activity,
                ) = row
                enrollment_stats[int(station_id)] = {
                    "total": int(total or 0),
                    "active": int(active or 0),
                    "completed": int(completed or 0),
                    "avg_progress": float(avg_progress or 0),
                    "total_hours": float(total_hours or 0),
                    "unique_users": int(unique_users or 0),
                    "last_activity": last_activity.isoformat() if last_activity else None,
                }

        active_users_map = {}
        since = timezone.now() - timedelta(days=30)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT cp.station_id, COUNT(DISTINCT ucp.user_id)
                FROM user_course_programs ucp
                JOIN course_programs cp ON cp.id = ucp.course_program_id
                WHERE ucp.last_activity >= %s
                GROUP BY cp.station_id
                """,
                [since],
            )
            for station_id, count in cursor.fetchall():
                active_users_map[int(station_id)] = int(count or 0)

        test_stats_map = {}
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT cp.station_id,
                       AVG(r.score) AS avg_score,
                       COUNT(*) AS total_attempts,
                       SUM(CASE WHEN r.is_passed THEN 1 ELSE 0 END) AS passed_count
                FROM test_results r
                LEFT JOIN course_program_lesson_tests lt ON lt.id = r.test_id AND r.test_type = 'lesson'
                LEFT JOIN course_program_lessons l ON l.id = lt.course_program_lesson_id
                LEFT JOIN final_tests ft ON ft.id = r.test_id AND r.test_type = 'final'
                LEFT JOIN course_programs cp ON cp.id = COALESCE(l.course_program_id, ft.course_program_id)
                GROUP BY cp.station_id
                """
            )
            for station_id, avg_score, total_attempts, passed_count in cursor.fetchall():
                total_attempts = int(total_attempts or 0)
                passed_count = int(passed_count or 0)
                test_stats_map[int(station_id)] = {
                    "average_score": round(float(avg_score or 0), 2),
                    "total_attempts": total_attempts,
                    "pass_rate": round((passed_count / total_attempts) * 100, 2) if total_attempts else 0,
                }

        totals_by_station = {s["id"]: {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0} for s in stations}
        completed_by_station = {s["id"]: {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0} for s in stations}

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT cp.station_id, COUNT(*)
                FROM course_program_topics t
                JOIN course_program_lessons l ON l.id = t.course_program_lesson_id
                JOIN course_programs cp ON cp.id = l.course_program_id
                WHERE t.is_active = true
                GROUP BY cp.station_id
                """
            )
            for station_id, count in cursor.fetchall():
                totals_by_station[int(station_id)]["text"] = int(count or 0)

            cursor.execute(
                """
                SELECT cp.station_id, f.file_type, COUNT(*)
                FROM course_program_topic_files f
                JOIN course_program_topics t ON t.id = f.course_program_topic_id
                JOIN course_program_lessons l ON l.id = t.course_program_lesson_id
                JOIN course_programs cp ON cp.id = l.course_program_id
                WHERE f.is_active = true
                GROUP BY cp.station_id, f.file_type
                """
            )
            for station_id, file_type, count in cursor.fetchall():
                key = "presentation"
                if file_type == "video":
                    key = "video"
                elif file_type == "pdf":
                    key = "pdf"
                totals_by_station[int(station_id)][key] = int(count or 0)

            cursor.execute(
                """
                SELECT cp.station_id, COUNT(*)
                FROM course_program_lesson_tests lt
                JOIN course_program_lessons l ON l.id = lt.course_program_lesson_id
                JOIN course_programs cp ON cp.id = l.course_program_id
                WHERE lt.is_active = true
                GROUP BY cp.station_id
                """
            )
            for station_id, count in cursor.fetchall():
                totals_by_station[int(station_id)]["test"] += int(count or 0)

            cursor.execute(
                """
                SELECT cp.station_id, COUNT(*)
                FROM final_tests ft
                JOIN course_programs cp ON cp.id = ft.course_program_id
                WHERE ft.is_active = true
                GROUP BY cp.station_id
                """
            )
            for station_id, count in cursor.fetchall():
                totals_by_station[int(station_id)]["test"] += int(count or 0)

            cursor.execute(
                """
                SELECT cp.station_id, ucm.material_type, COUNT(*)
                FROM user_course_materials ucm
                JOIN course_programs cp ON cp.id = ucm.course_program_id
                WHERE ucm.is_completed = true
                GROUP BY cp.station_id, ucm.material_type
                """
            )
            for station_id, material_type, count in cursor.fetchall():
                completed_by_station[int(station_id)][material_type] = int(count or 0)

        data = []
        for station in stations:
            station_id = station["id"]
            enroll = enrollment_stats.get(station_id, {})
            tests = test_stats_map.get(station_id, {})
            totals = totals_by_station.get(station_id, {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0})
            completed = completed_by_station.get(station_id, {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0})
            total_materials = sum(totals.values())
            data.append(
                {
                    "station_id": station_id,
                    "name": station["name"],
                    "short_name": station["short_name"],
                    "status": station["status"],
                    "course_programs": program_counts.get(station_id, 0),
                    "total_enrollments": enroll.get("total", 0),
                    "active_enrollments": enroll.get("active", 0),
                    "completed_enrollments": enroll.get("completed", 0),
                    "unique_users": enroll.get("unique_users", 0),
                    "average_progress": round(float(enroll.get("avg_progress", 0)), 2),
                    "average_test_score": tests.get("average_score", 0),
                    "total_materials": total_materials,
                    "materials_by_type": totals,
                    "completed_materials_by_type": completed,
                    "active_users": active_users_map.get(station_id, 0),
                    "last_activity": enroll.get("last_activity"),
                }
            )

        return JsonResponse({"data": data, "total": len(data)})


class AdminAnalyticsStationDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, stationId: int):
        station = Station.objects.filter(id=stationId).values(
            "id", "name", "short_name", "description", "status", "location", "type"
        ).first()
        if not station:
            return JsonResponse({"error": "Station not found"}, status=404)

        programs = list(
            CourseProgram.objects.filter(station_id=stationId).values(
                "id", "title", "description", "lessons_count", "topics_count", "tests_count"
            )
        )
        program_ids = [p["id"] for p in programs]

        enrollments = UserCourseProgram.objects.filter(course_program_id__in=program_ids)
        total_enrollments = enrollments.count()
        status_counts = {
            "not_started": enrollments.filter(status="not_started").count(),
            "in_progress": enrollments.filter(status="in_progress").count(),
            "completed": enrollments.filter(status="completed").count(),
        }
        unique_users = enrollments.values("user_id").distinct().count()
        avg_progress = enrollments.aggregate(avg=models.Avg("progress_percent")).get("avg") or 0
        total_hours = enrollments.aggregate(total=models.Sum("hours_studied")).get("total") or 0

        buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        for progress in enrollments.values_list("progress_percent", flat=True):
            p = progress or 0
            if p <= 20:
                buckets["0-20"] += 1
            elif p <= 40:
                buckets["21-40"] += 1
            elif p <= 60:
                buckets["41-60"] += 1
            elif p <= 80:
                buckets["61-80"] += 1
            else:
                buckets["81-100"] += 1

        totals_by_type = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
        completed_by_type = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT f.file_type, COUNT(*)
                FROM course_program_topic_files f
                JOIN course_program_topics t ON t.id = f.course_program_topic_id
                JOIN course_program_lessons l ON l.id = t.course_program_lesson_id
                JOIN course_programs cp ON cp.id = l.course_program_id
                WHERE f.is_active = true AND cp.station_id = %s
                GROUP BY f.file_type
                """,
                [stationId],
            )
            for file_type, count in cursor.fetchall():
                key = "presentation"
                if file_type == "video":
                    key = "video"
                elif file_type == "pdf":
                    key = "pdf"
                totals_by_type[key] = int(count or 0)

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM course_program_topics t
                JOIN course_program_lessons l ON l.id = t.course_program_lesson_id
                JOIN course_programs cp ON cp.id = l.course_program_id
                WHERE t.is_active = true AND cp.station_id = %s
                """,
                [stationId],
            )
            totals_by_type["text"] = int(cursor.fetchone()[0] or 0)

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM course_program_lesson_tests lt
                JOIN course_program_lessons l ON l.id = lt.course_program_lesson_id
                JOIN course_programs cp ON cp.id = l.course_program_id
                WHERE lt.is_active = true AND cp.station_id = %s
                """,
                [stationId],
            )
            totals_by_type["test"] += int(cursor.fetchone()[0] or 0)

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM final_tests ft
                JOIN course_programs cp ON cp.id = ft.course_program_id
                WHERE ft.is_active = true AND cp.station_id = %s
                """,
                [stationId],
            )
            totals_by_type["test"] += int(cursor.fetchone()[0] or 0)

            cursor.execute(
                """
                SELECT ucm.material_type, COUNT(*)
                FROM user_course_materials ucm
                JOIN course_programs cp ON cp.id = ucm.course_program_id
                WHERE ucm.is_completed = true AND cp.station_id = %s
                GROUP BY ucm.material_type
                """,
                [stationId],
            )
            for material_type, count in cursor.fetchall():
                completed_by_type[material_type] = int(count or 0)

        material_stats = {}
        for key in totals_by_type.keys():
            total = totals_by_type[key]
            completed = completed_by_type.get(key, 0)
            completion_rate = round((completed / total) * 100, 2) if total else 0
            material_stats[key] = {"total": total, "completed": completed, "completion_rate": completion_rate}

        test_stats = {"average_score": 0, "total_attempts": 0, "pass_rate": 0}
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT AVG(r.score) AS avg_score,
                       COUNT(*) AS total_attempts,
                       SUM(CASE WHEN r.is_passed THEN 1 ELSE 0 END) AS passed_count
                FROM test_results r
                LEFT JOIN course_program_lesson_tests lt ON lt.id = r.test_id AND r.test_type = 'lesson'
                LEFT JOIN course_program_lessons l ON l.id = lt.course_program_lesson_id
                LEFT JOIN final_tests ft ON ft.id = r.test_id AND r.test_type = 'final'
                LEFT JOIN course_programs cp ON cp.id = COALESCE(l.course_program_id, ft.course_program_id)
                WHERE cp.station_id = %s
                """,
                [stationId],
            )
            row = cursor.fetchone()
            if row:
                avg_score, total_attempts, passed_count = row
                total_attempts = int(total_attempts or 0)
                passed_count = int(passed_count or 0)
                test_stats = {
                    "average_score": round(float(avg_score or 0), 2),
                    "total_attempts": total_attempts,
                    "pass_rate": round((passed_count / total_attempts) * 100, 2) if total_attempts else 0,
                }

        courses_data = []
        for program in programs:
            course_program_id = program["id"]
            enroll = UserCourseProgram.objects.filter(course_program_id=course_program_id)
            status_counts_course = {
                "not_started": enroll.filter(status="not_started").count(),
                "in_progress": enroll.filter(status="in_progress").count(),
                "completed": enroll.filter(status="completed").count(),
            }
            totals_by_type_course = _get_material_counts_by_type_for_course(course_program_id)
            completed_by_type_course = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
            for row in UserCourseMaterial.objects.filter(
                course_program_id=course_program_id, is_completed=True
            ).values("material_type").annotate(count=models.Count("id")):
                completed_by_type_course[row["material_type"]] = row["count"]

            buckets_course = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
            for progress in enroll.values_list("progress_percent", flat=True):
                p = progress or 0
                if p <= 20:
                    buckets_course["0-20"] += 1
                elif p <= 40:
                    buckets_course["21-40"] += 1
                elif p <= 60:
                    buckets_course["41-60"] += 1
                elif p <= 80:
                    buckets_course["61-80"] += 1
                else:
                    buckets_course["81-100"] += 1

            test_stats_course = _get_course_test_score_stats(course_program_id)

            courses_data.append(
                {
                    "course_program_id": course_program_id,
                    "title": program["title"],
                    "description": program.get("description"),
                    "lessons_count": program.get("lessons_count", 0),
                    "topics_count": program.get("topics_count", 0),
                    "tests_count": program.get("tests_count", 0),
                    "total_enrollments": enroll.count(),
                    "active_enrollments": status_counts_course["in_progress"],
                    "completed_enrollments": status_counts_course["completed"],
                    "average_progress": round(float(enroll.aggregate(avg=models.Avg("progress_percent")).get("avg") or 0), 2),
                    "materials": {
                        "video": {"total": totals_by_type_course["video"], "completed": completed_by_type_course["video"]},
                        "pdf": {"total": totals_by_type_course["pdf"], "completed": completed_by_type_course["pdf"]},
                        "text": {"total": totals_by_type_course["text"], "completed": completed_by_type_course["text"]},
                        "presentation": {"total": totals_by_type_course["presentation"], "completed": completed_by_type_course["presentation"]},
                        "test": {"total": totals_by_type_course["test"], "completed": completed_by_type_course["test"]},
                    },
                    "test_results": test_stats_course,
                    "progress_distribution": [
                        {"range": key, "count": value} for key, value in buckets_course.items()
                    ],
                }
            )

        most_viewed = []
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ucm.material_key, ucm.material_type, cp.title, COUNT(*) AS view_count
                FROM user_course_materials ucm
                JOIN course_programs cp ON cp.id = ucm.course_program_id
                WHERE ucm.is_completed = true AND cp.station_id = %s
                GROUP BY ucm.material_key, ucm.material_type, cp.title
                ORDER BY view_count DESC
                LIMIT 20
                """,
                [stationId],
            )
            for material_key, material_type, title, view_count in cursor.fetchall():
                most_viewed.append(
                    {
                        "material_key": material_key,
                        "material_type": material_type,
                        "course_title": title,
                        "view_count": int(view_count),
                    }
                )

        activity_timeline = _build_station_activity_timeline(30, stationId)

        return JsonResponse(
            {
                "data": {
                    "station": station,
                    "overview": {
                        "total_courses": len(programs),
                        "total_enrollments": total_enrollments,
                        "active_enrollments": status_counts["in_progress"],
                        "completed_enrollments": status_counts["completed"],
                        "unique_users": unique_users,
                        "average_progress": round(float(avg_progress or 0), 2),
                        "average_test_score": test_stats["average_score"],
                        "total_hours_studied": float(total_hours or 0),
                    },
                    "enrollments": {
                        "by_status": status_counts,
                        "progress_distribution": [
                            {"range": key, "count": value} for key, value in buckets.items()
                        ],
                    },
                    "materials": {
                        "by_type": material_stats,
                        "most_viewed": most_viewed,
                    },
                    "test_results": test_stats,
                    "courses": courses_data,
                    "activity_timeline": activity_timeline,
                }
            }
        )


class AdminAnalyticsStationParticipantsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, stationId: int):
        program_ids = list(
            CourseProgram.objects.filter(station_id=stationId).values_list("id", flat=True)
        )
        if not program_ids:
            return JsonResponse({"data": [], "total": 0})

        enrollment_stats = {
            str(row["user_id"]): row
            for row in UserCourseProgram.objects.filter(course_program_id__in=program_ids)
            .values("user_id")
            .annotate(
                total=models.Count("id"),
                active=models.Count("id", filter=models.Q(status="in_progress")),
                completed=models.Count("id", filter=models.Q(status="completed")),
                avg_progress=models.Avg("progress_percent"),
                last_activity=models.Max("last_activity"),
            )
        }

        user_ids = [row["user_id"] for row in enrollment_stats.values()]
        users = {
            str(u["id"]): u
            for u in User.objects.filter(id__in=user_ids).values("id", "username", "full_name", "email")
        }
        profiles = {}
        for profile in UserProfile.objects.filter(id__in=user_ids).values(
            "id", "avatar_url", "position", "company"
        ):
            profile["avatar_url"] = _resolve_avatar_url(profile.get("avatar_url"))
            profiles[str(profile["id"])] = profile

        materials_map = {}
        for row in UserCourseMaterial.objects.filter(
            course_program_id__in=program_ids, is_completed=True
        ).values("user_id", "material_type").annotate(count=models.Count("id")):
            key = str(row["user_id"])
            if key not in materials_map:
                materials_map[key] = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
            materials_map[key][row["material_type"]] = row["count"]

        test_scores = {}
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT r.user_id, AVG(r.score) AS avg_score
                FROM test_results r
                LEFT JOIN course_program_lesson_tests lt ON lt.id = r.test_id AND r.test_type = 'lesson'
                LEFT JOIN course_program_lessons l ON l.id = lt.course_program_lesson_id
                LEFT JOIN final_tests ft ON ft.id = r.test_id AND r.test_type = 'final'
                LEFT JOIN course_programs cp ON cp.id = COALESCE(l.course_program_id, ft.course_program_id)
                WHERE cp.station_id = %s
                GROUP BY r.user_id
                """,
                [stationId],
            )
            for user_id, avg_score in cursor.fetchall():
                test_scores[str(user_id)] = round(float(avg_score or 0), 2)

        data = []
        for user_id, stats in enrollment_stats.items():
            user = users.get(user_id, {})
            profile = profiles.get(user_id, {})
            data.append(
                {
                    "user_id": user_id,
                    "username": user.get("username"),
                    "full_name": user.get("full_name"),
                    "email": user.get("email"),
                    "avatar_url": profile.get("avatar_url"),
                    "position": profile.get("position"),
                    "company": profile.get("company"),
                    "total_enrollments": stats.get("total", 0),
                    "active_courses": stats.get("active", 0),
                    "completed_courses": stats.get("completed", 0),
                    "average_progress": round(float(stats.get("avg_progress") or 0), 2),
                    "average_test_score": test_scores.get(user_id, 0),
                    "last_activity": stats.get("last_activity").isoformat() if stats.get("last_activity") else None,
                    "materials_completed": materials_map.get(
                        user_id, {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
                    ),
                }
            )

        return JsonResponse({"data": data, "total": len(data)})


class AdminAnalyticsCoursesView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        station_map = {s.id: s.name for s in Station.objects.all().values("id", "name")}
        programs = CourseProgram.objects.all().values(
            "id", "title", "station_id", "lessons_count", "topics_count", "tests_count"
        )

        data = []
        for program in programs:
            course_program_id = program["id"]
            enrollments = UserCourseProgram.objects.filter(course_program_id=course_program_id)
            counts = enrollments.aggregate(
                total=models.Count("id"),
                active=models.Count("id", filter=models.Q(status="in_progress")),
                completed=models.Count("id", filter=models.Q(status="completed")),
                avg_progress=models.Avg("progress_percent"),
            )
            test_stats = _get_course_test_score_stats(course_program_id)
            totals = _get_course_program_material_totals(course_program_id)
            completed_materials = UserCourseMaterial.objects.filter(
                course_program_id=course_program_id, is_completed=True
            ).count()

            data.append(
                {
                    "course_program_id": course_program_id,
                    "title": program["title"],
                    "station_id": program["station_id"],
                    "station_name": station_map.get(program["station_id"], ""),
                    "total_enrollments": counts["total"] or 0,
                    "active_enrollments": counts["active"] or 0,
                    "completed_enrollments": counts["completed"] or 0,
                    "average_progress": round(float(counts["avg_progress"] or 0), 2),
                    "average_test_score": test_stats["average_score"],
                    "total_materials": totals["total_units"],
                    "completed_materials": completed_materials,
                    "lessons_count": program["lessons_count"] or 0,
                    "topics_count": program["topics_count"] or 0,
                    "tests_count": program["tests_count"] or 0,
                }
            )

        return JsonResponse({"data": data})


class AdminAnalyticsCourseDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, courseProgramId: int):
        program = CourseProgram.objects.filter(id=courseProgramId).values().first()
        if not program:
            return JsonResponse({"error": "Course program not found"}, status=404)

        station = Station.objects.filter(id=program["station_id"]).values("name").first() or {}
        enrollments = UserCourseProgram.objects.filter(course_program_id=courseProgramId)
        total_enrollments = enrollments.count()
        status_counts = {
            "not_started": enrollments.filter(status="not_started").count(),
            "in_progress": enrollments.filter(status="in_progress").count(),
            "completed": enrollments.filter(status="completed").count(),
        }

        buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        for progress in enrollments.values_list("progress_percent", flat=True):
            p = progress or 0
            if p <= 20:
                buckets["0-20"] += 1
            elif p <= 40:
                buckets["21-40"] += 1
            elif p <= 60:
                buckets["41-60"] += 1
            elif p <= 80:
                buckets["61-80"] += 1
            else:
                buckets["81-100"] += 1

        totals_by_type = _get_material_counts_by_type_for_course(courseProgramId)
        completed_by_type = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
        for row in UserCourseMaterial.objects.filter(
            course_program_id=courseProgramId, is_completed=True
        ).values("material_type").annotate(count=models.Count("id")):
            completed_by_type[row["material_type"]] = row["count"]

        lesson_tests = CourseProgramLessonTest.objects.filter(
            lesson__course_program_id=courseProgramId
        ).values("id", "lesson_id", "lesson__title")
        test_by_lesson = []
        for test in lesson_tests:
            results = TestResult.objects.filter(test_id=test["id"], test_type="lesson")
            total_attempts = results.count()
            avg_score = results.aggregate(avg=models.Avg("score")).get("avg") or 0
            passed = results.filter(is_passed=True).count()
            pass_rate = round((passed / total_attempts) * 100, 2) if total_attempts else 0
            test_by_lesson.append(
                {
                    "lesson_id": test["lesson_id"],
                    "lesson_title": test["lesson__title"] or "",
                    "total_attempts": total_attempts,
                    "average_score": round(float(avg_score), 2),
                    "pass_rate": pass_rate,
                }
            )

        test_stats = _get_course_test_score_stats(courseProgramId)
        activity_timeline = _build_activity_timeline(30, course_program_id=courseProgramId)

        return JsonResponse(
            {
                "data": {
                    "course_program": {
                        "id": program["id"],
                        "title": program["title"],
                        "station_id": program["station_id"],
                        "station_name": station.get("name", ""),
                        "description": program.get("description"),
                        "duration": program.get("duration"),
                        "lessons_count": program.get("lessons_count", 0),
                        "topics_count": program.get("topics_count", 0),
                        "tests_count": program.get("tests_count", 0),
                    },
                    "enrollments": {
                        "total": total_enrollments,
                        "by_status": status_counts,
                        "progress_distribution": [
                            {"range": key, "count": value} for key, value in buckets.items()
                        ],
                    },
                    "materials": {
                        "by_type": {
                            "video": {"total": totals_by_type["video"], "completed": completed_by_type["video"]},
                            "pdf": {"total": totals_by_type["pdf"], "completed": completed_by_type["pdf"]},
                            "text": {"total": totals_by_type["text"], "completed": completed_by_type["text"]},
                            "presentation": {"total": totals_by_type["presentation"], "completed": completed_by_type["presentation"]},
                            "test": {"total": totals_by_type["test"], "completed": completed_by_type["test"]},
                        }
                    },
                    "test_results": {
                        "total_attempts": test_stats["total_attempts"],
                        "average_score": test_stats["average_score"],
                        "pass_rate": test_stats["pass_rate"],
                        "by_lesson": test_by_lesson,
                    },
                    "activity_timeline": activity_timeline,
                }
            }
        )


class AdminAnalyticsCourseParticipantsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, courseProgramId: int):
        enrollments = list(
            UserCourseProgram.objects.filter(course_program_id=courseProgramId).values(
                "user_id",
                "progress_percent",
                "status",
                "started_at",
                "completed_at",
                "hours_studied",
                "last_activity",
            )
        )
        user_ids = [e["user_id"] for e in enrollments]

        users = {
            str(u["id"]): u
            for u in User.objects.filter(id__in=user_ids).values("id", "username", "full_name", "email")
        }
        profiles = {}
        for profile in UserProfile.objects.filter(id__in=user_ids).values(
            "id", "avatar_url", "position", "company"
        ):
            profile["avatar_url"] = _resolve_avatar_url(profile.get("avatar_url"))
            profiles[str(profile["id"])] = profile

        materials_map = {}
        for row in UserCourseMaterial.objects.filter(
            course_program_id=courseProgramId, is_completed=True
        ).values("user_id", "material_type").annotate(count=models.Count("id")):
            key = str(row["user_id"])
            if key not in materials_map:
                materials_map[key] = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
            materials_map[key][row["material_type"]] = row["count"]

        test_stats_map = {}
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT r.user_id, COUNT(*) AS attempts, AVG(r.score) AS avg_score, MAX(r.score) AS best_score
                FROM test_results r
                LEFT JOIN course_program_lesson_tests lt ON lt.id = r.test_id AND r.test_type = 'lesson'
                LEFT JOIN course_program_lessons l ON l.id = lt.course_program_lesson_id
                LEFT JOIN final_tests ft ON ft.id = r.test_id AND r.test_type = 'final'
                WHERE (l.course_program_id = %s OR ft.course_program_id = %s)
                GROUP BY r.user_id
                """,
                [courseProgramId, courseProgramId],
            )
            for user_id, attempts, avg_score, best_score in cursor.fetchall():
                test_stats_map[str(user_id)] = {
                    "total_attempts": int(attempts or 0),
                    "average_score": round(float(avg_score or 0), 2),
                    "best_score": int(best_score or 0),
                }

        data = []
        for enrollment in enrollments:
            user_id = str(enrollment["user_id"])
            user = users.get(user_id, {})
            profile = profiles.get(user_id, {})
            data.append(
                {
                    "user_id": user_id,
                    "username": user.get("username"),
                    "full_name": user.get("full_name"),
                    "email": user.get("email"),
                    "avatar_url": profile.get("avatar_url"),
                    "position": profile.get("position"),
                    "company": profile.get("company"),
                    "progress_percent": enrollment["progress_percent"] or 0,
                    "status": enrollment["status"],
                    "started_at": enrollment["started_at"].isoformat() if enrollment["started_at"] else None,
                    "completed_at": enrollment["completed_at"].isoformat() if enrollment["completed_at"] else None,
                    "hours_studied": float(enrollment["hours_studied"] or 0),
                    "last_activity": enrollment["last_activity"].isoformat() if enrollment["last_activity"] else None,
                    "materials_completed": materials_map.get(user_id, {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}),
                    "test_results": test_stats_map.get(user_id, {"total_attempts": 0, "average_score": 0, "best_score": 0}),
                }
            )

        return JsonResponse({"data": data, "total": len(data)})


class AdminAnalyticsUsersView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        users = list(User.objects.all().values("id", "username", "full_name", "email", "role", "is_active", "created_at"))
        user_ids = [u["id"] for u in users]

        profiles = {}
        for profile in UserProfile.objects.filter(id__in=user_ids).values(
            "id", "avatar_url", "position", "company"
        ):
            profile["avatar_url"] = _resolve_avatar_url(profile.get("avatar_url"))
            profiles[str(profile["id"])] = profile

        enrollment_stats = {
            str(row["user_id"]): row
            for row in UserCourseProgram.objects.values("user_id").annotate(
                total=models.Count("id"),
                active=models.Count("id", filter=models.Q(status="in_progress")),
                completed=models.Count("id", filter=models.Q(status="completed")),
                avg_progress=models.Avg("progress_percent"),
                total_hours=models.Sum("hours_studied"),
                last_activity=models.Max("last_activity"),
            )
        }

        materials_map = {}
        for row in UserCourseMaterial.objects.filter(is_completed=True).values("user_id", "material_type").annotate(count=models.Count("id")):
            key = str(row["user_id"])
            if key not in materials_map:
                materials_map[key] = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
            materials_map[key][row["material_type"]] = row["count"]

        test_scores = {
            str(row["user_id"]): row["avg_score"]
            for row in TestResult.objects.values("user_id").annotate(avg_score=models.Avg("score"))
        }

        data = []
        for user in users:
            user_id = str(user["id"])
            profile = profiles.get(user_id, {})
            enroll = enrollment_stats.get(user_id, {})
            data.append(
                {
                    "user_id": user_id,
                    "username": user.get("username"),
                    "full_name": user.get("full_name"),
                    "email": user.get("email"),
                    "avatar_url": profile.get("avatar_url"),
                    "position": profile.get("position"),
                    "company": profile.get("company"),
                    "role": user.get("role"),
                    "is_active": user.get("is_active"),
                    "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
                    "total_enrollments": enroll.get("total", 0) or 0,
                    "active_courses": enroll.get("active", 0) or 0,
                    "completed_courses": enroll.get("completed", 0) or 0,
                    "total_hours_studied": float(enroll.get("total_hours") or 0),
                    "average_progress": round(float(enroll.get("avg_progress") or 0), 2),
                    "average_test_score": round(float(test_scores.get(user_id) or 0), 2),
                    "materials_completed": materials_map.get(user_id, {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}),
                    "last_activity": enroll.get("last_activity").isoformat() if enroll.get("last_activity") else None,
                }
            )

        return JsonResponse({"data": data, "total": len(data)})


class AdminAnalyticsUserDetailView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request, userId: str):
        user = User.objects.filter(id=userId).values("id", "username", "full_name", "email", "role", "created_at").first()
        if not user:
            return JsonResponse({"error": "User not found"}, status=404)
        profile = UserProfile.objects.filter(id=userId).values(
            "avatar_url", "position", "company"
        ).first() or {}
        profile["avatar_url"] = _resolve_avatar_url(profile.get("avatar_url"))

        enrollments = list(
            UserCourseProgram.objects.filter(user_id=userId).values(
                "course_program_id",
                "progress_percent",
                "status",
                "started_at",
                "completed_at",
                "hours_studied",
                "last_activity",
            )
        )
        program_ids = [e["course_program_id"] for e in enrollments]
        programs = {
            p["id"]: p
            for p in CourseProgram.objects.filter(id__in=program_ids).values("id", "title", "station_id")
        }
        stations = {s["id"]: s["name"] for s in Station.objects.filter(id__in=[p["station_id"] for p in programs.values()]).values("id", "name")}

        enrollments_data = []
        for e in enrollments:
            program = programs.get(e["course_program_id"], {})
            enrollments_data.append(
                {
                    "course_program_id": e["course_program_id"],
                    "course_title": program.get("title"),
                    "station_name": stations.get(program.get("station_id")),
                    "progress_percent": e["progress_percent"] or 0,
                    "status": e["status"],
                    "started_at": e["started_at"].isoformat() if e["started_at"] else None,
                    "completed_at": e["completed_at"].isoformat() if e["completed_at"] else None,
                    "hours_studied": float(e["hours_studied"] or 0),
                    "last_activity": e["last_activity"].isoformat() if e["last_activity"] else None,
                }
            )

        materials_by_type = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
        for row in UserCourseMaterial.objects.filter(
            user_id=userId, is_completed=True
        ).values("material_type").annotate(count=models.Count("id")):
            materials_by_type[row["material_type"]] = row["count"]

        materials_by_course = {}
        for row in UserCourseMaterial.objects.filter(
            user_id=userId, is_completed=True
        ).values("course_program_id", "material_type").annotate(count=models.Count("id")):
            course_id = row["course_program_id"]
            if course_id not in materials_by_course:
                materials_by_course[course_id] = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
            materials_by_course[course_id][row["material_type"]] = row["count"]

        materials_by_course_list = []
        for course_id, counts in materials_by_course.items():
            program = programs.get(course_id, {})
            materials_by_course_list.append(
                {
                    "course_program_id": course_id,
                    "course_title": program.get("title"),
                    "materials": counts,
                }
            )

        lesson_tests = {t["id"]: t["title"] for t in CourseProgramLessonTest.objects.values("id", "title")}
        final_tests = {t["id"]: t["title"] for t in FinalTest.objects.values("id", "title")}

        test_results = []
        for result in TestResult.objects.filter(user_id=userId).order_by("-completed_at").values(
            "test_id", "test_type", "score", "is_passed", "completed_at"
        )[:200]:
            title = final_tests.get(result["test_id"]) if result["test_type"] == "final" else lesson_tests.get(result["test_id"])
            test_results.append(
                {
                    "test_id": result["test_id"],
                    "test_type": result["test_type"],
                    "test_title": title or "Тест",
                    "course_title": None,
                    "score": result["score"],
                    "is_passed": result["is_passed"],
                    "completed_at": result["completed_at"].isoformat() if result["completed_at"] else None,
                }
            )

        activity_timeline = _build_activity_timeline(30, user_id=userId)

        return JsonResponse(
            {
                "data": {
                    "user": {
                        "id": user["id"],
                        "username": user.get("username"),
                        "full_name": user.get("full_name"),
                        "email": user.get("email"),
                        "avatar_url": profile.get("avatar_url"),
                        "position": profile.get("position"),
                        "company": profile.get("company"),
                        "role": user.get("role"),
                        "created_at": user.get("created_at").isoformat() if user.get("created_at") else None,
                    },
                    "enrollments": enrollments_data,
                    "materials": {
                        "by_type": materials_by_type,
                        "by_course": materials_by_course_list,
                    },
                    "test_results": test_results,
                    "activity_timeline": activity_timeline,
                }
            }
        )


class AdminAnalyticsMaterialsView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        totals = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT f.file_type, COUNT(*)
                FROM course_program_topic_files f
                WHERE f.is_active = true
                GROUP BY f.file_type
                """
            )
            for file_type, count in cursor.fetchall():
                if file_type == "video":
                    totals["video"] += count
                elif file_type == "pdf":
                    totals["pdf"] += count
                else:
                    totals["presentation"] += count

        totals["text"] = CourseProgramTopic.objects.filter(is_active=True).count()
        totals["test"] = CourseProgramLessonTest.objects.filter(is_active=True).count() + FinalTest.objects.filter(is_active=True).count()

        completed = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
        for row in UserCourseMaterial.objects.filter(is_completed=True).values("material_type").annotate(count=models.Count("id")):
            completed[row["material_type"]] = row["count"]

        by_course = []
        for program in CourseProgram.objects.all().values("id", "title"):
            totals_by_type = _get_material_counts_by_type_for_course(program["id"])
            completed_by_type = {"video": 0, "pdf": 0, "text": 0, "presentation": 0, "test": 0}
            for row in UserCourseMaterial.objects.filter(
                course_program_id=program["id"], is_completed=True
            ).values("material_type").annotate(count=models.Count("id")):
                completed_by_type[row["material_type"]] = row["count"]
            by_course.append(
                {
                    "course_program_id": program["id"],
                    "course_title": program["title"],
                    "materials": {
                        "video": {"total": totals_by_type["video"], "viewed": completed_by_type["video"]},
                        "pdf": {"total": totals_by_type["pdf"], "viewed": completed_by_type["pdf"]},
                        "text": {"total": totals_by_type["text"], "viewed": completed_by_type["text"]},
                        "presentation": {"total": totals_by_type["presentation"], "viewed": completed_by_type["presentation"]},
                        "test": {"total": totals_by_type["test"], "completed": completed_by_type["test"]},
                    },
                }
            )

        most_viewed = []
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ucm.material_key, ucm.material_type, cp.title, COUNT(*) AS view_count
                FROM user_course_materials ucm
                JOIN course_programs cp ON cp.id = ucm.course_program_id
                WHERE ucm.is_completed = true
                GROUP BY ucm.material_key, ucm.material_type, cp.title
                ORDER BY view_count DESC
                LIMIT 20
                """
            )
            for material_key, material_type, title, view_count in cursor.fetchall():
                most_viewed.append(
                    {
                        "material_key": material_key,
                        "material_type": material_type,
                        "course_title": title,
                        "view_count": int(view_count),
                    }
                )

        by_type = {}
        for key in totals.keys():
            total = totals[key]
            viewed = completed.get(key, 0)
            completion_rate = round((viewed / total) * 100, 2) if total else 0
            by_type[key] = {
                "total": total,
                "viewed" if key != "test" else "completed": viewed,
                "completion_rate": completion_rate,
            }

        return JsonResponse(
            {
                "data": {
                    "by_type": by_type,
                    "by_course": by_course,
                    "most_viewed": most_viewed,
                }
            }
        )


class MyEnrollmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        rows = list(
            UserCourse.objects.filter(user_id=user_id)
            .values("course_id", "progress_percent")
        )
        course_ids = [r["course_id"] for r in rows]
        course_map = {str(c["id"]): c for c in Course.objects.filter(id__in=course_ids).values("id", "title", "description", "station_id")}
        data = []
        for r in rows:
            c = course_map.get(str(r["course_id"]))
            if not c:
                continue
            data.append(
                {
                    "course_id": str(r["course_id"]),
                    "progress_percent": r["progress_percent"],
                    "title": c["title"],
                    "description": c["description"],
                    "station_id": c["station_id"],
                }
            )
        return JsonResponse({"data": data})


class CourseCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get comments for a specific lesson/topic/file"""
        station_id = request.GET.get("station_id")
        lesson_index = request.GET.get("lesson_index")
        topic_index = request.GET.get("topic_index")
        file_object_key = request.GET.get("file_object_key")

        if not station_id:
            return JsonResponse({"error": "station_id is required"}, status=400)

        query = CourseComment.objects.filter(station_id=station_id)

        if lesson_index is not None:
            query = query.filter(lesson_index=lesson_index)
        if topic_index is not None:
            query = query.filter(topic_index=topic_index)
        if file_object_key:
            query = query.filter(file_object_key=file_object_key)

        comments = list(
            query.values(
                "id",
                "user_id",
                "comment_text",
                "created_at",
                "updated_at",
                "file_object_key",
            )
            .order_by("-created_at")
        )
        
        # Get user info separately
        user_ids = list(set(str(c["user_id"]) for c in comments))
        from apps.accounts.models import User
        users_list = User.objects.filter(id__in=user_ids).values("id", "username", "full_name", "role")
        users = {str(u["id"]): u for u in users_list}

        # Format comments
        formatted_comments = []
        for comment in comments:
            user = users.get(str(comment["user_id"]), {})
            formatted_comments.append({
                "id": comment["id"],
                "userId": str(comment["user_id"]),
                "userName": user.get("full_name") or user.get("username", "Пользователь"),
                "userRole": user.get("role", "user"),
                "text": comment["comment_text"],
                "createdAt": comment["created_at"].isoformat() if comment["created_at"] else None,
                "fileObjectKey": comment["file_object_key"],
            })

        return JsonResponse({"data": formatted_comments})

    def post(self, request):
        """Create a new comment"""
        user_id = request.user.id
        station_id = request.data.get("station_id")
        lesson_index = request.data.get("lesson_index")
        topic_index = request.data.get("topic_index")
        file_object_key = request.data.get("file_object_key")
        comment_text = request.data.get("comment_text")

        if not station_id or not comment_text:
            return JsonResponse(
                {"error": "station_id and comment_text are required"}, status=400
            )

        comment = CourseComment.objects.create(
            user_id=user_id,
            station_id=station_id,
            lesson_index=lesson_index,
            topic_index=topic_index,
            file_object_key=file_object_key,
            comment_text=comment_text,
        )

        # Return created comment with user info
        from apps.accounts.models import User
        user = User.objects.filter(id=user_id).values("id", "username", "full_name", "role").first() or {}
        comment_data = CourseComment.objects.filter(id=comment.id).values(
            "id",
            "user_id",
            "comment_text",
            "created_at",
            "file_object_key",
        ).first()

        return JsonResponse({
            "data": {
                "id": comment_data["id"],
                "userId": str(comment_data["user_id"]),
                "userName": user.get("full_name") or user.get("username", "Пользователь"),
                "userRole": user.get("role", "user"),
                "text": comment_data["comment_text"],
                "createdAt": comment_data["created_at"].isoformat() if comment_data["created_at"] else None,
                "fileObjectKey": comment_data["file_object_key"],
            }
        }, status=201)


# ==================== Test Management Views ====================

class TestsListView(APIView):
    """List all tests (lesson and final) - Admin only"""
    permission_classes = [IsAdmin]

    def get(self, request):
        test_type = request.GET.get('type')  # 'lesson' or 'final' or None for all
        
        data = []
        
        try:
            if not test_type or test_type == 'lesson':
                # Get lesson tests with all fields
                lesson_tests = CourseProgramLessonTest.objects.all().values(
                    'id', 'title', 'questions_count', 'is_active', 'created_at', 'updated_at'
                )
                # Get additional fields and lesson_id using raw query
                from django.db import connection
                lesson_data_map = {}
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, course_program_lesson_id, 
                               COALESCE(description, '') as description,
                               COALESCE(passing_score, 70) as passing_score,
                               COALESCE(time_limit, 30) as time_limit,
                               attempts
                        FROM course_program_lesson_tests
                    """)
                    for row in cursor.fetchall():
                        lesson_data_map[row[0]] = {
                            'course_program_lesson_id': row[1],
                            'description': row[2] or '',
                            'passing_score': row[3] or 70,
                            'time_limit': row[4] or 30,
                            'attempts': row[5]
                        }
                
                for test in lesson_tests:
                    test_dict = dict(test)
                    additional_data = lesson_data_map.get(test['id'], {})
                    test_dict.update(additional_data)
                    test_dict['test_type'] = 'lesson'
                    test_dict['test_id'] = test['id']
                    data.append(test_dict)
            
            if not test_type or test_type == 'final':
                # Get final tests with all fields using raw query for consistency
                from django.db import connection
                final_tests_data = {}
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, course_program_id, title,
                               COALESCE(description, '') as description,
                               COALESCE(questions_count, 0) as questions_count,
                               COALESCE(passing_score, 70) as passing_score,
                               COALESCE(time_limit, 30) as time_limit,
                               attempts, is_active, created_at, updated_at
                        FROM final_tests
                    """)
                    for row in cursor.fetchall():
                        final_tests_data[row[0]] = {
                            'id': row[0],
                            'course_program_id': row[1],
                            'title': row[2],
                            'description': row[3] or '',
                            'questions_count': row[4] or 0,
                            'passing_score': row[5] or 70,
                            'time_limit': row[6] or 30,
                            'attempts': row[7],
                            'is_active': row[8],
                            'created_at': row[9],
                            'updated_at': row[10],
                            'test_type': 'final',
                            'test_id': row[0]
                        }
                
                data.extend(final_tests_data.values())
            
            return JsonResponse({'data': data})
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[TestsListView] Error: {e}", exc_info=True)
            from django.conf import settings
            error_response = {'error': str(e)}
            if settings.DEBUG:
                error_response['traceback'] = traceback.format_exc()
            return JsonResponse(error_response, status=500)


class TestDetailView(APIView):
    """Get test with questions and options - Admin only"""
    permission_classes = [IsAdmin]

    def get(self, request, test_id, test_type):
        # Get test
        if test_type == 'lesson':
            test = CourseProgramLessonTest.objects.filter(id=test_id).values().first()
        elif test_type == 'final':
            test = FinalTest.objects.filter(id=test_id).values().first()
        else:
            return JsonResponse({'error': 'Invalid test_type'}, status=400)
        
        if not test:
            return JsonResponse({'error': 'Test not found'}, status=404)
        
        # Get questions with options
        questions = TestQuestion.objects.filter(
            test_id=test_id, test_type=test_type
        ).order_by('order_index', 'id').values()
        
        questions_list = []
        for q in questions:
            options = TestQuestionOption.objects.filter(
                question_id=q['id']
            ).order_by('order_index', 'id').values('id', 'option_text', 'is_correct', 'order_index')
            
            # Find correct answer index
            correct_answer = None
            options_list = []
            for idx, opt in enumerate(options):
                options_list.append(opt['option_text'])
                if opt['is_correct']:
                    correct_answer = idx
            
            questions_list.append({
                'id': q['id'],
                'question': q['question'],
                'options': options_list,
                'correctAnswer': correct_answer,
                'points': q['points'],
                'image': q['image'],
                'explanation': q['explanation'],
                'order_index': q['order_index']
            })
        
        return JsonResponse({
            'test': {
                **test,
                'test_type': test_type,
                'questions': questions_list
            }
        })


class TestCreateView(APIView):
    """Create test - Admin only"""
    permission_classes = [IsAdmin]

    def post(self, request):
        test_type = request.data.get('test_type')  # 'lesson' or 'final'
        if test_type not in ['lesson', 'final']:
            return JsonResponse({'error': 'test_type must be "lesson" or "final"'}, status=400)
        
        title = request.data.get('title')
        if not title:
            return JsonResponse({'error': 'title is required'}, status=400)
        
        with transaction.atomic():
            if test_type == 'lesson':
                lesson_id = request.data.get('lesson_id')
                if not lesson_id:
                    return JsonResponse({'error': 'lesson_id is required for lesson test'}, status=400)
                
                test = CourseProgramLessonTest.objects.create(
                    lesson_id=lesson_id,
                    title=title,
                    description=request.data.get('description', ''),
                    passing_score=request.data.get('passing_score', 70),
                    time_limit=request.data.get('time_limit', 30),
                    attempts=request.data.get('attempts'),
                    is_active=request.data.get('is_active', True)
                )
            else:  # final
                course_program_id = request.data.get('course_program_id')
                if not course_program_id:
                    return JsonResponse({'error': 'course_program_id is required for final test'}, status=400)
                
                test = FinalTest.objects.create(
                    course_program_id=course_program_id,
                    title=title,
                    description=request.data.get('description', ''),
                    passing_score=request.data.get('passing_score', 70),
                    time_limit=request.data.get('time_limit', 30),
                    attempts=request.data.get('attempts'),
                    is_active=request.data.get('is_active', True)
                )
        
        return JsonResponse({'data': {'id': test.id, 'test_type': test_type}}, status=201)


class TestUpdateView(APIView):
    """Update test - Admin only"""
    permission_classes = [IsAdmin]

    def put(self, request, test_id, test_type):
        if test_type == 'lesson':
            test = CourseProgramLessonTest.objects.filter(id=test_id).first()
        elif test_type == 'final':
            test = FinalTest.objects.filter(id=test_id).first()
        else:
            return JsonResponse({'error': 'Invalid test_type'}, status=400)
        
        if not test:
            return JsonResponse({'error': 'Test not found'}, status=404)
        
        if 'title' in request.data:
            test.title = request.data['title']
        if 'description' in request.data:
            test.description = request.data.get('description', '')
        if 'passing_score' in request.data:
            test.passing_score = request.data['passing_score']
        if 'time_limit' in request.data:
            test.time_limit = request.data['time_limit']
        if 'attempts' in request.data:
            test.attempts = request.data.get('attempts')
        if 'is_active' in request.data:
            test.is_active = request.data['is_active']
        
        test.save()
        
        return JsonResponse({'data': {'id': test.id}})


class TestDeleteView(APIView):
    """Delete test - Admin only"""
    permission_classes = [IsAdmin]

    def delete(self, request, test_id, test_type):
        if test_type == 'lesson':
            test = CourseProgramLessonTest.objects.filter(id=test_id).first()
        elif test_type == 'final':
            test = FinalTest.objects.filter(id=test_id).first()
        else:
            return JsonResponse({'error': 'Invalid test_type'}, status=400)
        
        if not test:
            return JsonResponse({'error': 'Test not found'}, status=404)
        
        test.delete()
        return JsonResponse({'success': True})


class TestQuestionsUpdateView(APIView):
    """Update test questions - Admin only"""
    permission_classes = [IsAdmin]

    def put(self, request, test_id, test_type):
        questions = request.data.get('questions', [])
        
        if test_type not in ['lesson', 'final']:
            return JsonResponse({'error': 'Invalid test_type'}, status=400)
        
        with transaction.atomic():
            # Delete existing questions
            TestQuestion.objects.filter(test_id=test_id, test_type=test_type).delete()
            
            # Create new questions
            for q_idx, q_data in enumerate(questions):
                question = TestQuestion.objects.create(
                    test_id=test_id,
                    test_type=test_type,
                    question=q_data.get('question', ''),
                    points=q_data.get('points', 1),
                    image=q_data.get('image', ''),
                    explanation=q_data.get('explanation', ''),
                    order_index=q_idx
                )
                
                # Create options
                options = q_data.get('options', [])
                correct_answer = q_data.get('correctAnswer', 0)
                
                for opt_idx, opt_text in enumerate(options):
                    TestQuestionOption.objects.create(
                        question_id=question.id,
                        option_text=opt_text,
                        is_correct=(opt_idx == correct_answer),
                        order_index=opt_idx
                    )
            
            # Update questions_count
            questions_count = len(questions)
            if test_type == 'lesson':
                CourseProgramLessonTest.objects.filter(id=test_id).update(questions_count=questions_count)
            else:
                FinalTest.objects.filter(id=test_id).update(questions_count=questions_count)
        
        return JsonResponse({'success': True})


class LessonTestView(APIView):
    """Get lesson test by lesson_id - Authenticated users"""
    permission_classes = [IsAuthenticated]

    def get(self, request, lesson_id):
        try:
            # Get lesson test
            lesson_test = CourseProgramLessonTest.objects.filter(
                lesson_id=lesson_id,
                is_active=True
            ).order_by("id").first()
            
            if not lesson_test:
                return JsonResponse({'test': None})
            
            # Get questions with options
            questions = TestQuestion.objects.filter(
                test_id=lesson_test.id,
                test_type='lesson'
            ).order_by('order_index', 'id').values()
            
            questions_list = []
            for q in questions:
                options = TestQuestionOption.objects.filter(
                    question_id=q['id']
                ).order_by('order_index', 'id').values('id', 'option_text', 'is_correct', 'order_index')
                
                # Find correct answer index
                correct_answer = None
                options_list = []
                for idx, opt in enumerate(options):
                    options_list.append(opt['option_text'])
                    if opt['is_correct']:
                        correct_answer = idx
                
                questions_list.append({
                    'id': q['id'],
                    'question': q['question'],
                    'options': options_list,
                    'correctAnswer': correct_answer,
                    'points': q['points'] or 1,
                    'image': q['image'] or '',
                    'explanation': q['explanation'] or '',
                    'order_index': q['order_index']
                })
            
            # Format test data for TestQuiz component
            test_data = {
                'id': lesson_test.id,
                'title': lesson_test.title,
                'description': lesson_test.description or '',
                'questions': questions_list,
                'passingScore': lesson_test.passing_score or 70,
                'timeLimit': lesson_test.time_limit or 30,
                'attempts': lesson_test.attempts
            }
            
            return JsonResponse({'test': test_data})
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[LessonTestView] Error: {e}", exc_info=True)
            from django.conf import settings
            error_response = {'error': str(e)}
            if settings.DEBUG:
                error_response['traceback'] = traceback.format_exc()
            return JsonResponse(error_response, status=500)


class PublicTestView(APIView):
    """Get test by course_program_id - Public access"""
    permission_classes = [AllowAny]

    def get(self, request, course_program_id):
        try:
            # Get final test for course program
            final_test = FinalTest.objects.filter(
                course_program_id=course_program_id, 
                is_active=True
            ).order_by("id").first()
            
            if not final_test:
                return JsonResponse({'test': None})
            
            # Get questions with options
            questions = TestQuestion.objects.filter(
                test_id=final_test.id, 
                test_type='final'
            ).order_by('order_index', 'id').values()
            
            questions_list = []
            for q in questions:
                options = TestQuestionOption.objects.filter(
                    question_id=q['id']
                ).order_by('order_index', 'id').values('id', 'option_text', 'is_correct', 'order_index')
                
                # Find correct answer index
                correct_answer = None
                options_list = []
                for idx, opt in enumerate(options):
                    options_list.append(opt['option_text'])
                    if opt['is_correct']:
                        correct_answer = idx
                
                questions_list.append({
                    'id': q['id'],
                    'question': q['question'],
                    'options': options_list,
                    'correctAnswer': correct_answer,
                    'points': q['points'] or 1,
                    'image': q['image'] or '',
                    'explanation': q['explanation'] or '',
                    'order_index': q['order_index']
                })
            
            # Format test data for TestQuiz component
            test_data = {
                'id': final_test.id,
                'title': final_test.title,
                'description': final_test.description or '',
                'questions': questions_list,
                'passingScore': final_test.passing_score or 70,
                'timeLimit': final_test.time_limit or 30,
                'attempts': final_test.attempts
            }
            
            return JsonResponse({'test': test_data})
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[PublicTestView] Error: {e}", exc_info=True)
            from django.conf import settings
            error_response = {'error': str(e)}
            if settings.DEBUG:
                error_response['traceback'] = traceback.format_exc()
            return JsonResponse(error_response, status=500)


class TestResultsListView(APIView):
    """List test results - Admin only"""
    permission_classes = [IsAdmin]

    def get(self, request):
        test_id = request.GET.get('test_id')
        test_type = request.GET.get('test_type')
        user_id = request.GET.get('user_id')
        
        query = TestResult.objects.all()
        
        if test_id:
            query = query.filter(test_id=test_id)
        if test_type:
            query = query.filter(test_type=test_type)
        if user_id:
            query = query.filter(user_id=user_id)
        
        results = list(query.order_by('-completed_at').values(
            'id', 'test_id', 'test_type', 'user_id', 'score', 'is_passed',
            'correct_answers', 'total_questions', 'time_spent', 'completed_at'
        ))
        
        # Get user info
        from apps.accounts.models import User
        user_ids = list(set(str(r['user_id']) for r in results))
        users = {str(u['id']): u for u in User.objects.filter(id__in=user_ids).values('id', 'username', 'full_name')}
        
        # Format results
        formatted_results = []
        for r in results:
            user = users.get(str(r['user_id']), {})
            formatted_results.append({
                **r,
                'user_name': user.get('full_name') or user.get('username', 'Unknown')
            })
        
        return JsonResponse({'data': formatted_results})


class TestResultDetailView(APIView):
    """Get test result details - Admin only"""
    permission_classes = [IsAdmin]

    def get(self, request, result_id):
        result = TestResult.objects.filter(id=result_id).values().first()
        if not result:
            return JsonResponse({'error': 'Result not found'}, status=404)
        
        from apps.accounts.models import User
        user = User.objects.filter(id=result['user_id']).values('id', 'username', 'full_name').first() or {}
        
        return JsonResponse({
            'data': {
                **result,
                'user_name': user.get('full_name') or user.get('username', 'Unknown')
            }
        })


class TestResultCreateView(APIView):
    """Create test result - Authenticated users"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        import traceback
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            test_id = request.data.get('test_id')
            test_type = request.data.get('test_type')
            score = request.data.get('score')
            is_passed = request.data.get('is_passed', False)
            correct_answers = request.data.get('correct_answers', 0)
            total_questions = request.data.get('total_questions', 0)
            time_spent = request.data.get('time_spent')  # in seconds
            answers_data = request.data.get('answers_data')  # JSON with user answers
            
            logger.info(f"[TestResultCreateView] Received data: test_id={test_id} (type: {type(test_id)}), test_type={test_type}, score={score}, user_id={request.user.id if request.user else None}")
            
            if not test_id or not test_type:
                return JsonResponse({'error': 'test_id and test_type are required'}, status=400)
            
            # Validate test_id is numeric
            try:
                test_id = int(test_id)
            except (ValueError, TypeError):
                return JsonResponse({'error': f'Field \'id\' expected a number but got \'{test_id}\'. test_id must be a numeric value.'}, status=400)
            
            if test_type not in ['lesson', 'final']:
                return JsonResponse({'error': 'test_type must be "lesson" or "final"'}, status=400)
            
            if score is None:
                return JsonResponse({'error': 'score is required'}, status=400)
            
            # Get user ID from request
            user_id = request.user.id
            if not user_id:
                return JsonResponse({'error': 'User ID is required'}, status=401)
            
            # Check if test exists
            if test_type == 'final':
                test = FinalTest.objects.filter(id=test_id, is_active=True).first()
            else:
                test = CourseProgramLessonTest.objects.filter(id=test_id, is_active=True).first()
            
            if not test:
                return JsonResponse({'error': 'Test not found or inactive'}, status=404)
            
            # Check attempts limit
            if test.attempts is not None:
                user_attempts = TestResult.objects.filter(
                    test_id=test_id,
                    test_type=test_type,
                    user_id=user_id
                ).count()
                
                if user_attempts >= test.attempts:
                    return JsonResponse({
                        'error': f'Превышен лимит попыток ({test.attempts}). Вы уже использовали все доступные попытки.'
                    }, status=400)
            
            # Validate and prepare data
            # Ensure score is integer
            score = int(score)
            if score < 0 or score > 100:
                return JsonResponse({'error': 'Score must be between 0 and 100'}, status=400)
            
            # Ensure correct_answers and total_questions are integers
            correct_answers = int(correct_answers) if correct_answers is not None else 0
            total_questions = int(total_questions) if total_questions is not None else 0
            
            # Ensure time_spent is integer or None
            if time_spent is not None:
                time_spent = int(time_spent)
            
            # Ensure is_passed is boolean
            is_passed = bool(is_passed)
            
            # Validate and parse answers_data - should be dict or None
            if answers_data is not None:
                if isinstance(answers_data, str):
                    try:
                        answers_data = json.loads(answers_data)
                    except json.JSONDecodeError:
                        logger.warning(f"[TestResultCreateView] Failed to parse answers_data as JSON: {answers_data}")
                        answers_data = None
                elif not isinstance(answers_data, dict):
                    logger.warning(f"[TestResultCreateView] answers_data is not dict: {type(answers_data)}")
                    answers_data = None
            
            logger.info(f"[TestResultCreateView] Creating result: test_id={test_id}, test_type={test_type}, user_id={user_id}, score={score}")
            
            # Create test result
            result = TestResult.objects.create(
                test_id=test_id,
                test_type=test_type,
                user_id=user_id,
                score=score,
                is_passed=is_passed,
                correct_answers=correct_answers,
                total_questions=total_questions,
                time_spent=time_spent,
                answers_data=answers_data
            )

            course_program_id = None
            if test_type == "final":
                course_program_id = test.course_program_id
            else:
                lesson = CourseProgramLesson.objects.filter(id=test.lesson_id).values("course_program_id").first()
                if lesson:
                    course_program_id = lesson["course_program_id"]

            if course_program_id:
                UserCourseProgram.objects.get_or_create(
                    user_id=user_id,
                    course_program_id=course_program_id,
                    defaults={
                        "progress_percent": 0,
                        "status": "in_progress",
                        "started_at": timezone.now(),
                    },
                )
                UserCourseMaterial.objects.update_or_create(
                    user_id=user_id,
                    course_program_id=course_program_id,
                    material_type="test",
                    material_key=f"{test_type}:{test_id}",
                    defaults={
                        "is_completed": True,
                        "viewed_at": timezone.now(),
                    },
                )
            
            logger.info(f"[TestResultCreateView] Result created successfully: id={result.id}")
            
            return JsonResponse({
                'data': {
                    'id': result.id,
                    'test_id': result.test_id,
                    'test_type': result.test_type,
                    'score': result.score,
                    'is_passed': result.is_passed,
                    'correct_answers': result.correct_answers,
                    'total_questions': result.total_questions,
                    'time_spent': result.time_spent,
                    'completed_at': result.completed_at.isoformat() if result.completed_at else None
                }
            }, status=201)
            
        except Exception as e:
            logger.error(f"[TestResultCreateView] Error: {e}", exc_info=True)
            from django.conf import settings
            error_response = {'error': str(e)}
            if settings.DEBUG:
                error_response['traceback'] = traceback.format_exc()
            return JsonResponse(error_response, status=500)


class UserTestResultsView(APIView):
    """Get user's test results for a specific test - Authenticated users"""
    permission_classes = [IsAuthenticated]

    def get(self, request, test_id, test_type):
        if test_type not in ['lesson', 'final']:
            return JsonResponse({'error': 'Invalid test_type'}, status=400)
        
        user_id = request.user.id
        
        results = TestResult.objects.filter(
            test_id=test_id,
            test_type=test_type,
            user_id=user_id
        ).order_by('-completed_at').values(
            'id', 'score', 'is_passed', 'correct_answers', 
            'total_questions', 'time_spent', 'completed_at'
        )
        
        return JsonResponse({
            'data': list(results),
            'total_attempts': len(results)
        })


