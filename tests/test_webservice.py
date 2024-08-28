import asyncio
import json
import os
from io import open
from typing import Type, Union
from pytest_httpserver import HTTPServer
import pytest

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

import minfraud.webservice
import unittest

minfraud.webservice._SCHEME = "http"


class BaseTest(unittest.TestCase):
    client_class: Union[Type[AsyncClient], Type[Client]] = Client

    @pytest.fixture(autouse=True)
    def setup_httpserver(self, httpserver: HTTPServer):
        self.httpserver = httpserver

    def setUp(self):
        self.client = self.client_class(
            42,
            "abcdef123456",
            host="{0}:{1}".format(self.httpserver.host, self.httpserver.port),
        )
        test_dir = os.path.join(os.path.dirname(__file__), "data")
        with open(os.path.join(test_dir, self.request_file), encoding="utf-8") as file:
            content = file.read()
        self.full_request = json.loads(content)

        with open(os.path.join(test_dir, self.response_file), encoding="utf-8") as file:
            self.response = file.read()

    def test_invalid_auth(self):
        for error in (
            "ACCOUNT_ID_REQUIRED",
            "AUTHORIZATION_INVALID",
            "LICENSE_KEY_REQUIRED",
            "USER_ID_REQUIRED",
        ):
            with self.assertRaisesRegex(AuthenticationError, "Invalid auth"):
                self.create_error(
                    text=f'{{"code":"{error}","error":"Invalid auth"}}',
                    status_code=401,
                )

    def test_invalid_request(self):
        with self.assertRaisesRegex(InvalidRequestError, "IP invalid"):
            self.create_error(text='{"code":"IP_ADDRESS_INVALID","error":"IP invalid"}')

    def test_300_error(self):
        with self.assertRaisesRegex(
            HTTPError, r"Received an unexpected HTTP status \(300\) for"
        ):
            self.create_error(status_code=300)

    def test_permission_required(self):
        with self.assertRaisesRegex(PermissionRequiredError, "permission"):
            self.create_error(
                text='{"code":"PERMISSION_REQUIRED","error":"permission required"}',
                status_code=403,
            )

    def test_400_with_invalid_json(self):
        with self.assertRaisesRegex(
            HTTPError,
            "Received a 400 error but it did not include the expected JSON"
            " body: b?'?{blah}'?",
        ):
            self.create_error(text="{blah}")

    def test_400_with_no_body(self):
        with self.assertRaisesRegex(HTTPError, "Received a 400 error with no body"):
            self.create_error()

    def test_400_with_unexpected_content_type(self):
        with self.assertRaisesRegex(
            HTTPError, "Received a 400 with the following body: b?'?plain'?"
        ):
            self.create_error(content_type="text/plain", text="plain")

    def test_400_without_json_body(self):
        with self.assertRaisesRegex(
            HTTPError,
            "Received a 400 error but it did not include the expected JSON"
            " body: b?'?plain'?",
        ):
            self.create_error(text="plain")

    def test_400_with_unexpected_json(self):
        with self.assertRaisesRegex(
            HTTPError,
            "Error response contains JSON but it does not specify code or"
            ' error keys: b?\'?{"not":"expected"}\'?',
        ):
            self.create_error(text='{"not":"expected"}')

    def test_500_error(self):
        with self.assertRaisesRegex(HTTPError, r"Received a server error \(500\) for"):
            self.create_error(status_code=500)

    def create_error(self, status_code=400, text="", content_type=None):
        uri = "/".join(
            ["/minfraud/v2.0", "transactions", "report"]
            if self.type == "report"
            else ["/minfraud/v2.0", self.type]
        )
        if content_type is None:
            content_type = (
                "application/json"
                if self.type == "report"
                else "application/vnd.maxmind.com-error+json; charset=UTF-8; version=2.0"
            )
        self.httpserver.expect_request(uri, method="POST").respond_with_data(
            text,
            content_type=content_type,
            status=status_code,
        )
        return self.run_client(getattr(self.client, self.type)(self.full_request))

    def create_success(self, text=None, client=None, request=None):
        uri = "/".join(
            ["/minfraud/v2.0", "transactions", "report"]
            if self.type == "report"
            else ["/minfraud/v2.0", self.type]
        )
        if request is None:
            request = self.full_request

        response = self.response if text is None else text
        status = 204 if self.type == "report" else 200
        self.httpserver.expect_request(uri, method="POST").respond_with_data(
            response,
            content_type=f"application/vnd.maxmind.com-minfraud-{self.type}+json; charset=UTF-8; version=2.0",
            status=status,
        )
        if client is None:
            client = self.client

        return self.run_client(getattr(client, self.type)(request))

    def run_client(self, v):
        return v

    def test_named_constructor_args(self):
        id = "47"
        key = "1234567890ab"
        for client in (
            self.client_class(account_id=id, license_key=key),
            self.client_class(account_id=id, license_key=key),
        ):
            self.assertEqual(client._account_id, id)
            self.assertEqual(client._license_key, key)

    def test_missing_constructor_args(self):
        with self.assertRaises(TypeError):
            self.client_class(license_key="1234567890ab")

        with self.assertRaises(TypeError):
            self.client_class("47")


