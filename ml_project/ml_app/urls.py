from django.urls import path
from . import views

urlpatterns = [
    path("api/models/", views.ModelListView.as_view(), name="models_list"),
    path("api/models/<int:model_id>/", views.ModelListView.as_view(), name="models_list"),
    path("api/upload-model/", views.UploadModelView.as_view(), name="upload_model"),
    path("api/model/edit/<int:model_id>/", views.EditModelView.as_view(), name="model_edit"),
    path("api/model/predict/", views.ModelPredict.as_view(), name="model_predict"),
    path("health/", views.HealthCheckView.as_view(), name="health_check"),
]
