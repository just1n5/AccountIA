"""
Tareas asíncronas para procesamiento de documentos.
"""
from celery import shared_task
from django.db import transaction
from django.utils import timezone
import logging
import tempfile
import os

from .models import Document
# TEMPORALMENTE COMENTADO - Requiere pandas
from .parsers.excel_parser import ExogenaParser
from .services.storage_service import get_storage_service
from apps.declarations.models import Declaration, IncomeRecord

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_document(self, document_id: str):
    """
    Procesa un documento de forma asíncrona.
    
    Args:
        document_id: ID del documento a procesar
    """
    try:
        logger.info(f"Iniciando procesamiento de documento: {document_id}")
        
        # Obtener el documento
        document = Document.objects.select_related('declaration').get(id=document_id)
        
        # Marcar como procesando
        document.mark_as_processing()
        
        # Procesar según el tipo de documento
        if document.file_type == 'exogena_report':
            result = process_exogena_document(document)
        else:
            # Por ahora, otros tipos de documentos solo se marcan como procesados
            result = {
                'success': True,
                'data': {'message': 'Documento almacenado correctamente'}
            }
        
        if result['success']:
            document.mark_as_processed(result.get('data', {}))
            logger.info(f"Documento {document_id} procesado exitosamente")
        else:
            errors = result.get('errors', ['Error desconocido en el procesamiento'])
            document.mark_as_error(errors)
            logger.error(f"Error procesando documento {document_id}: {errors}")
            
    except Document.DoesNotExist:
        logger.error(f"Documento {document_id} no encontrado")
        
    except Exception as e:
        logger.error(f"Error inesperado procesando documento {document_id}: {str(e)}", exc_info=True)
        
        # Reintentar la tarea
        if self.request.retries < self.max_retries:
            logger.info(f"Reintentando tarea para documento {document_id} (intento {self.request.retries + 1})")
            raise self.retry(exc=e, countdown=60 * (self.request.retries + 1))
        else:
            # Si se agotan los reintentos, marcar como error
            try:
                document = Document.objects.get(id=document_id)
                document.mark_as_error([f"Error después de {self.max_retries} intentos: {str(e)}"])
            except Document.DoesNotExist:
                pass


def process_exogena_document(document: Document) -> dict:
    """
    Procesa un documento de información exógena.
    
    Args:
        document: Instancia del documento
        
    Returns:
        Dict con el resultado del procesamiento
    """
    try:
        # Descargar el archivo a un directorio temporal
        storage_service = get_storage_service()
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            
            # Descargar el archivo
            logger.info(f"Descargando archivo {document.storage_path}")
            file_content = storage_service.download_file(document.storage_path)
            tmp_file.write(file_content)
            tmp_file.flush()
            
            # Parsear el archivo
            logger.info(f"Parseando archivo Excel: {tmp_path}")
            # TEMPORALMENTE DESHABILITADO - Requiere pandas
            logger.warning("Excel parser temporalmente deshabilitado - pandas no instalado")
            return {
                'success': False,
                'errors': ['Parser de Excel temporalmente deshabilitado. Instalar pandas para habilitar.']
            }
            # parser = ExogenaParser()
            # parse_result = parser.parse_excel_file(tmp_path)
            
            # Eliminar archivo temporal
            os.unlink(tmp_path)
            
            if not parse_result['success']:
                return {
                    'success': False,
                    'errors': parse_result['errors']
                }
            
            # Guardar los registros en la base de datos
            with transaction.atomic():
                declaration = document.declaration
                records_created = 0
                
                # Limpiar registros anteriores si existen
                declaration.income_records.all().delete()
                
                # Crear nuevos registros
                for record_data in parse_result['records']:
                    IncomeRecord.objects.create(
                        declaration=declaration,
                        **{k: v for k, v in record_data.items() 
                           if k not in ['source_sheet', 'source_row']}
                    )
                    records_created += 1
                
                # Actualizar totales en la declaración
                stats = parse_result['stats']
                declaration.total_income = stats['total_income']
                declaration.total_withholdings = stats['total_withholdings']
                
                # Agregar advertencias si las hay
                if parse_result['warnings']:
                    declaration.processing_warnings = parse_result['warnings']
                
                declaration.save()
                
                logger.info(f"Creados {records_created} registros de ingresos para declaración {declaration.id}")
            
            # Preparar datos para almacenar en el documento
            processed_data = {
                'success': True,
                'stats': {
                    'total_records': stats['total_records'],
                    'processed_records': stats['processed_records'],
                    'skipped_records': stats['skipped_records'],
                    'total_income': str(stats['total_income']),
                    'total_withholdings': str(stats['total_withholdings']),
                    'income_by_type': {
                        k: {
                            'count': v['count'],
                            'gross_amount': str(v['gross_amount']),
                            'withholding_amount': str(v['withholding_amount'])
                        }
                        for k, v in stats['income_by_type'].items()
                    },
                    'income_by_schedule': {
                        k: {
                            'count': v['count'],
                            'gross_amount': str(v['gross_amount']),
                            'withholding_amount': str(v['withholding_amount'])
                        }
                        for k, v in stats['income_by_schedule'].items()
                    }
                },
                'errors': parse_result['errors'],
                'warnings': parse_result['warnings']
            }
            
            return {
                'success': True,
                'data': processed_data
            }
            
    except Exception as e:
        logger.error(f"Error procesando documento de exógena: {str(e)}", exc_info=True)
        return {
            'success': False,
            'errors': [f"Error al procesar el archivo: {str(e)}"]
        }


