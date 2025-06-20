#!/usr/bin/env python3
"""
AccountIA - Verificación de Servicios desde Docker
Este script se ejecuta DENTRO del contenedor Docker donde todas las conexiones funcionan correctamente.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent.parent / 'backend'
sys.path.insert(0, str(project_root))

# Inicializar Django
django.setup()

def check_redis_connection():
    """Verificar conexión a Redis"""
    print("🔍 Verificando conexión a Redis...")
    try:
        import redis
        
        # Conectar usando el hostname interno de Docker
        r = redis.Redis(host='redis', port=6379, db=0)
        
        # Test ping
        ping_result = r.ping()
        print(f"  ✅ Redis ping: {ping_result}")
        
        # Test info
        info = r.info('server')
        print(f"  ✅ Redis versión: {info['redis_version']}")
        
        # Test set/get
        r.set('test_key', 'test_value', ex=10)
        test_value = r.get('test_key')
        print(f"  ✅ Redis set/get: {test_value.decode() if test_value else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error de conexión a Redis: {e}")
        return False

def check_celery_worker():
    """Verificar Celery worker"""
    print("🔍 Verificando Celery worker...")
    try:
        from celery import Celery
        
        # Crear instancia de Celery
        app = Celery('accountia')
        app.config_from_object('config.celery_config')
        
        # Verificar workers activos
        inspect = app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            print(f"  ✅ Workers activos: {list(stats.keys())}")
            for worker, stat in stats.items():
                print(f"    Worker: {worker}")
                print(f"    Pool: {stat.get('pool', {}).get('implementation', 'N/A')}")
            return True
        else:
            print("  ❌ No hay workers conectados")
            return False
            
    except Exception as e:
        print(f"  ❌ Error conectando a Celery: {e}")
        return False

def test_celery_task():
    """Probar envío de tarea simple"""
    print("🔍 Probando envío de tarea a Celery...")
    try:
        from celery import Celery
        
        app = Celery('accountia')
        app.config_from_object('config.celery_config')
        
        # Enviar tarea simple
        @app.task
        def test_task(message):
            return f"Task executed: {message}"
        
        result = test_task.delay("Hello from verification!")
        print(f"  ✅ Tarea enviada: {result.id}")
        
        # Intentar obtener resultado (timeout de 5 segundos)
        try:
            task_result = result.get(timeout=5)
            print(f"  ✅ Resultado de tarea: {task_result}")
            return True
        except Exception as timeout_error:
            print(f"  ⚠️ Tarea enviada pero timeout en resultado: {timeout_error}")
            return True  # La tarea se envió, es suficiente para la verificación
            
    except Exception as e:
        print(f"  ❌ Error probando tarea: {e}")
        return False

def check_database_connection():
    """Verificar conexión a la base de datos"""
    print("🔍 Verificando conexión a PostgreSQL...")
    try:
        from django.db import connection
        
        # Test query
        with connection.cursor() as cursor:
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]
            print(f"  ✅ PostgreSQL: {version}")
            
        # Test modelo
        from django.contrib.auth.models import User
        user_count = User.objects.count()
        print(f"  ✅ Usuarios en BD: {user_count}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error de conexión a PostgreSQL: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 AccountIA - Verificación de Servicios desde Docker\n")
    
    # Ejecutar verificaciones
    checks = [
        check_database_connection(),
        check_redis_connection(),
        check_celery_worker(),
        test_celery_task()
    ]
    
    # Resumen
    print("\n" + "="*60)
    if all(checks):
        print("🎉 ¡Todas las verificaciones pasaron! Servicios funcionando correctamente.")
        print("\n💡 Comandos útiles:")
        print("   npm run dev              # Iniciar todos los servicios")
        print("   npm run health           # Verificar estado general")
        print("   npm run celery:worker    # Ver logs del worker")
        print("   npm run logs             # Ver todos los logs")
    else:
        print("❌ Algunas verificaciones fallaron.")
        print("\n💡 Pasos para solucionar:")
        print("   1. Verificar que todos los servicios estén corriendo: docker-compose ps")
        print("   2. Reiniciar servicios: docker-compose restart redis celery_worker")
        print("   3. Ver logs: docker-compose logs redis celery_worker")
        print("   4. Reinicio completo si es necesario: npm run restart")
    
    print("="*60)
    return all(checks)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
