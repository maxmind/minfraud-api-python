"""
minfraud.models
~~~~~~~~~~~~~~~

This module contains models for the minFraud response object.

"""

# pylint:disable=too-many-lines,too-many-instance-attributes,too-many-locals
from typing import Dict, List, Optional, Sequence

from geoip2.mixins import SimpleEquality
import geoip2.models
import geoip2.records


class IPRiskReason(SimpleEquality):
    """Reason for the IP risk.

    This class provides both a machine-readable code and a human-readable
    explanation of the reason for the IP risk score.

    Although more codes may be added in the future, the current codes are:

    - ``ANONYMOUS_IP`` - The IP address belongs to an anonymous network. See
      the object at ``->ipAddress->traits`` for more details.
    - ``BILLING_POSTAL_VELOCITY`` - Many different billing postal codes have
      been seen on this IP address.
    - ``EMAIL_VELOCITY`` - Many different email addresses have been seen on this
      IP address.
    - ``HIGH_RISK_DEVICE`` - A high risk device was seen on this IP address.
    - ``HIGH_RISK_EMAIL`` - A high risk email address was seen on this IP
      address in your past transactions.
    - ``ISSUER_ID_NUMBER_VELOCITY`` - Many different issuer ID numbers have been
      seen on this IP address.
    - ``MINFRAUD_NETWORK_ACTIVITY`` - Suspicious activity has been seen on this
      IP address across minFraud customers.

    .. attribute:: code

      This value is a machine-readable code identifying the
      reason.

      :type: str | None

    .. attribute:: reason

      This property provides a human-readable explanation of the
      reason. The text may change at any time and should not be matched
      against.

      :type: str | None
    """

    code: Optional[str]
    reason: Optional[str]

    def __init__(self, code: Optional[str] = None, reason: Optional[str] = None):
        self.code = code
        self.reason = reason


class GeoIP2Location(geoip2.records.Location):
    """Location information for the IP address.

    In addition to the attributes provided by ``geoip2.records.Location``,
    this class provides:

    .. attribute:: local_time

      The date and time of the transaction in the time
      zone associated with the IP address. The value is formatted according to
      `RFC 3339 <https://tools.ietf.org/html/rfc3339>`_. For instance, the
      local time in Boston might be returned as 2015-04-27T19:17:24-04:00.

      :type: str | None


    Parent:

    """

    __doc__ += geoip2.records.Location.__doc__  # type: ignore

    local_time: Optional[str]

    def __init__(self, *args, **kwargs) -> None:
        self.local_time = kwargs.get("local_time", None)
        super().__init__(*args, **kwargs)


class GeoIP2Country(geoip2.records.Country):
    """Country information for the IP address.

    In addition to the attributes provided by ``geoip2.records.Country``,
    this class provides:

    .. attribute:: is_high_risk

      This is true if the IP country is high risk.

      :type: bool | None

      .. deprecated:: 1.8.0
        Deprecated effective August 29, 2019.

    Parent:

    """

    __doc__ += geoip2.records.Country.__doc__  # type: ignore

    is_high_risk: bool

    def __init__(self, *args, **kwargs) -> None:
        self.is_high_risk = kwargs.get("is_high_risk", False)
        super().__init__(*args, **kwargs)


class IPAddress(geoip2.models.Insights):
    """Model for minFraud and GeoIP2 data about the IP address.

    .. attribute:: risk

      This field contains the risk associated with the IP address. The value
      ranges from 0.01 to 99. A higher score indicates a higher risk.

      :type: float | None

    .. attribute:: risk_reasons

      This tuple contains :class:`.IPRiskReason` objects identifying the
      reasons why the IP address received the associated risk. This will be
      an empty tuple if there are no reasons.

      :type: tuple[IPRiskReason]

    .. attribute:: city

      City object for the requested IP address.

      :type: :py:class:`geoip2.records.City`

    .. attribute:: continent

      Continent object for the requested IP address.

      :type: :py:class:`geoip2.records.Continent`

    .. attribute:: country

      Country object for the requested IP address. This record represents the
      country where MaxMind believes the IP is located.

      :type: :py:class:`GeoIP2Country`

    .. attribute:: location

      Location object for the requested IP address.

      :type: :py:class:`GeoIP2Location`

    .. attribute:: maxmind

      Information related to your MaxMind account.

      :type: :py:class:`geoip2.records.MaxMind`

    .. attribute:: registered_country

      The registered country object for the requested IP address. This record
      represents the country where the ISP has registered a given IP block in
      and may differ from the user's country.

      :type: :py:class:`geoip2.records.Country`

    .. attribute:: represented_country

      Object for the country represented by the users of the IP address
      when that country is different than the country in ``country``. For
      instance, the country represented by an overseas military base.

      :type: :py:class:`geoip2.records.RepresentedCountry`

    .. attribute:: subdivisions

      Object (tuple) representing the subdivisions of the country to which
      the location of the requested IP address belongs.

      :type: :py:class:`geoip2.records.Subdivisions`

    .. attribute:: traits

      Object with the traits of the requested IP address.

    """

    country: GeoIP2Country
    location: GeoIP2Location
    risk: Optional[float]
    risk_reasons: List[IPRiskReason]

    def __init__(
        self,
        locales: Sequence[str],
        *,
        country: Optional[Dict] = None,
        location: Optional[Dict] = None,
        risk: Optional[float] = None,
        risk_reasons: Optional[List[Dict]] = None,
        **kwargs,
    ) -> None:

        super().__init__(kwargs, locales=list(locales))
        self.country = GeoIP2Country(locales, **(country or {}))
        self.location = GeoIP2Location(**(location or {}))
        self.risk = risk
        self.risk_reasons = [IPRiskReason(**x) for x in risk_reasons or []]


