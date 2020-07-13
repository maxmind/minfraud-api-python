"""
minfraud.webservice
~~~~~~~~~~~~~~~~~~~

This module contains the webservice client class.

"""

from typing import Any, cast, Dict, Optional, Tuple, Type, Union

import requests
from requests.models import Response
from requests.utils import default_user_agent
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


class Client:
    """Client for accessing the minFraud Score and Insights web services."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        account_id: int,
        license_key: str,
        host: str = "minfraud.maxmind.com",
        locales: Tuple[str] = ("en",),
        timeout: Optional[float] = None,
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
        :param timeout: The timeout to use for the request.
        :type timeout: float
        :return: Client object
        :rtype: Client
        """

        self._locales = locales
        # requests 2.12.2 requires that the username passed to auth be a
        # string
        self._account_id = str(account_id)
        self._license_key = license_key
        self._base_uri = u"https://{0:s}/minfraud/v2.0".format(host)
        self._timeout = timeout

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
            Factors, self._response_for("factors", Factors, transaction, validate)
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
            Insights, self._response_for("insights", Insights, transaction, validate)
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
        return cast(Score, self._response_for("score", Score, transaction, validate))

    def _response_for(
        self,
        path: str,
        model_class: Union[Type[Factors], Type[Score], Type[Insights]],
        request: Dict[str, Any],
        validate: bool,
    ) -> Union[Score, Factors, Insights]:
        """Send request and create response object."""
        cleaned_request = self._copy_and_clean(request)
        if validate:
            try:
                validate_transaction(cleaned_request)
            except MultipleInvalid as ex:
                raise InvalidRequestError("Invalid transaction data: {0}".format(ex))
        uri = "/".join([self._base_uri, path])
        response = self._do_request(uri, cleaned_request)
        if response.status_code != 200:
            raise self._exception_for_error(response, uri)
        return self._handle_success(response, uri, model_class)

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

        cleaned_request = self._copy_and_clean(report)
        if validate:
            try:
                validate_report(cleaned_request)
            except MultipleInvalid as ex:
                raise InvalidRequestError("Invalid report data: {0}".format(ex))
        uri = "/".join([self._base_uri, "transactions", "report"])
        response = self._do_request(uri, cleaned_request)
        if response.status_code != 204:
            raise self._exception_for_error(response, uri)

    def _do_request(self, uri: str, data: Dict[str, Any]) -> Response:
        return requests.post(
            uri,
            json=data,
            auth=(self._account_id, self._license_key),
            headers={"Accept": "application/json", "User-Agent": self._user_agent()},
            timeout=self._timeout,
        )

    def _copy_and_clean(self, data: Any) -> Any:
        """Create a copy of the data structure with Nones removed."""
        if isinstance(data, dict):
            return dict(
                (k, self._copy_and_clean(v)) for (k, v) in data.items() if v is not None
            )
        if isinstance(data, (list, set, tuple)):
            return [self._copy_and_clean(x) for x in data if x is not None]
        return data

    @staticmethod
    def _user_agent() -> str:
        """Create User-Agent header."""
        return "minFraud-API/%s %s" % (__version__, default_user_agent())

    def _handle_success(
        self,
        response: Response,
        uri: str,
        model_class: Union[Type[Factors], Type[Score], Type[Insights]],
    ) -> Union[Score, Factors, Insights]:
        """Handle successful response."""
        try:
            body = response.json()
        except ValueError:
            raise MinFraudError(
                "Received a 200 response"
                " but could not decode the response as "
                "JSON: {0}".format(str(response.content)),
                200,
                uri,
            )
        if "ip_address" in body:
            body["ip_address"]["_locales"] = self._locales
        return model_class(body)

    def _exception_for_error(
        self, response: Response, uri: str
    ) -> Union[
        AuthenticationError,
        InsufficientFundsError,
        InvalidRequestError,
        HTTPError,
        PermissionRequiredError,
    ]:
        """Returns the exception for the error responses."""
        status = response.status_code

        if 400 <= status < 500:
            return self._exception_for_4xx_status(response, status, uri)
        if 500 <= status < 600:
            return self._exception_for_5xx_status(status, uri)
        return self._exception_for_unexpected_status(status, uri)

    def _exception_for_4xx_status(
        self, response: Response, status: int, uri: str
    ) -> Union[
        AuthenticationError,
        InsufficientFundsError,
        InvalidRequestError,
        HTTPError,
        PermissionRequiredError,
    ]:
        """Returns exception for error responses with 4xx status codes."""
        if not response.content:
            return HTTPError(
                "Received a {0} error with no body".format(status), status, uri
            )
        if response.headers.get("Content-Type", "").find("json") == -1:
            return HTTPError(
                "Received a {0} with the following "
                "body: {1}".format(status, str(response.content)),
                status,
                uri,
            )
        try:
            body = response.json()
        except ValueError:
            return HTTPError(
                "Received a {status:d} error but it did not include"
                " the expected JSON body: {content}".format(
                    status=status, content=str(response.content)
                ),
                status,
                uri,
            )
        else:
            if "code" in body and "error" in body:
                return self._exception_for_web_service_error(
                    body.get("error"), body.get("code"), status, uri
                )
            return HTTPError(
                "Error response contains JSON but it does not specify code"
                " or error keys: {0}".format(str(response.content)),
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
