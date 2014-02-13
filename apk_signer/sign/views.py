import hashlib

from django import forms

from django_paranoia.forms import ParanoidForm
from commonware.log import getLogger
from rest_framework.response import Response

from apk_signer.base import APIView
from apk_signer.exceptions import BadRequestError
from apk_signer.sign import signer
from apk_signer import storage


buf_size = 1024 * 1024  # 1MB buffer
log = getLogger(__name__)


class SignForm(ParanoidForm):
    apk_id = forms.CharField(max_length=1024)
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

        log.info('about to sign APK ID={id} from {src} to {dest}'
                 .format(src=src, dest=dest,
                         id=form.cleaned_data['apk_id']))

        with storage.get_apk(src) as fp:
            real_hash = checksum_hash(fp)
            claimed_hash = form.cleaned_data['unsigned_apk_s3_hash']
            log.info('Unsigned APK hash check: '
                     '{src} real={real} claimed={claimed}'
                     .format(src=src, real=real_hash,
                             claimed=claimed_hash))

            if real_hash != claimed_hash:
                raise BadRequestError('unsigned APK content '
                                      'hash check failed')

            with signer.sign(form.cleaned_data['apk_id'],
                             fp) as signed_fp:
                storage.put_signed_apk(signed_fp, dest)

        return Response({'signed_apk_s3_url': storage.signed_apk_url(dest)})


def checksum_hash(fp, buf_size=buf_size):
    m = hashlib.sha256()
    while 1:
        stuff = fp.read(buf_size)
        if stuff:
            m.update(stuff)
        else:
            break
    fp.seek(0)
    return m.hexdigest()
