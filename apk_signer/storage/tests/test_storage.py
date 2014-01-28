import tempfile

from apk_signer.base.tests import TestCase

import mock

from apk_signer import storage
from apk_signer.storage import NoSuchKey


class TestStorage(TestCase):

    def setUp(self):
        self.key_path = '/some/file.apk'

        p = mock.patch('apk_signer.storage.bucket')
        self.set_bucket(p.start())
        self.addCleanup(p.stop)

    def set_bucket(self, bucket):
        self.bkt = mock.Mock()
        bucket.return_value = self.bkt
        self.key = mock.Mock()
        self.bkt.get_key.return_value = self.key
        self.new_key = mock.Mock()
        self.bkt.new_key.return_value = self.new_key

    def test_get_apk(self):
        storage.get_apk(self.key_path)

        self.bkt.get_key.assert_called_with(self.key_path)
        assert self.key.get_contents_to_file.called

    def test_get_apk_fail(self):
        self.bkt.get_key.return_value = None

        with self.assertRaises(NoSuchKey):
            storage.get_apk(self.key_path)

    def test_put_ok(self):
        with tempfile.TemporaryFile() as fp:
            storage.put_signed_apk(fp, self.key_path)

        self.bkt.new_key.assert_called_with(self.key_path)
        self.new_key.send_file.assert_called_with(fp)
        self.new_key.set_acl.assert_called_with('public-read')
