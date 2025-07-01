"""
Parser básico sin pandas para MVP.
"""
from typing import Dict, List, Any
from decimal import Decimal
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ExogenaParser:
    """
    Parser básico que no requiere pandas para el MVP.
    """
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.stats = {
            'total_records': 0,
            'processed_records': 0,
            'skipped_records': 0,
            'total_income': Decimal('0'),
            'total_withholdings': Decimal('0'),
        }
    
    def parse_excel_file(self, file_path: str) -> Dict[str, Any]:
        """
        Por ahora retorna datos de ejemplo hasta que implementemos el parser real.
        """
        try:
            logger.info(f"Procesando archivo: {file_path}")
            
            # Datos de ejemplo para el MVP
            example_records = [
                {
                    'third_party_nit': '900123456',
                    'third_party_name': 'EMPRESA EJEMPLO SAS',
                    'concept_code': '5001',
                    'concept_description': 'Salarios',
                    'income_type': 'salary',
                    'tax_schedule': 'labor',
                    'gross_amount': Decimal('1000000'),
                    'withholding_amount': Decimal('50000'),
                    'source_row': 1
                },
                {
                    'third_party_nit': '900654321',
                    'third_party_name': 'HONORARIOS PROFESIONALES LTDA',
                    'concept_code': '5002',
                    'concept_description': 'Honorarios',
                    'income_type': 'honorarios',
                    'tax_schedule': 'labor',
                    'gross_amount': Decimal('500000'),
                    'withholding_amount': Decimal('55000'),
                    'source_row': 2
                }
            ]
            
            # Calcular estadísticas
            self.stats['total_records'] = len(example_records)
            self.stats['processed_records'] = len(example_records)
            
            for record in example_records:
                self.stats['total_income'] += record['gross_amount']
                self.stats['total_withholdings'] += record['withholding_amount']
            
            return {
                'success': True,
                'records': example_records,
                'stats': self.stats,
                'errors': self.errors,
                'warnings': ['Usando datos de ejemplo para MVP. Parser completo próximamente.']
            }
            
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return {
                'success': False,
                'records': [],
                'stats': self.stats,
                'errors': [f"Error: {str(e)}"],
                'warnings': []
            }
    
    def parse_demo_data(self) -> Dict[str, Any]:
        """
        Retorna datos demo estructurados para el MVP.
        Este método es específico para el endpoint de testing.
        """
        try:
            # Datos demo más realistas para el wizard
            demo_records = [
                {
                    'nit_tercero': '900123456-1',
                    'nombre_tercero': 'EMPRESA TECNOLOGÍA SAS',
                    'codigo_concepto': '5001',
                    'descripcion_concepto': 'Salarios y prestaciones sociales',
                    'tipo_ingreso': 'salario',
                    'cedula_tributaria': 'rentas_trabajo',
                    'valor_bruto': 45000000,
                    'valor_retencion': 2500000,
                    'fila_origen': 1,
                    'mes': 'Diciembre',
                    'año': 2024
                },
                {
                    'nit_tercero': '800654321-2',
                    'nombre_tercero': 'CONSULTORES PROFESIONALES LTDA',
                    'codigo_concepto': '5002',
                    'descripcion_concepto': 'Honorarios profesionales',
                    'tipo_ingreso': 'honorarios',
                    'cedula_tributaria': 'rentas_trabajo',
                    'valor_bruto': 8500000,
                    'valor_retencion': 850000,
                    'fila_origen': 2,
                    'mes': 'Diciembre',
                    'año': 2024
                },
                {
                    'nit_tercero': '700987654-3',
                    'nombre_tercero': 'INVERSIONES FINANCIERAS SA',
                    'codigo_concepto': '1001',
                    'descripcion_concepto': 'Rendimientos financieros',
                    'tipo_ingreso': 'financiero',
                    'cedula_tributaria': 'rentas_capital',
                    'valor_bruto': 2800000,
                    'valor_retencion': 420000,
                    'fila_origen': 3,
                    'mes': 'Diciembre',
                    'año': 2024
                }
            ]
            
            # Calcular totales
            total_ingresos = sum(record['valor_bruto'] for record in demo_records)
            total_retenciones = sum(record['valor_retencion'] for record in demo_records)
            
            # Clasificación por cédulas
            cedulas = {
                'rentas_trabajo': {
                    'total_ingresos': sum(r['valor_bruto'] for r in demo_records if r['cedula_tributaria'] == 'rentas_trabajo'),
                    'total_retenciones': sum(r['valor_retencion'] for r in demo_records if r['cedula_tributaria'] == 'rentas_trabajo'),
                    'registros': len([r for r in demo_records if r['cedula_tributaria'] == 'rentas_trabajo'])
                },
                'rentas_capital': {
                    'total_ingresos': sum(r['valor_bruto'] for r in demo_records if r['cedula_tributaria'] == 'rentas_capital'),
                    'total_retenciones': sum(r['valor_retencion'] for r in demo_records if r['cedula_tributaria'] == 'rentas_capital'),
                    'registros': len([r for r in demo_records if r['cedula_tributaria'] == 'rentas_capital'])
                }
            }
            
            return {
                'success': True,
                'records': demo_records,
                'metadata': {
                    'total_registros': len(demo_records),
                    'total_ingresos': total_ingresos,
                    'total_retenciones': total_retenciones,
                    'periodo_fiscal': 2024,
                    'archivo_procesado': 'demo_exogena_2024.xlsx',
                    'fecha_procesamiento': '2024-12-24T10:30:00Z'
                },
                'clasificacion_cedulas': cedulas,
                'resumen': {
                    'ingresos_laborales': cedulas['rentas_trabajo']['total_ingresos'],
                    'ingresos_capital': cedulas['rentas_capital']['total_ingresos'],
                    'retenciones_laborales': cedulas['rentas_trabajo']['total_retenciones'],
                    'retenciones_capital': cedulas['rentas_capital']['total_retenciones']
                },
                'warnings': [
                    'Datos demo generados para Sprint 2 - MVP',
                    'Parser completo de Excel será implementado en siguiente iteración'
                ],
                'errors': []
            }
            
        except Exception as e:
            logger.error(f"Error generando datos demo: {str(e)}")
            return {
                'success': False,
                'records': [],
                'metadata': {},
                'clasificacion_cedulas': {},
                'resumen': {},
                'warnings': [],
                'errors': [f"Error generando datos demo: {str(e)}"]
            }
