# directory: models
# file: promotions.py

from sqlalchemy import Column, Integer, String, Float
from database.base import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True)
    description = Column(String)
    discount_percent = Column(Float)
    min_days = Column(Integer)
    type = Column(String)  # 'time' lub 'loyalty'