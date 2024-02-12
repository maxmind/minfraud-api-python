"""This is an internal module used for preparing the minFraud request.

This code is only intended for internal use and is subject to change in ways
that may break any direct use of it.

"""

import re
import warnings
import hashlib
from typing import Any, Dict
from voluptuous import MultipleInvalid

from .errors import InvalidRequestError
from .validation import validate_report, validate_transaction

_TYPO_DOMAINS = {
    # gmail.com
    "gmai.com": "gmail.com",
    "gamil.com": "gmail.com",
    "gmali.com": "gmail.com",
    "gmial.com": "gmail.com",
    "gmil.com": "gmail.com",
    "gmaill.com": "gmail.com",
    "gmailm.com": "gmail.com",
    "gmailo.com": "gmail.com",
    "gmailyhoo.com": "gmail.com",
    "yahoogmail.com": "gmail.com",
    # outlook.com
    "putlook.com": "outlook.com",
}

_EQUIVALENT_DOMAINS = {
    "googlemail.com": "gmail.com",
    "pm.me": "protonmail.com",
    "proton.me": "protonmail.com",
    "yandex.by": "yandex.ru",
    "yandex.com": "yandex.ru",
    "yandex.kz": "yandex.ru",
    "yandex.ua": "yandex.ru",
    "ya.ru": "yandex.ru",
}

_FASTMAIL_DOMAINS = {
    "123mail.org",
    "150mail.com",
    "150ml.com",
    "16mail.com",
    "2-mail.com",
    "4email.net",
    "50mail.com",
    "airpost.net",
    "allmail.net",
    "bestmail.us",
    "cluemail.com",
    "elitemail.org",
    "emailcorner.net",
    "emailengine.net",
    "emailengine.org",
    "emailgroups.net",
    "emailplus.org",
    "emailuser.net",
    "eml.cc",
    "f-m.fm",
    "fast-email.com",
    "fast-mail.org",
    "fastem.com",
    "fastemail.us",
    "fastemailer.com",
    "fastest.cc",
    "fastimap.com",
    "fastmail.cn",
    "fastmail.co.uk",
    "fastmail.com",
    "fastmail.com.au",
    "fastmail.de",
    "fastmail.es",
    "fastmail.fm",
    "fastmail.fr",
    "fastmail.im",
    "fastmail.in",
    "fastmail.jp",
    "fastmail.mx",
    "fastmail.net",
    "fastmail.nl",
    "fastmail.org",
    "fastmail.se",
    "fastmail.to",
    "fastmail.tw",
    "fastmail.uk",
    "fastmail.us",
    "fastmailbox.net",
    "fastmessaging.com",
    "fea.st",
    "fmail.co.uk",
    "fmailbox.com",
    "fmgirl.com",
    "fmguy.com",
    "ftml.net",
    "h-mail.us",
    "hailmail.net",
    "imap-mail.com",
    "imap.cc",
    "imapmail.org",
    "inoutbox.com",
    "internet-e-mail.com",
    "internet-mail.org",
    "internetemails.net",
    "internetmailing.net",
    "jetemail.net",
    "justemail.net",
    "letterboxes.org",
    "mail-central.com",
    "mail-page.com",
    "mailandftp.com",
    "mailas.com",
    "mailbolt.com",
    "mailc.net",
    "mailcan.com",
    "mailforce.net",
    "mailftp.com",
    "mailhaven.com",
    "mailingaddress.org",
    "mailite.com",
    "mailmight.com",
    "mailnew.com",
    "mailsent.net",
    "mailservice.ms",
    "mailup.net",
    "mailworks.org",
    "ml1.net",
    "mm.st",
    "myfastmail.com",
    "mymacmail.com",
    "nospammail.net",
    "ownmail.net",
    "petml.com",
    "postinbox.com",
    "postpro.net",
    "proinbox.com",
    "promessage.com",
    "realemail.net",
    "reallyfast.biz",
    "reallyfast.info",
    "rushpost.com",
    "sent.as",
    "sent.at",
    "sent.com",
    "speedpost.net",
    "speedymail.org",
    "ssl-mail.com",
    "swift-mail.com",
    "the-fastest.net",
    "the-quickest.com",
    "theinternetemail.com",
    "veryfast.biz",
    "veryspeedy.net",
    "warpmail.net",
    "xsmail.com",
    "yepmail.net",
    "your-mail.com",
}

