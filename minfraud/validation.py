"""This is an internal module used for validating the minFraud request.

Internal code for validating the transaction dictionary.

This code is only intended for internal use and is subject to change in ways
that may break any direct use of it.

"""


import ipaddress
import re
import uuid
import urllib.parse
from decimal import Decimal
from typing import Optional

from email_validator import validate_email  # type: ignore
from voluptuous import All, Any, In, Match, Range, Required, Schema
from voluptuous.error import UrlInvalid

# Pylint doesn't like the private function type naming for the callable
# objects below. Given the consistent use of them, the current names seem
# preferable to blindly following pylint.
#
# pylint: disable=invalid-name,undefined-variable

_any_number = Any(float, int, Decimal)

_custom_input_key = All(str, Match(r"^[a-z0-9_]{1,25}$"))

_custom_input_value = Any(
    All(str, Match(r"^[^\n]{1,255}\Z")),
    All(
        _any_number, Range(min=-1e13, max=1e13, min_included=False, max_included=False)
    ),
    bool,
)

_md5 = All(str, Match(r"^[0-9A-Fa-f]{32}$"))

_country_code = All(str, Match(r"^[A-Z]{2}$"))

_telephone_country_code = Any(
    All(str, Match("^[0-9]{1,4}$")), All(int, Range(min=1, max=9999))
)

_subdivision_iso_code = All(str, Match(r"^[0-9A-Z]{1,4}$"))


def _ip_address(s: Optional[str]) -> str:
    # ipaddress accepts numeric IPs, which we don't want.
    if isinstance(s, str) and not re.match(r"^\d+$", s):
        return str(ipaddress.ip_address(s))
    raise ValueError


def _email_or_md5(s: str) -> str:
    if re.match(r"^[0-9A-Fa-f]{32}$", s):
        return s
    return validate_email(s, check_deliverability=False).email


# based off of:
# http://stackoverflow.com/questions/2532053/validate-a-hostname-string
def _hostname(hostname: str) -> str:
    if len(hostname) > 255:
        raise ValueError
    allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    if all(allowed.match(x) for x in hostname.split(".")):
        return hostname
    raise ValueError


_delivery_speed = In(["same_day", "overnight", "expedited", "standard"])

_address = {
    "address": str,
    "address_2": str,
    "city": str,
    "company": str,
    "country": _country_code,
    "first_name": str,
    "last_name": str,
    "phone_country_code": _telephone_country_code,
    "phone_number": str,
    "postal": str,
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
        "cashfree",
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
        "first_atlantic_commerce",
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
        "komoju",
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
        "paytm",
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
        "razorpay",
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
        "systempay",
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


def _credit_card_token(s: str) -> str:
    if re.match("^[\x21-\x7E]{1,255}$", s) and not re.match("^[0-9]{1,19}$", s):
        return s
    raise ValueError


_rfc3339_datetime = Match(
    r"(?a)\A\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})\Z"
)


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


def _uri(s: str) -> str:
    parsed = urllib.parse.urlparse(s)
    if parsed.scheme not in ["http", "https"] or not parsed.netloc:
        raise UrlInvalid("URL is invalid")
    return s


validate_transaction = Schema(
    {
        "account": {"user_id": str, "username_md5": _md5,},
        "billing": _address,
        "payment": {
            "processor": _payment_processor,
            "was_authorized": bool,
            "decline_code": str,
        },
        "credit_card": {
            "avs_result": _single_char,
            "bank_name": str,
            "bank_phone_country_code": _telephone_country_code,
            "bank_phone_number": str,
            "cvv_result": _single_char,
            "issuer_id_number": _iin,
            "last_4_digits": _credit_card_last_4,
            "token": _credit_card_token,
        },
        "custom_inputs": {_custom_input_key: _custom_input_value},
        Required("device"): {
            "accept_language": str,
            Required("ip_address"): _ip_address,
            "session_age": All(_any_number, Range(min=0)),
            "session_id": str,
            "user_agent": str,
        },
        "email": {"address": _email_or_md5, "domain": _hostname,},
        "event": {
            "shop_id": str,
            "time": _rfc3339_datetime,
            "type": _event_type,
            "transaction_id": str,
        },
        "order": {
            "affiliate_id": str,
            "amount": _price,
            "currency": _currency_code,
            "discount_code": str,
            "has_gift_message": bool,
            "is_gift": bool,
            "referrer_uri": _uri,
            "subaffiliate_id": str,
        },
        "shipping": _shipping_address,
        "shopping_cart": [
            {
                "category": str,
                "item_id": str,
                "price": _price,
                "quantity": All(int, Range(min=1)),
            },
        ],
    },
)


def _maxmind_id(s: Optional[str]) -> str:
    if isinstance(s, str) and len(s) == 8:
        return s
    raise ValueError


_tag = In(["chargeback", "not_fraud", "spam_or_abuse", "suspected_fraud"])


def _uuid(s: str) -> str:
    if isinstance(s, uuid.UUID):
        return str(s)
    if isinstance(s, str):
        return str(uuid.UUID(s))
    raise ValueError


validate_report = Schema(
    {
        "chargeback_code": str,
        Required("ip_address"): _ip_address,
        "maxmind_id": _maxmind_id,
        "minfraud_id": _uuid,
        "notes": str,
        Required("tag"): _tag,
        "transaction_id": str,
    },
)
