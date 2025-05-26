.. :changelog:

History
-------

3.1.0 (2025-05-23)
++++++++++++++++++

* Added support for the ``/billing_phone/matches_postal`` and
  ``/shipping_phone/matches_postal`` outputs. These are available as the
  ``matches_postal`` attribute on ``minfraud.model.Phone``.
* Added ``cryptomus`` to the ``/payment/processor`` validation.

3.0.0 (2025-02-10)
++++++++++++++++++

* BREAKING CHANGE: The ``minfraud.model.*`` classes have been refactored to
  simplify them and make them more flexible. They are no longer subclass
  NamedTuple and are now standard Python classes. This also means the
  classes are no longer immutable. For most users, these differences should
  not impact their integration.
* BREAKING CHANGE: Model attributes that were formerly tuples are now lists.
* BREAKING CHANGE: The deprecated `is_high_risk` attribute on
  `resp.ip_address.country` has been removed.
* IMPORTANT: Python 3.9 or greater is required. If you are using an older
  version, please use an earlier release.
* Added ``to_dict`` methods to the model classes. These return a dict version
  of the object that is suitable for serialization. It recursively calls
  ``to_dict`` or the equivalent on all objects contained within the object.
* The minFraud Factors subscores have been deprecated. They will be removed
  in March 2025. Please see `our release notes <https://dev.maxmind.com/minfraud/release-notes/2024/#deprecation-of-risk-factor-scoressubscores>`_
  for more information.
* Added ``epayco`` to the ``/payment/processor`` validation.

2.12.0b1 (2024-09-06)
+++++++++++++++++++++

* ``setuptools`` was incorrectly listed as a runtime dependency. This has
  been removed.
* Added support for the new risk reasons outputs in minFraud Factors. The risk
  reasons output codes and reasons are currently in beta and are subject to
  change. We recommend that you use these beta outputs with caution and avoid
  relying on them for critical applications.

2.11.0 (2024-07-08)
+++++++++++++++++++

* Updated the validation for the Report Transactions API to make the
  ``ip_address`` parameter optional. Now the ``tag`` and at least one of the
  following parameters must be supplied: ``ip_address``, ``maxmind_id``,
  ``minfraud_id``, ``transaction_id``.
* Added ``billing_phone`` and ``shipping_phone`` properties to the minFraud
  Insights and Factors response models. These contain objects with information
  about the respective phone numbers. Please see `our developer
  site <https://dev.maxmind.com/minfraud/api-documentation/responses/>`_ for
  more information.
* Added ``payconex`` to the ``/payment/processor`` validation.

2.10.0 (2024-04-16)
+++++++++++++++++++

* Added the following new values to the ``/payment/processor`` validation:

  * ``pxp_financial``
  * ``trustpay``

* Equivalent domain names are now normalized when ``hash_email`` is used.
  For example, ``googlemail.com`` will become ``gmail.com``.
* Periods are now removed from ``gmail.com`` email address local parts when
  ``hash_email`` is used. For example, ``f.o.o@gmail.com`` will become
  ``foo@gmail.com``.
* Fastmail alias subdomain email addresses are now normalized when
  ``hash_email`` is used. For example, ``alias@user.fastmail.com`` will
  become ``user@fastmail.com``.
* Additional ``yahoo.com`` email addresses now have aliases removed from
  their local part when ``hash_email`` is used. For example,
  ``foo-bar@yahoo.com`` will become ``foo@yahoo.com`` for additional
  ``yahoo.com`` domains.
* Duplicate ``.com`` s are now removed from email domain names when
  ``hash_email`` is used. For example, ``example.com.com`` will become
  ``example.com``.
* Certain TLD typos are now normalized when ``hash_email`` is used. For
  example, ``example.comcom`` will become ``example.com``.
* Additional ``gmail.com`` domain names with leading digits are now
  normalized when ``hash_email`` is used. For example, ``100gmail.com`` will
  become ``gmail.com``.
* Additional ``gmail.com`` typos are now normalized when ``hash_email`` is
  used. For example, ``gmali.com`` will become ``gmail.com``.
* When ``hash_email`` is used, the local part of an email address is now
  normalized to NFC.

2.9.0 (2023-12-05)
++++++++++++++++++

* IMPORTANT: Python 3.8 or greater is required. If you are using an older
  version, please use an earlier release.
* Updated ``geoip2`` to version that includes the ``is_anycast`` attribute on
  ``geoip2.record.Traits``. This property is ``True`` if the IP address
  belongs to an `anycast network <https://en.wikipedia.org/wiki/Anycast>`_.
  This is available in minFraud Insights and Factors.

