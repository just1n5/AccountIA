"""
Configuración del proyecto AccountIA
"""

# Asegurar que Celery se configure cuando Django inicia
from .celery import app as celery_app

__all__ = ('celery_app',)