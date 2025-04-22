import unittest
from typing import Any, cast

from minfraud.request import (
    _clean_email,
    clean_credit_card,
    maybe_hash_email,
)


class TestRequest(unittest.TestCase):
    def test_maybe_hash_email(self) -> None:
        tests = [
            {
                "name": "no email",
                "input": {"device": {"ip_address": "1.1.1.1"}},
                "expected": {"device": {"ip_address": "1.1.1.1"}},
            },
            {
                "name": "None email",
                "input": {"email": {"address": None}},
                "expected": {"email": {"address": None}},
            },
            {
                "name": "empty email",
                "input": {"email": {"address": ""}},
                "expected": {"email": {"address": ""}},
            },
            {
                "name": "already hashed email",
                "input": {"email": {"address": "757402e689152e0889ab9cf2c5984c65"}},
                "expected": {"email": {"address": "757402e689152e0889ab9cf2c5984c65"}},
            },
            {
                "name": "simple email",
                "input": {"email": {"address": "test@maxmind.com"}},
                "expected": {
                    "email": {
                        "address": "977577b140bfb7c516e4746204fbdb01",
                        "domain": "maxmind.com",
                    },
                },
            },
            {
                "name": "lots of extra whitespace",
                "input": {"email": {"address": "   test@   maxmind.com   "}},
                "expected": {
                    "email": {
                        "address": "977577b140bfb7c516e4746204fbdb01",
                        "domain": "maxmind.com",
                    },
                },
            },
            {
                "name": "domain already set",
                "input": {
                    "email": {"address": "test@maxmind.com", "domain": "google.com"},
                },
                "expected": {
                    "email": {
                        "address": "977577b140bfb7c516e4746204fbdb01",
                        "domain": "google.com",
                    },
                },
            },
            {
                "name": "uppercase and alias",
                "input": {"email": {"address": "Test+ignored@MaxMind.com"}},
                "expected": {
                    "email": {
                        "address": "977577b140bfb7c516e4746204fbdb01",
                        "domain": "maxmind.com",
                    },
                },
            },
            {
                "name": "multiple + signs",
                "input": {"email": {"address": "Test+ignored+more@maxmind.com"}},
                "expected": {
                    "email": {
                        "address": "977577b140bfb7c516e4746204fbdb01",
                        "domain": "maxmind.com",
                    },
                },
            },
            {
                "name": "empty alias",
                "input": {"email": {"address": "test+@maxmind.com"}},
                "expected": {
                    "email": {
                        "address": "977577b140bfb7c516e4746204fbdb01",
                        "domain": "maxmind.com",
                    },
                },
            },
            {
                "name": "Yahoo aliased email address",
                "input": {"email": {"address": "basename-keyword@yahoo.com"}},
                "expected": {
                    "email": {
                        "address": "667a28047b6caade43c7e75f66aab5f5",
                        "domain": "yahoo.com",
                    },
                },
            },
            {
                "name": "Yahoo email address with + in local part",
                "input": {"email": {"address": "Test+foo@yahoo.com"}},
                "expected": {
                    "email": {
                        "address": "a5f830c699fd71ad653aa59fa688c6d9",
                        "domain": "yahoo.com",
                    },
                },
            },
            {
                "name": "IDN in domain",
                "input": {"email": {"address": "test@bücher.com"}},
                "expected": {
                    "email": {
                        "address": "24948acabac551360cd510d5e5e2b464",
                        "domain": "xn--bcher-kva.com",
                    },
                },
            },
            {
                "name": "only + in local part",
                "input": {"email": {"address": "+@MaxMind.com"}},
                "expected": {
                    "email": {
                        "address": "aa57884e48f0dda9fc6f4cb2bffb1dd2",
                        "domain": "maxmind.com",
                    },
                },
            },
            {
                "name": "no domain",
                "input": {"email": {"address": "test@"}},
                "expected": {
                    "email": {
                        "address": "246a848af2f8394e3adbc738dbe43720",
                    },
                },
            },
            {
                "name": "email local part nfc normalization form 1",
                "input": {"email": {"address": "bu\u0308cher@example.com"}},
                "expected": {
                    "email": {
                        "address": "53550c712b146287a2d0dd30e5ed6f4b",
                        "domain": "example.com",
                    },
                },
            },
            {
                "name": "email local part nfc normalization form 2",
                "input": {"email": {"address": "b\u00fccher@example.com"}},
                "expected": {
                    "email": {
                        "address": "53550c712b146287a2d0dd30e5ed6f4b",
                        "domain": "example.com",
                    },
                },
            },
        ]

        for test in tests:
            with self.subTest(test["name"]):
                transaction = test["input"]

                maybe_hash_email(cast("dict[str, Any]", transaction))

                self.assertEqual(test["expected"], transaction)

    def test_clean_credit_card(self) -> None:
        tests = [
            {
                "name": "deprecated last_4_digits is cleaned to last_digits",
                "input": {
                    "issuer_id_number": "123456",
                    "last_4_digits": "1234",
                },
                "expected": {
                    "issuer_id_number": "123456",
                    "last_digits": "1234",
                },
            },
            {
                "name": "6 digit iin, 4 digit last_digits",
                "input": {
                    "issuer_id_number": "123456",
                    "last_digits": "1234",
                },
                "expected": {
                    "issuer_id_number": "123456",
                    "last_digits": "1234",
                },
            },
            {
                "name": "8 digit iin, 2 digit last_digits",
                "input": {
                    "issuer_id_number": "12345678",
                    "last_digits": "34",
                },
                "expected": {
                    "issuer_id_number": "12345678",
                    "last_digits": "34",
                },
            },
        ]

        for test in tests:
            with self.subTest(test["name"]):
                transaction = test["input"]

                clean_credit_card(cast("dict[str, Any]", transaction))

                self.assertEqual(test["expected"], transaction)

    def test_clean_email(self) -> None:
        tests: list[dict[str, str | None]] = [
            {"input": "", "output": None},
            {"input": "fasfs", "output": None},
            {"input": "test@gmail", "output": "test@gmail"},
            {"input": "e4d909c290d0fb1ca068ffaddf22cbd0", "output": None},
            {"input": "Test@maxmind", "output": "test@maxmind"},
            {"input": "Test@maxmind.com", "output": "test@maxmind.com"},
            {"input": "Test+007@maxmind.com", "output": "test@maxmind.com"},
            {"input": "Test+007+008@maxmind.com", "output": "test@maxmind.com"},
            {"input": "Test+@maxmind.com", "output": "test@maxmind.com"},
            {"input": "+@maxmind.com", "output": "+@maxmind.com"},
            {"input": "  Test@maxmind.com", "output": "test@maxmind.com"},
            {
                "input": "Test@maxmind.com|abc124472372",
                "output": "test@maxmind.com|abc124472372",
            },
            {"input": "Test+foo@yahoo.com", "output": "test+foo@yahoo.com"},
            {"input": "Test-foo@yahoo.com", "output": "test@yahoo.com"},
            {"input": "Test-foo-foo2@yahoo.com", "output": "test@yahoo.com"},
            {"input": "Test-foo@gmail.com", "output": "test-foo@gmail.com"},
            {"input": "gamil.com@gamil.com", "output": "gamilcom@gmail.com"},
            {"input": "Test+alias@bücher.com", "output": "test@xn--bcher-kva.com"},
            {"input": "foo@googlemail.com", "output": "foo@gmail.com"},
            {"input": "foo.bar@gmail.com", "output": "foobar@gmail.com"},
            {"input": "alias@user.fastmail.com", "output": "user@fastmail.com"},
            {"input": "foo-bar@ymail.com", "output": "foo@ymail.com"},
            {"input": "foo@example.com.com", "output": "foo@example.com"},
            {"input": "foo@example.comfoo", "output": "foo@example.comfoo"},
            {"input": "foo@example.cam", "output": "foo@example.cam"},
            {"input": "foo@10000gmail.com", "output": "foo@gmail.com"},
            {"input": "foo@example.comcom", "output": "foo@example.com"},
            {"input": "foo@example.com.", "output": "foo@example.com"},
            {"input": "foo@example.com...", "output": "foo@example.com"},
            {
                "input": "example@bu\u0308cher.com",
                "output": "example@xn--bcher-kva.com",
            },
            {"input": "example@b\u00fccher.com", "output": "example@xn--bcher-kva.com"},
        ]

        for test in tests:
            got, _ = _clean_email(cast("str", test["input"]))
            self.assertEqual(test["output"], got)
