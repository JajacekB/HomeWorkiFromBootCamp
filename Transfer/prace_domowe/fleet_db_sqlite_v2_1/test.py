from fleet_database import Session
from fleet_models_db import Vehicle

with Session() as session:
    types = session.query(Vehicle.type).distinct().all()
    print("Typy w bazie:", types)



def return_vehicle(user: User):
    with Session() as session:

        def update_costs_and_invoice(rental, vehicle, actual_return_date):

            start_date = rental.start_date
            planned_return = rental.planned_return_date
            planned_days = (planned_return - start_date).days + 1

            rental.actual_return_date = actual_return_date
            rental_days = (actual_return_date - start_date).days + 1
            if rental_days < 1:
                rental_days = 1

            if actual_return_date < planned_return:
                # Zwrot wcześniej
                base_cost = calculate_rental_cost(vehicle.cash_per_day, rental_days)
                late_fee = 0
                print(f"Zwrot wcześniej – nowy koszt na {rental_days} dni: {base_cost:.2f} zł")

            elif actual_return_date > planned_return:
                # Zwrot po terminie
                base_cost = calculate_rental_cost(vehicle.cash_per_day, planned_days)
                delay_days = (actual_return_date - planned_return).days
                late_fee = delay_days * vehicle.cash_per_day
                print(f"Zwrot po terminie o {delay_days} dni. Kara: {late_fee:.2f} zł")

            else:
                # Zwrot w terminie
                actual_return_date = planned_return
                rental.actual_return_date = actual_return_date
                base_cost = calculate_rental_cost(vehicle.cash_per_day, planned_days)
                late_fee = 0
                print(f"Zwrot w terminie. Koszt: {base_cost:.2f} zł")

            total_cost = base_cost + late_fee
            rental.total_cost = total_cost

            # Aktualizacja faktury
            if rental.invoice:
                rental.invoice.amount = total_cost
                rental.invoice.issue_date = actual_return_date

            # Aktualizacja pojazdu
            vehicle.is_available = True
            vehicle.borrower_id = None
            vehicle.return_date = None

        def process_return_for_vehicle(vehicle):

            # Znajdź aktywne wypożyczenie (związane z pojazdem i użytkownikiem)
            rental = session.query(RentalHistory).filter_by(
                vehicle_id=vehicle.id,
                user_id=vehicle.borrower_id
            ).order_by(RentalHistory.start_date.desc()).first()

            if not rental:
                print(f"Nie znaleziono historii wypożyczenia pojazdu {vehicle.vehicle_model}. Pomijam.")
                return False

            print(f"\nPojazd do zwrotu: {vehicle.brand} {vehicle.vehicle_model} (ID: {vehicle.vehicle_id})")
            print(f"📅 Planowany termin zwrotu: {rental.planned_return_date}\n")

            input_return_str = input(
                "Podaj datę faktycznego zwrotu (DD-MM-YYYY), lub naciśnij ENTER, aby przyjąć dzisiejszą datę: "
            ).strip()

            if not input_return_str:
                actual_return_date = date.today()
                return actual_return_date

            try:
                actual_return_date = datetime.strptime(input_return_str, "%d-%m-%Y").date()

            except ValueError:
                print("Niepoprawny format daty. Zwrot pominięty.")
                return False

            choice = input(
                f"\nCzy na pewno chcesz zwrócić pojazd:\n"
                f"{rental.vehicle}\n"
                f"Odpowiedz (tak/nie): "
            ).strip().lower()

            if choice in ("nie", "n", "no"):
                print("\nZwrot anulowany.")
                return

            update_costs_and_invoice(rental, vehicle, actual_return_date)

            # Aktualizacja pojazdu - zwrot
            vehicle.is_available = True
            vehicle.borrower_id = None
            vehicle.return_date = None

            session.commit()
            print(f"Pojazd {vehicle.vehicle_model} został zwrócony i jest dostępny.")
            return True

        if user.role == "client":
            # Pobierz pojazdy wypożyczone przez klienta
            rented_vehicles = session.query(Vehicle).filter(
                Vehicle.borrower_id == user.id,
                Vehicle.is_available == False
            ).all()

            if not rented_vehicles:
                print("Nie masz obecnie wypożyczonych pojazdów.")
                return

            for vehicle in rented_vehicles:
                print("\nCzy chcesz zwrócić ten pojazd?")
                print(f"{vehicle.brand} {vehicle.vehicle_model} (ID: {vehicle.vehicle_id})")
                answer = input("(tak/nie): ").strip().lower()
                if answer not in ("tak", "t", "yes", "y"):
                    continue
                process_return_for_vehicle(vehicle)

        elif user.role in ("seller", "admin"):
            while True:
                show_vehicles_rented_today(session)
                # Najpierw opcjonalnie wyświetl wypożyczone pojazdy dla danego użytkownika - albo od razu pytaj o ID pojazdu
                vehicle_id_str = input("\nPodaj ID pojazdu do zwrotu (lub wpisz 'koniec' aby wyjść): ").strip()
                if vehicle_id_str.lower() in ("koniec", "k"):
                    break

                try:
                    vehicle_id = int(vehicle_id_str)
                except ValueError:
                    print("Niepoprawne ID pojazdu.")
                    continue

                vehicle = session.query(Vehicle).filter_by(id=vehicle_id).first()
                if not vehicle:
                    print("Nie znaleziono pojazdu o podanym ID.")
                    continue

                if vehicle.is_available:
                    print("Ten pojazd jest już dostępny, nie jest wypożyczony.")
                    continue

                process_return_for_vehicle(vehicle)

        else:
            print("Funkcja dostępna tylko dla klientów i sprzedawców.")