from django_statsd.clients import statsd
from commonware.log import getLogger
from rest_framework.views import APIView
from rest_framework.response import Response

from apk_signer.base import log_cef


log = getLogger(__name__)


class CEFView(APIView):

    def get(self, request):
        log_cef('this is a test message', request, severity=5)
        return Response({'message': 'CEF messages sent'})


class LogView(APIView):

    def get(self, request):
        log.info('This is an info message')
        log.error('This is an error message')
        return Response({'message': 'messages logged on server'})


class StatsView(APIView):

    def get(self, request):
        key = 'apk_signer.system_check'
        statsd.incr(key)
        return Response({'message': '{key} incremented'.format(key=key)})


class TraceView(APIView):

    def post(self, request):
        raise RuntimeError(
            'This is a synthetic exception. Carry on, nothing to see')
