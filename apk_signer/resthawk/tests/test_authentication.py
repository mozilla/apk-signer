from django.conf import settings
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

import mock
from mohawk import Receiver, Sender
from mohawk.exc import MacMismatch
from nose.tools import eq_
from rest_framework.exceptions import AuthenticationFailed

from .. import (DummyUser, HawkAuthentication, lookup_credentials)
from ..middleware import HawkResponseMiddleware


class BaseTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.url = 'http://testserver/'
        self.credentials_id = 'apk-factory'
        self.credentials = settings.HAWK_CREDENTIALS[self.credentials_id]

    def _request(self, sender, method='GET', content_type='text/plain',
                 url=None, **kw):
        if not url:
            url = self.url

        do_request = getattr(self.factory, method.lower())
        return do_request(self.url,
                          HTTP_AUTHORIZATION=sender.request_header,
                          content_type=content_type,
                          data=kw.pop('data', ''),
                          **kw)

    def _sender(self, method='GET', content_type='text/plain', url=None,
                credentials=None, content=''):
        if not url:
            url = self.url
        if not credentials:
            credentials = self.credentials
        return Sender(credentials,
                      url, method,
                      content=content,
                      content_type=content_type)


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
        sender = self._sender(content_type='')
        req = self._request(sender, content_type='')
        assert isinstance(self.auth.authenticate(req)[0], DummyUser), (
            'Expected a successful authentication returning a dummy user')

    def test_hawk_post(self):
        post_data = 'one=1&two=2&three=3'
        content_type = 'application/x-www-form-urlencoded'
        method = 'POST'
        sender = self._sender(content=post_data,
                              content_type=content_type,
                              method=method)
        req = self._request(sender,
                            content_type=content_type,
                            data=post_data,
                            method=method)

        assert isinstance(self.auth.authenticate(req)[0], DummyUser), (
            'Expected a successful authentication returning a dummy user')

    def test_hawk_post_wrong_sig(self):
        post_data = 'one=1&two=2&three=3'
        content_type = 'application/x-www-form-urlencoded'
        method = 'POST'
        sender = self._sender(content=post_data,
                              content_type=content_type,
                              method=method)

        # This should fail the signature check.
        post_data = '{0}&TAMPERED_WITH=true'.format(post_data)

        req = self._request(sender,
                            content_type=content_type,
                            data=post_data,
                            method=method)

        with self.assertRaises(AuthenticationFailed) as exc:
            self.auth.authenticate(req)

        eq_(exc.exception.detail, 'authentication failed')

    def test_hawk_get_wrong_sig(self):
        sender = self._sender(url='http://realsite.com')
        req = self._request(sender, url='http://FAKE-SITE.com')

        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(req)

    def test_unknown_creds(self):
        wrong_creds = {'id': 'not-a-valid-id',
                       'key': 'not really',
                       'algorithm': 'sha256'}

        sender = self._sender(credentials=wrong_creds)
        req = self._request(sender)

        with self.assertRaises(AuthenticationFailed) as exc:
            self.auth.authenticate(req)

        eq_(exc.exception.detail, 'authentication failed')


@mock.patch.object(settings, 'SKIP_HAWK_AUTH', False)
class TestMiddleware(BaseTest):

    def setUp(self):
        super(TestMiddleware, self).setUp()
        self.mw = HawkResponseMiddleware()

    def request(self, method='GET', content_type='text/plain', url=None):
        if not url:
            url = self.url
        sender = self._sender(method=method, content_type=content_type)
        req = self._request(sender, method=method, content_type=content_type)
        self.authorize_request(sender, req, url=url, method=method)

        return req, sender

    def authorize_request(self, sender, req, url=None, method='GET'):
        if not url:
            url = self.url
        # Simulate how a view authorizes a request.
        receiver = Receiver(lookup_credentials,
                            sender.request_header,
                            url, method,
                            content=req.body,
                            content_type=req.META['content_type'])
        req.hawk_receiver = receiver

    def accept_response(self, response, sender):
        sender.accept_response(response['Server-Authorization'],
                               content=response.content,
                               content_type=response['Content-Type'])

    def test_respond_ok(self):
        req, sender = self.request()

        response = HttpResponse('the response')
        res = self.mw.process_response(req, response)
        self.accept_response(res, sender)

    def test_respond_with_bad_content(self):
        req, sender = self.request()

        response = HttpResponse('the response')
        res = self.mw.process_response(req, response)

        response.content = 'TAMPERED WITH'

        with self.assertRaises(MacMismatch):
            self.accept_response(res, sender)

    def test_respond_with_bad_content_type(self):
        req, sender = self.request()

        response = HttpResponse('the response')
        res = self.mw.process_response(req, response)

        response['Content-Type'] = 'TAMPERED WITH'

        with self.assertRaises(MacMismatch):
            self.accept_response(res, sender)
