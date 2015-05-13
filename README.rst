minfraud-api-python
===================


.. code-block:: pycon

    >>> from minfraud.webservice import Client
    >>>
    >>> client = Client(42, 'licensekey')
    >>>
    >>> request = {
    >>>     'device': {
    >>>         'accept_language': 'en-US,en;q=0.8',
    >>>         'ip_address': '81.2.69.160',
    >>>         'user_agent':
    >>>         'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.89 Safari/537.36'
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
    >>>         'address_2': 'Unit 5',
    >>>         'region': 'CT',
    >>>         'company': 'Company',
    >>>         'phone_country_code': '1',
    >>>         'phone_number': '323-123-4321',
    >>>         'address': '101 Address Rd.',
    >>>         'last_name': 'Last',
    >>>         'country': 'US',
    >>>         'city': 'City of Thorns',
    >>>         'postal': '06510',
    >>>         'first_name': 'First'
    >>>     },
    >>>     'shipping': {
    >>>         'city': 'Nowhere',
    >>>         'postal': '73003',
    >>>         'last_name': 'ShipLast',
    >>>         'country': 'US',
    >>>         'phone_number': '403-321-2323',
    >>>         'delivery_speed': 'same_day',
    >>>         'address_2': 'St. 43',
    >>>         'phone_country_code': '1',
    >>>         'company': 'ShipCo',
    >>>         'address': '322 Ship Addr. Ln.',
    >>>         'region': 'OK',
    >>>         'first_name': 'ShipFirst'
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
    >>>         'item_id': 'ad23232'
    >>>     }, {
    >>>         'category': 'beauty',
    >>>         'quantity': 1,
    >>>         'price': 100.0,
    >>>         'item_id': 'bst112'
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
    Score(credits_remaining=5077062248, id='FB49B8E0-F987-11E4-8AD9-8B1442B6BA89', risk_score=56.41, warnings=())
    >>>
    >>> client.insights(request)
    Insights(...)


Requirements
------------

This code requires Python 2.6+ or 3.3+. Older versions are not supported.
This library has been tested with CPython and PyPy.

Versioning
----------

The minFraud Python API uses `Semantic Versioning <http://semver.org/>`_.

Copyright and License
---------------------

This software is Copyright (c) 2015 by MaxMind, Inc.

This is free software, licensed under the Apache License, Version 2.0.
