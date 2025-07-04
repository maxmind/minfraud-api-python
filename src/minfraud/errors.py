"""Typed errors thrown by this library."""

from __future__ import annotations


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
    """

    http_status: int | None
    """The HTTP status code returned"""

    uri: str | None
    """The URI queried"""

    decoded_content: str | None
    """The decoded response content"""

    def __init__(
        self,
        message: str,
        http_status: int | None = None,
        uri: str | None = None,
        decoded_content: str | None = None,
    ) -> None:
        """Initialize an HTTPError instance."""
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
