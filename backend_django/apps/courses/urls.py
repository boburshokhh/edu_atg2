from django.urls import path

from apps.courses import views

urlpatterns = [
    path("stations/<int:stationId>", views.CoursesByStationView.as_view()),
    path("me/enrollments", views.MyEnrollmentsView.as_view()),
    path("<uuid:courseId>/programs", views.CourseProgramsView.as_view()),
    path("<uuid:courseId>/enroll", views.EnrollCourseView.as_view()),
    path("<uuid:courseId>", views.CourseDetailView.as_view()),
    path("comments", views.CourseCommentsView.as_view()),
    # Test management endpoints
    path("tests", views.TestsListView.as_view()),
    path("tests/<str:test_type>/<int:test_id>", views.TestDetailView.as_view()),
    path("tests/create", views.TestCreateView.as_view()),
    path("tests/<str:test_type>/<int:test_id>/update", views.TestUpdateView.as_view()),
    path("tests/<str:test_type>/<int:test_id>/delete", views.TestDeleteView.as_view()),
    path("tests/<str:test_type>/<int:test_id>/questions", views.TestQuestionsUpdateView.as_view()),
    path("tests/results", views.TestResultsListView.as_view()),
    path("tests/results/<int:result_id>", views.TestResultDetailView.as_view()),
]











