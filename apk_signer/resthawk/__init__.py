"""
A Django-Restframework adapter for Hawk

https://github.com/hueniverse/hawk

TODO: liberate
"""
import logging
import pprint
import traceback
import urlparse

from django.conf import settings

import hawk
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission


log = logging.getLogger(__name__)


class DummyUser(object):
    pass


class HawkAuthentication(BaseAuthentication):

    def authenticate(self, request):
        on_success = (DummyUser(), None)
        if getattr(settings, 'SKIP_HAWK_AUTH', False):
            log.warn('Hawk authentication disabled via settings')
            return on_success

        if not request.META.get('HTTP_AUTHORIZATION'):
            raise AuthenticationFailed('missing authorization header')

        server = hawk.Server(self._make_hawk_request(request),
                             self._lookup_creds)
        try:
            server.authenticate({'payload': request.body})
        except Exception, exc:
            log.debug(traceback.format_exc())
            log.info('Hawk: denying access because of {cls}: {exc}'
                     .format(cls=exc.__class__.__name__, exc=exc))
            raise AuthenticationFailed('authentication failed')

        request.HAWK_AUTHENTICATED = True
        return on_success

    def _make_hawk_request(self, d_req):
        req = {'headers': {}}
        req['headers']['authorization'] = d_req.META.get('HTTP_AUTHORIZATION')
        req['contentType'] = d_req.META.get('CONTENT_TYPE')
        req['method'] = d_req.method

        url = urlparse.urlparse(d_req.build_absolute_uri())
        req['host'] = url.hostname
        req['port'] = url.port or '80'
        req['url'] = url.geturl()
        log.debug('hawk adapted django request: {0}'
                  .format(pprint.pformat(req)))
        return req

    def _lookup_creds(self, id):
        if id not in settings.HAWK_CREDENTIALS:
            raise LookupError('No Hawk ID of {id}'.format(id=id))
        return settings.HAWK_CREDENTIALS[id]
