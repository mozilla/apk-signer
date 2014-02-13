"""
Django settings for apk_signer project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
import logging.handlers
import cef
import tempfile

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
    'apk_signer.resthawk',
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
    'apk_signer.resthawk.middleware.HawkResponseMiddleware',
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
        'mohawk': {
            'handlers': ['unicodesyslog'],
            # Set this to DEBUG for any Hawk auth debugging.
            'level': 'INFO',
            'propagate': True,
        },
        'boto': {
            'handlers': ['unicodesyslog'],
            'level': 'INFO',
            'propagate': True,
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
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apk_signer.resthawk.HawkAuthentication',
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

# When True, it means Hawk authentication will be disabled everywhere.
# This is mainly just to get a speed-up while testing.
SKIP_HAWK_AUTH = False

HAWK_CREDENTIALS = {
    # These credentials are for requests the APK Factory to communicate
    # with the signer.
    'apk-factory': {
        'id': 'apk-factory',
        # Set this to some long random string.
        'key': '',
        'algorithm': 'sha256'
    },
}

# Amazon Web Services access key for use with S3.
AWS_ACCESS_KEY = ''

# Amazon Web Services secret for use with S3.
AWS_SECRET_KEY = ''

# Name of S3 bucket where all signed/unsigned APKs are stored.
# This bucket must already exist.
S3_APK_BUCKET = 'mozilla-apk-cache-local'

# Name of S3 bucket where all key stores are kept.
# This bucket must already exist.
S3_KEY_BUCKET = 'mozilla-apk-keys-local'


# Various options for the signing process.
# The default testing value is the RHS

# Path to the keytool and jarsigner executables
# If left blank, `keytool` will be executed with no prefix
# (i.e. using $PATH)
APK_SIGNER_JAVA_CLI_PATH = ''

# Where to store temporary files for keystore manipulation
APK_SIGNER_KEYS_TEMP_DIR = tempfile.gettempdir()

# The password for all PKCS12 files
APK_SIGNER_STORE_PASSWD = ''

# How long is each generated self signed certificate valid for
APK_SIGNER_VALIDITY_PERIOD = 3650  # 10 years

# Type of key to use to sign the APK manifest
APK_SIGNER_APP_KEY_ALGO = 'RSA'

# Length of the generated key in bits
APK_SIGNER_APP_KEY_LENGTH = 2048

# Weird string that names the algo to use to sign the APK manifest.
# See http://docs.oracle.com/javase/7/docs/api/java/security/Signature.html
# Even though that page says SHA256withRSA is required, keytool and
# jarsigner both throw an error in my test environment
APK_SIGNER_SIGN_SIG_ALGO = 'SHA1withRSA'

# Digest algorithm to use on the APK manifest to generate signatures
APK_SIGNER_SIGN_DIGEST_ALGO = 'SHA1'
