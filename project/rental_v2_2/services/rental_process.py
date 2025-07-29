# directory: services
# file: rental_proces.py

from sqlalchemy import func
from collections import defaultdict
from datetime import date, datetime
from database.base import Session
from models.user import User
from models.vehicle import Vehicle
from models.rental_history import RentalHistory
from models.invoice import Invoice
from services.utils import get_positive_int
from services.vehicle_avability import get_available_vehicles
from services.rental_costs import calculate_rental_cost, recalculate_cost
from services.id_generators import generate_reservation_id, generate_invoice_number
from services.user_imput import get_return_date_from_user
from services.database_update import update_database





def rent_vehicle_for_client(session, user: User):
    print(f"\n>>> Rezerwacja dla klienta <<<")

    if user.role.lower() not in ("seller", "admin"):
        print("🚫 Tylko sprzedawcy i administratorzy mogą rezerwować pojazdy dla klientów.")
        return

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

    # Krok 2: Sortuj i grupuj pojazdy
    if vehicle_type == "car":
        vehicles_sorted = sorted(
            available_vehicles,
            key=lambda v: (v.cash_per_day, v.brand, v.vehicle_model, v.fuel_type)
        )
        grouped = defaultdict(list)
        for v in (vehicles_sorted):
            key = (v.brand, v.vehicle_model, v.cash_per_day, v.size, v.fuel_type)
            grouped[key].append(v)

        tabele_width = 98

        print("\nDostępne grupy pojazdów:\n")

        print(f"|{'L.p.':>5}| {'Marka':<15}| {'Model':<15}| {'Rodzaj':<11}| {'Paliwo':<11}|{'Cena za dzień':>16} |{'Dostępnych':^12}|")
        print(tabele_width * "_")

        for index, ((brand, model, price, size, fuel_type), cars) in enumerate(grouped.items(), start=1):
            formated_price = f"{price:.2f} zł"

            print(
                f"|{index:>4} | {brand:<15}| {model:<15}| {size:<11}| {fuel_type:<11}| {formated_price:>15} |{len(cars):^12}|"
            )

    elif vehicle_type == "scooter":
        vehicles_sorted = sorted(
            available_vehicles,
            key=lambda v: (v.cash_per_day, v.brand, v.vehicle_model)
        )
        grouped = defaultdict(list)
        for v in (vehicles_sorted):
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
        vehicles_sorted = sorted(
            available_vehicles,
            key=lambda v: (v.cash_per_day, v.brand, v.vehicle_model)
        )
        grouped = defaultdict(list)
        for v in (vehicles_sorted):
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

def return_vehicle(session, user):
    # Pobieranie aktywnie wynajętych i zarejestrowanych pojazdów

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

            total_cost, extra_fee, overdue_fee_text = recalculate_cost(
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
                    update_database(session, vehicle, actual_return_date_input, total_cost, extra_fee,selected_rental.reservation_id)

                print(
                    f"\nPojazd {vehicle} został pomyślnie zwrócony."
                    f"\nKoszty rozliczone."
                    f"\nTranzakcja zakończona"
                )
                return True