from sqlalchemy import Column, Integer, ForeignKey, String
from app.database import Base

class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    min_stock = Column(Integer, nullable=False)
