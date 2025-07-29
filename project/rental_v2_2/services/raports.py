# directory: services
# file: raports.py

from datetime import date
from sqlalchemy import and_
from models.rental_history import RentalHistory
from models.vehicle import Vehicle
from models.user import User


def show_vehicles_rented_today(session):
    today = date.today()

    rentals_today = session.query(RentalHistory).filter(
        and_(
            RentalHistory.start_date <= today,
            today <= RentalHistory.planned_return_date
        )
    ).all()

    if not rentals_today:
        print("\n✅ Dziś żaden pojazd nie jest wypożyczony.")
        return

    print("\n🚘 Pojazdy wypożyczone dziś:\n")

    for rental in rentals_today:
        vehicle = session.query(Vehicle).filter_by(id=rental.vehicle_id).first()
        user = session.query(User).filter_by(id=rental.user_id).first()

        print(
            f" [ID: {vehicle.id}]  {vehicle.brand} {vehicle.vehicle_model}"
            f"   ❌ Wypożyczony w terminie: {rental.start_date} → {rental.planned_return_date}"
            f"   👤 Klient ID {user.id}: {user.first_name} {user.last_name}\n"
        )
