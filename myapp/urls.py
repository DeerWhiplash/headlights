"""
URL configuration for desd project.
"""
from django.urls import path
from . import views

urlpatterns = [
    # Base URL for the app shows index
    path("", views.index, name="index"),
    
    # ML dashboard is only accessed when explicitly requested
    path("ml/", views.ml_dashboard, name="ml_dashboard"),
    
    # API endpoints
    path("api/models/", views.models_list, name="models_list"),
    path("api/upload-model/", views.upload_model, name="upload_model"),
]
