# -*- coding: utf-8 -*-
import base64
from contextlib import contextmanager
import os
import shutil
import tempfile
import zipfile
from zipfile import ZipFile

from django.conf import settings

from apk_signer.base.tests import TestCase
from apk_signer.storage import AppKeyAlreadyExists, NoSuchKey
from apk_signer.sign import signer
from apk_signer.sign.signer import SigningError

import mock


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


class Base(TestCase):

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

    @contextmanager
    def unsigned_apk(self):
        with tempfile.NamedTemporaryFile(prefix='test_sign_',
                                         suffix='.apk') as apk:
            # Create something signable. Pretend this is an unsigned APK.
            z = ZipFile(apk, 'w', zipfile.ZIP_DEFLATED)
            z.writestr("index.html", "")
            z.writestr("manifest.webapp", MANIFEST)
            z.writestr("img/pixel.gif", base64.b64decode(PIXEL_GIF))

            z.close()
            apk.seek(0)

            yield apk


class TestSigning(Base):

    def test_sign_and_verify(self):
        self.stor.get_app_key.return_value = self.open_keystore()

        with self.unsigned_apk() as apk:
            signed_fp = signer.sign(self.apk_id, apk)

            signed_fp.seek(0)
            output = signer.jarsigner(['-verify', '-verbose', signed_fp.name])

            buf = []
            for ln in output.splitlines():
                if ln.startswith('Warning:'):
                    # Strip out all trailing warnings.
                    break
                buf.append(ln)

            buf = '\n'.join(buf)
            assert buf.strip().endswith('jar verified.'), buf

    @mock.patch('apk_signer.sign.signer.jarsigner')
    def test_no_keystore(self, jarsigner):
        self.stor.get_app_key.side_effect = NoSuchKey

        with self.unsigned_apk() as apk:
            signer.sign(self.apk_id, apk)

        # Asset key store is saved.
        self.stor.put_app_key.assert_called_with(mock.ANY, self.apk_id)

    @mock.patch('apk_signer.sign.signer.gen_keystore')
    def test_collision(self, gen_keystore):
        gen_keystore.return_value = self.open_keystore().name
        self.stor.put_app_key.side_effect = AppKeyAlreadyExists
        with self.assertRaises(SigningError):
            signer.make_keystore(self.apk_id)


class TestFindExecutable(TestCase):

    def test_missing(self):
        with self.assertRaises(EnvironmentError):
            signer.find_executable('nope')

    def test_ok(self):
        signer.find_executable('keytool')


def asset(fn):
    return os.path.join(os.path.dirname(__file__), 'assets', fn)
