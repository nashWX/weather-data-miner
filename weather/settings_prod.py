from decouple import config


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config('DB_NAME', cast='str', default='weather'),
        'USER': config('DB_USER', cast='str', default='weatheruser'),
        'PASSWORD': config('DB_PASSWORD', cast='str', default='weatherpassword'),
        'HOST': 'localhost',
        'PORT': '',
    }
}

