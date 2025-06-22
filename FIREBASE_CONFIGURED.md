# 🎉 Firebase Configurado - Próximos Pasos

## ✅ Frontend Configurado

Tu archivo `frontend/.env` ya está actualizado con la configuración de Firebase:

```env
VITE_FIREBASE_API_KEY=AIzaSyCYr-CzvFq_KiEy_PLIs0B_hS0reYH6c1g
VITE_FIREBASE_AUTH_DOMAIN=accountia-dev.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=accountia-dev
VITE_FIREBASE_STORAGE_BUCKET=accountia-dev.firebasestorage.app
VITE_FIREBASE_MESSAGING_SENDER_ID=687868450492
VITE_FIREBASE_APP_ID=1:687868450492:web:f798fd2a0fe38560b4e2b9
```

## 📋 Pasos Siguientes:

### 1. **Habilitar Authentication en Firebase**

Ve a [Firebase Console](https://console.firebase.google.com/u/0/project/accountia-dev/authentication) y:

1. Click en "Authentication" en el menú lateral
2. Click en "Get started" si no lo has hecho
3. En la pestaña "Sign-in method", habilita:
   - **Email/Password** (obligatorio)
   - **Google** (recomendado)

### 2. **Descargar Credenciales del Servicio (Backend)**

1. Ve a [Configuración del proyecto](https://console.firebase.google.com/u/0/project/accountia-dev/settings/general)
2. Click en la pestaña "**Service accounts**"
3. Click en "**Generate new private key**"
4. Se descargará un archivo JSON
5. **Guarda este archivo** en: `backend/credentials/firebase-admin-sdk.json`

### 3. **Configurar la Base de Datos**

#### Opción A: Con Docker (Recomendado - 2 minutos)
```bash
# PostgreSQL
docker run -d -p 5432:5432 \
  -e POSTGRES_USER=accountia_user \
  -e POSTGRES_PASSWORD=accountia_password \
  -e POSTGRES_DB=accountia_dev \
  --name postgres-accountia \
  postgres:15-alpine

# Redis
docker run -d -p 6379:6379 --name redis-accountia redis:alpine
```

#### Opción B: Instalación Local
- [Descargar PostgreSQL](https://www.postgresql.org/download/)
- Crear base de datos manualmente

### 4. **Inicializar el Backend**

```bash
cd backend

# Verificar que el archivo de credenciales existe
ls credentials/firebase-admin-sdk.json

# Instalar dependencias (si no lo has hecho)
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
# Email: admin@accountia.co
# Password: (elige una segura)

# Iniciar el servidor
python manage.py runserver
```

### 5. **Iniciar el Frontend**

```bash
cd frontend

# Instalar dependencias (si no lo has hecho)
npm install

# Iniciar el servidor de desarrollo
npm run dev
```

### 6. **Iniciar Celery** (En otra terminal)

```bash
cd backend
celery -A config worker -l info
```

## 🧪 Verificación

1. **Frontend**: Abre http://localhost:3000
   - Deberías ver la página de login
   - No debe haber errores de Firebase en la consola

2. **Backend**: Abre http://localhost:8000/admin
   - Deberías poder hacer login con el superusuario

3. **API Docs**: Abre http://localhost:8000/api/docs/
   - Deberías ver la documentación de la API

## 🚨 Troubleshooting

### Error: "Firebase app not initialized"
- Verifica que todas las variables VITE_FIREBASE_* están en el .env
- Reinicia el servidor de desarrollo del frontend

### Error: "FIREBASE_CREDENTIALS_PATH not found"
- Asegúrate de haber descargado y guardado el archivo JSON en `backend/credentials/firebase-admin-sdk.json`

### Error: "could not connect to server" (PostgreSQL)
- Verifica que Docker está corriendo: `docker ps`
- O que PostgreSQL está instalado y corriendo localmente

### Error: "Connection refused" (Redis)
- Verifica que Redis está corriendo: `docker ps | grep redis`

## ✅ Checklist Final

- [ ] Firebase Authentication habilitado (Email/Password + Google)
- [ ] Archivo `firebase-admin-sdk.json` descargado y en `backend/credentials/`
- [ ] PostgreSQL corriendo (Docker o local)
- [ ] Redis corriendo (Docker o local)
- [ ] Backend corriendo sin errores (`python manage.py runserver`)
- [ ] Frontend corriendo sin errores (`npm run dev`)
- [ ] Celery worker corriendo (`celery -A config worker`)
- [ ] Puedes crear una cuenta en http://localhost:3000

## 🎯 ¡Listo para Desarrollar!

Una vez completados estos pasos, tu entorno estará completamente configurado y podrás:

1. Registrar usuarios
2. Crear declaraciones
3. Subir archivos Excel
4. Ver el procesamiento en tiempo real

¿Necesitas ayuda con algún paso específico?