# directory: models
# file: invoice.py

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from database.base import Base


class Invoice(Base):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    invoice_number = Column(String, unique=True, nullable=False, index=True)
    rental_id = Column(Integer, ForeignKey('rental_history.id'), nullable=True)
    issue_date = Column(Date, default=date.today)
    amount = Column(Float, nullable=False)

    rental = relationship("RentalHistory", back_populates="invoice")

    def __repr__(self):
        return f"Invoice {self.id} {self.rental_id} {self.invoice_number} Amount:{self.amount}"