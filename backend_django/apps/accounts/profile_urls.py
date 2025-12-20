from django.urls import path

from apps.accounts import views

urlpatterns = [
    path("me", views.MyProfileView.as_view()),
    path("me/stats", views.MyStatsView.as_view()),
]










