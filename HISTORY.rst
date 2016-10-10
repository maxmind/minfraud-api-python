.. :changelog:

History
-------

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
