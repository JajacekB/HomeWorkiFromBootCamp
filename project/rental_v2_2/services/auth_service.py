# directory: services
# file: auth_service.py

import bcrypt
from database.base import Session
from models.user import User
from services.user_service import register_user


def login_user(session):
    while True:
        print("\n=== LOGOWANIE DO SYSTEMU ===")
        login_or_email = input("\nLogin: ").strip()
        password = input("Hasło: ").strip()

        user = session.query(User).filter(
            (User.login == login_or_email) | (User.email == login_or_email)
        ).first()

        if not user:
            print("\nNie znaleziono użytkownika.")
        elif not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            print("\nBłędne hasło.")
        else:
            print(f"\nZalogowano jako {user.first_name} {user.last_name} ({user.role})")
            return user

        print(f"\nCo chcesz zrobić?\n"
                f"1. Spróbować jeszcze raz.\n"
                f"2. Zarejestrować się.\n"
                f"3. Anulować logowanie."
        )
        choice = input("\nWybierz opcje (1 - 3): ").strip()
        if choice == "1":
            continue
        elif choice == "2":
            return register_user()
        else:
            print("\nAnulowano logowanie.")
            return None