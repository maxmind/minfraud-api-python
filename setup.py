#!/usr/bin/env python

import ast
import io
import os
import re
import sys

from setuptools import setup

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with io.open("minfraud/version.py", "r", encoding="utf-8") as f:
    _version = str(ast.literal_eval(_version_re.search(f.read()).group(1)))

with io.open("README.rst", "r", encoding="utf-8") as f:
    _readme = f.read()

requirements = [
    "geoip2>=3.0.0,<4.0.0",
    "requests>=2.22.0",
    "rfc3987",
    "strict-rfc3339",
    "urllib3>=1.25.2",
    "validate_email",
    "voluptuous",
]

# Write requirements.txt needed for snyk testing, only for latest release python.
if os.environ.get("SNYK_TOKEN") and os.environ.get("RUN_SNYK"):
    with open("requirements.txt", "w") as f:
        for r in requirements:
            f.write(r + "\n")

setup(
    name="minfraud",
    version=_version,
    description="MaxMind minFraud Score, Insights, and Factors API",
    long_description=_readme,
    author="Gregory Oschwald",
    author_email="goschwald@maxmind.com",
    url="http://www.maxmind.com/",
    packages=["minfraud"],
    include_package_data=True,
    platforms="any",
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=requirements,
    extras_require={':python_version=="2.7"': ["ipaddress"]},
    tests_require=["requests_mock"],
    test_suite="tests",
    license="Apache License 2.0 ",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet",
    ],
)
