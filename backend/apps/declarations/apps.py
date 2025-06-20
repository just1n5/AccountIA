from django.apps import AppConfig


class DeclarationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.declarations'
    verbose_name = 'Declarations'

    def ready(self):
        # Import signal handlers
        pass
