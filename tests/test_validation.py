from decimal import Decimal
import sys
from voluptuous import MultipleInvalid

from minfraud.validation import validate_transaction

if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest

if sys.version_info[0] == 2:
    unittest.TestCase.assertRaisesRegex = unittest.TestCase.assertRaisesRegexp
    unittest.TestCase.assertRegex = unittest.TestCase.assertRegexpMatches


class ValidationBase(object):
    def setup_transaction(self, transaction):
        if 'device' not in transaction:
            transaction['device'] = {}

        if 'ip_address' not in transaction['device']:
            transaction['device']['ip_address'] = '1.1.1.1'

    def check_invalid_transaction(self, transaction):
        self.setup_transaction(transaction)
        with self.assertRaises(MultipleInvalid,
                               msg='{0!s} is invalid'.format(transaction)):
            validate_transaction(transaction)

    def check_transaction(self, transaction):
        self.setup_transaction(transaction)
        try:
            validate_transaction(transaction)
        except MultipleInvalid as e:
            self.fail('MultipleInvalid {0} thrown for {1}'.format(e.msg,
                                                                  transaction))

    def check_str_type(self, object, key):
        self.check_transaction({object: {key: 'string'}})
        self.check_invalid_transaction({object: {key: 12}})

    def check_positive_number(self, f):
        for good in (1, 1.1, Decimal('1.1')):
            self.check_transaction(f(good))
        for bad in ('1.2', '1', -1, -1.1, 0):
            self.check_invalid_transaction(f(bad))

    def check_bool(self, object, key):
        for good in (True, False):
            self.check_transaction({object: {key: good}})
        for bad in ('', 0, 'True'):
            self.check_invalid_transaction({object: {key: bad}})


class TestAccount(unittest.TestCase, ValidationBase):
    def test_account_user_id(self):
        self.check_transaction({'account': {'user_id': 'usr'}})

    def test_account_username_md5(self):
        self.check_transaction(
            {'account': {'username_md5': '14c4b06b824ec593239362517f538b29'}})

    def test_invalid_account_username_md5s(self):
        self.check_invalid_transaction(
            {'account': {'username_md5': '14c4b06b824ec593239362517f538b2'}})
        self.check_invalid_transaction({
            'account': {'username_md5': '14c4b06b824ec593239362517f538b29a'}
        })


class AddressBase(ValidationBase):
    def test_strings(self):
        for key in ('first_name', 'last_name', 'company', 'address',
                    'address_2', 'city', 'postal', 'phone_number'):
            self.check_str_type(self.type, key)

    def test_region(self):
        for region in ('A', 'AA', 'AAA', 'ZZZZ'):
            self.check_transaction({self.type: {'region': region}})
        for invalid in ('', 'AAAAA', 1, 'aaa'):
            self.check_invalid_transaction({self.type: {'region': invalid}})

    def test_country(self):
        for country in ('US', 'CA', 'GB'):
            self.check_transaction({self.type: {'country': country}})
        for invalid in ('', 'U1', 'USA', 1, '11', 'us'):
            self.check_invalid_transaction({self.type: {'country': invalid}})

    def test_phone_country_code(self):
        for code in (1, '1', '2341'):
            self.check_transaction({self.type: {'phone_country_code': code}})
        for invalid in ('', '12345', 'U'):
            self.check_invalid_transaction({self.type: {'phone_country_code':
                                                        invalid}})


class TestBillingAddress(unittest.TestCase, AddressBase):
    type = 'billing'


class TestShippingAddress(unittest.TestCase, AddressBase):
    type = 'shipping'

    def test_delivery_speed(self):
        for speed in ('same_day', 'overnight', 'expedited', 'standard'):
            self.check_transaction({self.type: {'delivery_speed': speed}})
        for invalid in ('fast', 'slow', ''):
            self.check_invalid_transaction({self.type: {'delivery_speed':
                                                        invalid}})


class TestCreditCard(ValidationBase, unittest.TestCase):
    def test_issuer_id_number(self):
        for iin in ('123456', '532313'):
            self.check_transaction({'credit_card': {'issuer_id_number': iin}})
        for invalid in ('12345', '1234567', 123456, '12345a'):
            self.check_invalid_transaction({'credit_card': {'issuer_id_number':
                                                            invalid}})

    def test_last_4_digits(self):
        for iin in ('1234', '9323'):
            self.check_transaction({'credit_card': {'last_4_digits': iin}})
        for invalid in ('12345', '123', 1234, '123a'):
            self.check_invalid_transaction({'credit_card': {'last_4_digits':
                                                            invalid}})

    def test_bank_name(self):
        self.check_str_type('credit_card', 'bank_name')

    def test_bank_phone_number(self):
        self.check_str_type('credit_card', 'bank_phone_number')

    def test_phone_country_code(self):
        for code in (1, '1', '2341'):
            self.check_transaction({'credit_card': {'bank_phone_country_code':
                                                    code}})
        for invalid in ('', '12345', 'U'):
            self.check_invalid_transaction(
                {'credit_card': {'bank_phone_country_code': invalid}})

    def test_avs_and_cvv(self):
        for key in ('avs_result', 'cvv_result'):
            for code in ('1', 'A'):
                self.check_transaction({'credit_card': {key: code}})
            for invalid in ('', '12'):
                self.check_invalid_transaction({'credit_card': {'credit_card':
                                                                invalid}})


