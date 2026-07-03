from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from config.database import Base
from datetime import datetime, timezone


class Product(Base):
    """Product model - represents dairy products"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String, default="")
    stock = Column(Integer, default=100)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
