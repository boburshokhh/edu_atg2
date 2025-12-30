from django.urls import path

from apps.core.views import HeroImageView, HeroSliderUploadView, HeroSliderView

urlpatterns = [
    path("hero-image", HeroImageView.as_view()),
    path("hero-slider", HeroSliderView.as_view()),
    path("hero-slider/upload", HeroSliderUploadView.as_view()),
]


