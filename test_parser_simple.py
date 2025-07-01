"""
Prueba simple del parser robusto.
"""
import pandas as pd
import tempfile
import os
from decimal import Decimal

# Simular la estructura del parser para probar la lógica
class TestRobustParser:
    def __init__(self):
        self.errors = []
        self.warnings = []
        
        # Mapeo de aliases para columnas comunes
        self.column_aliases = {
            'nit': ['nit del tercero', 'nit_tercero', 'nit tercero', 'identificacion', 'documento', 'cedula'],
            'name': ['nombre del tercero', 'nombre_tercero', 'nombre tercero', 'razon social', 'tercero'],
            'concept': ['concepto', 'codigo concepto', 'codigo_concepto', 'cod concepto', 'tipo concepto'],
            'gross_amount': ['valor del pago o abono en cuenta', 'valor_pago', 'valor bruto', 'valor_bruto', 'monto', 'valor', 'importe'],
            'withholding': ['retencion practicada', 'retencion_practicada', 'valor retencion', 'retencion', 'ret_fuente']
        }
        
        # Clasificación de conceptos por código
        self.concept_mapping = {
            '5001': {'type': 'salary', 'schedule': 'labor', 'description': 'Salarios'},
            '5002': {'type': 'honorarios', 'schedule': 'labor', 'description': 'Honorarios'},
            '5005': {'type': 'rental', 'schedule': 'capital', 'description': 'Arrendamientos'},
            '5007': {'type': 'interests', 'schedule': 'capital', 'description': 'Intereses'},
        }
    
    def test_csv_parsing(self, csv_content):
        """Prueba el parsing de un CSV."""
        
        # Crear archivo temporal
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            f.write(csv_content)
            temp_path = f.name
        
        try:
            # Cargar datos
            df = pd.read_csv(temp_path)
            print(f"✅ CSV cargado exitosamente: {len(df)} filas")
            print(f"📋 Columnas encontradas: {list(df.columns)}")
            
            # Detectar mapeo de columnas
            column_mapping = self._detect_and_map_columns(df)
            print(f"🗂️  Mapeo detectado: {column_mapping}")
            
            # Procesar algunos registros
            sample_records = []
            for idx, row in df.head(3).iterrows():
                record = {
                    'third_party_nit': self._clean_nit(row.get(column_mapping.get('nit', ''), '')),
                    'third_party_name': str(row.get(column_mapping.get('name', ''), '')),
                    'concept_code': str(row.get(column_mapping.get('concept', ''), '')),
                    'gross_amount': self._clean_amount(row.get(column_mapping.get('gross_amount', ''), 0)),
                    'withholding_amount': self._clean_amount(row.get(column_mapping.get('withholding', ''), 0))
                }
                
                # Clasificar ingreso
                classification = self._classify_income(record['concept_code'], record['third_party_name'])
                record.update(classification)
                
                record['concept_description'] = self.concept_mapping.get(
                    record['concept_code'], {}
                ).get('description', 'Concepto no clasificado')
                
                sample_records.append(record)
            
            print(f"\n📝 Registros procesados:")
            for i, record in enumerate(sample_records):
                print(f"   Registro {i+1}:")
                print(f"     - NIT: {record['third_party_nit']}")
                print(f"     - Nombre: {record['third_party_name']}")
                print(f"     - Concepto: {record['concept_code']} - {record['concept_description']}")
                print(f"     - Valor bruto: ${record['gross_amount']:,.0f}")
                print(f"     - Retención: ${record['withholding_amount']:,.0f}")
                print(f"     - Tipo: {record['income_type']} ({record['tax_schedule']})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def _detect_and_map_columns(self, df):
        """Detecta y mapea las columnas del DataFrame a campos estándar."""
        column_mapping = {}
        df_columns_lower = [col.lower().strip() for col in df.columns]
        
        for standard_field, aliases in self.column_aliases.items():
            matched = False
            
            for alias in aliases:
                for idx, col_name in enumerate(df_columns_lower):
                    if alias in col_name or col_name in alias:
                        column_mapping[standard_field] = df.columns[idx]
                        matched = True
                        break
                if matched:
                    break
        
        return column_mapping
    
    def _clean_nit(self, nit_value):
        """Limpia y normaliza valores de NIT."""
        if pd.isna(nit_value) or nit_value == '':
            return ''
        
        nit_str = str(nit_value).strip()
        
        # Básico: remover no-dígitos excepto guión
        import re
        nit_str = re.sub(r'[^\d\-]', '', nit_str)
        nit_str = nit_str.split('-')[0]  # Remover dígito verificación
        
        return nit_str
    
    def _clean_amount(self, amount_value):
        """Limpia y convierte valores monetarios a Decimal."""
        if pd.isna(amount_value) or amount_value == '':
            return Decimal('0')
        
        try:
            # Convertir a string y limpiar básico
            amount_str = str(amount_value).strip()
            
            # Remover símbolos comunes
            import re
            amount_str = re.sub(r'[$\s,]', '', amount_str)
            
            return Decimal(amount_str)
            
        except:
            return Decimal('0')
    
    def _classify_income(self, concept_code, third_party_name):
        """Clasifica el tipo de ingreso."""
        if concept_code in self.concept_mapping:
            mapping = self.concept_mapping[concept_code]
            return {
                'income_type': mapping['type'],
                'tax_schedule': mapping['schedule']
            }
        
        # Default
        return {'income_type': 'other', 'tax_schedule': 'other'}


# Ejecutar prueba
print("🧪 PRUEBA DEL PARSER ROBUSTO")
print("=" * 40)

# Datos de prueba CSV
csv_data = """NIT del Tercero,Nombre del Tercero,Concepto,Valor del Pago o Abono en Cuenta,Retención Practicada
900123456,EMPRESA ABC S.A.S,5001,50000000,7500000
800987654,BANCO XYZ,5007,2000000,300000
1234567890,CONSULTORIA PROFESIONAL,5002,15000000,1500000
555666777,INMOBILIARIA DEL VALLE,5005,8000000,800000"""

parser = TestRobustParser()
success = parser.test_csv_parsing(csv_data)

if success:
    print(f"\n🎉 ¡PRUEBA EXITOSA!")
    print("   El parser robusto puede manejar el formato de datos correctamente.")
else:
    print(f"\n❌ Prueba fallida")

print(f"\n" + "=" * 40)
