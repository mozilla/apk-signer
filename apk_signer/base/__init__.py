from django.conf import settings

from commonware.log import getLogger
from cef import log_cef as orig_log_cef
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView as RestAPIView

log = getLogger(__name__)
sys_cef_log = getLogger('apk_signer.cef')


def log_cef(msg, request, **kw):
    severity = kw.pop('severity', settings.CEF_DEFAULT_SEVERITY)
    cef_kw = {'msg': msg, 'signature': request.get_full_path(),
              'config': {
                  'cef.product': settings.CEF_PRODUCT,
                  'cef.vendor': settings.CEF_VENDOR,
                  'cef.version': settings.CEF_VERSION,
                  'cef.device_version': settings.CEF_DEVICE_VERSION,
                  'cef.file': getattr(settings, 'CEF_FILE', 'syslog')}}

    if severity > 2:
        # Log a copy of the CEF message but only for severe messages.
        # Messages lower than this could be every http request, etc.
        sys_cef_log.error('CEF Severity: {sev} Message: {msg}'
                          .format(sev=severity, msg=msg))

    # Allow the passing of additional cs* values.
    for k, v in kw.items():
        if k.startswith('cs'):
            cef_kw[k] = v

    orig_log_cef(msg, severity, request.META.copy(), **cef_kw)


def format_form_errors(forms):
    errors = {}
    if not isinstance(forms, list):
        forms = [forms]
    for f in forms:
        log.info('Error processing form: {0}'.format(f.__class__.__name__))
        if isinstance(f.errors, list):  # Cope with formsets.
            for e in f.errors:
                errors.update(e)
            continue
        errors.update(dict(f.errors.items()))

    return {'error': errors}


class APIView(RestAPIView):

    def form_errors(self, forms):
        return Response(format_form_errors(forms), status=400)


class UnprotectedAPIView(APIView):
    """
    An APIView that is not protected by global authentication (e.g. Hawk).
    """
    authentication_classes = []
    permission_classes = [AllowAny]
