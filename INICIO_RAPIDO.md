# 🚀 Guía de Inicio Rápido - AccountIA

¡Bienvenido al proyecto AccountIA! Esta guía te ayudará a poner en marcha el entorno de desarrollo en minutos.

## ✅ Prerrequisitos

Antes de comenzar, asegúrate de tener instalado:

- **Docker Desktop** - [Descargar aquí](https://www.docker.com/products/docker-desktop/)
- **Node.js 16+** - [Descargar aquí](https://nodejs.org/)
- **Git** - [Descargar aquí](https://git-scm.com/)

## 🎯 Inicio en 3 Pasos

### Paso 1: Configurar Variables de Entorno
```bash
# Copia el archivo de ejemplo
cp .env.example .env

# Edita el archivo .env con tus configuraciones
# (puedes usar valores por defecto para empezar)
```

### Paso 2: Ejecutar Setup Automatizado
```bash
# Instalar dependencias npm
npm install

# Configuración completa automatizada
npm run setup
```

### Paso 3: Iniciar Desarrollo
```bash
npm run dev
```

¡Eso es todo! Tu aplicación estará corriendo en:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin

## 🛠️ Comandos Útiles

```bash
# Ver todos los comandos disponibles
npm run help

# Desarrollo diario
npm run dev            # Iniciar todos los servicios
npm run logs           # Ver logs en tiempo real
npm run stop           # Detener servicios
npm run restart        # Reiniciar servicios

# Base de datos
npm run db:migrate     # Ejecutar migraciones
npm run db:seed        # Cargar datos de prueba
npm run db:backup      # Crear backup
npm run user:create    # Crear superusuario Django

# Acceso a shells
npm run shell:backend  # Shell de Django
npm run shell:db       # Shell de PostgreSQL

# Testing y calidad
npm test               # Ejecutar todos los tests
npm run lint           # Verificar calidad de código
npm run format         # Formatear código

# Diagnóstico
npm run health         # Verificar estado de servicios
npm run debug          # Información detallada del sistema
```

## 📊 Servicios Disponibles

Una vez iniciado, tendrás acceso a:

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Frontend | http://localhost:3000 | Aplicación React |
| Backend API | http://localhost:8000 | API Django REST |
| Admin Django | http://localhost:8000/admin | Panel de administración |
| API Docs | http://localhost:8000/api/docs | Documentación Swagger |
| PgAdmin | http://localhost:5050 | Administrador PostgreSQL |
| MailHog | http://localhost:8025 | Capturador de emails |

## 🔧 Configuración Inicial

### 1. Crear Superusuario de Django
```bash
npm run user:create
```

### 2. Cargar Datos de Prueba
```bash
npm run db:seed
```

### 3. Configurar Firebase (Opcional)
1. Crea un proyecto en [Firebase Console](https://console.firebase.google.com/)
2. Habilita Authentication
3. Actualiza las variables `VITE_FIREBASE_*` en tu `.env`

### 4. Configurar Google Cloud (Para IA)
1. Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilita Vertex AI API
3. Descarga las credenciales JSON
4. Actualiza `GOOGLE_APPLICATION_CREDENTIALS` en tu `.env`

## 🐛 Solución de Problemas

### Docker no inicia
```bash
# Verificar que Docker Desktop esté corriendo
docker --version

# Limpiar y reiniciar
npm run clean
npm run setup
```

### Servicios no responden
```bash
# Verificar estado de servicios
npm run health

# Ver logs para diagnosticar
npm run logs

# Información detallada del sistema
npm run debug
```

### Base de datos no conecta
```bash
# Reiniciar servicios de BD
npm run stop
npm run dev

# Verificar migraciones
npm run db:migrate
```

### Puertos ocupados
Si tienes conflictos de puertos, puedes cambiarlos en `docker-compose.yml`:
- Frontend: puerto 3000 → 3001
- Backend: puerto 8000 → 8001
- PostgreSQL: puerto 5432 → 5433

### Problemas de permisos (Linux/Mac)
```bash
# Dar permisos a los scripts
chmod +x scripts/*.sh
```

### Limpiar completamente
```bash
# Limpiar todo y empezar de nuevo
npm run clean
npm run setup
```

## 💻 Desarrollo Local (Sin Docker)

Si prefieres desarrollar sin Docker:

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 📚 Próximos Pasos

1. **Explora la documentación**: 
   - `README.md` - Documentación completa
   - `INDICE_ARCHIVOS.md` - Navegación de archivos
   - `/docs` - Documentación técnica detallada

2. **Examina el código**:
   - `/frontend/src` - Estructura React
   - `/backend/apps` - Módulos Django
   - `/ai_knowledge` - Base de conocimiento IA

3. **Ejecuta los tests**:
   ```bash
   npm test
   ```

4. **Explora las APIs**:
   - Visita http://localhost:8000/api/docs
   - Prueba endpoints en http://localhost:8000/admin

## 🆘 Obtener Ayuda

### Comandos de Diagnóstico
```bash
npm run help           # Lista completa de comandos
npm run health         # Estado de servicios
npm run debug          # Información del sistema
npm run logs           # Logs detallados
```

### Documentación
- **Documentación completa**: Ver `README.md`
- **Estructura de archivos**: Ver `INDICE_ARCHIVOS.md`
- **Documentación técnica**: Ver carpeta `/docs`

### Solución Rápida de Problemas
1. `npm run health` - ¿Están todos los servicios funcionando?
2. `npm run debug` - ¿Hay problemas de configuración?
3. `npm run logs` - ¿Qué dicen los logs?
4. `npm run clean && npm run setup` - Reiniciar todo

## 🎉 ¡Listo para Desarrollar!

Una vez que todo esté funcionando:

```bash
# Verificar que todo está bien
npm run health

# Iniciar desarrollo
npm run dev

# En otra terminal, ver logs
npm run logs
```

---

**¡Feliz desarrollo con AccountIA! 🇨🇴🚀**

💡 **Tip**: Usa `npm run help` para ver todos los comandos disponibles en cualquier momento.