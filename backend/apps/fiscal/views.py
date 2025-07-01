"""
Vistas de la API para análisis fiscal inteligente
"""
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from .services.intelligent_processor import get_intelligent_fiscal_processor

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_fiscal_data(request):
    """
    Endpoint principal para análisis fiscal inteligente
    
    POST /api/v1/fiscal/analyze/
    """
    try:
        logger.info(f"🚀 Iniciando análisis fiscal para usuario: {request.user}")
        
        # Obtener datos de la request
        data = request.data
        file_data = request.FILES.get('exogena_file')
        user_context = data.get('user_context', {})
        
        # Validar entrada
        if not file_data and not data.get('use_demo', False):
            return Response({
                'success': False,
                'error': 'Se requiere archivo de exógena o usar datos demo'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener procesador inteligente
        processor = get_intelligent_fiscal_processor()
        
        # Procesar datos
        if data.get('use_demo', False):
            result = processor.process_complete_analysis('demo', user_context)
        else:
            result = processor.process_complete_analysis(file_data, user_context)
        
        if result['success']:
            logger.info(f"✅ Análisis completado exitosamente en {result['processing_time']:.2f}s")
            return Response(result, status=status.HTTP_200_OK)
        else:
            logger.error(f"❌ Error en análisis: {result.get('error', 'Error desconocido')}")
            return Response(result, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
    except Exception as e:
        logger.error(f"❌ Error crítico en endpoint de análisis: {str(e)}")
        return Response({
            'success': False,
            'error': f'Error interno del servidor: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_parser_only(request):
    """
    Endpoint para probar solo el parser (útil para debugging)
    
    POST /api/v1/fiscal/test-parser/
    """
    try:
        file_data = request.FILES.get('exogena_file')
        
        if not file_data and not request.data.get('use_demo', False):
            return Response({
                'success': False,
                'error': 'Se requiere archivo de exógena o usar datos demo'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        from apps.documents.parsers.excel_parser import ExogenaParser
        parser = ExogenaParser()
        
        if request.data.get('use_demo', False):
            result = parser.parse_demo_data()
        else:
            result = parser.parse_excel_file(file_data)
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en test de parser: {str(e)}")
        return Response({
            'success': False,
            'error': f'Error en parser: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_fiscal_limits(request):
    """
    Obtiene límites fiscales vigentes
    
    GET /api/v1/fiscal/limits/
    """
    try:
        from .services.analysis_service import FiscalAnalysisService
        
        service = FiscalAnalysisService()
        
        limits_info = {
            'uvt_2024': service.UVT_2024,
            'fiscal_limits': service.FISCAL_LIMITS,
            'deduction_categories': service.DEDUCTION_CATEGORIES,
            'tax_brackets': [
                {
                    'min_income': bracket[0],
                    'max_income': bracket[1] if bracket[1] != float('inf') else None,
                    'rate': bracket[2],
                    'fixed_amount': bracket[3] if len(bracket) > 3 else 0
                }
                for bracket in service.TARIFA_RENTA
            ]
        }
        
        return Response({
            'success': True,
            'limits': limits_info
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error obteniendo límites fiscales: {str(e)}")
        return Response({
            'success': False,
            'error': f'Error obteniendo límites: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def simulate_deductions(request):
    """
    Simula el impacto de diferentes deducciones
    
    POST /api/v1/fiscal/simulate-deductions/
    """
    try:
        data = request.data
        base_income = data.get('base_income', 0)
        potential_deductions = data.get('deductions', {})
        
        from .services.analysis_service import FiscalAnalysisService
        service = FiscalAnalysisService()
        
        # Simular diferentes escenarios
        scenarios = []
        
        # Escenario base (sin deducciones adicionales)
        base_tax = service._calculate_income_tax({'base_gravable': base_income})
        scenarios.append({
            'name': 'Sin deducciones adicionales',
            'deductions': 0,
            'tax_amount': base_tax['impuesto_calculado'],
            'net_benefit': 0
        })
        
        # Escenario con deducciones
        total_deductions = sum(potential_deductions.values())
        adjusted_income = max(0, base_income - total_deductions)
        adjusted_tax = service._calculate_income_tax({'base_gravable': adjusted_income})
        
        scenarios.append({
            'name': 'Con deducciones propuestas',
            'deductions': total_deductions,
            'tax_amount': adjusted_tax['impuesto_calculado'],
            'net_benefit': base_tax['impuesto_calculado'] - adjusted_tax['impuesto_calculado']
        })
        
        return Response({
            'success': True,
            'scenarios': scenarios,
            'recommendations': [
                f"Ahorro potencial: ${scenarios[1]['net_benefit']:,.0f}",
                f"Reducción de impuesto: {(scenarios[1]['net_benefit']/base_tax['impuesto_calculado']*100):.1f}%" if base_tax['impuesto_calculado'] > 0 else "0%"
            ]
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error en simulación de deducciones: {str(e)}")
        return Response({
            'success': False,
            'error': f'Error en simulación: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def health_check(request):
    """
    Health check para el módulo fiscal
    
    GET /api/v1/fiscal/health/
    """
    try:
        # Verificar que los servicios se pueden instanciar
        processor = get_intelligent_fiscal_processor()
        
        return Response({
            'success': True,
            'status': 'healthy',
            'services': {
                'intelligent_processor': 'ok',
                'fiscal_analyzer': 'ok',
                'anomaly_detector': 'ok',
                'consistency_validator': 'ok'
            },
            'version': '1.0.0'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
