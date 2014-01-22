"""private_base will be populated from puppet and placed in this directory"""
import private_base as private

DOMAIN = 'apk-signer-dev.allizom.org'
ALLOWED_HOSTS = [DOMAIN]

SECRET_KEY = private.SECRET_KEY

SENTRY_DSN = private.SENTRY_DSN

STATSD_HOST = private.STATSD_HOST
STATSD_PORT = private.STATSD_PORT
STATSD_PREFIX = private.STATSD_PREFIX
