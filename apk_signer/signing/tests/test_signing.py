import hashlib
import os.path
import subprocess
import tempfile
import zipfile

from apk_signer.base.tests import TestCase

import mock

from apk_signer import signing
from apk_signer.storage import NoSuchKey


# Python 2.6 and earlier doesn't have context manager support
ZipFile = zipfile.ZipFile
if not hasattr(zipfile.ZipFile, "__enter__"):
    class ZipFile(zipfile.ZipFile):
        def __enter__(self):
            return self
        def __exit__(self, type, value, traceback):
            self.close()


PIXEL_GIF = 'R0lGODlhAQABAJH/AP///wAAAP///wAAACH/C0FET0JFOklSMS4wAt7tACH5BAEAAAIALAAAAAABAAEAAAICVAEAOw=='

MANIFEST = """{
  "version": "1.0",
  "name": "Packaged MozillaBall ょ",
  "description": "Exciting Open Web development action!",
  "launch_path": "/index.html",
  "icons": {
    "16": "/img/icon-16.png",
    "48": "/img/icon-48.png",
    "128": "/img/icon-128.png"
  },
  "permissions": [
    "contacts"
  ],
  "developer": {
    "name": "Mozilla Labs",
    "url": "http://mozillalabs.com"
  },
  "installs_allowed_from": [
    "https://marketplace.mozilla.com"
  ],
  "locales": {
    "es": {
      "description": "¡Acción abierta emocionante del desarrollo del Web!",
      "developer": {
        "url": "http://es.mozillalabs.com/"
      }
    },
    "it": {
      "description": "Azione aperta emozionante di sviluppo di fotoricettore!",
      "developer": {
        "url": "http://it.mozillalabs.com/"
      }
    }
  },
  "default_locale": "en"
}
"""

class TestSigning(TestCase):

    def setUp(self):
        self.testurl = "http://deltron3030.testmanifest.com/manifest.webapp"
        self.digest = hashlib.sha1(testurl).hexdigest()
        self.dn = "CN=Generated key for {url}, OU=Mozilla APK Factory, " \
                  "O=Mozilla Marketplace, L=Mountain View, ST=California, " \
                  "C=US".format(url=self.testurl)

    def test_keyhash(self):
        self.assertEqual(self.digest, signing.keyhash(self.testurl))

    def test_generate(self):
        key_fp = signing.generate(self.testurl)
        args - [ 'keytool', '-printcert',
                 '-storetype', 'pkcs12',
                 '-storepass', 'mozilla'
                 '-alias', '0',
                 '-keystore', key_fp.name]

        stdout = tempfile.TemporaryFile()
        rc = subprocess.call(args, stdout=stdout)
        self.assertFalse(rc)

        stdout.seek(0)
        for line in stdout:
            if line.startsith("Owner:"):
                self.assertEqual(line.strip(), "Owner: " + self.dn)

    def test_lookup(self):
        pass

    def test_sign(self):
        apk = tempfile.NamedTemporaryFile(suffix=".apk")
        z = Zipfile(apk, 'w', zipfile.ZIP_DEFLATED)
        z.writestr("img/pixel.gif", PIXEL_GIF)
        z.writestr("index.html", "")
        z.writestr("manifest.webapp", MANIFEST)
        apk.seek(0)
        self.assertTrue(signing.sign(self.testurl, apk))
