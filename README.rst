===================
minFraud Python API
===================

Description
-----------

This package provides an API for the `MaxMind minFraud Score, Insights, and
Factors web services <https://dev.maxmind.com/minfraud/>`_ as well as the
`Report Transaction web service
<https://dev.maxmind.com/minfraud/report-a-transaction?lang=en>`_.

Installation
------------

To install the ``minfraud`` module, type:

.. code-block:: bash

    $ pip install minfraud

If you are not able to install from PyPI, you may also use ``pip`` from the
source directory:

.. code-block:: bash

    $ python -m pip install .

Documentation
-------------

Complete API documentation is available on `Read the Docs
<https://minfraud.readthedocs.io/>`_.

Usage
-----

To use this API, create a new ``minfraud.Client`` object for a synchronous
request or ``minfraud.AsyncClient`` for an asynchronous request. The
constructors take your MaxMind account ID and license key:

.. code-block:: pycon

    >>> client = Client(42, 'licensekey')
    >>> async_client = AsyncClient(42, 'licensekey')

To use the Sandbox web service instead of the production web service,
you can provide the host argument:

.. code-block:: pycon

    >>> client = Client(42, 'licensekey', 'sandbox.maxmind.com')
    >>> async_client = AsyncClient(42, 'licensekey', 'sandbox.maxmind.com')

Score, Insights and Factors Usage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Factors service is called with the ``factors()`` method:

.. code-block:: pycon

    >>> client.factors({'device': {'ip_address': '152.216.7.110'}})
    >>> await async_client.factors({'device': {'ip_address': '152.216.7.110'}})

The Insights service is called with the ``insights()`` method:

.. code-block:: pycon

    >>> client.insights({'device': {'ip_address': '152.216.7.110'}})
    >>> await async_client.insights({'device': {'ip_address': '152.216.7.110'}})

The Score web service is called with the ``score()`` method:

.. code-block:: pycon

    >>> client.score({'device': {'ip_address': '152.216.7.110'}})
    >>> await async_client.score({'device': {'ip_address': '152.216.7.110'}})

Each of these methods takes a dictionary representing the transaction to be sent
to the web service. The structure of this dictionary should be in `the format
specified in the REST API documentation
<https://dev.maxmind.com/minfraud/api-documentation/requests?lang=en>`__.
All fields are optional.

Report Transactions Usage
^^^^^^^^^^^^^^^^^^^^^^^^^

MaxMind encourages the use of this API as data received through this channel is
used to continually improve the accuracy of our fraud detection algorithms. The
Report Transaction web service is called with the ``report()`` method:

.. code-block:: pycon

    >>> client.report({'ip_address': '152.216.7.110', 'tag': 'chargeback'})
    >>> await async_client.report({'ip_address': '152.216.7.110', 'tag': 'chargeback'})

The method takes a dictionary representing the report to be sent to the web
service. The structure of this dictionary should be in `the format specified
in the REST API documentation
<https://dev.maxmind.com/minfraud/report-a-transaction?lang=en>`__. The
required fields are ``tag`` and one or more of the following: ``ip_address``,
``maxmind_id``, ``minfraud_id``, ``transaction_id``.

Request Validation (for all request methods)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
  is unable to authenticate the request, e.g., if the license key or account
  ID is invalid.
* ``minfraud.InvalidRequestError`` - This will be raised when the server
  rejects the request as invalid for another reason, such as a reserved IP
  address. It is also raised if validation of the request before it is sent to
  the server fails.
* ``minfraud.HttpError`` - This will be raised when an unexpected HTTP
  error occurs such as a firewall interfering with the request to the server.
* ``minfraud.MinFraudError`` - This will be raised when some other error
  occurs such as unexpected content from the server. This also serves as the
  base class for the above errors.

Additionally, ``score``, ``insights`` and ``factors`` may also raise:

* ``minfraud.InsufficientFundsError`` - This will be raised when `your
  account <https://www.maxmind.com/en/account>`_ is out of funds.

Examples
--------