2.8.0 (2023-05-09)
++++++++++++++++++

* IMPORTANT: Python 3.7 or greater is required. If you are using an older
  version, please use an earlier release.
* Added the following new values to the ``/payment/processor`` validation:

  * ``google_pay``
  * ``placetopay``
  * ``shopify_payments``

2.7.2 (2022-03-29)
++++++++++++++++++

* Updated code to correctly handle ``None`` ``Content-Type`` from minFraud
  web service. This should never happen, but if it does, the correct
  exception will now be thrown.

2.7.1 (2022-03-29)
++++++++++++++++++

* Fixed ``KeyError`` when using the ``report()`` method. Reported by siang.
  GitHub #99.

2.7.0 (2022-03-28)
++++++++++++++++++

* Added the input ``/credit_card/country``. This is the country where the
  issuer of the card is located. This may be passed instead of
  ``/credit_card/issuer_id_number`` if you do not wish to pass partial
  account numbers or if your payment processor does not provide them.

2.6.0 (2022-01-25)
++++++++++++++++++

* Upgraded ``geoip2`` to 4.5.0. This adds mobile country code (MCC) and mobile
  network code (MNC) to minFraud Insights and Factors responses. These are
  available at ``response.ip_address.traits.mobile_country_code`` and
  ``response.ip_address.traits.mobile_network_code``. We expect this data to be
  available by late January, 2022.
* Added the following new values to the ``/payment/processor`` validation:

  * ``boacompra``
  * ``boku``
  * ``coregateway``
  * ``fiserv``
  * ``neopay``
  * ``neosurf``
  * ``openbucks``
  * ``paysera``
  * ``payvision``
  * ``trustly``
  * ``windcave``

* The ``/credit_card/last_4_digits`` input has been deprecated in favor of
  ``/credit_card/last_digits`` and will be removed in a future release.
  ``last_digits``/``last_4_digits`` also now supports two digit values in
  addition to the previous four digit values.
* Eight digit ``/credit_card/issuer_id_number`` inputs are now supported in
  addition to the previously accepted six digit ``issuer_id_number``. In most
  cases, you should send the last four digits for ``last_digits``. If you send
  an ``issuer_id_number`` that contains an eight digit IIN, and if the credit
  card brand is not one of the following, you should send the last two digits
  for ``last_digits``:

  * ``Discover``
  * ``JCB``
  * ``Mastercard``
  * ``UnionPay``
  * ``Visa``

2.5.0 (2021-09-20)
++++++++++++++++++

* Previously, the ``py.typed`` file was not being added to the source
  distribution. It is now explicitly specified in the manifest.

2.4.0 (2021-08-26)
++++++++++++++++++

* Added the following new values to the ``/payment/processor`` validation:

  * ``cardknox``
  * ``creditguard``
  * ``credorax``
  * ``datacap``
  * ``dlocal``
  * ``onpay``
  * ``safecharge``

* Added ``rule_label`` to minFraud output ``/disposition``.
* Added ``was_3d_secure_successful`` to ``/credit_card`` validation

2.3.1 (2021-02-12)
++++++++++++++++++

* In 2.2.0 and 2.3.0, a ``KeyError`` would be thrown if the response from the
  web service did not have the ``ip_address`` key but did contain the text
  "ip_address" in the JSON body. Reported and fixed by Justas-iDenfy. GitHub
  #78.

2.3.0 (2021-02-02)
++++++++++++++++++

* You may now set a proxy to use when making web service requests by passing
  the ``proxy`` parameter to the ``AsyncClient`` or ``Client`` constructor.
* Added ``apple_pay`` and ``aps_payments`` to the ``/payment/processor``
  validation.
* You may now enable client-side email hashing by setting the keyword argument
  ``hash_email`` to ``True`` in the web-service client request methods (i.e.,
  ``score``, ``insights``, ``factors``). When set, this normalizes the email
  address and sends an MD5 hash of it to the web service rather than the
  plain-text address. Note that the email domain will still be sent in plain
  text.
* Added support for the IP address risk reasons in the minFraud Insights and
  Factors responses. This is available at ``.ip_address.risk_reasons``. It is
  an array of ``IPRiskReason`` objects.

2.2.0 (2020-10-13)
++++++++++++++++++

* Added ``tsys`` to the ``/payment/processor`` validation.
* The device IP address is no longer a required input.

2.1.0 (2020-09-25)
++++++++++++++++++

* Added ``response.ip_address.traits.is_residential_proxy`` to the
  minFraud Insights and Factors models. This indicates whether the IP
  address is on a suspected anonymizing network and belongs to a
  residential ISP.
* ``HTTPError`` now provides the decoded response content in the
  ``decoded_content`` attribute.

