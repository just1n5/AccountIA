# AccountIA - Sprint 2: Backend de Documentos y Procesamiento

## 🚀 Cambios Implementados

### Backend
- ✅ **Modelos de Datos**: Declaration, IncomeRecord, Document
- ✅ **Parser de Excel**: Procesamiento robusto de archivos de información exógena
- ✅ **Servicio de Storage**: Integración con Google Cloud Storage y almacenamiento local
- ✅ **APIs RESTful**: Endpoints completos para declaraciones y documentos
- ✅ **Tareas Asíncronas**: Procesamiento en background con Celery
- ✅ **Admin Django**: Interfaces de administración completas

### Frontend
- ✅ **Componentes de Carga**: FileUpload con drag & drop
- ✅ **Wizard de Declaración**: Flujo paso a paso interactivo
- ✅ **Visualización de Datos**: DataReview con estadísticas
- ✅ **Carga de Documentos**: Soporte para múltiples archivos
- ✅ **Vista de Borrador**: Preview completo de la declaración
- ✅ **Dashboard**: Panel principal con historial

### Infraestructura
- ✅ **Autenticación Firebase**: Integración completa
- ✅ **Servicio API**: Cliente HTTP con interceptores
- ✅ **Sistema de Diseño**: Componentes UI consistentes
- ✅ **Tests**: Suite de pruebas para el parser

## 📋 Instalación Rápida

### 1. Backend
```bash
cd backend

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

### 2. Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Firebase

# Iniciar servidor de desarrollo
npm run dev
```

### 3. Servicios Adicionales
```bash
# Redis (para Celery)
docker run -d -p 6379:6379 redis:alpine

# Celery Worker
cd backend
celery -A config worker -l info
```

## 🔧 Configuración

### Variables de Entorno Backend (.env)
```env
# Base de datos
DATABASE_URL=postgresql://accountia_user:accountia_password@localhost:5432/accountia_dev

# Firebase Admin
FIREBASE_CREDENTIALS_PATH=path/to/firebase-admin-sdk.json

# Google Cloud Storage (opcional para desarrollo)
GCS_BUCKET_NAME=accountia-dev-documents
GOOGLE_APPLICATION_CREDENTIALS=path/to/gcs-credentials.json

# Desarrollo
DEBUG=True
USE_GOOGLE_CLOUD_STORAGE=False  # Usar almacenamiento local
```

### Variables de Entorno Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
VITE_FIREBASE_API_KEY=tu-api-key
VITE_FIREBASE_AUTH_DOMAIN=tu-proyecto.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=tu-proyecto
VITE_FIREBASE_STORAGE_BUCKET=tu-proyecto.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=tu-app-id
```

## 🧪 Testing

### Backend
```bash
cd backend

# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=apps

# Test específico
pytest apps/documents/tests/test_excel_parser.py -v
```

### Frontend
```bash
cd frontend

# Tests unitarios
npm test

# Tests E2E
npm run test:e2e
```

## 📱 Uso de la Aplicación

### 1. Registro/Login
- Acceder a http://localhost:3000
- Registrarse con email/contraseña o Google
- Confirmar email si es necesario

### 2. Crear Declaración
- En el dashboard, click en "Crear Declaración [Año]"
- Se creará una declaración en estado borrador

### 3. Wizard de Declaración
1. **Carga de Exógena**: Subir archivo Excel de la DIAN
2. **Revisión de Datos**: Verificar ingresos y retenciones procesados
3. **Documentos de Soporte**: Adjuntar facturas y certificados
4. **Borrador Final**: Revisar declaración completa

### 4. Procesamiento
- Los archivos se procesan de forma asíncrona
- Se notifica el progreso en tiempo real
- Los errores se muestran claramente

## 🛠️ Comandos Útiles

### NPM Scripts
```bash
# Desarrollo completo
npm run dev:all        # Inicia backend + frontend + servicios

# Backend
npm run backend:start  # Django server
npm run backend:migrate # Migraciones
npm run backend:test   # Tests

# Frontend  
npm run frontend:dev   # Servidor Vite
npm run frontend:build # Build producción
npm run frontend:test  # Tests

# Servicios
npm run redis:start    # Redis
npm run celery:start   # Worker
```

## 📊 API Endpoints

### Declaraciones
- `GET /api/v1/declarations/` - Listar declaraciones
- `POST /api/v1/declarations/` - Crear declaración
- `GET /api/v1/declarations/{id}/` - Detalle declaración
- `POST /api/v1/declarations/{id}/process_documents/` - Procesar documentos
- `GET /api/v1/declarations/{id}/income_summary/` - Resumen de ingresos

### Documentos
- `POST /api/v1/declarations/{id}/documents/initiate_upload/` - Iniciar carga
- `PUT /api/v1/documents/{id}/update_status/` - Actualizar estado
- `GET /api/v1/documents/{id}/download_url/` - URL de descarga
- `GET /api/v1/documents/{id}/processed_data/` - Datos procesados

## 🐛 Solución de Problemas

### Error: "No module named 'apps'"
```bash
cd backend
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### Error: "Firebase credentials not found"
1. Descargar credenciales desde Firebase Console
2. Guardar en `backend/credentials/`
3. Actualizar path en .env

### Error: "Celery connection refused"
```bash
# Verificar que Redis esté corriendo
docker ps | grep redis

# Si no está corriendo
docker run -d -p 6379:6379 redis:alpine
```

## 📝 Próximos Pasos

### Sprint 3: Motor de IA y RAG
- [ ] Implementar base de conocimiento fiscal
- [ ] Integrar Gemini para análisis
- [ ] Sistema de recomendaciones
- [ ] Chat conversacional

### Sprint 4: Pagos y Generación
- [ ] Integración con Stripe
- [ ] Generación de PDF Formulario 210
- [ ] Sistema de notificaciones
- [ ] Optimizaciones de rendimiento

## 🤝 Contribuir

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Este proyecto es privado y confidencial. Todos los derechos reservados.