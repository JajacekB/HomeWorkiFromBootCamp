# directory: utils
# file: input_helpers.py

from datetime import datetime, date


def choice_menu(prompt: str, variable):
    print(f"\n{prompt}\n{'-' * len(prompt)}")

    if isinstance(variable, dict):
        for key, val in variable.items():
            print(f"{key}: {val}")
        valid_inputs = variable.keys()

    elif isinstance(variable, list):
        for item in variable:
            print(f"- {item}")
        valid_inputs = variable

    else:
        raise TypeError("Variable musi być słownikiem lub listą")

    while True:
        choice = input("Wpisz swoją odpowiedź: ").strip().lower()
        if choice in valid_inputs:
            return choice
        else:
            print("Nieprawidłowy wybór. Spróbuj ponownie.")


def yes_or_not_menu(prompt: str) -> bool:
    print(f"\n{prompt}\n{'-' * len(prompt)}")
    while True:
        choice = input("Wybierz (tak/nie): ").strip().lower()
        if choice in {"tak", "t", "yes", "y"}:
            return True
        elif choice in {"nie", "n", "no"}:
            return False
        else:
            print("\nNieprawidłowy wybór. Wpisz tak lub nie.")


def get_date_from_user(prompt) -> date:
    # f"\nPodaj rzeczywistą datę zwrotu (DD-MM-YYYY) Enter = dziś: "  - przykładowy prompt do użycia
    while True:
        return_date_input_str = input(prompt).strip().lower()

        try:

            if return_date_input_str:
                return_date_input = datetime.strptime(return_date_input_str, "%d-%m-%Y").date()
            else:
                return_date_input = date.today()
            break

        except ValueError:
            print("❌ Niepoprawny format daty.")
            continue
    return return_date_input