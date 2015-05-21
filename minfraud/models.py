"""
minfraud.models
~~~~~~~~~~~~~~~

This module contains models for the minFraud response object.

"""
from collections import namedtuple
from functools import update_wrapper

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
    orig_cls.__name__ += 'Super'
    nt = namedtuple(name, keys)
    nt.__name__ = name + 'NamedTuple'
    nt.__new__.__defaults__ = (None, ) * len(keys)
    cls = type(name, (nt, orig_cls), {'__slots__': ()})
    update_wrapper(_inflate_to_namedtuple, cls)
    cls.__doc__ = orig_cls.__doc__
    orig_new = cls.__new__

    def new(cls, *args, **kwargs):
        if (args and kwargs) or len(args) > 1:
            raise ValueError('Only provide a single (dict) positional argument'
                             ' or use keyword arguments. Do not use both.')
        if args:
            values = args[0] if args[0] else {}

            for field, default in fields.items():
                if callable(default):
                    kwargs[field] = default(values.get(field))
                else:
                    kwargs[field] = values.get(field, default)

        return orig_new(cls, **kwargs)

    cls.__new__ = staticmethod(new)
    return cls


def _create_warnings(warnings):
    if not warnings:
        return ()
    return tuple([Warning(x) for x in warnings])


class GeoIP2Location(geoip2.records.Location):
    """
    Location information for the IP address

    In addition to the attributes provided by ``geoip2.records.Location``,
    this class provides:

    :ivar local_time: The date and time of the transaction in the time
      zone associated with the IP address. The value is formated according to
      RFC 3339. For instance, the local time in Boston might be returned as
      2015-04-27T19:17:24-04:00.
    :type local_time: str | None

    Parent:

    """
    __doc__ += geoip2.records.Location.__doc__
    _valid_attributes = geoip2.records.Location._valid_attributes.union(
        set(['local_time']))


class GeoIP2Country(geoip2.records.Country):
    """
    Country information for the IP address

    In addition to the attributes provided by ``geoip2.records.Country``,
    this class provides:

    :ivar is_high_risk: This is true if the IP country is high risk.
    :type is_high_risk: bool | None

    Parent:

    """
    __doc__ += geoip2.records.Country.__doc__
    _valid_attributes = geoip2.records.Country._valid_attributes.union(
        set(['is_high_risk']))


class IPLocation(geoip2.models.Insights):
    __doc__ = geoip2.models.Insights.__doc__

    def __init__(self, ip_location):
        if ip_location is None:
            ip_location = {}
        locales = ip_location.get('_locales')
        if '_locales' in ip_location:
            del ip_location['_locales']
        super(IPLocation, self).__init__(ip_location, locales=locales)
        self.country = GeoIP2Country(locales, **ip_location.get('country', {}))
        self.location = GeoIP2Location(**ip_location.get('location', {}))
        self._finalized = True

    # Unfortunately the GeoIP2 models are not immutable, only the records. This
    # corrects that for minFraud
    def __setattr__(self, name, value):
        if hasattr(self, '_finalized') and self._finalized:
            raise AttributeError("can't set attribute")
        super(IPLocation, self).__setattr__(name, value)


@_inflate_to_namedtuple
class Issuer(object):
    """
    Information about the credit card issuer.

    :ivar name: The name of the bank which issued the credit card.
    :type name: str | None
    :ivar matches_provided_name: This property is ``True`` if the name matches
      the name provided in the request for the card issuer. It is ``False`` if
      the name does not match. The property is ``None`` if either no name or
      issuer ID number (IIN) was provided in the request or if MaxMind does not
      have a name associated with the IIN.
    :type matches_provided_name: bool
    :ivar phone_number: The phone number of the bank which issued the credit
      card. In some cases the phone number we return may be out of date.
    :type phone_number: str
    :ivar matches_provided_phone_number: This property is ``True`` if the phone
      number matches the number provided in the request for the card issuer. It
      is ``False`` if the number does not match. It is ``None`` if either no
      phone number or issuer ID number (IIN) was provided in the request or if
      MaxMind does not have a phone number associated with the IIN.
    :type matches_provided_phone_number: bool
    """
    __slots__ = ()
    _fields = {
        'name': None,
        'matches_provided_name': None,
        'phone_number': None,
        'matches_provided_phone_number': None
    }


