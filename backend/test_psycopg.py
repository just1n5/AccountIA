#!/usr/bin/env python
"""Test directo de psycopg sin Django"""
import psycopg

print("=== TEST DIRECTO PSYCOPG ===")

# Intentar conexión directa con psycopg
try:
    conn = psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="accountia_dev", 
        user="accountia_user",
        password="password123"
    )
    print("✅ PSYCOPG CONECTÓ EXITOSAMENTE")
    
    cursor = conn.cursor()
    cursor.execute("SELECT current_user, current_database();")
    result = cursor.fetchone()
    print(f"✅ Usuario: {result[0]}, DB: {result[1]}")
    
    conn.close()
    
except Exception as e:
    print(f"❌ PSYCOPG FALLÓ: {e}")

print("\n=== TEST SIN PASSWORD (TRUST) ===")
# Probar sin password (trust debería permitir esto)
try:
    conn = psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="accountia_dev", 
        user="accountia_user"
        # Sin password
    )
    print("✅ PSYCOPG SIN PASSWORD FUNCIONÓ")
    conn.close()
    
except Exception as e:
    print(f"❌ PSYCOPG SIN PASSWORD FALLÓ: {e}")
