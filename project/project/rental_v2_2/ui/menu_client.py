# directory: ui
# file: menu_client.py

from ui.menu_base import handle_choice, logoff_user
from services.vehicle_management import get_vehicle
from services.user_service import update_profile
from ui.promotions_baner import show_dynamic_promo_banner
from services.rental_process import rent_vehicle, return_vehicle


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
            "1": lambda: get_vehicle(session, only_available=True),
            "2": lambda: rent_vehicle(session, user),
            "3": lambda: return_vehicle(session, user),
            "4": lambda: update_profile(session, user)
        })