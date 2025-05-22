"""Models for the minFraud response object."""

from __future__ import annotations

from typing import TYPE_CHECKING

import geoip2.models
import geoip2.records

if TYPE_CHECKING:
    from collections.abc import Sequence


class _Serializable:
    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.to_dict() == other.to_dict()

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def to_dict(self) -> dict:  # noqa: C901
        """Return a dict of the object suitable for serialization."""
        result = {}
        for key, value in self.__dict__.items():
            if hasattr(value, "to_dict") and callable(value.to_dict):
                if d := value.to_dict():
                    result[key] = d
            elif isinstance(value, list):
                ls = []
                for e in value:
                    if hasattr(e, "to_dict") and callable(e.to_dict):
                        if e := e.to_dict():
                            ls.append(e)
                    elif e is not None:
                        ls.append(e)
                if ls:
                    result[key] = ls
            elif value is not None:
                result[key] = value
        return result


class IPRiskReason(_Serializable):
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
    """

    code: str | None
    """This value is a machine-readable code identifying the reason."""

    reason: str | None
    """This property provides a human-readable explanation of the
    reason. The text may change at any time and should not be matched
    against."""

    def __init__(
        self,
        code: str | None = None,
        reason: str | None = None,
    ) -> None:
        """Initialize an IPRiskReason instance."""
        self.code = code
        self.reason = reason


class GeoIP2Location(geoip2.records.Location):
    """Location information for the IP address.

    In addition to the attributes provided by ``geoip2.records.Location``,
    this class provides the local_time attribute.

    """

    local_time: str | None
    """The date and time of the transaction in the time
    zone associated with the IP address. The value is formatted according to
    `RFC 3339 <https://tools.ietf.org/html/rfc3339>`_. For instance, the
    local time in Boston might be returned as 2015-04-27T19:17:24-04:00."""

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002
        """Initialize a GeoIP2Location instance."""
        self.local_time = kwargs.get("local_time")
        super().__init__(*args, **kwargs)


class IPAddress(geoip2.models.Insights):
    """Model for minFraud and GeoIP2 data about the IP address.

    This class inherits from :py:class:`geoip2.models.Insights`. In addition
    to the attributes provided by that class, it provides the ``risk`` and
    ``risk_reasons`` attributes. It also overrides the ``location`` attribute
    to use :py:class:`GeoIP2Location`.
    """

    location: GeoIP2Location
    """Location object for the requested IP address."""

    risk: float | None
    """This field contains the risk associated with the IP address. The value
    ranges from 0.01 to 99. A higher score indicates a higher risk."""

    risk_reasons: list[IPRiskReason]
    """This list contains :class:`.IPRiskReason` objects identifying the
    reasons why the IP address received the associated risk. This will be
    an empty list if there are no reasons."""

    def __init__(
        self,
        locales: Sequence[str] | None,
        *,
        country: dict | None = None,
        location: dict | None = None,
        risk: float | None = None,
        risk_reasons: list[dict] | None = None,
        **kwargs,
    ) -> None:
        """Initialize an IPAddress instance."""
        # For raw attribute
        if country is not None:
            kwargs["country"] = country
        if location is not None:
            kwargs["location"] = location
        if risk is not None:
            kwargs["risk"] = risk
        if risk_reasons is not None:
            kwargs["risk_reasons"] = risk_reasons

        super().__init__(locales, **kwargs)
        self.location = GeoIP2Location(**(location or {}))
        self.risk = risk
        self.risk_reasons = [IPRiskReason(**x) for x in risk_reasons or []]


class ScoreIPAddress(_Serializable):
    """Information about the IP address for minFraud Score."""

    risk: float | None
    """This field contains the risk associated with the IP address. The value
    ranges from 0.01 to 99. A higher score indicates a higher risk."""

    def __init__(self, *, risk: float | None = None, **_) -> None:
        """Initialize a ScoreIPAddress instance."""
        self.risk = risk


class Issuer(_Serializable):
    """Information about the credit card issuer."""

    name: str | None
    """The name of the bank which issued the credit card."""

    matches_provided_name: bool | None
    """This property is ``True`` if the name matches
    the name provided in the request for the card issuer. It is ``False`` if
    the name does not match. The property is ``None`` if either no name or
    no issuer ID number (IIN) was provided in the request or if MaxMind does
    not have a name associated with the IIN."""

    phone_number: str | None
    """The phone number of the bank which issued the credit
    card. In some cases the phone number we return may be out of date."""

    matches_provided_phone_number: bool | None
    """This property is ``True`` if the phone
    number matches the number provided in the request for the card issuer. It
    is ``False`` if the number does not match. It is ``None`` if either no
    phone number or no issuer ID number (IIN) was provided in the request or
    if MaxMind does not have a phone number associated with the IIN."""

    def __init__(
        self,
        *,
        name: str | None = None,
        matches_provided_name: bool | None = None,
        phone_number: str | None = None,
        matches_provided_phone_number: bool | None = None,
        **_,
    ) -> None:
        """Initialize an Issuer instance."""
        self.name = name
        self.matches_provided_name = matches_provided_name
        self.phone_number = phone_number
        self.matches_provided_phone_number = matches_provided_phone_number


class Device(_Serializable):
    """Information about the device associated with the IP address.

    In order to receive device output from minFraud Insights or minFraud
    Factors, you must be using the `Device Tracking Add-on
    <https://dev.maxmind.com/minfraud/track-devices?lang=en>`_.
    """

    confidence: float | None
    """This number represents our confidence that the ``device_id`` refers to
    a unique device as opposed to a cluster of similar devices. A confidence
    of 0.01 indicates very low confidence that the device is unique, whereas
    99 indicates very high confidence."""

    id: str | None
    """A UUID that MaxMind uses for the device associated with this IP address."""

    last_seen: str | None
    """This is the date and time of the last sighting of the device. This is an
    RFC 3339 date-time."""

    local_time: str | None
    """This is the local date and time of the transaction in the time zone of
    the device. This is determined by using the UTC offset associated with
    the device. This is an RFC 3339 date-time."""

    def __init__(
        self,
        *,
        confidence: float | None = None,
        id: str | None = None,
        last_seen: str | None = None,
        local_time: str | None = None,
        **_,
    ) -> None:
        """Initialize a Device instance."""
        self.confidence = confidence
        self.id = id
        self.last_seen = last_seen
        self.local_time = local_time


class Disposition(_Serializable):
    """Information about disposition for the request as set by custom rules.

    In order to receive a disposition, you must be use the minFraud custom
    rules.
    """

    action: str | None
    """The action to take on the transaction as defined by your custom rules.
    The current set of values are "accept", "manual_review", "reject", and
    "test". If you do not have custom rules set up, ``None`` will be
    returned."""

    reason: str | None
    """The reason for the action. The current possible values are "custom_rule"
    and "default". If you do not have custom rules set up, ``None`` will be
    returned."""

    rule_label: str | None
    """The label of the custom rule that was triggered. If you do not have
    custom rules set up, the triggered custom rule does not have a label, or
    no custom rule was triggered, ``None`` will be returned."""

    def __init__(
        self,
        *,
        action: str | None = None,
        reason: str | None = None,
        rule_label: str | None = None,
        **_,
    ) -> None:
        """Initialize a Disposition instance."""
        self.action = action
        self.reason = reason
        self.rule_label = rule_label


class EmailDomain(_Serializable):
    """Information about the email domain passed in the request."""

    first_seen: str | None
    """A date string (e.g. 2017-04-24) to identify the date an email domain
    was first seen by MaxMind. This is expressed using the ISO 8601 date
    format."""

    def __init__(self, *, first_seen: str | None = None, **_) -> None:
        """Initialize an EmailDomain instance."""
        self.first_seen = first_seen


class Email(_Serializable):
    """Information about the email address passed in the request."""

    domain: EmailDomain
    """An object containing information about the email domain."""

    first_seen: str | None
    """A date string (e.g. 2017-04-24) to identify the date an email address
    was first seen by MaxMind. This is expressed using the ISO 8601 date
    format."""

    is_disposable: bool | None
    """This field indicates whether the email is from a disposable email
    provider. It will be ``None`` when an email address was not passed in
    the inputs."""

    is_free: bool | None
    """This field is true if MaxMind believes that this email is hosted by a
    free email provider such as Gmail or Yahoo! Mail."""

    is_high_risk: bool | None
    """This field is true if MaxMind believes that this email is likely to be
    used for fraud. Note that this is also factored into the overall
    `risk_score` in the response as well."""

    def __init__(
        self,
        domain: dict | None = None,
        first_seen: str | None = None,
        is_disposable: bool | None = None,
        is_free: bool | None = None,
        is_high_risk: bool | None = None,
    ) -> None:
        """Initialize an Email instance."""
        self.domain = EmailDomain(**(domain or {}))
        self.first_seen = first_seen
        self.is_disposable = is_disposable
        self.is_free = is_free
        self.is_high_risk = is_high_risk


class CreditCard(_Serializable):
    """Information about the credit card based on the issuer ID number."""

    issuer: Issuer
    """An object containing information about the credit card issuer."""

    country: str | None
    """This property contains the `ISO 3166-1 alpha-2 country code
    <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2>`_ associated with the
    location of the majority of customers using this credit card as
    determined by their billing address. In cases where the location of
    customers is highly mixed, this defaults to the country of the bank
    issuing the card."""

    brand: str | None
    """The card brand, such as "Visa", "Discover", "American Express", etc."""

    is_business: bool | None
    """This property is ``True`` if the card is a business card."""

    is_issued_in_billing_address_country: bool | None
    """This property is true if the country of the billing address matches the
    country of the majority of customers using this credit card. In cases
    where the location of customers is highly mixed, the match is to the
    country of the bank issuing the card."""

    is_prepaid: bool | None
    """This property is ``True`` if the card is a prepaid card."""

    is_virtual: bool | None
    """This property is ``True`` if the card is a virtual card."""

    type: str | None
    """The card's type. The valid values are "charge", "credit", and "debit".
    See Wikipedia for an explanation of the difference between charge and
    credit cards."""

    def __init__(
        self,
        issuer: dict | None = None,
        country: str | None = None,
        brand: str | None = None,
        is_business: bool | None = None,
        is_issued_in_billing_address_country: bool | None = None,
        is_prepaid: bool | None = None,
        is_virtual: bool | None = None,
        type: str | None = None,  # noqa: A002
    ) -> None:
        """Initialize a CreditCard instance."""
        self.issuer = Issuer(**(issuer or {}))
        self.country = country
        self.brand = brand
        self.is_business = is_business
        self.is_issued_in_billing_address_country = is_issued_in_billing_address_country
        self.is_prepaid = is_prepaid
        self.is_virtual = is_virtual
        self.type = type


class BillingAddress(_Serializable):
    """Information about the billing address."""

    is_postal_in_city: bool | None
    """This property is ``True`` if the postal code
    provided with the address is in the city for the address. The property is
    ``False`` when the postal code is not in the city. If the address was
    not provided, could not be parsed, or was outside USA, the property will
    be ``None``."""

    latitude: float | None
    """The latitude associated with the address."""

    longitude: float | None
    """The longitude associated with the address."""

    distance_to_ip_location: int | None
    """The distance in kilometers from the
    address to the IP location."""

    is_in_ip_country: bool | None
    """This property is ``True`` if the address is in the
    IP country. The property is ``False`` when the address is not in the IP
    country. If the address could not be parsed or was not provided or if the
    IP address could not be geolocated, the property will be ``None``."""

    def __init__(
        self,
        *,
        is_postal_in_city: bool | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        distance_to_ip_location: int | None = None,
        is_in_ip_country: bool | None = None,
        **_,
    ) -> None:
        """Initialize a BillingAddress instance."""
        self.is_postal_in_city = is_postal_in_city
        self.latitude = latitude
        self.longitude = longitude
        self.distance_to_ip_location = distance_to_ip_location
        self.is_in_ip_country = is_in_ip_country


class ShippingAddress(_Serializable):
    """Information about the shipping address."""

    is_postal_in_city: bool | None
    """This property is ``True`` if the postal code
    provided with the address is in the city for the address. The property is
    ``False`` when the postal code is not in the city. If the address was
    not provided, could not be parsed, or was not in USA, the property will
    be ``None``."""

    latitude: float | None
    """The latitude associated with the address."""

    longitude: float | None
    """The longitude associated with the address."""

    distance_to_ip_location: int | None
    """The distance in kilometers from the
    address to the IP location."""

    is_in_ip_country: bool | None
    """This property is ``True`` if the address is in the
    IP country. The property is ``False`` when the address is not in the IP
    country. If the address could not be parsed or was not provided or if the
    IP address could not be geolocated, the property will be ``None``."""

    is_high_risk: bool | None
    """This property is ``True`` if the shipping address is high risk.
    If the address could not be parsed or was not provided, the property is
    ``None``."""

    distance_to_billing_address: int | None
    """The distance in kilometers from the
    shipping address to billing address."""

    def __init__(
        self,
        *,
        is_postal_in_city: bool | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        distance_to_ip_location: int | None = None,
        is_in_ip_country: bool | None = None,
        is_high_risk: bool | None = None,
        distance_to_billing_address: int | None = None,
        **_,
    ) -> None:
        """Initialize a ShippingAddress instance."""
        self.is_postal_in_city = is_postal_in_city
        self.latitude = latitude
        self.longitude = longitude
        self.distance_to_ip_location = distance_to_ip_location
        self.is_in_ip_country = is_in_ip_country
        self.is_high_risk = is_high_risk
        self.distance_to_billing_address = distance_to_billing_address


class Phone(_Serializable):
    """Information about the billing or shipping phone number."""

    country: str | None
    """The two-character ISO 3166-1 country code for the country associated with
    the phone number."""

    is_voip: bool | None
    """This property is ``True`` if the phone number is a Voice over Internet
    Protocol (VoIP) number allocated by a regulator. The property is
    ``False`` when the number is not VoIP. If the phone number was not
    provided or we do not have data for it, the property will be ``None``."""

    matches_postal: bool | None
    """This is ```True``` if the phone number's prefix is commonly
    associated with the postal code. It is ```False``` if the prefix is not
    associated with the postal code. It is non-```None``` only when the phone
    number is in the US, the number prefix is in our database, and the
    postal code and country are provided in the request.
    """

    network_operator: str | None
    """The name of the original network operator associated with the phone
    number. This field does not reflect phone numbers that have been ported
    from the original operator to another, nor does it identify mobile
    virtual network operators."""

    number_type: str | None
    """One of the following values: fixed or mobile. Additional values may be
    added in the future."""

    def __init__(
        self,
        *,
        country: str | None = None,
        is_voip: bool | None = None,
        matches_postal: bool | None = None,
        network_operator: str | None = None,
        number_type: str | None = None,
        **_,
    ) -> None:
        """Initialize a Phone instance."""
        self.country = country
        self.is_voip = is_voip
        self.matches_postal = matches_postal
        self.network_operator = network_operator
        self.number_type = number_type


class ServiceWarning(_Serializable):
    """Warning from the web service."""

    code: str | None
    """This value is a machine-readable code identifying the
    warning. See the `response warnings documentation
    <https://dev.maxmind.com/minfraud/api-documentation/responses?lang=en#schema--response--warning>`_
    for the current list of of warning codes."""

    warning: str | None
    """This property provides a human-readable explanation of the
    warning. The description may change at any time and should not be matched
    against."""

    input_pointer: str | None
    """This is a string representing the path to the input that
    the warning is associated with. For instance, if the warning was about
    the billing city, the string would be ``"/billing/city"``."""

    def __init__(
        self,
        *,
        code: str | None = None,
        warning: str | None = None,
        input_pointer: str | None = None,
        **_,
    ) -> None:
        """Initialize a ServiceWarning instance."""
        self.code = code
        self.warning = warning
        self.input_pointer = input_pointer


class Subscores(_Serializable):
    """Risk factor scores used in calculating the overall risk score.

    .. deprecated:: 2.12.0
     Use RiskScoreReason instead.
    """

    avs_result: float | None
    """The risk associated with the AVS result. If present, this is a value
    in the range 0.01 to 99."""

    billing_address: float | None
    """The risk associated with the billing address. If present, this is a
    value in the range 0.01 to 99."""

    billing_address_distance_to_ip_location: float | None
    """The risk associated with the distance between the billing address and
    the location for the given IP address. If present, this is a value in
    the range 0.01 to 99."""

    browser: float | None
    """The risk associated with the browser attributes such as the User-Agent
    and Accept-Language. If present, this is a value in the range 0.01 to
    99."""

    chargeback: float | None
    """Individualized risk of chargeback for the given IP address given for
    your account and any shop ID passed. This is only available to users
    sending chargeback data to MaxMind. If present, this is a value in the
    range 0.01 to 99."""

    country: float | None
    """The risk associated with the country the transaction originated from. If
    present, this is a value in the range 0.01 to 99."""

    country_mismatch: float | None
    """The risk associated with the combination of IP country, card issuer
    country, billing country, and shipping country. If present, this is a
    value in the range 0.01 to 99."""

    cvv_result: float | None
    """The risk associated with the CVV result. If present, this is a value
    in the range 0.01 to 99."""

    device: float | None
    """The risk associated with the device. If present, this is a value in the
    range 0.01 to 99."""

    email_address: float | None
    """The risk associated with the particular email address. If present, this
    is a value in the range 0.01 to 99."""

    email_domain: float | None
    """The general risk associated with the email domain. If present, this is a
    value in the range 0.01 to 99."""

    email_local_part: float | None
    """The risk associated with the email address local part (the part of the
    email address before the @ symbol). If present, this is a value in the
    range 0.01 to 99."""

    email_tenure: float | None
    """The risk associated with the issuer ID number on the email domain. If
    present, this is a value in the range 0.01 to 99.

    .. deprecated:: 1.8.0
        Deprecated effective August 29, 2019. This risk factor score will
        default to 1 and will be removed in a future release. The user
        tenure on email is reflected in the email address risk factor score.

    .. seealso::
        :py:attr:`minfraud.models.Subscores.email_address`
    """

    ip_tenure: float | None
    """The risk associated with the issuer ID number on the IP address. If
    present, this is a value in the range 0.01 to 99.

    .. deprecated:: 1.8.0
        Deprecated effective August 29, 2019. This risk factor score will
        default to 1 and will be removed in a future release. The IP tenure
        is reflected in the overall risk score.

    .. seealso::
        :py:attr:`minfraud.models.Score.risk_score`
    """

    issuer_id_number: float | None
    """The risk associated with the particular issuer ID number (IIN) given the
    billing location and the history of usage of the IIN on your account and
    shop ID. If present, this is a value in the range 0.01 to 99."""

    order_amount: float | None
    """The risk associated with the particular order amount for your account
    and shop ID. If present, this is a value in the range 0.01 to 99."""

    phone_number: float | None
    """The risk associated with the particular phone number. If present, this
    is a value in the range 0.01 to 99."""

    shipping_address: float | None
    """The risk associated with the shipping address. If present, this is a
    value in the range 0.01 to 99."""

    shipping_address_distance_to_ip_location: float | None
    """The risk associated with the distance between the shipping address and
    the location for the given IP address. If present, this is a value in
    the range 0.01 to 99."""

    time_of_day: float | None
    """The risk associated with the local time of day of the transaction in the
    IP address location. If present, this is a value in the range 0.01 to 99."""

    def __init__(
        self,
        *,
        avs_result: float | None = None,
        billing_address: float | None = None,
        billing_address_distance_to_ip_location: float | None = None,
        browser: float | None = None,
        chargeback: float | None = None,
        country: float | None = None,
        country_mismatch: float | None = None,
        cvv_result: float | None = None,
        device: float | None = None,
        email_address: float | None = None,
        email_domain: float | None = None,
        email_local_part: float | None = None,
        email_tenure: float | None = None,
        ip_tenure: float | None = None,
        issuer_id_number: float | None = None,
        order_amount: float | None = None,
        phone_number: float | None = None,
        shipping_address: float | None = None,
        shipping_address_distance_to_ip_location: float | None = None,
        time_of_day: float | None = None,
        **_,
    ) -> None:
        """Initialize a Subscores instance."""
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


class Reason(_Serializable):
    """The risk score reason for the multiplier.

    This class provides both a machine-readable code and a human-readable
    explanation of the reason for the risk score.

    See the `risk reasons documentation <https://dev.maxmind.com/minfraud/api-documentation/responses/#schema--response--risk-score-reason--multiplier-reason>`_
    for the current list of reason codes.
    """

    code: str | None
    """This value is a machine-readable code identifying the reason.

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
    """

    reason: str | None
    """This property provides a human-readable explanation of the
    reason. The text may change at any time and should not be matched
    against."""

    def __init__(
        self,
        *,
        code: str | None = None,
        reason: str | None = None,
        **_,
    ) -> None:
        """Initialize a Reason instance."""
        self.code = code
        self.reason = reason


class RiskScoreReason(_Serializable):
    """The risk score multiplier and the reasons for that multiplier."""

    multiplier: float
    """The factor by which the risk score is increased (if the value is greater than 1)
    or decreased (if the value is less than 1) for given risk reason(s).
    Multipliers greater than 1.5 and less than 0.66 are considered significant
    and lead to risk reason(s) being present."""

    reasons: list[Reason]
    """This list contains :class:`.Reason` objects that describe
    one of the reasons for the multiplier."""

    def __init__(
        self,
        *,
        multiplier: float,
        reasons: list | None = None,
        **_,
    ) -> None:
        """Initialize a RiskScoreReason instance."""
        self.multiplier = multiplier
        self.reasons = [Reason(**x) for x in reasons or []]


class Factors(_Serializable):
    """Model for Factors response."""

    billing_address: BillingAddress
    """A :class:`.BillingAddress` object containing minFraud
    data related to the billing address used in the transaction."""

    billing_phone: Phone
    """A :class:`.Phone` object containing minFraud data related to the billing
    phone used in the transaction."""

    credit_card: CreditCard
    """A :class:`.CreditCard` object containing minFraud data
    about the credit card used in the transaction."""

    disposition: Disposition
    """A :class:`.Disposition` object containing the disposition for the
    request as set by custom rules."""

    funds_remaining: float
    """The approximate US dollar value of the funds remaining on your MaxMind
    account."""

    device: Device
    """A :class:`.Device` object containing information about the device that
    MaxMind believes is associated with the IP address passed in the request."""

    email: Email
    """A :class:`.Email` object containing information about the email address
    passed in the request."""

    id: str
    """This is a UUID that identifies the minFraud request. Please use
    this ID in bug reports or support requests to MaxMind so that we can
    easily identify a particular request."""

    ip_address: IPAddress
    """A :class:`.IPAddress` object containing GeoIP2 and
    minFraud Insights information about the IP address."""

    queries_remaining: int
    """The approximate number of queries remaining on this service before
    your account runs out of funds."""

    risk_score: float
    """This property contains the risk score, from 0.01 to 99. A
    higher score indicates a higher risk of fraud. For example, a score of
    20 indicates a 20% chance that a transaction is fraudulent. We never
    return a risk score of 0, since all transactions have the possibility of
    being fraudulent. Likewise we never return a risk score of 100."""

    shipping_address: ShippingAddress
    """A :class:`.ShippingAddress` object containing
    minFraud data related to the shipping address used in the transaction."""

    shipping_phone: Phone
    """A :class:`.Phone` object containing minFraud data related to the shipping
    phone used in the transaction."""

    subscores: Subscores
    """A :class:`.Subscores` object containing scores for many of the
    individual risk factors that are used to calculate the overall risk
    score.

    .. deprecated:: 2.12.0
        Use RiskScoreReason instead.
    """

    warnings: list[ServiceWarning]
    """This list contains :class:`.ServiceWarning` objects detailing
    issues with the request that was sent such as invalid or unknown inputs.
    It is highly recommended that you check this list for issues when
    integrating the web service."""

    risk_score_reasons: list[RiskScoreReason]
    """This list contains :class:`.RiskScoreReason` objects that describe
    risk score reasons for a given transaction that change the risk score
    significantly. Risk score reasons are usually only returned for medium to
    high risk transactions. If there were no significant changes to the risk
    score due to these reasons, then this list will be empty."""

    def __init__(
        self,
        locales: Sequence[str],
        *,
        billing_address: dict | None = None,
        billing_phone: dict | None = None,
        credit_card: dict | None = None,
        disposition: dict | None = None,
        funds_remaining: float,
        device: dict | None = None,
        email: dict | None = None,
        id: str,
        ip_address: dict | None = None,
        queries_remaining: int,
        risk_score: float,
        shipping_address: dict | None = None,
        shipping_phone: dict | None = None,
        subscores: dict | None = None,
        warnings: list[dict] | None = None,
        risk_score_reasons: list[dict] | None = None,
        **_,
    ) -> None:
        """Initialize a Factors instance."""
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


class Insights(_Serializable):
    """Model for Insights response."""

    billing_address: BillingAddress
    """A :class:`.BillingAddress` object containing minFraud
    data related to the billing address used in the transaction."""

    billing_phone: Phone
    """A :class:`.Phone` object containing minFraud data related to the billing
    phone used in the transaction."""

    credit_card: CreditCard
    """A :class:`.CreditCard` object containing minFraud data
    about the credit card used in the transaction."""

    device: Device
    """A :class:`.Device` object containing information about the device that
    MaxMind believes is associated with the IP address passed in the request."""

    disposition: Disposition
    """A :class:`.Disposition` object containing the disposition for the
    request as set by custom rules."""

    email: Email
    """A :class:`.Email` object containing information about the email address
    passed in the request."""

    funds_remaining: float
    """The approximate US dollar value of the funds remaining on your MaxMind
    account."""

    id: str
    """This is a UUID that identifies the minFraud request. Please use
    this ID in bug reports or support requests to MaxMind so that we can
    easily identify a particular request."""

    ip_address: IPAddress
    """A :class:`.IPAddress` object containing GeoIP2 and
    minFraud Insights information about the IP address."""

    queries_remaining: int
    """The approximate number of queries remaining on this service before
    your account runs out of funds."""

    risk_score: float
    """This property contains the risk score, from 0.01 to 99. A
    higher score indicates a higher risk of fraud. For example, a score of
    20 indicates a 20% chance that a transaction is fraudulent. We never
    return a risk score of 0, since all transactions have the possibility of
    being fraudulent. Likewise we never return a risk score of 100."""

    shipping_address: ShippingAddress
    """A :class:`.ShippingAddress` object containing
    minFraud data related to the shipping address used in the transaction."""

    shipping_phone: Phone
    """A :class:`.Phone` object containing minFraud data related to the shipping
    phone used in the transaction."""

    warnings: list[ServiceWarning]
    """This list contains :class:`.ServiceWarning` objects detailing
    issues with the request that was sent such as invalid or unknown inputs.
    It is highly recommended that you check this list for issues when
    integrating the web service."""

    def __init__(
        self,
        locales: Sequence[str],
        *,
        billing_address: dict | None = None,
        billing_phone: dict | None = None,
        credit_card: dict | None = None,
        device: dict | None = None,
        disposition: dict | None = None,
        email: dict | None = None,
        funds_remaining: float,
        id: str,
        ip_address: dict | None = None,
        queries_remaining: int,
        risk_score: float,
        shipping_address: dict | None = None,
        shipping_phone: dict | None = None,
        warnings: list[dict] | None = None,
        **_,
    ) -> None:
        """Initialize an Insights instance."""
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


class Score(_Serializable):
    """Model for Score response."""

    disposition: Disposition
    """A :class:`.Disposition` object containing the disposition for the
    request as set by custom rules."""

    funds_remaining: float
    """The approximate US dollar value of the funds remaining on your MaxMind
    account."""

    id: str
    """This is a UUID that identifies the minFraud request. Please use
    this ID in bug reports or support requests to MaxMind so that we can
    easily identify a particular request."""

    ip_address: ScoreIPAddress
    """A :class:`.ScoreIPAddress` object containing IP address risk."""

    queries_remaining: int
    """The approximate number of queries remaining on this service before
    your account runs out of funds."""

    risk_score: float
    """This property contains the risk score, from 0.01 to 99. A
    higher score indicates a higher risk of fraud. For example, a score of
    20 indicates a 20% chance that a transaction is fraudulent. We never
    return a risk score of 0, since all transactions have the possibility of
    being fraudulent. Likewise we never return a risk score of 100."""

    warnings: list[ServiceWarning]
    """This list contains :class:`.ServiceWarning` objects detailing
    issues with the request that was sent such as invalid or unknown inputs.
    It is highly recommended that you check this list for issues when
    integrating the web service."""

    def __init__(
        self,
        *,
        disposition: dict | None = None,
        funds_remaining: float,
        id: str,
        ip_address: dict | None = None,
        queries_remaining: int,
        risk_score: float,
        warnings: list[dict] | None = None,
        **_,
    ) -> None:
        """Initialize a Score instance."""
        self.disposition = Disposition(**(disposition or {}))
        self.funds_remaining = funds_remaining
        self.id = id
        self.ip_address = ScoreIPAddress(**(ip_address or {}))
        self.queries_remaining = queries_remaining
        self.risk_score = risk_score
        self.warnings = [ServiceWarning(**x) for x in warnings or []]
