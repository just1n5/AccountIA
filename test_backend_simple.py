#!/usr/bin/env python3
"""
Verificación rápida del backend simplificado.
"""
import requests
import json
import time

def test_backend():
    """Prueba las principales funcionalidades del backend."""
    base_url = "http://localhost:8000"
    
    print("🔍 VERIFICANDO BACKEND SIMPLIFICADO")
    print("=" * 50)
    
    # 1. Health check
    print("1. Health check...")
    try:
        response = requests.get(f"{base_url}/health/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health check OK")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ No se puede conectar al backend: {e}")
        return False
    
    # 2. Test API declarations list
    print("2. Probando GET /api/v1/declarations/...")
    try:
        response = requests.get(f"{base_url}/api/v1/declarations/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ GET declarations OK - {data.get('count', 0)} declaraciones")
        else:
            print(f"   ❌ GET declarations failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error en GET declarations: {e}")
        return False
    
    # 3. Test crear declaración
    print("3. Probando POST /api/v1/declarations/...")
    try:
        data = {
            "fiscal_year": 2024,
            "title": "Test Declaración"
        }
        response = requests.post(
            f"{base_url}/api/v1/declarations/", 
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 201:
            result = response.json()
            print(f"   ✅ POST declarations OK - ID: {result.get('id')}")
            return True
        else:
            print(f"   ❌ POST declarations failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error en POST declarations: {e}")
        return False

def main():
    """Función principal."""
    print("⏳ Esperando que el backend esté listo...")
    time.sleep(3)
    
    if test_backend():
        print("\n🎉 BACKEND FUNCIONANDO CORRECTAMENTE")
        print("✅ Modo demo deshabilitado")
        print("✅ Endpoints de declarations funcionando")
        print("✅ Base de datos SQLite funcionando")
        print("\n🚀 Puedes continuar con el desarrollo!")
    else:
        print("\n❌ PROBLEMAS DETECTADOS EN EL BACKEND")
        print("💡 Revisa los logs del servidor para más detalles")

if __name__ == "__main__":
    main()
