from fleet_models_db import Vehicle, Car, Scooter, Bike, User, RentalHistory, Invoice, RepairHistory
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from fleet_database import Session, SessionLocal
from datetime import date, datetime, timedelta
from collections import defaultdict
from fleet_manager_user import get_users_by_role
from fleet_utils_db import (
    get_positive_int, get_positive_float,generate_repair_id,
    generate_vehicle_id, generate_reservation_id, generate_invoice_number,
    calculate_rental_cost, get_available_vehicles, get_unavailable_vehicle,
    update_database, recalculate_cost, get_return_date_from_user,
    show_vehicles_rented_today
)

def add_vehicles_batch():
    # Krok 1. Wybór typu pojazdu
    vehicle_type_map = {
        "samochód": "car",
        "skuter": "scooter",
        "rower": "bike"
    }
    type_prefix_map = {
        "samochód": "C",
        "skuter": "S",
        "rower": "B"
    }
    while True:
        vehicle_type_input = input("\nPodaj typ pojazdu (samochód, skuter, rower): ").strip().lower()

        if vehicle_type_input in vehicle_type_map:
            vehicle_type = vehicle_type_map[vehicle_type_input]
            prefix = type_prefix_map[vehicle_type_input]
            break

        print("\nNiepoprawny typ pojazdu. Spróbuj jeszcze raz")

    count = get_positive_int("\nIle pojazdów chcesz dodać? ")

    # Krok 2. Wprowadzenie wspólnych danych
    print("\n--- Dane wspólne dla całej serii ---")
    brand = input("Producent: ").strip().capitalize()
    model = input("Model: ").strip().capitalize()
    cash_per_day = get_positive_float("Cena za jedną dobę w zł: ")

    specific_fields = {}
    if vehicle_type == "car":
        specific_fields["size"] = input("Rozmiar (Miejski, Kompakt, Limuzyna, Crosover, SUV): ").strip().capitalize()
        specific_fields["fuel_type"] = input("Rodzaj paliwa (benzyna, diesel, hybryda, electric): ").strip()
    elif vehicle_type == "scooter":
        specific_fields["max_speed"] = get_positive_int("prędkość maksymalna (km/h): ")
    elif vehicle_type == "bike":
        specific_fields["bike_type"] = input("Typ roweru (MTB, Miejski, Szosowy): ").strip().capitalize()
        electric_input = input("Czy rower jest elektryczny (tak/nie): ").strip().lower()
        specific_fields["is_electric"] = electric_input in ("tak", "t", "yes", "y")

    # Krok 3. Wprowadzanie indywidualnych i tworzenie pojazdu
    vehicles = []
    with Session() as session:
        for i in range(count):
            print(f"\n--- POJAZD #{i + 1} ---")
            vehicle_id = generate_vehicle_id(prefix, session)
            while True:
                individual_id = input(
                    "Wpisz unikalny identyfikator pojazdu 😊\n"
                    "➡ Dla samochodu i skutera będzie to numer rejestracyjny,\n"
                    "➡ Dla roweru – numer seryjny (zazwyczaj znajdziesz go na ramie, okolice suportu):"
                    "?  "
                ).strip()
                if any(v.individual_id == individual_id for v in vehicles):
                    print("⚠️ Ten identyfikator już istnieje w tej serii. Podaj inny.")
                else:
                    break

            if vehicle_type == "car":
                vehicle = Car(
                    vehicle_id=vehicle_id,
                    brand=brand,
                    vehicle_model=model,
                    cash_per_day=cash_per_day,
                    size=specific_fields["size"],
                    fuel_type=specific_fields["fuel_type"],
                    individual_id=individual_id
                )
            elif vehicle_type == "scooter":
                vehicle = Scooter(
                    vehicle_id=vehicle_id,
                    brand=brand,
                    vehicle_model=model,
                    cash_per_day=cash_per_day,
                    max_speed=specific_fields["max_speed"],

                    individual_id=individual_id
                )
            elif vehicle_type == "bike":
                vehicle = Bike(
                    vehicle_id=vehicle_id,
                    brand=brand,
                    vehicle_model=model,
                    cash_per_day=cash_per_day,
                    bike_type=specific_fields["bike_type"],
                    is_electric=specific_fields["is_electric"],
                    individual_id=individual_id
                )
            session.add(vehicle)
            session.flush()

            vehicles.append(vehicle)

        # Krok 4. Przegląd wpisanych pojazdów
        print("\n--- PRZEGLĄD POJAZDÓW ---")
        for i, v in enumerate(vehicles, 1):
            print(f"\n[{i}] {v}")

        # Krok 5. Czy wszystko się zgadza? Czy poprawić?
        while True:
            answer = input(
                f"\nSprawdź uważnie czy wszystko się zgadza?"
                f"\nWybierz opcję: (Tak/Nie): "
            ).strip().lower()
            if answer in ("tak", "t", "yes", "y"):
                break
            elif answer in ("nie", "n", "no"):
                option = input(
                    f"\nWybierz sposób edycji:"
                    f"\n👉 Numer pojazdu ➡ tylko ten jeden"
                    f"\n👉 'Wszystko' ➡ zastosuj zmiany do wszystkich"
                    f"\nPodaj odpowiedź: "
                ).strip().lower()
                if option == "wszystko":
                    print("\n--- Popraw wspólne dane (ENTER = brak zmian) ---")
                    new_brand = input(f"Producent ({brand}): ").strip()
                    new_model = input(f"Model ({model}): ").strip()
                    new_cash = input(f"Cena za dobę ({cash_per_day}): ").strip()
                    if new_brand: brand = new_brand.capitalize()
                    if new_model: model = new_model.capitalize()
                    if new_cash:
                        cash_per_day = get_positive_float("Nowa cena za dobę: ")

                    if vehicle_type == "car":
                        new_size = input(f"Rozmiar ({specific_fields['size']}): ").strip()
                        new_fuel = input(f"Paliwo ({specific_fields['fuel_type']}): ").strip()
                        if new_size: specific_fields['size'] = new_size.capitalize()
                        if new_fuel: specific_fields['fuel_type'] = new_fuel

                    elif vehicle_type == "scooter":
                        new_speed = input(f"Prędkość maks. ({specific_fields['max_speed']}): ").strip()
                        if new_speed:
                            specific_fields["max_speed"] = get_positive_int("Nowa prędkość maksymalna: ")

                    elif vehicle_type == "bike":
                        new_type = input(f"Typ roweru ({specific_fields['bike_type']})").strip().capitalize()
                        new_electric = input(f"Elektryczny ("
                                            f"{'tak' if specific_fields['is_electric'] else 'nie'}): ").strip().lower()
                        if new_type: specific_fields["bike_type"] = new_type.capitalize()
                        if new_electric:
                            specific_fields["is_electric"] = new_electric in ("tak", "t", "yes", "y")

                    # Krok 6 Aktualizacja wszystkich w serii
                    for v in vehicles:
                        v.brand = brand
                        v.vehicle_model = model
                        v.cash_per_day = cash_per_day
                        for k, val in specific_fields.items():
                            setattr(v, k, val)
                    print("✅ Dane wspólne zostały zaktualizowane.")
                    continue
                elif option.isdigit() and 1 <= int(option) <=len(vehicles):
                    idx = int(option) - 1
                    new_id = input("Nowy identyfikator: ").strip()
                    if any(v.individual_id == new_id for i, v in enumerate(vehicles) if i != idx):
                        print("❌ Taki identyfikator już istnieje.")
                    else:
                        vehicles[idx].individual_id = new_id
                        print("✅ Zmieniono indywidualny identyfikator.")
                        continue
                else:
                    print("🤔 Nie rozumiem, spróbuj jeszcze raz.")
                    continue
            else:
                print("🤔 Wpisz 'tak' lub 'nie'.")

        # Krok 7 Zapis do bazy
        existing_ids = [v.individual_id for v in vehicles]
        if len(existing_ids) != len(set(existing_ids)):
            print("❌ Duplikat identyfikatorów indywidualnych w serii. Operacja przerwana.")
            return

        try:
            for v in vehicles:
                session.add(v)
            session.commit()
            session.flush()
            print(f"\n✅ Dodano {len(vehicles)} pojazdów do bazy.")
        except IntegrityError as e:
            session.rollback()
            print(f"\n❌ Błąd zapisu: {e}. Wszystkie zmiany zostały wycofane.")

