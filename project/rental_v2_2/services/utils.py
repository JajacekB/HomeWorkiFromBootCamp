

def format_date_pl(date_obj):
    month_pl = {
        1: "styczeń",
        2: "luty",
        3: "marzec",
        4: "kwiecień",
        5: "maj",
        6: "czerwiec",
        7: "lipiec",
        8: "sierpień",
        9: "wrzesień",
        10: "październik",
        11: "listopad",
        12: "grudzień"
    }
    day = date_obj.day
    month_name = month_pl.get(date_obj.month, "nieznany miesiąc")
    year = date_obj.year
    return f"{day}-{month_name}_{year}"


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