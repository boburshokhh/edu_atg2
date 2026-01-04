from __future__ import annotations

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.courses.models import Course, CourseProgram, UserCourse, CourseComment


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


