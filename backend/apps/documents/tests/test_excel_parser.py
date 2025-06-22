"""
Tests para el parser de archivos Excel de información exógena.
"""
import pytest
import pandas as pd
import numpy as np
from decimal import Decimal
from io import BytesIO
import tempfile
import os

from apps.documents.parsers.excel_parser import ExogenaParser


class TestExogenaParser:
    """Tests para ExogenaParser."""
    
    @pytest.fixture
    def parser(self):
        """Fixture que retorna una instancia del parser."""
        return ExogenaParser()
    
    @pytest.fixture
    def sample_excel_data(self):
        """Fixture que crea un archivo Excel de prueba."""
        # Crear DataFrame de prueba
        data = {
            'NIT del Tercero': ['900123456', '800987654', '1234567890'],
            'Nombre del Tercero': ['EMPRESA ABC S.A.S', 'BANCO XYZ', 'PROFESIONAL INDEPENDIENTE'],
            'Concepto': ['5001', '5007', '5002'],
            'Valor del Pago o Abono en Cuenta': [10000000, 500000, 8000000],
            'Retención Practicada': [1500000, 75000, 800000]
        }
        df = pd.DataFrame(data)
        
        # Crear archivo Excel temporal
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            df.to_excel(tmp.name, index=False, sheet_name='Datos')
            return tmp.name
    
    @pytest.fixture
    def complex_excel_data(self):
        """Fixture que crea un archivo Excel más complejo con múltiples hojas."""
        # Hoja 1: Ingresos
        ingresos_data = {
            'NIT del Tercero': ['900123456-1', '800987654', '1.234.567.890'],
            'Nombre del Tercero': ['EMPRESA ABC S.A.S', 'BANCO XYZ', 'PROFESIONAL INDEPENDIENTE'],
            'Concepto': ['5001 - Salarios', '5007', 'Honorarios (5002)'],
            'Valor del Pago o Abono en Cuenta': ['$10.000.000', '500,000.00', '8000000'],
            'Retención Practicada': ['$1.500.000', '75,000', '800000.00']
        }
        
        # Hoja 2: Retenciones adicionales
        retenciones_data = {
            'Identificación': ['111222333', '444555666'],
            'Razón Social': ['CLIENTE 1', 'CLIENTE 2'],
            'Código Concepto': ['5003', '5004'],
            'Valor': ['2000000', '1500000'],
            'Retención en la Fuente': ['200000', '150000']
        }
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            with pd.ExcelWriter(tmp.name, engine='openpyxl') as writer:
                pd.DataFrame(ingresos_data).to_excel(writer, sheet_name='Ingresos', index=False)
                pd.DataFrame(retenciones_data).to_excel(writer, sheet_name='Retenciones', index=False)
            return tmp.name
    
    def test_parser_initialization(self, parser):
        """Test que el parser se inicializa correctamente."""
        assert parser.errors == []
        assert parser.warnings == []
        assert parser.stats['total_records'] == 0
        assert parser.stats['total_income'] == Decimal('0')
    
    def test_parse_simple_excel(self, parser, sample_excel_data):
        """Test parseo de un archivo Excel simple."""
        try:
            result = parser.parse_excel_file(sample_excel_data)
            
            assert result['success'] is True
            assert len(result['records']) == 3
            assert result['stats']['total_records'] == 3
            assert result['stats']['processed_records'] == 3
            assert result['stats']['total_income'] == Decimal('18500000')
            assert result['stats']['total_withholdings'] == Decimal('2375000')
            
            # Verificar primer registro
            first_record = result['records'][0]
            assert first_record['third_party_nit'] == '900123456'
            assert first_record['third_party_name'] == 'EMPRESA ABC S.A.S'
            assert first_record['concept_code'] == '5001'
            assert first_record['income_type'] == 'salary'
            assert first_record['tax_schedule'] == 'labor'
            
        finally:
            # Limpiar archivo temporal
            os.unlink(sample_excel_data)
    
    def test_parse_complex_excel(self, parser, complex_excel_data):
        """Test parseo de un archivo Excel complejo con formato colombiano."""
        try:
            result = parser.parse_excel_file(complex_excel_data)
            
            assert result['success'] is True
            assert len(result['records']) == 5  # 3 de la primera hoja + 2 de la segunda
            
            # Verificar que se parsearon correctamente los valores con formato
            ingresos = [r['gross_amount'] for r in result['records']]
            assert Decimal('10000000') in ingresos  # Valor con formato de pesos
            assert Decimal('500000') in ingresos    # Valor con coma decimal
            
        finally:
            # Limpiar archivo temporal
            os.unlink(complex_excel_data)
    
    def test_clean_nit(self, parser):
        """Test limpieza de NITs."""
        assert parser._clean_nit('900123456-1') == '900123456'
        assert parser._clean_nit('1.234.567.890') == '1234567890'
        assert parser._clean_nit(' 800987654 ') == '800987654'
        assert parser._clean_nit('CC 12345678') == '12345678'
        assert parser._clean_nit(None) == ''
        assert parser._clean_nit('') == ''
    
    def test_clean_amount(self, parser):
        """Test limpieza de montos."""
        assert parser._clean_amount('$1.000.000') == Decimal('1000000')
        assert parser._clean_amount('1,500,000.50') == Decimal('1500000.50')
        assert parser._clean_amount('2.500.000,75') == Decimal('2500000.75')
        assert parser._clean_amount('1000000') == Decimal('1000000')
        assert parser._clean_amount('') == Decimal('0')
        assert parser._clean_amount(None) == Decimal('0')
    
    def test_classify_income(self, parser):
        """Test clasificación de ingresos."""
        # Test por código de concepto
        result = parser._classify_income('5001', 'EMPRESA ABC')
        assert result['type'] == 'salary'
        assert result['schedule'] == 'labor'
        
        result = parser._classify_income('5007', 'BANCO XYZ')
        assert result['type'] == 'interests'
        assert result['schedule'] == 'capital'
        
        # Test por nombre del tercero
        result = parser._classify_income('9999', 'INMOBILIARIA ABC')
        assert result['type'] == 'rental'
        assert result['schedule'] == 'capital'
        
        result = parser._classify_income('9999', 'CONSULTORIA PROFESIONAL')
        assert result['type'] == 'honorarios'
        assert result['schedule'] == 'labor'
    
    def test_parse_corrupted_file(self, parser):
        """Test manejo de archivo corrupto."""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            # Escribir datos no válidos
            tmp.write(b'This is not a valid Excel file')
            tmp_name = tmp.name
        
        try:
            result = parser.parse_excel_file(tmp_name)
            
            assert result['success'] is False
            assert len(result['errors']) > 0
            assert 'Error general' in result['errors'][0]
            
        finally:
            os.unlink(tmp_name)
    
    def test_parse_empty_excel(self, parser):
        """Test parseo de archivo Excel vacío."""
        # Crear Excel vacío
        df_empty = pd.DataFrame()
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            df_empty.to_excel(tmp.name, index=False)
            tmp_name = tmp.name
        
        try:
            result = parser.parse_excel_file(tmp_name)
            
            assert result['success'] is True
            assert len(result['records']) == 0
            assert len(result['warnings']) > 0
            
        finally:
            os.unlink(tmp_name)
    
    def test_statistics_calculation(self, parser):
        """Test cálculo de estadísticas."""
        records = [
            {
                'gross_amount': Decimal('5000000'),
                'withholding_amount': Decimal('500000'),
                'income_type': 'salary',
                'tax_schedule': 'labor'
            },
            {
                'gross_amount': Decimal('3000000'),
                'withholding_amount': Decimal('300000'),
                'income_type': 'salary',
                'tax_schedule': 'labor'
            },
            {
                'gross_amount': Decimal('2000000'),
                'withholding_amount': Decimal('100000'),
                'income_type': 'interests',
                'tax_schedule': 'capital'
            }
        ]
        
        parser._calculate_statistics(records)
        
        assert parser.stats['total_records'] == 3
        assert parser.stats['total_income'] == Decimal('10000000')
        assert parser.stats['total_withholdings'] == Decimal('900000')
        
        # Verificar agrupación por tipo
        assert parser.stats['income_by_type']['salary']['count'] == 2
        assert parser.stats['income_by_type']['salary']['gross_amount'] == Decimal('8000000')
        
        # Verificar agrupación por cédula
        assert parser.stats['income_by_schedule']['labor']['count'] == 2
        assert parser.stats['income_by_schedule']['capital']['count'] == 1


@pytest.mark.integration
class TestExogenaParserIntegration:
    """Tests de integración para el parser."""
    
    def test_real_world_excel_format(self):
        """Test con formato de Excel del mundo real."""
        # Este test requeriría un archivo Excel real de prueba
        # Por ahora, es un placeholder para tests futuros
        pass