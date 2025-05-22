from __future__ import annotations

import unittest
from typing import Any

from minfraud.models import (
    BillingAddress,
    CreditCard,
    Device,
    Disposition,
    Email,
    EmailDomain,
    Factors,
    GeoIP2Location,
    Insights,
    IPAddress,
    Issuer,
    Phone,
    Reason,
    RiskScoreReason,
    Score,
    ScoreIPAddress,
    ServiceWarning,
    ShippingAddress,
)


class TestModels(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = 20_000

    def test_billing_address(self) -> None:
        address = BillingAddress(**self.address_dict)  # type: ignore[arg-type]
        self.check_address(address)

    def test_shipping_address(self) -> None:
        address_dict = self.address_dict
        address_dict["is_high_risk"] = False
        address_dict["distance_to_billing_address"] = 200

        address = ShippingAddress(**address_dict)  # type:ignore[arg-type]
        self.check_address(address)
        self.assertEqual(False, address.is_high_risk)
        self.assertEqual(200, address.distance_to_billing_address)

    @property
    def address_dict(self) -> dict[str, bool | float]:
        return {
            "is_in_ip_country": True,
            "latitude": 43.1,
            "longitude": 32.1,
            "distance_to_ip_location": 100,
            "is_postal_in_city": True,
        }

    def check_address(self, address: BillingAddress | ShippingAddress) -> None:
        self.assertEqual(True, address.is_in_ip_country)
        self.assertEqual(True, address.is_postal_in_city)
        self.assertEqual(100, address.distance_to_ip_location)
        self.assertEqual(32.1, address.longitude)
        self.assertEqual(43.1, address.latitude)

    def test_credit_card(self) -> None:
        cc = CreditCard(
            issuer={"name": "Bank"},
            brand="Visa",
            country="US",
            is_issued_in_billing_address_country=True,
            is_business=True,
            is_prepaid=True,
            is_virtual=True,
            type="credit",
        )

        self.assertEqual("Bank", cc.issuer.name)
        self.assertEqual("Visa", cc.brand)
        self.assertEqual("US", cc.country)
        self.assertEqual(True, cc.is_business)
        self.assertEqual(True, cc.is_prepaid)
        self.assertEqual(True, cc.is_virtual)
        self.assertEqual(True, cc.is_issued_in_billing_address_country)
        self.assertEqual("credit", cc.type)

    def test_device(self) -> None:
        id = "b643d445-18b2-4b9d-bad4-c9c4366e402a"
        last_seen = "2016-06-08T14:16:38Z"
        local_time = "2016-06-10T14:19:10-08:00"
        device = Device(
            confidence=99,
            id=id,
            last_seen=last_seen,
            local_time=local_time,
        )

        self.assertEqual(99, device.confidence)
        self.assertEqual(id, device.id)
        self.assertEqual(last_seen, device.last_seen)
        self.assertEqual(local_time, device.local_time)

    def test_disposition(self) -> None:
        disposition = Disposition(
            action="accept",
            reason="default",
            rule_label="custom rule label",
        )

        self.assertEqual("accept", disposition.action)
        self.assertEqual("default", disposition.reason)
        self.assertEqual("custom rule label", disposition.rule_label)

    def test_email(self) -> None:
        first_seen = "2016-01-01"
        email = Email(
            first_seen=first_seen,
            is_disposable=True,
            is_free=True,
            is_high_risk=False,
        )

        self.assertEqual(first_seen, email.first_seen)
        self.assertEqual(True, email.is_disposable)
        self.assertEqual(True, email.is_free)
        self.assertEqual(False, email.is_high_risk)

    def test_email_domain(self) -> None:
        first_seen = "2016-01-01"
        domain = EmailDomain(
            first_seen=first_seen,
        )

        self.assertEqual(first_seen, domain.first_seen)

    def test_geoip2_location(self) -> None:
        time = "2015-04-19T12:59:23-01:00"
        location = GeoIP2Location(local_time=time, latitude=5)
        self.assertEqual(time, location.local_time)
        self.assertEqual(5, location.latitude)

    def test_ip_address(self) -> None:
        time = "2015-04-19T12:59:23-01:00"
        address = IPAddress(
            ["en"],
            country={
                "is_in_european_union": True,
            },
            location={
                "local_time": time,
            },
            risk=99,
            risk_reasons=[
                {
                    "code": "ANONYMOUS_IP",
                    "reason": "The IP address belongs to an anonymous network. "
                    "See /ip_address/traits for more details.",
                },
                {
                    "code": "MINFRAUD_NETWORK_ACTIVITY",
                    "reason": "Suspicious activity has been seen on this IP address "
                    "across minFraud customers.",
                },
            ],
            traits={
                "is_anonymous": True,
                "is_anonymous_proxy": True,
                "is_anonymous_vpn": True,
                "is_hosting_provider": True,
                "is_public_proxy": True,
                "is_residential_proxy": True,
                "is_satellite_provider": True,
                "is_tor_exit_node": True,
                "mobile_country_code": "310",
                "mobile_network_code": "004",
            },
        )

        self.assertEqual(time, address.location.local_time)
        self.assertEqual(True, address.country.is_in_european_union)
        self.assertEqual(99, address.risk)
        self.assertEqual(True, address.traits.is_anonymous)
        self.assertEqual(True, address.traits.is_anonymous_proxy)
        self.assertEqual(True, address.traits.is_anonymous_vpn)
        self.assertEqual(True, address.traits.is_hosting_provider)
        self.assertEqual(True, address.traits.is_public_proxy)
        self.assertEqual(True, address.traits.is_residential_proxy)
        self.assertEqual(True, address.traits.is_satellite_provider)
        self.assertEqual(True, address.traits.is_tor_exit_node)
        self.assertEqual("310", address.traits.mobile_country_code)
        self.assertEqual("004", address.traits.mobile_network_code)

        self.assertEqual("ANONYMOUS_IP", address.risk_reasons[0].code)
        self.assertEqual(
            "The IP address belongs to an anonymous network. "
            "See /ip_address/traits for more details.",
            address.risk_reasons[0].reason,
        )

        self.assertEqual("MINFRAUD_NETWORK_ACTIVITY", address.risk_reasons[1].code)
        self.assertEqual(
            "Suspicious activity has been seen on this IP address "
            "across minFraud customers.",
            address.risk_reasons[1].reason,
        )

    def test_empty_address(self) -> None:
        address = IPAddress([])
        self.assertEqual([], address.risk_reasons)

    def test_score_ip_address(self) -> None:
        address = ScoreIPAddress(risk=99)
        self.assertEqual(99, address.risk)

    def test_ip_address_locales(self) -> None:
        loc = IPAddress(
            ["fr"],
            country={"names": {"fr": "Country"}},
            city={"names": {"fr": "City"}},
        )

        self.assertEqual("City", loc.city.name)
        self.assertEqual("Country", loc.country.name)

    def test_issuer(self) -> None:
        phone = "132-342-2131"

        issuer = Issuer(
            name="Bank",
            matches_provided_name=True,
            phone_number=phone,
            matches_provided_phone_number=True,
        )

        self.assertEqual("Bank", issuer.name)
        self.assertEqual(True, issuer.matches_provided_name)
        self.assertEqual(phone, issuer.phone_number)
        self.assertEqual(True, issuer.matches_provided_phone_number)

    def test_phone(self) -> None:
        phone = Phone(
            country="US",
            is_voip=True,
            matches_postal=True,
            network_operator="Verizon/1",
            number_type="fixed",
        )

        self.assertEqual("US", phone.country)
        self.assertEqual(True, phone.is_voip)
        self.assertEqual(True, phone.matches_postal)
        self.assertEqual("Verizon/1", phone.network_operator)
        self.assertEqual("fixed", phone.number_type)

    def test_warning(self) -> None:
        code = "INVALID_INPUT"
        msg = "Input invalid"

        warning = ServiceWarning(code=code, warning=msg, input_pointer="/first/second")

        self.assertEqual(code, warning.code)
        self.assertEqual(msg, warning.warning)
        self.assertEqual("/first/second", warning.input_pointer)

    def test_reason(self) -> None:
        code = "EMAIL_ADDRESS_NEW"
        msg = "Riskiness of newly-sighted email address"

        reason = Reason(code=code, reason=msg)

        self.assertEqual(code, reason.code)
        self.assertEqual(msg, reason.reason)

    def test_risk_score_reason(self) -> None:
        multiplier = 0.34
        code = "EMAIL_ADDRESS_NEW"
        msg = "Riskiness of newly-sighted email address"

        reason = RiskScoreReason(
            multiplier=0.34,
            reasons=[{"code": code, "reason": msg}],
        )

        self.assertEqual(multiplier, reason.multiplier)
        self.assertEqual(code, reason.reasons[0].code)
        self.assertEqual(msg, reason.reasons[0].reason)

    def test_score(self) -> None:
        id = "b643d445-18b2-4b9d-bad4-c9c4366e402a"
        response = {
            "id": id,
            "funds_remaining": 10.01,
            "queries_remaining": 123,
            "risk_score": 0.01,
            "ip_address": {"risk": 99},
            "warnings": [{"code": "INVALID_INPUT"}],
        }
        score = Score(**response)  # type: ignore[arg-type]

        self.assertEqual(id, score.id)
        self.assertEqual(10.01, score.funds_remaining)
        self.assertEqual(123, score.queries_remaining)
        self.assertEqual(0.01, score.risk_score)
        self.assertEqual("INVALID_INPUT", score.warnings[0].code)
        self.assertEqual(99, score.ip_address.risk)

        self.assertEqual(response, score.to_dict())

    def test_insights(self) -> None:
        response = self.factors_response()
        del response["risk_score_reasons"]
        del response["subscores"]
        insights = Insights(None, **response)  # type: ignore[arg-type]
        self.check_insights_data(insights, response["id"])
        self.assertEqual(response, insights.to_dict())

    def test_factors(self) -> None:
        response = self.factors_response()
        factors = Factors(None, **response)  # type: ignore[arg-type]
        self.check_insights_data(factors, response["id"])
        self.check_risk_score_reasons_data(factors.risk_score_reasons)
        self.assertEqual(0.01, factors.subscores.avs_result)
        self.assertEqual(0.02, factors.subscores.billing_address)
        self.assertEqual(
            0.03,
            factors.subscores.billing_address_distance_to_ip_location,
        )
        self.assertEqual(0.04, factors.subscores.browser)
        self.assertEqual(0.05, factors.subscores.chargeback)
        self.assertEqual(0.06, factors.subscores.country)
        self.assertEqual(0.07, factors.subscores.country_mismatch)
        self.assertEqual(0.08, factors.subscores.cvv_result)
        self.assertEqual(0.18, factors.subscores.device)
        self.assertEqual(0.09, factors.subscores.email_address)
        self.assertEqual(0.10, factors.subscores.email_domain)
        self.assertEqual(0.19, factors.subscores.email_local_part)
        self.assertEqual(0.11, factors.subscores.email_tenure)
        self.assertEqual(0.12, factors.subscores.ip_tenure)
        self.assertEqual(0.13, factors.subscores.issuer_id_number)
        self.assertEqual(0.14, factors.subscores.order_amount)
        self.assertEqual(0.15, factors.subscores.phone_number)
        self.assertEqual(0.2, factors.subscores.shipping_address)
        self.assertEqual(
            0.16,
            factors.subscores.shipping_address_distance_to_ip_location,
        )
        self.assertEqual(0.17, factors.subscores.time_of_day)

        self.assertEqual(response, factors.to_dict())

    def factors_response(self) -> dict[str, Any]:
        return {
            "id": "b643d445-18b2-4b9d-bad4-c9c4366e402a",
            "disposition": {"action": "reject"},
            "ip_address": {"country": {"iso_code": "US"}},
            "credit_card": {
                "is_business": True,
                "is_prepaid": True,
                "brand": "Visa",
                "type": "debit",
            },
            "device": {"id": "b643d445-18b2-4b9d-bad4-c9c4366e402a"},
            "email": {"domain": {"first_seen": "2014-02-23"}, "is_free": True},
            "shipping_address": {"is_in_ip_country": True},
            "shipping_phone": {"is_voip": True},
            "billing_address": {"is_in_ip_country": True},
            "billing_phone": {"is_voip": True},
            "funds_remaining": 10.01,
            "queries_remaining": 123,
            "risk_score": 0.01,
            "subscores": {
                "avs_result": 0.01,
                "billing_address": 0.02,
                "billing_address_distance_to_ip_location": 0.03,
                "browser": 0.04,
                "chargeback": 0.05,
                "country": 0.06,
                "country_mismatch": 0.07,
                "cvv_result": 0.08,
                "device": 0.18,
                "email_address": 0.09,
                "email_domain": 0.10,
                "email_local_part": 0.19,
                "email_tenure": 0.11,
                "ip_tenure": 0.12,
                "issuer_id_number": 0.13,
                "order_amount": 0.14,
                "phone_number": 0.15,
                "shipping_address": 0.2,
                "shipping_address_distance_to_ip_location": 0.16,
                "time_of_day": 0.17,
            },
            "warnings": [{"code": "INVALID_INPUT"}],
            "risk_score_reasons": [
                {
                    "multiplier": 45,
                    "reasons": [
                        {
                            "code": "ANONYMOUS_IP",
                            "reason": "Risk due to IP being an Anonymous IP",
                        },
                    ],
                },
            ],
        }

    def check_insights_data(self, insights: Insights | Factors, uuid: str) -> None:
        self.assertEqual("US", insights.ip_address.country.iso_code)
        self.assertEqual(False, insights.ip_address.country.is_in_european_union)
        self.assertEqual(True, insights.credit_card.is_business)
        self.assertEqual(True, insights.credit_card.is_prepaid)
        self.assertEqual("Visa", insights.credit_card.brand)
        self.assertEqual("debit", insights.credit_card.type)
        self.assertEqual(uuid, insights.device.id)
        self.assertEqual("reject", insights.disposition.action)
        self.assertEqual(True, insights.email.is_free)
        self.assertEqual("2014-02-23", insights.email.domain.first_seen)
        self.assertEqual(True, insights.shipping_phone.is_voip)
        self.assertEqual(True, insights.shipping_address.is_in_ip_country)
        self.assertEqual(True, insights.billing_address.is_in_ip_country)
        self.assertEqual(True, insights.billing_phone.is_voip)
        self.assertEqual(uuid, insights.id)
        self.assertEqual(10.01, insights.funds_remaining)
        self.assertEqual(123, insights.queries_remaining)
        self.assertEqual(0.01, insights.risk_score)
        self.assertEqual("INVALID_INPUT", insights.warnings[0].code)
        self.assertIsInstance(insights.warnings, list, "warnings is a list")

    def check_risk_score_reasons_data(self, reasons: list[RiskScoreReason]) -> None:
        self.assertEqual(1, len(reasons))
        self.assertEqual(45, reasons[0].multiplier)
        self.assertEqual(1, len(reasons[0].reasons))
        self.assertEqual("ANONYMOUS_IP", reasons[0].reasons[0].code)
        self.assertEqual(
            "Risk due to IP being an Anonymous IP",
            reasons[0].reasons[0].reason,
        )
