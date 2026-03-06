from django.urls import path
from . import views

urlpatterns = [
    path("basic-report/", views.basic_report, name="basic_report"),
]