class ScoreIPAddress(SimpleEquality):
    """Information about the IP address for minFraud Score.

    .. attribute:: risk

      This field contains the risk associated with the IP address. The value
      ranges from 0.01 to 99. A higher score indicates a higher risk.

      :type: float | None
    """

    risk: Optional[float]

    def __init__(self, *, risk: Optional[float] = None, **_):
        self.risk = risk


class Issuer(SimpleEquality):
    """Information about the credit card issuer.

    .. attribute:: name

      The name of the bank which issued the credit card.

      :type: str | None

    .. attribute:: matches_provided_name

      This property is ``True`` if the name matches
      the name provided in the request for the card issuer. It is ``False`` if
      the name does not match. The property is ``None`` if either no name or
      no issuer ID number (IIN) was provided in the request or if MaxMind does
      not have a name associated with the IIN.

      :type: bool | None

    .. attribute:: phone_number

      The phone number of the bank which issued the credit
      card. In some cases the phone number we return may be out of date.

      :type: str | None

    .. attribute:: matches_provided_phone_number

      This property is ``True`` if the phone
      number matches the number provided in the request for the card issuer. It
      is ``False`` if the number does not match. It is ``None`` if either no
      phone number or no issuer ID number (IIN) was provided in the request or
      if MaxMind does not have a phone number associated with the IIN.

      :type: bool | None

    """

    name: Optional[str]
    matches_provided_name: Optional[bool]
    phone_number: Optional[str]
    matches_provided_phone_number: Optional[bool]

    def __init__(
        self,
        *,
        name: Optional[str] = None,
        matches_provided_name: Optional[bool] = None,
        phone_number: Optional[str] = None,
        matches_provided_phone_number: Optional[bool] = None,
        **_,
    ):
        self.name = name
        self.matches_provided_name = matches_provided_name
        self.phone_number = phone_number
        self.matches_provided_phone_number = matches_provided_phone_number


class Device(SimpleEquality):
    """Information about the device associated with the IP address.

    In order to receive device output from minFraud Insights or minFraud
    Factors, you must be using the `Device Tracking Add-on
    <https://dev.maxmind.com/minfraud/track-devices?lang=en>`_.

    .. attribute:: confidence

      This number represents our confidence that the ``device_id`` refers to
      a unique device as opposed to a cluster of similar devices. A confidence
      of 0.01 indicates very low confidence that the device is unique, whereas
      99 indicates very high confidence.

      :type: float | None

    .. attribute:: id

      A UUID that MaxMind uses for the device associated with this IP address.

      :type: str | None

    .. attribute:: last_seen

      This is the date and time of the last sighting of the device. This is an
      RFC 3339 date-time.

      :type: str | None

    .. attribute:: local_time

      This is the local date and time of the transaction in the time zone of
      the device. This is determined by using the UTC offset associated with
      the device. This is an RFC 3339 date-time.

      :type: str | None

    """

    confidence: Optional[float]
    id: Optional[str]
    last_seen: Optional[str]
    local_time: Optional[str]

    def __init__(
        self,
        *,
        confidence: Optional[float] = None,
        # pylint:disable=redefined-builtin
        id: Optional[str] = None,
        last_seen: Optional[str] = None,
        local_time: Optional[str] = None,
        **_,
    ):
        self.confidence = confidence
        self.id = id
        self.last_seen = last_seen
        self.local_time = local_time


class Disposition(SimpleEquality):
    """Information about disposition for the request as set by custom rules.

    In order to receive a disposition, you must be use the minFraud custom
    rules.

    .. attribute:: action

      The action to take on the transaction as defined by your custom rules.
      The current set of values are "accept", "manual_review", "reject", and
      "test". If you do not have custom rules set up, ``None`` will be
      returned.

      :type: str | None

    .. attribute:: reason

      The reason for the action. The current possible values are "custom_rule"
      and "default". If you do not have custom rules set up, ``None`` will be
      returned.

      :type: str | None

    .. attribute:: rule_label

      The label of the custom rule that was triggered. If you do not have
      custom rules set up, the triggered custom rule does not have a label, or
      no custom rule was triggered, ``None`` will be returned.

      :type: str | None
    """

    action: Optional[str]
    reason: Optional[str]
    rule_label: Optional[str]

    def __init__(
        self,
        *,
        action: Optional[str] = None,
        reason: Optional[str] = None,
        rule_label: Optional[str] = None,
        **_,
    ):
        self.action = action
        self.reason = reason
        self.rule_label = rule_label


class EmailDomain(SimpleEquality):
    """Information about the email domain passed in the request.

    .. attribute:: first_seen

      A date string (e.g. 2017-04-24) to identify the date an email domain
      was first seen by MaxMind. This is expressed using the ISO 8601 date
      format.

      :type: str | None

    """

    first_seen: Optional[str]

    def __init__(self, *, first_seen: Optional[str] = None, **_):
        self.first_seen = first_seen


