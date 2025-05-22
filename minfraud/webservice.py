"""Client for minFraud Score, Insights, and Factors."""

from __future__ import annotations

import json
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, cast

import aiohttp
import aiohttp.http
import requests
import requests.utils

from .errors import (
    AuthenticationError,
    HTTPError,
    InsufficientFundsError,
    InvalidRequestError,
    MinFraudError,
    PermissionRequiredError,
)
from .models import Factors, Insights, Score
from .request import prepare_report, prepare_transaction
from .version import __version__

if TYPE_CHECKING:
    import sys
    import types
    from collections.abc import Sequence

    from requests.models import Response

    if sys.version_info >= (3, 11):
        from typing import Self
    else:
        from typing_extensions import Self

_AIOHTTP_UA = f"minFraud-API/{__version__} {aiohttp.http.SERVER_SOFTWARE}"

_REQUEST_UA = f"minFraud-API/{__version__} {requests.utils.default_user_agent()}"

_SCHEME = "https"


class BaseClient:
    """Base class for minFraud clients."""

    _account_id: str
    _license_key: str
    _locales: Sequence[str]
    _timeout: float

    _score_uri: str
    _insights_uri: str
    _factors_uri: str
    _report_uri: str

    def __init__(
        self,
        account_id: int,
        license_key: str,
        host: str = "minfraud.maxmind.com",
        locales: Sequence[str] = ("en",),
        timeout: float = 60,
    ) -> None:
        """Initialize the base client."""
        self._locales = locales
        self._account_id = str(account_id)
        self._license_key = license_key
        self._timeout = timeout
        base_uri = f"{_SCHEME}://{host}/minfraud/v2.0"
        self._score_uri = f"{base_uri}/score"
        self._insights_uri = f"{base_uri}/insights"
        self._factors_uri = f"{base_uri}/factors"
        self._report_uri = f"{base_uri}/transactions/report"

    def _handle_success(
        self,
        raw_body: str,
        uri: str,
        model_class: Callable,
    ) -> Score | Factors | Insights:
        """Handle successful response."""
        try:
            decoded_body = json.loads(raw_body)
        except ValueError as ex:
            msg = (
                "Received a 200 response but could not decode the "
                f"response as JSON: {raw_body}"
            )
            raise MinFraudError(
                msg,
                200,
                uri,
            ) from ex
        return model_class(**decoded_body)

    def _exception_for_error(
        self,
        status: int,
        content_type: str | None,
        raw_body: str,
        uri: str,
    ) -> (
        AuthenticationError
        | InsufficientFundsError
        | InvalidRequestError
        | HTTPError
        | PermissionRequiredError
    ):
        """Return the exception for the error responses."""
        if 400 <= status < 500:
            return self._exception_for_4xx_status(status, content_type, raw_body, uri)
        if 500 <= status < 600:
            return self._exception_for_5xx_status(status, raw_body, uri)
        return self._exception_for_unexpected_status(status, raw_body, uri)

    def _exception_for_4xx_status(
        self,
        status: int,
        content_type: str | None,
        raw_body: str,
        uri: str,
    ) -> (
        AuthenticationError
        | InsufficientFundsError
        | InvalidRequestError
        | HTTPError
        | PermissionRequiredError
    ):
        """Return exception for error responses with 4xx status codes."""
        if not raw_body:
            return HTTPError(
                f"Received a {status} error with no body",
                status,
                uri,
                raw_body,
            )
        if content_type is None or content_type.find("json") == -1:
            return HTTPError(
                f"Received a {status} with the following body: {raw_body}",
                status,
                uri,
                raw_body,
            )
        try:
            decoded_body = json.loads(raw_body)
        except ValueError:
            return HTTPError(
                f"Received a {status} error but it did not "
                f"include the expected JSON body: {raw_body}",
                status,
                uri,
                raw_body,
            )

        if "code" in decoded_body and "error" in decoded_body:
            return self._exception_for_web_service_error(
                decoded_body.get("error"),
                decoded_body.get("code"),
                status,
                uri,
            )
        return HTTPError(
            "Error response contains JSON but it does not "
            f"specify code or error keys: {raw_body}",
            status,
            uri,
            raw_body,
        )

    @staticmethod
    def _exception_for_web_service_error(
        message: str,
        code: str,
        status: int,
        uri: str,
    ) -> (
        InvalidRequestError
        | AuthenticationError
        | PermissionRequiredError
        | InsufficientFundsError
    ):
        """Return exception for error responses with the JSON body."""
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
    def _exception_for_5xx_status(
        status: int,
        raw_body: str | None,
        uri: str,
    ) -> HTTPError:
        """Return exception for error response with 5xx status codes."""
        return HTTPError(
            f"Received a server error ({status}) for {uri}",
            status,
            uri,
            raw_body,
        )

    @staticmethod
    def _exception_for_unexpected_status(
        status: int,
        raw_body: str | None,
        uri: str,
    ) -> HTTPError:
        """Return exception for responses with unexpected status codes."""
        return HTTPError(
            f"Received an unexpected HTTP status ({status}) for {uri}",
            status,
            uri,
            raw_body,
        )


