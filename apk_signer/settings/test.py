from .base import *

# Any settings here will override the base settings but only while runnning the
# test suite.

SECRET_KEY = ('Imma let you finish but this is one of the best test '
              'suites of all time')

SKIP_HAWK_AUTH = True

HAWK_CREDENTIALS = {
    'apk-factory': {
        'id': 'apk-factory',
        'key': 'some long random string',
        'algorithm': 'sha256'
    },
    'apk-signer': {
        'id': 'apk-signer',
        'key': 'some long random string',
        'algorithm': 'sha256'
    }
}

LOGGING['loggers']['mohawk']['level'] = 'DEBUG'
