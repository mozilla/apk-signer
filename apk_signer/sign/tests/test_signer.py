# -*- coding: utf-8 -*-
import base64
import os
import shutil
import subprocess
import tempfile
import zipfile
from zipfile import ZipFile

from django.conf import settings

from apk_signer.base.tests import TestCase
from apk_signer.sign import signer

import mock
from nose.exc import SkipTest


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

        p = mock.patch('apk_signer.sign.signer.storage')
        self.stor = p.start()
        self.addCleanup(p.stop)

    def open_keystore(self):
        kf = open(asset('test.keystore'), 'rb')
        self.addCleanup(kf.close)
        return kf

    def test_generate(self):
        raise SkipTest
        key_fp = signer.generate(self.testurl)
        args = ['keytool', '-printcert',
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
        self.stor.get_app_key.return_value = self.open_keystore()

        with tempfile.NamedTemporaryFile(prefix='test_sign_',
                                         suffix='.apk') as apk:
            z = ZipFile(apk, 'w', zipfile.ZIP_DEFLATED)
            z.writestr("index.html", "")
            z.writestr("manifest.webapp", MANIFEST)
            z.writestr("img/pixel.gif", base64.b64decode(PIXEL_GIF))

            z.close()
            apk.seek(0)

            signed_fp = signer.sign(self.apk_id, apk)

            signed_fp.seek(0)
            output = signer.jarsigner(['-verify', '-verbose', signed_fp.name])
            assert output.strip().endswith('jar verified.'), output


def asset(fn):
    return os.path.join(os.path.dirname(__file__), 'assets', fn)
