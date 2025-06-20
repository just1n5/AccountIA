"""
Parser robusto para archivos Excel de información exógena de la DIAN
"""

import pandas as pd
import numpy as np
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal, InvalidOperation
from datetime import datetime
import openpyxl

logger = logging.getLogger(__name__)


class ExogenaParsingError(Exception):
    """Excepción personalizada para errores de parsing de exógena"""
    pass


class ExogenaParser:
    """
    Parser especializado para archivos de información exógena de la DIAN
    
    Maneja:
    - Detección automática de estructura
    - Limpieza y normalización de datos
    - Clasificación de conceptos fiscales
    - Manejo robusto de errores
    """
    
    # Mapeo de conceptos de exógena a tipos de ingresos
    CONCEPT_MAPPING = {
        # Rentas de trabajo (Cédula 1)
        'salarios': ['5001', '5002', '5003', '5004', '5005'],
        'cesantias': ['5006', '5007'],
        'primas': ['5008', '5009'],
        'vacaciones': ['5010'],
        'bonificaciones': ['5011', '5012'],
        
        # Rentas de capital (Cédula 2)
        'dividendos': ['4001', '4002', '4003'],
        'intereses': ['4004', '4005', '4006'],
        'rendimientos_financieros': ['4007', '4008'],
        'arrendamientos': ['4009', '4010'],
        
        # Rentas no laborales (Cédula 3)
        'honorarios': ['6001', '6002', '6003'],
        'servicios': ['6004', '6005'],
        'comisiones': ['6006', '6007'],
        'consultoria': ['6008', '6009'],
        
        # Otros conceptos
        'retenciones': ['7001', '7002', '7003', '7004'],
        'aportes_salud': ['8001', '8002'],
        'aportes_pension': ['8003', '8004']
    }
    
    # Columnas esperadas en el archivo de exógena
    EXPECTED_COLUMNS = [
        'tercero_informante',
        'nit_tercero',
        'dv_tercero', 
        'primer_apellido',
        'segundo_apellido',
        'primer_nombre',
        'otros_nombres',
        'concepto',
        'valor_pago',
        'ano_gravable'
    ]
    
    def __init__(self):
        """Inicializar el parser"""
        self.parsed_data = None
        self.raw_data = None
        self.errors = []
        self.warnings = []
    
    def parse_excel_file(self, file_content: bytes, filename: str = "archivo.xlsx") -> Dict[str, Any]:
        """
        Parsear archivo Excel de información exógena
        
        Args:
            file_content: Contenido del archivo como bytes
            filename: Nombre del archivo (para logging)
        
        Returns:
            Diccionario con datos parseados y metadatos
        """
        logger.info(f"🔍 Iniciando parsing de {filename}")
        
        try:
            # Resetear estado
            self._reset_state()
            
            # 1. Cargar archivo Excel
            df = self._load_excel_file(file_content, filename)
            
            # 2. Detectar y validar estructura
            df = self._detect_and_validate_structure(df)
            
            # 3. Limpiar y normalizar datos
            df = self._clean_and_normalize_data(df)
            
            # 4. Validar integridad de los datos
            self._validate_data_integrity(df)
            
            # 5. Clasificar conceptos
            classification = self._classify_income_concepts(df)
            
            # 6. Calcular totales y estadísticas
            summary = self._calculate_summary_statistics(df, classification)
            
            # 7. Generar resultado
            result = {
                'success': True,
                'filename': filename,
                'parsed_at': datetime.now().isoformat(),
                'total_records': len(df),
                'summary': summary,
                'classification': classification,
                'raw_data': df.to_dict('records'),
                'metadata': {
                    'columns_found': list(df.columns),
                    'data_types': df.dtypes.to_dict(),
                    'errors': self.errors,
                    'warnings': self.warnings
                }
            }
            
            logger.info(f"✅ Parsing completado: {len(df)} registros procesados")
            return result
            
        except Exception as e:
            error_msg = f"❌ Error parseando {filename}: {str(e)}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            
            return {
                'success': False,
                'filename': filename,
                'error': str(e),
                'errors': self.errors,
                'warnings': self.warnings
            }
    
    def _reset_state(self):
        """Resetear el estado del parser"""
        self.parsed_data = None
        self.raw_data = None
        self.errors = []
        self.warnings = []
    
    def _load_excel_file(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """Cargar archivo Excel de forma robusta"""
        try:
            # Intentar con openpyxl primero (formato .xlsx)
            df = pd.read_excel(
                file_content,
                engine='openpyxl',
                sheet_name=0,  # Primera hoja
                header=0,  # Primera fila como headers
                dtype=str  # Leer todo como string inicialmente
            )
            logger.info(f"✅ Archivo cargado con openpyxl: {df.shape}")
            
        except Exception as e1:
            try:
                # Intentar con xlrd para archivos .xls más antiguos
                df = pd.read_excel(
                    file_content,
                    engine='xlrd',
                    sheet_name=0,
                    header=0,
                    dtype=str
                )
                logger.info(f"✅ Archivo cargado con xlrd: {df.shape}")
                
            except Exception as e2:
                error_msg = f"No se pudo leer el archivo Excel. Openpyxl: {str(e1)}, Xlrd: {str(e2)}"
                raise ExogenaParsingError(error_msg)
        
        if df.empty:
            raise ExogenaParsingError("El archivo Excel está vacío")
        
        return df
    
    def _detect_and_validate_structure(self, df: pd.DataFrame) -> pd.DataFrame:
        """Detectar automáticamente la estructura del archivo"""
        logger.info("🔍 Detectando estructura del archivo...")
        
        # Limpiar nombres de columnas
        df.columns = df.columns.astype(str).str.strip().str.lower()
        df.columns = df.columns.str.replace(' ', '_').str.replace('.', '').str.replace('-', '_')
        
        # Buscar columnas clave por patrones
        column_mapping = {}
        
        for col in df.columns:
            col_lower = str(col).lower()
            
            # Tercero informante
            if any(term in col_lower for term in ['tercero', 'informante', 'empresa', 'empleador']):
                column_mapping['tercero_informante'] = col
            
            # NIT
            elif any(term in col_lower for term in ['nit', 'identificacion', 'cedula']):
                column_mapping['nit_tercero'] = col
            
            # Concepto  
            elif any(term in col_lower for term in ['concepto', 'codigo', 'tipo']):
                column_mapping['concepto'] = col
            
            # Valor
            elif any(term in col_lower for term in ['valor', 'pago', 'abono', 'monto', 'importe']):
                column_mapping['valor_pago'] = col
            
            # Nombres
            elif any(term in col_lower for term in ['nombre', 'apellido']):
                if 'primer' in col_lower and 'nombre' in col_lower:
                    column_mapping['primer_nombre'] = col
                elif 'primer' in col_lower and 'apellido' in col_lower:
                    column_mapping['primer_apellido'] = col
                elif 'segundo' in col_lower and 'apellido' in col_lower:
                    column_mapping['segundo_apellido'] = col
        
        # Verificar que tenemos las columnas mínimas necesarias
        required_cols = ['tercero_informante', 'concepto', 'valor_pago']
        missing_cols = [col for col in required_cols if col not in column_mapping]
        
        if missing_cols:
            self.warnings.append(f"Columnas faltantes: {missing_cols}")
            # Intentar detección alternativa por posición
            if len(df.columns) >= 3:
                logger.warning("⚠️ Intentando detección por posición...")
                column_mapping.update({
                    'tercero_informante': df.columns[0],
                    'concepto': df.columns[-2],  # Penúltima columna
                    'valor_pago': df.columns[-1]  # Última columna
                })
        
        # Renombrar columnas
        df = df.rename(columns=column_mapping)
        
        logger.info(f"✅ Columnas detectadas: {list(column_mapping.keys())}")
        return df
    
    def _clean_and_normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpiar y normalizar los datos"""
        logger.info("🧹 Limpiando y normalizando datos...")
        
        # Eliminar filas completamente vacías
        df = df.dropna(how='all')
        
        # Limpiar espacios en blanco
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str).str.strip()
        
        # Normalizar valores monetarios
        if 'valor_pago' in df.columns:
            df['valor_pago'] = self._normalize_monetary_values(df['valor_pago'])
        
        # Normalizar conceptos
        if 'concepto' in df.columns:
            df['concepto'] = self._normalize_concepts(df['concepto'])
        
        # Normalizar NITs
        if 'nit_tercero' in df.columns:
            df['nit_tercero'] = self._normalize_nits(df['nit_tercero'])
        
        # Eliminar filas con datos críticos faltantes
        critical_cols = ['tercero_informante', 'concepto', 'valor_pago']
        before_count = len(df)
        
        for col in critical_cols:
            if col in df.columns:
                df = df[df[col].notna()]
                df = df[df[col] != '']
                df = df[df[col] != 'nan']
        
        after_count = len(df)
        if before_count != after_count:
            removed = before_count - after_count
            self.warnings.append(f"Se eliminaron {removed} filas con datos críticos faltantes")
            logger.warning(f"⚠️ Eliminadas {removed} filas con datos incompletos")
        
        return df
    
    def _normalize_monetary_values(self, series: pd.Series) -> pd.Series:
        """Normalizar valores monetarios"""
        def clean_monetary(value):
            if pd.isna(value) or value == '':
                return 0.0
            
            # Convertir a string y limpiar
            value_str = str(value).strip()
            
            # Remover símbolos de moneda y separadores
            value_str = re.sub(r'[$,.\s]', '', value_str)
            
            # Remover caracteres no numéricos excepto punto y coma
            value_str = re.sub(r'[^\d,.-]', '', value_str)
            
            # Manejar formato colombiano (coma como separador decimal)
            if ',' in value_str and '.' in value_str:
                # Formato: 1.234.567,89
                value_str = value_str.replace('.', '').replace(',', '.')
            elif ',' in value_str:
                # Formato: 1234567,89
                value_str = value_str.replace(',', '.')
            
            try:
                return float(value_str)
            except (ValueError, TypeError):
                return 0.0
        
        return series.apply(clean_monetary)
    
    def _normalize_concepts(self, series: pd.Series) -> pd.Series:
        """Normalizar códigos de concepto"""
        def clean_concept(value):
            if pd.isna(value) or value == '':
                return ''
            
            # Convertir a string y limpiar
            value_str = str(value).strip()
            
            # Extraer solo números (códigos de concepto son numéricos)
            concept_code = re.sub(r'[^\d]', '', value_str)
            
            return concept_code if concept_code else value_str
        
        return series.apply(clean_concept)
    
    def _normalize_nits(self, series: pd.Series) -> pd.Series:
        """Normalizar números de NIT"""
        def clean_nit(value):
            if pd.isna(value) or value == '':
                return ''
            
            # Convertir a string y extraer solo números y guiones
            nit_str = str(value).strip()
            nit_clean = re.sub(r'[^\d-]', '', nit_str)
            
            return nit_clean
        
        return series.apply(clean_nit)
    
    def _validate_data_integrity(self, df: pd.DataFrame):
        """Validar la integridad de los datos"""
        logger.info("✅ Validando integridad de datos...")
        
        # Verificar valores monetarios negativos inusuales
        if 'valor_pago' in df.columns:
            negative_values = df['valor_pago'] < 0
            if negative_values.any():
                count = negative_values.sum()
                self.warnings.append(f"Se encontraron {count} valores negativos")
        
        # Verificar conceptos válidos
        if 'concepto' in df.columns:
            empty_concepts = df['concepto'] == ''
            if empty_concepts.any():
                count = empty_concepts.sum()
                self.warnings.append(f"Se encontraron {count} conceptos vacíos")
        
        # Verificar duplicados
        if 'tercero_informante' in df.columns and 'concepto' in df.columns:
            duplicates = df.duplicated(['tercero_informante', 'concepto'])
            if duplicates.any():
                count = duplicates.sum()
                self.warnings.append(f"Se encontraron {count} registros duplicados")
    
    def _classify_income_concepts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Clasificar conceptos de ingresos según la normativa fiscal"""
        logger.info("📊 Clasificando conceptos de ingresos...")
        
        if 'concepto' not in df.columns or 'valor_pago' not in df.columns:
            return {'error': 'Columnas requeridas no encontradas'}
        
        classification = {
            'rentas_trabajo': [],
            'rentas_capital': [],
            'rentas_no_laborales': [],
            'retenciones': [],
            'otros': []
        }
        
        concept_totals = {}
        
        # Agrupar por concepto y sumar valores
        for _, row in df.iterrows():
            concept = str(row['concepto']).strip()
            value = float(row.get('valor_pago', 0))
            
            if concept not in concept_totals:
                concept_totals[concept] = {
                    'total': 0,
                    'count': 0,
                    'category': self._categorize_concept(concept)
                }
            
            concept_totals[concept]['total'] += value
            concept_totals[concept]['count'] += 1
        
        # Organizar por categorías
        for concept, data in concept_totals.items():
            category = data['category']
            
            concept_info = {
                'concepto': concept,
                'total': data['total'],
                'registros': data['count']
            }
            
            classification[category].append(concept_info)
        
        return classification
    
    def _categorize_concept(self, concept_code: str) -> str:
        """Categorizar un código de concepto específico"""
        # Buscar en el mapeo de conceptos
        for category, codes in self.CONCEPT_MAPPING.items():
            if concept_code in codes:
                if category in ['salarios', 'cesantias', 'primas', 'vacaciones', 'bonificaciones']:
                    return 'rentas_trabajo'
                elif category in ['dividendos', 'intereses', 'rendimientos_financieros', 'arrendamientos']:
                    return 'rentas_capital'
                elif category in ['honorarios', 'servicios', 'comisiones', 'consultoria']:
                    return 'rentas_no_laborales'
                elif category == 'retenciones':
                    return 'retenciones'
        
        return 'otros'
    
    def _calculate_summary_statistics(self, df: pd.DataFrame, classification: Dict) -> Dict[str, Any]:
        """Calcular estadísticas resumen"""
        logger.info("📈 Calculando estadísticas resumen...")
        
        summary = {
            'total_registros': len(df),
            'total_ingresos': 0,
            'total_retenciones': 0,
            'impuesto_estimado': 0
        }
        
        if 'valor_pago' in df.columns:
            # Calcular totales por categoría
            for category, items in classification.items():
                category_total = sum(item['total'] for item in items)
                summary[f'total_{category}'] = category_total
                
                if category != 'retenciones':
                    summary['total_ingresos'] += category_total
                else:
                    summary['total_retenciones'] = category_total
        
        # Estimación preliminar del impuesto (muy básica)
        if summary['total_ingresos'] > 0:
            # Estimación muy básica - esto debería ser más sofisticado
            base_gravable = max(0, summary['total_ingresos'] - 47000000)  # UVT aprox 2024
            summary['impuesto_estimado'] = base_gravable * 0.19  # Tarifa básica
        
        return summary


# Función de conveniencia
def parse_exogena_file(file_content: bytes, filename: str = "archivo.xlsx") -> Dict[str, Any]:
    """
    Función de conveniencia para parsear un archivo de exógena
    
    Args:
        file_content: Contenido del archivo como bytes
        filename: Nombre del archivo
    
    Returns:
        Diccionario con resultado del parsing
    """
    parser = ExogenaParser()
    return parser.parse_excel_file(file_content, filename)
