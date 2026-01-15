from django.urls import path

from apps.courses import views

urlpatterns = [
    path("stations/<int:stationId>", views.CoursesByStationView.as_view()),
    path("me/enrollments", views.MyEnrollmentsView.as_view()),
    path("me/programs", views.MyCourseProgramsView.as_view()),
    path("me/stats", views.MyCourseProgramsStatsView.as_view()),
    path("programs/<int:courseProgramId>/enroll", views.EnrollCourseProgramView.as_view()),
    path("programs/<int:courseProgramId>/progress", views.CourseProgramProgressView.as_view()),
    path("programs/<int:courseProgramId>/materials/complete", views.CourseProgramMaterialCompleteView.as_view()),
    path("<uuid:courseId>/programs", views.CourseProgramsView.as_view()),
    path("<uuid:courseId>/enroll", views.EnrollCourseView.as_view()),
    path("<uuid:courseId>", views.CourseDetailView.as_view()),
    path("comments", views.CourseCommentsView.as_view()),
    # Test management endpoints
    # Paths with suffixes (/update, /delete, etc.) must come before simple paths to avoid conflicts
    path("tests/results", views.TestResultsListView.as_view()),
    path("tests/results/<int:result_id>", views.TestResultDetailView.as_view()),
    path("tests/results/create", views.TestResultCreateView.as_view()),
    path("tests/create", views.TestCreateView.as_view()),
    path("tests/<str:test_type>/<int:test_id>/results", views.UserTestResultsView.as_view()),
    path("tests/<str:test_type>/<int:test_id>/questions", views.TestQuestionsUpdateView.as_view()),
    path("tests/<str:test_type>/<int:test_id>/update", views.TestUpdateView.as_view()),
    path("tests/<str:test_type>/<int:test_id>/delete", views.TestDeleteView.as_view()),
    path("tests/<str:test_type>/<int:test_id>", views.TestDetailView.as_view()),
    # Simple paths (without suffixes) come last
    path("tests/lesson/<int:lesson_id>", views.LessonTestView.as_view()),
    path("tests/course-program/<int:course_program_id>", views.PublicTestView.as_view()),
    path("tests", views.TestsListView.as_view()),
]