2.0.3 (2020-07-28)
++++++++++++++++++

* Added ``py.typed`` file per PEP 561. Reported by Árni Már Jónsson. GitHub
  #62.
* Tightened ``install_requirements`` for dependencies to prevent a new
  major version from being installed.

2.0.2 (2020-07-27)
++++++++++++++++++

* Fixed type annotation for ``locales`` in ``minfraud.webservice`` to allow
  tuples of arbitrary length. Reported by Árni Már Jónsson. GitHub #60.

2.0.1 (2020-07-21)
++++++++++++++++++

* Minor documentation fix.

2.0.0 (2020-07-21)
++++++++++++++++++

* IMPORTANT: Python 2.7 and 3.5 support has been dropped. Python 3.6 or greater
  is required.
* Asyncio support has been added for web service requests. To make async
  requests, use ``minfraud.AsyncClient``.
* ``minfraud.Client`` now provides a ``close()`` method and an associated
  context manager to be used in ``with`` statements.
* For both ``Client`` and ``AsyncClient`` requests, the default timeout is
  now 60 seconds.
* Type hints have been added.
* Email validation is now done with ``email_validator`` rather than
  ``validate_email``.
* URL validation is now done with ``urllib.parse`` rather than ``rfc3987``.
* RFC 3339 timestamp validation is now done via a regular expression.

1.13.0 (2020-07-14)
+++++++++++++++++++

* Added the following new values to the ``/payment/processor`` validation:

  * ``cashfree``
  * ``first_atlantic_commerce``
  * ``komoju``
  * ``paytm``
  * ``razorpay``
  * ``systempay``

* Added support for the following new subscores in Factors responses:

  * ``device``: the risk associated with the device
  * ``email_local_part``: the risk associated with the email address local part
  * ``shipping_address``: the risk associated with the shipping address

1.12.1 (2020-06-17)
+++++++++++++++++++

* Fixes documentation that caused warnings when building a distribution.

1.12.0 (2020-06-17)
+++++++++++++++++++

* Added support for the Report Transactions API. We encourage use of this API
  as we use data received through this channel to continually improve the
  accuracy of our fraud detection algorithms.

1.11.0 (2020-04-06)
+++++++++++++++++++

* Added support for the new credit card output ``/credit_card/is_business``.
  This indicates whether the card is a business card. It may be accessed via
  ``response.credit_card.is_business`` on the minFraud Insights and Factors
  response objects.

1.10.0 (2020-03-26)
+++++++++++++++++++

* Added support for the new email domain output ``/email/domain/first_seen``.
  This may be accessed via ``response.email.domain.first_seen`` on the
  minFraud Insights and Factors response objects.
* Added the following new values to the ``/payment/processor`` validation:

  * ``cardpay``
  * ``epx``

1.9.0 (2020-02-21)
++++++++++++++++++

* Added support for the new email output ``/email/is_disposable``. This may
  be accessed via the ``is_disposable`` attribute of
  ``minfraud.models.Email``.

1.8.0 (2019-12-20)
++++++++++++++++++

* The client-side validation for numeric custom inputs has been updated to
  match the server-side validation. The valid range is -9,999,999,999,999
  to 9,999,999,999,999. Previously, larger numbers were allowed.
* Python 3.3 and 3.4 are no longer supported.
* Added the following new values to the ``/payment/processor`` validation:

  * ``affirm``
  * ``afterpay``
  * ``cetelem``
  * ``datacash``
  * ``dotpay``
  * ``ecommpay``
  * ``g2a_pay``
  * ``gocardless``
  * ``interac``
  * ``klarna``
  * ``mercanet``
  * ``payeezy``
  * ``paylike``
  * ``payment_express``
  * ``paysafecard``
  * ``smartdebit``
  * ``synapsefi``

* Deprecated the ``email_tenure`` and ``ip_tenure`` attributes of
  ``minfraud.models.Subscores``.
* Deprecated the ``is_high_risk`` attribute of
  ``minfraud.models.GeoIP2Country``.

1.7.0 (2018-04-10)
++++++++++++++++++

* Python 2.6 support has been dropped. Python 2.7+ or 3.3+ is now required.
* Renamed MaxMind user ID to account ID in the code and added support for the
  new ``ACCOUNT_ID_REQUIRED`` error code.
* Added the following new values to the ``/payment/processor`` validation:

  * ``ccavenue``
  * ``ct_payments``
  * ``dalenys``
  * ``oney``
  * ``posconnect``

* Added support for the ``/device/local_time`` output.
* Added support for the ``/credit_card/is_virtual`` output.
* Added ``payout_change`` to the ``/event/type`` input validation.

