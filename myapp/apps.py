from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

class MyappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "myapp"

    def ready(self):
        # Import here to avoid circular imports
        # Only run this in the main process (not in management commands)
        import os
        import myapp.signals

        if os.environ.get('RUN_MAIN', None) != 'true':
            logger.info("Application starting up...")
