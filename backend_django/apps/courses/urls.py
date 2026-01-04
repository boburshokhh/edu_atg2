from django.urls import path

from apps.courses import views

urlpatterns = [
    path("stations/<int:stationId>", views.CoursesByStationView.as_view()),
    path("me/enrollments", views.MyEnrollmentsView.as_view()),
    path("<uuid:courseId>/programs", views.CourseProgramsView.as_view()),
    path("<uuid:courseId>/enroll", views.EnrollCourseView.as_view()),
    path("<uuid:courseId>", views.CourseDetailView.as_view()),
    path("comments", views.CourseCommentsView.as_view()),
]











