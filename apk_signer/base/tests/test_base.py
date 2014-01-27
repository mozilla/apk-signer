from django import forms

from nose.tools import eq_
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from apk_signer.base import APIView

from . import TestCase


class FakeForm(forms.Form):
    foo = forms.CharField()


class FormView(APIView):

    def post(self, request):
        form = FakeForm(request.POST)
        if not form.is_valid():
            return self.form_errors([form])

        return Response({'result': 'not supposed to see this'})


class TestAPIView(TestCase):

    def test_form_error(self):
        view = FormView().as_view()
        res = view(APIRequestFactory().post('/', {}))  # missing fields
        res.render()
        eq_(self.json(res, expected_status=400),
            {'error': {'foo': ['This field is required.']}})
