"""This is an internal module used for validating the minFraud request."""

import re
import sys
from decimal import Decimal

import rfc3987
from geoip2.compat import compat_ip_address
from strict_rfc3339 import validate_rfc3339

# I can't reproduce the failure locally and the order looks right to me.
# It is failing on pylint 1.8.3 on Travis. We should try removing this
# when a new version of pylint is released.
# pylint: disable=wrong-import-order
from validate_email import validate_email
from voluptuous import All, Any, In, Match, Range, Required, Schema

"""
Internal code for validating the transaction dictionary.

This code is only intended for internal use and is subject to change in ways
that may break any direct use of it.

"""

# Pylint doesn't like the private function type naming for the callable
# objects below. Given the consistent use of them, the current names seem
# preferable to blindly following pylint.
#
# pylint: disable=invalid-name,undefined-variable

if sys.version_info[0] >= 3:
    _unicode = str
    _unicode_or_printable_ascii = str
    long = int
else:
    _unicode = unicode
    _unicode_or_printable_ascii = Any(unicode, Match(r"^[\x20-\x7E]*$"))

_any_string = Any(_unicode_or_printable_ascii, str)
_any_number = Any(float, int, long, Decimal)

_custom_input_key = All(_any_string, Match(r"^[a-z0-9_]{1,25}$"))

_custom_input_value = Any(
    All(_any_string, Match(r"^[^\n]{1,255}\Z")),
    All(
        _any_number, Range(min=-1e13, max=1e13, min_included=False, max_included=False)
    ),
    bool,
)

_md5 = All(_any_string, Match(r"^[0-9A-Fa-f]{32}$"))

_country_code = All(_any_string, Match(r"^[A-Z]{2}$"))

_telephone_country_code = Any(
    All(_any_string, Match("^[0-9]{1,4}$")), All(int, Range(min=1, max=9999))
)

_subdivision_iso_code = All(_any_string, Match(r"^[0-9A-Z]{1,4}$"))


def _ip_address(s):
    # ipaddress accepts numeric IPs, which we don't want.
    if isinstance(s, (str, _unicode)) and not re.match(r"^\d+$", s):
        return str(compat_ip_address(s))
    raise ValueError


def _email_or_md5(s):
    if validate_email(s) or re.match(r"^[0-9A-Fa-f]{32}$", s):
        return s
    raise ValueError


# based off of:
# http://stackoverflow.com/questions/2532053/validate-a-hostname-string
def _hostname(hostname):
    if len(hostname) > 255:
        raise ValueError
    allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    if all(allowed.match(x) for x in hostname.split(".")):
        return hostname
    raise ValueError


_delivery_speed = In(["same_day", "overnight", "expedited", "standard"])

_address = {
    "address": _unicode_or_printable_ascii,
    "address_2": _unicode_or_printable_ascii,
    "city": _unicode_or_printable_ascii,
    "company": _unicode_or_printable_ascii,
    "country": _country_code,
    "first_name": _unicode_or_printable_ascii,
    "last_name": _unicode_or_printable_ascii,
    "phone_country_code": _telephone_country_code,
    "phone_number": _unicode_or_printable_ascii,
    "postal": _unicode_or_printable_ascii,
    "region": _subdivision_iso_code,
}

_shipping_address = _address.copy()

_shipping_address["delivery_speed"] = _delivery_speed

