from collections import namedtuple
from functools import update_wrapper
import geoip2.models
import geoip2.records


class _InflateToNamedtuple(object):
    def __init__(self, cls):
        keys = sorted(cls._fields.keys())
        self.fields = cls._fields
        name = cls.__name__
        cls.__name__ += 'Super'
        nt = namedtuple(name, keys)
        nt.__name__ = name + 'NamedTuple'
        nt.__new__.__defaults__ = (None, ) * len(keys)
        self.cls = type(name, (nt, cls), {'__slots__': ()})
        update_wrapper(self, cls)

    def __call__(self, *args, **kwargs):
        if (args and kwargs) or len(args) > 1:
            raise ValueError('Only provide a single (dict) positional argument'
                             ' or use keyword arguments. Do not use both.')
        if args:
            values = args[0] if args[0] else {}

            for field, default in self.fields.items():
                if callable(default):
                    kwargs[field] = default(values.get(field))
                else:
                    kwargs[field] = values.get(field, default)

        return self.cls(**kwargs)

    def __repr__(self):
        return repr(self.cls)


inflate_to_namedtuple = _InflateToNamedtuple

# Using a class factory decorator rather than a metaclass as supporting
# metaclasses on Python 2 and 3 is more painful (although we could use
# six, I suppose).
# def inflate_to_namedtuple(orig_cls):
#     fields = orig_cls._fields
#     keys = sorted(orig_cls._fields.keys())
#     nt = namedtuple(orig_cls.__name__, keys)
#     nt.__name__ = orig_cls.__name__ + 'NamedTuple'
#     nt.__new__.__defaults__ = (None,) * len(keys)
#     new_dict = orig_cls.__dict__.copy()
#     del new_dict['_fields']
#     new_dict['__slots__'] = ()
#     cls = type(orig_cls.__name__, (nt, ), new_dict)
#
#     update_wrapper(inflate_to_namedtuple, cls)
#     orig_new = cls.__new__
#
#     def new(self, *args, **kwargs):
#         if (args and kwargs) or len(args) > 1:
#             raise ValueError('Only provide a single (dict) positional argument'
#                              ' or use keyword arguments. Do not use both.')
#         if args:
#             values = args[0] if args[0] else {}
#
#             for field, default in fields.items():
#                 if callable(default):
#                     kwargs[field] = default(values.get(field))
#                 else:
#                     kwargs[field] = values.get(field, default)
#
#         return orig_new(cls, **kwargs)
#
#     cls.__new__ = new
#     return cls


def create_warnings(warnings):
    if not warnings:
        return ()
    return tuple([Warning(x) for x in warnings])


class GeoIP2Location(geoip2.records.Location):
    _valid_attributes = geoip2.records.Location._valid_attributes.union(
        set(['local_time']))


class GeoIP2Country(geoip2.records.Country):
    _valid_attributes = geoip2.records.Country._valid_attributes.union(
        set(['is_high_risk']))


# fill in missing data
class IPLocation(geoip2.models.Insights):
    def __init__(self, raw_response, locales=None):
        if raw_response is None:
            raw_response = {}
        super(IPLocation, self).__init__(raw_response, locales)
        self.city = GeoIP2Country(locales, **raw_response.get('city', {}))
        self.location = GeoIP2Location(**raw_response.get('location', {}))


@inflate_to_namedtuple
class Issuer(object):
    _fields = {
        'name': None,
        'matches_provided_name': None,
        'phone_number': None,
        'matches_provided_phone_number': None
    }


@inflate_to_namedtuple
class CreditCard(object):
    _fields = {
        'issuer': Issuer,
        'country': None,
        'is_issued_in_billing_address_country': None,
        'is_prepaid': None
    }


@inflate_to_namedtuple
class BillingAddress(object):
    _fields = {
        'is_postal_in_city': None,
        'latitude': None,
        'longitude': None,
        'distance_to_ip_location': None,
        'is_in_ip_country': None
    }


@inflate_to_namedtuple
class ShippingAddress(object):
    _fields = {
        'is_postal_in_city': None,
        'latitude': None,
        'longitude': None,
        'distance_to_ip_location': None,
        'is_in_ip_country': None,
        'is_high_risk': None,
        'distance_to_billing_address': None
    }


@inflate_to_namedtuple
class Warning(object):
    _fields = {'code': None, 'warning': None, 'input': None}


@inflate_to_namedtuple
class Insights(object):
    _fields = {
        'id': None,
        'risk_score': None,
        'warnings': create_warnings,
        'credits_remaining': None,
        'ip_location': IPLocation,
        'credit_card': CreditCard,
        'shipping_address': ShippingAddress,
        'billing_address': BillingAddress
    }


@inflate_to_namedtuple
class Score(object):
    _fields = {
        'id': None,
        'risk_score': None,
        'warnings': create_warnings,
        'credits_remaining': None,
    }
