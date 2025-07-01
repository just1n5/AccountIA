"""
Script de validación para probar el parser robusto con archivos reales.
"""
import sys
import os
import django

# Agregar el directorio backend al path
sys.path.append('C:/Users/justi/Desktop/Proyecto Accountia/backend')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.documents.parsers.excel_parser import ExogenaParser
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_parser_with_real_files():
    """Prueba el parser con archivos reales de prueba."""
    
    # Archivos de prueba
    test_files = [
        'C:/Users/justi/Desktop/Proyecto Accountia/test_exogena.xlsx',
        'C:/Users/justi/Desktop/Proyecto Accountia/test_exogena_2024.csv'
    ]
    
    parser = ExogenaParser()
    
    print("🧪 VALIDACIÓN DEL PARSER ROBUSTO")
    print("=" * 50)
    
    for file_path in test_files:
        if not os.path.exists(file_path):
            print(f"⚠️  Archivo no encontrado: {file_path}")
            continue
            
        print(f"\n📁 Procesando archivo: {os.path.basename(file_path)}")
        print("-" * 40)
        
        try:
            # Probar el parser robusto
            result = parser.parse_excel_file(file_path)
            
            if result['success']:
                print("✅ Procesamiento exitoso!")
                
                # Mostrar estadísticas
                stats = result['stats']
                print(f"📊 Estadísticas:")
                print(f"   - Total registros: {stats['total_records']}")
                print(f"   - Procesados: {stats['processed_records']}")
                print(f"   - Omitidos: {stats['skipped_records']}")
                print(f"   - Total ingresos: ${stats['total_income']:,.0f}")
                print(f"   - Total retenciones: ${stats['total_withholdings']:,.0f}")
                print(f"   - Terceros únicos: {stats['third_parties_count']}")
                print(f"   - Conceptos únicos: {stats['concepts_count']}")
                
                # Mostrar información del archivo
                if 'file_info' in result:
                    file_info = result['file_info']
                    print(f"📄 Información del archivo:")
                    print(f"   - Tipo: {file_info.get('file_type', 'N/A')}")
                    print(f"   - Filas totales: {file_info.get('total_rows', 'N/A')}")
                    print(f"   - Columnas: {file_info.get('total_cols', 'N/A')}")
                    print(f"   - Fila de encabezados: {file_info.get('header_row', 'N/A')}")
                
                # Mostrar mapeo de columnas
                if 'column_mapping' in result:
                    print(f"🗂️  Mapeo de columnas:")
                    for key, value in result['column_mapping'].items():
                        print(f"   - {key}: '{value}'")
                
                # Mostrar algunas muestras de registros
                records = result['records']
                if records:
                    print(f"📝 Muestra de registros (primeros 3):")
                    for i, record in enumerate(records[:3]):
                        print(f"   Registro {i+1}:")
                        print(f"     - NIT: {record['third_party_nit']}")
                        print(f"     - Nombre: {record['third_party_name']}")
                        print(f"     - Concepto: {record['concept_code']} - {record['concept_description']}")
                        print(f"     - Valor bruto: ${record['gross_amount']:,.0f}")
                        print(f"     - Retención: ${record['withholding_amount']:,.0f}")
                        print(f"     - Tipo: {record['income_type']} ({record['tax_schedule']})")
                
                # Mostrar advertencias si las hay
                if result['warnings']:
                    print(f"⚠️  Advertencias:")
                    for warning in result['warnings']:
                        print(f"   - {warning}")
                
                # Mostrar validación
                if 'validation' in result:
                    validation = result['validation']
                    if validation['warnings']:
                        print(f"🔍 Validación - Advertencias:")
                        for warning in validation['warnings']:
                            print(f"   - {warning}")
            
            else:
                print("❌ Error en el procesamiento:")
                for error in result['errors']:
                    print(f"   - {error}")
                    
        except Exception as e:
            print(f"💥 Error inesperado: {str(e)}")
            logger.exception("Error durante la prueba")


def test_demo_data():
    """Prueba los datos demo para asegurar compatibilidad."""
    print(f"\n🎯 PRUEBA DE DATOS DEMO")
    print("=" * 30)
    
    parser = ExogenaParser()
    
    try:
        demo_result = parser.parse_demo_data()
        
        if demo_result['success']:
            print("✅ Datos demo generados exitosamente!")
            
            print(f"📊 Metadatos:")
            metadata = demo_result['metadata']
            print(f"   - Total registros: {metadata['total_registros']}")
            print(f"   - Total ingresos: ${metadata['total_ingresos']:,.0f}")
            print(f"   - Total retenciones: ${metadata['total_retenciones']:,.0f}")
            print(f"   - Período fiscal: {metadata['periodo_fiscal']}")
            
            print(f"🏷️  Clasificación por cédulas:")
            for cedula, data in demo_result['clasificacion_cedulas'].items():
                print(f"   - {cedula}: {data['registros']} registros, ${data['total_ingresos']:,.0f}")
        else:
            print("❌ Error generando datos demo:")
            for error in demo_result['errors']:
                print(f"   - {error}")
                
    except Exception as e:
        print(f"💥 Error inesperado: {str(e)}")
        logger.exception("Error durante la prueba de datos demo")


def verify_compatibility():
    """Verifica que los campos retornados sean compatibles con IncomeRecord."""
    print(f"\n🔧 VERIFICACIÓN DE COMPATIBILIDAD")
    print("=" * 40)
    
    parser = ExogenaParser()
    
    # Campos requeridos por IncomeRecord
    required_fields = [
        'third_party_nit',
        'third_party_name', 
        'concept_code',
        'concept_description',
        'income_type',
        'gross_amount',
        'withholding_amount',
        'tax_schedule'
    ]
    
    try:
        # Usar datos demo para verificar
        demo_result = parser.parse_demo_data()
        
        if demo_result['success'] and demo_result['records']:
            sample_record = demo_result['records'][0]
            
            print("✅ Verificando campos en registro de muestra:")
            missing_fields = []
            
            for field in required_fields:
                if field in sample_record:
                    print(f"   ✅ {field}: {sample_record[field]}")
                else:
                    missing_fields.append(field)
                    print(f"   ❌ {field}: FALTANTE")
            
            if not missing_fields:
                print(f"\n🎉 ¡COMPATIBILIDAD COMPLETA!")
                print("   Todos los campos requeridos están presentes.")
            else:
                print(f"\n⚠️  Campos faltantes: {missing_fields}")
        
        else:
            print("❌ No se pudieron obtener registros de muestra")
            
    except Exception as e:
        print(f"💥 Error durante verificación: {str(e)}")
        logger.exception("Error durante verificación de compatibilidad")


if __name__ == "__main__":
    print("🚀 INICIANDO VALIDACIÓN COMPLETA DEL PARSER ROBUSTO")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    test_demo_data()
    test_parser_with_real_files()
    verify_compatibility()
    
    print(f"\n✅ VALIDACIÓN COMPLETADA")
    print("=" * 30)
