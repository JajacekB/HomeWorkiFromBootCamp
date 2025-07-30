# services/user_service.py

import bcrypt
from typing import List
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, not_
from models.user import User
from models.vehicle import Vehicle
from services.utils import get_positive_int
from validation.input_validation import get_valid_phone, get_valid_email, prompt_update_with_validation
from validation.password_validation import is_valid_password_format, validate_and_change_password
from validation.validation import is_valid_phone, is_valid_email
from utils.iput_helpers import choice_menu, yes_or_not_menu, get_date_from_user


def register_user(session, role="client", auto=False):
    """
    Rejestracja nowego użytkownika.
    :param role: 'client' lub 'seller'
    :param auto: jeśli True, login i hasło są generowane automatycznie (dla sprzedawcy).
    """
    print(f"\n=== REJESTRACJA NOWEGO {'SPRZEDAWCY' if role == 'seller' else 'KLIENTA'} ===")

    print("\nPodaj dane potrzebne do rejestracji")
    first_name = input("🧑 Imię: ").strip().capitalize()
    last_name = input("👤 Nazwisko: ").strip().capitalize()
    phone = get_valid_phone()
    email = get_valid_email()
    address = input("🏠 Adres zamieszkania: ").strip()

    if auto and role == "seller":
        count = session.query(User).filter_by(role="seller").count()
        seller_number = str(count + 1).zfill(2)
        login = f"Seller{seller_number}"
        raw_password = login
        password_hash = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()
        print(f"\nUtworzono login: {login} | hasło: {raw_password}")

    else:
        login = input("Login: ").strip()
        while True:
            password = input("Hasło: ").strip()
            password_confirm = input("Potwierdź hasło: ").strip()
            if password != password_confirm:
                print("\n❌ Hasła nie są takie same. Spróbuj ponownie.")
                continue
            if not is_valid_password_format(password):
                print("\n❌ Hasło musi mieć co najmniej 6 znaków, zawierać 1 wielką literę i 1 cyfrę.")
                continue
            break  # wszystko OK

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        login=login,
        phone=phone,
        email=email,
        password_hash=password_hash,
        address=address,
        role=role
    )

    try:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        print(f"\n✅ Użytkownik {login} został dodany pomyślnie.")
        return new_user
    except IntegrityError:
        session.rollback()
        print("\n❌ Login, telefon lub email już istnieje. Spróbuj z innymi danymi.")
        return None


def update_profile(session, user: User):
    while True:
        question = {
            "1": "Dane osobowe (imę, nazwisko, telefon, email, adres zamiszkania)",
            "2": "Hasło",
            "3": "Wyjdź bez zmian"
        }
        choice = choice_menu(f"\n=== AKTUALIZACJA PROFILU UŻYTKOWNIKA ==="
            f"\nZalogowany jako: {user.first_name} {user.last_name} ({user.login})"
            f"\nCo chcesz zmienić?", question
        )
        if choice == "1":
            db_user = session.query(User).filter(User.id == user.id).first()
            if not db_user:
                print("❌ Nie znaleziono użytkownika w bazie.")
                return

            print("\nWprowadź nowe dane lub naciśnij (ENTER), aby pozostawić bez zmiany")

            def prompt_update(field_name, current_value):
                val = input(f"{field_name} [{current_value}]: ").strip()
                return val if val else current_value

            new_first_name = prompt_update("Imię:", db_user.first_name).strip().capitalize()
            new_last_name = prompt_update("Nazwisko:", db_user.last_name).strip().capitalize()
            new_phone = prompt_update_with_validation("Telefon", db_user.phone, is_valid_phone)
            new_email = prompt_update_with_validation("Email", db_user.email, is_valid_email)
            new_address = prompt_update("Adres:", db_user.address).strip()

            contfirm = yes_or_not_menu(
                f"\nNowe dane użytkownkia:"
                f"\nImię: {new_first_name}"
                f"\nNazwisko: {new_last_name}"
                f"\nTelefon: {new_phone}"
                f"\nEmail: {new_email}"
                f"\nAdres: {new_address}"
            )

            if contfirm:
                db_user.first_name = new_first_name
                db_user.last_name = new_last_name
                db_user.phone = new_phone
                db_user.email = new_email
                db_user.address = new_address
                try:
                    session.commit()
                    print("✅ Dane zostały zaktualizowane.")
                    # aktualizacja zalogowanego usera
                    for attr in ["first_name", "last_name", "phone", "email", "address"]:
                        setattr(user, attr, getattr(db_user, attr))

                except IntegrityError:
                    session.rollback()
                    print("❌ Podany email lub telefon jest już zajęty przez innego użytkownika.")
            else:
                print("❌ Anulowano aktualizację danych.")
        elif choice == "2":
            db_user = session.query(User).filter(User.id == user.id).first()
            if not db_user:
                print("❌ Nie znaleziono użytkownika.")
                return

            if validate_and_change_password(db_user):
                try:
                    session.commit()
                    print("✅ Hasło zostało zmienione.")
                except Exception as e:
                    session.rollback()
                    print("❌ Błąd podczas zapisywania hasła:", e)
        elif choice == "3":
            print("🔙 Powrót bez zmian.")
            return

        else:
            print("❌ Niepoprawny wybór. Spróbuj ponownie.")


