# directory: services
# file: id_generators.py

from sqlalchemy import extract, func, cast, Integer
from database.base import Session
from models.rental_history import RentalHistory
from models.repair_history import RepairHistory
from models.invoice import Invoice
from models.vehicle import Vehicle


def generate_reservation_id():
    with Session() as session:
        last = session.query(RentalHistory).order_by(RentalHistory.id.desc()).first()
        if last and last.reservation_id and len(last.reservation_id) > 1 and last.reservation_id[1:].isdigit():
            last_num = int(last.reservation_id[1:])
        else:
            last_num = 0
        new_num = last_num + 1

        # Określamy długość cyfr - minimalnie 4, albo więcej jeśli liczba jest większa
        digits = max(4, len(str(new_num)))
        return f"R{new_num:0{digits}d}"

def generate_repair_id():
    with Session() as session:
        last = session.query(RepairHistory).order_by(RepairHistory.id.desc()).first()
        if last and last.repair_id and len(last.repair_id) > 1 and last.repair_id[1:].isdigit():
            last_num = int(last.repair_id[1:])
        else:
            last_num = 0
        new_num = last_num + 1

        # Określamy długość cyfr - minimalnie 4, albo więcej jeśli liczba jest większa
        digits = max(4, len(str(new_num)))
        return f"N{new_num:0{digits}d}"

def generate_invoice_number(planned_return_date):
    """
                Generuje numer faktury w formacie FV/YYYY/MM/NNNN
                - session: aktywna sesja SQLAlchemy
                - planned_return_date: data zakończenia wypożyczenia (datetime.date)
                """
    with Session() as session:

        year = planned_return_date.year
        month = planned_return_date.month

        # Policz faktury wystawione w danym roku i miesiącu
        count = session.query(Invoice).filter(
            extract('year', Invoice.issue_date) == year,
            extract('month', Invoice.issue_date) == month
        ).count()

        # Dodaj 1 do sekwencji
        sequence = count + 1

        # Zbuduj numer faktury
        invoice_number = f"FV/{year}/{month:02d}/{sequence:04d}"
        return invoice_number

def generate_vehicle_id(session ,prefix: str) -> str:
    prefix = prefix.upper()
    prefix_len = len(prefix)

    # Szukamy najwyższego numeru w bazie danych
    max_number_db = session.query(
        func.max(
            cast(func.substr(Vehicle.vehicle_id, prefix_len + 1), Integer)
        )
    ).filter(
        Vehicle.vehicle_id.ilike(f"{prefix}%")
    ).scalar() or 0

    # Szukamy najwyższego numeru w obiektach dodanych do sesji (tymczasowych)
    max_number_pending = 0
    for obj in session.new:
        if isinstance(obj, Vehicle) and obj.vehicle_id and obj.vehicle_id.startswith(prefix):
            try:
                number = int(obj.vehicle_id[prefix_len:])
                if number > max_number_pending:
                    max_number_pending = number
            except ValueError:
                continue

    # Bierzemy najwyższy z obu
    next_number = max(max_number_db, max_number_pending) + 1
    return f"{prefix}{next_number:03d}"