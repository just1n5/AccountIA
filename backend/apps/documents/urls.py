"""
URLs para la aplicación de documentos.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, DocumentTemplateViewSet

app_name = 'documents'

# Router principal para documentos generales
router = DefaultRouter()
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'templates', DocumentTemplateViewSet, basename='document-template')

# Router para documentos anidados bajo declaraciones
declaration_documents_router = DefaultRouter()
declaration_documents_router.register(
    r'documents',
    DocumentViewSet,
    basename='declaration-documents'
)

urlpatterns = [
    # URLs generales
    path('', include(router.urls)),
    
    # URLs anidadas bajo declaraciones
    path('declarations/<str:declaration_pk>/', include(declaration_documents_router.urls)),
]
