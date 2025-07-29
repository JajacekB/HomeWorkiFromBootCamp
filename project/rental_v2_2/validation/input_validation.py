from validation.validation import is_valid_phone, is_valid_email

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


def prompt_update_with_validation(field_name, current_value, validation_func):
    while True:
        val = input(f"{field_name} [{current_value}]: ").strip()
        if not val:
            return current_value  # ENTER = zostaje stara wartość
        if validation_func(val):
            return val
        else:
            print(f"❌ Niepoprawny {field_name.lower()}, spróbuj ponownie.")