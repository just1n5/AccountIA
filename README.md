# AccountIA - Asesor Tributario Inteligente

![AccountIA Logo](frontend/public/logo.svg)

**Tu declaración de renta, por fin simple.**

AccountIA es una plataforma inteligente que utiliza IA para simplificar el proceso de declaración de renta en Colombia. Transformamos un proceso tradicionalmente complejo en una experiencia guiada, clara y confiable.

## 🎯 Propuesta de Valor

- **Simple**: Sube tu información exógena y déjanos hacer el trabajo pesado
- **Inteligente**: IA especializada en normativa fiscal colombiana
- **Seguro**: Cumplimiento estricto con la Ley 1581 de 2012 (Habeas Data)
- **Optimizado**: Identifica deducciones y beneficios que podrías estar perdiendo

## 🏗️ Arquitectura del Proyecto

### Stack Tecnológico

- **Frontend**: React.js + TypeScript + Tailwind CSS + Vite
- **Backend**: Python + Django + Django REST Framework
- **Base de Datos**: PostgreSQL
- **IA**: Google Gemini con RAG (Retrieval-Augmented Generation)
- **Autenticación**: Firebase Authentication
- **Almacenamiento**: Google Cloud Storage
- **Infraestructura**: Google Cloud Platform
- **Contenerización**: Docker + Docker Compose

### Estructura de Carpetas

```
accountia/
├── frontend/          # Aplicación React
├── backend/           # API Django
├── database/          # Scripts y configuración de BD
├── ai_knowledge/      # Base de conocimiento para IA
├── infrastructure/    # Configuración de deployment
├── docs/             # Documentación del proyecto
├── tests/            # Tests de integración y E2E
└── scripts/          # Scripts de automatización (Node.js)
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Docker y Docker Compose
- Node.js 16+ (para scripts npm)
- Git

### Configuración del Entorno de Desarrollo

1. **Configura las variables de entorno**
   ```bash
   cp .env.example .env
   # Edita .env con tus configuraciones locales
   ```

2. **Ejecuta el setup automatizado**
   ```bash
   npm run setup
   ```

3. **Inicia el entorno de desarrollo**
   ```bash
   npm run dev
   ```

4. **Accede a la aplicación**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin Django: http://localhost:8000/admin

### Comandos Útiles

```bash
# Desarrollo
npm run dev           # Inicia todos los servicios
npm run help          # Ver todos los comandos disponibles
npm test              # Ejecuta todos los tests
npm run logs          # Ver logs de servicios
npm run health        # Verificar estado de servicios

# Base de datos
npm run db:migrate    # Ejecuta migraciones
npm run db:seed       # Carga datos de prueba
npm run db:backup     # Crea backup de la BD
npm run db:restore    # Restaura backup
npm run user:create   # Crear superusuario Django

# Calidad de código
npm run lint          # Verifica calidad de código
npm run format        # Formatea el código

# IA y Conocimiento
npm run ai:update-kb  # Actualiza base de conocimiento de IA
npm run ai:test       # Prueba funcionalidades de IA

# Deployment
npm run build         # Construir imágenes
npm run deploy:dev    # Deploy a desarrollo
npm run deploy:prod   # Deploy a producción
```

## 📁 Descripción de Módulos

### Frontend (`/frontend`)

Aplicación React con TypeScript que implementa la interfaz de usuario siguiendo nuestro sistema de diseño.

**Características principales:**
- Diseño responsivo con Tailwind CSS
- Autenticación con Firebase
- Gestión de estado con Zustand
- Tests con Vitest y Testing Library

### Backend (`/backend`)

API RESTful construida con Django que maneja la lógica de negocio y la integración con servicios externos.

**Módulos principales:**
- `authentication/`: Manejo de usuarios y autenticación
- `declarations/`: Lógica de declaraciones de renta
- `documents/`: Gestión de documentos y archivos
- `ai_core/`: Integración con IA y servicios de análisis
- `payments/`: Procesamiento de pagos

### Base de Conocimiento IA (`/ai_knowledge`)

Repositorio de documentos legales y fiscales procesados para el sistema RAG.

**Contenido:**
- Estatuto Tributario colombiano
- Conceptos unificados DIAN
- Decretos y reglamentaciones
- Embeddings y índices vectoriales

## 🔧 Desarrollo

### Configuración Inicial

```bash
# Setup completo
npm run setup