class BaseTransactionTest(BaseTest):

    def has_ip_location(self):
        return self.type in ["factors", "insights"]

    def test_200(self):
        model = self.create_success()
        response = json.loads(self.response)
        if self.has_ip_location():
            response["ip_address"]["_locales"] = ("en",)
        self.assertEqual(self.cls(response), model)
        if self.has_ip_location():
            self.assertEqual("United Kingdom", model.ip_address.country.name)
            self.assertEqual(True, model.ip_address.traits.is_residential_proxy)
            self.assertEqual("310", model.ip_address.traits.mobile_country_code)
            self.assertEqual("004", model.ip_address.traits.mobile_network_code)
            self.assertEqual("ANONYMOUS_IP", model.ip_address.risk_reasons[0].code)

    def test_200_on_request_with_nones(self):
        model = self.create_success(
            request={
                "device": {"ip_address": "152.216.7.110", "accept_language": None},
                "event": {"shop_id": None},
                "shopping_cart": [
                    {
                        "category": None,
                        "quantity": 2,
                    },
                    None,
                ],
            }
        )
        response = self.response
        self.assertEqual(0.01, model.risk_score)

    def test_200_with_email_hashing(self):
        uri = "/".join(["/minfraud/v2.0", self.type])
        self.httpserver.expect_request(
            uri,
            method="POST",
            json={
                "email": {
                    "address": "977577b140bfb7c516e4746204fbdb01",
                    "domain": "maxmind.com",
                }
            },
        ).respond_with_data(
            self.response,
            content_type=f"application/vnd.maxmind.com-minfraud-{self.type}+json; charset=UTF-8; version=2.0",
            status=200,
        )

        request = {"email": {"address": "Test+ignore@maxmind.com"}}
        self.run_client(getattr(self.client, self.type)(request, hash_email=True))

    # This was fixed in https://github.com/maxmind/minfraud-api-python/pull/78

    def test_200_with_locales(self):
        locales = ("fr",)
        client = self.client_class(
            42,
            "abcdef123456",
            locales=locales,
            host="{0}:{1}".format(self.httpserver.host, self.httpserver.port),
        )
        model = self.create_success(client=client)
        response = json.loads(self.response)
        if self.has_ip_location():
            response["ip_address"]["_locales"] = locales
        self.assertEqual(self.cls(response), model)
        if self.has_ip_location():
            self.assertEqual("Royaume-Uni", model.ip_address.country.name)
            self.assertEqual("Londres", model.ip_address.city.name)

    def test_200_with_reserved_ip_warning(self):
        model = self.create_success(
            """
                {
                    "risk_score": 12,
                    "id": "0e52f5ac-7690-4780-a939-173cb13ecd75",
                    "warnings": [
                        {
                            "code": "IP_ADDRESS_RESERVED",
                            "warning":
                                "The IP address supplied is in a reserved network.",
                            "input_pointer": "/device/ip_address"
                        }
                    ]
                }
            """
        )

        self.assertEqual(12, model.risk_score)

    def test_200_with_no_risk_score_reasons(self):
        if "risk_score_reasons" not in self.response:
            return

        response = json.loads(self.response)
        del response["risk_score_reasons"]
        model = self.create_success(text=json.dumps(response))
        self.assertEqual(tuple(), model.risk_score_reasons)

    def test_200_with_no_body(self):
        with self.assertRaisesRegex(
            MinFraudError,
            "Received a 200 response but could not decode the response as"
            " JSON: b?'?'?",
        ):
            self.create_success(text="")

    def test_200_with_invalid_json(self):
        with self.assertRaisesRegex(
            MinFraudError,
            "Received a 200 response but could not decode the response as"
            " JSON: b?'?{'?",
        ):
            self.create_success(text="{")

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

    def test_204(self):
        self.create_success()

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
