# 🔧 Solución de Problemas - AccountIA

## ❌ **Problemas que acabas de experimentar y sus soluciones:**

### 1. **Error: "no such file or directory, open '...common\__init__.py'"**

**✅ SOLUCIONADO** - Era un problema en el script de setup que intentaba crear archivos en directorios que no existían.

**Qué se arregló:**
- Se crearon todos los directorios faltantes
- Se mejoró el script de setup para crear directorios antes de archivos
- Se añadieron validaciones para evitar estos errores

### 2. **Error: "unable to get image 'accountia-celery_beat'"**

**Causa:** Docker Desktop no está ejecutándose o hay problemas de conectividad.

**Soluciones:**

#### ✅ **Paso 1: Verificar Docker Desktop**
```bash
# Verificar que Docker esté corriendo
docker --version
docker info
```

#### ✅ **Paso 2: Iniciar Docker Desktop**
1. Abrir Docker Desktop desde el menú de inicio
2. Esperar a que aparezca "Engine running" en verde
3. Verificar que no haya errores en la interfaz

#### ✅ **Paso 3: Ejecutar setup actualizado**
```bash
# El setup mejorado ahora verifica Docker antes de continuar
npm run setup
```

#### ✅ **Paso 4: Iniciar servicios**
```bash
npm run dev
```

## 🛠️ **Problemas Comunes y Soluciones**

### **Docker Desktop no inicia**
```bash
# 1. Reiniciar Docker Desktop completamente
# 2. Verificar recursos del sistema (mínimo 4GB RAM)
# 3. En Windows: verificar que WSL2 esté habilitado
# 4. Ejecutar como administrador si es necesario
```

### **Puertos ocupados**
```bash
# Verificar qué está usando los puertos
netstat -ano | findstr :3000
netstat -ano | findstr :8000
netstat -ano | findstr :5432

# Cambiar puertos en docker-compose.yml si es necesario
```

### **Problemas de construcción de imágenes**
```bash
# Limpiar todo Docker y empezar de nuevo
npm run clean
docker system prune -a
npm run setup
```

### **Base de datos no conecta**
```bash
# Verificar estado de PostgreSQL
npm run health
npm run logs:backend

# Reiniciar servicios de BD
docker-compose restart postgres redis
```

### **Frontend no carga**
```bash
# Verificar logs del frontend
npm run logs:frontend

# Reconstruir imagen del frontend
docker-compose build frontend
npm run restart
```

## ✅ **Comandos de Diagnóstico**

### **Verificación completa del sistema**
```bash
npm run debug       # Información detallada del sistema
npm run health      # Estado de todos los servicios
npm run logs        # Logs de todos los servicios
```

### **Verificación específica**
```bash
docker ps                           # Contenedores ejecutándose
docker-compose ps                   # Estado de servicios AccountIA
docker system df                    # Uso de espacio Docker
docker-compose logs backend         # Logs específicos del backend
```

## 🚨 **Soluciones de Emergencia**

### **Resetear todo completamente**
```bash
# ADVERTENCIA: Esto eliminará todos los datos locales
npm run clean
docker system prune -a -f
docker volume prune -f
npm run setup
```

### **Problemas de permisos (Windows)**
```bash
# Ejecutar PowerShell como Administrador
# Verificar que Docker Desktop tenga permisos
# Verificar que la carpeta del proyecto no esté en OneDrive
```

### **Problemas de WSL2 (Windows)**
```bash
# Verificar WSL2
wsl --list --verbose

# Actualizar WSL2 si es necesario
wsl --update
```

## 📞 **Cómo Obtener Ayuda**

### **1. Información de Debug**
```bash
npm run debug > debug_output.txt
# Comparte este archivo si necesitas ayuda
```

### **2. Logs Detallados**
```bash
npm run logs > logs_output.txt
# Incluye estos logs al reportar problemas
```

### **3. Estado del Sistema**
```bash
npm run health
# Toma una captura de pantalla de la salida
```

## 💡 **Consejos de Prevención**

### **Antes de empezar desarrollo diario:**
```bash
npm run health      # Verificar que todo esté bien
npm run dev         # Iniciar servicios
```

### **Si algo funciona mal:**
```bash
npm run debug       # Ver qué está pasando
npm run logs        # Ver logs detallados
npm run restart     # Reiniciar servicios
```

### **Mantenimiento regular:**
```bash
# Una vez por semana
npm run clean       # Limpiar contenedores viejos
npm run setup       # Verificar configuración
```

---

## 🎯 **Para continuar desde donde te quedaste:**

```bash
# 1. Verificar que Docker Desktop esté ejecutándose
# 2. Ejecutar el setup actualizado
npm run setup

# 3. Iniciar desarrollo
npm run dev

# 4. Verificar que todo funcione
npm run health
```

**¡El proyecto ahora debería funcionar perfectamente! 🚀**