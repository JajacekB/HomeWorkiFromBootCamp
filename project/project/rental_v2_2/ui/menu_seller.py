# directory: ui
# file: menu_seller.py

from services.user_service import add_client, remove_user, get_clients, update_profile
from services.vehicle_management import add_vehicles_batch, get_vehicle, remove_vehicle
from services.rental_process import rent_vehicle_for_client, return_vehicle
from services.repair import repair_vehicle
from ui.menu_base import handle_choice, logoff_user

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
            "1": lambda: add_client(session),
            "2": lambda: remove_user(session, role="client"),
            "3": lambda: get_clients(session),
            "4": lambda: add_vehicles_batch(session),
            "5": lambda: remove_vehicle(session),
            "6": lambda: get_vehicle(session),
            "7": lambda: rent_vehicle_for_client(session, user),
            "8": lambda: return_vehicle(session, user),
            "9": lambda: repair_vehicle(session),
            "10": lambda: update_profile(session, user)
        })