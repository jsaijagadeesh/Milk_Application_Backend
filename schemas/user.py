from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    """Schema for creating a user"""
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    name: str
    email: str
    role: str
    wallet_balance: float
    
    class Config:
        from_attributes = True


class AddWallet(BaseModel):
    """Schema for adding to wallet"""
    amount: float


class DeductWallet(BaseModel):
    """Schema for deducting from wallet"""
    amount: float
