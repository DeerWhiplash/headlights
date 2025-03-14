from django.urls import path
from . import views

urlpatterns = [
    path("", views.MLDashboardView.as_view(), name="ml_dashboard"),
    path("api/models/", views.ModelListView.as_view(), name="models_list"),
    path("api/upload-model/", views.UploadModelView.as_view(), name="upload_model"),
    path("health/", views.HealthCheckView.as_view(), name="health_check"),
]
