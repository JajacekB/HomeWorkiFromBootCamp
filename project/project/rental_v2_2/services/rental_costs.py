# directory: services
# file:  rental_cost.py

from datetime import date
from database.base import Session
from models.rental_history import RentalHistory
from models.promotions import Promotion
from models.user import User
from models.vehicle import Vehicle


def calculate_rental_cost(user, daily_rate, rental_days):
    with Session() as session:
        """
        Zwraca koszt z uwzględnieniem rabatu czasowego i lojalnościowego.
        """
        # Zlicz zakończone wypożyczenia
        past_rentals = session.query(RentalHistory).filter_by(user_id=user.id).count()
        next_rental_number = past_rentals + 1

        # Sprawdzenie promocji lojalnościowej (co 10. wypożyczenie)
        loyalty_discount_days = 1 if next_rental_number % 10 == 0 else 0
        if loyalty_discount_days == 1:
            print("🎉 To Twoje 10., 20., 30... wypożyczenie – pierwszy dzień za darmo!")

        # Pobierz rabaty czasowe z tabeli
        time_promos = session.query(Promotion).filter_by(type="time").order_by(Promotion.min_days.desc()).all()

        discount = 0.0
        for promo in time_promos:
            if rental_days >= promo.min_days:
                discount = promo.discount_percent / 100.0
                print(f"\n✅ Przyznano rabat {int(promo.discount_percent)}% ({promo.description})")
                break

        # Cena po uwzględnieniu rabatu i 1 dnia gratis (jeśli przysługuje)
        paid_days = max(rental_days - loyalty_discount_days, 0)
        price = paid_days * daily_rate * (1 - discount)

        return round(price, 2), discount * 100, "lojalność + czasowy" if discount > 0 and loyalty_discount_days else (
            "lojalność" if loyalty_discount_days else (
            "czasowy" if discount > 0 else "brak"))


def recalculate_cost(session, user: User, vehicle: Vehicle, return_date: date, reservation_id: str):
    # Rozdzielenie przypadków; przed czasem, aktualny, przeterminowany

    rental_looked = session.query(RentalHistory).filter(
        RentalHistory.reservation_id == reservation_id
    ).first()

    if not rental_looked:
        raise ValueError("Nie znaleziono rezerwacji o podanym ID")

    planned_return_date = rental_looked.planned_return_date
    start_date = rental_looked.start_date
    base_cost = rental_looked.base_cost

    cash_per_day = vehicle.cash_per_day

    if return_date < start_date:
        total_cost = cash_per_day
        overdue_fee_text = f"(Skrócenie rezerwacji – kara {cash_per_day} zł)"
    if return_date > planned_return_date:
        extra_days = (return_date - planned_return_date).days
        extra_fee = extra_days * cash_per_day
        total_cost = base_cost + extra_fee
        overdue_fee_text = f"\n{base_cost} zł opłata bazowa + {extra_days * cash_per_day} zł kara za przeterminowanie.)"
    elif return_date == planned_return_date:
        extra_fee = 0
        total_cost = base_cost
        overdue_fee_text = " (zwrot terminowy)"
    else:
        new_period = (planned_return_date - start_date).days
        extra_fee = 0
        total_cost = calculate_rental_cost(user, cash_per_day, new_period)
        overdue_fee_text = " (zwrot przed terminem, naliczono koszt zgodnie z czasem użytkowania)"

        return total_cost, extra_fee, overdue_fee_text


