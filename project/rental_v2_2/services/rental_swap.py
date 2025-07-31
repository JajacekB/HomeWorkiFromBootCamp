

from datetime import date
from models.user import User
from models.rental_history import RentalHistory
from services.vehicle_avability import get_available_vehicles
from services.rental_costs import calculate_rental_cost

def update_database_after_vehicle_swap(
        session, original_vehicle, replacement_vehicle, broken_rental, different_price: bool):
    # liczymy koszt za dotychczasowy najem
    today = date.today()

    old_rental_cost = broken_rental.base_cost
    old_rental_period = (broken_rental.planned_return_date - broken_rental.start_date).days
    real_rental_days_old = (today - broken_rental.start_date).days
    real_rental_days_new = (broken_rental.planned_return_date - today).days

    if real_rental_days_old < 1:
        real_rental_days_old = 1
    if real_rental_days_new < 0:
        real_rental_days_new = 0

    # Oblicz koszt pojazdu zepsutego
    broken_veh_cost = old_rental_cost * real_rental_days_old / old_rental_period

    # Oblicz koszt pojazdu zastępczego
    if different_price:
        user = session.query(User).filter(User.id == original_vehicle.user_id).first()
        replacement_veh_cost, _, _ = calculate_rental_cost(user, replacement_vehicle.cash_per_day, real_rental_days_new)
    else:
        replacement_veh_cost = old_rental_cost - broken_veh_cost

    # Aktualizacja statusu pojazdu zwracanego
    original_vehicle.is_available = True
    original_vehicle.borrower_id = None
    original_vehicle.return_date = None

    # Aktualizacja statusu pojazdu zastępczego
    replacement_vehicle.is_available = False
    replacement_vehicle.borrower_id = broken_rental.user_id
    replacement_vehicle.return_date = broken_rental.planned_return_date

    # Korekta historii najmu pojazdu popsutego
    broken_rental.actual_return_date = today
    broken_rental.total_cost = round(broken_veh_cost, 2)

    # Nowa rezerwacja dla pojazdu zastępczego
    base_res_id = broken_rental.reservation_id
    existing = session.query(RentalHistory).filter(
        RentalHistory.reservation_id.like(f"{base_res_id}%")
    ).all()

    new_suffix = chr(65 + len(existing))  # 'A', 'B', 'C', ...
    new_res_id = f"{base_res_id}{new_suffix}"

    new_rental = RentalHistory(
        reservation_id=new_res_id,
        user_id=broken_rental.user_id,
        vehicle_id=replacement_vehicle.id,
        start_date=today,
        planned_return_date=broken_rental.planned_return_date,
        actual_return_date=None,
        base_cost=round(replacement_veh_cost, 2),
        total_cost=round(replacement_veh_cost, 2),
    )
    session.add(new_rental)
    session.commit()
    return True


def find_replacement_vehicle(session, reference_vehicle, planned_return_date, prefer_cheaper: bool):
    # szukanie pojazdu z flagą preffer_cheeper
    available_vehicles = get_available_vehicles(
        session, date.today(), planned_return_date, reference_vehicle.type
    )

    if prefer_cheaper:
        # Najdroższy z tańszych
        vehicle = next(
            (v for v in sorted(available_vehicles, key=lambda v: v.cash_per_day, reverse=True)
            if v.cash_per_day < reference_vehicle.cash_per_day),
            None
        )
    else:
        # Najtańszy z droższych
        vehicle = next(
            (v for v in sorted(available_vehicles, key=lambda v: v.cash_per_day)
            if v.cash_per_day > reference_vehicle.cash_per_day),
            None
        )

    return vehicle