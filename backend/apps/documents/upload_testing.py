"""
Endpoint simple para upload directo en modo testing.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.conf import settings
import os

from apps.declarations.models import Declaration
from apps.documents.models import Document
from apps.documents.services.storage_service import get_storage_service

import logging
logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def upload_direct_testing(request, declaration_id):
    """
    Upload directo para modo testing - sin signed URLs
    """
    # Solo en modo testing
    if not getattr(settings, 'DEV_SKIP_AUTH_FOR_TESTING', False):
        return Response(
            {'error': 'Solo disponible en modo testing'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Obtener declaración
    declaration = get_object_or_404(Declaration, id=declaration_id)
    
    # Validar archivo
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No se envió archivo'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file = request.FILES['file']
    
    # Validar extensión
    name, ext = os.path.splitext(file.name)
    if ext.lower() not in ['.xlsx', '.xls']:
        return Response(
            {'error': 'Solo archivos Excel (.xlsx, .xls)'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Crear documento
        document = Document.objects.create(
            declaration=declaration,
            file_name=file.name,
            original_file_name=file.name,
            file_size=file.size,
            file_type='exogena_report',
            mime_type=file.content_type or 'application/vnd.ms-excel',
            description='Información exógena',
            upload_status='uploaded'
        )
        
        # Guardar archivo
        storage_service = get_storage_service()
        storage_key = f"testing/{declaration_id}/{file.name}"
        
        storage_service.upload_file(
            file_obj=file,
            blob_name=storage_key,
            content_type=file.content_type
        )
        
        document.storage_path = storage_key
        
        # Procesar con datos demo
        from apps.documents.parsers.excel_parser import ExogenaParser
        parser = ExogenaParser()
        demo_data = parser.parse_demo_data()
        
        document.processed_data = demo_data
        document.upload_status = 'processed'
        document.save()
        
        # Actualizar declaración
        meta = demo_data.get('metadata', {})
        declaration.total_income = str(meta.get('total_ingresos', 50000000))
        declaration.total_withholdings = str(meta.get('total_retenciones', 5000000))
        declaration.save()
        
        return Response({
            'success': True,
            'document_id': str(document.id),
            'processed_data': demo_data,
            'message': 'Archivo procesado con datos demo'
        })
        
    except Exception as e:
        logger.error(f"Error en upload testing: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