# Solo instalar dependencias
npm run install:frontend
npm run install:backend
```

### Desarrollo Diario

```bash
# Iniciar desarrollo
npm run dev

# Ver logs en tiempo real
npm run logs

# Acceder a shells
npm run shell:backend    # Django shell
npm run shell:db        # PostgreSQL shell
```

### Testing

```bash
npm test                # Todos los tests
npm run test:backend    # Tests de Django
npm run test:frontend   # Tests de React
npm run test:coverage   # Con reporte de cobertura
npm run test:e2e        # Tests end-to-end
```

## 📊 Monitoreo y Observabilidad

- **Logs**: Estructurados en JSON para análisis
- **Health Checks**: `npm run health` para verificar servicios
- **Métricas**: `npm run monitoring` para Prometheus + Grafana
- **Debug**: `npm run debug` para información del sistema

## 🔐 Seguridad

### Implementadas
- ✅ Cifrado en tránsito (HTTPS/TLS)
- ✅ Cifrado en reposo (BD y archivos)
- ✅ Autenticación robusta (Firebase + JWT)
- ✅ Validación de entrada
- ✅ Principio de menor privilegio
- ✅ Cumplimiento Ley 1581 de 2012

### Comandos de Seguridad
```bash
npm run lint            # Verificar calidad y seguridad del código
npm run format          # Aplicar estándares de formato
```

## 🚀 Deployment

### Entornos

1. **Development**: `dev.accountia.co`
2. **Staging**: `staging.accountia.co`
3. **Production**: `app.accountia.co`

### Comandos de Deploy

```bash
npm run build           # Construir imágenes
npm run deploy:dev      # Deploy a desarrollo
npm run deploy:staging  # Deploy a staging
npm run deploy:prod     # Deploy a producción
```

## 📖 Documentación

- [API Documentation](docs/api/endpoints.md)
- [Architecture Overview](docs/architecture/system-overview.md)
- [Database Schema](docs/architecture/database-schema.md)
- [Security Guidelines](docs/architecture/security-guidelines.md)
- [User Stories](docs/user-stories/mvp-stories.md)
- [Guía de Inicio Rápido](INICIO_RAPIDO.md)
- [Índice de Archivos](INDICE_ARCHIVOS.md)

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

### Estándares de Código

- **Python**: PEP 8, Black, isort, mypy
- **JavaScript/TypeScript**: ESLint, Prettier
- **Commits**: Conventional Commits
- **Tests**: Cobertura mínima 80%

```bash
# Verificar estándares
npm run lint

# Aplicar formato
npm run format
```

## 🆘 Solución de Problemas

### Comandos de Diagnóstico
```bash
npm run health          # Verificar estado de servicios
npm run debug           # Información detallada del sistema
npm run logs            # Ver logs de todos los servicios
```

### Problemas Comunes

**Servicios no inician:**
```bash
npm run clean           # Limpiar contenedores
npm run setup           # Reconfigurar
```

**Errores de base de datos:**
```bash
npm run db:backup       # Hacer backup
npm run db:migrate      # Ejecutar migraciones
```

**Problemas de desarrollo:**
```bash
npm run restart         # Reiniciar servicios
npm run logs:backend    # Ver logs específicos
npm run logs:frontend   # Ver logs del frontend
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

## 👥 Equipo

- **Product Owner**: [Nombre]
- **Tech Lead**: [Nombre]
- **Frontend Developer**: [Nombre]
- **Backend Developer**: [Nombre]
- **DevOps Engineer**: [Nombre]

## 📞 Soporte

- **Email**: soporte@accountia.co
- **Documentación**: [docs.accountia.co](https://docs.accountia.co)
- **Issues**: [GitHub Issues](https://github.com/tu-org/accountia/issues)

---

**AccountIA** - Simplificando las finanzas personales en Colombia 🇨🇴

## 💡 Comandos Rápidos de Referencia

```bash
# Setup inicial
npm run setup

# Desarrollo diario  
npm run dev
npm run logs
npm run health

# Base de datos
npm run db:migrate
npm run db:backup
npm run user:create

# Testing
npm test
npm run test:coverage

# Calidad
npm run lint
npm run format

# Ayuda
npm run help
```