class Email(SimpleEquality):
    """Information about the email address passed in the request.

    .. attribute:: domain

      An object containing information about the email domain.

      :type: EmailDomain

    .. attribute:: first_seen

      A date string (e.g. 2017-04-24) to identify the date an email address
      was first seen by MaxMind. This is expressed using the ISO 8601 date
      format.

      :type: str | None

    .. attribute:: is_disposable

      This field indicates whether the email is from a disposable email
      provider. It will be ``None`` when an email address was not passed in
      the inputs.

      :type: bool | None

    .. attribute:: is_free

      This field is true if MaxMind believes that this email is hosted by a
      free email provider such as Gmail or Yahoo! Mail.

      :type: bool | None

    .. attribute:: is_high_risk

      This field is true if MaxMind believes that this email is likely to be
      used for fraud. Note that this is also factored into the overall
      `risk_score` in the response as well.

      :type: bool | None

    """

    domain: EmailDomain
    first_seen: Optional[str]
    is_disposable: Optional[bool]
    is_free: Optional[bool]
    is_high_risk: Optional[bool]

    def __init__(
        self,
        domain: Optional[Dict] = None,
        first_seen: Optional[str] = None,
        is_disposable: Optional[bool] = None,
        is_free: Optional[bool] = None,
        is_high_risk: Optional[bool] = None,
    ):
        self.domain = EmailDomain(**(domain or {}))
        self.first_seen = first_seen
        self.is_disposable = is_disposable
        self.is_free = is_free
        self.is_high_risk = is_high_risk


class CreditCard(SimpleEquality):
    """Information about the credit card based on the issuer ID number.

    .. attribute:: country

      This property contains the `ISO 3166-1 alpha-2 country code
      <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_ associated with the
      location of the majority of customers using this credit card as
      determined by their billing address. In cases where the location of
      customers is highly mixed, this defaults to the country of the bank
      issuing the card.

      :type: str | None

    .. attribute:: brand

      The card brand, such as "Visa", "Discover", "American Express", etc.

      :type: str | None

    .. attribute:: is_business

      This property is ``True`` if the card is a business card.

      :type: bool | None

    .. attribute:: is_issued_in_billing_address_country

      This property is true if the country of the billing address matches the
      country of the majority of customers using this credit card. In cases
      where the location of customers is highly mixed, the match is to the
      country of the bank issuing the card.

      :type: bool | None

    .. attribute:: is_prepaid

      This property is ``True`` if the card is a prepaid card.

      :type: bool | None

    .. attribute:: is_virtual

      This property is ``True`` if the card is a virtual card.

      :type: bool | None

    .. attribute:: type

      The card's type. The valid values are "charge", "credit", and "debit".
      See Wikipedia for an explanation of the difference between charge and
      credit cards.

      :type: str | None

    .. attribute:: issuer

      An object containing information about the credit card issuer.

      :type: Issuer

    """

    issuer: Issuer
    country: Optional[str]
    brand: Optional[str]
    is_business: Optional[bool]
    is_issued_in_billing_address_country: Optional[bool]
    is_prepaid: Optional[bool]
    is_virtual: Optional[bool]
    type: Optional[str]

    def __init__(
        self,
        issuer: Optional[Dict] = None,
        country: Optional[str] = None,
        brand: Optional[str] = None,
        is_business: Optional[bool] = None,
        is_issued_in_billing_address_country: Optional[bool] = None,
        is_prepaid: Optional[bool] = None,
        is_virtual: Optional[bool] = None,
        # pylint:disable=redefined-builtin
        type: Optional[str] = None,
    ):
        self.issuer = Issuer(**(issuer or {}))
        self.country = country
        self.brand = brand
        self.is_business = is_business
        self.is_issued_in_billing_address_country = is_issued_in_billing_address_country
        self.is_prepaid = is_prepaid
        self.is_virtual = is_virtual
        self.type = type


class BillingAddress(SimpleEquality):
    """Information about the billing address.

    .. attribute:: distance_to_ip_location

      The distance in kilometers from the
      address to the IP location.

      :type: int | None

    .. attribute:: is_in_ip_country

      This property is ``True`` if the address is in the
      IP country. The property is ``False`` when the address is not in the IP
      country. If the address could not be parsed or was not provided or if the
      IP address could not be geolocated, the property will be ``None``.

      :type: bool | None

    .. attribute:: is_postal_in_city

      This property is ``True`` if the postal code
      provided with the address is in the city for the address. The property is
      ``False`` when the postal code is not in the city. If the address was
      not provided, could not be parsed, or was outside USA, the property will
      be ``None``.

      :type: bool | None

    .. attribute:: latitude

      The latitude associated with the address.

      :type: float | None

    .. attribute:: longitude

      The longitude associated with the address.

      :type: float | None

    """

    is_postal_in_city: Optional[bool]
    latitude: Optional[float]
    longitude: Optional[float]
    distance_to_ip_location: Optional[int]
    is_in_ip_country: Optional[bool]

    def __init__(
        self,
        *,
        is_postal_in_city: Optional[bool] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        distance_to_ip_location: Optional[int] = None,
        is_in_ip_country: Optional[bool] = None,
        **_,
    ):
        self.is_postal_in_city = is_postal_in_city
        self.latitude = latitude
        self.longitude = longitude
        self.distance_to_ip_location = distance_to_ip_location
        self.is_in_ip_country = is_in_ip_country


