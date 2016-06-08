import sys

from minfraud.models import *

if sys.version_info[:2] == (2, 6):
    import unittest2 as unittest
else:
    import unittest

if sys.version_info[0] == 2:
    unittest.TestCase.assertRaisesRegex = unittest.TestCase.assertRaisesRegexp
    unittest.TestCase.assertRegex = unittest.TestCase.assertRegexpMatches


class TestModels(unittest.TestCase):
    def test_model_immutability(self):
        """This tests some level of _shallow_ immutability for these classes"""
        T = namedtuple('T', ['obj', 'attr'], {})
        models = [T(GeoIP2Country(), 'iso_code'),
                  T(GeoIP2Location(), 'latitude'), T(Issuer(), 'name'),
                  T(CreditCard(), 'country'), T(Device(), 'id'),
                  T(Email(), 'is_free'), T(BillingAddress(), 'latitude'),
                  T(ShippingAddress(), 'latitude'),
                  T(ServiceWarning(), 'code'), T(Insights(), 'id'),
                  T(Score(), 'id'), T(
                      IPAddress({}), 'city')]
        for model in models:
            for attr in (model.attr, 'does_not_exist'):
                with self.assertRaises(
                        AttributeError,
                        msg='{0!s} - {0}'.format(model.obj, attr)):
                    setattr(model.obj, attr, 5)

    def test_billing_address(self):
        address = BillingAddress(self.address_dict)
        self.check_address(address)

    def test_shipping_address(self):
        address_dict = self.address_dict
        address_dict['is_high_risk'] = False
        address_dict['distance_to_billing_address'] = 200

        address = ShippingAddress(address_dict)
        self.check_address(address)
        self.assertEqual(False, address.is_high_risk)
        self.assertEqual(200, address.distance_to_billing_address)

    @property
    def address_dict(self):
        return {
            'is_in_ip_country': True,
            'latitude': 43.1,
            'longitude': 32.1,
            'distance_to_ip_location': 100,
            'is_postal_in_city': True
        }

    def check_address(self, address):
        self.assertEqual(True, address.is_in_ip_country)
        self.assertEqual(True, address.is_postal_in_city)
        self.assertEqual(100, address.distance_to_ip_location)
        self.assertEqual(32.1, address.longitude)
        self.assertEqual(43.1, address.latitude)

    def test_credit_card(self):
        cc = CreditCard({
            'issuer': {'name': 'Bank'},
            'brand': 'Visa',
            'country': 'US',
            'is_issued_in_billing_address_country': True,
            'is_prepaid': True,
            'type': 'credit'
        })

        self.assertEqual('Bank', cc.issuer.name)
        self.assertEqual('Visa', cc.brand)
        self.assertEqual('US', cc.country)
        self.assertEqual(True, cc.is_prepaid)
        self.assertEqual(True, cc.is_issued_in_billing_address_country)
        self.assertEqual('credit', cc.type)

    def test_device(self):
        id = 'b643d445-18b2-4b9d-bad4-c9c4366e402a'
        last_seen = '2016-06-08T14:16:38Z'
        device = Device({'confidence': 99, 'id': id, 'last_seen': last_seen})

        self.assertEqual(99, device.confidence)
        self.assertEqual(id, device.id)
        self.assertEqual(last_seen, device.last_seen)

    def test_email(self):
        email = Email({'is_free': True, 'is_high_risk': False})

        self.assertEqual(True, email.is_free)
        self.assertEqual(False, email.is_high_risk)

    def test_geoip2_country(self):
        country = GeoIP2Country(is_high_risk=True, iso_code='US')
        self.assertEqual(True, country.is_high_risk)
        self.assertEqual('US', country.iso_code)

    def test_geoip2_location(self):
        time = "2015-04-19T12:59:23-01:00"
        location = GeoIP2Location(local_time=time, latitude=5)
        self.assertEqual(time, location.local_time)
        self.assertEqual(5, location.latitude)

    def test_ip_address(self):
        time = "2015-04-19T12:59:23-01:00"
        address = IPAddress({
            'country': {'is_high_risk': True},
            'location': {'local_time': time},
            'risk': 99,
        })

        self.assertEqual(time, address.location.local_time)
        self.assertEqual(True, address.country.is_high_risk)
        self.assertEqual(99, address.risk)

    def test_score_ip_address(self):
        address = ScoreIPAddress({'risk': 99})
        self.assertEqual(99, address.risk)

    def test_ip_address_locales(self):

        loc = IPAddress({
            '_locales': ['fr'],
            'country': {'names': {'fr': 'Country'}},
            'city': {'names': {'fr': 'City'}},
        })

        self.assertEqual('City', loc.city.name)
        self.assertEqual('Country', loc.country.name)

    def test_issuer(self):
        phone = '132-342-2131'

        issuer = Issuer({
            'name': 'Bank',
            'matches_provided_name': True,
            'phone_number': phone,
            'matches_provided_phone_number': True
        })

        self.assertEqual('Bank', issuer.name)
        self.assertEqual(True, issuer.matches_provided_name)
        self.assertEqual(phone, issuer.phone_number)
        self.assertEqual(True, issuer.matches_provided_phone_number)

    def test_warning(self):
        code = 'INVALID_INPUT'
        msg = 'Input invalid'

        warning = ServiceWarning({'code': code,
                                  'warning': msg,
                                  'input_pointer': "/first/second"})

        self.assertEqual(code, warning.code)
        self.assertEqual(msg, warning.warning)
        self.assertEqual('/first/second', warning.input_pointer)

    def test_score(self):
        id = 'b643d445-18b2-4b9d-bad4-c9c4366e402a'
        score = Score({
            'id': id,
            'funds_remaining': 10.01,
            'queries_remaining': 123,
            'risk_score': 0.01,
            'ip_address': {'risk': 99},
            'warnings': [{'code': 'INVALID_INPUT'}],
        })

        self.assertEqual(id, score.id)
        self.assertEqual(10.01, score.funds_remaining)
        self.assertEqual(123, score.queries_remaining)
        self.assertEqual(0.01, score.risk_score)
        self.assertEqual('INVALID_INPUT', score.warnings[0].code)
        self.assertEqual(99, score.ip_address.risk)

    def test_insights(self):
        response = self.factors_response()
        del response['subscores']
        insights = Insights(response)
        self.check_insights_data(insights, response['id'])

    def test_factors(self):
        response = self.factors_response()
        factors = Factors(response)
        self.check_insights_data(factors, response['id'])
        self.assertEqual(0.01, factors.subscores.avs_result)
        self.assertEqual(0.02, factors.subscores.billing_address)
        self.assertEqual(
            0.03, factors.subscores.billing_address_distance_to_ip_location)
        self.assertEqual(0.04, factors.subscores.browser)
        self.assertEqual(0.05, factors.subscores.chargeback)
        self.assertEqual(0.06, factors.subscores.country)
        self.assertEqual(0.07, factors.subscores.country_mismatch)
        self.assertEqual(0.08, factors.subscores.cvv_result)
        self.assertEqual(0.09, factors.subscores.email_address)
        self.assertEqual(0.10, factors.subscores.email_domain)
        self.assertEqual(0.11, factors.subscores.email_tenure)
        self.assertEqual(0.12, factors.subscores.ip_tenure)
        self.assertEqual(0.13, factors.subscores.issuer_id_number)
        self.assertEqual(0.14, factors.subscores.order_amount)
        self.assertEqual(0.15, factors.subscores.phone_number)
        self.assertEqual(
            0.16, factors.subscores.shipping_address_distance_to_ip_location)
        self.assertEqual(0.17, factors.subscores.time_of_day)

    def factors_response(self):
        return {
            'id': "b643d445-18b2-4b9d-bad4-c9c4366e402a",
            'ip_address': {'country': {'iso_code': 'US'}},
            'credit_card': {
                'is_prepaid': True,
                'brand': 'Visa',
                'type': 'debit'
            },
            'device': {'id': "b643d445-18b2-4b9d-bad4-c9c4366e402a"},
            'email': {'is_free': True},
            'shipping_address': {'is_in_ip_country': True},
            'billing_address': {'is_in_ip_country': True},
            'funds_remaining': 10.01,
            'queries_remaining': 123,
            'risk_score': 0.01,
            'subscores': {
                'avs_result': 0.01,
                'billing_address': 0.02,
                'billing_address_distance_to_ip_location': 0.03,
                'browser': 0.04,
                'chargeback': 0.05,
                'country': 0.06,
                'country_mismatch': 0.07,
                'cvv_result': 0.08,
                'email_address': 0.09,
                'email_domain': 0.10,
                'email_tenure': 0.11,
                'ip_tenure': 0.12,
                'issuer_id_number': 0.13,
                'order_amount': 0.14,
                'phone_number': 0.15,
                'shipping_address_distance_to_ip_location': 0.16,
                'time_of_day': 0.17,
            },
            'warnings': [{"code": "INVALID_INPUT"}]
        }

    def check_insights_data(self, insights, uuid):
        self.assertEqual('US', insights.ip_address.country.iso_code)
        self.assertEqual(True, insights.credit_card.is_prepaid)
        self.assertEqual('Visa', insights.credit_card.brand)
        self.assertEqual('debit', insights.credit_card.type)
        self.assertEqual(uuid, insights.device.id)
        self.assertEqual(True, insights.email.is_free)
        self.assertEqual(True, insights.shipping_address.is_in_ip_country)
        self.assertEqual(True, insights.billing_address.is_in_ip_country)
        self.assertEqual(uuid, insights.id)
        self.assertEqual(10.01, insights.funds_remaining)
        self.assertEqual(123, insights.queries_remaining)
        self.assertEqual(0.01, insights.risk_score)
        self.assertEqual("INVALID_INPUT", insights.warnings[0].code)
        self.assertIsInstance(insights.warnings, tuple,
                              'warnings is a tuple, not a dict')