def remove_vehicle():
    vehicle_id = input("\nPodaj numer referencyjny pojazdu, który chcesz usunąć: ").strip().upper()

    with Session() as session:
        vehicle = session.query(Vehicle).filter_by(vehicle_id=vehicle_id).first()

        if not vehicle:
            print("❌ Nie znaleziono pojazdu.")
            return

        if not vehicle.is_available:
            print("🚫 Pojazd jest niedostępny. Nie można go usunąć")
            return

        print(f"\nCzy chcesz usunąć pojad - {vehicle}")
        while True:
            choice = input("\n(Tak/Nie): ").strip().lower()
            if choice in ("tak", "t", "yes", "y"):
                session.delete(vehicle)
                session.commit()
                print("\n✅ Pojazd został usunięty ze stanu wypożyczalni.")
                return
            elif choice in ("nie", "n", "no"):
                print("\n❌ Usuwanie pojazdu anulowane.")
                return
            else:
                print("\n❌ Niepoprawna odpowiedź. spróbuj ponownie.")

def get_vehicle(only_available: bool = False):
    print("\n>>> Przeglądanie pojazdów <<<")

    if only_available:
        status = "available"
    else:
        status_map = {
            "w": "all",
            "d": "available",
            "n": "rented"
        }

        while True:
            status_input = input(
                "\nKtóre pojazdy chcesz przejrzeć:"
                "\n (W) - wszystkie lub naciśnij Enter"
                "\n (D) - dostępne"
                "\n (N) - niedostępne"
                "\nWybierz [W/D/N]: "
            ).strip().lower()

            if status_input == "":
                status = "all"
                break

            if status_input in status_map:
                status = status_map[status_input]
                break
            print("\n❌ Zły wybór statusu pojazdu, spróbuj jeszcze raz.")

    vehicle_type_map = {
        "wszystkie": "all",
        "samochód": "car",
        "skuter": "scooter",
        "rower": "bike"
    }

    while True:
        vehicle_type_input = input(
            "\nJakiego typu pojazdy chcesz zobaczyć:\n"
            "\n(Wszystkie) lub naciśnij Enetr"
            "\n(Samochód)"
            "\n(Skuter)"
            "\n(Rower)"
            "\nWybierz typ: "
        ).strip().lower()

        if vehicle_type_input == "":
            vehicle_type = "all"
            break

        if vehicle_type_input in vehicle_type_map:
            vehicle_type = vehicle_type_map[vehicle_type_input]
            break
        print("\n❌ Zły wybór typu pojazdu, spróbuj jeszcze raz.")

    with Session() as session:
        vehicles = []

        if status == "available":
            vehicles = get_available_vehicles(session, vehicle_type=vehicle_type)

        elif status == "rented":
            unavailable_ids = get_unavailable_vehicle(session, vehicle_type=vehicle_type)
            if not unavailable_ids:
                print("\n🚫 Brak niedostępnych pojazdów na dziś.")
                return

            vehicles = session.query(Vehicle).filter(Vehicle.id.in_(unavailable_ids)).all()

        else:
            vehicles = session.query(Vehicle).all()

        if not vehicles:
            print("🚫 Brak pojazdów spełniających podane kryteria.")
            return

        # Przygotowujemy gotowe stringi WEWNĄTRZ sesji
        output_lines = []
        current_type = None
        for vehicle in sorted(vehicles, key=lambda v: (v.type, v.vehicle_id)):
            if vehicle.type != current_type:
                current_type = vehicle.type
                output_lines.append(f"\n--- {current_type.upper()} ---\n")
            output_lines.append(str(vehicle) + "\n")

    # Po wyjściu z with sesja jest zamknięta,
    # ale mamy już gotowe teksty do wyświetlenia
    print("\n=== POJAZDY ===")
    for line in output_lines:
        print(line)


