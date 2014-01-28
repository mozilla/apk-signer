from django.core.urlresolvers import reverse

import mock
from nose.tools import eq_

from apk_signer.base.tests import TestCase


class SignTestBase(TestCase):

    def setUp(self):
        self.key_path = '/path/to/unsigned/file.apk'

    def data(self):
        return {
            'unsigned_apk_s3_path': self.key_path,
            'unsigned_apk_s3_hash': 'xyxyxy',
        }

    def post(self, data=None):
        data = data or self.data()
        return self.client.post(reverse('sign'), data=data)


class TestSignView(SignTestBase):

    def test_missing_s3_path(self):
        data = self.data()
        del data['unsigned_apk_s3_path']
        eq_(self.post(data).status_code, 400)

    def test_missing_s3_hash(self):
        data = self.data()
        del data['unsigned_apk_s3_hash']
        eq_(self.post(data).status_code, 400)


class TestSignedStorage(SignTestBase):

    def setUp(self):
        super(TestSignedStorage, self).setUp()

        p = mock.patch('apk_signer.sign.views.storage')
        storage = p.start()
        self.addCleanup(p.stop)
        self.get_apk = storage.get_apk
        self.put_signed_apk = storage.put_signed_apk

    def test_fetch_ok(self):
        self.post()
        self.get_apk.assert_called_with(self.key_path)

    def test_put_ok(self):
        self.post()
        # TODO: validate the new APK path.
        self.put_signed_apk.assert_called_with(mock.ANY, mock.ANY)