class ShippingAddress(SimpleEquality):
    """Information about the shipping address.

    .. attribute:: distance_to_ip_location

      The distance in kilometers from the
      address to the IP location.

      :type: int | None

    .. attribute:: is_in_ip_country

      This property is ``True`` if the address is in the
      IP country. The property is ``False`` when the address is not in the IP
      country. If the address could not be parsed or was not provided or if the
      IP address could not be geolocated, the property will be ``None``.

      :type: bool | None

    .. attribute:: is_postal_in_city

      This property is ``True`` if the postal code
      provided with the address is in the city for the address. The property is
      ``False`` when the postal code is not in the city. If the address was
      not provided, could not be parsed, or was not in USA, the property will
      be ``None``.

      :type: bool | None

    .. attribute:: latitude

      The latitude associated with the address.

      :type: float | None

    .. attribute:: longitude

      The longitude associated with the address.

      :type: float | None

    .. attribute:: is_high_risk

      This property is ``True`` if the shipping address is in
      the IP country. The property is ``false`` when the address is not in the
      IP country. If the shipping address could not be parsed or was not
      provided or the IP address could not be geolocated, then the property is
      ``None``.

      :type: bool | None

    .. attribute:: distance_to_billing_address

      The distance in kilometers from the
      shipping address to billing address.

      :type: int | None

    """

    is_postal_in_city: Optional[bool]
    latitude: Optional[float]
    longitude: Optional[float]
    distance_to_ip_location: Optional[int]
    is_in_ip_country: Optional[bool]
    is_high_risk: Optional[bool]
    distance_to_billing_address: Optional[int]

    def __init__(
        self,
        *,
        is_postal_in_city: Optional[bool] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        distance_to_ip_location: Optional[int] = None,
        is_in_ip_country: Optional[bool] = None,
        is_high_risk: Optional[bool] = None,
        distance_to_billing_address: Optional[int] = None,
        **_,
    ):
        self.is_postal_in_city = is_postal_in_city
        self.latitude = latitude
        self.longitude = longitude
        self.distance_to_ip_location = distance_to_ip_location
        self.is_in_ip_country = is_in_ip_country
        self.is_high_risk = is_high_risk
        self.distance_to_billing_address = distance_to_billing_address


class Phone(SimpleEquality):
    """Information about the billing or shipping phone number.

    .. attribute:: country

      The two-character ISO 3166-1 country code for the country associated with
      the phone number.

      :type: str | None

    .. attribute:: is_voip

      This property is ``True`` if the phone number is a Voice over Internet
      Protocol (VoIP) number allocated by a regulator. The property is
      ``False`` when the number is not VoIP. If the phone number was not
      provided or we do not have data for it, the property will be ``None``.

      :type: bool | None

    .. attribute:: network_operator

      The name of the original network operator associated with the phone
      number. This field does not reflect phone numbers that have been ported
      from the original operator to another, nor does it identify mobile
      virtual network operators.

      :type: str | None

    .. attribute:: number_type

      One of the following values: fixed or mobile. Additional values may be
      added in the future.

      :type: str | None

    """

    country: Optional[str]
    is_voip: Optional[bool]
    network_operator: Optional[str]
    number_type: Optional[str]

    def __init__(
        self,
        *,
        country: Optional[str] = None,
        is_voip: Optional[bool] = None,
        network_operator: Optional[str] = None,
        number_type: Optional[str] = None,
        **_,
    ):
        self.country = country
        self.is_voip = is_voip
        self.network_operator = network_operator
        self.number_type = number_type


class ServiceWarning(SimpleEquality):
    """Warning from the web service.

    .. attribute:: code

      This value is a machine-readable code identifying the
      warning. See the `web service documentation
      <https://dev.maxmind.com/minfraud/api-documentation/responses?lang=en#schema--response--warning>`_
      for the current list of of warning codes.

      :type: str | None

    .. attribute:: warning

      This property provides a human-readable explanation of the
      warning. The description may change at any time and should not be matched
      against.

      :type: str | None

    .. attribute:: input_pointer

      This is a string representing the path to the input that
      the warning is associated with. For instance, if the warning was about
      the billing city, the string would be ``"/billing/city"``.

      :type: str | None

    """

    code: Optional[str]
    warning: Optional[str]
    input_pointer: Optional[str]

    def __init__(
        self,
        *,
        code: Optional[str] = None,
        warning: Optional[str] = None,
        input_pointer: Optional[str] = None,
        **_,
    ):
        self.code = code
        self.warning = warning
        self.input_pointer = input_pointer


