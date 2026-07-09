from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    """Schema for user registration"""
    name: str
    email: EmailStr
    password: str
    # Optional address at registration time
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = "India"


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str
    expires_in: int
    user: Optional[dict] = None


class UserAuthResponse(BaseModel):
    """Schema for authenticated user response"""
    id: int
    name: str
    email: str
    role: str
    wallet_balance: float
    
    class Config:
        from_attributes = True
