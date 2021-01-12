import unittest

from minfraud.request import maybe_hash_email


class TestRequest(unittest.TestCase):
    def test_maybe_hash_email(self):
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
                    }
                },
            },
            {
                "name": "lots of extra whitespace",
                "input": {"email": {"address": "   test@   maxmind.com   "}},
                "expected": {
                    "email": {
                        "address": "977577b140bfb7c516e4746204fbdb01",
                        "domain": "maxmind.com",
                    }
                },
            },
            {
                "name": "domain already set",
                "input": {
                    "email": {"address": "test@maxmind.com", "domain": "google.com"}
                },
                "expected": {
                    "email": {
                        "address": "977577b140bfb7c516e4746204fbdb01",
                        "domain": "google.com",
                    }
                },
            },
            {
                "name": "uppercase and alias",
                "input": {"email": {"address": "Test+ignored@MaxMind.com"}},
                "expected": {
                    "email": {
                        "address": "977577b140bfb7c516e4746204fbdb01",
                        "domain": "maxmind.com",
                    }
                },
            },
            {
                "name": "multiple + signs",
                "input": {"email": {"address": "Test+ignored+more@maxmind.com"}},
                "expected": {
                    "email": {
                        "address": "977577b140bfb7c516e4746204fbdb01",
                        "domain": "maxmind.com",
                    }
                },
            },
            {
                "name": "empty alias",
                "input": {"email": {"address": "test+@maxmind.com"}},
                "expected": {
                    "email": {
                        "address": "977577b140bfb7c516e4746204fbdb01",
                        "domain": "maxmind.com",
                    }
                },
            },
            {
                "name": "Yahoo aliased email address",
                "input": {"email": {"address": "basename-keyword@yahoo.com"}},
                "expected": {
                    "email": {
                        "address": "667a28047b6caade43c7e75f66aab5f5",
                        "domain": "yahoo.com",
                    }
                },
            },
            {
                "name": "Yahoo email address with + in local part",
                "input": {"email": {"address": "Test+foo@yahoo.com"}},
                "expected": {
                    "email": {
                        "address": "a5f830c699fd71ad653aa59fa688c6d9",
                        "domain": "yahoo.com",
                    }
                },
            },
            {
                "name": "IDN in domain",
                "input": {"email": {"address": "test@bücher.com"}},
                "expected": {
                    "email": {
                        "address": "24948acabac551360cd510d5e5e2b464",
                        "domain": "xn--bcher-kva.com",
                    }
                },
            },
            {
                "name": "only + in local part",
                "input": {"email": {"address": "+@MaxMind.com"}},
                "expected": {
                    "email": {
                        "address": "aa57884e48f0dda9fc6f4cb2bffb1dd2",
                        "domain": "maxmind.com",
                    }
                },
            },
            {
                "name": "no domain",
                "input": {"email": {"address": "test@"}},
                "expected": {
                    "email": {
                        "address": "246a848af2f8394e3adbc738dbe43720",
                    }
                },
            },
        ]

        for test in tests:
            with self.subTest(test["name"]):
                transaction = test["input"]

                maybe_hash_email(transaction)

                self.assertEqual(test["expected"], transaction)
