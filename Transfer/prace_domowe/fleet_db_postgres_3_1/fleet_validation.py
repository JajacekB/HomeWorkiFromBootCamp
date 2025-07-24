import dns.resolver
import bcrypt
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


def get_valid_phone() -> str:
    """Pobiera numer telefonu od użytkownika, aż będzie poprawny."""
    while True:
        phone = input("📱 Nr telefonu: ").strip()
        if is_valid_phone(phone):
            return phone
        else:
            print("❌ Niepoprawny format telefonu. Spróbuj jeszcze raz.")


def get_valid_email() -> str:
    """Pobiera e-mail od użytkownika, aż będzie poprawny i domena zadziała."""
    while True:
        email = input("📧 Podaj adres e-mail: ").strip()
        if is_valid_email(email):
            print("✅ Poprawny e-mail i domena działa.")
            return email
        else:
            print("❌ Niepoprawny adres e-mail lub domena.")


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


def is_valid_password_format(
    password: str,
    min_length: int = 6,
    require_upper: bool = True,
    require_digit: bool = True
) -> bool:
    """Sprawdza, czy hasło spełnia wymagania długości, wielkiej litery i cyfry."""
    if len(password) < min_length:
        print(f"❌ Hasło musi mieć co najmniej {min_length} znaków.")
        return False
    if require_upper and not re.search(r"[A-Z]", password):
        print("❌ Hasło musi zawierać co najmniej jedną wielką literę.")
        return False
    if require_digit and not re.search(r"\d", password):
        print("❌ Hasło musi zawierać co najmniej jedną cyfrę.")
        return False
    return True


def get_password_with_confirmation() -> str | None:
    """
    Pobiera nowe hasło dwukrotnie i sprawdza, czy są identyczne.
    Zwraca hasło lub None, jeśli nie są zgodne.
    """
    new_pw = input("\nPodaj nowe hasło: ").strip()
    new_pw_confirm = input("Potwierdź nowe hasło: ").strip()

    if new_pw != new_pw_confirm:
        print("❌ Hasła nie są takie same.")
        return None
    return new_pw


def validate_and_change_password(
    db_user,
    min_length: int = 6,
    require_upper: bool = True,
    require_digit: bool = True
) -> bool:
    """
    Sprawdza stare hasło, prosi o dwukrotne podanie nowego hasła,
    waliduje je i aktualizuje hash w obiekcie użytkownika.
    Zwraca True, jeśli zmiana się powiodła, False w przeciwnym razie.
    """
    current_pw = input("\nPodaj obecne hasło: ").strip()
    if not bcrypt.checkpw(current_pw.encode(), db_user.password_hash.encode()):
        print("❌ Nieprawidłowe hasło.")
        return False

    new_pw = get_password_with_confirmation()
    if new_pw is None:
        return False

    if not is_valid_password_format(new_pw, min_length, require_upper, require_digit):
        return False

    new_hash = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt()).decode()
    db_user.password_hash = new_hash
    return True