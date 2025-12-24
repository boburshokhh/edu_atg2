from __future__ import annotations

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.courses.models import Course, CourseProgram, UserCourse


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


