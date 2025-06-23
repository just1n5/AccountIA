"""
Middleware para desarrollo que permite testing sin autenticación completa
Solo para uso en desarrollo local
"""
import os
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.models import AnonymousUser


class DevelopmentAuthMiddleware:
    """
    Middleware que permite bypass de autenticación en desarrollo
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, 'DEBUG', False) and os.getenv('DEV_SKIP_AUTH_FOR_TESTING') == '1'
    
    def __call__(self, request):
        if self.enabled and self.should_bypass_auth(request):
            # Crear o usar usuario demo para testing
            demo_user = self.get_or_create_demo_user()
            request.user = demo_user
            
        response = self.get_response(request)
        return response
    
    def should_bypass_auth(self, request):
        """
        Determina si debe hacer bypass de autenticación
        """
        # Solo para APIs específicas en desarrollo
        api_paths = [
            '/api/v1/declarations/',
            '/api/v1/documents/',
        ]
        
        path = request.path
        return any(path.startswith(api_path) for api_path in api_paths)
    
    def get_or_create_demo_user(self):
        """
        Obtiene o crea usuario demo para testing
        """
        # Import aquí para evitar problemas de importación circular
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
        
        return demo_user


class CORSMiddleware:
    """
    Middleware CORS mejorado para desarrollo
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        if settings.DEBUG:
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization'
            response['Access-Control-Allow-Credentials'] = 'true'
        
        return response
    
    def process_request(self, request):
        if request.method == 'OPTIONS':
            response = JsonResponse({})
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Accept, Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization'
            return response