def remove_user(session, role="client"):
    while True:
        users = session.query(User).filter_by(role=role).all()
        if not users:
            print(f"\nℹ️ Brak użytkowników o roli '{role}' w bazie.")
            return

        print(f"\n📋 Lista użytkowników o roli '{role}':")
        for user in users:
            print(f" - ID: {user.id}, Login: {user.login}, Imię: {user.first_name} {user.last_name}")

        while True:
            user_input = input(
                f"\n🧑 Wpisz login lub ID użytkownika o roli '{role}' do usunięcia."
                f"\n🔙 Wpisz 'Anuluj', aby wrócić: "
            ).strip()

            if user_input.lower() in ("anuluj", "a", "no", "n", "exit", "e", "out", "o"):
                return

            user_id = int(user_input) if user_input.isdigit() else -1
            query = session.query(User).filter(
                or_(
                    User.login == user_input,
                    User.id == user_input
                )
            ).first()

            if not query:
                print("\n❌ Nie znaleziono użytkownika o podanym loginie lub ID.")
            elif query.role == "admin":
                print("\n❌ Nie można usunąć użytkownika o roli 'admin'.")
            elif query.role != role:
                print(f"\n❌ Użytkownik {query.login} ma rolę '{query.role}', a nie '{role}'.")
            else:
                active_rentals = session.query(Vehicle).filter_by(
                    borrower_id=query.id, is_available=False).count()
                if active_rentals > 0:
                    print(f"\n🚫 Nie można usunąć użytkownika {query.login}, ponieważ ma aktywne wypożyczenie.")
                else:
                    print(f"\n✅ Znaleziono użytkownika: \n{query}\n")
                    confirm = yes_or_not_menu(f"Czy chcesz go usunąć?")

                    if confirm:
                        session.delete(query)
                        session.commit()
                        print(f"\n✅ Użytkownik {query.login} został usunięty z bazy.")
                    else:
                        print("\n❌ Anulowano usunięcie użytkownika.")

            # Pytanie o kolejne usunięcie
            again = yes_or_not_menu("\nCzy chcesz usunąć kolejnego użytkownika?")
            if again:
                break

        print("🔙 Powrót do menu.")
        return



def get_clients(session):
    print(">>> Przeglądanie klientów <<<")
    question = {
        "W": "Wszyscy",
        "T": "Tylko z wypożyczeniem",
        "B": "Bez wypożyczenia"
    }
    client_status = choice_menu("\nW jaki sposób chcesz przeglądać klientów?", question)

    if client_status == "w":
        clients = (
            session.query(User)
            .filter(User.role == "client")
            .order_by(User.last_name, User.first_name)
            .all()
        )
        if not clients:
            print("\n🚫 Brak klientów spełniających podane kryteria.")
            return
        print("\n>>> WSZYSCY KIENCI WYPOŻYCZALNI <<<\n")
        for client in clients:
            print(client, "\n")

    elif client_status == "t":
        borrower_ids = (
            session.query(Vehicle.borrower_id)
            .filter(Vehicle.is_available == False, Vehicle.borrower_id != None)
            .distinct()
            .all()
        )
        borrower_ids = [row[0] for row in borrower_ids]
        clients = (
            session.query(User)
            .filter(User.id.in_(borrower_ids), User.role == "client")
            .order_by(User.last_name, User.first_name)
            .all()
        )
        if not clients:
            print("\n🚫 Brak klientów spełniających podane kryteria.")
            return
        print("\n\n>>> KLIENCI Z WYPOŻYCZENIEM <<<\n")
        for client in clients:
            print(client, "\n")

        question = {
            "W": "Wyświetl szczegóły użytkownika",
            "P": "Powrót do menu główneg"
        }
        choice = choice_menu(f"\nCo chcesz teraz zrobić?")

        if choice == "p":
            return
        if choice == "w":

            user_id_input = get_positive_int("\nPodaj ID klient: ")

            client = session.query(User).filter(User.id == user_id_input).first()
            if not clients:
                print("❌ Nie znaleziono użytkownika o podanym ID.")
                return
            vehicles = session.query(Vehicle).filter(Vehicle.borrower_id == user_id_input).all()
            print("\n", client, ":")
            for vehicle in vehicles:
                print("\n      ", vehicle)
    elif client_status in "B":
        borrowed_ids = (
            session.query(Vehicle.borrower_id)
            .filter(Vehicle.is_available == False, Vehicle.borrower_id != None)
            .distinct()
            .all()
        )
        borrower_id_list = [id for (id,) in borrowed_ids]
        clients = (
            session.query(User)
            .filter(
                User.role == "client",
                not_(User.id.in_(borrower_id_list))
            )
            .order_by(User.last_name, User.first_name)
            .all()
        )
        if not clients:
            print("\n🚫 Brak klientów spełniających podane kryteria.")
            return
        print("\n\n>>> KLIENCI BEZ WYPOŻYCXZENIA <<<\n")
        for client in clients:
            print(client, "\n")


def get_users_by_role(session, role_name: str) -> List[User]:
    """Zwraca listę użytkowników o podanej roli."""
    return session.query(User).filter_by(role=role_name).all()


def add_client(session):
    return register_user(session, role="client")


def add_seller(session):
    return register_user(session, role="seller", auto=True)