@_inflate_to_namedtuple
class CreditCard(object):
    """
    Information about the credit card based on the issuer ID number

    :ivar country: This property contains an ISO 3166-1 alpha-2 country
      code representing the country that the card was issued in.
    :type country: str | None
    :ivar is_issued_in_billing_address_country: This property is true if the
      country of the billing address matches the country that the credit card
      was issued in.
    :type is_issued_in_billing_address_country: bool | None
    :ivar is_prepaid: This property is ``True`` if the card is a prepaid card.
    :type is_prepaid: bool | None
    :ivar issuer: An object containing information about the credit card issuer.
    :type issuer: Issuer
    """
    __slots__ = ()
    _fields = {
        'issuer': Issuer,
        'country': None,
        'is_issued_in_billing_address_country': None,
        'is_prepaid': None
    }


@_inflate_to_namedtuple
class BillingAddress(object):
    """
    Information about the billing address

    :ivar distance_to_ip_location: The distance in kilometers from the
      address to the IP location in kilometers.
    :type distance_to_ip_location: int | None
    :ivar is_in_ip_country: This property is ``True`` if the address is in the
      IP country. The property is ``False`` when the address is not in the IP
      country. If the address could not be parsed or was not provided or if the
      IP address could not be geo-located, the property will be ``None``.
    :type is_in_ip_country: bool | None
    :ivar is_postal_in_city: This property is ``True`` if the postal code
      provided with the address is in the city for the address. The property is
      ``False`` when the postal code is not in the city. If the address could
      not be parsed or was not provided, the property will be ``None``.
    :type is_postal_in_city: bool | None
    :ivar latitude: The latitude associated with the address.
    :type latitude: float | None
    :ivar longitude: The longitude associated with the address.
    :type longitude: float | None
    """
    __slots__ = ()
    _fields = {
        'is_postal_in_city': None,
        'latitude': None,
        'longitude': None,
        'distance_to_ip_location': None,
        'is_in_ip_country': None
    }


@_inflate_to_namedtuple
class ShippingAddress(object):
    """
    Information about the shipping address

    :ivar distance_to_ip_location: The distance in kilometers from the
      address to the IP location in kilometers.
    :type distance_to_ip_location: int | None
    :ivar is_in_ip_country: This property is ``True`` if the address is in the
      IP country. The property is ``False`` when the address is not in the IP
      country. If the address could not be parsed or was not provided or if the
      IP address could not be geo-located, the property will be ``None``.
    :type is_in_ip_country: bool | None
    :ivar is_postal_in_city: This property is ``True`` if the postal code
      provided with the address is in the city for the address. The property is
      ``False`` when the postal code is not in the city. If the address could
      not be parsed or was not provided, the property will be ``None``.
    :type is_postal_in_city: bool | None
    :ivar latitude: The latitude associated with the address.
    :type latitude: float | None
    :ivar longitude: The longitude associated with the address.
    :type longitude: float | None
    :ivar is_high_risk: This property is ``True`` if the shipping address is in
      the IP country. The property is ``false`` when the address is not in the
      IP country. If the shipping address could not be parsed or was not
      provided or the IP address could not be geo-located, then the property is
      ``None``.
    :type is_high_risk: bool | None
    :ivar distance_to_billing_address: The distance in kilometers from the
      shipping address to billing address.
    :type distance_to_billing_address: int | None
    """
    __slots__ = ()
    _fields = {
        'is_postal_in_city': None,
        'latitude': None,
        'longitude': None,
        'distance_to_ip_location': None,
        'is_in_ip_country': None,
        'is_high_risk': None,
        'distance_to_billing_address': None
    }


