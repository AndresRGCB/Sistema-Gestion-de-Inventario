from sqlalchemy import Column, Integer, ForeignKey, String, TIMESTAMP
from sqlalchemy.sql import func
from app.database import Base

class Movement(Base):
    __tablename__ = "movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    source_store_id = Column(String(50), nullable=True)
    target_store_id = Column(String(50), nullable=True)
    quantity = Column(Integer, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    type = Column(String(10), nullable=False)
