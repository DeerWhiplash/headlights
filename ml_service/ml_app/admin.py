from django.contrib import admin
from .models import Model

@admin.register(Model)
class ModelAdmin(admin.ModelAdmin):
    list_display = ('model_id', 'model_name', 'notes', 'filepath', 'price_per_prediction')
