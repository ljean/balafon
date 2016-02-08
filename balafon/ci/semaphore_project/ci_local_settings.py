# -*- coding: utf-8 -*-

import sys

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Luc JEAN', 'ljean@apidev.fr'),
)

MANAGERS = ADMINS

#if 'test' in sys.argv:
#    DATABASES = {
#        'default': {
#            'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#            'NAME': 'quatuor-test-db.sqlite3',                      # Or path to database file if using sqlite3.
#            'USER': '',                      # Not used with sqlite3.
#            'PASSWORD': '',                # Not used with sqlite3.
#            'HOST': '', # Set to empty string for localhost. Not used with sqlite3.
#            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
#        }
#    }
#else:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'debussy_balafon',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': 'lynxlynx',                # Not used with sqlite3.
        'HOST': 'localhost', # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}        


EMAIL_HOST = 'smtp.alwaysdata.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_SUBJECT_PREFIX = 'cdlh - dev'
EMAIL_HOST_PASSWORD = 'apidev1$'
EMAIL_HOST_USER = 'webapp@apidev.fr'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

SECRET_KEY = 'debussy'*10
INTERNAL_IPS = ('127.0.0.1',)
WKHTMLTOPDF_CMD = r'wkhtmltopdf'

BALAFON_NOTIFICATION_EMAIL = 'ljean@apidev.fr'
COOP_CMS_SITE_PREFIX = 'http://127.0.0.1:8000'