class Subscores(SimpleEquality):
    """Risk factor scores used in calculating the overall risk score.

    .. deprecated:: 2.12.0
      Use RiskScoreReason instead.

    .. attribute:: avs_result

      The risk associated with the AVS result. If present, this is a value
      in the range 0.01 to 99.

      :type: float | None

    .. attribute:: billing_address

      The risk associated with the billing address. If present, this is a
      value in the range 0.01 to 99.

      :type: float | None

    .. attribute:: billing_address_distance_to_ip_location

      The risk associated with the distance between the billing address and
      the location for the given IP address. If present, this is a value in
      the range 0.01 to 99.

      :type: float | None

    .. attribute:: browser

      The risk associated with the browser attributes such as the User-Agent
      and Accept-Language. If present, this is a value in the range 0.01 to
      99.

      :type: float | None

    .. attribute:: chargeback

      Individualized risk of chargeback for the given IP address given for
      your account and any shop ID passed. This is only available to users
      sending chargeback data to MaxMind. If present, this is a value in the
      range 0.01 to 99.

      :type: float | None

    .. attribute:: country

      The risk associated with the country the transaction originated from. If
      present, this is a value in the  range 0.01 to 99.

      :type: float | None

    .. attribute:: country_mismatch

      The risk associated with the combination of IP country, card issuer
      country, billing country, and shipping country. If present, this is a
      value in the range 0.01 to 99.

      :type: float | None

    .. attribute:: cvv_result

      The risk associated with the CVV result. If present, this is a value
      in the range 0.01 to 99.

      :type: float | None

    .. attribute:: device

      The risk associated with the device. If present, this is a value in the
      range 0.01 to 99.

      :type: float | None

    .. attribute:: email_address

      The risk associated with the particular email address. If present, this
      is a value in the range 0.01 to 99.

      :type: float | None

    .. attribute:: email_domain

      The general risk associated with the email domain. If present, this is a
      value in the range 0.01 to 99.

      :type: float | None

    .. attribute:: email_local_part

      The risk associated with the email address local part (the part of the
      email address before the @ symbol). If present, this is a value in the
      range 0.01 to 99.

      :type: float | None

     .. attribute:: email_tenure

      The risk associated with the issuer ID number on the email domain. If
      present, this is a value in the range 0.01 to 99.

      :type: float | None

      .. deprecated:: 1.8.0
        Deprecated effective August 29, 2019. This risk factor score will
        default to 1 and will be removed in a future release. The user
        tenure on email is reflected in the email address risk factor score.

      .. seealso::
        :py:attr:`minfraud.models.Subscores.email_address`

    .. attribute:: ip_tenure

      The risk associated with the issuer ID number on the IP address. If
      present, this is a value in the range 0.01 to 99.

      :type: float | None

      .. deprecated:: 1.8.0
        Deprecated effective August 29, 2019. This risk factor score will
        default to 1 and will be removed in a future release. The IP tenure
        is reflected in the overall risk score.

      .. seealso::
        :py:attr:`minfraud.models.Score.risk_score`

    .. attribute:: issuer_id_number

      The risk associated with the particular issuer ID number (IIN) given the
      billing location and the history of usage of the IIN on your account and
      shop ID. If present, this is a value in the range 0.01 to 99.

      :type: float | None

    .. attribute:: order_amount

      The risk associated with the particular order amount for your account
      and shop ID. If present, this is a value in the range 0.01 to 99.

      :type: float | None

    .. attribute:: phone_number

      The risk associated with the particular phone number. If present, this
      is a value in the range 0.01 to 99.

      :type: float | None

    .. attribute:: shipping_address

      The risk associated with the shipping address. If present, this is a
      value in the range 0.01 to 99.

      :type: float | None

    .. attribute:: shipping_address_distance_to_ip_location

      The risk associated with the distance between the shipping address and
      the location for the given IP address. If present, this is a value in
      the range 0.01 to 99.

      :type: float | None

    .. attribute:: time_of_day

      The risk associated with the local time of day of the transaction in the
      IP address location. If present, this is a value in the range 0.01 to 99.

      :type: float | None

    """

    avs_result: Optional[float]
    billing_address: Optional[float]
    billing_address_distance_to_ip_location: Optional[float]
    browser: Optional[float]
    chargeback: Optional[float]
    country: Optional[float]
    country_mismatch: Optional[float]
    cvv_result: Optional[float]
    device: Optional[float]
    email_address: Optional[float]
    email_domain: Optional[float]
    email_local_part: Optional[float]
    email_tenure: Optional[float]
    ip_tenure: Optional[float]
    issuer_id_number: Optional[float]
    order_amount: Optional[float]
    phone_number: Optional[float]
    shipping_address: Optional[float]
    shipping_address_distance_to_ip_location: Optional[float]
    time_of_day: Optional[float]

    def __init__(
        self,
        *,
        avs_result: Optional[float] = None,
        billing_address: Optional[float] = None,
        billing_address_distance_to_ip_location: Optional[float] = None,
        browser: Optional[float] = None,
        chargeback: Optional[float] = None,
        country: Optional[float] = None,
        country_mismatch: Optional[float] = None,
        cvv_result: Optional[float] = None,
        device: Optional[float] = None,
        email_address: Optional[float] = None,
        email_domain: Optional[float] = None,
        email_local_part: Optional[float] = None,
        email_tenure: Optional[float] = None,
        ip_tenure: Optional[float] = None,
        issuer_id_number: Optional[float] = None,
        order_amount: Optional[float] = None,
        phone_number: Optional[float] = None,
        shipping_address: Optional[float] = None,
        shipping_address_distance_to_ip_location: Optional[float] = None,
        time_of_day: Optional[float] = None,
        **_,
    ):
        self.avs_result = avs_result
        self.billing_address = billing_address
        self.billing_address_distance_to_ip_location = (
            billing_address_distance_to_ip_location
        )
        self.browser = browser
        self.chargeback = chargeback
        self.country = country
        self.country_mismatch = country_mismatch
        self.cvv_result = cvv_result
        self.device = device
        self.email_address = email_address
        self.email_domain = email_domain
        self.email_local_part = email_local_part
        self.email_tenure = email_tenure
        self.ip_tenure = ip_tenure
        self.issuer_id_number = issuer_id_number
        self.order_amount = order_amount
        self.phone_number = phone_number
        self.shipping_address = shipping_address
        self.shipping_address_distance_to_ip_location = (
            shipping_address_distance_to_ip_location
        )
        self.time_of_day = time_of_day


