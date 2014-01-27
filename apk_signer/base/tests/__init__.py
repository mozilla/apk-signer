import json

from django import test

from nose.tools import eq_


class TestCase(test.TestCase):

    def assert2x(self, response):
        assert str(response.status_code).startswith('2'), (
                'Unexpected status code: {code}; response={res}[...]'
                .format(code=response.status_code,
                        # Truncate responses to avoid spewing garbage.
                        # Typically it will be a short JSON dict.
                        res=response.content[0:512]))

    def json(self, response, expected_status=200,
             expected_type='application/json'):
        eq_(response.status_code, expected_status,
            'Status {actual} != {expected} (expected); response={res}'
            .format(actual=response.status_code,
                    expected=expected_status,
                    res=response.content))
        eq_(response['Content-Type'], expected_type, response.content)
        return json.loads(response.content)
