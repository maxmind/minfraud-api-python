"""
minfraud.webservice
~~~~~~~~~~~~~~~~~~~

This module contains the webservice client class.

"""

import json
from typing import Any, cast, Dict, Optional, Tuple, Type, Union

import aiohttp
import aiohttp.http
import requests
import requests.utils
from requests.models import Response
from voluptuous import MultipleInvalid

from .version import __version__
from .errors import (
    MinFraudError,
    HTTPError,
    AuthenticationError,
    InsufficientFundsError,
    InvalidRequestError,
    PermissionRequiredError,
)
from .models import Factors, Insights, Score
from .validation import validate_report, validate_transaction


_AIOHTTP_UA = "minFraud-API/%s %s" % (__version__, aiohttp.http.SERVER_SOFTWARE,)

_REQUEST_UA = "minFraud-API/%s %s" % (__version__, requests.utils.default_user_agent(),)


# pylint: disable=too-many-instance-attributes, missing-class-docstring
class BaseClient:
    _account_id: str
    _license_key: str
    _locales: Tuple[str]
    _timeout: float

    _score_uri: str
    _insights_uri: str
    _factors_uri: str
    _report_uri: str

    def __init__(  # pylint: disable=too-many-arguments
        self,
        account_id: int,
        license_key: str,
        host: str = "minfraud.maxmind.com",
        locales: Tuple[str] = ("en",),
        timeout: float = 60,
    ) -> None:
        self._locales = locales
        self._account_id = str(account_id)
        self._license_key = license_key
        self._timeout = timeout

        base_uri = u"https://{0:s}/minfraud/v2.0".format(host)
        self._score_uri = "/".join([base_uri, "score"])
        self._insights_uri = "/".join([base_uri, "insights"])
        self._factors_uri = "/".join([base_uri, "factors"])
        self._report_uri = "/".join([base_uri, "transactions", "report"])

    def _prepare_report(self, request: Dict[str, Any], validate: bool):
        cleaned_request = self._copy_and_clean(request)
        if validate:
            try:
                validate_report(cleaned_request)
            except MultipleInvalid as ex:
                raise InvalidRequestError("Invalid report data: {0}".format(ex))
        return cleaned_request

    def _prepare_transaction(self, request: Dict[str, Any], validate: bool):
        cleaned_request = self._copy_and_clean(request)
        if validate:
            try:
                validate_transaction(cleaned_request)
            except MultipleInvalid as ex:
                raise InvalidRequestError("Invalid transaction data: {0}".format(ex))
        return cleaned_request

    def _copy_and_clean(self, data: Any) -> Any:
        """Create a copy of the data structure with Nones removed."""
        if isinstance(data, dict):
            return dict(
                (k, self._copy_and_clean(v)) for (k, v) in data.items() if v is not None
            )
        if isinstance(data, (list, set, tuple)):
            return [self._copy_and_clean(x) for x in data if x is not None]
        return data

    def _handle_success(
        self,
        body: str,
        uri: str,
        model_class: Union[Type[Factors], Type[Score], Type[Insights]],
    ) -> Union[Score, Factors, Insights]:
        """Handle successful response."""
        try:
            decoded_body = json.loads(body)
        except ValueError:
            raise MinFraudError(
                "Received a 200 response"
                " but could not decode the response as "
                "JSON: {0}".format(body),
                200,
                uri,
            )
        if "ip_address" in body:
            decoded_body["ip_address"]["_locales"] = self._locales
        return model_class(decoded_body)  # type: ignore

    def _exception_for_error(
        self, status: int, content_type: str, body: str, uri: str
    ) -> Union[
        AuthenticationError,
        InsufficientFundsError,
        InvalidRequestError,
        HTTPError,
        PermissionRequiredError,
    ]:
        """Returns the exception for the error responses."""

        if 400 <= status < 500:
            return self._exception_for_4xx_status(status, content_type, body, uri)
        if 500 <= status < 600:
            return self._exception_for_5xx_status(status, uri)
        return self._exception_for_unexpected_status(status, uri)

    def _exception_for_4xx_status(
        self, status: int, content_type: str, body: str, uri: str
    ) -> Union[
        AuthenticationError,
        InsufficientFundsError,
        InvalidRequestError,
        HTTPError,
        PermissionRequiredError,
    ]:
        """Returns exception for error responses with 4xx status codes."""
        if not body:
            return HTTPError(
                "Received a {0} error with no body".format(status), status, uri
            )
        if content_type.find("json") == -1:
            return HTTPError(
                "Received a {0} with the following " "body: {1}".format(status, body),
                status,
                uri,
            )
        try:
            decoded_body = json.loads(body)
        except ValueError:
            return HTTPError(
                "Received a {status:d} error but it did not include"
                " the expected JSON body: {content}".format(
                    status=status, content=body
                ),
                status,
                uri,
            )
        else:
            if "code" in decoded_body and "error" in decoded_body:
                return self._exception_for_web_service_error(
                    decoded_body.get("error"), decoded_body.get("code"), status, uri
                )
            return HTTPError(
                "Error response contains JSON but it does not specify code"
                " or error keys: {0}".format(body),
                status,
                uri,
            )

    @staticmethod
    def _exception_for_web_service_error(
        message: str, code: str, status: int, uri: str
    ) -> Union[
        InvalidRequestError,
        AuthenticationError,
        PermissionRequiredError,
        InsufficientFundsError,
    ]:
        """Returns exception for error responses with the JSON body."""
        if code in (
            "ACCOUNT_ID_REQUIRED",
            "AUTHORIZATION_INVALID",
            "LICENSE_KEY_REQUIRED",
            "USER_ID_REQUIRED",
        ):
            return AuthenticationError(message)
        if code == "INSUFFICIENT_FUNDS":
            return InsufficientFundsError(message)
        if code == "PERMISSION_REQUIRED":
            return PermissionRequiredError(message)

        return InvalidRequestError(message, code, status, uri)

    @staticmethod
    def _exception_for_5xx_status(status: int, uri: str) -> HTTPError:
        """Returns exception for error response with 5xx status codes."""
        return HTTPError(
            u"Received a server error ({0}) for " u"{1}".format(status, uri),
            status,
            uri,
        )

    @staticmethod
    def _exception_for_unexpected_status(status: int, uri: str) -> HTTPError:
        """Returns exception for responses with unexpected status codes."""
        return HTTPError(
            u"Received an unexpected HTTP status " u"({0}) for {1}".format(status, uri),
            status,
            uri,
        )