class Reason(SimpleEquality):
    """The risk score reason for the multiplier.

    This class provides both a machine-readable code and a human-readable
    explanation of the reason for the risk score.

    Although more codes_ may be added in the future, the current codes are:

    - ``BROWSER_LANGUAGE`` - Riskiness of the browser user-agent and
      language associated with the request.
    - ``BUSINESS_ACTIVITY`` - Riskiness of business activity
        associated with the request.
    - ``COUNTRY`` - Riskiness of the country associated with the request.
    - ``CUSTOMER_ID`` - Riskiness of a customer's activity.
    - ``EMAIL_DOMAIN`` - Riskiness of email domain.
    - ``EMAIL_DOMAIN_NEW`` - Riskiness of newly-sighted email domain.
    - ``EMAIL_ADDRESS_NEW`` - Riskiness of newly-sighted email address.
    - ``EMAIL_LOCAL_PART`` - Riskiness of the local part of the email address.
    - ``EMAIL_VELOCITY`` - Velocity on email - many requests on same email
      over short period of time.
    - ``ISSUER_ID_NUMBER_COUNTRY_MISMATCH`` - Riskiness of the country mismatch
      between IP, billing, shipping and IIN country.
    - ``ISSUER_ID_NUMBER_ON_SHOP_ID`` - Risk of Issuer ID Number for the shop ID.
    - ``ISSUER_ID_NUMBER_LAST_DIGITS_ACTIVITY`` - Riskiness of many recent requests
      and previous high-risk requests on the IIN and last digits of the credit card.
    - ``ISSUER_ID_NUMBER_SHOP_ID_VELOCITY`` - Risk of recent Issuer ID Number activity
      for the shop ID.
    - ``INTRACOUNTRY_DISTANCE`` - Risk of distance between IP, billing,
      and shipping location.
    - ``ANONYMOUS_IP`` - Risk due to IP being an Anonymous IP.
    - ``IP_BILLING_POSTAL_VELOCITY`` - Velocity of distinct billing postal code
      on IP address.
    - ``IP_EMAIL_VELOCITY`` - Velocity of distinct email address on IP address.
    - ``IP_HIGH_RISK_DEVICE`` - High-risk device sighted on IP address.
    - ``IP_ISSUER_ID_NUMBER_VELOCITY`` - Velocity of distinct IIN on IP address.
    - ``IP_ACTIVITY`` - Riskiness of IP based on minFraud network activity.
    - ``LANGUAGE`` - Riskiness of browser language.
    - ``MAX_RECENT_EMAIL`` - Riskiness of email address
      based on past minFraud risk scores on email.
    - ``MAX_RECENT_PHONE`` - Riskiness of phone number
      based on past minFraud risk scores on phone.
    - ``MAX_RECENT_SHIP`` - Riskiness of email address
      based on past minFraud risk scores on ship address.
    - ``MULTIPLE_CUSTOMER_ID_ON_EMAIL`` - Riskiness of email address
      having many customer IDs.
    - ``ORDER_AMOUNT`` - Riskiness of the order amount.
    - ``ORG_DISTANCE_RISK`` - Risk of ISP and distance between
      billing address and IP location.
    - ``PHONE`` - Riskiness of the phone number or related numbers.
    - ``CART`` - Riskiness of shopping cart contents.
    - ``TIME_OF_DAY`` - Risk due to local time of day.
    - ``TRANSACTION_REPORT_EMAIL`` - Risk due to transaction reports
      on the email address.
    - ``TRANSACTION_REPORT_IP`` - Risk due to transaction reports on the IP address.
    - ``TRANSACTION_REPORT_PHONE`` - Risk due to transaction reports
        on the phone number.
    - ``TRANSACTION_REPORT_SHIP`` - Risk due to transaction reports
        on the shipping address.
    - ``EMAIL_ACTIVITY`` - Riskiness of the email address
      based on minFraud network activity.
    - ``PHONE_ACTIVITY`` - Riskiness of the phone number
        based on minFraud network activity.
    - ``SHIP_ACTIVITY`` - Riskiness of ship address based on minFraud network activity.

    .. _codes: https://dev.maxmind.com/minfraud/api-documentation/responses\
    /#schema--response--risk-score-reason--multiplier-reason

    .. attribute:: code

      This value is a machine-readable code identifying the
      reason.

      :type: str | None

    .. attribute:: reason

      This property provides a human-readable explanation of the
      reason. The text may change at any time and should not be matched
      against.

      :type: str | None
    """

    code: Optional[str]
    reason: Optional[str]

    def __init__(
        self, *, code: Optional[str] = None, reason: Optional[str] = None, **_
    ):
        self.code = code
        self.reason = reason


class RiskScoreReason(SimpleEquality):
    """The risk score multiplier and the reasons for that multiplier.

    .. attribute:: multiplier

      The factor by which the risk score is increased (if the value is greater than 1)
      or decreased (if the value is less than 1) for given risk reason(s).
      Multipliers greater than 1.5 and less than 0.66 are considered significant
      and lead to risk reason(s) being present.

      :type: float | None

    .. attribute:: reasons

      This tuple contains :class:`.Reason` objects that describe
      one of the reasons for the multiplier.

      :type: tuple[Reason]

    """

    multiplier: float
    reasons: List[Reason]

    def __init__(
        self,
        *,
        multiplier: float,
        reasons: Optional[List] = None,
        **_,
    ):
        self.multiplier = multiplier
        self.reasons = [Reason(**x) for x in reasons or []]


