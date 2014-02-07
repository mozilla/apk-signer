"""private_base will be populated from puppet and placed in this directory"""
from apk_signer.settings import base as base_settings
import private_base as private

DOMAIN = 'apk-signer.allizom.org'
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

S3_BUCKET = 'mozilla-apk-cache-stage'
