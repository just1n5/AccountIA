#!/usr/bin/env python3
"""
Script para crear y aplicar migraciones para múltiples declaraciones.
"""

import os
import sys
import django

# Agregar el directorio backend al path
sys.path.append('C:/Users/justi/Desktop/Proyecto Accountia/backend')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """Ejecuta la creación y aplicación de migraciones."""
    
    print("🔄 CREANDO Y APLICANDO MIGRACIONES PARA MÚLTIPLES DECLARACIONES")
    print("=" * 70)
    
    try:
        # 1. Crear migraciones para declarations
        print("\n📝 Paso 1: Creando migraciones para app declarations...")
        call_command('makemigrations', 'declarations', verbosity=2)
        
        # 2. Crear migraciones para documents (si hay cambios)
        print("\n📝 Paso 2: Verificando migraciones para app documents...")
        call_command('makemigrations', 'documents', verbosity=2)
        
        # 3. Mostrar migraciones pendientes
        print("\n📋 Paso 3: Revisando migraciones pendientes...")
        call_command('showmigrations', verbosity=1)
        
        # 4. Aplicar migraciones
        print("\n⚡ Paso 4: Aplicando migraciones...")
        call_command('migrate', verbosity=2)
        
        # 5. Verificar estructura de base de datos
        print("\n🔍 Paso 5: Verificando estructura de base de datos...")
        
        with connection.cursor() as cursor:
            # Verificar tabla declarations
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'declarations_declaration'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            print("\n📊 Estructura de tabla declarations_declaration:")
            for col in columns:
                print(f"   - {col[0]} ({col[1]}) {'NULL' if col[2] == 'YES' else 'NOT NULL'}")
        
        print("\n✅ MIGRACIONES COMPLETADAS EXITOSAMENTE")
        print("\n🎯 Nuevas funcionalidades disponibles:")
        print("   ✅ Múltiples declaraciones por usuario y año")
        print("   ✅ Títulos personalizados para declaraciones")
        print("   ✅ Soft delete (eliminación reversible)")
        print("   ✅ Duplicación de declaraciones")
        print("   ✅ Estadísticas y métricas avanzadas")
        print("   ✅ Acciones en lote")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR durante la migración: {str(e)}")
        logger.exception("Error durante migración")
        return False


def create_sample_data():
    """Crea datos de ejemplo para probar las múltiples declaraciones."""
    
    print("\n🧪 CREANDO DATOS DE EJEMPLO...")
    
    try:
        from apps.users.models import User
        from apps.declarations.models import Declaration
        
        # Crear usuario de prueba
        user, created = User.objects.get_or_create(
            email='test@accountia.co',
            defaults={
                'username': 'test_user',
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True
            }
        )
        
        if created:
            print(f"   ✅ Usuario creado: {user.email}")
        else:
            print(f"   ℹ️  Usuario ya existe: {user.email}")
        
        # Crear múltiples declaraciones de ejemplo
        sample_declarations = [
            {
                'title': 'Declaración Principal 2023',
                'fiscal_year': 2023,
                'status': 'completed'
            },
            {
                'title': 'Declaración Corrección 2023',
                'fiscal_year': 2023,
                'status': 'draft'
            },
            {
                'title': 'Declaración Renta 2024',
                'fiscal_year': 2024,
                'status': 'processing'
            },
            {
                'title': 'Borrador Provisional 2024',
                'fiscal_year': 2024,
                'status': 'draft'
            }
        ]
        
        created_count = 0
        for decl_data in sample_declarations:
            declaration, created = Declaration.objects.get_or_create(
                user=user,
                title=decl_data['title'],
                defaults=decl_data
            )
            
            if created:
                created_count += 1
                print(f"   ✅ Declaración creada: {declaration.title}")
            else:
                print(f"   ℹ️  Declaración ya existe: {declaration.title}")
        
        print(f"\n📊 Resumen:")
        print(f"   - Usuario: {user.email}")
        print(f"   - Declaraciones totales: {user.declarations.count()}")
        print(f"   - Declaraciones activas: {user.declarations.filter(is_active=True).count()}")
        print(f"   - Nuevas declaraciones creadas: {created_count}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR creando datos de ejemplo: {str(e)}")
        logger.exception("Error creando datos de ejemplo")
        return False


if __name__ == "__main__":
    print("🚀 SETUP DE MÚLTIPLES DECLARACIONES - ACCOUNTIA")
    print("Actualizando base de datos para soportar múltiples declaraciones por usuario...\n")
    
    # Ejecutar migraciones
    migration_success = main()
    
    if migration_success:
        # Crear datos de ejemplo
        print("\n" + "=" * 70)
        sample_data_success = create_sample_data()
        
        if sample_data_success:
            print("\n🎉 ¡SETUP COMPLETADO EXITOSAMENTE!")
            print("\n🔥 ¡AccountIA ahora soporta múltiples declaraciones por usuario!")
            print("\n📋 Próximos pasos:")
            print("   1. Probar las nuevas APIs de declaraciones")
            print("   2. Actualizar el frontend para mostrar múltiples declaraciones")
            print("   3. Probar funcionalidades de duplicar y eliminar")
        else:
            print("\n⚠️  Setup completado con errores en datos de ejemplo")
    else:
        print("\n❌ Setup falló. Revisar errores arriba.")
        sys.exit(1)
