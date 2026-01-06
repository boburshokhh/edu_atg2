from django.urls import path, re_path

from apps.files import views

urlpatterns = [
    path("presign", views.PresignDownloadView.as_view()),
    path("presign-upload", views.PresignUploadView.as_view()),
    path("upload", views.DirectUploadView.as_view()),
    path("folder-contents", views.FolderContentsView.as_view()),
    path("exists", views.ExistsObjectView.as_view()),
    path("object", views.DeleteObjectView.as_view()),
    re_path(r"^stream/(?P<key>.+)$", views.StreamObjectView.as_view()),
    re_path(r"^video/(?P<key>.+)$", views.VideoStreamView.as_view()),  # Public video streaming
    re_path(r"^hls/(?P<key>.+)$", views.HlsObjectView.as_view()),
    path("transcode-hls", views.TranscodeHlsView.as_view()),
    path("transcode-jobs/<int:job_id>", views.TranscodeJobView.as_view()),
]





