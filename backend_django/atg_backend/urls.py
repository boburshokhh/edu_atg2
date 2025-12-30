from django.http import JsonResponse
from django.urls import include, path


def health(_request):
    return JsonResponse({"ok": True})


urlpatterns = [
    path("health", health),
    path("auth/", include("apps.accounts.urls")),
    path("users/", include("apps.accounts.profile_urls")),
    path("site/", include("apps.core.urls")),
    path("stations/", include("apps.stations.urls")),
    path("courses/", include("apps.courses.urls")),
    path("files/", include("apps.files.urls")),
]


