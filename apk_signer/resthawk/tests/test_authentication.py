from django.conf import settings
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

import hawk
import mock
from nose.tools import eq_
from rest_framework.exceptions import AuthenticationFailed

from .. import (DummyUser, HawkAuthentication, lookup_credentials,
                make_hawk_request)
from ..middleware import HawkResponseMiddleware


class BaseTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = 'http://testserver/'
        self.credentials = settings.HAWK_CREDENTIALS['apk-factory']

    def opt(self, override=None):
        opt = {
            'credentials': self.credentials,
            'ext': '',
            'app': '',
            'dlg': '',
            'payload': '',
            'contentType': None,
        }
        opt.update(override or {})
        return opt


@mock.patch.object(settings, 'SKIP_HAWK_AUTH', False)
class TestAuthentication(BaseTest):

    def setUp(self):
        super(TestAuthentication, self).setUp()
        self.auth = HawkAuthentication()

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


@mock.patch.object(settings, 'SKIP_HAWK_AUTH', False)
class TestMiddleware(BaseTest):

    def setUp(self):
        super(TestMiddleware, self).setUp()
        self.mw = HawkResponseMiddleware()

    def request(self, method='GET'):
        opt = self.opt(override={'payload': ''})
        header = hawk.client.header(self.url, method, options=opt)
        req = self.factory.get(self.url, HTTP_AUTHORIZATION=header['field'])

        # Simulate how the view caches artifacts.
        server = hawk.Server(make_hawk_request(req), lookup_credentials)
        artifacts = server.authenticate({'payload': req.body})
        req.META['_HAWK_ARTIFACTS'] = artifacts

        return req, header['artifacts']

    def verify(self, response, artifacts):
        return hawk.client.authenticate(
                        {'headers': response},
                        self.credentials,
                        artifacts,
                        {'payload': response.content, 'required': True})

    def test_ok(self):
        req, artifacts = self.request()

        response = HttpResponse('the response')
        res = self.mw.process_response(req, response)

        eq_(self.verify(res, artifacts), True)
        #assert 0
