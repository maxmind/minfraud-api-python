import re
import sys

from strict_rfc3339 import validate_rfc3339
from validate_email import validate_email
from voluptuous import All, Any, In, Length, Match, Range, Required, Schema
import rfc3987

is_PY3 = sys.version_info[0] == 3

if is_PY3:
    import ipaddress  # pylint:disable=F0401
else:
    import ipaddr as ipaddress  # pylint:disable=F0401

    ipaddress.ip_address = ipaddress.IPAddress

if is_PY3:
    string_types = str
else:
    string_types = basestring

md5 = All(str, Match('^[0-9A-Fa-f]{32}$'))

country_code = All(str, Match('^[A-Z]{2}$'))

telephone_country_code = All(str, Match('^[0-9]{1,4}$'))

subdivision_iso_code = All(str, Match('^[A-Z]{2}$'))


def ip_address(s):
    # ipaddress accepts numeric IPs, which we don't want.
    if isinstance(s, str) and not re.match('^\d+$', s):
        return str(ipaddress.ip_address(s))
    raise ValueError


def email_or_md5(s):
    if validate_email(s) or re.match('^[0-9A-Fa-f]{32}$', s):
        return s
    raise ValueError


# based off of:
# http://stackoverflow.com/questions/2532053/validate-a-hostname-string
def hostname(hostname):
    if len(hostname) > 255:
        raise ValueError
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    if all(allowed.match(x) for x in hostname.split(".")):
        return hostname
    raise ValueError


delivery_speed = In(['same_day', 'overnight', 'expedited', 'standard'])

address = {
    'address': str,
    'address_2': str,
    'city': str,
    'company': str,
    'country': country_code,
    'first_name': str,
    'last_name': str,
    'phone_country_code': telephone_country_code,
    'phone_number': str,
    'postal': str,
    'region': subdivision_iso_code,
}

shipping_address = address.copy()

shipping_address['delivery_speed'] = delivery_speed

processors = ['adyen',
              'altapay',
              'amazon_payments',
              'authorizenet',
              'balanced',
              'beanstream',
              'bluepay',
              'braintree',
              'chase_paymentech',
              'cielo',
              'collector',
              'compropago',
              'conekta',
              'cuentadigital',
              'dibs',
              'digital_river',
              'elavon',
              'epayeu',
              'eprocessing_network',
              'eway',
              'first_data',
              'global_payments',
              'ingenico',
              'internetsecure',
              'intuit_quickbooks_payments',
              'iugu',
              'mastercard_payment_gateway',
              'mercadopago',
              'merchant_esolutions',
              'mirjeh',
              'mollie',
              'moneris_solutions',
              'nmi',
              'other',
              'openpaymx',
              'optimal_payments',
              'payfast',
              'paygate',
              'payone',
              'paypal',
              'paystation',
              'paytrace',
              'paytrail',
              'payture',
              'payu',
              'payulatam',
              'princeton_payment_solutions',
              'psigate',
              'qiwi',
              'raberil',
              'rede',
              'redpagos',
              'rewardspay',
              'sagepay',
              'simplify_commerce',
              'skrill',
              'smartcoin',
              'sps_decidir',
              'stripe',
              'telerecargas',
              'towah',
              'usa_epay',
              'vindicia',
              'virtual_card_services',
              'vme',
              'worldpay', ]

payment_processor = In(processors)

single_char = All(str, Length(min=1, max=1))

iin = Match('^[0-9]{6}$')

credit_card_last_4 = Match('^[0-9]{4}$')


def rfc3339_datetime(s):
    if validate_rfc3339(s):
        return s
    raise ValueError


event_types = ['account_creation',
               'account_login',
               'purchase',
               'recurring_purchase',
               'referral',
               'survey', ]

event_type = In(event_types)

currency_code = Match('^[A-Z]{3}$')

price = All(Any(float, int), Range(min=0))


def uri(s):
    if rfc3987.parse(s).get('scheme') in ['http', 'https']:
        return s
    raise ValueError


transaction_validator = Schema({
    'account': {'user_id': str,
                'username_md5': md5, },
    'billing': address,
    'payment': {
        'processor': payment_processor,
        'was_authorized': bool,
        'decline_code': str,
    },
    'credit_card': {
        'avs_result': single_char,
        'bank_name': str,
        'bank_phone_country_code': telephone_country_code,
        'bank_phone_number': str,
        'cvv_result': single_char,
        'issuer_id_number': iin,
        'last_4_digits': credit_card_last_4,
    },
    Required('device'): {
        'accept_language': str,
        Required('ip_address'): ip_address,
        'user_agent': str
    },
    'email': {'address': email_or_md5,
              'domain': hostname, },
    'event': {
        'shop_id': str,
        'time': rfc3339_datetime,
        'type': event_type,
        'transaction_id': str,
    },
    'order': {
        'affiliate_id': str,
        'amount': price,
        'currency': currency_code,
        'discount_code': str,
        'referrer_uri': uri,
        'subaffiliate_id': str,
    },
    'shipping': shipping_address,
    'shopping_cart': [{
        'category': str,
        'item_id': str,
        'price': price,
        'quantity': All(int, Range(min=0)),
    }, ],
}, )