_payment_processor = In(
    [
        "adyen",
        "affirm",
        "afterpay",
        "altapay",
        "amazon_payments",
        "american_express_payment_gateway",
        "authorizenet",
        "balanced",
        "beanstream",
        "bluepay",
        "bluesnap",
        "bpoint",
        "braintree",
        "cardpay",
        "ccavenue",
        "ccnow",
        "cetelem",
        "chase_paymentech",
        "checkout_com",
        "cielo",
        "collector",
        "commdoo",
        "compropago",
        "concept_payments",
        "conekta",
        "ct_payments",
        "cuentadigital",
        "curopayments",
        "cybersource",
        "dalenys",
        "dalpay",
        "datacash",
        "dibs",
        "digital_river",
        "dotpay",
        "ebs",
        "ecomm365",
        "ecommpay",
        "elavon",
        "emerchantpay",
        "epay",
        "eprocessing_network",
        "epx",
        "eway",
        "exact",
        "first_data",
        "g2a_pay",
        "global_payments",
        "gocardless",
        "heartland",
        "hipay",
        "ingenico",
        "interac",
        "internetsecure",
        "intuit_quickbooks_payments",
        "iugu",
        "klarna",
        "lemon_way",
        "mastercard_payment_gateway",
        "mercadopago",
        "mercanet",
        "merchant_esolutions",
        "mirjeh",
        "mollie",
        "moneris_solutions",
        "nmi",
        "oceanpayment",
        "oney",
        "openpaymx",
        "optimal_payments",
        "orangepay",
        "other",
        "pacnet_services",
        "payeezy",
        "payfast",
        "paygate",
        "paylike",
        "payment_express",
        "paymentwall",
        "payone",
        "paypal",
        "payplus",
        "paysafecard",
        "paystation",
        "paytrace",
        "paytrail",
        "payture",
        "payu",
        "payulatam",
        "payway",
        "payza",
        "pinpayments",
        "posconnect",
        "princeton_payment_solutions",
        "psigate",
        "qiwi",
        "quickpay",
        "raberil",
        "rede",
        "redpagos",
        "rewardspay",
        "sagepay",
        "securetrading",
        "simplify_commerce",
        "skrill",
        "smartcoin",
        "smartdebit",
        "solidtrust_pay",
        "sps_decidir",
        "stripe",
        "synapsefi",
        "telerecargas",
        "towah",
        "transact_pro",
        "usa_epay",
        "vantiv",
        "verepay",
        "vericheck",
        "vindicia",
        "virtual_card_services",
        "vme",
        "vpos",
        "wirecard",
        "worldpay",
    ]
)

_single_char = Match("^[A-Za-z0-9]$")

_iin = Match("^[0-9]{6}$")

_credit_card_last_4 = Match("^[0-9]{4}$")


def _credit_card_token(s):
    if re.match("^[\x21-\x7E]{1,255}$", s) and not re.match("^[0-9]{1,19}$", s):
        return s
    raise ValueError


def _rfc3339_datetime(s):
    if validate_rfc3339(s):
        return s
    raise ValueError


_event_type = In(
    [
        "account_creation",
        "account_login",
        "email_change",
        "password_reset",
        "payout_change",
        "purchase",
        "recurring_purchase",
        "referral",
        "survey",
    ]
)

_currency_code = Match("^[A-Z]{3}$")

_price = All(_any_number, Range(min=0, min_included=False))


def _uri(s):
    if rfc3987.parse(s).get("scheme") in ["http", "https"]:
        return s
    raise ValueError


validate_transaction = Schema(
    {
        "account": {"user_id": _unicode_or_printable_ascii, "username_md5": _md5,},
        "billing": _address,
        "payment": {
            "processor": _payment_processor,
            "was_authorized": bool,
            "decline_code": _unicode_or_printable_ascii,
        },
        "credit_card": {
            "avs_result": _single_char,
            "bank_name": _unicode_or_printable_ascii,
            "bank_phone_country_code": _telephone_country_code,
            "bank_phone_number": _unicode_or_printable_ascii,
            "cvv_result": _single_char,
            "issuer_id_number": _iin,
            "last_4_digits": _credit_card_last_4,
            "token": _credit_card_token,
        },
        "custom_inputs": {_custom_input_key: _custom_input_value},
        Required("device"): {
            "accept_language": _unicode_or_printable_ascii,
            Required("ip_address"): _ip_address,
            "session_age": All(_any_number, Range(min=0)),
            "session_id": _unicode_or_printable_ascii,
            "user_agent": _unicode_or_printable_ascii,
        },
        "email": {"address": _email_or_md5, "domain": _hostname,},
        "event": {
            "shop_id": _unicode_or_printable_ascii,
            "time": _rfc3339_datetime,
            "type": _event_type,
            "transaction_id": _unicode_or_printable_ascii,
        },
        "order": {
            "affiliate_id": _unicode_or_printable_ascii,
            "amount": _price,
            "currency": _currency_code,
            "discount_code": _unicode_or_printable_ascii,
            "has_gift_message": bool,
            "is_gift": bool,
            "referrer_uri": _uri,
            "subaffiliate_id": _unicode_or_printable_ascii,
        },
        "shipping": _shipping_address,
        "shopping_cart": [
            {
                "category": _unicode_or_printable_ascii,
                "item_id": _unicode_or_printable_ascii,
                "price": _price,
                "quantity": All(int, Range(min=1)),
            },
        ],
    },
)