class TestDevice(ValidationBase, unittest.TestCase):
    def test_ip_address(self):
        for ip in ('1.2.3.4', '2001:db8:0:0:1:0:0:1', '::FFFF:1.2.3.4'):
            self.check_transaction({'device': {'ip_address': ip}})
        for invalid in ('1.2.3.', '299.1.1.1', '::AF123'):
            self.check_invalid_transaction({'device': {'ip_address': invalid}})

    def test_missing_ip(self):
        with self.assertRaises(MultipleInvalid):
            validate_transaction({'device': {}})

    def test_missing_device(self):
        with self.assertRaises(MultipleInvalid):
            validate_transaction({})

    def test_user_agent(self):
        self.check_str_type('device', 'user_agent')

    def test_accept_language(self):
        self.check_str_type('device', 'accept_language')


class TestEmail(ValidationBase, unittest.TestCase):
    def test_address(self):
        for good in ('test@maxmind.com', '977577b140bfb7c516e4746204fbdb01'):
            self.check_transaction({'email': {'address': good}})
        for bad in ('not.email', '977577b140bfb7c516e4746204fbdb0',
                    '977577b140bfb7c516e4746204fbdb012'):
            self.check_invalid_transaction({'email': {'address': bad}})

    def test_domain(self):
        for good in ('maxmind.com', 'www.bbc.co.uk'):
            self.check_transaction({'email': {'domain': good}})
        for bad in ('bad ', ' bad.com'):
            self.check_invalid_transaction({'email': {'domain': bad}})


class TestEvent(ValidationBase, unittest.TestCase):
    def test_transaction(self):
        self.check_str_type('event', 'transaction_id')

    def test_shop_id(self):
        self.check_str_type('event', 'shop_id')

    def test_time(self):
        for good in ('2015-05-08T16:07:56+00:00', '2015-05-08T16:07:56Z'):
            self.check_transaction({'event': {'time': good}})
        for bad in ('2015-05-08T16:07:56', '2015-05-08 16:07:56Z'):
            self.check_invalid_transaction({'event': {'time': bad}})

    def test_type(self):
        for good in ('account_creation', 'account_login', 'purchase',
                     'recurring_purchase', 'referral', 'survey'):
            self.check_transaction({'event': {'type': good}})
        for bad in ('bad', 1, ''):
            self.check_invalid_transaction({'event': {'type': bad}})


class TestOrder(ValidationBase, unittest.TestCase):
    def test_amount(self):
        self.check_positive_number(lambda v: {'order': {'amount': v}})

    def test_currency(self):
        for good in ('USD', 'GBP'):
            self.check_transaction({'order': {'currency': good}})
        for bad in ('US', 'US1', 'USDD', 'usd'):
            self.check_invalid_transaction({'order': {'currency': bad}})

    def test_discount_code(self):
        self.check_str_type('order', 'discount_code')

    def test_affiliate_id(self):
        self.check_str_type('order', 'affiliate_id')

    def test_subaffiliate_id(self):
        self.check_str_type('order', 'subaffiliate_id')

    def test_is_gift(self):
        self.check_bool('order', 'is_gift')

    def test_has_gift_message(self):
        self.check_bool('order', 'has_gift_message')

    def test_referrer_uri(self):
        for good in ('http://www.mm.com/fadsf', 'https://x.org/'):
            self.check_transaction({'order': {'referrer_uri': good}})
        for bad in ('ftp://a.com/', 'www.mm.com'):
            self.check_invalid_transaction({'order': {'referrer_uri': bad}})


class TestPayment(ValidationBase, unittest.TestCase):
    def test_processor(self):
        for good in ('adyen', 'stripe'):
            self.check_transaction({'payment': {'processor': good}})
        for bad in ('notvalid', ' stripe'):
            self.check_invalid_transaction({'payment': {'processor': bad}})

    def test_was_authorized(self):
        self.check_bool('payment', 'was_authorized')

    def test_decline_code(self):
        self.check_str_type('payment', 'decline_code')


class TestShoppingCart(ValidationBase, unittest.TestCase):
    def test_category(self):
        self.check_transaction({'shopping_cart': [{'category': 'cat'}]})

    def test_item_id(self):
        self.check_transaction({'shopping_cart': [{'item_id': 'cat'}]})

    def test_amount(self):
        self.check_positive_number(lambda v: {'shopping_cart': [{'price': v}]})

    def test_quantity(self):
        for good in (1, 1000):
            self.check_transaction({'shopping_cart': [{'quantity': good}]})
        for bad in (1.1, -1, 0):
            self.check_invalid_transaction({'shopping_cart': [{'quantity': bad}
                                                              ]})
