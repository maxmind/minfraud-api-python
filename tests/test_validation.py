from decimal import Decimal
from voluptuous import MultipleInvalid

from minfraud.validation import validate_transaction, validate_report

import unittest


class ValidationBase:
    def setup_transaction(self, transaction):
        if "device" not in transaction:
            transaction["device"] = {}

        if "ip_address" not in transaction["device"]:
            transaction["device"]["ip_address"] = "1.1.1.1"

    def check_invalid_transaction(self, transaction):
        self.setup_transaction(transaction)
        with self.assertRaises(
            MultipleInvalid, msg="{0!s} is invalid".format(transaction)
        ):
            validate_transaction(transaction)

    def check_transaction(self, transaction):
        self.setup_transaction(transaction)
        try:
            validate_transaction(transaction)
        except MultipleInvalid as e:
            self.fail("MultipleInvalid {0} thrown for {1}".format(e.msg, transaction))

    def check_transaction_str_type(self, object, key):
        self.check_transaction({object: {key: "string"}})
        self.check_invalid_transaction({object: {key: 12}})

    def check_positive_number(self, f):
        for good in (1, 1.1, Decimal("1.1")):
            self.check_transaction(f(good))
        for bad in ("1.2", "1", -1, -1.1, 0):
            self.check_invalid_transaction(f(bad))

    def check_bool(self, object, key):
        for good in (True, False):
            self.check_transaction({object: {key: good}})
        for bad in ("", 0, "True"):
            self.check_invalid_transaction({object: {key: bad}})

    def setup_report(self, report):
        if "ip_address" not in report:
            report["ip_address"] = "1.2.3.4"

        if "tag" not in report:
            report["tag"] = "chargeback"

    def check_invalid_report(self, report):
        self.setup_report(report)
        with self.assertRaises(MultipleInvalid, msg="{0!s} is invalid".format(report)):
            validate_report(report)

    def check_report(self, report):
        self.setup_report(report)
        try:
            validate_report(report)
        except MultipleInvalid as e:
            self.fail("MultipleInvalid {0} thrown for {1}".format(e.msg, report))

    def check_report_str_type(self, key):
        self.check_report({key: "string"})
        self.check_invalid_report({key: 12})


class TestAccount(unittest.TestCase, ValidationBase):
    def test_account_user_id(self):
        self.check_transaction({"account": {"user_id": "usr"}})

    def test_account_username_md5(self):
        self.check_transaction(
            {"account": {"username_md5": "14c4b06b824ec593239362517f538b29"}}
        )

    def test_invalid_account_username_md5s(self):
        self.check_invalid_transaction(
            {"account": {"username_md5": "14c4b06b824ec593239362517f538b2"}}
        )
        self.check_invalid_transaction(
            {"account": {"username_md5": "14c4b06b824ec593239362517f538b29a"}}
        )


class AddressBase(ValidationBase):
    def test_strings(self):
        for key in (
            "first_name",
            "last_name",
            "company",
            "address",
            "address_2",
            "city",
            "postal",
            "phone_number",
        ):
            self.check_transaction_str_type(self.type, key)

    def test_region(self):
        for region in ("A", "AA", "AAA", "ZZZZ"):
            self.check_transaction({self.type: {"region": region}})
        for invalid in ("", "AAAAA", 1, "aaa"):
            self.check_invalid_transaction({self.type: {"region": invalid}})

    def test_country(self):
        for country in ("US", "CA", "GB"):
            self.check_transaction({self.type: {"country": country}})
        for invalid in ("", "U1", "USA", 1, "11", "us"):
            self.check_invalid_transaction({self.type: {"country": invalid}})

    def test_phone_country_code(self):
        for code in (1, "1", "2341"):
            self.check_transaction({self.type: {"phone_country_code": code}})
        for invalid in ("", "12345", "U"):
            self.check_invalid_transaction({self.type: {"phone_country_code": invalid}})


class TestBillingAddress(unittest.TestCase, AddressBase):
    type = "billing"


class TestShippingAddress(unittest.TestCase, AddressBase):
    type = "shipping"

    def test_delivery_speed(self):
        for speed in ("same_day", "overnight", "expedited", "standard"):
            self.check_transaction({self.type: {"delivery_speed": speed}})
        for invalid in ("fast", "slow", ""):
            self.check_invalid_transaction({self.type: {"delivery_speed": invalid}})