def rent_vehicle_for_client(user: User):
    print(f"\n>>> Rezerwacja dla klienta <<<")

    if user.role.lower() not in ("seller", "admin"):
        print("🚫 Tylko sprzedawcy i administratorzy mogą rezerwować pojazdy dla klientów.")
        return

    with Session() as session:
        while True:
            client_id = get_positive_int(
                "\nPodaj id klienta, dla którego chcesz wynająć pojazd (ENTER = Ty sam): ",
                allow_empty=True
            )

            if client_id is None:
                print(f"\nWypożyczasz pojazd dla siebie: {user.first_name} {user.last_name} ({user.login}).")
                rent_vehicle(user)
                return


            client = session.query(User).filter_by(id=client_id).first()
            if not client:
                print("❌ Nie znaleziono użytkownika o podanym ID.")
                continue

            print(f"\nZnaleziony klient: {client.id}, rola: '{client.role}'")  # diagnostyka

            if client.role.lower() != "client":
                print("🚫 Ten użytkownik nie ma roli klienta.")
                continue

            print(f"\nWypozyczasz pojazd dla: [{client.id}] - {client.first_name} {client.last_name}.")

            rent_vehicle(client, session=session)
            return


def rent_vehicle(user: User, session=None):
    if session is None:
        with Session() as session:
            return rent_vehicle(user, session=session)

    print("\n=== WYPOŻYCZENIE POJAZDU ===\n")

    # Wprowadzenie danych wyporzyczenia (typ pojazdu i okres wypożyczenia)
    vehicle_type_map = {
        "samochód": "car",
        "skuter": "scooter",
        "rower": "bike"
    }

    while True:
        vehicle_type_input = input(
            "\nWybierz typ pojazdu (Samochód, Skuter, Rower): "
        ).strip().lower()

        if vehicle_type_input in vehicle_type_map:
            vehicle_type = vehicle_type_map[vehicle_type_input]
            break

        else:
            print("\nZły wybór. Spróbuj jeszcz raz")
            continue

    while True:

        start_date_str = input(
            "\nData rozpoczęcia (DD-MM-YYYY) Enter = dziś: "
        ).strip()
        end_date_str = input("\nData zakończenia (DD-MM-YYYY): ").strip()

        try:

            if start_date_str:
                start_date = datetime.strptime(start_date_str, "%d-%m-%Y").date()
            else:
                start_date = date.today()

            planned_return_date = datetime.strptime(end_date_str, "%d-%m-%Y").date()
            break

        except ValueError:
            print("❌ Niepoprawny format daty.")
            continue

    # Krok 1: Znajdź dostępne pojazdy
    available_vehicles = get_available_vehicles(session, start_date, planned_return_date, vehicle_type)

    if not available_vehicles:
        print("\n🚫 Brak dostępnych pojazdów w tym okresie.")
        return

    # Krok 2: Grupuj pojazdy
    if vehicle_type == "car":
        grouped = defaultdict(list)
        for v in (available_vehicles):
            key = (v.brand, v.vehicle_model, v.cash_per_day, v.size, v.fuel_type)
            grouped[key].append(v)

        tabele_width = 98

        print("\nDostępne grupy pojazdów:\n")

        print(f"|{'L.p.':>5}| {'Marka':<15}| {'Model':<15}| {'Rodzaj':<11}| {'Paliw':<11}|{'Cena za dzień':>16} |{'Dostępnych':^12}|")
        print(tabele_width * "_")

        for index, ((brand, model, price, size, fuel_type), cars) in enumerate(grouped.items(), start=1):
            formated_price = f"{price:.2f} zł"

            print(
                f"|{index:>4} | {brand:<15}| {model:<15}| {size:<11}| {fuel_type:<11}| {formated_price:>15} |{len(cars):^12}|"
            )

    elif vehicle_type == "scooter":
        grouped = defaultdict(list)
        for v in (available_vehicles):
            key = (v.brand, v.vehicle_model, v.cash_per_day, v.max_speed)
            grouped[key].append(v)

        tabele_width = 86

        print("\nDostępne grupy pojazdów:\n")

        print(
            f"|{'L.p.':>5}| {'Marka':<15}| {'Model':<15}|{'prędkość maX':>13} |{'Cena za dzień':>15} |{'Dostępnych':^12}|")
        print(tabele_width * "_")

        for index, ((brand, model, price, max_speed), scooter) in enumerate(grouped.items(), start=1):
            formated_price = f"{price:.2f} zł"

            print(
                f"|{index:>4} | {brand:<15}| {model:<15}|{max_speed:>13} | {formated_price:>14} |{len(scooter):^11}|"
            )

    elif vehicle_type == "bike":
        grouped = defaultdict(list)
        for v in (available_vehicles):
            key = (v.brand, v.vehicle_model, v.cash_per_day, v.bike_type, v.is_electric)
            grouped[key].append(v)

        tabele_width = 95

        print("\nDostępne grupy pojazdów:\n")

        print(
            f"|{'L.p.':>5}| {'Marka':<15}| {'Model':<15}| {'Rodzaj roweru':<21}|{'Cena za dzień':>16} |{'Dostępnych':^12}|")
        print(tabele_width * "_")

        for index, ((brand, model, price, bike_type, is_electric), bike) in enumerate(grouped.items(), start=1):
            formated_price = f"{price:.2f} zł"
            if is_electric:
                bike_variety = f"{bike_type} - elektryczny"
            else:
                bike_variety = f"{bike_type} - klasyczny"

            print(
                f"|{index:>4} | {brand:<15}| {model:<15}| {bike_variety:<21}| {formated_price:>15} |{len(bike):^12}|"
            )

    # Krok 3: Wybór modelu
    while True:
        chosen_model = input("\nPodaj model pojazdu do wypożyczenia: ").strip()
        matching_vehicles = [v for v in available_vehicles if v.vehicle_model.lower() == chosen_model.lower()]

        if not matching_vehicles:
            print("🚫 Nie znaleziono pojazdu o podanym modelu. Wybierz ponownie.")
            continue

        # Szukaj najmniej wypożyczanego w bazie

        # Lista ID dostępnych pojazdów danego modelu
        matching_ids = [v.id for v in matching_vehicles]

        result = session.query(
            Vehicle,
            func.count(RentalHistory.id).label("rental_count")
        ).outerjoin(RentalHistory).filter(
            Vehicle.id.in_(matching_ids)
        ).group_by(Vehicle.id).order_by("rental_count").first()

        if result:
            chosen_vehicle, rental_count = result
        else:
            # fallback — pierwszy dostępny z listy
            chosen_vehicle = matching_vehicles[0]
            rental_count = 0
        print(
            f"\n✅ Wybrano pojazd: {chosen_vehicle.brand} {chosen_vehicle.vehicle_model}"
            f" (ID: {chosen_vehicle.id}) — wypożyczany {rental_count or 0} razy.")

        if not chosen_vehicle:
            print("🚫 Nie znaleziono pojazdu o podanym modelu. Wybierz ponownie.")
        else:
            break

    # Krok 4: Oblicz koszty i rabaty
    rent_days = (planned_return_date - start_date).days
    base_cost = rent_days * chosen_vehicle.cash_per_day
    total_cost, discount_value, discount_type = calculate_rental_cost(
        user, chosen_vehicle.cash_per_day, rent_days
    )

    # Krok 5: Potwierdzenie
    print(f"\nKoszt podstawowy: {base_cost} zł")
    confirm = input(
        f"Całkowity koszt wypożyczenia po rabatach: {total_cost:.2f} zł.\n"
        f"Czy potwierdzasz? (Tak/Nie): "
    ).strip().lower()
    if confirm not in ("tak", "t", "yes", "y"):
        print("\n🚫 Anulowano rezerwację.")
        return

    # Krok 6: Zapis danych do bazy
    reservation_id = generate_reservation_id()
    invoice_number = generate_invoice_number(planned_return_date)

    # Aktualizacja pojazdu
    chosen_vehicle.is_available = False
    chosen_vehicle.borrower_id = user.id
    chosen_vehicle.return_date = planned_return_date
    session.add(chosen_vehicle)

    # Historia wypożyczeń
    rental = RentalHistory(
        reservation_id=reservation_id,
        user_id=user.id,
        vehicle_id=chosen_vehicle.id,
        start_date=start_date,
        planned_return_date=planned_return_date,
        base_cost=base_cost,
        total_cost=total_cost
    )
    session.add(rental)
    session.flush()

    # Faktura
    invoice = Invoice(
        invoice_number=invoice_number,
        rental_id=rental.id,
        amount=total_cost,
        issue_date=planned_return_date
    )

    session.add_all([invoice])
    session.commit()

    print(
        f"\n✅ Zarezerwowałeś {chosen_vehicle.brand} {chosen_vehicle.vehicle_model} "
        f"od {start_date} do {planned_return_date}.\nMiłej jazdy!"
    )

