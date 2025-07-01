"""
URLs para la aplicación de documentos.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, DocumentTemplateViewSet
from .upload_testing import upload_direct_testing
from .debug.simple_upload import debug_upload
from .declaration_documents import get_declaration_documents

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
    
    # Upload directo para testing
    path('declarations/<str:declaration_id>/upload-testing/', upload_direct_testing, name='upload-testing'),
    
    # Debug upload (temporal)
    path('declarations/<str:declaration_id>/debug-upload/', debug_upload, name='debug-upload'),
    
    # Listar documentos de una declaración (testing)
    path('declarations/<str:declaration_id>/documents/', get_declaration_documents, name='declaration-documents'),
    
    # URLs anidadas bajo declaraciones
    path('declarations/<str:declaration_pk>/', include(declaration_documents_router.urls)),
]
