"""
Django settings for Ks Financial App project.
Base settings - common for all environments.
"""

from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

# Загружаем .env из корня проекта
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / '.env')

# Build paths inside the project like this: BASE_DIR / 'subdir'.

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_spectacular',  # Swagger/OpenAPI documentation

    # Project apps
    'apps.accounts.apps.AccountsConfig',
    'apps.transactions.apps.TransactionsConfig',
    'apps.categories.apps.CategoriesConfig',
    'apps.analytics.apps.AnalyticsConfig',
    'apps.core.apps.CoreConfig',
    'apps.blog.apps.BlogConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
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

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',  # Swagger/OpenAPI
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', 15))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_LIFETIME_DAYS', 7))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}

# CORS settings
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', 'http://localhost:5173').split(',')
CORS_ALLOW_CREDENTIALS = True

# Cookie settings for security
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SAMESITE = 'Lax'

# Email settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@ks-financial-app.com')

# Frontend URL
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

# Auth settings
LOGIN_URL = 'auth_pages:login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'auth_pages:login'

# Swagger/OpenAPI Settings (drf-spectacular)
SPECTACULAR_SETTINGS = {
    'TITLE': 'Ks Financial App API',
    'DESCRIPTION': '''
## API для системы учёта и анализа персональных финансов

### Аутентификация
- Используйте **POST /api/v1/auth/login/** для получения токенов
- Access token передавайте в заголовке: `Authorization: Bearer <token>`
- Refresh token автоматически устанавливается в HttpOnly cookie

### Основные эндпоинты
- **Транзакции** - CRUD операций с финансами
- **Категории** - управление категориями
- **Аналитика** - статистика и AI рекомендации
- **Блог** - посты и комментарии

### AI Функционал
- **AI Рекомендации** - персональные советы по экономии
- **SMS Парсинг** - автоматическое создание транзакций из SMS
''',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'AUTHENTICATION_WHITELIST': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'SECURITY_SCHEMES': {
        'jwtAuth': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
            'description': 'JWT Bearer token authentication'
        },
        'cookieAuth': {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'refresh_token',
            'description': 'Refresh token in HttpOnly cookie'
        }
    },
    'TAGS': [
        {'name': 'Auth', 'description': 'Аутентификация и управление профилем'},
        {'name': 'Transactions', 'description': 'Управление транзакциями'},
        {'name': 'Categories', 'description': 'Категории доходов/расходов'},
        {'name': 'Analytics', 'description': 'Аналитика и AI рекомендации'},
        {'name': 'Blog', 'description': 'Блог и комментарии'},
    ]
}

# AI Settings
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
LLM_MODEL = os.getenv('LLM_MODEL', 'llama2')

# Redis Cache Settings
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'default-cache',
        'TIMEOUT': 300,
    },
    'redis': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': REDIS_PASSWORD,
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
        },
        'TIMEOUT': 3600,
        'KEY_PREFIX': 'ks_financial',
    }
}

# Cache settings for forecasts
FORECAST_CACHE_TTL = {
    'daily': 3600,      # 1 hour
    'weekly': 7200,     # 2 hours
    'monthly': 14400,   # 4 hours
}

# Session cache (optional - use Redis for sessions in production)
# SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
# SESSION_CACHE_ALIAS = 'redis'
