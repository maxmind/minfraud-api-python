"""
minfraud
~~~~~~~~

A client API to MaxMind's minFraud Score and Insights web services.
"""

# flake8: noqa: F401
from .errors import (
    AuthenticationError,
    HTTPError,
    InsufficientFundsError,
    InvalidRequestError,
    MinFraudError,
)
from .version import __version__
from .webservice import AsyncClient, Client

__author__ = "Gregory Oschwald"
