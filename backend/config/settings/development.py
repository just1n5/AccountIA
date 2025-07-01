"""
Development settings for AccountIA project.
"""
import os
from .base import *

# Debug
DEBUG = True

# Development flags
DEV_SKIP_AUTH_FOR_TESTING = os.getenv('DEV_SKIP_AUTH_FOR_TESTING', '0') == '1'
DEV_MOCK_EXTERNAL_SERVICES = os.getenv('DEV_MOCK_EXTERNAL_SERVICES', '0') == '1'

# Middleware - agregar middleware de desarrollo
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'config.middleware.development.CORSMiddleware',  # CORS mejorado
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'config.middleware.development.DevelopmentAuthMiddleware',  # Auth bypass para desarrollo
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'config.utils.development.DevelopmentAuthentication',  # Permite bypass en desarrollo
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'config.utils.development.DevelopmentPermission',  # Permite todo en desarrollo
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Database - PostgreSQL para desarrollo
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'accountia_dev'),
        'USER': os.getenv('DB_USER', 'accountia_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'password123'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
            # 'options': '-c default_transaction_isolation=read committed'
        },
    }
}

# SQLite backup (commented)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable caching in development
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Additional apps for development
# INSTALLED_APPS += [
#     'django_extensions',
# ]

# Logging
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

# Allow all hosts in development
ALLOWED_HOSTS = ['*']
