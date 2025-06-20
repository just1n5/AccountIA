# 🔄 Procesamiento Asíncrono con Celery y Redis

## 📋 Servicios Configurados

### ✅ **Redis** (Broker de mensajes)
- **Imagen**: `redis:7-alpine`
- **Puerto**: `6379`
- **Contenedor**: `accountia_redis`
- **Función**: Actúa como broker para las tareas de Celery

### ✅ **Celery Worker** (Procesador de tareas)
- **Contenedor**: `accountia_celery_worker`
- **Función**: Ejecuta tareas en segundo plano (parseo de Excel, análisis IA)

### ✅ **Celery Beat** (Programador de tareas)
- **Contenedor**: `accountia_celery_beat`
- **Función**: Ejecuta tareas programadas (limpieza, reportes)

---

## 🚀 **Comandos Útiles**

### **Gestión General**
```bash
# Iniciar todos los servicios
npm run dev

# Ver logs de todos los servicios
npm run logs

# Reiniciar servicios
npm run restart
```

### **Monitoreo de Celery**
```bash
# Ver logs del worker
npm run celery:worker

# Ver logs del beat scheduler
npm run celery:beat

# Verificar tareas activas
npm run celery:status

# Probar Celery y Redis
npm run celery:test
```

### **Redis**
```bash
# Acceder a Redis CLI
npm run redis:cli

# Monitorear comandos en tiempo real
npm run redis:monitor
```

---

## 🔧 **Configuración**

### **Variables de Entorno Importantes**
```env
# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Google Cloud (para procesamiento de archivos)
GOOGLE_CLOUD_PROJECT=accountia-dev-0001
GCS_BUCKET_NAME=accountia-dev-documents-0001
GOOGLE_APPLICATION_CREDENTIALS=/app/config/credentials/google-cloud-credentials.json
```

### **Archivos de Configuración**
- `backend/config/celery.py` - Configuración principal de Celery
- `backend/apps/documents/tasks.py` - Tareas específicas (parseo Excel)
- `docker-compose.yml` - Definición de servicios

---

## 📝 **Tipos de Tareas**

### **Procesamiento de Documentos**
```python
# Tarea principal para procesar archivos Excel
@shared_task(bind=True, max_retries=3)
def process_exogena_file(self, document_id):
    # 1. Descargar archivo de GCS
    # 2. Parsear con pandas/openpyxl
    # 3. Extraer y clasificar datos
    # 4. Actualizar base de datos
```

### **Análisis con IA**
```python
# Análisis inteligente de datos fiscales
@shared_task
def analyze_tax_data(declaration_id):
    # 1. Obtener datos procesados
    # 2. Aplicar RAG para recomendaciones
    # 3. Generar insights
```

---

## 🐛 **Troubleshooting**

### **Problema: Worker no inicia**
```bash
# Verificar logs
npm run celery:worker

# Verificar que Redis esté corriendo
npm run redis:cli
> ping
PONG

# Reiniciar servicios
npm run restart
```

### **Problema: Tareas no se procesan**
```bash
# Verificar tareas activas
npm run celery:status

# Verificar configuración
npm run celery:test

# Ver logs en tiempo real
npm run logs
```

### **Problema: Redis no conecta**
```bash
# Verificar estado del contenedor
docker ps | grep redis

# Verificar configuración
npm run health

# Limpiar y reiniciar
npm run clean && npm run dev
```

---

## 📊 **Monitoreo Avanzado**

### **Flower (Web UI para Celery)**
```bash
# Iniciar Flower (opcional)
npm run celery:monitor

# Acceder a: http://localhost:5555
```

### **Redis Commander (Web UI para Redis)**
```bash
# Agregar al docker-compose.yml si necesitas UI web para Redis
```

---

## 🔐 **Seguridad**

### **Credenciales de Google Cloud**
- ✅ Archivo protegido por `.gitignore`
- ✅ Montado como volumen de solo lectura (`:ro`)
- ✅ Accesible en `/app/config/credentials/` dentro del contenedor

### **Variables Sensibles**
- ✅ Todas las variables sensibles están en `.env` (protegido)
- ✅ Redis configurado solo para acceso interno
- ✅ Celery configurado con serialización JSON segura

---

## 📈 **Performance**

### **Configuración Optimizada**
```python
# Configuración en config/celery.py
CELERY_TASK_ALWAYS_EAGER = False  # Procesar asíncronamente
CELERY_TASK_SERIALIZER = 'json'   # Serialización rápida
CELERY_TIMEZONE = 'America/Bogota'  # Zona horaria Colombia
```

### **Límites Recomendados**
- **Worker concurrency**: 4 (por defecto)
- **Task timeout**: 300 segundos (5 minutos)
- **Max retries**: 3 intentos

---

## ✅ **Verificación Rápida**

```bash
# Verificar que todo esté funcionando
npm run celery:test

# Debería mostrar:
# ✅ Redis funcionando
# ✅ Workers activos  
# ✅ Tarea de prueba exitosa
```

¡Tu sistema de procesamiento asíncrono está listo para manejar archivos Excel y análisis de IA! 🚀
