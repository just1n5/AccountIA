"""
Configuración de la aplicación Fiscal
"""
from django.apps import AppConfig


class FiscalConfig(AppConfig):
    """Configuración de la app fiscal"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.fiscal'
    verbose_name = 'Análisis Fiscal'
    
    def ready(self):
        """Inicialización cuando la app está lista"""
        # Importar señales si las hay
        pass
