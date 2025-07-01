"""
Development settings ULTRA SIMPLIFICADO para AccountIA project.
Configuración mínima sin dependencias complejas.
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
    # Removemos drf_spectacular para evitar dependencias
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

# Remover apps problemáticas de INSTALLED_APPS
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
    
    # Local apps
    'apps.users',
    'apps.declarations',
    'apps.documents',
    'apps.authentication',
    # Removemos las que pueden causar problemas
    # 'apps.ai_core',
    # 'apps.payments',
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

print("🔧 [SETTINGS] Usando configuración development_ultra_simple.py")
print("🔧 [SETTINGS] Sin drf_spectacular")
print("🔧 [SETTINGS] SQLite database")
print("🔧 [SETTINGS] Apps mínimas")
