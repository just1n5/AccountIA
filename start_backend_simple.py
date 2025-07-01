#!/usr/bin/env python
"""
Script rápido para iniciar el backend con la configuración correcta
"""
import os
import sys
import subprocess

def main():
    print("🚀 INICIANDO BACKEND ACCOUNTIA")
    print("=" * 40)
    
    # Cambiar al directorio backend
    backend_dir = "backend"
    if os.path.exists(backend_dir):
        os.chdir(backend_dir)
        print(f"📁 Cambiado a directorio: {os.getcwd()}")
    else:
        print("❌ Directorio 'backend' no encontrado")
        return
    
    # Verificar Python
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        print(f"🐍 Python: {result.stdout.strip()}")
    except Exception as e:
        print(f"❌ Error verificando Python: {e}")
        return
    
    # Aplicar migraciones
    print("\n🔧 Aplicando migraciones...")
    try:
        subprocess.run([sys.executable, "manage.py", "migrate", "--verbosity=2"], check=True)
        print("✅ Migraciones aplicadas exitosamente")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error aplicando migraciones: {e}")
        return
    
    # Verificar que las migraciones se aplicaron
    print("\n📋 Verificando migraciones...")
    try:
        result = subprocess.run([sys.executable, "manage.py", "showmigrations", "declarations"], 
                              capture_output=True, text=True, check=True)
        print("Migraciones de declarations:")
        print(result.stdout)
    except Exception as e:
        print(f"⚠️ No se pudo verificar migraciones: {e}")
    
    # Iniciar servidor
    print("\n🚀 Iniciando servidor de desarrollo...")
    print("📍 URL: http://localhost:8000")
    print("⏹️  Para detener: Ctrl+C")
    print("-" * 40)
    
    try:
        subprocess.run([sys.executable, "manage.py", "runserver", "8000"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error en el servidor: {e}")
    
    print("\n✅ Backend terminado")

if __name__ == "__main__":
    main()
