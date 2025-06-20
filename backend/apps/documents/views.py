"""
Vistas de la API para gestión de documentos y declaraciones
"""

import logging
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone

from .models import Declaration, Document, ProcessingLog
from .services.storage_service import get_gcs_service
from .tasks import process_exogena_file, generate_declaration_summary

logger = logging.getLogger(__name__)


class DeclarationViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar declaraciones de renta
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Obtener solo las declaraciones del usuario autenticado"""
        return Declaration.objects.filter(user=self.request.user)
    
    def create(self, request):
        """
        Crear una nueva declaración de renta
        
        POST /api/v1/declarations/
        Body: {"fiscal_year": 2024}
        """
        try:
            fiscal_year = request.data.get('fiscal_year')
            
            if not fiscal_year:
                return Response(
                    {'error': 'fiscal_year es requerido'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verificar que no exista ya una declaración para ese año
            existing = Declaration.objects.filter(
                user=request.user, 
                fiscal_year=fiscal_year
            ).first()
            
            if existing:
                return Response(
                    {
                        'error': f'Ya existe una declaración para el año {fiscal_year}',
                        'existing_declaration_id': str(existing.id)
                    },
                    status=status.HTTP_409_CONFLICT
                )
            
            # Crear nueva declaración
            declaration = Declaration.objects.create(
                user=request.user,
                fiscal_year=fiscal_year
            )
            
            logger.info(f"✅ Declaración creada: {declaration.id} para usuario {request.user.id}")
            
            return Response({
                'id': str(declaration.id),
                'fiscal_year': declaration.fiscal_year,
                'status': declaration.status,
                'created_at': declaration.created_at.isoformat()
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"❌ Error creando declaración: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, pk=None):
        """
        Obtener detalles de una declaración
        
        GET /api/v1/declarations/{id}/
        """
        try:
            declaration = get_object_or_404(self.get_queryset(), pk=pk)
            
            # Incluir documentos asociados
            documents = []
            for doc in declaration.documents.all():
                documents.append({
                    'id': str(doc.id),
                    'file_name': doc.original_filename,
                    'file_type': doc.get_file_type_display(),
                    'upload_status': doc.get_upload_status_display(),
                    'created_at': doc.created_at.isoformat(),
                    'file_size': doc.file_size
                })
            
            return Response({
                'id': str(declaration.id),
                'fiscal_year': declaration.fiscal_year,
                'status': declaration.get_status_display(),
                'summary_data': declaration.summary_data or {},
                'documents': documents,
                'created_at': declaration.created_at.isoformat(),
                'updated_at': declaration.updated_at.isoformat()
            })
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo declaración {pk}: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def list(self, request):
        """
        Listar todas las declaraciones del usuario
        
        GET /api/v1/declarations/
        """
        try:
            declarations = self.get_queryset()
            
            result = []
            for declaration in declarations:
                result.append({
                    'id': str(declaration.id),
                    'fiscal_year': declaration.fiscal_year,
                    'status': declaration.get_status_display(),
                    'total_income': declaration.get_total_income(),
                    'total_withholdings': declaration.get_total_withholdings(),
                    'estimated_tax': declaration.get_estimated_tax(),
                    'created_at': declaration.created_at.isoformat(),
                    'documents_count': declaration.documents.count()
                })
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"❌ Error listando declaraciones para usuario {request.user.id}: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def generate_summary(self, request, pk=None):
        """
        Generar resumen completo de la declaración
        
        POST /api/v1/declarations/{id}/generate_summary/
        """
        try:
            declaration = get_object_or_404(self.get_queryset(), pk=pk)
            
            # Lanzar tarea asíncrona
            task = generate_declaration_summary.delay(str(declaration.id))
            
            return Response({
                'message': 'Generación de resumen iniciada',
                'task_id': task.id,
                'declaration_id': str(declaration.id)
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            logger.error(f"❌ Error generando resumen para declaración {pk}: {str(e)}")
            return Response(
                {'error': 'Error interno del servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_document_upload(request, declaration_id):
    """
    Crear URL firmada para subir un documento
    
    POST /api/v1/declarations/{declaration_id}/documents/
    Body: {
        "file_name": "exogena_2024.xlsx",
        "file_type": "exogena_report"
    }
    """
    try:
        # Verificar que la declaración pertenece al usuario
        declaration = get_object_or_404(
            Declaration.objects.filter(user=request.user), 
            pk=declaration_id
        )
        
        file_name = request.data.get('file_name')
        file_type = request.data.get('file_type', 'other')
        
        if not file_name:
            return Response(
                {'error': 'file_name es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar tipo de archivo
        valid_file_types = [choice[0] for choice in Document.FILE_TYPE_CHOICES]
        if file_type not in valid_file_types:
            return Response(
                {'error': f'file_type debe ser uno de: {valid_file_types}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generar URL firmada
        gcs_service = get_gcs_service()
        upload_url, storage_path = gcs_service.generate_signed_url(
            file_name, 
            str(request.user.id)
        )
        
        # Crear registro de documento
        document = Document.objects.create(
            declaration=declaration,
            file_name=file_name,
            original_filename=file_name,
            file_type=file_type,
            storage_path=storage_path,
            upload_status='pending'
        )
        
        logger.info(f"✅ URL firmada generada para documento {document.id}")
        
        return Response({
            'document_id': str(document.id),
            'upload_url': upload_url,
            'storage_path': storage_path,
            'expires_in_minutes': 15
        })
        
    except Exception as e:
        logger.error(f"❌ Error creando URL de upload: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_document_status(request, declaration_id, document_id):
    """
    Actualizar el estado de un documento tras la subida
    
    PUT /api/v1/declarations/{declaration_id}/documents/{document_id}/status/
    Body: {"upload_status": "uploaded"}
    """
    try:
        # Verificar que el documento pertenece al usuario
        document = get_object_or_404(
            Document.objects.filter(
                declaration__user=request.user,
                declaration_id=declaration_id
            ), 
            pk=document_id
        )
        
        new_status = request.data.get('upload_status')
        
        if not new_status:
            return Response(
                {'error': 'upload_status es requerido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar estado
        valid_statuses = [choice[0] for choice in Document.UPLOAD_STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'upload_status debe ser uno de: {valid_statuses}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Actualizar estado
        document.upload_status = new_status
        document.save()
        
        # Si se marcó como subido, iniciar procesamiento
        if new_status == 'uploaded':
            # Verificar que el archivo existe en GCS
            gcs_service = get_gcs_service()
            if gcs_service.file_exists(document.storage_path):
                # Obtener metadatos del archivo
                metadata = gcs_service.get_file_metadata(document.storage_path)
                if metadata:
                    document.file_size = metadata.get('size')
                    document.content_type = metadata.get('content_type')
                    document.save()
                
                # Lanzar procesamiento asíncrono
                if document.is_exogena_file():
                    task = process_exogena_file.delay(str(document.id))
                    
                    logger.info(f"✅ Procesamiento iniciado para documento {document.id}, task: {task.id}")
                    
                    return Response({
                        'message': 'Documento marcado como subido y procesamiento iniciado',
                        'document_id': str(document.id),
                        'task_id': task.id,
                        'status': document.upload_status
                    }, status=status.HTTP_202_ACCEPTED)
                else:
                    return Response({
                        'message': 'Documento marcado como subido',
                        'document_id': str(document.id),
                        'status': document.upload_status
                    })
            else:
                document.mark_as_error('Archivo no encontrado en Google Cloud Storage')
                return Response(
                    {'error': 'Archivo no encontrado en el almacenamiento'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response({
            'message': 'Estado actualizado',
            'document_id': str(document.id),
            'status': document.upload_status
        })
        
    except Exception as e:
        logger.error(f"❌ Error actualizando estado de documento {document_id}: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_document_status(request, declaration_id, document_id):
    """
    Obtener el estado actual de un documento
    
    GET /api/v1/declarations/{declaration_id}/documents/{document_id}/status/
    """
    try:
        document = get_object_or_404(
            Document.objects.filter(
                declaration__user=request.user,
                declaration_id=declaration_id
            ), 
            pk=document_id
        )
        
        # Obtener logs recientes
        recent_logs = []
        for log in document.processing_logs.all()[:5]:  # Últimos 5 logs
            recent_logs.append({
                'level': log.level,
                'message': log.message,
                'created_at': log.created_at.isoformat()
            })
        
        return Response({
            'document_id': str(document.id),
            'file_name': document.original_filename,
            'file_type': document.get_file_type_display(),
            'upload_status': document.upload_status,
            'upload_status_display': document.get_upload_status_display(),
            'file_size': document.file_size,
            'error_message': document.error_message,
            'retry_count': document.retry_count,
            'can_retry': document.can_retry(),
            'processing_duration': str(document.get_processing_duration()) if document.get_processing_duration() else None,
            'created_at': document.created_at.isoformat(),
            'updated_at': document.updated_at.isoformat(),
            'recent_logs': recent_logs,
            'has_processed_data': bool(document.processed_data)
        })
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo estado de documento {document_id}: {str(e)}")
        return Response(
            {'error': 'Error interno del servidor'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def health_check(request):
    """
    Endpoint de health check
    
    GET /api/v1/health/
    """
    try:
        # Verificar conexión a base de datos
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Verificar conexión a Google Cloud Storage
        gcs_status = 'ok'
        try:
            gcs_service = get_gcs_service()
            gcs_service.client.list_buckets(max_results=1)
        except Exception:
            gcs_status = 'error'
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'services': {
                'database': 'ok',
                'google_cloud_storage': gcs_status
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=500)
