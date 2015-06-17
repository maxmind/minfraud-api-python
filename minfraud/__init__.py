"""
minfraud
~~~~~~~~

A client API to MaxMind's minFraud Score and Insights web services.
"""

from .errors import MinFraudError, AuthenticationError, \
    HTTPError, InvalidRequestError, InsufficientFundsError

from .webservice import Client
from .version import __version__

__author__ = 'Gregory Oschwald'