class Factors(SimpleEquality):
    """Model for Factors response.

    .. attribute:: id

      This is a UUID that identifies the minFraud request. Please use
      this ID in bug reports or support requests to MaxMind so that we can
      easily identify a particular request.

      :type: str

    .. attribute:: funds_remaining

      The approximate US dollar value of the funds remaining on your MaxMind
      account.

      :type: float

    .. attribute:: queries_remaining

      The approximate number of queries remaining on this service before
      your account runs out of funds.

      :type: int

    .. attribute:: warnings

      This tuple contains :class:`.ServiceWarning` objects detailing
      issues with the request that was sent such as invalid or unknown inputs.
      It is highly recommended that you check this array for issues when
      integrating the web service.

      :type: tuple[ServiceWarning]

    .. attribute:: risk_score

      This property contains the risk score, from 0.01 to 99. A
      higher score indicates a higher risk of fraud. For example, a score of
      20 indicates a 20% chance that a transaction is fraudulent. We never
      return a risk score of 0, since all transactions have the possibility of
      being fraudulent. Likewise we never return a risk score of 100.

      :type: float

    .. attribute:: credit_card

      A :class:`.CreditCard` object containing minFraud data
      about the credit card used in the transaction.

      :type: CreditCard

    .. attribute:: device

      A :class:`.Device` object containing information about the device that
      MaxMind believes is associated with the IP address passed in the request.

      :type: Device

    .. attribute:: disposition

      A :class:`.Disposition` object containing the disposition for the
      request as set by custom rules.

      :type: Disposition

    .. attribute:: email

      A :class:`.Email` object containing information about the email address
      passed in the request.

      :type: Email

    .. attribute:: ip_address

      A :class:`.IPAddress` object containing GeoIP2 and
      minFraud Insights information about the IP address.

      :type: IPAddress

    .. attribute:: billing_address

      A :class:`.BillingAddress` object containing minFraud
      data related to the billing address used in the transaction.

      :type: BillingAddress

    .. attribute:: billing_phone

      A :class:`.Phone` object containing minFraud data related to the billing
      phone used in the transaction.

      :type: Phone

    .. attribute:: shipping_address

      A :class:`.ShippingAddress` object containing
      minFraud data related to the shipping address used in the transaction.

      :type: ShippingAddress

    .. attribute:: shipping_phone

      A :class:`.Phone` object containing minFraud data related to the shipping
      phone used in the transaction.

      :type: Phone

    .. attribute:: subscores

      A :class:`.Subscores` object containing scores for many of the
      individual risk factors that are used to calculate the overall risk
      score.

      .. deprecated:: 2.12.0
        Use RiskScoreReason instead.

    .. attribute:: risk_score_reasons

      This tuple contains :class:`.RiskScoreReason` objects that describe
      risk score reasons for a given transaction that change the risk score
      significantly. Risk score reasons are usually only returned for medium to
      high risk transactions. If there were no significant changes to the risk
      score due to these reasons, then this tuple will be empty.

      :type: tuple[RiskScoreReason]

    """

    billing_address: BillingAddress
    billing_phone: Phone
    credit_card: CreditCard
    disposition: Disposition
    funds_remaining: float
    device: Device
    email: Email
    id: str
    ip_address: IPAddress
    queries_remaining: int
    risk_score: float
    shipping_address: ShippingAddress
    shipping_phone: Phone
    subscores: Subscores
    warnings: List[ServiceWarning]
    risk_score_reasons: List[RiskScoreReason]

    def __init__(
        self,
        locales: Sequence[str],
        *,
        billing_address: Optional[Dict] = None,
        billing_phone: Optional[Dict] = None,
        credit_card: Optional[Dict] = None,
        disposition: Optional[Dict] = None,
        funds_remaining: float,
        device: Optional[Dict] = None,
        email: Optional[Dict] = None,
        # pylint:disable=redefined-builtin
        id: str,
        ip_address: Optional[Dict] = None,
        queries_remaining: int,
        risk_score: float,
        shipping_address: Optional[Dict] = None,
        shipping_phone: Optional[Dict] = None,
        subscores: Optional[Dict] = None,
        warnings: Optional[List[Dict]] = None,
        risk_score_reasons: Optional[List[Dict]] = None,
        **_,
    ):
        self.billing_address = BillingAddress(**(billing_address or {}))
        self.billing_phone = Phone(**(billing_phone or {}))
        self.credit_card = CreditCard(**(credit_card or {}))
        self.disposition = Disposition(**(disposition or {}))
        self.funds_remaining = funds_remaining
        self.device = Device(**(device or {}))
        self.email = Email(**(email or {}))
        self.id = id
        self.ip_address = IPAddress(locales, **(ip_address or {}))
        self.queries_remaining = queries_remaining
        self.risk_score = risk_score
        self.shipping_address = ShippingAddress(**(shipping_address or {}))
        self.shipping_phone = Phone(**(shipping_phone or {}))
        self.subscores = Subscores(**(subscores or {}))
        self.warnings = [ServiceWarning(**x) for x in warnings or []]
        self.risk_score_reasons = [
            RiskScoreReason(**x) for x in risk_score_reasons or []
        ]


