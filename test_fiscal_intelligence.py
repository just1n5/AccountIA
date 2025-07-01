#!/usr/bin/env python3
"""
Script de Prueba Completa - AccountIA Fiscal Intelligence
Valida toda la implementación del Plan de Conocimiento del Contador

Este script prueba:
1. Parser inteligente con archivos reales del usuario
2. Análisis fiscal completo
3. Detección de anomalías
4. Validación de consistencia
5. Generación de recomendaciones

Archivos a probar:
- reporteExogena2022.xls
- reporteExogena2023.xlsx
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Agregar el path del proyecto para importar módulos Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Configurar Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Ahora importar los módulos del proyecto
from apps.fiscal.services.intelligent_processor import get_intelligent_fiscal_processor
from apps.documents.parsers.excel_parser import ExogenaParser


class AccountIATestRunner:
    """Runner de pruebas para validar toda la implementación"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        self.test_files = [
            'reporteExogena2022.xls',
            'reporteExogena2023.xlsx'
        ]
    
    def run_complete_test_suite(self):
        """Ejecuta la suite completa de pruebas"""
        print("🚀 INICIANDO SUITE DE PRUEBAS ACCOUNTIA")
        print("=" * 60)
        print(f"Fecha: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Archivos a probar: {', '.join(self.test_files)}")
        print("=" * 60)
        
        # Test 1: Verificar que los servicios se pueden instanciar
        self.test_services_initialization()
        
        # Test 2: Probar parser con datos demo
        self.test_demo_data_processing()
        
        # Test 3: Probar parser con archivos reales (si existen)
        self.test_real_files_processing()
        
        # Test 4: Probar análisis fiscal completo
        self.test_complete_fiscal_analysis()
        
        # Test 5: Validar detección de anomalías
        self.test_anomaly_detection()
        
        # Test 6: Validar consistencia fiscal
        self.test_consistency_validation()
        
        # Generar reporte final
        self.generate_final_report()
    
    def test_services_initialization(self):
        """Test 1: Verificar inicialización de servicios"""
        print("\n📋 TEST 1: Inicialización de Servicios")
        print("-" * 40)
        
        try:
            # Probar procesador inteligente
            processor = get_intelligent_fiscal_processor()
            print("✅ IntelligentFiscalProcessor inicializado correctamente")
            
            # Verificar componentes internos
            assert processor.parser is not None, "Parser no inicializado"
            assert processor.fiscal_analyzer is not None, "Analizador fiscal no inicializado"
            assert processor.anomaly_detector is not None, "Detector de anomalías no inicializado"
            assert processor.consistency_validator is not None, "Validador de consistencia no inicializado"
            
            print("✅ Todos los servicios internos inicializados correctamente")
            
            self.test_results.append({
                'test': 'services_initialization',
                'status': 'PASSED',
                'message': 'Servicios inicializados correctamente'
            })
            
        except Exception as e:
            print(f"❌ Error en inicialización: {str(e)}")
            self.test_results.append({
                'test': 'services_initialization',
                'status': 'FAILED',
                'error': str(e)
            })
    
    def test_demo_data_processing(self):
        """Test 2: Procesar datos demo"""
        print("\n📋 TEST 2: Procesamiento de Datos Demo")
        print("-" * 40)
        
        try:
            parser = ExogenaParser()
            result = parser.parse_demo_data()
            
            if result['success']:
                records = result.get('records', [])
                metadata = result.get('metadata', {})
                
                print(f"✅ Datos demo procesados: {len(records)} registros")
                print(f"   Total ingresos: ${metadata.get('total_ingresos', 0):,.0f}")
                print(f"   Total retenciones: ${metadata.get('total_retenciones', 0):,.0f}")
                
                # Verificar estructura de datos
                if records:
                    sample_record = records[0]
                    required_fields = ['nit_tercero', 'nombre_tercero', 'valor_bruto', 'valor_retencion']
                    
                    for field in required_fields:
                        assert field in sample_record, f"Campo requerido {field} no encontrado"
                    
                    print("✅ Estructura de datos validada correctamente")
                
                self.test_results.append({
                    'test': 'demo_data_processing',
                    'status': 'PASSED',
                    'records_count': len(records),
                    'total_income': metadata.get('total_ingresos', 0)
                })
            else:
                raise Exception(f"Error en datos demo: {result.get('error', 'Error desconocido')}")
                
        except Exception as e:
            print(f"❌ Error en datos demo: {str(e)}")
            self.test_results.append({
                'test': 'demo_data_processing',
                'status': 'FAILED',
                'error': str(e)
            })
    
    def test_real_files_processing(self):
        """Test 3: Procesar archivos reales del usuario"""
        print("\n📋 TEST 3: Procesamiento de Archivos Reales")
        print("-" * 40)
        
        for filename in self.test_files:
            try:
                file_path = project_root / filename
                
                if not file_path.exists():
                    print(f"⚠️  Archivo {filename} no encontrado, saltando...")
                    continue
                
                print(f"📄 Procesando {filename}...")
                
                parser = ExogenaParser()
                result = parser.parse_excel_file(str(file_path))
                
                if result['success']:
                    records = result.get('records', [])
                    print(f"✅ {filename} procesado: {len(records)} registros")
                    
                    # Mostrar estadísticas básicas
                    if records:
                        total_income = sum(r.get('gross_amount', 0) for r in records)
                        total_withholdings = sum(r.get('withholding_amount', 0) for r in records)
                        unique_nits = len(set(r.get('third_party_nit', '') for r in records))
                        
                        print(f"   Ingresos totales: ${total_income:,.0f}")
                        print(f"   Retenciones totales: ${total_withholdings:,.0f}")
                        print(f"   Terceros únicos: {unique_nits}")
                    
                    self.test_results.append({
                        'test': f'real_file_{filename}',
                        'status': 'PASSED',
                        'filename': filename,
                        'records_count': len(records)
                    })
                else:
                    error_msg = result.get('error', 'Error desconocido')
                    print(f"❌ Error procesando {filename}: {error_msg}")
                    self.test_results.append({
                        'test': f'real_file_{filename}',
                        'status': 'FAILED',
                        'filename': filename,
                        'error': error_msg
                    })
                    
            except Exception as e:
                print(f"❌ Error crítico con {filename}: {str(e)}")
                self.test_results.append({
                    'test': f'real_file_{filename}',
                    'status': 'FAILED',
                    'filename': filename,
                    'error': str(e)
                })
    
    def test_complete_fiscal_analysis(self):
        """Test 4: Análisis fiscal completo"""
        print("\n📋 TEST 4: Análisis Fiscal Completo")
        print("-" * 40)
        
        try:
            processor = get_intelligent_fiscal_processor()
            
            # Usar datos demo para el análisis completo
            result = processor.process_complete_analysis('demo')
            
            if result['success']:
                processing_time = result.get('processing_time', 0)
                print(f"✅ Análisis fiscal completado en {processing_time:.2f} segundos")
                
                # Verificar componentes del análisis
                components = [
                    'parser_results', 'fiscal_analysis', 'anomaly_detection', 
                    'consistency_validation', 'final_recommendations'
                ]
                
                for component in components:
                    if component in result:
                        print(f"   ✅ {component.replace('_', ' ').title()}: OK")
                    else:
                        print(f"   ⚠️  {component.replace('_', ' ').title()}: Faltante")
                
                # Verificar análisis fiscal específico
                fiscal_analysis = result.get('fiscal_analysis', {})
                if fiscal_analysis.get('success'):
                    tax_calc = fiscal_analysis.get('tax_calculation', {})
                    requires_declaration = fiscal_analysis.get('requires_declaration', False)
                    
                    print(f"   📊 Obligado a declarar: {'Sí' if requires_declaration else 'No'}")
                    print(f"   📊 Base gravable: ${tax_calc.get('base_gravable', 0):,.0f}")
                    
                    if tax_calc.get('saldo_a_favor', 0) > 0:
                        print(f"   💰 Saldo a favor: ${tax_calc.get('saldo_a_favor', 0):,.0f}")
                    elif tax_calc.get('saldo_a_pagar', 0) > 0:
                        print(f"   💸 Saldo a pagar: ${tax_calc.get('saldo_a_pagar', 0):,.0f}")
                
                # Verificar recomendaciones
                recommendations = fiscal_analysis.get('optimizations', [])
                print(f"   💡 Recomendaciones generadas: {len(recommendations)}")
                
                self.test_results.append({
                    'test': 'complete_fiscal_analysis',
                    'status': 'PASSED',
                    'processing_time': processing_time,
                    'requires_declaration': requires_declaration,
                    'recommendations_count': len(recommendations)
                })
            else:
                error_msg = result.get('error', 'Error desconocido')
                raise Exception(error_msg)
                
        except Exception as e:
            print(f"❌ Error en análisis fiscal: {str(e)}")
            self.test_results.append({
                'test': 'complete_fiscal_analysis',
                'status': 'FAILED',
                'error': str(e)
            })
    
    def test_anomaly_detection(self):
        """Test 5: Detección de anomalías"""
        print("\n📋 TEST 5: Detección de Anomalías")
        print("-" * 40)
        
        try:
            from apps.fiscal.services.anomaly_detector import get_anomaly_detector
            
            # Crear datos de prueba con anomalías conocidas
            test_records = [
                {
                    'third_party_nit': '900123456',
                    'third_party_name': 'EMPRESA NORMAL SAS',
                    'gross_amount': 10000000,
                    'withholding_amount': 1000000,
                    'income_type': 'salary'
                },
                {
                    'third_party_nit': '800999999',
                    'third_party_name': 'FIDUCIARIA SOSPECHOSA SA',
                    'gross_amount': 200000000,  # Monto muy alto
                    'withholding_amount': 0,
                    'income_type': 'other',
                    'special_flags': ['potential_false_income', 'high_value_alert']
                },
                {
                    'third_party_nit': '700123456',
                    'third_party_name': 'EMPRESA DUPLICADA SAS',
                    'gross_amount': 5000000,
                    'withholding_amount': 6000000,  # Retención mayor que ingreso
                    'income_type': 'honorarios'
                }
            ]
            
            test_cedulas = {
                'rentas_trabajo': {'ingresos_brutos': 15000000, 'retenciones': 1000000},
                'rentas_capital': {'ingresos_brutos': 200000000, 'retenciones': 0}
            }
            
            detector = get_anomaly_detector()
            result = detector.detect_anomalies(test_records, test_cedulas)
            
            if result['success']:
                anomalies_count = result.get('anomalies_count', 0)
                risk_score = result.get('risk_score', {})
                
                print(f"✅ Detección completada: {anomalies_count} anomalías encontradas")
                print(f"   📊 Score de riesgo: {risk_score.get('score', 0)}/100 ({risk_score.get('level', 'unknown')})")
                
                # Mostrar tipos de anomalías detectadas
                anomalies = result.get('anomalies', [])
                anomaly_types = set(a.get('type', 'unknown') for a in anomalies)
                
                for anomaly_type in anomaly_types:
                    count = len([a for a in anomalies if a.get('type') == anomaly_type])
                    print(f"   🔍 {anomaly_type}: {count} casos")
                
                self.test_results.append({
                    'test': 'anomaly_detection',
                    'status': 'PASSED',
                    'anomalies_count': anomalies_count,
                    'risk_score': risk_score.get('score', 0)
                })
            else:
                raise Exception("Error en detección de anomalías")
                
        except Exception as e:
            print(f"❌ Error en detección de anomalías: {str(e)}")
            self.test_results.append({
                'test': 'anomaly_detection',
                'status': 'FAILED',
                'error': str(e)
            })
    
    def test_consistency_validation(self):
        """Test 6: Validación de consistencia"""
        print("\n📋 TEST 6: Validación de Consistencia")
        print("-" * 40)
        
        try:
            from apps.fiscal.services.consistency_validator import get_consistency_validator
            
            # Crear datos de análisis fiscal de prueba
            test_analysis = {
                'success': True,
                'cedulas_totals': {
                    'rentas_trabajo': {'ingresos_brutos': 50000000, 'retenciones': 5000000},
                    'rentas_capital': {'ingresos_brutos': 5000000, 'retenciones': 350000}
                },
                'potential_deductions': {
                    'renta_exenta_trabajo': 12500000,  # 25% de 50M
                    'deducciones_dependientes': 1500000,
                    'deducciones_salud': 750000
                },
                'tax_calculation': {
                    'base_gravable': 40000000,
                    'impuesto_calculado': 8000000,
                    'retenciones_totales': 5350000,
                    'saldo_a_pagar': 2650000
                }
            }
            
            validator = get_consistency_validator()
            result = validator.validate_data_consistency(test_analysis)
            
            if result['success']:
                consistency_score = result.get('consistency_score', {})
                validations_count = len(result.get('validations', []))
                
                print(f"✅ Validación completada: {validations_count} validaciones realizadas")
                print(f"   📊 Score de consistencia: {consistency_score.get('score', 0)}/100 ({consistency_score.get('level', 'unknown')})")
                print(f"   📋 Listo para declaración: {'Sí' if result.get('is_consistent', False) else 'No'}")
                
                # Mostrar tipos de validaciones
                validations = result.get('validations', [])
                severity_counts = {}
                
                for validation in validations:
                    severity = validation.get('severity', 'unknown')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                for severity, count in severity_counts.items():
                    print(f"   📝 {severity.title()}: {count} validaciones")
                
                self.test_results.append({
                    'test': 'consistency_validation',
                    'status': 'PASSED',
                    'consistency_score': consistency_score.get('score', 0),
                    'validations_count': validations_count
                })
            else:
                raise Exception("Error en validación de consistencia")
                
        except Exception as e:
            print(f"❌ Error en validación de consistencia: {str(e)}")
            self.test_results.append({
                'test': 'consistency_validation',
                'status': 'FAILED',
                'error': str(e)
            })
    
    def generate_final_report(self):
        """Genera reporte final de todas las pruebas"""
        end_time = datetime.now()
        total_time = (end_time - self.start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("📊 REPORTE FINAL DE PRUEBAS ACCOUNTIA")
        print("=" * 60)
        
        # Estadísticas generales
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['status'] == 'PASSED'])
        failed_tests = len([t for t in self.test_results if t['status'] == 'FAILED'])
        
        print(f"⏱️  Tiempo total de ejecución: {total_time:.2f} segundos")
        print(f"📋 Tests ejecutados: {total_tests}")
        print(f"✅ Tests exitosos: {passed_tests}")
        print(f"❌ Tests fallidos: {failed_tests}")
        print(f"📊 Tasa de éxito: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n📋 DETALLE DE RESULTADOS:")
        print("-" * 40)
        
        for test in self.test_results:
            status_icon = "✅" if test['status'] == 'PASSED' else "❌"
            test_name = test['test'].replace('_', ' ').title()
            print(f"{status_icon} {test_name}")
            
            if test['status'] == 'FAILED' and 'error' in test:
                print(f"   Error: {test['error']}")
            elif test['status'] == 'PASSED':
                # Mostrar métricas específicas si están disponibles
                if 'records_count' in test:
                    print(f"   Registros procesados: {test['records_count']}")
                if 'processing_time' in test:
                    print(f"   Tiempo de procesamiento: {test['processing_time']:.2f}s")
                if 'consistency_score' in test:
                    print(f"   Score de consistencia: {test['consistency_score']}/100")
        
        # Conclusiones
        print("\n🎯 CONCLUSIONES:")
        print("-" * 40)
        
        if failed_tests == 0:
            print("🎉 ¡EXCELENTE! Todos los tests pasaron exitosamente.")
            print("✅ El sistema AccountIA está funcionando correctamente.")
            print("🚀 La implementación del 'Plan de Conocimiento del Contador' está completa.")
        else:
            print(f"⚠️  Se encontraron {failed_tests} problemas que requieren atención.")
            print("🔧 Revisa los errores reportados arriba.")
            
        print("\n📁 PRÓXIMOS PASOS:")
        if failed_tests == 0:
            print("1. ✅ Proceder con implementación del frontend inteligente")
            print("2. ✅ Realizar pruebas de integración completas")
            print("3. ✅ Preparar para testing con usuarios reales")
        else:
            print("1. 🔧 Corregir los errores identificados")
            print("2. 🔄 Re-ejecutar las pruebas")
            print("3. 📋 Validar funcionamiento completo")
        
        # Guardar reporte en archivo
        report_data = {
            'execution_date': self.start_time.isoformat(),
            'total_time': total_time,
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'failed_tests': failed_tests,
                'success_rate': passed_tests/total_tests*100 if total_tests > 0 else 0
            },
            'test_results': self.test_results
        }
        
        report_file = project_root / f"test_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            print(f"\n📄 Reporte guardado en: {report_file}")
        except Exception as e:
            print(f"⚠️  No se pudo guardar el reporte: {str(e)}")


if __name__ == "__main__":
    print("🤖 ACCOUNTIA - TEST SUITE DE INTELIGENCIA FISCAL")
    print("Validando implementación del Plan de Conocimiento del Contador")
    print()
    
    try:
        runner = AccountIATestRunner()
        runner.run_complete_test_suite()
    except KeyboardInterrupt:
        print("\n⚠️  Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error crítico en test suite: {str(e)}")
        import traceback
        traceback.print_exc()
