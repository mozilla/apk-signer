from django_statsd.clients import statsd
from commonware.log import getLogger
from rest_framework.response import Response

from apk_signer.base import APIView, log_cef, UnprotectedAPIView
from apk_signer.sign import signer


log = getLogger(__name__)


class AuthView(APIView):

    def get(self, request):
        return Response({'message': 'GET authentication successful'})

    def post(self, request):
        return Response({'message': 'POST authentication successful'})


class CEFView(UnprotectedAPIView):

    def get(self, request):
        log_cef('this is a test message', request, severity=5)
        return Response({'message': 'CEF messages sent'})


class LogView(UnprotectedAPIView):

    def get(self, request):
        log.info('This is an info message')
        log.error('This is an error message')
        return Response({'message': 'messages logged on server'})


class StatsView(UnprotectedAPIView):

    def get(self, request):
        key = 'apk_signer.system_check'
        statsd.incr(key)
        return Response({'message': '{key} incremented'.format(key=key)})


class TraceView(UnprotectedAPIView):

    def post(self, request):
        raise RuntimeError(
            'This is a synthetic exception. Carry on, nothing to see')


class ToolsView(UnprotectedAPIView):

    def get(self, request):
        ok = True
        msg = {}
        for name in ('keytool', 'jarsigner'):
            result = 'ok'
            try:
                signer.find_executable(name)
            except EnvironmentError:
                log.exception('could not find executable {n}'.format(n=name))
                ok = False
                result = 'MISSING'
            msg[name] = result

        return Response({'success': ok, 'msg': msg})
