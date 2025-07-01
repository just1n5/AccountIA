"""
Endpoint simple para listar documentos de una declaración.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
import logging

from apps.declarations.models import Declaration
from apps.documents.models import Document

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_declaration_documents(request, declaration_id):
    """
    Lista los documentos de una declaración específica
    """
    # Solo en modo testing por ahora
    if not getattr(settings, 'DEV_SKIP_AUTH_FOR_TESTING', False):
        return Response(
            {'error': 'Solo disponible en modo testing'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        logger.info(f"=== GET DOCUMENTS START ===")
        logger.info(f"Declaration ID: {declaration_id}")
        
        # Manejar caso especial para demo
        if declaration_id == 'demo-declaration-1':
            # Buscar cualquier declaración disponible
            declaration = Declaration.objects.first()
            if not declaration:
                logger.info("No hay declaraciones, devolviendo lista vacía")
                return Response({
                    'results': [],
                    'count': 0
                })
            logger.info(f"Usando declaración: {declaration.id}")
        else:
            # Buscar declaración específica
            declaration = get_object_or_404(Declaration, id=declaration_id)
            logger.info(f"Declaración encontrada: {declaration}")
        
        # Obtener documentos de la declaración
        documents = Document.objects.filter(declaration=declaration)
        logger.info(f"Documentos encontrados: {documents.count()}")
        
        # Serializar documentos
        documents_data = []
        for doc in documents:
            logger.info(f"Documento: {doc.id} - {doc.file_name} - {doc.upload_status}")
            documents_data.append({
                'id': str(doc.id),
                'declaration_id': str(doc.declaration.id),
                'file_name': doc.file_name,
                'original_file_name': doc.original_file_name,
                'file_size': doc.file_size,
                'file_type': doc.file_type,
                'mime_type': doc.mime_type,
                'description': doc.description,
                'upload_status': doc.upload_status,
                'processing_errors': doc.processing_errors,
                'processed_data': doc.processed_data,
                'storage_path': doc.storage_path,
                'uploaded_by': str(doc.uploaded_by.id) if doc.uploaded_by else None,
                'created_at': doc.created_at.isoformat(),
                'updated_at': doc.updated_at.isoformat()
            })
        
        response_data = {
            'results': documents_data,
            'count': len(documents_data)
        }
        
        logger.info(f"=== GET DOCUMENTS SUCCESS ===")
        logger.info(f"Returning {len(documents_data)} documents")
        
        return Response(response_data)
        
    except Exception as e:
        logger.error(f"❌ Error en get_declaration_documents: {str(e)}")
        logger.error(f"Traceback: ", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
