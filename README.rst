================================================
minFraud Score, Insights, and Factors Python API
================================================

Description
-----------

This package provides an API for the `MaxMind minFraud Score, Insights, Factors
web services <https://dev.maxmind.com/minfraud/>`_.

Installation
------------

To install the ``minfraud`` module, type:

.. code-block:: bash

    $ pip install minfraud

If you are not able to use pip, you may also use easy_install from the
source directory:

.. code-block:: bash

    $ easy_install .

Documentation
-------------

Complete API documentation is available on `Read the Docs
<http://minfraud.readthedocs.io/>`_.

Usage
-----

To use this API, create a new ``minfraud.Client`` object. The constructor
takes your MaxMind user ID and license key:

.. code-block:: pycon

    >>> client = Client(42, 'licensekey')

The Factors service is called with the ``factors()`` method:

.. code-block:: pycon

    >>> factors = client.factors({'device': {'ip_address': '81.2.69.160'}})

The Insights service is called with the ``insights()`` method:

.. code-block:: pycon

    >>> insights = client.insights({'device': {'ip_address': '81.2.69.160'}})

The Score web service is called with the ``score()`` method:

.. code-block:: pycon

    >>> insights = client.insights({'device': {'ip_address': '81.2.69.160'}})

Each of these methods takes a dictionary representing the transaction to be sent
to the web service. The structure of this dictionary should be in `the format
specified in the REST API documentation
<https://dev.maxmind.com/minfraud/#Request_Body>`_.
The ``ip_address`` in the ``device`` sub-dictionary is required. All other
fields are optional.

Assuming validation has not been disabled, before sending the transaction to
the web service, the transaction dictionary structure and content will be
validated. If validation fails, a ``minfraud.InvalidRequestError``
will be raised.

If the dictionary is valid, a request will be made to the web service. If the
request succeeds, a model object for the service response will be returned.
If the request fails, one of the errors listed below will be raised.

Errors
------

The possible errors are:

* ``minfraud.AuthenticationError`` - This will be raised when the server
  is unable to authenticate the request, e.g., if the license key or user ID
  is invalid.
* ``minfraud.InsufficientFundsError`` - This will be raised when `your
  account <https://www.maxmind.com/en/account>`_ is out of funds.
* ``minfraud.InvalidRequestError`` - This will be raised when the server
  rejects the request as invalid for another reason, such as a missing or
  reserved IP address. It is also raised if validation of the request before
  it is sent to the server fails.
* ``minfraud.HttpError`` - This will be raised when an unexpected HTTP
  error occurs such as a firewall interfering with the request to the server.
* ``minfraud.MinFraudError`` - This will be raised when some other error
  occurs such as unexpected content from the server. This also serves as the
  base class for the above errors.

Example
-------

.. code-block:: pycon

    >>> from minfraud import Client
    >>>
    >>> client = Client(42, 'licensekey')
    >>>
    >>> request = {
    >>>     'device': {
    >>>         'ip_address': '81.2.69.160',
    >>>         'accept_language': 'en-US,en;q=0.8',
    >>>         'user_agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36'
    >>>     },
    >>>     'event': {
    >>>         'shop_id': 's2123',
    >>>         'type': 'purchase',
    >>>         'transaction_id': 'txn3134133',
    >>>         'time': '2014-04-12T23:20:50.052+00:00'
    >>>     },
    >>>     'account': {
    >>>         'user_id': '3132',
    >>>         'username_md5': '570a90bfbf8c7eab5dc5d4e26832d5b1'
    >>>     },
    >>>     'email': {
    >>>         'address': '977577b140bfb7c516e4746204fbdb01',
    >>>         'domain': 'maxmind.com'
    >>>     },
    >>>     'billing': {
    >>>         'first_name': 'Jane'
    >>>         'last_name': 'Doe',
    >>>         'company': 'Company',
    >>>         'address': '101 Address Rd.',
    >>>         'address_2': 'Unit 5',
    >>>         'city': 'Hamden',
    >>>         'region': 'CT',
    >>>         'country': 'US',
    >>>         'postal': '06510',
    >>>         'phone_country_code': '1',
    >>>         'phone_number': '323-123-4321',
    >>>     },
    >>>     'shipping': {
    >>>         'first_name': 'John'
    >>>         'last_name': 'Doe',
    >>>         'company': 'ShipCo',
    >>>         'address': '322 Ship Addr. Ln.',
    >>>         'address_2': 'St. 43',
    >>>         'city': 'New Haven',
    >>>         'region': 'CT',
    >>>         'country': 'US',
    >>>         'postal': '06510',
    >>>         'phone_country_code': '1',
    >>>         'phone_number': '403-321-2323',
    >>>         'delivery_speed': 'same_day',
    >>>     },
    >>>     'credit_card': {
    >>>         'bank_phone_country_code': '1',
    >>>         'avs_result': 'Y',
    >>>         'bank_phone_number': '800-342-1232',
    >>>         'last_4_digits': '7643',
    >>>         'cvv_result': 'N',
    >>>         'bank_name': 'Bank of No Hope',
    >>>         'issuer_id_number': '323132'
    >>>     },
    >>>     'payment': {
    >>>         'decline_code': 'invalid number',
    >>>         'was_authorized': False,
    >>>         'processor': 'stripe'
    >>>     },
    >>>     'shopping_cart': [{
    >>>         'category': 'pets',
    >>>         'quantity': 2,
    >>>         'price': 20.43,
    >>>         'item_id': 'lsh12'
    >>>     }, {
    >>>         'category': 'beauty',
    >>>         'quantity': 1,
    >>>         'price': 100.0,
    >>>         'item_id': 'ms12'
    >>>     }],
    >>>     'order': {
    >>>         'affiliate_id': 'af12',
    >>>         'referrer_uri': 'http://www.amazon.com/',
    >>>         'subaffiliate_id': 'saf42',
    >>>         'discount_code': 'FIRST',
    >>>         'currency': 'USD',
    >>>         'amount': 323.21
    >>>     }
    >>> }
    >>>
    >>> client.score(request)
    Score(...)
    >>>
    >>> client.insights(request)
    Insights(...)
    >>>
    >>> client.factors(request)
    Factors(...)

Requirements
------------

This code requires Python 2.6+ or 3.3+. Older versions are not supported.
This library has been tested with CPython and PyPy.

Versioning
----------

The minFraud Python API uses `Semantic Versioning <http://semver.org/>`_.

Support
-------

Please report all issues with this code using the `GitHub issue tracker
<https://github.com/maxmind/minfraud-api-python/issues>`_.

If you are having an issue with a MaxMind service that is not specific to the
client API, please contact `MaxMind support <http://www.maxmind.com/en/support>`_
for assistance.

Copyright and License
---------------------

This software is Copyright © 2015-2016 by MaxMind, Inc.

This is free software, licensed under the Apache License, Version 2.0.
