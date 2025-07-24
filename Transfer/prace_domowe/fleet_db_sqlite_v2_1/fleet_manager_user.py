from fleet_validation import (
    get_valid_phone, get_valid_email, is_valid_phone, is_valid_email,
    validate_and_change_password, is_valid_password_format, is_valid_email_format)
from fleet_models_db import User, Vehicle
from fleet_database import Session
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy import or_, not_
from typing import List
import bcrypt
import getpass

def get_users_by_role(session, role_name: str) -> List[User]:
    """Zwraca listę użytkowników o podanej roli."""
    return session.query(User).filter_by(role=role_name).all()

def login_user():
    while True:
        print("\n=== LOGOWANIE DO SYSTEMU ===")
        login_or_email = input("\nLogin: ").strip()
        password = input("Hasło: ").strip()

        with Session() as session:
            user = session.query(User).filter(
                (User.login == login_or_email) | (User.email == login_or_email)
            ).first()

            if not user:
                print("\nNie znaleziono użytkownika.")
            elif not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
                print("\nBłędne hasło.")
            else:
                print(f"\nZalogowano jako {user.first_name} {user.last_name} ({user.role})")
                return user  #

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

def register_user(role="client", auto=False):
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
        with Session() as session:
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

    with Session() as session:
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

def add_client():
    return register_user(role="client")

def add_seller():
    return register_user(role="seller", auto=True)

def remove_user(role="client"):
    while True:
        with Session() as session:
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

            with Session() as session:
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
                        confirm = input(f"\n✅ Znaleziono użytkownika: \n{query}\n"
                                        f"Czy chcesz go usunąć? (TAK/NIE)? ").strip().lower()
                        if confirm in ("tak", "t", "yes", "y"):
                            session.delete(query)
                            session.commit()
                            print(f"\n✅ Użytkownik {query.login} został usunięty z bazy.")
                        else:
                            print("\n❌ Anulowano usunięcie użytkownika.")

        # Pytanie o kolejne usunięcie
        while True:
            again = input("\nCzy chcesz usunąć kolejnego użytkownika? (TAK/NIE): ").strip().lower()
            if again in ("tak", "t", "yes", "y"):
                break  # wraca do początku głównej pętli
            elif again in ("nie", "n", "no"):
                print("🔙 Powrót do menu.")
                return
            else:
                print("❌ Niepoprawna odpowiedź. Wpisz 'tak' lub 'nie'.")

def get_clients():
    print(">>> Przeglądanie klientów <<<")
    client_status = input(
        "\nW jaki sposób chcesz przeglądać klientów?"
        "\n(A) - wszyscy"
        "\n(T) - tylko z wypożyczeniem"
        "\n(N) - tylko bez wypożyczenia"
        "\n\nTwój wybór: "
    ).strip().lower()
    with Session() as session:
        if client_status in ("a", "wszyscy"):
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

        elif client_status in ("t", "tak", "z", "z wypożyczeniem","w"):
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
            while True:
                choice = input(
                    f"\nCo chcesz teraz zrobić:"
                    f"\n(P) - Powrót do menu główneg"
                    f"\n(W) - Wyświetl szczegóły użytkownika"
                    f"\n\nTwój wybór: "
                ).strip().lower()
                if choice not in ["p", "powrót", "w", "wyświetl"]:
                    print("\nZły wybór, spróbuj jeszcze raz.")
                    continue
                if choice in ["p", "powrót"]:
                    return
                if choice in ["w", "wyświetl"]:
                    while True:
                        user_input = input("\nPodaj ID klient: ").strip()
                        try:
                            id_input = int(user_input)
                            break  # poprawna liczba, wychodzimy z pętli
                        except ValueError:
                            print("❌ Podaj poprawny numer ID (liczbę całkowitą).")
                    client = session.query(User).filter(User.id == id_input).first()
                    if not clients:
                        print("❌ Nie znaleziono użytkownika o podanym ID.")
                        return
                    vehicles = session.query(Vehicle).filter(Vehicle.borrower_id == id_input).all()
                    print("\n", client, ":")
                    for vehicle in vehicles:
                        print("\n      ", vehicle)
        elif client_status in ("n", "nie", "bez", "bez wypożyczenia"):
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

def prompt_update_with_validation(field_name, current_value, validation_func):
    while True:
        val = input(f"{field_name} [{current_value}]: ").strip()
        if not val:
            return current_value  # ENTER = zostaje stara wartość
        if validation_func(val):
            return val
        else:
            print(f"❌ Niepoprawny {field_name.lower()}, spróbuj ponownie.")

def update_profile(user: User):
    while True:
        print(
            f"\n=== AKTUALIZACJA PROFILU UŻYTKOWNIKA ==="
            f"\nZalogowany jako: {user.first_name} {user.last_name} ({user.login})"
            f"\nCo chcesz zmienić?"
            f"\n1. Dane osobowe (imę, nazwisko, telefon, email, adres zamiszkania)"
            f"\n2. Hasło"
            f"\n3. Wyjdź bez zmian"
        )

        choice = input("\nWybierz opcję (1 -3)").strip()

        if choice == "1":
            with Session() as session:
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

                print(
                    f"\nNowe dane użytkownkia:"
                    f"\nImię: {new_first_name}"
                    f"\nNazwisko: {new_last_name}"
                    f"\nTelefon: {new_phone}"
                    f"\nEmail: {new_email}"
                    f"\nAdres: {new_address}"
                )

                contfirm = input("\nCzy zapisać zmiany? (tak/nie): ").strip().lower()
                if contfirm in ("tak", "t", "yes", "y"):
                    db_user.first_name = new_first_name
                    db_user.last_name = new_last_name
                    db_user.phone = new_phone
                    db_user.email = new_email
                    db_user.address = new_address
                    try:
                        session.commit()
                        print("✅ Dane zostały zaktualizowane.")
                        user.first_name = new_first_name
                        user.last_name = new_last_name
                        user.phone = new_phone
                        user.email = new_email
                        user.address = new_address
                    except IntegrityError:
                        session.rollback()
                        print("❌ Podany email lub telefon jest już zajęty przez innego użytkownika.")
                else:
                    print("❌ Anulowano aktualizację danych.")
        elif choice == "2":
            with Session() as session:
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


