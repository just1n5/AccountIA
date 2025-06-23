"""
Decoradores y utilidades para desarrollo
"""
import os
from functools import wraps
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import BasePermission


class DevelopmentAuthentication(BaseAuthentication):
    """
    Autenticación que permite bypass en desarrollo
    """
    
    def authenticate(self, request):
        if settings.DEBUG and os.getenv('DEV_SKIP_AUTH_FOR_TESTING') == '1':
            # Crear usuario demo para desarrollo
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                demo_user = User.objects.get(email='demo@accountia.com')
            except User.DoesNotExist:
                demo_user = User.objects.create_user(
                    email='demo@accountia.com',
                    password='demo123',
                    first_name='Demo',
                    last_name='User',
                    is_active=True
                )
            return (demo_user, None)
        return None


class DevelopmentPermission(BasePermission):
    """
    Permiso que permite todo en desarrollo
    """
    
    def has_permission(self, request, view):
        if settings.DEBUG and os.getenv('DEV_SKIP_AUTH_FOR_TESTING') == '1':
            return True
        return False


def development_auth_bypass(view_func):
    """
    Decorador que permite bypass de autenticación en desarrollo
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if settings.DEBUG and os.getenv('DEV_SKIP_AUTH_FOR_TESTING') == '1':
            # Crear usuario demo si no existe
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            try:
                demo_user = User.objects.get(email='demo@accountia.com')
            except User.DoesNotExist:
                demo_user = User.objects.create_user(
                    email='demo@accountia.com',
                    password='demo123',
                    first_name='Demo',
                    last_name='User',
                    is_active=True
                )
            request.user = demo_user
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
