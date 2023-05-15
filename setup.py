#!/usr/bin/env python

import ast
import io
import re

from setuptools import setup

_version_re = re.compile(r"__version__\s+=\s+(.*)")

with io.open("minfraud/version.py", "r", encoding="utf-8") as f:
    _version = str(ast.literal_eval(_version_re.search(f.read()).group(1)))

setup(
    version=_version,
)
