from django.conf import settings
from django.test import RequestFactory, TestCase

import hawk
import mock
from nose.tools import eq_
from rest_framework.exceptions import AuthenticationFailed

from .. import DummyUser, HawkAuthentication


@mock.patch.object(settings, 'SKIP_HAWK_AUTH', False)
class TestAuthentication(TestCase):

    def setUp(self):
        self.auth = HawkAuthentication()
        self.factory = RequestFactory()
        self.url = 'http://testserver/'

    def opt(self, override=None):
        opt = {
            'credentials': settings.HAWK_CREDENTIALS['apk-factory'],
            'ext': '',
            'app': '',
            'dlg': '',
            'payload': '',
            'contentType': None,
        }
        opt.update(override or {})
        return opt

    def test_missing_auth_header(self):
        req = self.factory.get('/')
        with self.assertRaises(AuthenticationFailed) as exc:
            self.auth.authenticate(req)

        eq_(exc.exception.detail, 'missing authorization header')

    def test_bad_auth_header(self):
        req = self.factory.get('/', HTTP_AUTHORIZATION='not really')
        with self.assertRaises(AuthenticationFailed) as exc:
            self.auth.authenticate(req)

        eq_(exc.exception.detail, 'authentication failed')

    def test_hawk_get(self):
        header = hawk.client.header(self.url, 'GET', options=self.opt())
        req = self.factory.get(self.url, HTTP_AUTHORIZATION=header['field'])
        assert isinstance(self.auth.authenticate(req)[0], DummyUser), (
                'Expected a successful authentication returning a dummy user')

    def test_hawk_post(self):
        post_data = 'one=1&two=2&three=3'
        content_type = 'multipart/form-data'
        header = hawk.client.header(self.url, 'POST',
                    options=self.opt({'payload': post_data,
                                      'contentType': content_type}))
        req = self.factory.post(self.url, HTTP_AUTHORIZATION=header['field'],
                                content_type=content_type,
                                data=post_data)

        assert isinstance(self.auth.authenticate(req)[0], DummyUser), (
                'Expected a successful authentication returning a dummy user')

    def test_hawk_post_wrong_sig(self):
        post_data = 'one=1&two=2&three=3'
        header = hawk.client.header(self.url, 'POST',
                                    options=self.opt({'payload': post_data}))

        # This should fail the signature check.
        post_data = '{0}&TAMPERED_WITH=true'.format(post_data)

        req = self.factory.post(self.url, HTTP_AUTHORIZATION=header['field'],
                                content_type='multipart/form-data',
                                data=post_data)

        with self.assertRaises(AuthenticationFailed) as exc:
            self.auth.authenticate(req)

        eq_(exc.exception.detail, 'authentication failed')

    def test_hawk_get_wrong_sig(self):
        header = hawk.client.header(self.url, 'GET', options=self.opt())

        req = self.factory.get(self.url, HTTP_AUTHORIZATION=header['field'],
                               # This should fail the signature check.
                               data=dict(TAMPERED_WITH=True))

        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(req)

    def test_unknown_creds(self):
        header = hawk.client.header(self.url, 'GET', options=self.opt({
            'credentials': {'id': 'not-a-valid-id',
                            'key': 'not really',
                            'algorithm': 'sha256'},
        }))
        req = self.factory.get(self.url, HTTP_AUTHORIZATION=header['field'])
        with self.assertRaises(AuthenticationFailed) as exc:
            self.auth.authenticate(req)

        eq_(exc.exception.detail, 'authentication failed')
