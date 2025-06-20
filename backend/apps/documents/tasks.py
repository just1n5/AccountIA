"""
Tareas de Celery para el procesamiento asíncrono de documentos
"""

import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction

from .models import Document, Declaration, ProcessingLog
from .services.storage_service import get_gcs_service
from .parsers.excel_parser import parse_exogena_file, ExogenaParsingError

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_exogena_file(self, document_id):
    """
    Tarea asíncrona para procesar archivo de información exógena
    
    Args:
        document_id: ID del documento a procesar
    """
    try:
        # Obtener el documento
        document = Document.objects.get(id=document_id)
        declaration = document.declaration
        
        logger.info(f"🔄 Iniciando procesamiento de documento {document_id} - {document.original_filename}")
        
        # Marcar como procesando
        document.mark_as_processing()
        
        # Log de inicio
        ProcessingLog.objects.create(
            document=document,
            level='info',
            message='Iniciando procesamiento de archivo de información exógena',
            details={'task_id': self.request.id}
        )
        
        # 1. Descargar archivo desde Google Cloud Storage
        try:
            gcs_service = get_gcs_service()
            file_content = gcs_service.download_file(document.storage_path)
            logger.info(f"✅ Archivo descargado: {len(file_content)} bytes")
            
        except Exception as e:
            error_msg = f"Error descargando archivo: {str(e)}"
            logger.error(f"❌ {error_msg}")
            document.mark_as_error(error_msg)
            
            ProcessingLog.objects.create(
                document=document,
                level='error',
                message=error_msg,
                details={'storage_path': document.storage_path}
            )
            return {'success': False, 'error': error_msg}
        
        # 2. Parsear archivo Excel
        try:
            parsing_result = parse_exogena_file(file_content, document.original_filename)
            
            if not parsing_result.get('success', False):
                error_msg = f"Error parseando archivo: {parsing_result.get('error', 'Error desconocido')}"
                logger.error(f"❌ {error_msg}")
                document.mark_as_error(error_msg)
                
                ProcessingLog.objects.create(
                    document=document,
                    level='error',
                    message=error_msg,
                    details=parsing_result
                )
                return {'success': False, 'error': error_msg}
            
            logger.info(f"✅ Archivo parseado exitosamente: {parsing_result['total_records']} registros")
            
        except ExogenaParsingError as e:
            error_msg = f"Error específico de parsing: {str(e)}"
            logger.error(f"❌ {error_msg}")
            document.mark_as_error(error_msg)
            
            ProcessingLog.objects.create(
                document=document,
                level='error',
                message=error_msg
            )
            return {'success': False, 'error': error_msg}
        
        except Exception as e:
            error_msg = f"Error inesperado parseando archivo: {str(e)}"
            logger.error(f"❌ {error_msg}")
            document.mark_as_error(error_msg)
            
            ProcessingLog.objects.create(
                document=document,
                level='error',
                message=error_msg
            )
            return {'success': False, 'error': error_msg}
        
        # 3. Actualizar documento y declaración con los datos procesados
        try:
            with transaction.atomic():
                # Actualizar documento
                document.mark_as_processed(parsing_result)
                
                # Actualizar declaración con el resumen
                summary = parsing_result.get('summary', {})
                if declaration.summary_data:
                    # Combinar con datos existentes
                    declaration.summary_data.update(summary)
                else:
                    declaration.summary_data = summary
                
                declaration.status = 'completed'
                declaration.save()
                
                logger.info(f"✅ Datos guardados en base de datos")
            
        except Exception as e:
            error_msg = f"Error guardando datos: {str(e)}"
            logger.error(f"❌ {error_msg}")
            document.mark_as_error(error_msg)
            
            ProcessingLog.objects.create(
                document=document,
                level='error',
                message=error_msg
            )
            return {'success': False, 'error': error_msg}
        
        # 4. Log de éxito
        ProcessingLog.objects.create(
            document=document,
            level='info',
            message='Procesamiento completado exitosamente',
            details={
                'total_records': parsing_result['total_records'],
                'total_income': summary.get('total_ingresos', 0),
                'total_withholdings': summary.get('total_retenciones', 0),
                'processing_time': str(document.get_processing_duration())
            }
        )
        
        logger.info(f"🎉 Procesamiento completado exitosamente para documento {document_id}")
        
        return {
            'success': True,
            'document_id': str(document_id),
            'total_records': parsing_result['total_records'],
            'total_income': summary.get('total_ingresos', 0),
            'total_withholdings': summary.get('total_retenciones', 0)
        }
        
    except Document.DoesNotExist:
        error_msg = f"Documento {document_id} no encontrado"
        logger.error(f"❌ {error_msg}")
        return {'success': False, 'error': error_msg}
        
    except Exception as exc:
        # Reintentar en caso de error
        error_msg = f"Error inesperado procesando documento {document_id}: {str(exc)}"
        logger.error(f"❌ {error_msg}")
        
        try:
            document = Document.objects.get(id=document_id)
            document.mark_as_error(error_msg)
            
            ProcessingLog.objects.create(
                document=document,
                level='error',
                message=f"Error en intento {self.request.retries + 1}: {error_msg}"
            )
        except:
            pass  # Si no podemos actualizar el documento, continuar
        
        # Reintentar si no hemos excedido el límite
        if self.request.retries < self.max_retries:
            logger.info(f"🔄 Reintentando procesamiento de documento {document_id} (intento {self.request.retries + 1})")
            raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
        else:
            logger.error(f"❌ Se agotaron los reintentos para documento {document_id}")
            return {'success': False, 'error': error_msg}


