from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class MLAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ml_app"

    def ready(self):
        # Import here to avoid circular imports
        # Only run this in the main process (not in management commands)
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            try:
                from .views import model_check_on_startup
                model_check_on_startup()
            except Exception as e:
                logger.warning(f"Failed to run model check on startup: {e}")