class Insights(SimpleEquality):
    """Model for Insights response.

    .. attribute:: id

      This is a UUID that identifies the minFraud request. Please use
      this ID in bug reports or support requests to MaxMind so that we can
      easily identify a particular request.

      :type: str

    .. attribute:: funds_remaining

      The approximate US dollar value of the funds remaining on your MaxMind
      account.

      :type: float

    .. attribute:: queries_remaining

      The approximate number of queries remaining on this service before
      your account runs out of funds.

      :type: int

    .. attribute:: warnings

      This tuple contains :class:`.ServiceWarning` objects detailing
      issues with the request that was sent such as invalid or unknown inputs.
      It is highly recommended that you check this array for issues when
      integrating the web service.

      :type: tuple[ServiceWarning]

    .. attribute:: risk_score

      This property contains the risk score, from 0.01 to 99. A
      higher score indicates a higher risk of fraud. For example, a score of
      20 indicates a 20% chance that a transaction is fraudulent. We never
      return a risk score of 0, since all transactions have the possibility of
      being fraudulent. Likewise we never return a risk score of 100.

      :type: float

    .. attribute:: credit_card

      A :class:`.CreditCard` object containing minFraud data
      about the credit card used in the transaction.

      :type: CreditCard

    .. attribute:: device

      A :class:`.Device` object containing information about the device that
      MaxMind believes is associated with the IP address passed in the request.

      :type: Device

    .. attribute:: disposition

      A :class:`.Disposition` object containing the disposition for the
      request as set by custom rules.

      :type: Disposition

    .. attribute:: email

      A :class:`.Email` object containing information about the email address
      passed in the request.

      :type: Email

    .. attribute:: ip_address

      A :class:`.IPAddress` object containing GeoIP2 and
      minFraud Insights information about the IP address.

      :type: IPAddress

    .. attribute:: billing_address

      A :class:`.BillingAddress` object containing minFraud
      data related to the billing address used in the transaction.

      :type: BillingAddress

    .. attribute:: billing_phone

      A :class:`.Phone` object containing minFraud data related to the billing
      phone used in the transaction.

      :type: Phone

    .. attribute:: shipping_address

      A :class:`.ShippingAddress` object containing
      minFraud data related to the shipping address used in the transaction.

      :type: ShippingAddress

    .. attribute:: shipping_phone

      A :class:`.Phone` object containing minFraud data related to the shipping
      phone used in the transaction.

      :type: Phone
    """

    billing_address: BillingAddress
    billing_phone: Phone
    credit_card: CreditCard
    device: Device
    disposition: Disposition
    email: Email
    funds_remaining: float
    id: str
    ip_address: IPAddress
    queries_remaining: int
    risk_score: float
    shipping_address: ShippingAddress
    shipping_phone: Phone
    warnings: List[ServiceWarning]

    def __init__(
        self,
        locales: Sequence[str],
        *,
        billing_address: Optional[Dict] = None,
        billing_phone: Optional[Dict] = None,
        credit_card: Optional[Dict] = None,
        device: Optional[Dict] = None,
        disposition: Optional[Dict] = None,
        email: Optional[Dict] = None,
        funds_remaining: float,
        # pylint:disable=redefined-builtin
        id: str,
        ip_address: Optional[Dict] = None,
        queries_remaining: int,
        risk_score: float,
        shipping_address: Optional[Dict] = None,
        shipping_phone: Optional[Dict] = None,
        warnings: Optional[List[Dict]] = None,
        **_,
    ):
        self.billing_address = BillingAddress(**(billing_address or {}))
        self.billing_phone = Phone(**(billing_phone or {}))
        self.credit_card = CreditCard(**(credit_card or {}))
        self.device = Device(**(device or {}))
        self.disposition = Disposition(**(disposition or {}))
        self.email = Email(**(email or {}))
        self.funds_remaining = funds_remaining
        self.id = id
        self.ip_address = IPAddress(locales, **(ip_address or {}))
        self.queries_remaining = queries_remaining
        self.risk_score = risk_score
        self.shipping_address = ShippingAddress(**(shipping_address or {}))
        self.shipping_phone = Phone(**(shipping_phone or {}))
        self.warnings = [ServiceWarning(**x) for x in warnings or []]


class Score(SimpleEquality):
    """Model for Score response.

    .. attribute:: id

      This is a UUID that identifies the minFraud request. Please use
      this ID in bug reports or support requests to MaxMind so that we can
      easily identify a particular request.

      :type: str

    .. attribute:: funds_remaining

      The approximate US dollar value of the funds remaining on your MaxMind
      account.

      :type: float

    .. attribute:: queries_remaining

      The approximate number of queries remaining on this service before
      your account runs out of funds.

      :type: int

    .. attribute:: warnings

      This tuple contains :class:`.ServiceWarning` objects detailing
      issues with the request that was sent such as invalid or unknown inputs.
      It is highly recommended that you check this array for issues when
      integrating the web service.

      :type: tuple[ServiceWarning]

    .. attribute:: risk_score

      This property contains the risk score, from 0.01 to 99. A
      higher score indicates a higher risk of fraud. For example, a score of
      20 indicates a 20% chance that a transaction is fraudulent. We never
      return a risk score of 0, since all transactions have the possibility of
      being fraudulent. Likewise we never return a risk score of 100.

      :type: float

    .. attribute:: disposition

      A :class:`.Disposition` object containing the disposition for the
      request as set by custom rules.

      :type: Disposition

    .. attribute:: ip_address

      A :class:`.ScoreIPAddress` object containing IP address risk.

      :type: IPAddress
    """

    disposition: Disposition
    funds_remaining: float
    id: str
    ip_address: ScoreIPAddress
    queries_remaining: int
    risk_score: float
    warnings: List[ServiceWarning]

    def __init__(
        self,
        *,
        disposition: Optional[Dict] = None,
        funds_remaining: float,
        # pylint:disable=redefined-builtin
        id: str,
        ip_address: Optional[Dict] = None,
        queries_remaining: int,
        risk_score: float,
        warnings: Optional[List[Dict]] = None,
        **_,
    ):
        self.disposition = Disposition(**(disposition or {}))
        self.funds_remaining = funds_remaining
        self.id = id
        self.ip_address = ScoreIPAddress(**(ip_address or {}))
        self.queries_remaining = queries_remaining
        self.risk_score = risk_score
        self.warnings = [ServiceWarning(**x) for x in warnings or []]