@shared_task
def cleanup_failed_documents():
    """
    Tarea para limpiar documentos que han fallado múltiples veces
    """
    logger.info("🧹 Iniciando limpieza de documentos fallidos")
    
    # Buscar documentos con errores que no pueden reintentarse
    failed_documents = Document.objects.filter(
        upload_status='error',
        retry_count__gte=3,
        updated_at__lt=timezone.now() - timezone.timedelta(hours=24)
    )
    
    count = 0
    for document in failed_documents:
        try:
            # Eliminar archivo de Google Cloud Storage
            gcs_service = get_gcs_service()
            if gcs_service.file_exists(document.storage_path):
                gcs_service.delete_file(document.storage_path)
            
            # Marcar documento para auditoría (no eliminar de BD)
            ProcessingLog.objects.create(
                document=document,
                level='info',
                message='Documento marcado para limpieza automática',
                details={'reason': 'Multiple failures', 'retry_count': document.retry_count}
            )
            
            count += 1
            
        except Exception as e:
            logger.error(f"❌ Error limpiando documento {document.id}: {str(e)}")
    
    logger.info(f"✅ Limpieza completada: {count} documentos procesados")
    return {'cleaned_documents': count}


@shared_task
def generate_declaration_summary(declaration_id):
    """
    Tarea para generar resumen completo de una declaración
    """
    try:
        declaration = Declaration.objects.get(id=declaration_id)
        logger.info(f"📊 Generando resumen para declaración {declaration_id}")
        
        # Obtener todos los documentos procesados
        processed_documents = declaration.documents.filter(upload_status='processed')
        
        combined_summary = {
            'total_ingresos': 0,
            'total_retenciones': 0,
            'total_rentas_trabajo': 0,
            'total_rentas_capital': 0,
            'total_rentas_no_laborales': 0,
            'documents_processed': len(processed_documents),
            'generated_at': timezone.now().isoformat()
        }
        
        # Combinar datos de todos los documentos
        for document in processed_documents:
            if document.processed_data and 'summary' in document.processed_data:
                doc_summary = document.processed_data['summary']
                
                combined_summary['total_ingresos'] += doc_summary.get('total_ingresos', 0)
                combined_summary['total_retenciones'] += doc_summary.get('total_retenciones', 0)
                combined_summary['total_rentas_trabajo'] += doc_summary.get('total_rentas_trabajo', 0)
                combined_summary['total_rentas_capital'] += doc_summary.get('total_rentas_capital', 0)
                combined_summary['total_rentas_no_laborales'] += doc_summary.get('total_rentas_no_laborales', 0)
        
        # Calcular impuesto estimado
        total_income = combined_summary['total_ingresos']
        if total_income > 0:
            # Cálculo simplificado - en producción usar lógica fiscal real
            base_gravable = max(0, total_income - 47000000)  # Aprox. UVT 2024
            combined_summary['impuesto_estimado'] = base_gravable * 0.19
            combined_summary['saldo_a_pagar'] = max(0, combined_summary['impuesto_estimado'] - combined_summary['total_retenciones'])
        
        # Actualizar declaración
        declaration.summary_data = combined_summary
        declaration.mark_as_completed()
        
        logger.info(f"✅ Resumen generado para declaración {declaration_id}")
        
        return {
            'success': True,
            'declaration_id': str(declaration_id),
            'summary': combined_summary
        }
        
    except Declaration.DoesNotExist:
        error_msg = f"Declaración {declaration_id} no encontrada"
        logger.error(f"❌ {error_msg}")
        return {'success': False, 'error': error_msg}
        
    except Exception as e:
        error_msg = f"Error generando resumen: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return {'success': False, 'error': error_msg}


@shared_task
def test_task(message="Hello from Celery!"):
    """
    Tarea de prueba para verificar que Celery está funcionando
    """
    logger.info(f"🧪 Test task ejecutada: {message}")
    return {
        'success': True,
        'message': f"Test task completada: {message}",
        'timestamp': timezone.now().isoformat()
    }
