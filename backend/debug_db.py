#!/usr/bin/env python
"""Debug script para verificar configuración de base de datos en Django"""
import os
import sys

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

import django
django.setup()

from django.conf import settings

print("=== CONFIGURACIÓN DE BASE DE DATOS ===")
db_config = settings.DATABASES['default']

print(f"ENGINE: {db_config['ENGINE']}")
print(f"NAME: {db_config['NAME']}")
print(f"USER: {db_config['USER']}")
print(f"PASSWORD: {db_config['PASSWORD']}")
print(f"HOST: {db_config['HOST']}")
print(f"PORT: {db_config['PORT']}")

print("\n=== VARIABLES DE ENTORNO ===")
print(f"DB_NAME: {os.getenv('DB_NAME', 'NO DEFINIDA')}")
print(f"DB_USER: {os.getenv('DB_USER', 'NO DEFINIDA')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD', 'NO DEFINIDA')}")
print(f"DB_HOST: {os.getenv('DB_HOST', 'NO DEFINIDA')}")
print(f"DB_PORT: {os.getenv('DB_PORT', 'NO DEFINIDA')}")

print("\n=== TEST DE CONEXIÓN ===")
try:
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute("SELECT current_user, current_database();")
    result = cursor.fetchone()
    print(f"✅ CONEXIÓN EXITOSA: Usuario={result[0]}, DB={result[1]}")
except Exception as e:
    print(f"❌ ERROR DE CONEXIÓN: {e}")
