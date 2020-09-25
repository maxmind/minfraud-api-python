"""
minfraud.errors
~~~~~~~~~~~~~~~

This module contains errors that are raised by this package.

"""

from typing import Optional


class MinFraudError(RuntimeError):
    """There was a non-specific error in minFraud.

    This class represents a generic error. It extends :py:exc:`RuntimeError`
    and does not add any additional attributes.
    """


class AuthenticationError(MinFraudError):
    """There was a problem authenticating the request."""


class HTTPError(MinFraudError):
    """There was an error when making your HTTP request.

    This class represents an HTTP transport error. It extends
    :py:exc:`MinFraudError` and adds attributes of its own.

    .. attribute:: http_status:

      The HTTP status code returned

      :type: int

    .. attribute:: uri:

      The URI queried

      :type: str

    .. attribute:: decoded_content:

      The decoded response content

      :type: str

    """

    http_status: Optional[int]
    uri: Optional[str]
    decoded_content: Optional[str]

    def __init__(
        self,
        message: str,
        http_status: Optional[int] = None,
        uri: Optional[str] = None,
        decoded_content: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.http_status = http_status
        self.uri = uri
        self.decoded_content = decoded_content


class InvalidRequestError(MinFraudError):
    """The request was invalid."""


class InsufficientFundsError(MinFraudError):
    """Your account is out of funds for the service queried."""


class PermissionRequiredError(MinFraudError):
    """Your account does not have permission to access this service."""