class AsyncClient(BaseClient):
    """Async client for accessing the minFraud web services."""

    _existing_session: aiohttp.ClientSession

    def __init__(  # pylint: disable=too-many-arguments
        self,
        account_id: int,
        license_key: str,
        host: str = "minfraud.maxmind.com",
        locales: Tuple[str] = ("en",),
        timeout: float = 60,
    ) -> None:
        """Constructor for AsyncClient.

        :param account_id: Your MaxMind account ID
        :type account_id: int
        :param license_key: Your MaxMind license key
        :type license_key: str
        :param host: The host to use when connecting to the web service.
        :type host: str
        :param locales: A tuple of locale codes to use in name property
        :type locales: tuple[str]
        :param timeout: The timeout in seconts to use when waiting on the request.
          This sets both the connect timeout and the read timeout. The default is
          60.
        :type timeout: float
        :return: Client object
        :rtype: Client
        """
        super().__init__(account_id, license_key, host, locales, timeout)

    async def factors(
        self, transaction: Dict[str, Any], validate: bool = True
    ) -> Factors:
        """Query Factors endpoint with transaction data.

        :param transaction: A dictionary containing the transaction to be
          sent to the minFraud Insights web service as specified in the `REST
          API documentation
          <https://dev.maxmind.com/minfraud/#Request_Body>`_.
        :type transaction: dict
        :param validate: If set to false, validation of the transaction
          dictionary will be disabled. This validation helps ensure that your
          request is correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :return: A Factors model object
        :rtype: Factors
        :raises: AuthenticationError, InsufficientFundsError,
          InvalidRequestError, HTTPError, MinFraudError,
        """
        return cast(
            Factors,
            await self._response_for(self._factors_uri, Factors, transaction, validate),
        )

    async def insights(
        self, transaction: Dict[str, Any], validate: bool = True
    ) -> Insights:
        """Query Insights endpoint with transaction data.

        :param transaction: A dictionary containing the transaction to be
          sent to the minFraud Insights web service as specified in the `REST
          API documentation
          <https://dev.maxmind.com/minfraud/#Request_Body>`_.
        :type transaction: dict
        :param validate: If set to false, validation of the transaction
          dictionary will be disabled. This validation helps ensure that your
          request is correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :return: An Insights model object
        :rtype: Insights
        :raises: AuthenticationError, InsufficientFundsError,
          InvalidRequestError, HTTPError, MinFraudError,
        """
        return cast(
            Insights,
            await self._response_for(
                self._insights_uri, Insights, transaction, validate
            ),
        )

    async def score(self, transaction: Dict[str, Any], validate: bool = True) -> Score:
        """Query Score endpoint with transaction data.

        :param transaction: A dictionary containing the transaction to be
          sent to the minFraud Score web service as specified in the `REST API
          documentation
          <https://dev.maxmind.com/minfraud/#Request_Body>`_.
        :type transaction: dict
        :param validate: If set to false, validation of the transaction
          dictionary will be disabled. This validation helps ensure that your
          request is correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :return: A Score model object
        :rtype: Score
        :raises: AuthenticationError, InsufficientFundsError,
          InvalidRequestError, HTTPError, MinFraudError,
        """
        return cast(
            Score,
            await self._response_for(self._score_uri, Score, transaction, validate),
        )

    async def report(
        self, report: Dict[str, Optional[str]], validate: bool = True
    ) -> None:
        """Send a transaction report to the Report Transaction endpoint.

        :param report: A dictionary containing the transaction report to be sent
          to the Report Transations web service as specified in the `REST API`
          documentation
          <https://dev.maxmind.com/minfraud/report-transaction/#Request_Body>_.
        :type report: dict
        :param validate: If set to false, validation of the report dictionary
          will be disabled. This validation helps ensure that your request is
          correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :return: Nothing
        :rtype: None
        :raises: AuthenticationError, InvalidRequestError, HTTPError,
          MinFraudError,
        """
        prepared_request = self._prepare_report(report, validate)
        uri = self._report_uri
        async with await self._do_request(uri, prepared_request) as response:
            status = response.status
            content_type = response.content_type
            body = await response.text()

            if status != 204:
                raise self._exception_for_error(status, content_type, body, uri)

    async def _response_for(
        self,
        uri: str,
        model_class: Union[Type[Factors], Type[Score], Type[Insights]],
        request: Dict[str, Any],
        validate: bool,
    ) -> Union[Score, Factors, Insights]:
        """Send request and create response object."""
        prepared_request = self._prepare_transaction(request, validate)
        async with await self._do_request(uri, prepared_request) as response:
            status = response.status
            content_type = response.content_type
            body = await response.text()

            if status != 200:
                raise self._exception_for_error(status, content_type, body, uri)
            return self._handle_success(body, uri, model_class)

    async def _do_request(
        self, uri: str, data: Dict[str, Any]
    ) -> aiohttp.ClientResponse:
        session = await self._session()
        return await session.post(uri, json=data)

    async def _session(self) -> aiohttp.ClientSession:
        if not hasattr(self, "_existing_session"):
            self._existing_session = aiohttp.ClientSession(
                auth=aiohttp.BasicAuth(self._account_id, self._license_key),
                headers={"Accept": "application/json", "User-Agent": _AIOHTTP_UA},
                timeout=aiohttp.ClientTimeout(total=self._timeout),
            )

        return self._existing_session

    async def close(self):
        """Close underlying session

        This will close the session and any associated connections.
        """
        if hasattr(self, "_existing_session"):
            await self._existing_session.close()

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, exc_type: None, exc_value: None, traceback: None) -> None:
        await self.close()


