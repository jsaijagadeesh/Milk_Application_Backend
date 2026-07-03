from pydantic import BaseModel
from typing import Optional


class ProductCreate(BaseModel):
    """Schema for creating a product"""
    name: str
    price: float
    category: str
    description: Optional[str] = ""
    stock: Optional[int] = 100


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    name: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    stock: Optional[int] = None


class ProductResponse(BaseModel):
    """Schema for product response"""
    id: int
    name: str
    price: float
    category: str
    description: str
    stock: int
    
    class Config:
        from_attributes = True
