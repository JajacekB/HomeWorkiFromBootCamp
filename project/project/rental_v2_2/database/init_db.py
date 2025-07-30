# directory: database
# file: init_cb.py

from sqlalchemy.exc import IntegrityError
from models.user import User
from models.vehicle import Vehicle, Car, Bike, Scooter
from models.rental_history import RentalHistory
from models.repair_history import RepairHistory
from models.promotions import Promotion
from models.invoice import Invoice
from database.base import Base, engine, Session, SessionLocal
import bcrypt



def create_tables():
    Base.metadata.create_all(engine)
    print("Baza danych i tabele zostały utworzone.")


def create_admin_user():
    session = Session()
    existing_admin = session.query(User).filter_by(login="admin").first()

    if not existing_admin:
        admin_user = User(
            first_name="Admin",
            last_name="",
            login="admin",
            phone=666555444,
            email="admin@system.local",
            password_hash=bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode(),
            role="admin",
            address=""
        )
        try:
            session.add(admin_user)
            session.commit()
            print("Użytkownik 'admin' został utworzony")
        except IntegrityError:
            session.rollback()
            print("Nie udało się utworzyć domyślnego admina.")
    else:
        print("Użytkownik 'admin' już istnieje.")
    session.close()


def create_promotions():
    session = Session()
    promotions_data = [
        {"id": 1, "description": "5% zniżki przy wynajmie na minimum 5 dni", "discount_percent": 5, "min_days": 5, "type": "time"},
        {"id": 2, "description": "9% zniżki przy wynajmie na minimum 7 dni", "discount_percent": 9, "min_days": 7, "type": "time"},
        {"id": 3, "description": "20% zniżki przy wynajmie na minimum 14 dni", "discount_percent": 20, "min_days": 14, "type": "time"},
        {"id": 4, "description": "Co 10. wypożyczenie – jedna doba gratis!", "discount_percent": 100, "min_days": 0, "type": "loyalty"}
    ]

    for promo in promotions_data:
        existing = session.query(Promotion).filter_by(id=promo["id"]).first()
        if existing:
            for key, value in promo.items():
                setattr(existing, key, value)
        else:
            session.add(Promotion(**promo))

    session.commit()
    session.close()
    print("✅ Promocje zostały dodane lub zaktualizowane.")


if __name__ == "__main__":
    create_tables()
    create_admin_user()
    create_promotions()