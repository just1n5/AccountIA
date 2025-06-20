#!/usr/bin/env python3
"""
Script de verificación de configuración de Google Cloud Storage
"""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def check_env_variables():
    """Verificar variables de entorno"""
    print("🔍 Verificando variables de entorno...")
    
    required_vars = [
        'GOOGLE_CLOUD_PROJECT',
        'GCS_BUCKET_NAME', 
        'GOOGLE_APPLICATION_CREDENTIALS'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"  ✅ {var}: {value}")
    
    if missing_vars:
        print(f"  ❌ Variables faltantes: {', '.join(missing_vars)}")
        return False
    
    return True

def check_credentials_file():
    """Verificar archivo de credenciales"""
    print("\n📁 Verificando archivo de credenciales...")
    
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if not credentials_path:
        print("  ❌ Variable GOOGLE_APPLICATION_CREDENTIALS no configurada")
        return False
    
    full_path = project_root / credentials_path
    if not full_path.exists():
        print(f"  ❌ Archivo no encontrado: {full_path}")
        print(f"  💡 Coloca el archivo JSON en: {full_path}")
        return False
    
    print(f"  ✅ Archivo encontrado: {full_path}")
    return True

def test_gcs_connection():
    """Probar conexión a Google Cloud Storage"""
    print("\n☁️ Probando conexión a Google Cloud Storage...")
    
    try:
        from google.cloud import storage
        
        client = storage.Client(project=os.getenv('GOOGLE_CLOUD_PROJECT'))
        bucket_name = os.getenv('GCS_BUCKET_NAME')
        bucket = client.bucket(bucket_name)
        
        # Verificar que el bucket existe
        if bucket.exists():
            print(f"  ✅ Conexión exitosa al bucket: {bucket_name}")
            print(f"  ✅ Proyecto: {client.project}")
            return True
        else:
            print(f"  ❌ El bucket no existe: {bucket_name}")
            return False
            
    except ImportError:
        print("  ❌ google-cloud-storage no instalado")
        print("  💡 Ejecuta: pip install google-cloud-storage")
        return False
    except Exception as e:
        print(f"  ❌ Error de conexión: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🚀 AccountIA - Verificación de Google Cloud Storage\n")
    
    # Cargar variables de entorno desde .env
    env_file = project_root / '.env'
    if env_file.exists():
        print(f"📋 Cargando variables desde: {env_file}\n")
        # Cargar manualmente el archivo .env
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
    else:
        print("⚠️ Archivo .env no encontrado\n")
    
    # Ejecutar verificaciones
    checks = [
        check_env_variables(),
        check_credentials_file(),
        test_gcs_connection()
    ]
    
    # Resumen
    print("\n" + "="*50)
    if all(checks):
        print("🎉 ¡Todas las verificaciones pasaron! Google Cloud Storage está configurado correctamente.")
    else:
        print("❌ Algunas verificaciones fallaron. Revisa la configuración.")
        print("\n💡 Pasos para solucionar:")
        print("   1. Verifica que el archivo .env tenga los valores correctos")
        print("   2. Descarga el JSON de credenciales desde Google Cloud Console")
        print("   3. Colócalo en backend/config/credentials/google-cloud-credentials.json")
        print("   4. Ejecuta: pip install google-cloud-storage")
    
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Verificación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)
