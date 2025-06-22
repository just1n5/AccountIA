"""
Parser simplificado para archivos de información exógena (MVP sin pandas).
"""
import csv
import json
import logging
from typing import Dict, List, Any, Optional
from decimal import Decimal
import re

logger = logging.getLogger(__name__)


class SimpleExogenaParser:
    """
    Parser básico para archivos CSV de información exógena (MVP).
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
    
    def parse_csv_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parsea un archivo CSV de información exógena.
        
        Args:
            file_path: Ruta al archivo CSV
            
        Returns:
            Dict con los datos procesados y estadísticas
        """
        try:
            logger.info(f"Iniciando parseo de archivo CSV: {file_path}")
            
            records = []
            
            with open(file_path, 'r', encoding='utf-8') as file:
                # Detectar el separador
                sample = file.read(1024)
                file.seek(0)
                
                separators = [',', ';', '\t']
                separator = ','
                for sep in separators:
                    if sample.count(sep) > sample.count(separator):
                        separator = sep
                
                csv_reader = csv.DictReader(file, delimiter=separator)
                
                for row_num, row in enumerate(csv_reader, 1):
                    try:
                        # Procesar la fila
                        record = self._process_row(row, row_num)
                        if record:
                            records.append(record)
                            self.stats['processed_records'] += 1
                        else:
                            self.stats['skipped_records'] += 1
                            
                    except Exception as e:
                        self.warnings.append(f"Error en fila {row_num}: {str(e)}")
                        self.stats['skipped_records'] += 1
            
            # Calcular estadísticas finales
            self._calculate_statistics(records)
            
            return {
                'success': True,
                'records': records,
                'stats': self.stats,
                'errors': self.errors,
                'warnings': self.warnings
            }
            
        except Exception as e:
            logger.error(f"Error al parsear archivo: {str(e)}", exc_info=True)
            self.errors.append(f"Error general: {str(e)}")
            return {
                'success': False,
                'records': [],
                'stats': self.stats,
                'errors': self.errors,
                'warnings': self.warnings
            }
    
    def _process_row(self, row: Dict[str, str], row_num: int) -> Optional[Dict[str, Any]]:
        """
        Procesa una fila del CSV.
        """
        # Mapeo flexible de columnas
        nit = self._find_column_value(row, ['nit', 'identificacion', 'cedula'])
        nombre = self._find_column_value(row, ['nombre', 'razon_social', 'tercero'])
        concepto = self._find_column_value(row, ['concepto', 'codigo_concepto'])
        valor = self._find_column_value(row, ['valor', 'valor_pago', 'monto', 'ingreso'])
        retencion = self._find_column_value(row, ['retencion', 'retencion_practicada', 'withholding'])
        
        # Validar datos esenciales
        if not all([nit, nombre, concepto, valor]):
            return None
        
        # Limpiar y convertir valores
        nit_clean = self._clean_nit(nit)
        nombre_clean = self._clean_text(nombre)
        concepto_clean = self._clean_concept(concepto)
        valor_clean = self._clean_amount(valor)
        retencion_clean = self._clean_amount(retencion) if retencion else Decimal('0')
        
        if valor_clean <= 0:
            return None
        
        return {
            'third_party_nit': nit_clean,
            'third_party_name': nombre_clean,
            'concept_code': concepto_clean,
            'concept_description': f'Concepto {concepto_clean}',
            'income_type': 'other',
            'tax_schedule': 'general',
            'gross_amount': valor_clean,
            'withholding_amount': retencion_clean,
            'source_row': row_num
        }
    
    def _find_column_value(self, row: Dict[str, str], possible_names: List[str]) -> Optional[str]:
        """
        Busca un valor en las columnas posibles (case insensitive).
        """
        for col_name, value in row.items():
            col_lower = col_name.lower().replace(' ', '_')
            for possible in possible_names:
                if possible.lower() in col_lower:
                    return value.strip() if value else None
        return None
    
    def _clean_nit(self, value: str) -> str:
        """Limpia un NIT."""
        if not value:
            return ''
        nit = re.sub(r'[^\d-]', '', value.strip())
        if '-' in nit:
            nit = nit.split('-')[0]
        return nit
    
    def _clean_text(self, value: str) -> str:
        """Limpia texto."""
        if not value:
            return ''
        return ' '.join(value.strip().split())
    
    def _clean_concept(self, value: str) -> str:
        """Extrae código del concepto."""
        if not value:
            return ''
        match = re.search(r'(\d{4})', value)
        return match.group(1) if match else value[:4]
    
    def _clean_amount(self, value: str) -> Decimal:
        """Convierte valor monetario a Decimal."""
        if not value:
            return Decimal('0')
        
        try:
            # Eliminar símbolos y espacios
            amount_str = value.replace('$', '').replace(' ', '').replace(',', '')
            return Decimal(amount_str)
        except:
            return Decimal('0')
    
    def _calculate_statistics(self, records: List[Dict[str, Any]]) -> None:
        """Calcula estadísticas."""
        self.stats['total_records'] = len(records)
        
        for record in records:
            self.stats['total_income'] += record['gross_amount']
            self.stats['total_withholdings'] += record['withholding_amount']


# Mantener compatibilidad con el código existente
class ExogenaParser:
    """
    Wrapper para mantener compatibilidad mientras no tengamos pandas.
    """
    
    def __init__(self):
        self.simple_parser = SimpleExogenaParser()
    
    def parse_excel_file(self, file_path: str) -> Dict[str, Any]:
        """
        Por ahora, solo soporta CSV. TODO: Agregar soporte Excel cuando tengamos pandas.
        """
        if file_path.endswith('.csv'):
            return self.simple_parser.parse_csv_file(file_path)
        else:
            return {
                'success': False,
                'records': [],
                'stats': {},
                'errors': ['Solo se soportan archivos CSV por ahora. Excel próximamente.'],
                'warnings': []
            }