@shared_task(bind=True)
def process_declaration_documents(self, declaration_id: str):
    """
    Procesa todos los documentos de una declaración.
    
    Args:
        declaration_id: ID de la declaración
    """
    try:
        logger.info(f"Procesando documentos de declaración: {declaration_id}")
        
        declaration = Declaration.objects.prefetch_related('documents').get(id=declaration_id)
        
        # Obtener documentos pendientes de procesar
        pending_documents = declaration.documents.filter(
            upload_status__in=['uploaded', 'error'],
            is_active=True
        )
        
        if not pending_documents.exists():
            logger.info(f"No hay documentos pendientes para declaración {declaration_id}")
            return
        
        # Procesar cada documento
        for document in pending_documents:
            process_document.delay(str(document.id))
        
        logger.info(f"Lanzadas {pending_documents.count()} tareas de procesamiento para declaración {declaration_id}")
        
    except Declaration.DoesNotExist:
        logger.error(f"Declaración {declaration_id} no encontrada")
    except Exception as e:
        logger.error(f"Error procesando documentos de declaración {declaration_id}: {str(e)}", exc_info=True)


@shared_task
def cleanup_old_documents():
    """
    Tarea periódica para limpiar documentos antiguos.
    """
    try:
        # Documentos en estado 'uploading' por más de 24 horas
        cutoff_time = timezone.now() - timezone.timedelta(hours=24)
        
        old_uploading = Document.objects.filter(
            upload_status='uploading',
            created_at__lt=cutoff_time
        )
        
        count = old_uploading.count()
        if count > 0:
            old_uploading.update(
                upload_status='error',
                processing_errors=['Tiempo de carga expirado']
            )
            logger.info(f"Marcados {count} documentos como error por tiempo de carga expirado")
            
        # TODO: Limpiar archivos huérfanos en storage
        
    except Exception as e:
        logger.error(f"Error en limpieza de documentos: {str(e)}", exc_info=True)


@shared_task
def generate_declaration_summary(declaration_id: str):
    """
    Genera un resumen completo de la declaración.
    
    Args:
        declaration_id: ID de la declaración
    """
    try:
        declaration = Declaration.objects.prefetch_related(
            'income_records',
            'documents'
        ).get(id=declaration_id)
        
        # TODO: Implementar generación de resumen con IA
        # Por ahora, solo actualizar estadísticas básicas
        
        summary = {
            'total_income_sources': declaration.income_records.values('third_party_nit').distinct().count(),
            'document_count': declaration.documents.filter(is_active=True).count(),
            'processed_documents': declaration.documents.filter(
                upload_status='processed',
                is_active=True
            ).count(),
            'has_errors': declaration.documents.filter(
                upload_status='error',
                is_active=True
            ).exists()
        }
        
        # Actualizar declaration_data con el resumen
        declaration.declaration_data['summary'] = summary
        declaration.save(update_fields=['declaration_data', 'updated_at'])
        
        logger.info(f"Resumen generado para declaración {declaration_id}")
        
    except Declaration.DoesNotExist:
        logger.error(f"Declaración {declaration_id} no encontrada")
    except Exception as e:
        logger.error(f"Error generando resumen para declaración {declaration_id}: {str(e)}", exc_info=True)