def return_vehicle(user):
    # Pobieranie aktywnie wynajętych i zarejestrowanych pojazdów
    with Session() as session:

        if user.role == "client":

            rented_vehs = session.query(RentalHistory).filter(
                RentalHistory.user_id == user.id,
                RentalHistory.actual_return_date.is_(None)
            ).all()

            vehicles = session.query(Vehicle).filter(Vehicle.borrower_id == user.id).order_by(
                Vehicle.return_date.asc()).all()

            print(type(vehicles))

        else:
            print("Lipa")
            unavailable_veh = session.query(Vehicle).filter(Vehicle.is_available != True).all()
            unavailable_veh_ids = [v.id for v in unavailable_veh]

            if not unavailable_veh:
                print("\nBrak wynajętych pojazdów")
                return

            # lista wynajętych pojazdów
            rented_vehs = session.query(RentalHistory).filter(
                RentalHistory.vehicle_id.in_(unavailable_veh_ids),
                RentalHistory.actual_return_date.is_(None)
            ).order_by(RentalHistory.planned_return_date.asc()).all()

            reservation_ids = [i.reservation_id for i in rented_vehs]
            rented_ids = [r.vehicle_id for r in rented_vehs]

            vehicles = session.query(Vehicle).filter(Vehicle.id.in_(rented_ids)).order_by(Vehicle.return_date).all()

        table_wide = 91
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

        veh_ids = [z.id for z in vehicles]

        print(f"\nLista wynajętych pojazdów:\n")
        print(
            f"|{'ID.':>5}|{'Data zwrotu':>21} | {'Marka':^14} | {'Model':^14} |{'Nr rejestracyjny/seryjny':>25} |"
        )
        print(table_wide * "_")
        for p in vehicles:
            date_obj = p.return_date
            day = date_obj.day
            month_name = month_pl[date_obj.month]
            year = date_obj.year
            date_str = f"{day}-{month_name}_{year}"

            print(
                f"|{p.id:>4} |{date_str:>21} |{p.brand:>15} |{p.vehicle_model:>15} | {p.individual_id:>24} |"
            )

        # Wybór pojazdu do zwrotu i potwierdzenie chęci anulowania wynajmu lub rezerwacji
        choice = get_positive_int(
            f"\nKtóry pojazd chcesz zwrócić?"
            f"\nPodaj nr ID: "
        )

        vehicle = session.query(Vehicle).filter(Vehicle.id == choice).first()
        print(
            f"\nCzy na pewno chcesz zwrócić pojazd: "
            f"\n{vehicle}"
        )
        while True:
            choice = input(
                f"Wybierz (tak/nie): "
            ).strip().lower()

            if choice in ("nie", "n", "no"):
                print("\nZwrot pojazdu anulowany.")
                return

            elif choice in ("tak", "t", "yes", "y"):

                actual_return_date_input = get_return_date_from_user(session)

                # Znajdź odpowiednią rezerwację (reservation_id) dla wybranego pojazdu i użytkownika
                selected_rental = None
                for rental in rented_vehs:
                    if rental.vehicle_id == vehicle.id and rental.user_id == vehicle.borrower_id:
                        selected_rental = rental
                        break

                if selected_rental is None:
                    print("Nie znaleziono rezerwacji odpowiadającej wybranemu pojazdowi.")
                    return

                total_cost, overdue_fee_text = recalculate_cost(
                    session, user, vehicle, actual_return_date_input, selected_rental.reservation_id
                )

                print(
                    f"\n💸 — KKW (Rzeczywisty Koszt Wynajmu) wynosi: {total_cost} zł.{overdue_fee_text}"
                )
                print(
                    f"\nCzy na pewno chcesz zwrócić pojazd: "
                    f"\n{vehicle}"
                )
                choice = input(
                    f"Wybierz (tak/nie): "
                ).strip().lower()

                while True:
                    if choice in ("nie", "n", "no"):
                        print("\nZwrot pojazdu anulowany.")
                        return

                    elif choice in ("tak", "t", "yes", "y"):
                        update_database(session, vehicle, actual_return_date_input, total_cost, selected_rental.reservation_id)

                    print(
                        f"\nPojazd {vehicle} został pomyślnie zwrócony."
                        f"\nKoszty rozliczone."
                        f"\nTranzakcja zakończona"
                    )
        return True

