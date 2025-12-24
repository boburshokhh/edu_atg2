from django.urls import path

from apps.stations import views

urlpatterns = [
    # List and CRUD for stations
    path("", views.StationsListView.as_view()),
    path("create/", views.StationCreateView.as_view()),
    path("<int:id>", views.StationDetailView.as_view()),
    # Course program (public + admin edit)
    path("<int:id>/course-program", views.StationCourseProgramView.as_view()),
    path("<int:id>/course-program/update", views.StationCourseProgramUpdateView.as_view()),
    # Course program topic files (materials per topic)
    path(
        "<int:id>/course-program/topics/<int:topic_id>/files",
        views.StationCourseProgramTopicFilesView.as_view(),
    ),
    path(
        "<int:id>/course-program/topics/<int:topic_id>/files/create/",
        views.StationCourseProgramTopicFileCreateView.as_view(),
    ),
    path(
        "<int:id>/course-program/topics/<int:topic_id>/files/<int:file_id>/update/",
        views.StationCourseProgramTopicFileUpdateView.as_view(),
    ),
    path(
        "<int:id>/course-program/topics/<int:topic_id>/files/<int:file_id>/delete/",
        views.StationCourseProgramTopicFileDeleteView.as_view(),
    ),
    # Promo video (public + admin)
    path("<int:id>/promo-video", views.StationPromoVideoView.as_view()),
    path("<int:id>/promo-video/update", views.StationPromoVideoUpdateView.as_view()),
    path("<int:id>/promo-video/delete", views.StationPromoVideoDeleteView.as_view()),
    path("<int:id>/update/", views.StationUpdateView.as_view()),
    path("<int:id>/delete/", views.StationDeleteView.as_view()),
    # Equipment
    path("<int:id>/equipment", views.StationEquipmentView.as_view()),
    path("<int:id>/equipment/create/", views.StationEquipmentCreateView.as_view()),
    path("<int:id>/equipment/<int:equipment_id>/update/", views.StationEquipmentUpdateView.as_view()),
    path("<int:id>/equipment/<int:equipment_id>/delete/", views.StationEquipmentDeleteView.as_view()),
    # Specifications
    path("<int:id>/specs", views.StationSpecsView.as_view()),
    path("<int:id>/specs/create/", views.StationSpecificationCreateView.as_view()),
    path("<int:id>/specs/<int:spec_id>/update/", views.StationSpecificationUpdateView.as_view()),
    path("<int:id>/specs/<int:spec_id>/delete/", views.StationSpecificationDeleteView.as_view()),
    # Safety Systems
    path("<int:id>/safety", views.StationSafetyView.as_view()),
    path("<int:id>/safety/create/", views.StationSafetySystemCreateView.as_view()),
    path("<int:id>/safety/<int:safety_id>/update/", views.StationSafetySystemUpdateView.as_view()),
    path("<int:id>/safety/<int:safety_id>/delete/", views.StationSafetySystemDeleteView.as_view()),
    # Safety System Features
    path("<int:id>/safety/<int:safety_id>/features/create/", views.StationSafetySystemFeatureCreateView.as_view()),
    path(
        "<int:id>/safety/<int:safety_id>/features/<int:feature_id>/update/",
        views.StationSafetySystemFeatureUpdateView.as_view(),
    ),
    path(
        "<int:id>/safety/<int:safety_id>/features/<int:feature_id>/delete/",
        views.StationSafetySystemFeatureDeleteView.as_view(),
    ),
    # Gas Supply Sources
    path("<int:id>/gas-sources", views.StationGasSupplySourceView.as_view()),
    path("<int:id>/gas-sources/create/", views.StationGasSupplySourceCreateView.as_view()),
    path("<int:id>/gas-sources/<int:source_id>/update/", views.StationGasSupplySourceUpdateView.as_view()),
    path("<int:id>/gas-sources/<int:source_id>/delete/", views.StationGasSupplySourceDeleteView.as_view()),
    # Photos
    path("<int:id>/photos/create/", views.StationPhotoCreateView.as_view()),
    path("<int:id>/photos/<int:photo_id>/update/", views.StationPhotoUpdateView.as_view()),
    path("<int:id>/photos/<int:photo_id>/delete/", views.StationPhotoDeleteView.as_view()),
    # Normative Docs
    path("<int:id>/docs/create/", views.StationNormativeDocCreateView.as_view()),
    path("<int:id>/docs/<int:doc_id>/delete/", views.StationNormativeDocDeleteView.as_view()),
]
