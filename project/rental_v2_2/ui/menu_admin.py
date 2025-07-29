# directory: ui
# file: menu_admin.p

from ui.menu_base import handle_choice, logoff_user
from services.user_service import add_seller, add_client,remove_user, get_clients, update_profile
from services.vehicle_management import add_vehicles_batch, remove_vehicle, get_vehicle
from services.rental_process import rent_vehicle_for_client, return_vehicle
from services.repair import repair_vehicle


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
            "1": lambda: add_seller(session),
            "2": lambda: remove_user(session, role="seller"),
            "3": lambda: add_client(session),
            "4": lambda: remove_user(session),
            "5": lambda: get_clients(session),
            "6": lambda: add_vehicles_batch(session),
            "7": lambda: remove_vehicle(session),
            "8": lambda: get_vehicle(session),
            "9": lambda: rent_vehicle_for_client(session, user),
            "10": lambda: return_vehicle(session, user),
            "11": lambda: repair_vehicle(session),
            "12": lambda: update_profile(session, user)
        })
