"""
Endpoint de upload super simplificado para debugging del error 500.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import traceback
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def debug_upload(request, declaration_id):
    """
    Upload de debugging que reporta cada paso
    """
    try:
        # Paso 1: Verificar configuración
        logger.info("=== DEBUG UPLOAD START ===")
        logger.info(f"Declaration ID: {declaration_id}")
        logger.info(f"DEV_SKIP_AUTH_FOR_TESTING: {getattr(settings, 'DEV_SKIP_AUTH_FOR_TESTING', 'NOT_SET')}")
        
        if not getattr(settings, 'DEV_SKIP_AUTH_FOR_TESTING', False):
            return Response(
                {'error': 'Testing mode not enabled'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Paso 2: Verificar archivo
        logger.info(f"Files in request: {list(request.FILES.keys())}")
        if 'file' not in request.FILES:
            return Response(
                {'error': 'No file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        logger.info(f"File name: {file.name}, Size: {file.size}")
        
        # Paso 3: Intentar importar modelos
        try:
            from apps.declarations.models import Declaration
            logger.info("✅ Declaration model imported")
        except ImportError as e:
            logger.error(f"❌ Declaration import failed: {e}")
            return Response({'error': f'Declaration import error: {e}'}, status=500)
        
        try:
            from apps.documents.models import Document
            logger.info("✅ Document model imported")
        except ImportError as e:
            logger.error(f"❌ Document import failed: {e}")
            return Response({'error': f'Document import error: {e}'}, status=500)
        
        # Paso 4: Buscar declaración (manejo especial para demo)
        try:
            if declaration_id == 'demo-declaration-1':
                # Buscar la primera declaración disponible para testing
                declaration = Declaration.objects.first()
                if not declaration:
                    # Crear una declaración demo si no existe ninguna
                    from apps.users.models import User
                    import uuid
                    
                    # Crear usuario si no existe
                    user_uuid = uuid.UUID('12345678-1234-5678-9012-123456789012')
                    user, _ = User.objects.get_or_create(
                        id=user_uuid,
                        defaults={
                            'email': 'test@example.com',
                            'first_name': 'Usuario',
                            'last_name': 'de Prueba',
                            'username': 'usuario_prueba',
                            'is_active': True
                        }
                    )
                    
                    # Crear declaración demo
                    declaration = Declaration.objects.create(
                        user=user,
                        fiscal_year=2024,
                        status='draft'
                    )
                    logger.info(f"✅ Declaración demo creada automáticamente: {declaration.id}")
            else:
                declaration = Declaration.objects.get(id=declaration_id)
            
            logger.info(f"✅ Declaration found: {declaration}")
        except Declaration.DoesNotExist:
            logger.error(f"❌ Declaration not found: {declaration_id}")
            return Response({'error': f'Declaration {declaration_id} not found'}, status=404)
        except Exception as e:
            logger.error(f"❌ Error getting declaration: {e}")
            return Response({'error': f'Database error: {e}'}, status=500)
        
        # Paso 5: Intentar crear documento básico
        try:
            document = Document.objects.create(
                declaration=declaration,
                file_name=file.name,
                original_file_name=file.name,
                file_size=file.size,
                file_type='exogena_report',
                upload_status='uploaded',
                storage_path=f'debug/{declaration_id}/{file.name}'
            )
            logger.info(f"✅ Document created: {document.id}")
        except Exception as e:
            logger.error(f"❌ Error creating document: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return Response({'error': f'Document creation error: {e}'}, status=500)
        
        # Paso 6: PROCESAMIENTO REAL DEL ARCHIVO
        try:
            # Guardar archivo temporalmente para procesamiento
            import tempfile
            import os
            
            # Detectar extensión del archivo
            file_ext = os.path.splitext(file.name)[1].lower()
            if file_ext not in ['.xlsx', '.xls']:
                logger.warning(f"Archivo no es Excel: {file_ext}, usando datos demo")
                # Fallback a datos demo si no es Excel
                demo_data = {
                    'success': True,
                    'records': [{
                        'nit_tercero': '900123456-1',
                        'nombre_tercero': 'EMPRESA DEMO (fallback)',
                        'valor_bruto': 1000000,
                        'valor_retencion': 100000
                    }],
                    'metadata': {
                        'total_registros': 1,
                        'total_ingresos': 1000000,
                        'total_retenciones': 100000,
                        'archivo_procesado': file.name,
                        'processing_type': 'DEMO_FALLBACK'
                    },
                    'warnings': [f'Archivo {file.name} no es Excel válido, usando datos demo']
                }
            else:
                # Procesar archivo Excel REAL
                with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                    # Escribir contenido del archivo subido al archivo temporal
                    for chunk in file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name
                
                logger.info(f"[REAL PROCESSING] Procesando archivo Excel real: {file.name}")
                
                # Importar y usar parser robusto
                try:
                    from apps.documents.parsers.excel_parser import ExogenaParser
                    parser = ExogenaParser()
                    
                    # Procesar archivo real
                    real_data = parser.parse_excel_file(temp_file_path)
                    
                    # Limpiar archivo temporal
                    os.unlink(temp_file_path)
                    
                    if real_data['success'] and real_data.get('records'):
                        # Éxito en procesamiento real
                        logger.info(f"[REAL SUCCESS] Procesados {len(real_data['records'])} registros reales")
                        
                        # Convertir formato para compatibilidad
                        total_income = float(real_data.get('stats', {}).get('total_income', 0))
                        total_withholdings = float(real_data.get('stats', {}).get('total_withholdings', 0))
                        
                        demo_data = {
                            'success': True,
                            'records': real_data['records'][:5],  # Primeros 5 registros para preview
                            'metadata': {
                                'total_registros': len(real_data['records']),
                                'total_ingresos': total_income,
                                'total_retenciones': total_withholdings,
                                'archivo_procesado': file.name,
                                'processing_type': 'REAL_DATA'
                            },
                            'full_data': real_data,  # Datos completos
                            'warnings': real_data.get('warnings', [])
                        }
                        
                        # Actualizar declaración con datos REALES
                        try:
                            declaration.total_income = str(total_income)
                            declaration.total_withholdings = str(total_withholdings)
                            declaration.save()
                            logger.info(f"[REAL DATA] Declaración actualizada - Ingresos: {total_income}, Retenciones: {total_withholdings}")
                        except Exception as e:
                            logger.error(f"Error actualizando declaración: {e}")
                            
                    else:
                        # Fallo en procesamiento real, usar demo como fallback
                        logger.warning(f"[FALLBACK] Procesamiento real falló: {real_data.get('errors', [])}")
                        demo_data = {
                            'success': True,
                            'records': [{
                                'nit_tercero': '900123456-1',
                                'nombre_tercero': 'EMPRESA DEMO (fallback por errores)',
                                'valor_bruto': 1000000,
                                'valor_retencion': 100000
                            }],
                            'metadata': {
                                'total_registros': 1,
                                'total_ingresos': 1000000,
                                'total_retenciones': 100000,
                                'archivo_procesado': file.name,
                                'processing_type': 'DEMO_FALLBACK'
                            },
                            'warnings': ['Procesamiento real falló, usando datos demo como fallback'],
                            'real_processing_errors': real_data.get('errors', [])[:3]  # Primeros 3 errores
                        }
                        
                except ImportError as e:
                    logger.error(f"[ERROR] Parser no disponible: {e}")
                    # Fallback por dependencias faltantes
                    demo_data = {
                        'success': True,
                        'records': [{
                            'nit_tercero': '900123456-1',
                            'nombre_tercero': 'EMPRESA DEMO (parser no disponible)',
                            'valor_bruto': 1000000,
                            'valor_retencion': 100000
                        }],
                        'metadata': {
                            'total_registros': 1,
                            'total_ingresos': 1000000,
                            'total_retenciones': 100000,
                            'archivo_procesado': file.name,
                            'processing_type': 'DEMO_PARSER_ERROR'
                        },
                        'warnings': [f'Parser no disponible: {e}']
                    }
                except Exception as e:
                    logger.error(f"[ERROR] Error en procesamiento real: {e}")
                    # Fallback por otros errores
                    demo_data = {
                        'success': True,
                        'records': [{
                            'nit_tercero': '900123456-1',
                            'nombre_tercero': 'EMPRESA DEMO (error procesamiento)',
                            'valor_bruto': 1000000,
                            'valor_retencion': 100000
                        }],
                        'metadata': {
                            'total_registros': 1,
                            'total_ingresos': 1000000,
                            'total_retenciones': 100000,
                            'archivo_procesado': file.name,
                            'processing_type': 'DEMO_ERROR_FALLBACK'
                        },
                        'warnings': [f'Error en procesamiento: {str(e)[:100]}...']
                    }
                    
        except Exception as e:
            logger.error(f"❌ Error crítico en procesamiento: {e}")
            # Fallback final a datos demo básicos
            demo_data = {
                'success': True,
                'records': [{
                    'nit_tercero': '900123456-1',
                    'nombre_tercero': 'EMPRESA DEMO (error crítico)',
                    'valor_bruto': 1000000,
                    'valor_retencion': 100000
                }],
                'metadata': {
                    'total_registros': 1,
                    'total_ingresos': 1000000,
                    'total_retenciones': 100000,
                    'archivo_procesado': file.name,
                    'processing_type': 'DEMO_CRITICAL_ERROR'
                },
                'warnings': [f'Error crítico: {str(e)[:100]}...']
            }
        
        # Paso 7: Actualizar documento
        try:
            document.processed_data = demo_data
            document.upload_status = 'processed'
            document.save()
            logger.info(f"✅ Document updated with {'real data' if demo_data.get('metadata', {}).get('processing_type') == 'REAL_DATA' else 'demo data'}")
        except Exception as e:
            logger.error(f"❌ Error updating document: {e}")
            return Response({'error': f'Document update error: {e}'}, status=500)
        
        logger.info("=== DEBUG UPLOAD SUCCESS ===")
        
        return Response({
            'success': True,
            'document_id': str(document.id),
            'message': 'Debug upload completed successfully',
            'processed_data': demo_data,  # Incluir los datos procesados
            'status': 'processed',  # Estado para el frontend
            'debug_info': {
                'declaration_id': declaration_id,
                'file_name': file.name,
                'file_size': file.size,
                'document_created': True,
                'backend_working': True
            }
        })
        
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response(
            {'error': f'Critical error: {e}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
