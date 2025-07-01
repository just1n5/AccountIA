"""
Development settings ULTRA MÍNIMO para AccountIA project.
Solo declaraciones, sin documentos por ahora.
"""
import os
from .base import *

# Debug
DEBUG = True
ALLOWED_HOSTS = ['*']

# CORS settings básicos
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# REST Framework - CONFIGURACIÓN ULTRA SIMPLIFICADA
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # SIMPLIFICADO: Permitir todo en desarrollo
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Database - SQLite para desarrollo (más simple)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Middleware SIMPLIFICADO
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# SOLO APPS ESENCIALES - SIN DOCUMENTS POR AHORA
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps - SOLO LOS ESENCIALES
    'rest_framework',
    'corsheaders',
    
    # Local apps - SOLO LAS QUE FUNCIONAN
    'apps.users',
    'apps.declarations',
    'apps.authentication',
    # Temporalmente removemos documents hasta instalar pandas
    # 'apps.documents',
]

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable caching in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Logging ultra simplificado
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# Disable HTTPS redirect in development
SECURE_SSL_REDIRECT = False

# CONFIGURACIÓN PARA TESTING
DEV_SKIP_AUTH_FOR_TESTING = True

# FORZAR URL CONFIGURATION MÍNIMA
ROOT_URLCONF = 'config.urls_minimal'

print("🔧 [SETTINGS] Usando configuración development_minimal.py")
print("🔧 [SETTINGS] SIN app documents (temporalmente)")
print("🔧 [SETTINGS] SQLite database")
print("🔧 [SETTINGS] Solo declaraciones y usuarios")
print("🔧 [SETTINGS] URLs mínimas forzadas")
