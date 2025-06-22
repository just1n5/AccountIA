# 🔧 Guía de Configuración de Variables de Entorno - AccountIA

## 📋 Índice
1. [Configuración de Firebase](#1-configuración-de-firebase)
2. [Configuración del Backend](#2-configuración-del-backend)
3. [Configuración del Frontend](#3-configuración-del-frontend)
4. [Configuración de la Base de Datos](#4-configuración-de-la-base-de-datos)
5. [Configuración de Redis](#5-configuración-de-redis)
6. [Verificación](#6-verificación)

---

## 1. Configuración de Firebase

### Paso 1: Crear un proyecto en Firebase
1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Click en "Crear proyecto"
3. Nombre: `accountia-dev` (o el nombre que prefieras)
4. Desactiva Google Analytics por ahora (opcional)
5. Click en "Crear proyecto"

### Paso 2: Configurar Authentication
1. En el menú lateral, ve a "Authentication"
2. Click en "Comenzar"
3. En la pestaña "Sign-in method", habilita:
   - Email/Password
   - Google (opcional pero recomendado)

### Paso 3: Obtener configuración para el Frontend
1. Ve a "Configuración del proyecto" (engranaje en el menú)
2. En la sección "Tus aplicaciones", click en el icono Web (`</>`)
3. Registra tu app:
   - Nombre: `AccountIA Web`
   - NO marques "Firebase Hosting" por ahora
4. Copia la configuración que aparece:

```javascript
const firebaseConfig = {
  apiKey: "AIza...",
  authDomain: "accountia-dev.firebaseapp.com",
  projectId: "accountia-dev",
  storageBucket: "accountia-dev.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abcdef"
};
```

### Paso 4: Obtener credenciales para el Backend
1. En "Configuración del proyecto", ve a "Cuentas de servicio"
2. Click en "Generar nueva clave privada"
3. Se descargará un archivo JSON
4. Guarda este archivo en `backend/credentials/firebase-admin-sdk.json`

---

## 2. Configuración del Backend

### Paso 1: Copiar el archivo de ejemplo
```bash
cd backend
cp .env.example .env
```

### Paso 2: Editar el archivo .env

```env
# Variables mínimas necesarias para desarrollo:

# Básicos
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=dev-secret-key-accountia-2024-change-in-production

# Base de datos (ajusta según tu configuración)
DATABASE_URL=postgresql://accountia_user:accountia_password@localhost:5432/accountia_dev

# Firebase
FIREBASE_CREDENTIALS_PATH=./credentials/firebase-admin-sdk.json

# Redis (para Celery)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# CORS (permite el frontend)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Almacenamiento (False = usa almacenamiento local)
USE_GOOGLE_CLOUD_STORAGE=False
```

### Paso 3: Crear directorio de credenciales
```bash
mkdir -p backend/credentials
```

### Paso 4: Copiar el archivo de Firebase
Copia el archivo JSON descargado de Firebase a:
```
backend/credentials/firebase-admin-sdk.json
```

---

## 3. Configuración del Frontend

### Paso 1: Copiar el archivo de ejemplo
```bash
cd frontend
cp .env.example .env
```

### Paso 2: Editar el archivo .env
Usa los valores que copiaste de Firebase Console:

```env
# Backend API
VITE_API_URL=http://localhost:8000

# Firebase (reemplaza con tus valores)
VITE_FIREBASE_API_KEY=AIzaSyDtN8k9V5rB2tO8PqK6FmEJT7Q8bXw2kPo
VITE_FIREBASE_AUTH_DOMAIN=accountia-dev.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=accountia-dev
VITE_FIREBASE_STORAGE_BUCKET=accountia-dev.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=892041962752
VITE_FIREBASE_APP_ID=1:892041962752:web:6a5d8e4f3c2b1a3d4e5f6

# Entorno
VITE_APP_ENV=development
```

---

## 4. Configuración de la Base de Datos

### Opción A: PostgreSQL Local

1. **Instalar PostgreSQL**:
   - Windows: Descarga desde [postgresql.org](https://www.postgresql.org/download/windows/)
   - Mac: `brew install postgresql`
   - Linux: `sudo apt-get install postgresql`

2. **Crear base de datos y usuario**:
```sql
sudo -u postgres psql

CREATE USER accountia_user WITH PASSWORD 'accountia_password';
CREATE DATABASE accountia_dev OWNER accountia_user;
GRANT ALL PRIVILEGES ON DATABASE accountia_dev TO accountia_user;
\q
```

### Opción B: PostgreSQL con Docker

1. **Crear archivo docker-compose para PostgreSQL**:
```yaml
# postgres-docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: accountia_user
      POSTGRES_PASSWORD: accountia_password
      POSTGRES_DB: accountia_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

2. **Iniciar PostgreSQL**:
```bash
docker-compose -f postgres-docker-compose.yml up -d
```

---

## 5. Configuración de Redis

### Opción A: Redis con Docker (Recomendado)
```bash
docker run -d -p 6379:6379 --name redis-accountia redis:alpine
```

### Opción B: Redis Local
- Windows: Descarga desde [redis.io](https://redis.io/download)
- Mac: `brew install redis`
- Linux: `sudo apt-get install redis-server`

---

## 6. Verificación

### Verificar Backend
```bash
cd backend

# Verificar que Python puede leer las variables
python manage.py shell
>>> from django.conf import settings
>>> print(settings.DEBUG)  # Debe mostrar True
>>> print(settings.DATABASES['default']['NAME'])  # Debe mostrar accountia_dev
>>> exit()

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver
```

### Verificar Frontend
```bash
cd frontend

# Verificar variables
npm run dev

# Abre http://localhost:3000 y verifica:
# - No hay errores en la consola sobre Firebase
# - Puedes acceder a la página de login
```

### Verificar Celery
```bash
cd backend
celery -A config worker -l info

# Deberías ver:
# [tasks]
#   . apps.documents.tasks.process_document
#   . apps.documents.tasks.process_declaration_documents
```

---

## 🚨 Problemas Comunes

### Error: "FIREBASE_CREDENTIALS_PATH not found"
- Verifica que el archivo existe en `backend/credentials/firebase-admin-sdk.json`
- Verifica que la ruta en .env es correcta

### Error: "could not connect to server" (PostgreSQL)
- Verifica que PostgreSQL está corriendo
- Verifica usuario y contraseña
- Si usas Docker, verifica que el contenedor está activo

### Error: "Firebase: No Firebase App" (Frontend)
- Verifica que todas las variables VITE_FIREBASE_* están configuradas
- Verifica que no hay espacios extra en los valores

### Error: "CORS policy" (Frontend)
- Verifica que CORS_ALLOWED_ORIGINS en el backend incluye http://localhost:3000

---

## 📝 Checklist Final

- [ ] Firebase project creado
- [ ] Authentication habilitado en Firebase
- [ ] Archivo firebase-admin-sdk.json descargado y copiado
- [ ] Backend .env configurado
- [ ] Frontend .env configurado
- [ ] PostgreSQL corriendo y accesible
- [ ] Redis corriendo
- [ ] Backend inicia sin errores
- [ ] Frontend inicia sin errores
- [ ] Puedes registrar un usuario en la app

¡Listo! Tu entorno de desarrollo está configurado. 🎉