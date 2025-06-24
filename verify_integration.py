#!/usr/bin/env python3
"""
Script de Verificación Rápida - Integración Frontend-Backend
AccountIA Sprint 2

Este script verifica que la integración esté funcionando correctamente.
"""

import requests
import json
import sys
import subprocess
import time
from pathlib import Path

def print_status(message, status="INFO"):
    colors = {
        "SUCCESS": "\033[92m✅",
        "ERROR": "\033[91m❌", 
        "WARNING": "\033[93m⚠️",
        "INFO": "\033[94mℹ️"
    }
    reset = "\033[0m"
    print(f"{colors.get(status, colors['INFO'])} {message}{reset}")

def check_backend():
    """Verificar que el backend esté funcionando"""
    print_status("Verificando Backend Django...", "INFO")
    
    try:
        # Health check
        response = requests.get("http://localhost:8000/health/", timeout=5)
        if response.status_code == 200:
            print_status("Backend health check OK", "SUCCESS")
        else:
            print_status(f"Backend health check falló: {response.status_code}", "ERROR")
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"No se puede conectar al backend: {e}", "ERROR")
        print_status("Asegúrate de que el backend esté ejecutándose en puerto 8000", "WARNING")
        return False
    
    try:
        # Declaraciones endpoint
        response = requests.get("http://localhost:8000/api/v1/declarations/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get('count', 0)
            print_status(f"API de declaraciones OK - {count} declaraciones encontradas", "SUCCESS")
            return True
        else:
            print_status(f"API de declaraciones falló: {response.status_code}", "ERROR")
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"Error en API de declaraciones: {e}", "ERROR")
        return False

def check_env_variables():
    """Verificar variables de entorno críticas"""
    print_status("Verificando variables de entorno...", "INFO")
    
    env_file = Path(".env")
    if not env_file.exists():
        print_status("Archivo .env no encontrado", "ERROR")
        return False
    
    # Manejar codificación en Windows
    try:
        env_content = env_file.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        try:
            env_content = env_file.read_text(encoding='latin-1')
        except UnicodeDecodeError:
            env_content = env_file.read_text(encoding='cp1252', errors='ignore')
    
    critical_vars = {
        "VITE_API_URL": "http://localhost:8000/api/v1",
        "DEV_SKIP_AUTH_FOR_TESTING": "1",
        "CORS_ALLOWED_ORIGINS": "http://localhost:3000"
    }
    
    all_good = True
    for var, expected in critical_vars.items():
        if f"{var}=" in env_content:
            if expected in env_content:
                print_status(f"{var} configurada correctamente", "SUCCESS")
            else:
                print_status(f"{var} configurada pero valor podría ser incorrecto", "WARNING")
        else:
            print_status(f"{var} no encontrada", "ERROR")
            all_good = False
    
    return all_good

def check_frontend_files():
    """Verificar archivos críticos del frontend"""
    print_status("Verificando archivos del frontend...", "INFO")
    
    critical_files = [
        "frontend/package.json",
        "frontend/vite.config.js",
        "frontend/src/services/api.ts",
        "frontend/src/services/declarationService.ts",
        "frontend/src/components/dashboard/Dashboard.tsx"
    ]
    
    all_exist = True
    for file_path in critical_files:
        if Path(file_path).exists():
            print_status(f"{file_path} ✓", "SUCCESS")
        else:
            print_status(f"{file_path} no encontrado", "ERROR")
            all_exist = False
    
    # Verificar contenido de vite.config.js
    vite_config = Path("frontend/vite.config.js")
    if vite_config.exists():
        try:
            content = vite_config.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            content = vite_config.read_text(encoding='cp1252', errors='ignore')
        if "http://localhost:8000" in content:
            print_status("Proxy de Vite configurado para desarrollo local", "SUCCESS")
        elif "http://backend:8000" in content:
            print_status("⚠️ Proxy de Vite configurado para Docker - debería ser localhost", "WARNING")
        else:
            print_status("Configuración de proxy no encontrada", "WARNING")
    
    return all_exist