@_inflate_to_namedtuple
class Warning(object):
    """
    Warning from the web service

    :ivar code: This value is a machine-readable code identifying the
      warning. See the `web service documentation
      <http://dev.maxmind.com/minfraud-score-and-insights-api-documentation/#Warning_Object>`_
      for the current list of of warning codes.
    :type code: str
    :ivar warning: This property provides a human-readable explanation of the
      warning. The description may change at any time and should not be matched
      against.
    :type warning: str
    :ivar input: This is a tuple of keys representing the path to the input that
      the warning is associated with. For instance, if the warning was about the
      billing city, the tuple would be ``("billing", "city")``. The key is used
      for an object and the index number for an array.
    :type input: tuple[str|int]
    """
    __slots__ = ()
    _fields = {
        'code': None,
        'warning': None,
        'input': lambda x: tuple(x) if x else ()
    }


@_inflate_to_namedtuple
class Insights(object):
    """
    Model for Insights response

    :ivar id: This is a UUID that identifies the minFraud request. Please use
      this ID in bug reports or support requests to MaxMind so that we can
      easily identify a particular request.
    :type id: str
    :ivar credits_remaining: The approximate number of service credits remaining
      on your account.
    :type credits_remaining: int
    :ivar warnings: This tuple contains :class:`.Warning` objects detailing
      issues with the request that was sent such as invalid or unknown inputs.
      It is highly recommended that you check this array for issues when
      integrating the web service.
    :type warnings: tuple[Warning]
    :ivar risk_score: This property contains the risk score, from 0.01 to 99. A
      higher score indicates a higher risk of fraud. For example, a score of 20
      indicates a 20% chance that a transaction is fraudulent. We never return a
      risk score of 0, since all transactions have the possibility of being
      fraudulent. Likewise we never return a risk score of 100.
    :type risk_score: float
    :ivar credit_card: A :class:`.CreditCard` object containing minFraud data
      about the credit card used in the transaction.
    :type credit_card: CreditCard
    :ivar ip_location: A :class:`.IPLocation` object containing GeoIP2 and
      minFraud Insights information about the geo-located IP address.
    :type ip_location: IPLocation
    :ivar billing_address: A :class:`.BillingAddress` object containing minFraud
      data related to the billing address used in the transaction.
    :type billing_address: BillingAddress
    :ivar shipping_address: A :class:`.ShippingAddress` object containing
      minFraud data related to the shipping address used in the transaction.
    """
    __slots__ = ()
    _fields = {
        'id': None,
        'risk_score': None,
        'warnings': _create_warnings,
        'credits_remaining': None,
        'ip_location': IPLocation,
        'credit_card': CreditCard,
        'shipping_address': ShippingAddress,
        'billing_address': BillingAddress
    }


@_inflate_to_namedtuple
class Score(object):
    """
    Model for Score response

    :ivar id: This is a UUID that identifies the minFraud request. Please use
      this ID in bug reports or support requests to MaxMind so that we can easily
      identify a particular request.
    :type id: str
    :ivar credits_remaining: The approximate number of service credits remaining
      on your account.
    :type credits_remaining: int
    :ivar warnings: This tuple contains :class:`.Warning` objects detailing
      issues with the request that was sent such as invalid or unknown inputs. It
      is highly recommended that you check this array for issues when integrating
      the web service.
    :type warnings: tuple[Warning]
    :ivar risk_score: This property contains the risk score, from 0.01 to 99. A
      higher score indicates a higher risk of fraud. For example, a score of 20
      indicates a 20% chance that a transaction is fraudulent. We never return a
      risk score of 0, since all transactions have the possibility of being
      fraudulent. Likewise we never return a risk score of 100.
    :type risk_score: float
    """
    __slots__ = ()
    _fields = {
        'id': None,
        'risk_score': None,
        'warnings': _create_warnings,
        'credits_remaining': None,
    }
