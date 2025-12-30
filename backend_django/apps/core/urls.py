from django.urls import path

from apps.core.views import HeroImageView

urlpatterns = [
    path("hero-image", HeroImageView.as_view()),
]


