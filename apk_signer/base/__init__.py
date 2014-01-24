from django.conf import settings

from commonware.log import getLogger
from cef import log_cef as orig_log_cef
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

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


class UnprotectedAPIView(APIView):
    """
    An APIView that is not protected by global authentication (e.g. Hawk).
    """
    authentication_classes = []
    permission_classes = [AllowAny]
