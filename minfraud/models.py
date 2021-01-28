"""
minfraud.models
~~~~~~~~~~~~~~~

This module contains models for the minFraud response object.

"""
# pylint:disable=too-many-lines
from collections import namedtuple
from functools import update_wrapper
from typing import Any, Dict, List, Optional, Tuple

import geoip2.models
import geoip2.records


# Using a factory decorator rather than a metaclass as supporting
# metaclasses on Python 2 and 3 is more painful (although we could use
# six, I suppose). Using a closure rather than a class-based decorator as
# class based decorators don't work right with `update_wrapper`,
# causing help(class) to not work correctly.
def _inflate_to_namedtuple(orig_cls):
    keys = sorted(orig_cls._fields.keys())
    fields = orig_cls._fields
    name = orig_cls.__name__
    orig_cls.__name__ += "Super"
    ntup = namedtuple(name, keys)
    ntup.__name__ = name + "NamedTuple"
    ntup.__new__.__defaults__ = (None,) * len(keys)
    new_cls = type(
        name, (ntup, orig_cls), {"__slots__": (), "__doc__": orig_cls.__doc__}
    )
    update_wrapper(_inflate_to_namedtuple, new_cls)
    orig_new = new_cls.__new__

    # wipe out original namedtuple field docs as they aren't useful
    # for attr in fields:
    #     getattr(cls, attr).__func__.__doc__ = None

    def new(cls, *args, **kwargs):
        """Create new instance."""
        if (args and kwargs) or len(args) > 1:
            raise ValueError(
                "Only provide a single (dict) positional argument"
                " or use keyword arguments. Do not use both."
            )
        if args:
            values = args[0] if args[0] else {}

            for field, default in fields.items():
                if callable(default):
                    kwargs[field] = default(values.get(field))
                else:
                    kwargs[field] = values.get(field, default)

        return orig_new(cls, **kwargs)

    new_cls.__new__ = staticmethod(new)
    return new_cls


@_inflate_to_namedtuple
class IPRiskReason:
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

    __slots__ = ()
    _fields = {
        "code": None,
        "reason": None,
    }


def _create_ip_risk_reasons(
    reasons: Optional[List[Dict[str, str]]]
) -> Tuple[IPRiskReason, ...]:
    if not reasons:
        return ()
    return tuple([IPRiskReason(x) for x in reasons])  # type: ignore


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
    risk_reasons: Tuple[IPRiskReason, ...]

    def __init__(self, ip_address: Dict[str, Any]) -> None:
        if ip_address is None:
            ip_address = {}
        locales = ip_address.get("_locales")
        if "_locales" in ip_address:
            del ip_address["_locales"]
        super().__init__(ip_address, locales=locales)
        self.country = GeoIP2Country(locales, **ip_address.get("country", {}))
        self.location = GeoIP2Location(**ip_address.get("location", {}))
        self.risk = ip_address.get("risk", None)
        self.risk_reasons = _create_ip_risk_reasons(ip_address.get("risk_reasons"))
        self._finalized = True

    # Unfortunately the GeoIP2 models are not immutable, only the records. This
    # corrects that for minFraud
    def __setattr__(self, name: str, value: Any) -> None:
        if hasattr(self, "_finalized") and self._finalized:
            raise AttributeError("can't set attribute")
        super().__setattr__(name, value)


@_inflate_to_namedtuple
class ScoreIPAddress:
    """Information about the IP address for minFraud Score.

    .. attribute:: risk

      This field contains the risk associated with the IP address. The value
      ranges from 0.01 to 99. A higher score indicates a higher risk.

      :type: float | None
    """

    risk: Optional[float]

    __slots__ = ()
    _fields = {
        "risk": None,
    }


@_inflate_to_namedtuple
class Issuer:
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

    __slots__ = ()
    _fields = {
        "name": None,
        "matches_provided_name": None,
        "phone_number": None,
        "matches_provided_phone_number": None,
    }


