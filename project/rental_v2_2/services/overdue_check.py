# directory: services
# file: overdue_check.py

from datetime import date, datetime
from models.vehicle import Vehicle
from database.base import Session
from models.repair_history import RepairHistory
from models.rental_history import RentalHistory
from services.rental_costs import calculate_rental_cost


def check_overdue_vehicles(user, session: Session):
    if user.role not in ("seller", "admin"):
        return

    print("\n=== Sprawdzanie przeterminowanych zwrotów pojazdów i powrotów z naprawy ===")

    today = date.today()
    overdue_vehicles = session.query(Vehicle).filter(
        Vehicle.return_date.isnot(None),
        Vehicle.return_date < today,
        Vehicle.is_available == False
    ).order_by(Vehicle.return_date.asc()).all()

    if not overdue_vehicles:
        print("Brak przeterminowanych zwrotów.\n")
        return

    for vehicle in overdue_vehicles:
        print(f"\nPojazd: {vehicle.brand} {vehicle.vehicle_model} (ID: {vehicle.vehicle_id})")
        print(f"Planowany zwrot: {vehicle.return_date}")
        answer = input("Czy pojazd został zwrócony? (tak/nie): ").strip().lower()

        if answer not in ("tak", "t", "yes", "y"):
            print("Pojazd nadal wypożyczony, sprawdzimy go ponownie jutro.")
            continue

        actual_return_str = input("Podaj datę zwrotu (DD-MM-YYYY): ").strip()
        try:
            actual_return_date = datetime.strptime(actual_return_str, "%d-%m-%Y").date()
        except ValueError:
            print("Niepoprawny format daty, pomijam ten pojazd.")
            continue

        rental = session.query(RentalHistory).filter_by(
            vehicle_id=vehicle.id,
            user_id=vehicle.borrower_id
        ).order_by(RentalHistory.planned_return_date.desc()).first()

        repair = session.query(RepairHistory).filter_by(
            vehicle_id=vehicle.id,
            mechanic_id=vehicle.borrower_id
        ).order_by(RepairHistory.planned_end_date.desc()).first()

        if rental and repair:
            print(f"\n⚠️ UWAGA! Pojazd ID: {vehicle.id} figuruje jako wypożyczony i w naprawie!")
            choice = input("\nCzy chcesz: (I) Ignoruj / (N) anuluj Naprawę / (W) anuluj Wypożyczenie: ").strip().lower()
            if choice == "i": continue
            elif choice == "n": repair.actual_return_date = date.today()
            elif choice == "w": rental.actual_return_date = date.today()
            else:
                print("Nieprawidłowy wybór.")
                continue
            session.commit()

        elif repair:
            repair.actual_return_date = actual_return_date
            vehicle.is_available = True
            vehicle.borrower_id = None
            vehicle.return_date = None
            session.commit()
            print("✅ Powrót z naprawy zarejestrowany.")

        elif rental:
            rental.actual_return_date = actual_return_date
            planned = rental.planned_return_date
            delay = (actual_return_date - planned).days

            if actual_return_date == planned:
                rental.late_fee = 0.0
                rental.total_cost = rental.base_cost
                print("✅ Zwrot o czasie. Koszt bez zmian.")

            elif actual_return_date < planned:
                rental.late_fee = 0.0
                real_days = (actual_return_date - rental.start_date).days + 1
                new_total = calculate_rental_cost(user, vehicle.cash_per_day, real_days)
                rental.total_cost = new_total
                print(f"✅ Zwrot przed czasem. Nowy koszt: {new_total:.2f} zl")

            else:
                extra_days = (actual_return_date - planned).days
                extra_fee = extra_days * vehicle.cash_per_day
                rental.late_fee = extra_fee
                rental.total_cost = rental.base_cost + extra_fee
                print(f"⚠️ Zwrot po terminie. Kara: {extra_fee:.2f} zl")

            # Faktura
            if rental.invoice:
                rental.invoice.amount = rental.total_cost
            else:
                print("Brak faktury do aktualizacji.")

            # Aktualizacja pojazdu
            vehicle.is_available = True
            vehicle.borrower_id = None
            vehicle.return_date = None
            session.commit()
            print(f"✅ Zaktualizowano dane pojazdu: {vehicle.vehicle_model}")

    print("\n=== Koniec sprawdzania przeterminowanych zwrotów ===\n")