1.6.0 (2018-01-18)
++++++++++++++++++

* Updated ``geoip2`` dependency. This version adds the
  ``is_in_european_union`` attribute to ``geoip2.record.Country`` and
  ``geoip2.record.RepresentedCountry``. This attribute is ``True`` if the
  country is a member state of the European Union.
* Added the following new values to the ``/payment/processor`` validation:

  * ``cybersource``
  * ``transact_pro``
  * ``wirecard``

1.5.0 (2017-10-30)
++++++++++++++++++

* Added the following new values to the ``/payment/processor`` validation:

  * ``bpoint``
  * ``checkout_com``
  * ``emerchantpay``
  * ``heartland``
  * ``payway``

* Updated ``geoip2`` dependency to add support for GeoIP2 Precision Insights
  anonymizer fields.

1.4.0 (2017-07-06)
++++++++++++++++++

* Added support for custom inputs. You may set up custom inputs from your
  account portal.
* Added the following new values to the ``/payment/processor`` validation:

  * ``american_express_payment_gateway``
  * ``bluesnap``
  * ``commdoo``
  * ``curopayments``
  * ``ebs``
  * ``exact``
  * ``hipay``
  * ``lemon_way``
  * ``oceanpayment``
  * ``paymentwall``
  * ``payza``
  * ``securetrading``
  * ``solidtrust_pay``
  * ``vantiv``
  * ``vericheck``
  * ``vpos``

* Added the following new input values:
  ``/device/session_age`` and ``/device/session_id``.
* Added support for the ``/email/first_seen`` output.

1.3.2 (2016-12-08)
++++++++++++++++++

* Recent releases of ``requests`` (2.12.2 and 2.12.3) require that the
  username for basic authentication be a string or bytes. The documentation
  for this module uses an integer for the ``user_id``, which will break with
  these ``requests`` versions. The ``user_id`` is now converted to bytes
  before being passed to ``requests``.
* Fixed test breakage on 3.6.

1.3.1 (2016-11-22)
++++++++++++++++++

* Fixed ``setup.py`` on Python 2.

1.3.0 (2016-11-22)
++++++++++++++++++

* The disposition was added to the minFraud response models. This is used to
  return the disposition of the transaction as set by the custom rules for the
  account.
* Fixed package's long description for display on PyPI.

1.2.0 (2016-11-14)
++++++++++++++++++

* Allow ``/credit_card/token`` input.

1.1.0 (2016-10-10)
++++++++++++++++++

* Added the following new values to the ``/event/type`` validation:
  ``email_change`` and ``password_reset``.

1.0.0 (2016-09-15)
++++++++++++++++++

* Added the following new values to the ``/payment/processor`` validation:
  ``concept_payments``, ``ecomm365``, ``orangepay``, and ``pacnet_services``.
* `ipaddress` is now used for IP validation on Python 2 instead of `ipaddr`.

0.5.0 (2016-06-08)
++++++++++++++++++

* BREAKING CHANGE: ``credits_remaining`` has been removed from the web service
  response model and has been replaced by ``queries_remaining``.
* Added ``queries_remaining`` and ``funds_remaining``. Note that
  ``funds_remaining`` will not be returned by the web service until our new
  credit system is in place.
* ``confidence`` and ``last_seen`` were added to the ``Device`` response
  model.

0.4.0 (2016-05-23)
++++++++++++++++++

* Added support for the minFraud Factors.
* Added IP address risk to the minFraud Score model.
* Added the following new values to the ``/payment/processor`` validation:
  ``ccnow``, ``dalpay``, ``epay`` (replaces ``epayeu``), ``payplus``,
  ``pinpayments``, ``quickpay``, and ``verepay``.
* A ``PERMISSION_REQUIRED`` error will now throw a ``PermissionRequiredError``
  exception.

0.3.0 (2016-01-20)
++++++++++++++++++

* Added support for new minFraud Insights outputs. These are:

  * ``/credit_card/brand``
  * ``/credit_card/type``
  * ``/device/id``
  * ``/email/is_free``
  * ``/email/is_high_risk``

* ``input`` on the ``Warning`` response model has been replaced with
  ``input_pointer``. The latter is a JSON pointer to the input that
  caused the warning.

0.2.0 (2015-08-10)
++++++++++++++++++

* Added ``is_gift`` and ``has_gift_message`` to `order` input dictionary
  validation.
* Request keys with ``None`` values are no longer validated or sent to the
  web service.

0.1.0 (2015-06-29)
++++++++++++++++++

* First beta release.

0.0.1 (2015-06-19)
++++++++++++++++++

* Initial release.
