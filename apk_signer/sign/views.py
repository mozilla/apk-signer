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


class SignView(APIView):

    def post(self, request):
        form = SignForm(request.POST)
        if not form.is_valid():
            return self.form_errors([form])

        path = form.cleaned_data['unsigned_apk_s3_path']
        with storage.get_apk(path) as fp:
            log.info('about to sign APK at {path}'.format(path=path))
            # TODO: make a real signed path with manifest URL.
            new_path = 'apk_id/signed/signed.apk'
            storage.put_signed_apk(fp, new_path)

        return Response({'signed_apk_s3_url': 'not implemented'})
