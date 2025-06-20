# 📋 Índice de Archivos Principales - AccountIA

Esta guía te ayuda a navegar rápidamente por los archivos más importantes del proyecto.

## 🚀 Archivos de Inicio

| Archivo | Descripción | Cuándo usarlo |
|---------|-------------|---------------|
| `INICIO_RAPIDO.md` | Guía de inicio para nuevos desarrolladores | Primera vez configurando el proyecto |
| `README.md` | Documentación principal del proyecto | Referencia general y comandos |
| `package.json` | Configuración npm y scripts del proyecto | Comandos principales (`npm run help`) |
| `setup.ps1` | Script de configuración para Windows | Setup automatizado en Windows |
| `scripts/setup.sh` | Script de configuración para Linux/Mac | Setup automatizado en Unix |

## ⚙️ Configuración

| Archivo | Descripción | Acción requerida |
|---------|-------------|-------------------|
| `.env.example` | Template de variables de entorno | Copiar a `.env` y personalizar |
| `docker-compose.yml` | Configuración de servicios | Revisar puertos si hay conflictos |
| `LICENSE` | Licencia del proyecto | Revisar términos legales |

## 📝 Scripts NPM

| Script | Comando | Descripción |
|--------|---------|-------------|
| **Setup** | `npm run setup` | Configuración inicial automatizada |
| **Desarrollo** | `npm run dev` | Iniciar entorno de desarrollo |
| **Ayuda** | `npm run help` | Ver todos los comandos disponibles |
| **Testing** | `npm test` | Ejecutar todos los tests |
| **Logs** | `npm run logs` | Ver logs de servicios |
| **Salud** | `npm run health` | Verificar estado de servicios |

### Scripts Adicionales

| Categoría | Comandos Principales |
|-----------|---------------------|
| **Base de Datos** | `npm run db:migrate`, `npm run db:backup`, `npm run user:create` |
| **Calidad** | `npm run lint`, `npm run format` |
| **IA** | `npm run ai:update-kb`, `npm run ai:test` |
| **Deploy** | `npm run build`, `npm run deploy:dev` |
| **Debug** | `npm run debug`, `npm run clean` |

## 🔧 Backend (Django)

| Archivo | Descripción | Importancia |
|---------|-------------|-------------|
| `backend/manage.py` | Punto de entrada de Django | ⭐⭐⭐ Critical |
| `backend/requirements.txt` | Dependencias Python | ⭐⭐⭐ Critical |
| `backend/config/urls.py` | Configuración de URLs principales | ⭐⭐⭐ Critical |
| `backend/config/asgi.py` | Configuración ASGI para deployment | ⭐⭐ Important |
| `backend/Dockerfile` | Imagen Docker del backend | ⭐⭐ Important |
| `backend/apps/authentication/apps.py` | Configuración del módulo auth | ⭐⭐ Important |

## 🎨 Frontend (React)

| Archivo | Descripción | Importancia |
|---------|-------------|-------------|
| `frontend/package.json` | Dependencias y scripts npm | ⭐⭐⭐ Critical |
| `frontend/index.html` | HTML principal | ⭐⭐⭐ Critical |
| `frontend/vite.config.js` | Configuración de Vite | ⭐⭐⭐ Critical |
| `frontend/tailwind.config.js` | Configuración de estilos | ⭐⭐⭐ Critical |
| `frontend/tsconfig.json` | Configuración TypeScript | ⭐⭐ Important |
| `frontend/Dockerfile` | Imagen Docker del frontend | ⭐⭐ Important |

## 🗄️ Base de Datos

| Archivo | Descripción | Uso |
|---------|-------------|-----|
| `database/scripts/init-database.sql` | Script de inicialización | Configuración inicial de PostgreSQL |

## 📚 Documentación

| Archivo | Descripción | Audiencia |
|---------|-------------|-----------|
| `docs/README.md` | Índice de documentación | Todo el equipo |
| `docs/user-stories/mvp-stories.md` | Historias de usuario del MVP | Product Owner, Developers |

## 🤖 Inteligencia Artificial

| Archivo | Descripción | Equipo responsable |
|---------|-------------|-------------------|
| `ai_knowledge/README.md` | Guía de la base de conocimiento | AI/ML Engineers |

## 🛠️ Scripts de Automatización

| Archivo | Descripción | Uso |
|---------|-------------|-----|
| `scripts/setup.js` | Setup automatizado en Node.js | `npm run setup` |
| `scripts/help.js` | Mostrar ayuda de comandos | `npm run help` |
| `scripts/health-check.js` | Verificar estado de servicios | `npm run health` |
| `scripts/debug-info.js` | Información de debug | `npm run debug` |
| `scripts/backup-db.js` | Backup de base de datos | `npm run db:backup` |
| `scripts/restore-db.js` | Restaurar base de datos | `npm run db:restore` |

## 🔍 Cómo Usar Este Índice

### Para nuevos desarrolladores:
1. Comienza con `INICIO_RAPIDO.md`
2. Ejecuta `npm install && npm run setup`
3. Inicia desarrollo con `npm run dev`
4. Usa `npm run help` para ver todos los comandos
5. Revisa `backend/config/urls.py` para entender las rutas
6. Explora `frontend/src/` para la estructura del UI

### Para configurar entornos:
1. Personaliza `.env` según el entorno
2. Ajusta `docker-compose.yml` si es necesario
3. Revisa `backend/requirements.txt` para dependencias
4. Configura variables `VITE_*` en `.env` para el frontend

### Para desarrollo diario:
```bash
npm run dev           # Iniciar desarrollo
npm run logs          # Ver logs
npm run health        # Verificar servicios
npm test              # Ejecutar tests
npm run lint          # Verificar calidad
```

### Para deployment:
```bash
npm run build         # Construir imágenes
npm run deploy:dev    # Deploy a desarrollo
npm run deploy:prod   # Deploy a producción
```

### Para desarrollo de IA:
1. Revisa `ai_knowledge/README.md`
2. Configura API keys de Google/OpenAI en `.env`
3. Usa `npm run ai:update-kb` para actualizar conocimiento
4. Explora `backend/apps/ai_core/`

## 🆘 Si Algo No Funciona

### Diagnóstico Paso a Paso:
```bash
# 1. Verificar estado general
npm run health

# 2. Ver información detallada
npm run debug

# 3. Revisar logs
npm run logs

# 4. Limpiar y reiniciar
npm run clean
npm run setup
```

### Problemas Comunes:

**Error de Docker**: 
```bash
# Verifica que Docker Desktop esté corriendo
docker --version
npm run health
```

**Error de puertos**: 
- Cambia puertos en `docker-compose.yml`
- O detén otros servicios que usen los mismos puertos

**Error de dependencias**: 
```bash
npm run clean
npm install
npm run setup
```

**Error de permisos** (Unix): 
```bash
chmod +x scripts/*.sh
chmod +x scripts/*.js
```

## 💡 **Comandos Más Usados**

```bash
# Setup inicial (solo una vez)
npm install
npm run setup

# Desarrollo diario
npm run dev
npm run health
npm run logs

# Base de datos
npm run db:migrate
npm run user:create
npm run db:backup

# Testing y calidad
npm test
npm run lint

# Ayuda y debug
npm run help
npm run debug
```

---

💡 **Tip**: Mantén abierta una terminal con `npm run logs` mientras desarrollas para ver la actividad en tiempo real.