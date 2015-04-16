# -*- coding: utf-8 -*-

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': 'test.sqlite3',
#         'USER': '',
#         'PASSWORD': '',
#         'HOST': '',
#         'PORT': '',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sanza_ci',
        'USER': 'postgres',
        'PASSWORD': 'lynxlynx',
        'HOST': 'localhost',
        'PORT': '',
    }
}