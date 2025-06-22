"""
Middleware de autenticación Firebase simple para MVP
"""
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class FirebaseAuthMiddleware(MiddlewareMixin):
    """
    Middleware simple que permite acceso a todas las rutas por ahora.
    En el futuro implementaremos validación real de Firebase.
    """
    
    def process_request(self, request):
        # URLs que no requieren autenticación
        public_urls = [
            '/health/',
            '/api/v1/auth/',
            '/admin/',
            '/api/schema/',
            '/api/docs/',
            '/api/redoc/',
        ]
        
        # Verificar si es una URL pública
        path = request.path
        if any(path.startswith(url) for url in public_urls):
            return None
        
        # Para el MVP, permitir acceso si hay un token Bearer
        # (sin validar el token real aún)
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            # Por ahora, cualquier token Bearer es válido
            # TODO: Validar token real con Firebase Admin SDK
            logger.info(f"✅ Request to {path} with Firebase token (MVP mode)")
            
            # CRÍTICO: Configurar request.user como autenticado
            # Para el MVP, crear/obtener un usuario dummy real
            mvp_user, created = User.objects.get_or_create(
                email='mvp-user@accountia.dev',
                defaults={
                    'username': 'mvp-user',
                    'first_name': 'Usuario',
                    'last_name': 'MVP',
                }
            )
            
            if created:
                logger.info("👤 Created MVP user for development")
            
            request.user = mvp_user
            
            return None
        
        # Si no hay token y es una ruta protegida, devolver 403
        if path.startswith('/api/v1/'):
            logger.warning(f"❌ Request to {path} without valid token")
            return JsonResponse(
                {'detail': 'Las credenciales de autenticación no se proveyeron.'},
                status=403
            )
        
        return None
