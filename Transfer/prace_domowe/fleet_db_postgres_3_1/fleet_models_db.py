from sqlalchemy import Column, Integer, String, Float, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from database_base import Base
from datetime import datetime, date, timedelta


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
            f"id: [{self.id}]\n"
            f"Numer ewidencyjny: [{self.vehicle_id}]\n"
            f"{self.brand}, {self.vehicle_model}\n"
            f"{self.size}, {self.fuel_type}\n"
            f"Numer rejestracyjny: {self.individual_id}\n"
            f"{self.cash_per_day}zł za dzień\n"
            f"{'Dostępny' if self.is_available else 'Niedostępny'}"
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
            f"id: [{self.id}]\n"
            f"Numer ewidencyjny: [{self.vehicle_id}]\n"
            f"{self.brand}, {self.vehicle_model}\n"
            f"Maks. prędkość: {self.max_speed}km/h\n"
            f"Numer rejestracyjny: {self.individual_id}\n"
            f"{self.cash_per_day}zł za dzień\n"
            f"{'Dostępny' if self.is_available else 'Niedostępny'}"
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
            f"id: [{self.id}]\n"
            f"Numer ewidencyjny: [{self.vehicle_id}]\n"
            f"{self.brand}, {self.vehicle_model}\n"
            f"{self.bike_type}, {'elektryczny' if self.is_electric else 'zwykły'}\n"
            f"Numer seryjny: {self.individual_id}\n"
            f"{self.cash_per_day}zł za dzień\n"
            f"{'Dostępny' if self.is_available else 'Niedostępny'}"
        )


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False)  # 'admin', 'seller', 'client'
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    login = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    address = Column(String, nullable=True)
    registration_day = Column(Date, default=date.today)

    vehicles = relationship("Vehicle", back_populates="borrower")
    rental_history = relationship("RentalHistory", back_populates="user")
    repairs_done = relationship("RepairHistory", back_populates="mechanic", foreign_keys="RepairHistory.mechanic_id")

    def __repr__(self):
        return (f"    Klient: [ID={self.id}]\n"
                f"          {self.first_name} {self.last_name}"
            )


class RentalHistory(Base):
    __tablename__ = 'rental_history'

    id = Column(Integer, primary_key=True)
    reservation_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_cost = Column(Float, nullable=False)

    user = relationship("User", back_populates="rental_history")
    vehicle = relationship("Vehicle", back_populates="rental_history")
    invoice = relationship("Invoice", back_populates="rental", uselist=False)

    def __repr__(self):
        return f"<RentalHistory {self.reservation_id} User:{self.user_id} Vehicle:{self.vehicle_id}>"


class RepairHistory(Base):
    __tablename__ = 'repair_history'

    id = Column(Integer, primary_key=True)
    repair_id = Column(String, unique=True, nullable=False, index=True)

    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    mechanic_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    cost = Column(Float, nullable=True)
    description = Column(String, nullable=True)

    mechanic = relationship("User", back_populates="repairs_done", foreign_keys=[mechanic_id])
    vehicle = relationship("Vehicle", back_populates="repairs")

    def __repr__(self):
        return f"<RepairHistory {self.repair_id} Mechanik:{self.mechanic.first_name} {self.mechanic.last_name} Vehicle:{self.vehicle_id}>"


class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String, unique=True, nullable=False, index=True)
    rental_id = Column(Integer, ForeignKey('rental_history.id'), nullable=True)
    issue_date = Column(Date, default=date.today)
    amount = Column(Float, nullable=False)

    rental = relationship("RentalHistory", back_populates="invoice")

    def __repr__(self):
        return f"<Invoice {self.invoice_number} Amount:{self.amount}>"

class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True)
    description = Column(String)
    discount_percent = Column(Float)
    min_days = Column(Integer)
    type = Column(String)  # 'time' lub 'loyalty'