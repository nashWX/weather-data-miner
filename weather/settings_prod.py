from decouple import config


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME', cast=str),
        'USER': config('DB_USER', cast=str),
        'PASSWORD': config('DB_PASSWORD', cast=str),
        'HOST': 'localhost',
        'PORT': '',
    }
}

STATIC_ROOT = '/home/weather-project/weather-data-miner/staticfiles/'