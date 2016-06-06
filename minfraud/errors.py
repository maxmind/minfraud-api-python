"""
minfraud.errors
~~~~~~~~~~~~~~~

This module contains errors that are raised by this package.

"""


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

    """

    def __init__(self, message, http_status=None, uri=None):
        super(HTTPError, self).__init__(message)
        self.http_status = http_status
        self.uri = uri


class InvalidRequestError(MinFraudError):
    """The request was invalid."""


class InsufficientFundsError(MinFraudError):
    """Your account is out of funds for the service queried."""


class PermissionRequiredError(MinFraudError):
    """Your account does not have permission to access this service."""
