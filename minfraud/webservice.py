"""
minfraud.webservice
~~~~~~~~~~~~~~~~~~~

This module contains the webservice client class.

"""

import requests
from requests.utils import default_user_agent
from voluptuous import MultipleInvalid

from .version import __version__
from .errors import MinFraudError, HTTPError, AuthenticationError, \
    InsufficientFundsError, InvalidRequestError, PermissionRequiredError
from .models import Factors, Insights, Score
from .validation import validate_transaction


class Client(object):
    """Client for accessing the minFraud Score and Insights web services."""

    def __init__(self,
                 user_id,
                 license_key,
                 host='minfraud.maxmind.com',
                 locales=('en', ),
                 timeout=None):
        """Constructor for Client.

        :param user_id: Your MaxMind user ID
        :type user_id: int
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
        # pylint: disable=too-many-arguments
        self._locales = locales
        self._user_id = user_id
        self._license_key = license_key
        self._base_uri = u'https://{0:s}/minfraud/v2.0'.format(host)
        self._timeout = timeout

    def factors(self, transaction, validate=True):
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
        return self._response_for('factors', Factors, transaction, validate)

    def insights(self, transaction, validate=True):
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
        return self._response_for('insights', Insights, transaction, validate)

    def score(self, transaction, validate=True):
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
        return self._response_for('score', Score, transaction, validate)

    def _response_for(self, path, model_class, request, validate):
        """Send request and create response object."""
        cleaned_request = self._copy_and_clean(request)
        if validate:
            try:
                validate_transaction(cleaned_request)
            except MultipleInvalid as ex:
                raise InvalidRequestError(
                    "Invalid transaction data: {0}".format(ex))
        uri = '/'.join([self._base_uri, path])
        response = requests.post(uri,
                                 json=cleaned_request,
                                 auth=(self._user_id, self._license_key),
                                 headers={'Accept': 'application/json',
                                          'User-Agent': self._user_agent()},
                                 timeout=self._timeout)
        if response.status_code == 200:
            return self._handle_success(response, uri, model_class)
        else:
            self._handle_error(response, uri)

    def _copy_and_clean(self, data):
        """Create a copy of the data structure with Nones removed."""
        if isinstance(data, dict):
            return dict((k, self._copy_and_clean(v))
                        for (k, v) in data.items() if v is not None)
        elif isinstance(data, (list, set, tuple)):
            return [self._copy_and_clean(x) for x in data if x is not None]
        else:
            return data

    def _user_agent(self):
        """Create User-Agent header."""
        return 'minFraud-API/%s %s' % (__version__, default_user_agent())

    def _handle_success(self, response, uri, model_class):
        """Handle successful response."""
        try:
            body = response.json()
        except ValueError:
            raise MinFraudError('Received a 200 response'
                                ' but could not decode the response as '
                                'JSON: {0}'.format(response.content), 200, uri)
        if 'ip_address' in body:
            body['ip_address']['_locales'] = self._locales
        return model_class(body)

    def _handle_error(self, response, uri):
        """Handle error responses."""
        status = response.status_code

        if 400 <= status < 500:
            self._handle_4xx_status(response, status, uri)
        elif 500 <= status < 600:
            self._handle_5xx_status(status, uri)
        else:
            self._handle_non_200_status(status, uri)

    def _handle_4xx_status(self, response, status, uri):
        """Handle error responses with 4xx status codes."""
        if not response.content:
            raise HTTPError('Received a {0} error with no body'.format(status),
                            status, uri)
        elif response.headers.get('Content-Type', '').find('json') == -1:
            raise HTTPError('Received a {0} with the following '
                            'body: {1}'.format(status, response.content),
                            status, uri)
        try:
            body = response.json()
        except ValueError:
            raise HTTPError(
                'Received a {status:d} error but it did not include'
                ' the expected JSON body: {content}'.format(
                    status=status, content=response.content),
                status,
                uri)
        else:
            if 'code' in body and 'error' in body:
                self._handle_web_service_error(
                    body.get('error'), body.get('code'), status, uri)
            else:
                raise HTTPError(
                    'Error response contains JSON but it does not specify code'
                    ' or error keys: {0}'.format(response.content), status,
                    uri)

    def _handle_web_service_error(self, message, code, status, uri):
        """Handle error responses with the JSON body from the web service."""
        if code in ('AUTHORIZATION_INVALID', 'LICENSE_KEY_REQUIRED',
                    'USER_ID_REQUIRED'):
            raise AuthenticationError(message)
        elif code == 'INSUFFICIENT_FUNDS':
            raise InsufficientFundsError(message)
        elif code == 'PERMISSION_REQUIRED':
            raise PermissionRequiredError(message)

        raise InvalidRequestError(message, code, status, uri)

    def _handle_5xx_status(self, status, uri):
        """Handle error response with 5xx status codes."""
        raise HTTPError(u'Received a server error ({0}) for '
                        u'{1}'.format(status, uri), status, uri)

    def _handle_non_200_status(self, status, uri):
        """Handle successful responses with unexpected status codes."""
        raise HTTPError(u'Received an unexpected HTTP status '
                        u'({0}) for {1}'.format(status, uri), status, uri)