class TestCreditCard(ValidationBase, unittest.TestCase):
    def test_issuer_id_number(self):
        for iin in ("123456", "532313"):
            self.check_transaction({"credit_card": {"issuer_id_number": iin}})
        for invalid in ("12345", "1234567", 123456, "12345a"):
            self.check_invalid_transaction(
                {"credit_card": {"issuer_id_number": invalid}}
            )

    def test_last_4_digits(self):
        for iin in ("1234", "9323"):
            self.check_transaction({"credit_card": {"last_4_digits": iin}})
        for invalid in ("12345", "123", 1234, "123a"):
            self.check_invalid_transaction({"credit_card": {"last_4_digits": invalid}})

    def test_bank_name(self):
        self.check_transaction_str_type("credit_card", "bank_name")

    def test_bank_phone_number(self):
        self.check_transaction_str_type("credit_card", "bank_phone_number")

    def test_phone_country_code(self):
        for code in (1, "1", "2341"):
            self.check_transaction({"credit_card": {"bank_phone_country_code": code}})
        for invalid in ("", "12345", "U"):
            self.check_invalid_transaction(
                {"credit_card": {"bank_phone_country_code": invalid}}
            )

    def test_avs_and_cvv(self):
        for key in ("avs_result", "cvv_result"):
            for code in ("1", "A"):
                self.check_transaction({"credit_card": {key: code}})
            for invalid in ("", "12"):
                self.check_invalid_transaction(
                    {"credit_card": {"credit_card": invalid}}
                )

    def test_token(self):
        for token in ("123456abc1245", "\x21", "1" * 20):
            self.check_transaction({"credit_card": {"token": token}})
        for invalid in ("\x20", "123456", "x" * 256):
            self.check_invalid_transaction({"credit_card": {"token": invalid}})


class TestCustomInputs(ValidationBase, unittest.TestCase):
    def test_valid_inputs(self):
        self.check_transaction(
            {
                "custom_inputs": {
                    "string_input_1": "test string",
                    "int_input": 19,
                    "float_input": 3.2,
                    "bool_input": True,
                }
            }
        )

    def test_invalid(self):
        for invalid in (
            {"InvalidKey": 1},
            {"too_long": "x" * 256},
            {"has_newline": "test\n"},
            {"too_big": 1e13},
            {"too_small": -1e13},
            {"too_big_float": float(1e13)},
        ):
            self.check_invalid_transaction({"custom_inputs": invalid})


class TestDevice(ValidationBase, unittest.TestCase):
    def test_ip_address(self):
        for ip in ("1.2.3.4", "2001:db8:0:0:1:0:0:1", "::FFFF:1.2.3.4"):
            self.check_transaction({"device": {"ip_address": ip}})
        for invalid in ("1.2.3.", "299.1.1.1", "::AF123"):
            self.check_invalid_transaction({"device": {"ip_address": invalid}})

    def test_missing_ip(self):
        with self.assertRaises(MultipleInvalid):
            validate_transaction({"device": {}})

    def test_missing_device(self):
        with self.assertRaises(MultipleInvalid):
            validate_transaction({})

    def test_user_agent(self):
        self.check_transaction_str_type("device", "user_agent")

    def test_accept_language(self):
        self.check_transaction_str_type("device", "accept_language")

    def test_session_id(self):
        self.check_transaction_str_type("device", "session_id")

    def test_session_age(self):
        for valid in (3600, 0, 25.5):
            self.check_transaction(
                {"device": {"ip_address": "4.4.4.4", "session_age": valid}}
            )
        for invalid in ("foo", -1):
            self.check_invalid_transaction(
                {"device": {"ip_address": "4.4.4.4", "session_age": invalid}}
            )


class TestEmail(ValidationBase, unittest.TestCase):
    def test_address(self):
        for good in ("test@maxmind.com", "977577b140bfb7c516e4746204fbdb01"):
            self.check_transaction({"email": {"address": good}})
        for bad in (
            "not.email",
            "977577b140bfb7c516e4746204fbdb0",
            "977577b140bfb7c516e4746204fbdb012",
        ):
            self.check_invalid_transaction({"email": {"address": bad}})

    def test_domain(self):
        for good in ("maxmind.com", "www.bbc.co.uk"):
            self.check_transaction({"email": {"domain": good}})
        for bad in ("bad ", " bad.com"):
            self.check_invalid_transaction({"email": {"domain": bad}})


