"""
Utilidades de permisos para desarrollo y testing.
"""
from django.conf import settings
from rest_framework.permissions import IsAuthenticated, AllowAny


def get_testing_permission_classes():
    """
    Retorna las clases de permisos apropiadas para testing.
    Si DEV_SKIP_AUTH_FOR_TESTING está activado, usa AllowAny.
    De lo contrario, usa IsAuthenticated.
    """
    if getattr(settings, 'DEV_SKIP_AUTH_FOR_TESTING', False):
        return [AllowAny]
    return [IsAuthenticated]


class TestingAwarePermission:
    """
    Clase base que permite saltarse la autenticación en modo testing.
    """
    @classmethod
    def get_permission_classes(cls):
        return get_testing_permission_classes()


# Para uso fácil en imports
TestingPermissionClasses = get_testing_permission_classes()
