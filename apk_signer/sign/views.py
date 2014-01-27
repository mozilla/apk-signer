from django import forms

from django_paranoia.forms import ParanoidForm
from commonware.log import getLogger
from rest_framework.response import Response

from apk_signer.base import APIView


log = getLogger(__name__)


class SignForm(ParanoidForm):
    unsigned_apk_s3_path = forms.CharField()
    unsigned_apk_s3_hash = forms.CharField()


class SignView(APIView):

    def post(self, request):
        form = SignForm(request.POST)
        if not form.is_valid():
            return self.form_errors([form])
        raise NotImplementedError('TODO: fetch from S3, sign/push APK to S3')
        return Response({'signed_apk_s3_url': ''})
