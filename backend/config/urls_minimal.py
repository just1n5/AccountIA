"""
AccountIA URL Configuration MÍNIMA
Solo declaraciones, sin documentos por ahora.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'accountia-backend-minimal',
        'version': '1.0.0'
    })

def api_info(request):
    """Info endpoint para verificar API"""
    return JsonResponse({
        'message': 'AccountIA API funcionando (versión mínima)',
        'version': '1.0.0',
        'debug': settings.DEBUG,
        'endpoints': {
            'health': '/health/',
            'admin': '/admin/',
            'declarations': '/api/v1/declarations/',
            'auth': '/api/v1/auth/',
        }
    })


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check
    path('health/', health_check, name='health_check'),
    path('api/info/', api_info, name='api_info'),
    
    # API v1 - SOLO DECLARACIONES
    path('api/v1/auth/', include('apps.authentication.urls')),
    path('api/v1/users/', include('apps.users.urls')),
    path('api/v1/', include('apps.declarations.urls')),  # Declaraciones
    # Temporalmente sin documents
    # path('api/v1/', include('apps.documents.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
