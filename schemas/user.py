from pydantic import BaseModel, EmailStr
from typing import Optional, List


# ==================== ADDRESS SCHEMAS ====================

class AddressCreate(BaseModel):
    """Schema for creating an address"""
    street: str
    city: str
    state: str
    postal_code: str
    country: Optional[str] = "India"
    is_default: Optional[bool] = False


class AddressUpdate(BaseModel):
    """Schema for updating an address"""
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    is_default: Optional[bool] = None


class AddressResponse(BaseModel):
    """Schema for address response"""
    id: int
    user_id: int
    street: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool

    class Config:
        from_attributes = True


# ==================== USER SCHEMAS ====================

class UserCreate(BaseModel):
    """Schema for creating a user"""
    name: str
    email: EmailStr
    password: str
    role: Optional[str] = "user"


class UserProfileUpdate(BaseModel):
    """Schema for user updating their own profile (role NOT allowed)"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    # Address fields (optional — updates/creates address in same call)
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class AdminUserUpdate(BaseModel):
    """Schema for admin updating any user (all fields including role)"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    # Address fields (optional)
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


class UserUpdate(BaseModel):
    """Schema for updating a user (legacy, kept for compatibility)"""
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