class Client(BaseClient):
    """Synchronous client for accessing the minFraud web services."""

    _session: requests.Session

    def __init__(  # pylint: disable=too-many-arguments
        self,
        account_id: int,
        license_key: str,
        host: str = "minfraud.maxmind.com",
        locales: Tuple[str] = ("en",),
        timeout: float = 60,
    ) -> None:
        """Constructor for Client.

        :param account_id: Your MaxMind account ID
        :type account_id: int
        :param license_key: Your MaxMind license key
        :type license_key: str
        :param host: The host to use when connecting to the web service.
        :type host: str
        :param locales: A tuple of locale codes to use in name property
        :type locales: tuple[str]
        :param timeout: The timeout in seconts to use when waiting on the request.
          This sets both the connect timeout and the read timeout. The default is
          60.
        :type timeout: float
        :return: Client object
        :rtype: Client
        """
        super().__init__(account_id, license_key, host, locales, timeout)

        self._session = requests.Session()
        self._session.auth = (self._account_id, self._license_key)
        self._session.headers["Accept"] = "application/json"
        self._session.headers["User-Agent"] = _REQUEST_UA

    def factors(self, transaction: Dict[str, Any], validate: bool = True) -> Factors:
        """Query Factors endpoint with transaction data.

        :param transaction: A dictionary containing the transaction to be
          sent to the minFraud Insights web service as specified in the `REST
          API documentation
          <https://dev.maxmind.com/minfraud/#Request_Body>`_.
        :type transaction: dict
        :param validate: If set to false, validation of the transaction
          dictionary will be disabled. This validation helps ensure that your
          request is correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :return: A Factors model object
        :rtype: Factors
        :raises: AuthenticationError, InsufficientFundsError,
          InvalidRequestError, HTTPError, MinFraudError,
        """
        return cast(
            Factors,
            self._response_for(self._factors_uri, Factors, transaction, validate),
        )

    def insights(self, transaction: Dict[str, Any], validate: bool = True) -> Insights:
        """Query Insights endpoint with transaction data.

        :param transaction: A dictionary containing the transaction to be
          sent to the minFraud Insights web service as specified in the `REST
          API documentation
          <https://dev.maxmind.com/minfraud/#Request_Body>`_.
        :type transaction: dict
        :param validate: If set to false, validation of the transaction
          dictionary will be disabled. This validation helps ensure that your
          request is correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :return: An Insights model object
        :rtype: Insights
        :raises: AuthenticationError, InsufficientFundsError,
          InvalidRequestError, HTTPError, MinFraudError,
        """
        return cast(
            Insights,
            self._response_for(self._insights_uri, Insights, transaction, validate),
        )

    def score(self, transaction: Dict[str, Any], validate: bool = True) -> Score:
        """Query Score endpoint with transaction data.

        :param transaction: A dictionary containing the transaction to be
          sent to the minFraud Score web service as specified in the `REST API
          documentation
          <https://dev.maxmind.com/minfraud/#Request_Body>`_.
        :type transaction: dict
        :param validate: If set to false, validation of the transaction
          dictionary will be disabled. This validation helps ensure that your
          request is correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :return: A Score model object
        :rtype: Score
        :raises: AuthenticationError, InsufficientFundsError,
          InvalidRequestError, HTTPError, MinFraudError,
        """
        return cast(
            Score, self._response_for(self._score_uri, Score, transaction, validate)
        )

    def report(self, report: Dict[str, Optional[str]], validate: bool = True) -> None:
        """Send a transaction report to the Report Transaction endpoint.

        :param report: A dictionary containing the transaction report to be sent
          to the Report Transations web service as specified in the `REST API`
          documentation
          <https://dev.maxmind.com/minfraud/report-transaction/#Request_Body>_.
        :type report: dict
        :param validate: If set to false, validation of the report dictionary
          will be disabled. This validation helps ensure that your request is
          correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :return: Nothing
        :rtype: None
        :raises: AuthenticationError, InvalidRequestError, HTTPError,
          MinFraudError,
        """
        prepared_request = self._prepare_report(report, validate)
        uri = self._report_uri

        response = self._do_request(uri, prepared_request)
        status = response.status_code
        content_type = response.headers["Content-Type"]
        body = response.text
        if status != 204:
            raise self._exception_for_error(status, content_type, body, uri)

    def _response_for(
        self,
        uri: str,
        model_class: Union[Type[Factors], Type[Score], Type[Insights]],
        request: Dict[str, Any],
        validate: bool,
    ) -> Union[Score, Factors, Insights]:
        """Send request and create response object."""
        prepared_request = self._prepare_transaction(request, validate)

        response = self._do_request(uri, prepared_request)
        status = response.status_code
        content_type = response.headers["Content-Type"]
        body = response.text
        if status != 200:
            raise self._exception_for_error(status, content_type, body, uri)
        return self._handle_success(body, uri, model_class)

    def _do_request(self, uri: str, data: Dict[str, Any]) -> Response:
        return self._session.post(uri, json=data, timeout=self._timeout)

    def close(self):
        """Close underlying session

        This will close the session and any associated connections.
        """
        self._session.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, exc_type: None, exc_value: None, traceback: None) -> None:
        self.close()
