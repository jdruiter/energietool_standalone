import os
from pathlib import Path

# 04de0f863ecc9f16c22bb4e3356876322079549aabf62ca9c5605b89596e362a616295543d9177afd7cce40afc0a4b4e

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
BASE_URL = "http://localhost:8000"

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'collected_static')
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# ---- DEBUG
VERSION = 'DEBUG'
DEBUG = True


# ---- LIVE
# VERSION = 'LIVE'
# DEBUG = False
# CSRF_COOKIE_SECURE = True     # CSRF cookie only over https
# SESSION_COOKIE_SECURE = True    # session cookie only over https


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'eprijs.nl',
]


INSTALLED_APPS = [
    'django.contrib.admin',   # django==3.2, 4.2
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'import_export',
    'rosetta',
    'eprijzen',
]
# 'widget_tweaks', # for render


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'energieprijzen.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'templates'), ],
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

WSGI_APPLICATION = 'energieprijzen.wsgi.application'
SECRET_KEY = '9u7-!=r$43inxt=juw$#&!zgmnez5mqd3f-e6_w*29%_--lil1'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite')
    }
}


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/
USE_I18N = True
USE_L10N = False
LANGUAGE_CODE = 'en-US' # en-US, nl-NL
LANGUAGES = [
    ('en', 'English'),
    ('nl', 'Nederlands'),
    ('de', 'Deutsch'),
    ('fr', 'French'),
]

LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

TIME_ZONE = 'UTC'
USE_TZ = False
APPEND_SLASHES = True


# logging
import logging
# default: https://github.com/django/django/blob/main/django/utils/log.py
LOGGING_CONFIG = None   #disables django default logging (works better than disable_existing_logging)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,   # Disabled loggers are not the same as removed; the logger will still exist, but will silently discard anything logged to it
    'formatters': {
        'plain': {
            'format': '%(asctime)s - %(levelname)s - %(message)s',
            'datefmt': '%d-%m-%Y %H:%M'
        },
        'verbose': {
            'format': '[%(asctime)s] - %(levelname)s - %(filename)s - [%(name)s:%(lineno)s] - %(funcName)s - %(message)s',
            'datefmt': '%d-%m-%Y %H:%M'
        },
    },
    'handlers': {
        'file-management-commands': {
            'level': 'DEBUG',
            'class':'logging.FileHandler',
            'filename': 'logs/management-commands.log',
            'formatter': 'verbose',
        },
        'file-api-results': {
            'level': 'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024*2, # 5MB
            'backupCount': 20,
            'filename': 'logs/API-results.log',
            'formatter': 'plain',
        },
        'file-eprijzen': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/eprijzen.log',
            'formatter': 'verbose'
        },
        'file-python-warnings': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'logs/python-warnings.log',
            'formatter': 'verbose'
        },
        'file-django': {
            'level': 'DEBUG',
            'class':'logging.FileHandler',
            'filename': 'logs/django.log',
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'default': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/default.log',
            'formatter': 'verbose'
        },
        'file-django-request': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django-request.log',
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 20,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.security.DisallowedHost': { #to prevent those DISALLOWED_HOST emails
            'handlers': [],
            'propagate': False,  #propagate to parent loggers (if existing)
        },
        'eprijzen': {
            'handlers': ['console', 'file-eprijzen'],
            'level': 'DEBUG',
            'propagate': False
        },
        'api-results': {
            'handlers': ['console', 'file-api-results'],
            'level': 'DEBUG',
            'propagate': False
        },
        'django': {
            'handlers': ['console', 'file-django'],  #contains all static files requests
            'level': 'INFO',
            'propagate': False
        },
        'django.request': {
            'handlers': ['file-django-request'],
            'level': 'INFO',
            'propagate': True
        },
        'py.warnings': {
            'handlers': ['file-python-warnings'],
            'level': 'INFO',
            'propagate': False
        },
        'management-commands': {
            'handlers': ['console', 'file-management-commands'],
            'level': 'DEBUG',
            'propagate': False
        },
        '': {  #Catch all logger. Setting others to propagate=True will reach this one
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': True
        },
        # 'django.db.backends': {  #Show SQL queries
        #     'handlers': ['file-debug', ],
        #     'level': 'DEBUG',
        # },
    },
    'root': {
        'handlers': ['default'],
        'level': 'INFO'
    },
}
import logging.config
logging.config.dictConfig(LOGGING)

""" 
logger = logging.getLogger('project.interesting.stuff')
propagate=True
true -> events logged to this logger will be passed to higher level loggers, in addition to any handlers attached to this logger
Why is the hierarchy important? Well, because loggers can be set to propagate their logging calls to their parents. 
In this way, you can define a single set of handlers at the root of a logger tree, and capture all logging calls in the subtree of loggers. 

"""