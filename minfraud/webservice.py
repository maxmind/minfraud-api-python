import requests
from requests.utils import default_user_agent
from voluptuous import MultipleInvalid
import minfraud
from minfraud.errors import MinFraudError, HTTPError, AddressNotFoundError, AuthenticationError, InsufficientFundsError, \
    InvalidRequestError
from minfraud.models import Insights, Score
from minfraud.validation import validate_transaction


class Client(object):
    def __init__(self, user_id, license_key,
                 host='minfraud.maxmind.com',
                 locales=None,
                 timeout=None):
        # pylint: disable=too-many-arguments
        if locales is None:
            locales = ['en']
        self._locales = locales
        self._user_id = user_id
        self._license_key = license_key
        self._base_uri = u'https://{0:s}/minfraud/v2.0'.format(host)
        self._timeout = timeout

    def insights(self, transaction, validate=True):
        return self._response_for('insights', Insights, transaction, validate)

    def score(self, transaction, validate=True):
        return self._response_for('score', Score, transaction, validate)

    def _response_for(self, path, model_class, request, validate):
        if validate:
            try:
                validate_transaction(request)
            except MultipleInvalid as e:
                raise InvalidRequestError(
                    "Invalid transaction data: {}".format(e))
        uri = '/'.join([self._base_uri, path])
        response = requests.post(
            uri,
            json=request,
            auth=(self._user_id, self._license_key),
            headers=
            {'Accept': 'application/json',
             'User-Agent': self._user_agent()},
            timeout=self._timeout)
        if response.status_code == 200:
            return self._handle_success(response, uri, model_class)
        else:
            self._handle_error(response, uri)

    def _user_agent(self):
        return 'minFraud-API/%s %s' % (minfraud.__version__,
                                       default_user_agent())

    def _handle_success(self, response, uri, model_class):
        try:
            body = response.json()
        except ValueError as ex:
            raise MinFraudError('Received a 200 response'
                                ' but could not decode the response as '
                                'JSON: {}'.format(response.content), 200, uri)
        if 'ip_location' in body:
            body['locales'] = self._locales
        return model_class(body)

    def _handle_error(self, response, uri):
        status = response.status_code

        if 400 <= status < 500:
            self._handle_4xx_status(response, status, uri)
        elif 500 <= status < 600:
            self._handle_5xx_status(status, uri)
        else:
            self._handle_non_200_status(status, uri)

    def _handle_4xx_status(self, response, status, uri):
        if not response.content:
            raise HTTPError('Received a {} error with no body'.format(status),
                            status, uri)
        elif response.headers.get('Content-Type', '').find('json') == -1:
            raise HTTPError('Received a {} with the following '
                            'body: {}'.format(status, response.content),
                            status, uri)
        try:
            body = response.json()
        except ValueError as ex:
            raise HTTPError(
                'Received a {status:d} error but it did not include'
                ' the expected JSON body: {content}'
                .format(status=status,
                        uri=uri,
                        content=response.content), status, uri)
        else:
            if 'code' in body and 'error' in body:
                self._handle_web_service_error(body.get('error'),
                                               body.get('code'), status, uri)
            else:
                raise HTTPError(
                    'Error response contains JSON but it does not specify code'
                    ' or error keys: {}'.format(response.content), status, uri)

    def _handle_web_service_error(self, message, code, status, uri):
        if code in ('IP_ADDRESS_NOT_FOUND', 'IP_ADDRESS_RESERVED'):
            raise AddressNotFoundError(message)
        elif code in ('AUTHORIZATION_INVALID', 'LICENSE_KEY_REQUIRED',
                      'USER_ID_REQUIRED'):
            raise AuthenticationError(message)
        elif code == 'INSUFFICIENT_FUNDS':
            raise InsufficientFundsError(message)

        raise InvalidRequestError(message, code, status, uri)

    def _handle_5xx_status(self, status, uri):
        raise HTTPError(u'Received a server error ({0}) for '
                        u'{1}'.format(status, uri), status, uri)

    def _handle_non_200_status(self, status, uri):
        raise HTTPError(u'Received an unexpected HTTP status '
                        u'({0}) for {1}'.format(status, uri), status, uri)
