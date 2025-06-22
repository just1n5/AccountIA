"""
Parser básico sin pandas para MVP.
"""
from typing import Dict, List, Any
from decimal import Decimal
import logging

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
