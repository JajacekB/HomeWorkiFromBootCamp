from fleet_models_db import Vehicle, RentalHistory, RepairHistory
from datetime import date, datetime, timedelta
from fleet_utils_db import (get_vehicles_unavailable_today,
get_available_vehicles, generate_vehicle_id, generate_reservation_id,
generate_invoice_number, generate_repair_id, get_positive_int,
get_positive_float


)


def check_overdue_vehicles(user, session):
    if user.role not in ("seller", "admin"):
        return  # tylko dla seller i admin

    print("\n=== Sprawdzanie przeterminowanych zwrotów pojazdów ===")

    today = date.today()
    overdue_vehicles = session.query(Vehicle).filter(
        Vehicle.return_date != None,
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

        if answer in ("tak", "t", "yes", "y"):
            actual_return_str = input("Podaj datę zwrotu (DD-MM-YYYY): ").strip()
            try:
                actual_return_date = datetime.strptime(actual_return_str, "%d-%m-%Y").date()
            except ValueError:
                print("Niepoprawny format daty, pomijam ten pojazd.")
                continue

            # Oblicz opóźnienie
            delay_days = (actual_return_date - vehicle.return_date).days
            delay_days = max(0, delay_days)

            # Szukamy powiązanej historii wypożyczenia (ostatniej rezerwacji tego pojazdu i tego wypożyczającego)
            rental = session.query(RentalHistory).filter_by(
                vehicle_id=vehicle.id,
                user_id=vehicle.borrower_id
            ).order_by(RentalHistory.end_date.desc()).first()

            if not rental:
                print("Nie znaleziono historii wypożyczenia tego pojazdu dla tego użytkownika.")
                continue

            # Obliczamy dodatkową opłatę za opóźnienie (100% ceny za dzień)
            additional_fee = delay_days * vehicle.cash_per_day
            print(f"Dodatkowa opłata za {delay_days} dni opóźnienia: {additional_fee:.2f} zł")

            # Aktualizujemy end_date w RentalHistory (przedłużenie wypożyczenia)
            if actual_return_date > rental.end_date:
                print(f"Przedłużam wypożyczenie z {rental.end_date} do {actual_return_date}")
                rental.end_date = actual_return_date

                # Aktualizujemy całkowity koszt (bez rabatów, bo to dodatkowe dni)
                base_days = (rental.end_date - rental.start_date).days + 1  # liczymy dni od początku do nowej daty
                new_total_cost = base_days * vehicle.cash_per_day
                rental.total_cost = new_total_cost

                # Aktualizujemy fakturę powiązaną z rezerwacją (Invoice)
                invoice = rental.invoice
                if invoice:
                    invoice.amount = new_total_cost
                    print(f"Zaktualizowano kwotę faktury do: {invoice.amount:.2f} zł")
                else:
                    print("Brak faktury powiązanej z tą rezerwacją, nie można zaktualizować kwoty.")

            # Aktualizacja pojazdu - zwrot i czyszczenie danych
            vehicle.is_available = True
            vehicle.borrower_id = None
            vehicle.return_date = None

            session.commit()
            print(f"Pojazd {vehicle.vehicle_model} został zwrócony i jest dostępny.")

        else:
            print("Pojazd nadal wypożyczony, sprawdzimy go ponownie jutro.")

    print("\n=== Koniec sprawdzania przeterminowanych zwrotów ===\n")
