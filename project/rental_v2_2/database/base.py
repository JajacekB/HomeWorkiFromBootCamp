# directory: database
# file: base.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL, DEBUG

engine = create_engine(
    DATABASE_URL,
    echo=DEBUG,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

Base = declarative_base()
Session = sessionmaker(bind=engine, expire_on_commit=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# from models.user import User
# from models.vehicle import Vehicle, Car, Bike, Scooter
# from models.repair_history import RepairHistory
# from models.rental_history import RentalHistory
# from models.promotions import Promotion
# from models.invoice import Invoice