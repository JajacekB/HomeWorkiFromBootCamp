# directory: models
# file: rental_history.py

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base


class RentalHistory(Base):
    __tablename__ = 'rental_history'

    id = Column(Integer, primary_key=True)
    reservation_id = Column(String, unique=True, nullable=False, index=True)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)

    start_date = Column(Date, nullable=False)
    planned_return_date = Column(Date, nullable=False)
    actual_return_date = Column(Date, nullable=True)

    base_cost = Column(Float, nullable=True)
    late_fee = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=False)

    user = relationship("User", back_populates="rental_history")
    vehicle = relationship("Vehicle", back_populates="rental_history")
    invoice = relationship("Invoice", back_populates="rental", uselist=False)

    def __repr__(self):
        return f"<RentalHistory ID:{self.id} Nr rezerwacji:{self.reservation_id} User:{self.user_id} Vehicle:{self.vehicle_id}>"