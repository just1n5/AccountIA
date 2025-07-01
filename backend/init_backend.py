#!/usr/bin/env python
"""
Script para inicializar el backend con configuración simplificada
"""
import os
import sys
import django
from pathlib import Path

# Agregar el directorio backend al path de Python
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configurar Django con settings simplificados
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development_simple')

try:
    django.setup()
    
    print("✅ Django configurado correctamente")
    
    # Verificar la base de datos
    from django.core.management import execute_from_command_line
    
    print("🔄 Aplicando migraciones...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("🔄 Creando superusuario demo si no existe...")
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(email='demo@accountia.co').exists():
        User.objects.create_user(
            email='demo@accountia.co',
            username='demo_user',
            first_name='Demo',
            last_name='User',
            password='demo123',
            is_superuser=True,
            is_staff=True
        )
        print("✅ Usuario demo creado: demo@accountia.co / demo123")
    else:
        print("✅ Usuario demo ya existe")
    
    print("🚀 Backend inicializado correctamente")
    print("🌐 Puedes acceder al admin en: http://localhost:8000/admin/")
    print("📚 API docs en: http://localhost:8000/api/docs/")
    
except Exception as e:
    print(f"❌ Error inicializando backend: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
