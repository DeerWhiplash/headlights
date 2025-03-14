"""
URL configuration for desd project.
"""
from django.urls import path

from myapp.views.IndexView import IndexView
from myapp.views.MLDashboardView import MLDashboardView, ModelListView, UploadModelView


urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("ml/", MLDashboardView.as_view() , name="ml_dashboard"),
    
    # ML-related API endpoints
    path("api/models/", ModelListView.as_view(), name="models_list"),
    path("api/upload-model/", UploadModelView.as_view(), name="upload_model"),
    # Additional endpoints could be added here as needed
]
