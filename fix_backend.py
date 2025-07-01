#!/usr/bin/env python
"""
Script para aplicar migraciones y verificar el estado del backend.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection
from django.apps import apps

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def check_database_connection():
    """Verifica que la conexión a la base de datos funcione"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexión a la base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}")
        return False

def apply_migrations():
    """Aplica las migraciones pendientes"""
    try:
        print("\n🔄 Aplicando migraciones...")
        
        # Mostrar migraciones pendientes
        execute_from_command_line(['manage.py', 'showmigrations', '--plan'])
        
        # Aplicar migraciones
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        
        print("✅ Migraciones aplicadas exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error aplicando migraciones: {e}")
        return False

def verify_declaration_model():
    """Verifica que el modelo Declaration funcione correctamente"""
    try:
        from declarations.models import Declaration
        
        # Verificar que podemos hacer queries básicos
        declarations_count = Declaration.objects.count()
        active_declarations = Declaration.objects.filter(is_active=True).count()
        
        print(f"✅ Modelo Declaration verificado:")
        print(f"   - Total declaraciones: {declarations_count}")
        print(f"   - Declaraciones activas: {active_declarations}")
        
        return True
    except Exception as e:
        print(f"❌ Error verificando modelo Declaration: {e}")
        return False

def create_test_data():
    """Crea datos de prueba si no existen"""
    try:
        from django.contrib.auth import get_user_model
        from declarations.models import Declaration
        
        User = get_user_model()
        
        # Crear usuario de prueba si no existe
        test_user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Usuario',
                'last_name': 'de Prueba'
            }
        )
        
        if created:
            print("✅ Usuario de prueba creado")
        
        # Crear declaración de prueba si no existe
        test_declaration, created = Declaration.objects.get_or_create(
            user=test_user,
            fiscal_year=2024,
            title='Declaración Renta 2024',
            defaults={
                'status': 'draft',
                'total_income': 50000000,
                'total_withholdings': 3000000,
            }
        )
        
        if created:
            print("✅ Declaración de prueba creada")
        
        return True
    except Exception as e:
        print(f"❌ Error creando datos de prueba: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Verificando y reparando backend de AccountIA...")
    print("=" * 50)
    
    # 1. Verificar conexión a la base de datos
    if not check_database_connection():
        return False
    
    # 2. Aplicar migraciones
    if not apply_migrations():
        return False
    
    # 3. Verificar modelo Declaration
    if not verify_declaration_model():
        return False
    
    # 4. Crear datos de prueba
    if not create_test_data():
        return False
    
    print("\n🎉 Backend verificado y reparado exitosamente!")
    print("✅ Todas las verificaciones pasaron")
    print("\n📝 Próximos pasos:")
    print("1. Iniciar el servidor de desarrollo: python manage.py runserver")
    print("2. Verificar que el endpoint /api/v1/declarations/ funcione")
    print("3. Probar el frontend nuevamente")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
