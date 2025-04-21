"""
Local settings for development without database
This overrides settings.py for local development - ONLY FOR DEVELOPMENT!
"""

# Este archivo solo debe ser usado en desarrollo, NO EN PRODUCCIÓN
# Archivo comentado para evitar problemas en producción

"""
import os
from pathlib import Path

# Override DATABASE settings for local development without a database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    }
}

# Enable debug mode for development
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Disable CSRF in development for API testing
# CSRF_COOKIE_SECURE = False
# SESSION_COOKIE_SECURE = False

# Set static files directory
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(Path(__file__).resolve().parent.parent, 'staticfiles')
STATICFILES_DIRS = [os.path.join(Path(__file__).resolve().parent.parent, 'static')]

# Set media directory
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(Path(__file__).resolve().parent.parent, 'media')

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True
""" 