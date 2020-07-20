import asyncio
import json
import os
from io import open
from typing import Type, Union

# httpretty currently doesn't work, but mocket with the compat interface
# does.
from mocket.plugins.httpretty import HTTPretty as httpretty, httprettified  # type: ignore

from minfraud.errors import (
    HTTPError,
    InvalidRequestError,
    AuthenticationError,
    InsufficientFundsError,
    MinFraudError,
    PermissionRequiredError,
)
from minfraud.models import Factors, Insights, Score
from minfraud.webservice import AsyncClient, Client

import unittest


class BaseTest(unittest.TestCase):
    client_class: Union[Type[AsyncClient], Type[Client]] = Client

    def setUp(self):
        self.client = self.client_class(42, "abcdef123456")

        test_dir = os.path.join(os.path.dirname(__file__), "data")
        with open(os.path.join(test_dir, self.request_file), encoding="utf-8") as file:
            content = file.read()
        self.full_request = json.loads(content)

        with open(os.path.join(test_dir, self.response_file), encoding="utf-8") as file:
            self.response = file.read()

    base_uri = "https://minfraud.maxmind.com/minfraud/v2.0"

    @httprettified
    def test_invalid_auth(self):
        for error in (
            "ACCOUNT_ID_REQUIRED",
            "AUTHORIZATION_INVALID",
            "LICENSE_KEY_REQUIRED",
            "USER_ID_REQUIRED",
        ):
            with self.assertRaisesRegex(AuthenticationError, "Invalid auth"):
                self.create_error(
                    text=u'{{"code":"{0:s}","error":"Invalid auth"}}'.format(error),
                    status_code=401,
                )

    @httprettified
    def test_invalid_request(self):
        with self.assertRaisesRegex(InvalidRequestError, "IP invalid"):
            self.create_error(text='{"code":"IP_ADDRESS_INVALID","error":"IP invalid"}')

    @httprettified
    def test_300_error(self):
        with self.assertRaisesRegex(
            HTTPError, "Received an unexpected HTTP status \(300\) for"
        ):
            self.create_error(status_code=300)

    @httprettified
    def test_permission_required(self):
        with self.assertRaisesRegex(PermissionRequiredError, "permission"):
            self.create_error(
                text='{"code":"PERMISSION_REQUIRED","error":"permission required"}',
                status_code=403,
            )

    @httprettified
    def test_400_with_invalid_json(self):
        with self.assertRaisesRegex(
            HTTPError,
            "Received a 400 error but it did not include the expected JSON"
            " body: b?'?{blah}'?",
        ):
            self.create_error(text="{blah}")

    @httprettified
    def test_400_with_no_body(self):
        with self.assertRaisesRegex(HTTPError, "Received a 400 error with no body"):
            self.create_error()

    @httprettified
    def test_400_with_unexpected_content_type(self):
        with self.assertRaisesRegex(
            HTTPError, "Received a 400 with the following body: b?'?plain'?"
        ):
            self.create_error(content_type="text/plain", text="plain")

    @httprettified
    def test_400_without_json_body(self):
        with self.assertRaisesRegex(
            HTTPError,
            "Received a 400 error but it did not include the expected JSON"
            " body: b?'?plain'?",
        ):
            self.create_error(text="plain")

    @httprettified
    def test_400_with_unexpected_json(self):
        with self.assertRaisesRegex(
            HTTPError,
            "Error response contains JSON but it does not specify code or"
            ' error keys: b?\'?{"not":"expected"}\'?',
        ):
            self.create_error(text='{"not":"expected"}')

    @httprettified
    def test_500_error(self):
        with self.assertRaisesRegex(HTTPError, "Received a server error \(500\) for"):
            self.create_error(status_code=500)

    def create_error(self, status_code=400, text="", content_type=None):
        uri = "/".join(
            [self.base_uri, "transactions", "report"]
            if self.type == "report"
            else [self.base_uri, self.type]
        )
        if content_type is None:
            content_type = (
                "application/json"
                if self.type == "report"
                else "application/vnd.maxmind.com-error+json; charset=UTF-8; version=2.0"
            )
        httpretty.register_uri(
            httpretty.POST,
            uri=uri,
            status=status_code,
            body=text,
            content_type=content_type,
        )
        return self.run_client(getattr(self.client, self.type)(self.full_request))

    def create_success(self, text=None, client=None, request=None):
        uri = "/".join(
            [self.base_uri, "transactions", "report"]
            if self.type == "report"
            else [self.base_uri, self.type]
        )
        httpretty.register_uri(
            httpretty.POST,
            uri=uri,
            status=204 if self.type == "report" else 200,
            body=self.response if text is None else text,
            content_type="application/vnd.maxmind.com-minfraud-{0}+json; charset=UTF-8; version=2.0".format(
                self.type
            ),
        )
        if client is None:
            client = self.client
        if request is None:
            request = self.full_request
        print(client)
        return self.run_client(getattr(client, self.type)(request))

    def run_client(self, v):
        return v

    @httprettified
    def test_named_constructor_args(self):
        id = "47"
        key = "1234567890ab"
        for client in (
            self.client_class(account_id=id, license_key=key),
            self.client_class(account_id=id, license_key=key),
        ):
            self.assertEqual(client._account_id, id)
            self.assertEqual(client._license_key, key)

    @httprettified
    def test_missing_constructor_args(self):
        with self.assertRaises(TypeError):
            self.client_class(license_key="1234567890ab")

        with self.assertRaises(TypeError):
            self.client_class("47")


