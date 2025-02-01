from sqlalchemy import Column, Integer, String, DECIMAL
from app.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    category = Column(String(100), nullable=True)
    price = Column(DECIMAL(10,2), nullable=False)
    sku = Column(String(50), unique=True, nullable=False)
