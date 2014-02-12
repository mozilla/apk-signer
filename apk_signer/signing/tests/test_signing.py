# -*- coding: utf-8 -*-
import base64
import shutil
import subprocess
import tempfile
import zipfile
from zipfile import ZipFile

from django.conf import settings

from apk_signer.base.tests import TestCase

import mock
from nose.exc import SkipTest

from apk_signer import signing


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
        tmp = tempfile.mkdtemp(prefix='tmp_apk_signer_test_')
        tmp_p = mock.patch.object(settings, 'APK_SIGNER_KEYS_TEMP_DIR', tmp)
        tmp_p.start()

        def rm_tmp():
            shutil.rmtree(tmp)
            tmp_p.stop()

        self.addCleanup(rm_tmp)

        self.apk_id = 'hash_based_on_manifest_url'
        self.dn = ("CN=Generated key for ID {id}, OU=Mozilla APK Factory, "
                   "O=Mozilla Marketplace, L=Mountain View, ST=California, "
                   "C=US".format(id=self.apk_id))

        # TODO: set up temp file for key stores.

        # TODO: Cache this as a test asset for speed.
        self.keystore = signing.gen_keystore(self.apk_id)

        p = mock.patch('apk_signer.signing.storage')
        self.stor = p.start()
        self.addCleanup(p.stop)

    def test_generate(self):
        raise SkipTest
        key_fp = signing.generate(self.testurl)
        args - ['keytool', '-printcert',
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

    def test_sign_and_verify(self):
        kf = open(self.keystore, 'rb')
        self.stor.get_app_key.return_value = kf
        self.addCleanup(kf.close)

        with tempfile.NamedTemporaryFile(prefix='test_sign_',
                                         suffix='.apk') as apk:
            z = ZipFile(apk, 'w', zipfile.ZIP_DEFLATED)
            z.writestr("index.html", "")
            z.writestr("manifest.webapp", MANIFEST)
            z.writestr("img/pixel.gif", base64.b64decode(PIXEL_GIF))

            z.close()
            apk.seek(0)

            signed_fp = signing.sign(self.apk_id, apk)

            signed_fp.seek(0)
            output = signing.jarsigner(['-verify', '-verbose', signed_fp.name])
            assert output.strip().endswith('jar verified.'), output
