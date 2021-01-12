"""This is an internal module used for preparing the minFraud request.

This code is only intended for internal use and is subject to change in ways
that may break any direct use of it.

"""

import hashlib
from typing import Any, Dict
from voluptuous import MultipleInvalid

from .errors import InvalidRequestError
from .validation import validate_report, validate_transaction

_TYPO_DOMAINS = {
    # gmail.com
    "35gmai.com": "gmail.com",
    "636gmail.com": "gmail.com",
    "gamil.com": "gmail.com",
    "gmail.comu": "gmail.com",
    "gmial.com": "gmail.com",
    "gmil.com": "gmail.com",
    "yahoogmail.com": "gmail.com",
    # outlook.com
    "putlook.com": "outlook.com",
}


def prepare_report(request: Dict[str, Any], validate: bool):
    """Validate and prepare minFraud report"""
    cleaned_request = _copy_and_clean(request)
    if validate:
        try:
            validate_report(cleaned_request)
        except MultipleInvalid as ex:
            raise InvalidRequestError(f"Invalid report data: {ex}") from ex
    return cleaned_request


def prepare_transaction(
    request: Dict[str, Any],
    validate: bool,
    hash_email: bool,
):
    """Validate and prepare minFraud transaction"""
    cleaned_request = _copy_and_clean(request)
    if validate:
        try:
            validate_transaction(cleaned_request)
        except MultipleInvalid as ex:
            raise InvalidRequestError(f"Invalid transaction data: {ex}") from ex

    if hash_email:
        maybe_hash_email(cleaned_request)

    return cleaned_request


def _copy_and_clean(data: Any) -> Any:
    """Create a copy of the data structure with Nones removed."""
    if isinstance(data, dict):
        return dict((k, _copy_and_clean(v)) for (k, v) in data.items() if v is not None)
    if isinstance(data, (list, set, tuple)):
        return [_copy_and_clean(x) for x in data if x is not None]
    return data


def maybe_hash_email(transaction):
    """Hash email address in transaction, if present"""
    try:
        email = transaction["email"]
        address = email["address"]
    except KeyError:
        return

    if address is None:
        return

    address = address.lower().strip()

    at_idx = address.rfind("@")
    if at_idx == -1:
        return

    domain = _clean_domain(address[at_idx + 1 :])
    local_part = address[:at_idx]

    if domain != "" and "domain" not in email:
        email["domain"] = domain

    email["address"] = _hash_email(local_part, domain)


def _clean_domain(domain):
    domain = domain.strip().rstrip(".").encode("idna").decode("ASCII")
    return _TYPO_DOMAINS.get(domain, domain)


def _hash_email(local_part, domain):
    # Strip off aliased part of email address
    if domain == "yahoo.com":
        divider = "-"
    else:
        divider = "+"

    alias_idx = local_part.find(divider)
    if alias_idx > 0:
        local_part = local_part[:alias_idx]

    return hashlib.md5(f"{local_part}@{domain}".encode("UTF-8")).hexdigest()