class TestEvent(ValidationBase, unittest.TestCase):
    def test_transaction(self):
        self.check_transaction_str_type("event", "transaction_id")

    def test_shop_id(self):
        self.check_transaction_str_type("event", "shop_id")

    def test_time(self):
        for good in ("2015-05-08T16:07:56+00:00", "2015-05-08T16:07:56Z"):
            self.check_transaction({"event": {"time": good}})
        for bad in ("2015-05-08T16:07:56", "2015-05-08 16:07:56Z"):
            self.check_invalid_transaction({"event": {"time": bad}})

    def test_type(self):
        for good in (
            "account_creation",
            "account_login",
            "email_change",
            "password_reset",
            "payout_change",
            "purchase",
            "recurring_purchase",
            "referral",
            "survey",
        ):
            self.check_transaction({"event": {"type": good}})
        for bad in ("bad", 1, ""):
            self.check_invalid_transaction({"event": {"type": bad}})


class TestOrder(ValidationBase, unittest.TestCase):
    def test_amount(self):
        self.check_positive_number(lambda v: {"order": {"amount": v}})

    def test_currency(self):
        for good in ("USD", "GBP"):
            self.check_transaction({"order": {"currency": good}})
        for bad in ("US", "US1", "USDD", "usd"):
            self.check_invalid_transaction({"order": {"currency": bad}})

    def test_discount_code(self):
        self.check_transaction_str_type("order", "discount_code")

    def test_affiliate_id(self):
        self.check_transaction_str_type("order", "affiliate_id")

    def test_subaffiliate_id(self):
        self.check_transaction_str_type("order", "subaffiliate_id")

    def test_is_gift(self):
        self.check_bool("order", "is_gift")

    def test_has_gift_message(self):
        self.check_bool("order", "has_gift_message")

    def test_referrer_uri(self):
        for good in ("http://www.mm.com/fadsf", "https://x.org/"):
            self.check_transaction({"order": {"referrer_uri": good}})
        for bad in ("ftp://a.com/", "www.mm.com"):
            self.check_invalid_transaction({"order": {"referrer_uri": bad}})


class TestPayment(ValidationBase, unittest.TestCase):
    def test_processor(self):
        for good in ("adyen", "stripe"):
            self.check_transaction({"payment": {"processor": good}})
        for bad in ("notvalid", " stripe"):
            self.check_invalid_transaction({"payment": {"processor": bad}})

    def test_was_authorized(self):
        self.check_bool("payment", "was_authorized")

    def test_decline_code(self):
        self.check_transaction_str_type("payment", "decline_code")


class TestShoppingCart(ValidationBase, unittest.TestCase):
    def test_category(self):
        self.check_transaction({"shopping_cart": [{"category": "cat"}]})

    def test_item_id(self):
        self.check_transaction({"shopping_cart": [{"item_id": "cat"}]})

    def test_amount(self):
        self.check_positive_number(lambda v: {"shopping_cart": [{"price": v}]})

    def test_quantity(self):
        for good in (1, 1000):
            self.check_transaction({"shopping_cart": [{"quantity": good}]})
        for bad in (1.1, -1, 0):
            self.check_invalid_transaction({"shopping_cart": [{"quantity": bad}]})


class TestReport(unittest.TestCase, ValidationBase):
    def test_ip_address(self):
        for good in ("182.193.2.1", "a74:777f:3acd:57a0:4e7e:e999:7fe6:1b5b"):
            self.check_report({"ip_address": good})
        for bad in ("1.2.3.", "299.1.1.1", "::AF123", "", None):
            self.check_invalid_report({"ip_address": bad})

    def test_maxmind_id(self):
        for good in ("12345678", "abcdefgh"):
            self.check_report({"maxmind_id": good})
        for bad in ("1234567", "123456789", "", None):
            self.check_invalid_report({"maxmind_id": bad})

    def test_minfraud_id(self):
        for good in (
            "12345678-1234-1234-1234-123456789012",
            "1234-5678-1234-1234-1234-1234-5678-9012",
            "12345678901234567890123456789012",
        ):
            self.check_report({"minfraud_id": good})
        for bad in (
            "1234567812341234123412345678901",
            "12345678-123412341234-12345678901",
            "12345678-1234-1234-1234-1234567890123",
            "12345678-1234-1234-1234-12345678901g",
            "",
        ):
            self.check_invalid_report({"minfraud_id": bad})

    def test_strings(self):
        for key in (
            "chargeback_code",
            "notes",
            "transaction_id",
        ):
            self.check_report_str_type(key)

    def test_tag(self):
        for good in ("chargeback", "not_fraud", "spam_or_abuse", "suspected_fraud"):
            self.check_report({"tag": good})
        for bad in ("risky_business", "", None):
            self.check_invalid_report({"tag": bad})