def repair_vehicle(user):
    with SessionLocal() as session:
        available_vehicles = get_available_vehicles(session)
        if not available_vehicles:
            print("Brak dostępnych pojazdów do naprawy.")
            return

        print("\nDostępne pojazdy do naprawy:")
        for v in available_vehicles:
            print(f"- {v.vehicle_model} ({v.type}), ID: {v.id}, Numer: {v.individual_id}")

        try:
            vehicle_id = int(input("Podaj ID pojazdu do przekazania do naprawy: "))
        except ValueError:
            print("Błędne ID.")
            return

        vehicle = session.query(Vehicle).filter_by(id=vehicle_id, is_available=True).first()
        if not vehicle:
            print("Nie znaleziono pojazdu lub jest niedostępny.")
            return

        workshops = get_users_by_role("workshop", session)
        if not workshops:
            print("Brak zdefiniowanych użytkowników warsztatu.")
            return

        print("\nDostępne warsztaty:")
        for idx, w in enumerate(workshops, 1):
            print(f"{idx}. {w.first_name} {w.last_name} ({w.login})")

        workshop_choice = get_positive_int("Wybierz numer warsztatu: ") - 1
        selected_workshop = workshops[workshop_choice]

        repair_days = get_positive_int("Podaj liczbę dni naprawy: ")
        planned_end_date = datetime.today().date() + timedelta(days=repair_days)

        repair_cost_per_day = get_positive_float("\nPodaj jednostkowy koszt naprawy: ")
        repair_cost = repair_cost_per_day * repair_days

        description = input("\nKrótko opisz zakres naprawy: ")

        while True:
            confirm = input(
                f"\nPotwierdź oddanie do naprawy pojazdu:\n {vehicle}"
                f"\nKoszt naprawy {repair_cost} zł"
                f"\nWybierz (tak/nie): "
            ).strip().lower()
            if confirm not in ("tak", "t", "yes", "y"):
                print("\nNaprawa anulowana.")
                return

            # Historia naprawy
            repair_id = generate_repair_id()

            repair = RepairHistory(
                repair_id=repair_id,
                vehicle_id=vehicle.id,
                mechanic_id=selected_workshop.id,
                start_date=datetime.today().date(),
                planned_end_date=planned_end_date,
                actual_return_date=None,  # Domyślnie brak
                cost=repair_cost,
                description=description
            )
            session.add(repair)

            # Aktualizacja pojazdu
            vehicle.is_available = False
            vehicle.borrower_id = selected_workshop.id
            vehicle.return_date = planned_end_date  # Jeśli jeszcze używasz tej kolumny w Vehicle

            session.commit()
            print(
                f"\nPojazd {vehicle.brand} {vehicle.vehicle_model} {vehicle.individual_id}"
                f"\nprzekazany do warsztatu: {selected_workshop.first_name} {selected_workshop.last_name} do dnia {planned_end_date}."
            )
            return