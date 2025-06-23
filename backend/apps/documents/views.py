"""
Vistas API para documentos.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.conf import settings
import uuid
import os

from .models import Document, DocumentTemplate
from .serializers import (
    DocumentSerializer,
    DocumentUploadSerializer,
    DocumentStatusUpdateSerializer,
    DocumentProcessedDataSerializer,
    DocumentTemplateSerializer
)
from .services.storage_service import get_storage_service
from .tasks import process_document
from apps.declarations.models import Declaration
from apps.common.permissions import get_testing_permission_classes

import logging

logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de documentos.
    """
    serializer_class = DocumentSerializer
    permission_classes = [AllowAny]  # TESTING: Sin permisos
    
    def get_queryset(self):
        """
        Filtra documentos por declaración y usuario.
        """
        # TESTING: Simplificar para testing
        print(f"🔍 DEBUG Documents: self.request.user = {self.request.user}")
        
        # Si viene en el contexto de una declaración específica
        declaration_id = self.kwargs.get('declaration_pk')
        
        if declaration_id:
            # TESTING: No verificar usuario
            declaration = get_object_or_404(Declaration, id=declaration_id)
            return Document.objects.filter(
                declaration=declaration,
                is_active=True
            ).order_by('-created_at')
        
        # TESTING: Retornar todos los documentos
        return Document.objects.filter(
            is_active=True
        ).select_related('declaration').order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def initiate_upload(self, request, declaration_pk=None):
        """
        Inicia el proceso de carga de un documento.
        Retorna una URL firmada para que el cliente suba directamente a GCS.
        """
        # Validar que existe la declaración
        declaration = get_object_or_404(
            Declaration,
            id=declaration_pk,
            user=request.user
        )
        
        # Validar que la declaración es editable
        if not declaration.is_editable:
            return Response(
                {'error': 'No se pueden agregar documentos a esta declaración'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar datos de entrada
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        
        with transaction.atomic():
            # Generar nombre único para el archivo
            file_ext = os.path.splitext(validated_data['file_name'])[1]
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            
            # Crear registro de documento
            document = Document.objects.create(
                declaration=declaration,
                file_name=unique_filename,
                original_file_name=validated_data['file_name'],
                file_size=validated_data.get('file_size'),
                file_type=validated_data['file_type'],
                mime_type=validated_data.get('mime_type', 'application/octet-stream'),
                description=validated_data.get('description', ''),
                upload_status='pending',
                uploaded_by=request.user
            )
            
            # Generar URL firmada para subida
            storage_service = get_storage_service()
            storage_key = document.get_storage_key()
            
            try:
                signed_url = storage_service.generate_signed_url(
                    blob_name=storage_key,
                    expiration=3600,  # 1 hora
                    method='PUT',
                    content_type=document.mime_type
                )
                
                document.storage_path = storage_key
                document.upload_status = 'uploading'
                document.save()
                
            except Exception as e:
                logger.error(f"Error al generar URL firmada: {str(e)}")
                document.mark_as_error([f"Error al preparar la carga: {str(e)}"])
                
                return Response(
                    {'error': 'Error al preparar la carga del archivo'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        return Response({
            'document_id': str(document.id),
            'upload_url': signed_url,
            'storage_key': storage_key,
            'expires_in': 3600
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['put'])
    def update_status(self, request, pk=None, declaration_pk=None):
        """
        Actualiza el estado de un documento después de la carga.
        """
        document = self.get_object()
        
        serializer = DocumentStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validated_data
        new_status = validated_data['upload_status']
        
        if new_status == 'uploaded':
            # Marcar como subido y lanzar procesamiento
            document.upload_status = 'uploaded'
            document.save()
            
            # Lanzar tarea de procesamiento según el tipo
            if document.file_type == 'exogena_report':
                process_document.delay(str(document.id))
                
        elif new_status == 'error':
            # Marcar con error
            document.mark_as_error([validated_data.get('error_message', 'Error de carga')])
        
        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['get'])
    def download_url(self, request, pk=None, declaration_pk=None):
        """
        Genera una URL firmada para descargar un documento.
        """
        document = self.get_object()
        
        if document.upload_status not in ['uploaded', 'processed']:
            return Response(
                {'error': 'El documento no está disponible para descarga'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            storage_service = get_storage_service()
            download_url = storage_service.generate_signed_url(
                blob_name=document.storage_path,
                expiration=3600,  # 1 hora
                method='GET'
            )
            
            return Response({
                'download_url': download_url,
                'filename': document.original_file_name,
                'expires_in': 3600
            })
            
        except Exception as e:
            logger.error(f"Error al generar URL de descarga: {str(e)}")
            return Response(
                {'error': 'Error al generar URL de descarga'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def processed_data(self, request, pk=None, declaration_pk=None):
        """
        Obtiene los datos procesados de un documento.
        """
        document = self.get_object()
        
        if not document.is_processed:
            return Response(
                {'error': 'El documento no ha sido procesado'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = DocumentProcessedDataSerializer(document)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None, declaration_pk=None):
        """
        Solicita el reprocesamiento de un documento.
        """
        document = self.get_object()
        
        if document.upload_status != 'error':
            return Response(
                {'error': 'Solo se pueden reprocesar documentos con error'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Limpiar errores anteriores
        document.processing_errors = []
        document.mark_as_processing()
        
        # Lanzar tarea de procesamiento
        process_document.delay(str(document.id))
        
        return Response({
            'message': 'Reprocesamiento iniciado',
            'document_id': str(document.id)
        })
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un documento (soft delete).
        """
        document = self.get_object()
        
        # Verificar que la declaración es editable
        if not document.declaration.is_editable:
            return Response(
                {'error': 'No se pueden eliminar documentos de esta declaración'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Soft delete
        document.is_active = False
        document.save()
        
        return Response(status=status.HTTP_204_NO_CONTENT)


class DocumentTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para plantillas de documentos.
    """
    queryset = DocumentTemplate.objects.filter(is_active=True)
    serializer_class = DocumentTemplateSerializer
    permission_classes = [AllowAny]  # TESTING: Sin permisos
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """
        Genera un documento basado en una plantilla.
        """
        template = self.get_object()
        
        # TODO: Implementar generación de documentos desde plantillas
        # Por ahora retornar un placeholder
        
        return Response({
            'message': 'Funcionalidad de generación de documentos en desarrollo',
            'template': template.name
        }, status=status.HTTP_501_NOT_IMPLEMENTED)
