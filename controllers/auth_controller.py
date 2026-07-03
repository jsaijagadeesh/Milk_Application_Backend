"""
Authentication Controller
Handles login, registration, and JWT token management
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from config.database import get_db
from services.auth_service import AuthService
from services.user_service import UserService
from schemas.auth import UserRegister, UserLogin, TokenResponse, UserAuthResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=dict)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **name**: User's full name
    - **email**: User's email (must be unique)
    - **password**: User's password (will be hashed)
    """
    try:
        # Check if email already exists
        existing_user = UserService.get_user_by_email(db, payload.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash password
        password_hash = AuthService.hash_password(payload.password)
        
        # Create new user
        new_user = UserService.create_user_with_password(
            db,
            name=payload.name,
            email=payload.email,
            password_hash=password_hash,
            role="user"
        )
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
                "role": new_user.role
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    """
    Login user and get JWT token
    
    - **email**: User's email
    - **password**: User's password
    
    Returns JWT token that should be used in Authorization header: `Bearer {token}`
    """
    try:
        # Get user by email
        user = UserService.get_user_by_email(db, payload.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not AuthService.verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(status_code=401, detail="User account is inactive")
        
        # Create JWT token
        token_data = AuthService.create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role
        )
        
        return TokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            user={
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "wallet_balance": user.wallet_balance
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify-token")
def verify_token(token: str):
    """
    Verify JWT token validity
    
    - **token**: JWT token to verify
    """
    try:
        payload = AuthService.verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return {
            "success": True,
            "valid": True,
            "user_id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role")
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
