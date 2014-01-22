"""
Django settings for apk_signer project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import logging.handlers
import cef

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# You must set a secret key in local settings.
SECRET_KEY = ''

DEBUG = False
TEMPLATE_DEBUG = False

# On production, this must contain the hostname of the Django app.
ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',

    # Third-party apps, patches, fixes
    'raven.contrib.django',
    'rest_framework',

    # Local apps
    'apk_signer.base',
    'apk_signer.system',
)

MIDDLEWARE_CLASSES = (
    'django_statsd.middleware.GraphiteRequestTimingMiddleware',
    'django_statsd.middleware.GraphiteMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    'django_paranoia.sessions.ParanoidSessionMiddleware',
)

ROOT_URLCONF = 'apk_signer.urls'

WSGI_APPLICATION = 'apk_signer.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

# This app does not use a database but declaring some settings seems to help
# out a few pesky things.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = False
USE_L10N = False
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'


# Custom settings.

STATSD_CLIENT = 'django_statsd.clients.normal'


DJANGO_PARANOIA_REPORTERS = [
    'django_paranoia.reporters.cef_',
]

SESSION_ENGINE = 'django_paranoia.sessions'


SYSLOG_TAG = 'http_app_apk_signer'
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'base': {
            '()': 'logging.Formatter',
            'format':
                '%(name)s:%(levelname)s '
                '%(message)s :%(pathname)s:%(lineno)s'
        },
        'cef': {
            '()': cef.SysLogFormatter,
            'datefmt': '%H:%M:%s',
        }
    },
    'handlers': {
        'unicodesyslog': {
            '()': 'mozilla_logger.log.UnicodeHandler',
            'facility': logging.handlers.SysLogHandler.LOG_LOCAL7,
            'formatter': 'base',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.handlers.SentryHandler',
        },
        'console': {
            'level': 'DEBUG',
            '()': logging.StreamHandler,
            'formatter': 'base',
        },
        'cef_syslog': {
            '()': logging.handlers.SysLogHandler,
            'facility': logging.handlers.SysLogHandler.LOG_LOCAL4,
            'formatter': 'cef',
        },

    },
    'loggers': {
        '': {
            'handlers': ['unicodesyslog'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['unicodesyslog', 'sentry'],
            'level': 'INFO',
            'propagate': True
        },
        'cef': {
            'handlers': ['cef_syslog']
        },
    }
}

SENTRY_DSN = ''

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'PAGINATE_BY': 20,
    'PAGINATE_BY_PARAM': 'limit'
}

# CEF logging.

CEF_DEFAULT_SEVERITY = 5
CEF_PRODUCT = 'APK-Signer'
CEF_VENDOR = 'Mozilla'
CEF_VERSION = '0'
CEF_DEVICE_VERSION = '0'

# Should robots.txt allow web crawlers? We set this to False since it's a
# private API.
ENGAGE_ROBOTS = False

# Common test runner settings.
# Note: you must put django_nose in your INSTALLED_APPS (in local settings)
# for these to take affect.

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--logging-clear-handlers',
    '--with-nicedots',
    '--with-blockage',
    '--http-whitelist=""',
]