_YAHOO_DOMAINS = {
    "y7mail.com",
    "yahoo.at",
    "yahoo.be",
    "yahoo.bg",
    "yahoo.ca",
    "yahoo.cl",
    "yahoo.co.id",
    "yahoo.co.il",
    "yahoo.co.in",
    "yahoo.co.kr",
    "yahoo.co.nz",
    "yahoo.co.th",
    "yahoo.co.uk",
    "yahoo.co.za",
    "yahoo.com",
    "yahoo.com.ar",
    "yahoo.com.au",
    "yahoo.com.br",
    "yahoo.com.co",
    "yahoo.com.hk",
    "yahoo.com.hr",
    "yahoo.com.mx",
    "yahoo.com.my",
    "yahoo.com.pe",
    "yahoo.com.ph",
    "yahoo.com.sg",
    "yahoo.com.tr",
    "yahoo.com.tw",
    "yahoo.com.ua",
    "yahoo.com.ve",
    "yahoo.com.vn",
    "yahoo.cz",
    "yahoo.de",
    "yahoo.dk",
    "yahoo.ee",
    "yahoo.es",
    "yahoo.fi",
    "yahoo.fr",
    "yahoo.gr",
    "yahoo.hu",
    "yahoo.ie",
    "yahoo.in",
    "yahoo.it",
    "yahoo.lt",
    "yahoo.lv",
    "yahoo.nl",
    "yahoo.no",
    "yahoo.pl",
    "yahoo.pt",
    "yahoo.ro",
    "yahoo.se",
    "yahoo.sk",
    "ymail.com",
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

    if cleaned_request.get("credit_card", None):
        clean_credit_card(cleaned_request)

    return cleaned_request


def _copy_and_clean(data: Any) -> Any:
    """Create a copy of the data structure with Nones removed."""
    if isinstance(data, dict):
        return dict((k, _copy_and_clean(v)) for (k, v) in data.items() if v is not None)
    if isinstance(data, (list, set, tuple)):
        return [_copy_and_clean(x) for x in data if x is not None]
    return data


def clean_credit_card(credit_card):
    """Clean the credit_card input of a transaction request"""
    last4 = credit_card.pop("last_4_digits", None)
    if last4:
        warnings.warn(
            "last_4_digits has been deprecated in favor of last_digits",
            DeprecationWarning,
        )
        credit_card["last_digits"] = last4


def maybe_hash_email(transaction):
    """Hash email address in transaction, if present"""
    try:
        email = transaction["email"]
        address = email["address"]
    except KeyError:
        return

    if address is None:
        return

    address, domain = _clean_email(address)
    if not address:
        return

    if domain != "" and "domain" not in email:
        email["domain"] = domain

    email["address"] = hashlib.md5(address.encode("UTF-8")).hexdigest()


def _clean_domain(domain):
    domain = domain.strip().rstrip(".").encode("idna").decode("ASCII")

    domain = re.sub(r"(?:\.com){2,}$", ".com", domain)
    domain = re.sub(r"\.com[^.]+$", ".com", domain)
    domain = re.sub(r"(?:\.(?:com|c[a-z]{1,2}m|co[ln]|[dsvx]o[mn]|))$", ".com", domain)
    domain = re.sub(r"^\d+(?:gmail?\.com)$", "gmail.com", domain)

    domain = _TYPO_DOMAINS.get(domain, domain)
    domain = _EQUIVALENT_DOMAINS.get(domain, domain)

    return domain


def _clean_email(address):
    address = address.lower().strip()

    at_idx = address.rfind("@")
    if at_idx == -1:
        return None, None

    domain = _clean_domain(address[at_idx + 1 :])  # noqa
    local_part = address[:at_idx]

    # Strip off aliased part of email address.
    if domain in _YAHOO_DOMAINS:
        divider = "-"
    else:
        divider = "+"

    alias_idx = local_part.find(divider)
    if alias_idx > 0:
        local_part = local_part[:alias_idx]

    if domain == "gmail.com":
        local_part = local_part.replace(".", "")

    domain_parts = domain.split(".")
    if len(domain_parts) > 2:
        possible_domain = ".".join(domain_parts[1:])
        if possible_domain in _FASTMAIL_DOMAINS:
            domain = possible_domain
            if local_part != "":
                local_part = domain_parts[0]

    return f"{local_part}@{domain}", domain
