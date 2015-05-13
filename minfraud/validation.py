import re
import sys
from decimal import Decimal

from strict_rfc3339 import validate_rfc3339
from validate_email import validate_email
from voluptuous import All, Any, In, Length, Match, Range, Required, Schema
import rfc3987

is_PY3 = sys.version_info[0] == 3

if is_PY3:
    import ipaddress  # pylint:disable=F0401

    unicode_or_printable_ascii = str
else:
    import ipaddr as ipaddress  # pylint:disable=F0401

    ipaddress.ip_address = ipaddress.IPAddress

    unicode_or_printable_ascii = Any(unicode, Match('^[\x20-\x7E]*$'))

any_string = Any(unicode_or_printable_ascii, str)

md5 = All(any_string, Match('^[0-9A-Fa-f]{32}$'))

country_code = All(any_string, Match('^[A-Z]{2}$'))

telephone_country_code = Any(All(any_string, Match('^[0-9]{1,4}$')),
                             All(int, Range(min=1,
                                            max=9999)))

subdivision_iso_code = All(any_string, Match('^[0-9A-Z]{1,4}$'))


def ip_address(s):
    # ipaddress accepts numeric IPs, which we don't want.
    if (isinstance(s, str) or isinstance(s, unicode)) \
            and not re.match('^\d+$', s):
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
    'address': unicode_or_printable_ascii,
    'address_2': unicode_or_printable_ascii,
    'city': unicode_or_printable_ascii,
    'company': unicode_or_printable_ascii,
    'country': country_code,
    'first_name': unicode_or_printable_ascii,
    'last_name': unicode_or_printable_ascii,
    'phone_country_code': telephone_country_code,
    'phone_number': unicode_or_printable_ascii,
    'postal': unicode_or_printable_ascii,
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

single_char = Match('^[A-Za-z0-9]$')

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

price = All(Any(float, int, Decimal), Range(min=0, min_included=False))


def uri(s):
    if rfc3987.parse(s).get('scheme') in ['http', 'https']:
        return s
    raise ValueError


validate_transaction = Schema({
    'account': {'user_id': unicode_or_printable_ascii,
                'username_md5': md5, },
    'billing': address,
    'payment': {
        'processor': payment_processor,
        'was_authorized': bool,
        'decline_code': unicode_or_printable_ascii,
    },
    'credit_card': {
        'avs_result': single_char,
        'bank_name': unicode_or_printable_ascii,
        'bank_phone_country_code': telephone_country_code,
        'bank_phone_number': unicode_or_printable_ascii,
        'cvv_result': single_char,
        'issuer_id_number': iin,
        'last_4_digits': credit_card_last_4,
    },
    Required('device'): {
        'accept_language': unicode_or_printable_ascii,
        Required('ip_address'): ip_address,
        'user_agent': unicode_or_printable_ascii
    },
    'email': {'address': email_or_md5,
              'domain': hostname, },
    'event': {
        'shop_id': unicode_or_printable_ascii,
        'time': rfc3339_datetime,
        'type': event_type,
        'transaction_id': unicode_or_printable_ascii,
    },
    'order': {
        'affiliate_id': unicode_or_printable_ascii,
        'amount': price,
        'currency': currency_code,
        'discount_code': unicode_or_printable_ascii,
        'referrer_uri': uri,
        'subaffiliate_id': unicode_or_printable_ascii,
    },
    'shipping': shipping_address,
    'shopping_cart': [{
        'category': unicode_or_printable_ascii,
        'item_id': unicode_or_printable_ascii,
        'price': price,
        'quantity': All(int, Range(min=1)),
    }, ],
}, )
