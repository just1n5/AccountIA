#!/usr/bin/env python
"""
Script de configuración rápida para el Sprint 2 de AccountIA.
Ejecuta las migraciones y configuraciones necesarias.
"""
import os
import sys
import subprocess
from pathlib import Path

# Colores para la terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_step(message):
    print(f"\n{BLUE}➤ {message}{RESET}")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠ {message}{RESET}")

def run_command(command, cwd=None):
    """Ejecuta un comando y retorna el resultado."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=cwd
        )
        if result.returncode == 0:
            return True, result.stdout
        else:
            return False, result.stderr
    except Exception as e:
        return False, str(e)

def main():
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}AccountIA - Configuración Sprint 2{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    # Obtener rutas
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    frontend_dir = project_root / "frontend"
    
    # 1. Verificar Python
    print_step("Verificando Python...")
    success, output = run_command("python --version")
    if success:
        print_success(f"Python instalado: {output.strip()}")
    else:
        print_error("Python no encontrado. Por favor instala Python 3.8+")
        sys.exit(1)
    
    # 2. Backend - Instalar dependencias
    print_step("Instalando dependencias del backend...")
    success, output = run_command("pip install -r requirements.txt", cwd=backend_dir)
    if success:
        print_success("Dependencias del backend instaladas")
    else:
        print_error(f"Error instalando dependencias: {output}")
        print_warning("Intenta crear un entorno virtual primero:")
        print("  python -m venv venv")
        print("  source venv/bin/activate  # En Linux/Mac")
        print("  venv\\Scripts\\activate     # En Windows")
    
    # 3. Backend - Migraciones
    print_step("Ejecutando migraciones de Django...")
    
    # Crear migraciones
    success, output = run_command("python manage.py makemigrations", cwd=backend_dir)
    if success:
        print_success("Migraciones creadas")
    else:
        print_warning(f"Advertencia en migraciones: {output}")
    
    # Aplicar migraciones
    success, output = run_command("python manage.py migrate", cwd=backend_dir)
    if success:
        print_success("Migraciones aplicadas")
    else:
        print_error(f"Error aplicando migraciones: {output}")
    
    # 4. Frontend - Verificar Node.js
    print_step("Verificando Node.js...")
    success, output = run_command("node --version")
    if success:
        print_success(f"Node.js instalado: {output.strip()}")
    else:
        print_error("Node.js no encontrado. Por favor instala Node.js 18+")
        print("  Descarga desde: https://nodejs.org/")
    
    # 5. Frontend - Instalar dependencias
    print_step("Instalando dependencias del frontend...")
    success, output = run_command("npm install", cwd=frontend_dir)
    if success:
        print_success("Dependencias del frontend instaladas")
    else:
        print_warning(f"Advertencia instalando dependencias: {output}")
    
    # 6. Crear archivo .env si no existe
    print_step("Configurando variables de entorno...")
    
    backend_env = backend_dir / ".env"
    if not backend_env.exists():
        print_warning(".env del backend no existe. Creando desde ejemplo...")
        env_example = backend_dir / ".env.example"
        if env_example.exists():
            import shutil
            shutil.copy(env_example, backend_env)
            print_success(".env del backend creado")
        else:
            print_warning("No se encontró .env.example del backend")
    
    frontend_env = frontend_dir / ".env"
    if not frontend_env.exists():
        print_warning(".env del frontend no existe. Creando desde ejemplo...")
        env_example = frontend_dir / ".env.example"
        if env_example.exists():
            import shutil
            shutil.copy(env_example, frontend_env)
            print_success(".env del frontend creado")
        else:
            print_warning("No se encontró .env.example del frontend")
    
    # 7. Crear superusuario
    print_step("Creación de superusuario Django...")
    print("  Para crear un superusuario, ejecuta:")
    print(f"  cd {backend_dir}")
    print("  python manage.py createsuperuser")
    
    # 8. Resumen final
    print(f"\n{GREEN}{'='*60}{RESET}")
    print(f"{GREEN}¡Configuración completada!{RESET}")
    print(f"{GREEN}{'='*60}{RESET}")
    
    print("\nPara iniciar el desarrollo:")
    print("\n1. Backend:")
    print(f"   cd {backend_dir}")
    print("   python manage.py runserver")
    
    print("\n2. Frontend:")
    print(f"   cd {frontend_dir}")
    print("   npm run dev")
    
    print("\n3. Celery (en otra terminal):")
    print(f"   cd {backend_dir}")
    print("   celery -A config worker -l info")
    
    print("\n4. Redis (usando Docker):")
    print("   docker run -d -p 6379:6379 redis:alpine")
    
    print(f"\n{YELLOW}Importante:{RESET}")
    print("- Configura las variables de entorno en los archivos .env")
    print("- Configura Firebase en ambos proyectos")
    print("- Para producción, configura Google Cloud Storage")
    
    print(f"\n{BLUE}¡Feliz desarrollo! 🚀{RESET}")

if __name__ == "__main__":
    main()