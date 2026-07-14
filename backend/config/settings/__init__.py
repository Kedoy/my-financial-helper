"""
Default settings module.
"""
import os

# По умолчанию используем development settings
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development')

if settings_module == 'config.settings.base':
    from .base import *
elif settings_module == 'config.settings.production':
    from .production import *
else:
    from .development import *
