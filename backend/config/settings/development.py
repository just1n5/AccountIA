"""
Development settings for AccountIA project.
"""

from .base import *

# Debug
DEBUG = True

# Database - SQLite para desarrollo (más simple)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Uncomment below to use PostgreSQL
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.getenv('DB_NAME', 'accountia_dev'),
#         'USER': os.getenv('DB_USER', 'accountia_user'),
#         'PASSWORD': os.getenv('DB_PASSWORD', 'accountia_password'),
#         'HOST': os.getenv('DB_HOST', 'localhost'),  # Cambiado de 'postgres' a 'localhost'
#         'PORT': os.getenv('DB_PORT', '5432'),
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