"""
URL configuration for ml_app
"""
from django.urls import path
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path("", views.ml_dashboard, name="ml_dashboard"),
    # Add index URL pattern to fix the NoReverseMatch error
    path("index/", RedirectView.as_view(url='/'), name="index"),
]
