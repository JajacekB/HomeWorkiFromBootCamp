from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fleet_models_db import (
    User,
    Vehicle,
    Car,
    Scooter,
    Bike,
    Promotion,
    RentalHistory,
    RepairHistory,
    Invoice
)

# Dane połączenia z PostgreSQL
DATABASE_URL = "postgresql+psycopg2://postgres:secret@localhost:5432/fleet_db"

# Silnik bazy danych
engine = create_engine(DATABASE_URL)

# Sesja – nowy sposób tworzenia sesji
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tylko do inicjalizacji bazy
def rebuild_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)