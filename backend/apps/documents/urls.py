"""
URLs para la app de documentos
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DeclarationViewSet,
    create_document_upload,
    update_document_status,
    get_document_status,
    health_check
)

# Router para ViewSets
router = DefaultRouter()
router.register(r'declarations', DeclarationViewSet, basename='declaration')

# URLs personalizadas
custom_urlpatterns = [
    # Health check
    path('health/', health_check, name='health_check'),
    
    # Documentos
    path(
        'declarations/<uuid:declaration_id>/documents/',
        create_document_upload,
        name='create_document_upload'
    ),
    path(
        'declarations/<uuid:declaration_id>/documents/<uuid:document_id>/status/',
        update_document_status,
        name='update_document_status'
    ),
    path(
        'declarations/<uuid:declaration_id>/documents/<uuid:document_id>/status/',
        get_document_status,
        name='get_document_status'
    ),
]

# Combinar URLs
urlpatterns = [
    path('', include(router.urls)),
    *custom_urlpatterns,
]