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
    _valid_attributes = geoip2.records.Location._valid_attributes.union(
        set(['local_time']))


class GeoIP2Country(geoip2.records.Country):
    _valid_attributes = geoip2.records.Country._valid_attributes.union(
        set(['is_high_risk']))


class IPLocation(geoip2.models.Insights):
    def __init__(self, ip_location):
        if ip_location is None:
            ip_location = {}
        locales = ip_location.get('locales')
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
    __slots__ = ()
    _fields = {
        'name': None,
        'matches_provided_name': None,
        'phone_number': None,
        'matches_provided_phone_number': None
    }


@_inflate_to_namedtuple
class CreditCard(object):
    __slots__ = ()
    _fields = {
        'issuer': Issuer,
        'country': None,
        'is_issued_in_billing_address_country': None,
        'is_prepaid': None
    }


@_inflate_to_namedtuple
class BillingAddress(object):
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
    __slots__ = ()
    _fields = {'code': None, 'warning': None, 'input': None}


@_inflate_to_namedtuple
class Insights(object):
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
    __slots__ = ()
    _fields = {
        'id': None,
        'risk_score': None,
        'warnings': _create_warnings,
        'credits_remaining': None,
    }
