"""
minfraud
~~~~~~~~

A client API to MaxMind's minFraud Score and Insights web services.
"""

from minfraud.errors import MinFraudError, AuthenticationError, \
        HTTPError, InvalidRequestError, InsufficientFundsError

from minfraud.webservice import Client

__author__ = 'Gregory Oschwald'
__version__ = '0.0.1'