Score, Insights and Factors Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: pycon

    >>> import asyncio
    >>> from minfraud import AsyncClient, Client
    >>>
    >>> request = {
    >>>     'device': {
    >>>         'ip_address': '152.216.7.110',
    >>>         'accept_language': 'en-US,en;q=0.8',
    >>>         'session_age': 3600,
    >>>         'session_id': 'a333a4e127f880d8820e56a66f40717c',
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
    >>>         'first_name': 'Jane',
    >>>         'last_name': 'Doe',
    >>>         'company': 'Company',
    >>>         'address': '101 Address Rd.',
    >>>         'address_2': 'Unit 5',
    >>>         'city': 'Hamden',
    >>>         'region': 'CT',
    >>>         'country': 'US',
    >>>         'postal': '06510',
    >>>         'phone_country_code': '1',
    >>>         'phone_number': '123-456-7890',
    >>>     },
    >>>     'shipping': {
    >>>         'first_name': 'John',
    >>>         'last_name': 'Doe',
    >>>         'company': 'ShipCo',
    >>>         'address': '322 Ship Addr. Ln.',
    >>>         'address_2': 'St. 43',
    >>>         'city': 'New Haven',
    >>>         'region': 'CT',
    >>>         'country': 'US',
    >>>         'postal': '06510',
    >>>         'phone_country_code': '1',
    >>>         'phone_number': '123-456-0000',
    >>>         'delivery_speed': 'same_day',
    >>>     },
    >>>     'credit_card': {
    >>>         'bank_phone_country_code': '1',
    >>>         'avs_result': 'Y',
    >>>         'bank_phone_number': '123-456-1234',
    >>>         'last_digits': '7643',
    >>>         'cvv_result': 'N',
    >>>         'bank_name': 'Bank of No Hope',
    >>>         'issuer_id_number': '411111',
    >>>         'was_3d_secure_successful': True
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
    >>>      },
    >>>     'custom_inputs': {
    >>>         'section': 'news',
    >>>         'num_of_previous_purchases': 19,
    >>>         'discount': 3.2,
    >>>         'previous_user': True
    >>>     }
    >>> }
    >>>
    >>> # This example function uses a synchronous Client object. The object
    >>> # can be used across multiple requests.
    >>> def client(account_id, license_key):
    >>>     with Client(account_id, license_key) as client:
    >>>
    >>>         print(client.score(request))
    Score(...)
    >>>
    >>>         print(client.insights(request))
    Insights(...)
    >>>
    >>>         print(client.factors(request))
    Factors(...)
    >>>
    >>> # This example function uses an asynchronous AsyncClient object. The
    >>> # object can be used across multiple requests.
    >>> async def async_client(account_id, license_key):
    >>>     async with AsyncClient(account_id, license_key) as client:
    >>>
    >>>         print(await client.score(request))
    Score(...)
    >>>
    >>>         print(await client.insights(request))
    Insights(...)
    >>>
    >>>         print(await client.factors(request))
    Factors(...)
    >>>
    >>> client(42, 'license_key')
    >>> asyncio.run(async_client(42, 'license_key'))

Report Transactions Example
^^^^^^^^^^^^^^^^^^^^^^^^^^^

For synchronous reporting:

.. code-block:: pycon

    >>> from minfraud import Client
    >>>
    >>> with Client(42, 'licensekey') as client
    >>>     transaction_report = {
    >>>         'ip_address': '152.216.7.110',
    >>>         'tag': 'chargeback',
    >>>         'minfraud_id': '2c69df73-01c0-45a5-b218-ed85f40b17aa',
    >>>      }
    >>>      client.report(transaction_report)

For asynchronous reporting:

.. code-block:: pycon

    >>> import asyncio
    >>> from minfraud import AsyncClient
    >>>
    >>> async def report():
    >>>     async with AsyncClient(42, 'licensekey') as client
    >>>         transaction_report = {
    >>>             'ip_address': '152.216.7.110',
    >>>             'tag': 'chargeback',
    >>>             'minfraud_id': '2c69df73-01c0-45a5-b218-ed85f40b17aa',
    >>>          }
    >>>          await async_client.report(transaction_report)
    >>>
    >>> asyncio.run(report())

Requirements
------------

Python 3.9 or greater is required. Older versions are not supported.

Versioning
----------

The minFraud Python API uses `Semantic Versioning <https://semver.org/>`_.

Support
-------

Please report all issues with this code using the `GitHub issue tracker
<https://github.com/maxmind/minfraud-api-python/issues>`_.

If you are having an issue with a MaxMind service that is not specific to the
client API, please contact `MaxMind support <https://www.maxmind.com/en/support>`_
for assistance.

Copyright and License
---------------------

This software is Copyright © 2015-2025 by MaxMind, Inc.

This is free software, licensed under the Apache License, Version 2.0.
