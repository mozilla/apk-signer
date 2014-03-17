"""private_base will be populated from puppet and placed in this directory"""
from apk_signer.settings import base as base_settings
import private_base as private

DOMAIN = private.DOMAIN
ALLOWED_HOSTS = [DOMAIN]

SECRET_KEY = private.SECRET_KEY

SENTRY_DSN = private.SENTRY_DSN

STATSD_HOST = private.STATSD_HOST
STATSD_PORT = private.STATSD_PORT
STATSD_PREFIX = private.STATSD_PREFIX

HAWK_CREDENTIALS = base_settings.HAWK_CREDENTIALS
HAWK_CREDENTIALS['apk-factory']['key'] = private.HAWK_APK_FACTORY_KEY

AWS_ACCESS_KEY = private.AWS_ACCESS_KEY
AWS_SECRET_KEY = private.AWS_SECRET_KEY

S3_APK_BUCKET = private.S3_APK_BUCKET
S3_KEY_BUCKET = private.S3_KEY_BUCKET

APK_SIGNER_STORE_PASSWD = private.APK_SIGNER_STORE_PASSWD
APK_SIGNER_KEYS_TEMP_DIR = private.APK_SIGNER_KEYS_TEMP_DIR

APK_USER_MODE = getattr(private, 'APK_USER_MODE', 'END_USER')

CACHE_PREFIX = APK_USER_MODE
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.PyLibMCCache',
        'LOCATION': private.CACHES_DEFAULT_LOCATION,
        'TIMEOUT': 500,
        'KEY_PREFIX': CACHE_PREFIX,
    },
}
