
def get_positive_int(prompt, max_value: int | None = None, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if allow_empty and not value:
            return None
        try:
            value = int(value)
            if value <= 0:
                print("❌ Liczba musi być większa od zera.")
                continue
            if max_value is not None and value > max_value:
                print(f"❌ Liczba musi być mniejsza lub równa {max_value}.")
                continue
            return value
        except ValueError:
            print("❌ Wprowadź poprawną liczbę całkowitą (np. 25).")

def get_positive_float(prompt, max_value: float | None = None, allow_empty=False):
    while True:
        value = input(prompt).strip()
        if allow_empty and not value:
            return None
        try:
            value = float(value)
            if value <= 0:
                print("❌ Liczba musi być większa od zera.")
                continue
            if max_value is not None and value > max_value:
                print(f"❌ Liczba musi być mniejsza lub równa {max_value}.")
                continue
            return value
        except ValueError:
            print("❌ Wprowadź poprawną liczbę całkowitą (np. 25.5).")