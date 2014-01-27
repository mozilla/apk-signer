from django.core.urlresolvers import reverse

from nose.tools import eq_

from apk_signer.base.tests import TestCase


class TestAuthView(TestCase):

    def data(self):
        return {
            'unsigned_apk_s3_path': '/path/to/unsigned/file.apk',
            'unsigned_apk_s3_hash': 'xyxyxy',
        }

    def post(self, data=None):
        data = data or self.data()
        return self.client.post(reverse('sign'), data=data)

    def test_missing_s3_path(self):
        data = self.data()
        del data['unsigned_apk_s3_path']
        eq_(self.post(data).status_code, 400)

    def test_missing_s3_hash(self):
        data = self.data()
        del data['unsigned_apk_s3_hash']
        eq_(self.post(data).status_code, 400)
