#!/usr/bin/env python3
"""
Script de prueba para verificar que los endpoints de AccountIA funcionen correctamente
después de aplicar la solución de autenticación.
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(text):
    print(f"\n{'='*60}")
    print(f"🧪 {text}")
    print(f"{'='*60}")

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def test_endpoint(method, url, data=None, expected_status=200):
    """Función auxiliar para probar endpoints"""
    try:
        print(f"\n🔍 Testing {method} {url}")
        
        if method.upper() == 'GET':
            response = requests.get(url, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=10)
        else:
            raise ValueError(f"Método {method} no soportado")
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == expected_status:
            print_success(f"Endpoint {url} funciona correctamente")
            
            # Mostrar contenido de respuesta si es JSON
            try:
                json_data = response.json()
                if isinstance(json_data, dict):
                    if 'count' in json_data:
                        print(f"   Resultados: {json_data.get('count', 0)} items")
                    elif 'id' in json_data:
                        print(f"   ID creado: {json_data['id']}")
                    elif 'status' in json_data:
                        print(f"   Status: {json_data['status']}")
                elif isinstance(json_data, list):
                    print(f"   Lista con {len(json_data)} elementos")
                
                return response.json()
            except:
                print(f"   Respuesta (no JSON): {response.text[:100]}")
                return response.text
        else:
            print_error(f"Endpoint {url} falló. Esperado: {expected_status}, Recibido: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print_error(f"No se puede conectar a {url}. ¿Está el servidor corriendo?")
        return None
    except requests.exceptions.Timeout:
        print_error(f"Timeout conectando a {url}")
        return None
    except Exception as e:
        print_error(f"Error inesperado: {e}")
        return None

def main():
    print_header("ACCOUNTIA - PRUEBAS DE ENDPOINTS")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"URL Base: {BASE_URL}")
    
    success_count = 0
    total_tests = 0
    
    # 1. Verificar salud del sistema
    print_header("1. VERIFICACIÓN DE SALUD")
    total_tests += 1
    health_result = test_endpoint('GET', f"{BASE_URL}/health/")
    if health_result:
        success_count += 1
    
    # 2. Verificar schema de API
    print_header("2. VERIFICACIÓN DE SCHEMA")
    total_tests += 1
    schema_result = test_endpoint('GET', f"{BASE_URL}/api/schema/")
    if schema_result:
        success_count += 1
        print_info("Schema de API disponible")
    
    # 3. Probar endpoint de declaraciones (GET)
    print_header("3. PRUEBA DE DECLARACIONES - LISTADO")
    total_tests += 1
    declarations_result = test_endpoint('GET', f"{BASE_URL}/api/v1/declarations/")
    if declarations_result is not None:
        success_count += 1
    
    # 4. Crear una declaración de prueba (POST)
    print_header("4. PRUEBA DE DECLARACIONES - CREACIÓN")
    total_tests += 1
    test_declaration = {
        "fiscal_year": 2024
    }
    
    create_result = test_endpoint('POST', f"{BASE_URL}/api/v1/declarations/", test_declaration, 201)
    declaration_id = None
    if create_result and isinstance(create_result, dict) and 'id' in create_result:
        success_count += 1
        declaration_id = create_result['id']
        print_success(f"Declaración creada con ID: {declaration_id}")
    
    # 5. Probar endpoint de documentos (GET)
    print_header("5. PRUEBA DE DOCUMENTOS - LISTADO")
    total_tests += 1
    documents_result = test_endpoint('GET', f"{BASE_URL}/api/v1/documents/")
    if documents_result is not None:
        success_count += 1
    
    # 6. Probar plantillas de documentos
    print_header("6. PRUEBA DE PLANTILLAS")
    total_tests += 1
    templates_result = test_endpoint('GET', f"{BASE_URL}/api/v1/templates/")
    if templates_result is not None:
        success_count += 1
    
    # 7. Si se creó una declaración, probar obtener su detalle
    if declaration_id:
        print_header("7. PRUEBA DE DECLARACIÓN - DETALLE")
        total_tests += 1
        detail_result = test_endpoint('GET', f"{BASE_URL}/api/v1/declarations/{declaration_id}/")
        if detail_result:
            success_count += 1
    
    # Resumen final
    print_header("RESUMEN DE PRUEBAS")
    print(f"✅ Pruebas exitosas: {success_count}/{total_tests}")
    print(f"❌ Pruebas fallidas: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print_success("🎉 ¡TODAS LAS PRUEBAS PASARON! El sistema está funcionando correctamente")
        return 0
    elif success_count > 0:
        print(f"⚠️  Algunas pruebas fallaron. Revisa la configuración.")
        return 1
    else:
        print_error("💥 TODAS LAS PRUEBAS FALLARON. Verifica que el servidor esté corriendo.")
        return 2

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
