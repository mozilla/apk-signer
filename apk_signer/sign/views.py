from django import forms

from django_paranoia.forms import ParanoidForm
from commonware.log import getLogger
from rest_framework.response import Response

from apk_signer.base import APIView
from apk_signer import storage


log = getLogger(__name__)


class SignForm(ParanoidForm):
    unsigned_apk_s3_path = forms.CharField()
    unsigned_apk_s3_hash = forms.CharField()
    signed_apk_s3_path = forms.CharField()


class SignView(APIView):

    def post(self, request):
        form = SignForm(request.POST)
        if not form.is_valid():
            return self.form_errors([form])

        src = form.cleaned_data['unsigned_apk_s3_path']
        dest = form.cleaned_data['signed_apk_s3_path']

        with storage.get_apk(src) as fp:
            fp.seek(0)
            log.info('about to sign APK from {src} to {dest}'
                     .format(src=src, dest=dest))
            # TODO: sign the raw APK and put the signed APK on S3.
            storage.put_signed_apk(fp, dest)

        return Response({'signed_apk_s3_url': 'not implemented'})
