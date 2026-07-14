"""
Development settings.
"""

from .base import *
import os

DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# More permissive CORS for development
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3000',
    'http://127.0.0.1:5173',
    'http://127.0.0.1:3000',
]

# Console email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Show toolbar for debugging
INSTALLED_APPS += [
    'django.contrib.admindocs',
]

# Database - use PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'fin_db'),
        'USER': os.getenv('POSTGRES_USER', 'fin_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'fin_password'),
        'HOST': os.getenv('POSTGRES_HOST', '/tmp/postgresql'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

# Logging for development
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
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