def test_api_integration():
    """Probar integración específica de APIs"""
    print_status("Probando integración de APIs...", "INFO")
    
    try:
        # Probar GET declarations
        response = requests.get("http://localhost:8000/api/v1/declarations/")
        if response.status_code == 200:
            print_status("GET /api/v1/declarations/ ✓", "SUCCESS")
        else:
            print_status(f"GET /api/v1/declarations/ falló: {response.status_code}", "ERROR")
            return False
        
        # Probar crear declaración (puede fallar si ya existe)
        test_data = {"fiscal_year": 2025}
        response = requests.post("http://localhost:8000/api/v1/declarations/", 
                               json=test_data, 
                               headers={"Content-Type": "application/json"})
        
        if response.status_code in [201, 400]:  # 201 = creada, 400 = ya existe
            if response.status_code == 201:
                print_status("POST /api/v1/declarations/ ✓ (declaración creada)", "SUCCESS")
            else:
                print_status("POST /api/v1/declarations/ ✓ (declaración ya existe)", "SUCCESS")
        else:
            print_status(f"POST /api/v1/declarations/ falló: {response.status_code}", "ERROR")
            return False
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_status(f"Error en pruebas de API: {e}", "ERROR")
        return False

def check_ports():
    """Verificar que los puertos estén disponibles/en uso"""
    print_status("Verificando puertos...", "INFO")
    
    # Verificar puerto 8000 (backend)
    try:
        response = requests.get("http://localhost:8000/health/", timeout=2)
        print_status("Puerto 8000 (backend) - ACTIVO ✓", "SUCCESS")
    except:
        print_status("Puerto 8000 (backend) - NO RESPONDE", "ERROR")
        return False
    
    # Verificar puerto 3000 (frontend) - solo si está ejecutándose
    try:
        response = requests.get("http://localhost:3000", timeout=2)
        print_status("Puerto 3000 (frontend) - ACTIVO ✓", "SUCCESS")
    except:
        print_status("Puerto 3000 (frontend) - NO ACTIVO (esto es normal si no has iniciado el frontend)", "INFO")
    
    return True

def main():
    print("""
🚀 AccountIA - Verificación de Integración Frontend-Backend
===========================================================
""")
    
    all_checks_passed = True
    
    # Ejecutar todas las verificaciones
    checks = [
        ("Variables de entorno", check_env_variables),
        ("Archivos del frontend", check_frontend_files),
        ("Puertos", check_ports),
        ("Backend Django", check_backend),
        ("Integración de APIs", test_api_integration)
    ]
    
    for check_name, check_func in checks:
        print(f"\n🔍 {check_name}")
        print("-" * 50)
        if not check_func():
            all_checks_passed = False
    
    print("\n" + "="*60)
    print("📋 RESUMEN DE VERIFICACIÓN")
    print("="*60)
    
    if all_checks_passed:
        print_status("¡Todas las verificaciones pasaron exitosamente!", "SUCCESS")
        print_status("Tu integración frontend-backend está lista", "SUCCESS")
        print("""
🎯 PRÓXIMOS PASOS:
1. Si el frontend no está ejecutándose: npm run frontend
2. Abrir http://localhost:3000 en tu navegador
3. Probar el dashboard y crear declaraciones
""")
    else:
        print_status("Algunas verificaciones fallaron", "ERROR")
        print_status("Revisa los errores indicados arriba", "WARNING")
        print("""
🔧 PASOS PARA SOLUCIONAR:
1. Asegúrate de que el backend esté ejecutándose: npm run backend
2. Verifica las variables de entorno en .env
3. Revisa los archivos indicados como faltantes
4. Ejecuta este script nuevamente
""")
    
    print(f"\n📚 Para más ayuda, consulta: FRONTEND_INTEGRATION_GUIDE.md\n")

if __name__ == "__main__":
    main()
