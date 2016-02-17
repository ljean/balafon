# -*- coding: utf-8 -*-
"""project settings"""

import os.path
import sys

DEBUG = False
TEMPLATE_DEBUG = DEBUG
CI_DRONE = True

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test_db',
        'USER': 'runner',
        'PASSWORD': 'semaphoredb',
        'HOST': '127.0.0.1',
        'PORT': 5432,
        'ATOMIC_REQUESTS': True,
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en'

gettext = lambda s: s
LANGUAGES = (
    ('en', gettext(u'English')),
    ('fr', gettext(u'Français')),
)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.abspath(PROJECT_PATH + '/public/media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.abspath(PROJECT_PATH + '/public/static/')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'drone-ci'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'coop_cms.utils.RequestMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.abspath(PROJECT_PATH + '/templates'),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    'django.core.context_processors.request',
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "balafon.Search.context_processors.quick_search_form",
    "balafon.Crm.context_processors.crm",
    "balafon.Users.context_processors.user_config",
)

AUTHENTICATION_BACKENDS = (
    'balafon.Profile.backends.ArticleCategoryPermissionBackend',
    'coop_cms.apps.email_auth.auth_backends.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ACCOUNT_ACTIVATION_DAYS = 7

SOUTH_SKIP_MIGRATIONS = True
SOUTH_TESTS_MIGRATE = False

LOCALE_REDIRECT_PERMANENT = False

DJALOHA_LINK_MODELS = ('basic_cms.Article', )
COOP_CMS_ARTICLE_LOGO_SIZE = "950x250"
COOP_CMS_NEWSLETTER_TEMPLATES = (
    ('basic_newsletter.html', 'Basic'),
)
COOP_CMS_ARTICLE_TEMPLATES = (
    ('standard.html', u'Standard'),
)
COOP_CMS_FROM_EMAIL = u'"ljean@apidev.fr"'
COOP_CMS_TEST_EMAILS = ('"Luc JEAN - Apidev" <ljean@apidev.fr>', )  # 'luc.jean@gmail.com')
COOP_CMS_SITE_PREFIX = ''
COOP_CMS_REPLY_TO = 'ljean@apidev.fr'
COOP_CMS_TITLE_OPTIONAL = True

EMAIL_IMAGE_FOLDER = 'emailing'
SEARCH_FORM_LIST = 'balafon.config.SEARCH_FORMS'
BALAFON_DEFAULT_COUNTRY = 'France'
BALAFON_MY_COMPANY = "Apidev"
BALAFON_AS_HOMEPAGE = False
BALAFON_NOTIFICATION_EMAIL = 'ljean@apidev.fr'
BALAFON_UNACCENT_FILTER_SUPPORT = True

LOGIN_REDIRECT_URL = "/"

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAdminUser',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    )
}

INSTALLED_APPS = (
    # contribs
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',

    # 3rd parties
    'django_extensions',
    'floppyforms',
    'sorl.thumbnail',
    'captcha',
    'registration',

    # externals
    'djaloha',
    'colorbox',
    'coop_cms',
    'coop_bar',
    'coop_cms.apps.basic_cms',
    'coop_cms.apps.email_auth',
    'coop_cms.apps.coop_bootstrap',

    # balafon
    'balafon',
    'balafon.Crm',
    'balafon.Search',
    'balafon.Emailing',
    'balafon.Profile',
    'balafon.Store',
    'balafon.Users',

    'django.contrib.admin',
    'django.contrib.admindocs',
)


if (len(sys.argv) > 1) and (not sys.argv[1] in ('makemigrations', 'schemamigration', 'datamigration')):
    INSTALLED_APPS = (
        'modeltranslation',
    ) + INSTALLED_APPS

if len(sys.argv) > 1 and 'test' == sys.argv[1]:
    INSTALLED_APPS = INSTALLED_APPS + ('coop_cms.apps.test_app',)

import warnings
warnings.filterwarnings('ignore', r"django.contrib.localflavor is deprecated")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'coop_cms': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'colorbox': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'balafon_crm': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    }
}

try:
    from ci_local_settings import *
except ImportError:
    pass