import dns.resolver
import re


def is_valid_phone(phone: str) -> bool:
    """Sprawdza format numeru telefonu."""
    pattern = re.compile(r"^(\+\d{1,3}[ -]?)?\d{3}[ -]?\d{3}[ -]?\d{3}$")
    return bool(pattern.fullmatch(phone))


def is_valid_email(email: str) -> bool:
    """Sprawdza format e-maila oraz czy domena ma rekord MX."""
    if not is_valid_email_format(email):
        return False
    domain = email.split('@')[1]
    return domain_has_mx_record(domain)


def is_valid_email_format(email: str) -> bool:
    """Sprawdza format adresu e-mail."""
    pattern = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
    return bool(pattern.match(email))


def domain_has_mx_record(domain: str) -> bool:
    """Sprawdza czy domena ma rekord MX (obsługa poczty)."""
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        return len(answers) > 0
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN,
            dns.resolver.NoNameservers, dns.exception.Timeout):
        return False