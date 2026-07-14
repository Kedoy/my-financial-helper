"""
Production settings.
"""

from .base import *

DEBUG = False

# Security settings for production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# Allowed hosts should be set explicitly in production
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# CORS for production
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

# Database - PostgreSQL для продакшена
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'fin_db'),
        'USER': os.getenv('POSTGRES_USER', 'fin_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'fin_password'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# Static files with manifest for caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/app.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
