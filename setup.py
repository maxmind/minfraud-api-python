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
    "aiohttp>=3.6.2",
    "email_validator",
    "geoip2>=4.0.0,<5.0.0",
    "requests>=2.24.0",
    "urllib3>=1.25.2",
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
    description="MaxMind minFraud Score, Insights, Factors and Report Transactions API",
    long_description=_readme,
    author="Gregory Oschwald",
    author_email="goschwald@maxmind.com",
    url="http://www.maxmind.com/",
    packages=["minfraud"],
    include_package_data=True,
    platforms="any",
    python_requires=">=3.6",
    install_requires=requirements,
    tests_require=["mocket>=3.8.6"],
    test_suite="tests",
    license="Apache License 2.0 ",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python",
        "Topic :: Internet :: Proxy Servers",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet",
    ],
)
