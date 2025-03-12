"""
API URL configuration for ml_app
"""
from django.urls import path
from . import views

urlpatterns = [
    path("models/", views.models_list, name="models_list"),
    path("upload-model/", views.upload_model, name="upload_model"),
]
