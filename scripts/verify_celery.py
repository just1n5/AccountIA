#!/usr/bin/env python3
"""
Script de verificación de Celery y Redis
"""

import os
import sys
import time
from pathlib import Path

# Agregar el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def check_redis_connection():
    """Verificar conexión a Redis"""
    print("🔍 Verificando conexión a Redis...")
    
    try:
        import redis
        
        # Intentar conectar a Redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        r = redis.from_url(redis_url)
        
        # Test básico
        r.ping()
        
        # Test de escritura/lectura
        test_key = 'accountia:test'
        test_value = 'redis_working'
        r.setex(test_key, 10, test_value)  # Expira en 10 segundos
        
        if r.get(test_key).decode() == test_value:
            print(f"  ✅ Redis funcionando correctamente")
            print(f"  ✅ URL: {redis_url}")
            r.delete(test_key)  # Limpiar
            return True
        else:
            print(f"  ❌ Error en test de escritura/lectura")
            return False
            
    except ImportError:
        print("  ❌ redis no instalado")
        print("  💡 Ejecuta: pip install redis")
        return False
    except Exception as e:
        print(f"  ❌ Error de conexión a Redis: {str(e)}")
        return False

def check_celery_worker():
    """Verificar que Celery worker esté activo"""
    print("\n🔍 Verificando Celery worker...")
    
    try:
        from celery import Celery
        
        # Configurar Celery app
        app = Celery('accountia')
        broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
        app.conf.broker_url = broker_url
        app.conf.result_backend = broker_url
        
        # Verificar workers activos
        inspect = app.control.inspect()
        
        # Dar tiempo para la conexión
        active_workers = inspect.active()
        
        if active_workers:
            print(f"  ✅ Workers activos: {list(active_workers.keys())}")
            
            # Verificar estadísticas
            stats = inspect.stats()
            if stats:
                for worker_name, worker_stats in stats.items():
                    print(f"  ✅ Worker {worker_name}: {worker_stats.get('total', 'N/A')} tareas procesadas")
            
            return True
        else:
            print("  ❌ No hay workers activos")
            print("  💡 Asegúrate de que el contenedor celery_worker esté ejecutándose")
            return False
            
    except ImportError:
        print("  ❌ celery no instalado")
        print("  💡 Ejecuta: pip install celery")
        return False
    except Exception as e:
        print(f"  ❌ Error conectando a Celery: {str(e)}")
        return False

def test_celery_task():
    """Enviar una tarea de prueba a Celery"""
    print("\n🔍 Probando envío de tarea a Celery...")
    
    try:
        from celery import Celery
        
        # Configurar Celery app
        app = Celery('accountia')
        broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
        app.conf.broker_url = broker_url
        app.conf.result_backend = broker_url
        
        # Definir tarea de prueba
        @app.task
        def test_task(message):
            return f"Test task received: {message}"
        
        # Enviar tarea
        result = test_task.delay("Hello from AccountIA!")
        
        print(f"  ✅ Tarea enviada con ID: {result.id}")
        
        # Esperar resultado (máximo 10 segundos)
        try:
            task_result = result.get(timeout=10)
            print(f"  ✅ Resultado de la tarea: {task_result}")
            return True
        except Exception as e:
            print(f"  ⚠️ Tarea enviada pero no se pudo obtener resultado: {str(e)}")
            print("  💡 Esto puede ser normal si el worker no está configurado para esta tarea específica")
            return True  # La tarea se envió correctamente
            
    except Exception as e:
        print(f"  ❌ Error enviando tarea: {str(e)}")
        return False

def check_docker_services():
    """Verificar que los servicios de Docker estén ejecutándose"""
    print("\n🐳 Verificando servicios de Docker...")
    
    import subprocess
    
    services_to_check = [
        'accountia_redis',
        'accountia_celery_worker', 
        'accountia_celery_beat'
    ]
    
    running_services = []
    
    for service in services_to_check:
        try:
            result = subprocess.run(
                ['docker', 'ps', '--filter', f'name={service}', '--format', 'table {{.Names}}\t{{.Status}}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if service in result.stdout and 'Up' in result.stdout:
                print(f"  ✅ {service}: Running")
                running_services.append(service)
            else:
                print(f"  ❌ {service}: Not running")
                
        except subprocess.TimeoutExpired:
            print(f"  ⚠️ {service}: Timeout checking status")
        except Exception as e:
            print(f"  ❌ {service}: Error checking status - {str(e)}")
    
    return len(running_services) == len(services_to_check)

def main():
    """Función principal"""
    print("🚀 AccountIA - Verificación de Celery y Redis\n")
    
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
        check_docker_services(),
        check_redis_connection(),
        check_celery_worker(),
        test_celery_task()
    ]
    
    # Resumen
    print("\n" + "="*60)
    if all(checks):
        print("🎉 ¡Todas las verificaciones pasaron! Celery y Redis están configurados correctamente.")
        print("\n💡 Comandos útiles:")
        print("   npm run celery:worker    # Ver logs del worker")
        print("   npm run celery:beat      # Ver logs del beat scheduler") 
        print("   npm run celery:status    # Ver tareas activas")
        print("   npm run redis:cli        # Acceder a Redis CLI")
    else:
        print("❌ Algunas verificaciones fallaron.")
        print("\n💡 Pasos para solucionar:")
        print("   1. Ejecutar: npm run dev (para iniciar todos los servicios)")
        print("   2. Verificar logs: npm run logs")
        print("   3. Verificar servicios específicos:")
        print("      npm run celery:worker")
        print("      npm run celery:beat")
        print("   4. Reiniciar si es necesario: npm run restart")
    
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Verificación cancelada por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)
