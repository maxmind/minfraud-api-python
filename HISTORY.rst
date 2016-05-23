.. :changelog:

History
-------

0.4.0 (2016-05-23)
++++++++++++++++++

* Added support for the minFraud Factors.
* Added IP address risk to the minFraud Score model.
* Added the following new values to the ``/payment/processor`` validation:
  ``ccnow``, ``dalpay``, ``epay`` (repaces ``epayeu``), ``payplus``,
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
