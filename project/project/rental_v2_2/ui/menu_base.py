# directory: ui
# file: manu_base.py

from ui.promotions_baner import show_dynamic_promo_banner
from database.base import SessionLocal
from services.user_service import register_user
from services.auth_service import login_user

class LogoutException(Exception):
    pass


def logoff_user():
    print("\n🔒 Wylogowano.")
    raise LogoutException()

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
            user = login_user(session)
            if user:
                return user
        elif choice == "2":
            user = register_user(session)
            if user:
                return user
        elif choice == "0":
            print("Do widzenia!")
            exit()
        else:
            print("❌ Niepoprawny wybór, spróbuj ponownie.")

def handle_choice(options: dict):
    # Obsługuje wybór użytkownika z mapy opcji.
    choice = input("Wybierz opcję: ").strip()
    action = options.get(choice)
    if callable(action):
        action()
    else:
        print("❌ Zły wybór. Spróbuj ponownie.")