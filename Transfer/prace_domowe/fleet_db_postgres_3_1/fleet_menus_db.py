from fleet_promo_db import  show_dynamic_promo_banner
from fleet_database import SessionLocal
from fleet_manager_user import (
    login_user, register_user, add_seller,
    add_client, remove_user, get_clients, update_profile)
from fleet_manager_fleet import (
    get_vehicle, rent_vehicle, return_vehicle,
    add_vehicles_batch, remove_vehicle, rent_vehicle_for_client,
    repair_vehicle
)

class LogoutException(Exception):
    pass

def logoff_user():
    print("\n🔒 Wylogowano.")
    raise LogoutException()


def handle_choice(options: dict):
    # Obsługuje wybór użytkownika z mapy opcji.
    choice = input("Wybierz opcję: ").strip()
    action = options.get(choice)
    if callable(action):
        action()
    else:
        print("❌ Zły wybór. Spróbuj ponownie.")


def start_menu():
    while True:
        with SessionLocal() as session:
            show_dynamic_promo_banner(session)


        print("""
=== SYSTEM WYPOŻYCZANIA POJAZDÓW ===

0. Zamknij program
1. Zaloguj się
2. Zarejestruj się

""")
        choice = input("Wybierz opcję (0-2): ").strip()

        if choice == "1":
            user = login_user()
            if user:
                return user
        elif choice == "2":
            user = register_user()
            if user:
                return user
        elif choice == "0":
            print("Do widzenia!")
            exit(0)
        else:
            print("❌ Niepoprawny wybór, spróbuj ponownie.")


def menu_client(user, session):
    while True:
        show_dynamic_promo_banner(session)
        print(f"""\n=== MENU KLIENTA ===
0. Wyloguj się
1. Przeglądaj pojazdy
2. Wypożycz pojazd
3. Zwróć pojazd
4. Zaktualizuj profil
""")
        handle_choice({
            "0": logoff_user,
            "1": lambda: get_vehicle(only_available=True),
            "2": lambda: rent_vehicle(user),
            "3": lambda: return_vehicle(user),
            "4": lambda: update_profile(user)
        })


def menu_seller(user, session):
    while True:
        print(f"""\n=== MENU SPRZEDAWCY ===
0. Wyloguj się
1. Dodaj nowego klienta
2. Usuń klienta
3. Przeglądaj klientów
4. Dodaj nowy pojazd
5. Usuń pojazd z użytkowania
6. Przeglądaj pojazdy
7. Wypożycz pojazd klientowi
8. Zwróć pojazd
9. Oddaj pojazd do naprawy
10. Aktualizuj profil
""")
        handle_choice({
            "0": logoff_user,
            "1": add_client,
            "2": lambda: remove_user(role="client"),
            "3": get_clients,
            "4": add_vehicles_batch,
            "5": remove_vehicle,
            "6": lambda: get_vehicle(),
            "7": lambda: rent_vehicle_for_client(user),
            "8": lambda: return_vehicle(user),
            "9": repair_vehicle,
            "10": lambda: update_profile(user)
        })


def menu_admin(user, session):
    while True:
        print(f"""\n=== MENU ADMINA ===
0. Wyloguj się 
1. Dodaj nowego sprzedawcę
2. Usuń sprzedawcę
3. Dodaj nowego klienta
4. Usuń klienta
5. Przeglądaj klientów
6. Dodaj nowy pojazd
7. Usuń pojazd z użytkowania
8. Przeglądaj pojazdy 
9. Wypożycz pojazd klientowi
10. Zwróć pojazd
11. Oddaj pojazd do naprawy
12. Aktualizuj profil
""")
        handle_choice({
            "0": logoff_user,
            "1": add_seller,
            "2": lambda: remove_user(role="seller"),
            "3": add_client,
            "4": lambda: remove_user(),
            "5": get_clients,
            "6": add_vehicles_batch,
            "7": remove_vehicle,
            "8": lambda: get_vehicle(),
            "9": lambda: rent_vehicle_for_client(user),
            "10": lambda: return_vehicle(user),
            "11": repair_vehicle,
            "12": lambda: update_profile(user)
        })

