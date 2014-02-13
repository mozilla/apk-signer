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

APK_SIGNER_STORE_PASSWD = 'keytool password just for testing'

# Safety measure to make sure setUp() resets this setting correctly.
APK_SIGNER_KEYS_TEMP_DIR = '/nowhere/dont/even/try'

# Find these on $PATH
APK_SIGNER_JAVA_CLI_PATH = ''