class BaseTransactionTest(BaseTest):
    def has_ip_location(self):
        return self.type in ["factors", "insights"]

    @httprettified
    def test_200(self):
        model = self.create_success()
        response = json.loads(self.response)
        if self.has_ip_location():
            response["ip_address"]["_locales"] = ("en",)
        self.assertEqual(self.cls(response), model)
        if self.has_ip_location():
            self.assertEqual("United Kingdom", model.ip_address.country.name)

    @httprettified
    def test_200_on_request_with_nones(self):
        model = self.create_success(
            request={
                "device": {"ip_address": "81.2.69.160", "accept_language": None},
                "event": {"shop_id": None},
                "shopping_cart": [{"category": None, "quantity": 2,}, None],
            }
        )
        response = self.response
        self.assertEqual(0.01, model.risk_score)

    @httprettified
    def test_200_with_locales(self):
        locales = ("fr",)
        client = self.client_class(42, "abcdef123456", locales=locales)
        model = self.create_success(client=client)
        response = json.loads(self.response)
        if self.has_ip_location():
            response["ip_address"]["_locales"] = locales
        self.assertEqual(self.cls(response), model)
        if self.has_ip_location():
            self.assertEqual("Royaume-Uni", model.ip_address.country.name)
            self.assertEqual("Londres", model.ip_address.city.name)

    @httprettified
    def test_200_with_no_body(self):
        with self.assertRaisesRegex(
            MinFraudError,
            "Received a 200 response but could not decode the response as"
            " JSON: b?'?'?",
        ):
            self.create_success(text="")

    @httprettified
    def test_200_with_invalid_json(self):
        with self.assertRaisesRegex(
            MinFraudError,
            "Received a 200 response but could not decode the response as"
            " JSON: b?'?{'?",
        ):
            self.create_success(text="{")

    @httprettified
    def test_insufficient_funds(self):
        with self.assertRaisesRegex(InsufficientFundsError, "out of funds"):
            self.create_error(
                text='{"code":"INSUFFICIENT_FUNDS","error":"out of funds"}',
                status_code=402,
            )


class TestFactors(BaseTransactionTest):
    type = "factors"
    cls = Factors
    request_file = "full-transaction-request.json"
    response_file = "factors-response.json"


class TestInsights(BaseTransactionTest):
    type = "insights"
    cls = Insights
    request_file = "full-transaction-request.json"
    response_file = "insights-response.json"


class TestScore(BaseTransactionTest):
    type = "score"
    cls = Score
    request_file = "full-transaction-request.json"
    response_file = "score-response.json"


class TestReportTransaction(BaseTest):
    type = "report"
    request_file = "full-report-request.json"
    response_file = "report-response.json"

    @httprettified
    def test_204(self):
        self.create_success()

    @httprettified
    def test_204_on_request_with_nones(self):
        self.create_success(
            request={
                "ip_address": "81.2.69.60",
                "tag": "chargeback",
                "chargeback_code": None,
                "maxmind_id": None,
                "minfraud_id": None,
                "notes": None,
            }
        )


class AsyncBase:
    def setUp(self):
        self._loop = asyncio.new_event_loop()
        super().setUp()

    def tearDown(self):
        self._loop.run_until_complete(self.client.close())
        self._loop.close()
        super().tearDown()

    def run_client(self, v):
        return self._loop.run_until_complete(v)


class TestAsyncFactors(AsyncBase, TestFactors):
    client_class = AsyncClient


class TestAsyncInsights(AsyncBase, TestInsights):
    client_class = AsyncClient


class TestAsyncScore(AsyncBase, TestScore):
    client_class = AsyncClient


class TestAsyncReportTransaction(AsyncBase, TestReportTransaction):
    client_class = AsyncClient


del BaseTest, BaseTransactionTest
