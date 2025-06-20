from django.apps import AppConfig


class Ai_coreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ai_core'
    verbose_name = 'Ai_core'

    def ready(self):
        # Import signal handlers
        pass
