"""
minfraud
~~~~~~~~

A client API to MaxMind's minFraud Score and Insights web services.
"""

# flake8: noqa: F401
from .errors import (
    MinFraudError,
    AuthenticationError,
    HTTPError,
    InvalidRequestError,
    InsufficientFundsError,
)

from .webservice import AsyncClient, Client
from .version import __version__

__author__ = "Gregory Oschwald"
