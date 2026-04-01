from django.urls import path
from . import views

urlpatterns = [
    path("basic-report/<str:document_id>/", views.basic_report, name="basic_report"),
    path("full-report/<str:document_id>/", views.full_report, name="full_report"),
    path(
        "validate/<str:document_id>/",
        views.extraction_quality_report,
        name="extraction_quality_report",
    ),
    path(
        "debug/<str:document_id>/",
        views.extraction_debug_report,
        name="extraction_debug_report",
    ),
]
