"""private_base will be populated from puppet and placed in this directory"""
from apk_signer.settings import base as base_settings
import private_base as private

DOMAIN = 'apk-signer.mozilla.org'
ALLOWED_HOSTS = [DOMAIN]

SECRET_KEY = private.SECRET_KEY

SENTRY_DSN = private.SENTRY_DSN

STATSD_HOST = private.STATSD_HOST
STATSD_PORT = private.STATSD_PORT
STATSD_PREFIX = private.STATSD_PREFIX

HAWK_CREDENTIALS = base_settings.HAWK_CREDENTIALS
HAWK_CREDENTIALS['apk-factory']['key'] = private.HAWK_APK_FACTORY_KEY
HAWK_CREDENTIALS['apk-signer']['key'] = private.HAWK_APK_SIGNER_KEY