@_inflate_to_namedtuple
class Device:
    """Information about the device associated with the IP address.

    In order to receive device output from minFraud Insights or minFraud
    Factors, you must be using the `Device Tracking Add-on
    <https://dev.maxmind.com/minfraud/device/>`_.

    .. attribute:: confidence

      This number represents our confidence that the ``device_id`` refers to
      a unique device as opposed to a cluster of similar devices. A confidence
      of 0.01 indicates very low confidence that the device is unique, whereas
      99 indicates very high confidence.

      :type: float | None

    .. attribute:: id

      A UUID that MaxMind uses for the device associated with this IP address.
      Note that many devices cannot be uniquely identified because they are too
      common (for example, all iPhones of a given model and OS release). In
      these cases, the minFraud service will simply not return a UUID for that
      device.

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

    __slots__ = ()
    _fields = {
        "confidence": None,
        "id": None,
        "last_seen": None,
        "local_time": None,
    }


@_inflate_to_namedtuple
class Disposition:
    """Information about disposition for the request as set by custom rules.

    In order to receive a disposition, you must be use the minFraud custom
    rules.

    .. attribute:: action

      The action to take on the transaction as defined by your custom rules.
      The current set of values are "accept", "manual_review", and "reject".
      If you do not have custom rules set up, ``None`` will be returned.

      :type: str | None

    .. attribute:: reason

      The reason for the action. The current possible values are
      "custom_rule", "block_list", and "default". If you do not have custom
      rules set up, ``None`` will be returned.

      :type: str | None
    """

    action: Optional[str]
    reason: Optional[str]

    __slots__ = ()
    _fields = {
        "action": None,
        "reason": None,
    }


@_inflate_to_namedtuple
class EmailDomain:
    """Information about the email domain passed in the request.

    .. attribute:: first_seen

      A date string (e.g. 2017-04-24) to identify the date an email domain
      was first seen by MaxMind. This is expressed using the ISO 8601 date
      format.

      :type: str | None

    """

    first_seen: Optional[str]

    __slots__ = ()
    _fields = {
        "first_seen": None,
    }


@_inflate_to_namedtuple
class Email:
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

    __slots__ = ()
    _fields = {
        "domain": EmailDomain,
        "first_seen": None,
        "is_disposable": None,
        "is_free": None,
        "is_high_risk": None,
    }


@_inflate_to_namedtuple
class CreditCard:
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

    __slots__ = ()
    _fields = {
        "issuer": Issuer,
        "country": None,
        "brand": None,
        "is_business": None,
        "is_issued_in_billing_address_country": None,
        "is_prepaid": None,
        "is_virtual": None,
        "type": None,
    }


@_inflate_to_namedtuple
class BillingAddress:
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

    __slots__ = ()
    _fields = {
        "is_postal_in_city": None,
        "latitude": None,
        "longitude": None,
        "distance_to_ip_location": None,
        "is_in_ip_country": None,
    }


@_inflate_to_namedtuple
class ShippingAddress:
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

    __slots__ = ()
    _fields = {
        "is_postal_in_city": None,
        "latitude": None,
        "longitude": None,
        "distance_to_ip_location": None,
        "is_in_ip_country": None,
        "is_high_risk": None,
        "distance_to_billing_address": None,
    }


@_inflate_to_namedtuple
class ServiceWarning:
    """Warning from the web service.

    .. attribute:: code

      This value is a machine-readable code identifying the
      warning. See the `web service documentation
      <https://dev.maxmind.com/minfraud/#Warning>`_
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

    __slots__ = ()
    _fields = {
        "code": None,
        "warning": None,
        "input_pointer": None,
    }


def _create_warnings(warnings: List[Dict[str, str]]) -> Tuple[ServiceWarning, ...]:
    if not warnings:
        return ()
    return tuple([ServiceWarning(x) for x in warnings])  # type: ignore


@_inflate_to_namedtuple
class Subscores:
    """Subscores used in calculating the overall risk score.

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
      country, billing country, and shipping country.  If present, this is a
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
        Deprecated effective August 29, 2019. This subscore will default to 1
        and will be removed in a future release. The user tenure on email is
        reflected in the email address subscore output.

      .. seealso::
        :py:attr:`minfraud.models.Subscores.email_address`

    .. attribute:: ip_tenure

      The risk associated with the issuer ID number on the IP address. If
      present, this is a value in the range 0.01 to 99.

      :type: float | None

      .. deprecated:: 1.8.0
        Deprecated effective August 29, 2019. This subscore will default to 1
        and will be removed in a future release. The IP tenure is reflected in
        the overall risk score.

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

    __slots__ = ()
    _fields = {
        "avs_result": None,
        "billing_address": None,
        "billing_address_distance_to_ip_location": None,
        "browser": None,
        "chargeback": None,
        "country": None,
        "country_mismatch": None,
        "cvv_result": None,
        "device": None,
        "email_address": None,
        "email_domain": None,
        "email_local_part": None,
        "email_tenure": None,
        "ip_tenure": None,
        "issuer_id_number": None,
        "order_amount": None,
        "phone_number": None,
        "shipping_address": None,
        "shipping_address_distance_to_ip_location": None,
        "time_of_day": None,
    }


@_inflate_to_namedtuple
class Factors:
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

    .. attribute:: shipping_address

      A :class:`.ShippingAddress` object containing
      minFraud data related to the shipping address used in the transaction.

    .. attribute:: subscores

      A :class:`.Subscores` object containing subscores for many of the
      individual components that are used to calculate the overall risk score.
    """

    billing_address: BillingAddress
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
    subscores: Subscores
    warnings: Tuple[ServiceWarning, ...]

    __slots__ = ()
    _fields = {
        "billing_address": BillingAddress,
        "credit_card": CreditCard,
        "disposition": Disposition,
        "funds_remaining": None,
        "device": Device,
        "email": Email,
        "id": None,
        "ip_address": IPAddress,
        "queries_remaining": None,
        "risk_score": None,
        "shipping_address": ShippingAddress,
        "subscores": Subscores,
        "warnings": _create_warnings,
    }


@_inflate_to_namedtuple
class Insights:
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

    .. attribute:: shipping_address

      A :class:`.ShippingAddress` object containing
      minFraud data related to the shipping address used in the transaction.
    """

    billing_address: BillingAddress
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
    warnings: Tuple[ServiceWarning, ...]

    __slots__ = ()
    _fields = {
        "billing_address": BillingAddress,
        "credit_card": CreditCard,
        "device": Device,
        "disposition": Disposition,
        "email": Email,
        "funds_remaining": None,
        "id": None,
        "ip_address": IPAddress,
        "queries_remaining": None,
        "risk_score": None,
        "shipping_address": ShippingAddress,
        "warnings": _create_warnings,
    }


@_inflate_to_namedtuple
class Score:
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
    warnings: Tuple[ServiceWarning, ...]

    __slots__ = ()
    _fields = {
        "disposition": Disposition,
        "funds_remaining": None,
        "id": None,
        "ip_address": ScoreIPAddress,
        "queries_remaining": None,
        "risk_score": None,
        "warnings": _create_warnings,
    }
