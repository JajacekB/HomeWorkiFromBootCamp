# directory: models
# file: repair_history.py

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from database.base import Base


class RepairHistory(Base):
    __tablename__ = 'repair_history'

    id = Column(Integer, primary_key=True)
    repair_id = Column(String, unique=True, nullable=False, index=True)

    vehicle_id = Column(Integer, ForeignKey('vehicles.id'), nullable=False)
    mechanic_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    start_date = Column(Date, nullable=False)
    planned_end_date = Column(Date, nullable=False)  # dawniej end_date
    actual_return_date = Column(Date, nullable=True)  # nowa kolumna

    cost = Column(Float, nullable=True)
    description = Column(String, nullable=True)

    mechanic = relationship("User", back_populates="repairs_done", foreign_keys=[mechanic_id])
    vehicle = relationship("Vehicle", back_populates="repairs")

    def __repr__(self):
        return f"RepairHistory {self.repair_id} Mechanik:{self.mechanic.first_name} {self.mechanic.last_name} Vehicle:{self.vehicle_id}"