import os
import sys

import json
import requests_mock
from minfraud.errors import HTTPError, InvalidRequestError, \
    AuthenticationError, InsufficientFundsError, MinFraudError, \
    PermissionRequiredError
from minfraud.models import Factors, Insights, Score
from minfraud.webservice import Client

if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest

if sys.version_info[0] == 2:
    unittest.TestCase.assertRaisesRegex = unittest.TestCase.assertRaisesRegexp
    unittest.TestCase.assertRegex = unittest.TestCase.assertRegexpMatches


class BaseTest(object):
    def setUp(self):
        self.client = Client(42, 'abcdef123456')
        test_dir = os.path.join(os.path.dirname(__file__), 'data')
        with open(os.path.join(test_dir, 'full-request.json'), 'r') as file:
            content = file.read()
        self.full_request = json.loads(content)
        with open(
                os.path.join(test_dir, '{0}-response.json'.format(self.type)),
                'r') as file:
            self.response = file.read()

    base_uri = 'https://minfraud.maxmind.com/minfraud/v2.0/'

    def has_ip_location(self):
        return self.type in ['factors', 'insights']

    def test_200(self):
        model = self.create_success()
        response = json.loads(self.response)
        if self.has_ip_location():
            response['ip_address']['_locales'] = ('en', )
        self.assertEqual(self.cls(response), model)
        if self.has_ip_location():
            self.assertEqual('United Kingdom', model.ip_address.country.name)

    def test_200_on_request_with_nones(self):
        model = self.create_success(request={
            'device': {
                'ip_address': '81.2.69.160',
                'accept_language': None
            },
            'event': {
                'shop_id': None
            },
            'shopping_cart': [{
                'category': None,
                'quantity': 2,
            }, None],
        })
        response = self.response
        self.assertEqual(0.01, model.risk_score)

    def test_200_with_locales(self):
        locales = ('fr', )
        client = Client(42, 'abcdef123456', locales=locales)
        model = self.create_success(client=client)
        response = json.loads(self.response)
        if self.has_ip_location():
            response['ip_address']['_locales'] = locales
        self.assertEqual(self.cls(response), model)
        if self.has_ip_location():
            self.assertEqual('Royaume-Uni', model.ip_address.country.name)
            self.assertEqual('Londres', model.ip_address.city.name)

    def test_200_with_no_body(self):
        with self.assertRaisesRegex(
                MinFraudError,
                "Received a 200 response but could not decode the response as"
                " JSON: b?'?'?"):
            self.create_success(text='')

    def test_200_with_invalid_json(self):
        with self.assertRaisesRegex(
                MinFraudError,
                "Received a 200 response but could not decode the response as"
                " JSON: b?'?{'?"):
            self.create_success(text='{')

    def test_insufficient_funds(self):
        with self.assertRaisesRegex(InsufficientFundsError, 'out of funds'):
            self.create_error(
                text='{"code":"INSUFFICIENT_FUNDS","error":"out of funds"}',
                status_code=402)

    def test_invalid_auth(self):
        for error in ('AUTHORIZATION_INVALID', 'LICENSE_KEY_REQUIRED',
                      'USER_ID_REQUIRED'):
            with self.assertRaisesRegex(AuthenticationError, 'Invalid auth'):
                self.create_error(
                    text=u'{{"code":"{0:s}","error":"Invalid auth"}}'.format(
                        error),
                    status_code=401)

    def test_invalid_request(self):
        with self.assertRaisesRegex(InvalidRequestError, 'IP invalid'):
            self.create_error(
                text='{"code":"IP_ADDRESS_INVALID","error":"IP invalid"}')

    def test_permission_required(self):
        with self.assertRaisesRegex(PermissionRequiredError, 'permission'):
            self.create_error(
                text=
                '{"code":"PERMISSION_REQUIRED","error":"permission required"}',
                status_code=403)

    def test_400_with_invalid_json(self):
        with self.assertRaisesRegex(
                HTTPError,
                "Received a 400 error but it did not include the expected JSON"
                " body: b?'?{blah}'?"):
            self.create_error(text='{blah}')

    def test_400_with_no_body(self):
        with self.assertRaisesRegex(HTTPError,
                                    'Received a 400 error with no body'):
            self.create_error()

    def test_400_with_unexpected_content_type(self):
        with self.assertRaisesRegex(
                HTTPError,
                "Received a 400 with the following body: b?'?plain'?"):
            self.create_error(headers={'Content-Type': 'text/plain'},
                              text='plain')

    def test_400_without_json_body(self):
        with self.assertRaisesRegex(
                HTTPError,
                "Received a 400 error but it did not include the expected JSON"
                " body: b?'?plain'?"):
            self.create_error(text='plain')

    def test_400_with_unexpected_json(self):
        with self.assertRaisesRegex(
                HTTPError,
                'Error response contains JSON but it does not specify code or'
                ' error keys: b?\'?{"not":"expected"}\'?'):
            self.create_error(text='{"not":"expected"}')

    def test_300_error(self):
        with self.assertRaisesRegex(
                HTTPError, 'Received an unexpected HTTP status \(300\) for'):
            self.create_error(status_code=300)

    def test_500_error(self):
        with self.assertRaisesRegex(HTTPError,
                                    'Received a server error \(500\) for'):
            self.create_error(status_code=500)

    @requests_mock.mock()
    def create_error(self, mock, status_code=400, text='', headers=None):
        if headers is None:
            headers = {
                'Content-Type':
                'application/vnd.maxmind.com-error+json; charset=UTF-8;'
                ' version=2.0'
            }
        mock.post(self.base_uri + self.type,
                  status_code=status_code,
                  text=text,
                  headers=headers)
        return getattr(self.client, self.type)(self.full_request)

    @requests_mock.mock()
    def create_success(self,
                       mock,
                       text=None,
                       headers=None,
                       client=None,
                       request=None):
        if headers is None:
            headers = {
                'Content-Type':
                'application/vnd.maxmind.com-minfraud-{0}+json;'
                ' charset=UTF-8; version=2.0'.format(self.type)
            }
        if text is None:
            text = self.response
        mock.post(self.base_uri + self.type,
                  status_code=200,
                  text=text,
                  headers=headers)
        if client is None:
            client = self.client
        if request is None:
            request = self.full_request
        return getattr(client, self.type)(request)


class TestFactors(BaseTest, unittest.TestCase):
    type = 'factors'
    cls = Factors


class TestInsights(BaseTest, unittest.TestCase):
    type = 'insights'
    cls = Insights


class TestScore(BaseTest, unittest.TestCase):
    type = 'score'
    cls = Score
