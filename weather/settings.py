"""
Django settings for weather project.

Generated by 'django-admin startproject' using Django 3.2.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
from decouple import config
from celery.schedules import crontab
# Build paths inside the project like this: BASE_DIR / 'subdir'.
import os
# GDAL_LIBRARY_PATH = ''
if os.name == 'nt':
    VENV_BASE = os.environ['VIRTUAL_ENV']
    os.environ['PATH'] = os.path.join(VENV_BASE, 'Lib/site-packages/osgeo') + ';' + os.environ['PATH']
    os.environ['PROJ_LIB'] = os.path.join(VENV_BASE, 'Lib/site-packages/osgeo/data/proj') + ';' + os.environ['PATH']
    
    GDAL_LIBRARY_PATH = os.path.join(VENV_BASE, 'Lib/site-packages/osgeo/gdal303.dll')

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8z&brt7e7c(b^mq46bx2ub$b5+&r9m%w3g8tqv^uc0^#feha3s'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', cast=bool, default=False)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda hosts: [h.strip() for h in hosts.split(',')], default='*,')


# Application definition

INSTALLED_APPS = [
    'grappelli',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'weather.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'app.context_processor.util',
            ],
        },
    },
]

WSGI_APPLICATION = 'weather.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME', cast=str),
        'USER': config('DB_USER', cast=str),
        'PASSWORD': config('DB_PASSWORD', cast=str),
        'HOST': config('DB_HOST', cast=str, default='localhost'),
        'PORT': '',
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = config('timezone', cast=str, default="America/New_York")

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# Add these new lines
STATICFILES_DIRS = (
    BASE_DIR / 'static',
)

STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_ROOT = BASE_DIR / 'media'
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SESSION_EXPIRE_AT_BROWSER_CLOSE=True

redis_port = config('redis_port', cast=int, default=6379)

CELERY_BROKER_URL = f"redis://localhost:{redis_port}"
CELERY_RESULT_BACKEND = f"redis://localhost:{redis_port}"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"

CELERYBEAT_SCHEDULE = {
    'retrive_tornado': {
        'task': 'app.tasks.tornadow_warning',
        'schedule': crontab(minute='*/5')
    },
    'retrive_flood': {
        'task': 'app.tasks.flood_warning',
        'schedule': crontab(minute='*/8')
    },
    'retrive_thunderstorm': {
        'task': 'app.tasks.thunderstorm_warning',
        'schedule': crontab(minute='*/10')
    },
    # 'update_location_location_id': {
    #     'task': 'app.tasks.update_missing_location_id',
    #     'schedule': crontab(minute='*/25')
    # },
    # 'update_population': {
    #     'task': 'app.tasks.update_population',
    #     'schedule': crontab(minute='0', hour='*/6')
    # },
    'update_empty_map': {
        'task': 'app.tasks.update_empty_map',
        'schedule': crontab(minute='30', hour='*/4')
    },
}


CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379',
    }
}

GRAPPELLI_ADMIN_TITLE = 'STORM SCANNER'
if not DEBUG:
    from .settings_prod import *