from django.core.urlresolvers import reverse

from mock import patch
from nose.tools import eq_

from apk_signer.base.tests import TestCase


class TestAuthView(TestCase):

    def test_get(self):
        res = self.client.get(reverse('system.auth'))
        self.assert2x(res)
        eq_(self.json(res),
            {'message': 'GET authentication successful'})

    def test_post(self):
        res = self.client.post(reverse('system.auth'))
        self.assert2x(res)
        eq_(self.json(res),
            {'message': 'POST authentication successful'})


class TestCEFView(TestCase):

    @patch('apk_signer.system.views.log_cef')
    def test(self, cef):
        eq_(self.json(self.client.get(reverse('system.cef'))),
            {'message': 'CEF messages sent'})
        assert cef.called


class TestLogView(TestCase):

    @patch('apk_signer.system.views.log')
    def test(self, log):
        eq_(self.json(self.client.get(reverse('system.log'))),
            {'message': 'messages logged on server'})
        assert log.info.called
        assert log.error.called


class TestTraceView(TestCase):

    def test(self):
        with self.assertRaises(RuntimeError):
            self.client.post(reverse('system.trace'))


class TestStatsView(TestCase):

    @patch('apk_signer.system.views.statsd')
    def test(self, statsd):
        self.assert2x(self.client.get(reverse('system.stats')))
        assert statsd.incr.called


class TestToolsView(TestCase):

    def test_ok(self):
        res = self.json(self.client.get(reverse('system.tools')))
        eq_(res['detail']['success'], True)
        eq_(res['detail']['msg'], {'keytool': 'ok', 'jarsigner': 'ok'})

    @patch('apk_signer.sign.signer.find_executable')
    def test_not_ok(self, find_executable):
        find_executable.side_effect = EnvironmentError
        res = self.json(self.client.get(reverse('system.tools')),
                        expected_status=409)
        eq_(res['detail']['success'], False)
        eq_(res['detail']['msg'],
            {'keytool': 'MISSING', 'jarsigner': 'MISSING'})
