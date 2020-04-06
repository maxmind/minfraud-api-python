.. :changelog:

History
-------

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