class AsyncClient(BaseClient):
    """Async client for accessing the minFraud web services."""

    _existing_session: aiohttp.ClientSession
    _proxy: str | None

    def __init__(  # noqa: PLR0913
        self,
        account_id: int,
        license_key: str,
        host: str = "minfraud.maxmind.com",
        locales: Sequence[str] = ("en",),
        timeout: float = 60,
        proxy: str | None = None,
    ) -> None:
        """Construct AsyncClient.

        :param account_id: Your MaxMind account ID
        :type account_id: int
        :param license_key: Your MaxMind license key
        :type license_key: str
        :param host: The host to use when connecting to the web service.
        :type host: str
        :param locales: A tuple of locale codes to use in name property
        :type locales: tuple[str]
        :param timeout: The timeout in seconds to use when waiting on the request.
          This sets both the connect timeout and the read timeout. The default is
          60.
        :type timeout: float
        :param proxy: The URL of an HTTP proxy to use. It may optionally include
          a basic auth username and password, e.g.,
          ``http://username:password@host:port``.
        :return: Client object
        :rtype: Client
        """
        super().__init__(account_id, license_key, host, locales, timeout)
        self._proxy = proxy

    async def factors(
        self,
        transaction: dict[str, Any],
        validate: bool = True,  # noqa: FBT001, FBT002
        hash_email: bool = False,  # noqa: FBT001, FBT002
    ) -> Factors:
        """Query Factors endpoint with transaction data.

        :param transaction: A dictionary containing the transaction to be
          sent to the minFraud Factors web service as specified in the `REST
          API documentation
          <https://dev.maxmind.com/minfraud/api-documentation/requests?lang=en>`_.
        :type transaction: dict
        :param validate: If set to false, validation of the transaction
          dictionary will be disabled. This validation helps ensure that your
          request is correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :param hash_email: By default, the email address is sent in plain text.
          If this is set to ``True``, the email address will be normalized and
          converted to an MD5 hash before the request is sent. The email domain
          will continue to be sent in plain text.
        :type hash_email: bool
        :return: A Factors model object
        :rtype: Factors
        :raises: AuthenticationError, InsufficientFundsError,
          InvalidRequestError, HTTPError, MinFraudError,
        """
        return cast(
            "Factors",
            await self._response_for(
                self._factors_uri,
                partial(Factors, self._locales),
                transaction,
                validate,
                hash_email,
            ),
        )

    async def insights(
        self,
        transaction: dict[str, Any],
        validate: bool = True,  # noqa: FBT001, FBT002
        hash_email: bool = False,  # noqa: FBT001, FBT002
    ) -> Insights:
        """Query Insights endpoint with transaction data.

        :param transaction: A dictionary containing the transaction to be
          sent to the minFraud Insights web service as specified in the `REST
          API documentation
          <https://dev.maxmind.com/minfraud/api-documentation/requests?lang=en>`_.
        :type transaction: dict
        :param validate: If set to false, validation of the transaction
          dictionary will be disabled. This validation helps ensure that your
          request is correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :param hash_email: By default, the email address is sent in plain text.
          If this is set to ``True``, the email address will be normalized and
          converted to an MD5 hash before the request is sent. The email domain
          will continue to be sent in plain text.
        :type hash_email: bool
        :return: An Insights model object
        :rtype: Insights
        :raises: AuthenticationError, InsufficientFundsError,
          InvalidRequestError, HTTPError, MinFraudError,
        """
        return cast(
            "Insights",
            await self._response_for(
                self._insights_uri,
                partial(Insights, self._locales),
                transaction,
                validate,
                hash_email,
            ),
        )

    async def score(
        self,
        transaction: dict[str, Any],
        validate: bool = True,  # noqa: FBT001, FBT002
        hash_email: bool = False,  # noqa: FBT001, FBT002
    ) -> Score:
        """Query Score endpoint with transaction data.

        :param transaction: A dictionary containing the transaction to be
          sent to the minFraud Score web service as specified in the `REST API
          documentation
          <https://dev.maxmind.com/minfraud/api-documentation/requests?lang=en>`_.
        :type transaction: dict
        :param validate: If set to false, validation of the transaction
          dictionary will be disabled. This validation helps ensure that your
          request is correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :param hash_email: By default, the email address is sent in plain text.
          If this is set to ``True``, the email address will be normalized and
          converted to an MD5 hash before the request is sent. The email domain
          will continue to be sent in plain text.
        :type hash_email: bool
        :return: A Score model object
        :rtype: Score
        :raises: AuthenticationError, InsufficientFundsError,
          InvalidRequestError, HTTPError, MinFraudError,
        """
        return cast(
            "Score",
            await self._response_for(
                self._score_uri,
                Score,
                transaction,
                validate,
                hash_email,
            ),
        )

    async def report(
        self,
        report: dict[str, str | None],
        validate: bool = True,  # noqa: FBT001, FBT002
    ) -> None:
        """Send a transaction report to the Report Transaction endpoint.

        :param report: A dictionary containing the transaction report to be sent
          to the Report Transations web service as specified in the `REST API`
          documentation
          <https://dev.maxmind.com/minfraud/report-a-transaction?lang=en>_.
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
        prepared_request = prepare_report(report, validate)
        uri = self._report_uri
        async with await self._do_request(uri, prepared_request) as response:
            status = response.status
            content_type = response.content_type
            raw_body = await response.text()

            if status != 204:
                raise self._exception_for_error(status, content_type, raw_body, uri)

    async def _response_for(
        self,
        uri: str,
        model_class: Callable,
        request: dict[str, Any],
        validate: bool,  # noqa: FBT001
        hash_email: bool,  # noqa: FBT001
    ) -> Score | Factors | Insights:
        """Send request and create response object."""
        prepared_request = prepare_transaction(request, validate, hash_email)
        async with await self._do_request(uri, prepared_request) as response:
            status = response.status
            content_type = response.content_type
            raw_body = await response.text()

            if status != 200:
                raise self._exception_for_error(status, content_type, raw_body, uri)
            return self._handle_success(raw_body, uri, model_class)

    async def _do_request(
        self,
        uri: str,
        data: dict[str, Any],
    ) -> aiohttp.ClientResponse:
        session = await self._session()
        return await session.post(uri, json=data, proxy=self._proxy)

    async def _session(self) -> aiohttp.ClientSession:
        if not hasattr(self, "_existing_session"):
            self._existing_session = aiohttp.ClientSession(
                auth=aiohttp.BasicAuth(self._account_id, self._license_key),
                headers={"Accept": "application/json", "User-Agent": _AIOHTTP_UA},
                timeout=aiohttp.ClientTimeout(total=self._timeout),
            )

        return self._existing_session

    async def close(self) -> None:
        """Close underlying session.

        This will close the session and any associated connections.
        """
        if hasattr(self, "_existing_session"):
            await self._existing_session.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        await self.close()


class Client(BaseClient):
    """Synchronous client for accessing the minFraud web services."""

    _proxies: dict[str, str] | None
    _session: requests.Session

    def __init__(  # noqa: PLR0913
        self,
        account_id: int,
        license_key: str,
        host: str = "minfraud.maxmind.com",
        locales: Sequence[str] = ("en",),
        timeout: float = 60,
        proxy: str | None = None,
    ) -> None:
        """Construct Client.

        :param account_id: Your MaxMind account ID
        :type account_id: int
        :param license_key: Your MaxMind license key
        :type license_key: str
        :param host: The host to use when connecting to the web service.
          By default, the client connects to the production host. However,
          during testing and development, you can set this option to
          'sandbox.maxmind.com' to use the Sandbox environment's host. The
          sandbox allows you to experiment with the API without affecting your
          production data.
        :type host: str
        :param locales: A tuple of locale codes to use in name property
        :type locales: tuple[str]
        :param timeout: The timeout in seconds to use when waiting on the request.
          This sets both the connect timeout and the read timeout. The default is
          60.
        :param proxy: The URL of an HTTP proxy to use. It may optionally include
          a basic auth username and password, e.g.,
          ``http://username:password@host:port``.
        :type timeout: float
        :return: Client object
        :rtype: Client
        """
        super().__init__(account_id, license_key, host, locales, timeout)

        self._session = requests.Session()
        self._session.auth = (self._account_id, self._license_key)
        self._session.headers["Accept"] = "application/json"
        self._session.headers["User-Agent"] = _REQUEST_UA

        if proxy is None:
            self._proxies = None
        else:
            self._proxies = {"https": proxy}

    def factors(
        self,
        transaction: dict[str, Any],
        validate: bool = True,  # noqa: FBT001, FBT002
        hash_email: bool = False,  # noqa: FBT001, FBT002
    ) -> Factors:
        """Query Factors endpoint with transaction data.

        :param transaction: A dictionary containing the transaction to be
          sent to the minFraud Factors web service as specified in the `REST
          API documentation
          <https://dev.maxmind.com/minfraud/api-documentation/requests?lang=en>`_.
        :type transaction: dict
        :param validate: If set to false, validation of the transaction
          dictionary will be disabled. This validation helps ensure that your
          request is correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :param hash_email: By default, the email address is sent in plain text.
          If this is set to ``True``, the email address will be normalized and
          converted to an MD5 hash before the request is sent. The email domain
          will continue to be sent in plain text.
        :type hash_email: bool
        :return: A Factors model object
        :rtype: Factors
        :raises: AuthenticationError, InsufficientFundsError,
          InvalidRequestError, HTTPError, MinFraudError,
        """
        return cast(
            "Factors",
            self._response_for(
                self._factors_uri,
                partial(Factors, self._locales),
                transaction,
                validate,
                hash_email,
            ),
        )

    def insights(
        self,
        transaction: dict[str, Any],
        validate: bool = True,  # noqa: FBT001, FBT002
        hash_email: bool = False,  # noqa: FBT001, FBT002
    ) -> Insights:
        """Query Insights endpoint with transaction data.

        :param transaction: A dictionary containing the transaction to be
          sent to the minFraud Insights web service as specified in the `REST
          API documentation
          <https://dev.maxmind.com/minfraud/api-documentation/requests?lang=en>`_.
        :type transaction: dict
        :param validate: If set to false, validation of the transaction
          dictionary will be disabled. This validation helps ensure that your
          request is correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :param hash_email: By default, the email address is sent in plain text.
          If this is set to ``True``, the email address will be normalized and
          converted to an MD5 hash before the request is sent. The email domain
          will continue to be sent in plain text.
        :type hash_email: bool
        :return: An Insights model object
        :rtype: Insights
        :raises: AuthenticationError, InsufficientFundsError,
          InvalidRequestError, HTTPError, MinFraudError,
        """
        return cast(
            "Insights",
            self._response_for(
                self._insights_uri,
                partial(Insights, self._locales),
                transaction,
                validate,
                hash_email,
            ),
        )

    def score(
        self,
        transaction: dict[str, Any],
        validate: bool = True,  # noqa: FBT001, FBT002
        hash_email: bool = False,  # noqa: FBT001, FBT002
    ) -> Score:
        """Query Score endpoint with transaction data.

        :param transaction: A dictionary containing the transaction to be
          sent to the minFraud Score web service as specified in the `REST API
          documentation
          <https://dev.maxmind.com/minfraud/api-documentation/requests?lang=en>`_.
        :type transaction: dict
        :param validate: If set to false, validation of the transaction
          dictionary will be disabled. This validation helps ensure that your
          request is correct before sending it to MaxMind. Validation raises an
          InvalidRequestError.
        :type validate: bool
        :param hash_email: By default, the email address is sent in plain text.
          If this is set to ``True``, the email address will be normalized and
          converted to an MD5 hash before the request is sent. The email domain
          will continue to be sent in plain text.
        :type hash_email: bool
        :return: A Score model object
        :rtype: Score
        :raises: AuthenticationError, InsufficientFundsError,
          InvalidRequestError, HTTPError, MinFraudError,
        """
        return cast(
            "Score",
            self._response_for(
                self._score_uri,
                Score,
                transaction,
                validate,
                hash_email,
            ),
        )

    def report(
        self,
        report: dict[str, str | None],
        validate: bool = True,  # noqa: FBT001, FBT002
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
        prepared_request = prepare_report(report, validate)
        uri = self._report_uri

        response = self._do_request(uri, prepared_request)
        status = response.status_code
        content_type = response.headers.get("Content-Type")
        raw_body = response.text
        if status != 204:
            raise self._exception_for_error(status, content_type, raw_body, uri)

    def _response_for(
        self,
        uri: str,
        model_class: Callable,
        request: dict[str, Any],
        validate: bool,  # noqa: FBT001
        hash_email: bool,  # noqa: FBT001
    ) -> Score | Factors | Insights:
        """Send request and create response object."""
        prepared_request = prepare_transaction(request, validate, hash_email)

        response = self._do_request(uri, prepared_request)
        status = response.status_code
        content_type = response.headers.get("Content-Type")
        raw_body = response.text
        if status != 200:
            raise self._exception_for_error(status, content_type, raw_body, uri)
        return self._handle_success(raw_body, uri, model_class)

    def _do_request(self, uri: str, data: dict[str, Any]) -> Response:
        return self._session.post(
            uri,
            json=data,
            timeout=self._timeout,
            proxies=self._proxies,
        )

    def close(self) -> None:
        """Close underlying session.

        This will close the session and any associated connections.
        """
        self._session.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None:
        self.close()
