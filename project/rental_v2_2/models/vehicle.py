# directory: models
# file: vehicle

from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from database.base import Base


class Vehicle(Base):
    __tablename__ = 'vehicles'

    id = Column(Integer, primary_key=True)
    vehicle_id = Column(String, unique=True, nullable=False)
    brand = Column(String, nullable=False)
    vehicle_model = Column(String, nullable=False)
    cash_per_day = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)
    borrower_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    return_date = Column(Date, nullable=True)
    individual_id = Column(String, unique=True, nullable=False)
    purchase_date = Column(Date, default=date.today)
    type = Column(String)  # 'car', 'scooter', 'bike'

    borrower = relationship("User", back_populates="vehicles")
    rental_history = relationship("RentalHistory", back_populates="vehicle")
    repairs = relationship("RepairHistory", back_populates="vehicle")

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'vehicle'
    }


class Car(Vehicle):
    __tablename__ = 'cars'
    id = Column(Integer, ForeignKey('vehicles.id'), primary_key=True)  # <-- klucz obcy do vehicles.id
    size = Column(String)
    fuel_type = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'car',
    }

    def __repr__(self):
        return(
            f"\nNumer ewidencyjny: [{self.vehicle_id}] "
            f"{self.brand} {self.vehicle_model}   "
            f"{self.size} - {self.fuel_type}\n"
            f"Numer rejestracyjny: {self.individual_id}   "
            f"{self.cash_per_day}zł za dzień  "
            f"{'Dostępny' if self.is_available else f'Niedostępny do {self.return_date}'}\n"
        )


class Scooter(Vehicle):
    __tablename__ = 'scooters'
    id = Column(Integer, ForeignKey('vehicles.id'), primary_key=True)
    max_speed = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'scooter',
    }

    def __repr__(self):
        return (
            f"Numer ewidencyjny: [{self.vehicle_id} ] "
            f"{self.brand} {self.vehicle_model} "
            f"Maks. prędkość: {self.max_speed}km/h\n"
            f"Numer rejestracyjny: {self.individual_id} "
            f"{self.cash_per_day}zł za dzień "
            f"{'Dostępny' if self.is_available else f'Niedostępny do {self.return_date}'}\n"
        )


class Bike(Vehicle):
    __tablename__ = 'bikes'
    id = Column(Integer, ForeignKey('vehicles.id'), primary_key=True)
    bike_type = Column(String)
    is_electric = Column(Boolean)

    __mapper_args__ = {
        'polymorphic_identity': 'bike',
    }

    def __repr__(self):
        return (
            f"Numer ewidencyjny: [{self.vehicle_id}] "
            f"{self.brand} {self.vehicle_model} "
            f"{self.bike_type} - {'elektryczny' if self.is_electric else 'zwykły'}\n"
            f"Numer seryjny: {self.individual_id} "
            f"{self.cash_per_day}zł za dzień "
            f"{'Dostępny' if self.is_available else f'Niedostępny do {self.return_date}'}\n"
        )