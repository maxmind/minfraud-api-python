"""Internal module for version (to prevent cyclic imports)."""

from importlib.metadata import version

__version__ = version("minfraud")
