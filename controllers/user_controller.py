from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from config.database import get_db
from services.user_service import UserService
from services.auth_service import AuthService
from schemas.user import UserCreate, AddWallet, DeductWallet
from controllers.permissions import get_current_user, require_admin, check_resource_owner

router = APIRouter(prefix="/api/v1/users", tags=["users"])


# ==================== PUBLIC ENDPOINTS ====================

@router.get("", response_model=dict)
def get_users(db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(require_admin)):
    """Get all users (admin only)"""
    try:
        users = UserService.get_all_users(db)
        return {
            "success": True,
            "users": [
                {
                    "id": u.id,
                    "name": u.name,
                    "email": u.email,
                    "role": u.role,
                    "wallet_balance": u.wallet_balance
                }
                for u in users
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=dict)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get a specific user (authenticated user/admin)"""
    if not check_resource_owner(user_id, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "success": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "wallet_balance": user.wallet_balance
        }
    }


# ==================== AUTHENTICATED ENDPOINTS ====================

@router.get("/{user_id}/wallet", response_model=dict)
def get_wallet(user_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's wallet balance (authenticated users only)"""
    # User can only view their own wallet, admin can view any
    if not check_resource_owner(user_id, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "success": True,
        "walletBalance": user.wallet_balance
    }


@router.post("/{user_id}/wallet/add", response_model=dict)
def add_wallet(user_id: int, payload: AddWallet, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """Add money to wallet (authenticated users only)"""
    # User can only add to their own wallet, admin can add to any
    if not check_resource_owner(user_id, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    try:
        if payload.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        user = UserService.add_wallet(db, user_id, payload.amount)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "wallet_balance": user.wallet_balance
            },
            "walletBalance": user.wallet_balance
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/wallet/deduct", response_model=dict)
def deduct_wallet(user_id: int, payload: DeductWallet, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """Deduct money from wallet (authenticated users only)"""
    # User can only deduct from their own wallet, admin can deduct from any
    if not check_resource_owner(user_id, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    try:
        if payload.amount <= 0:
            raise HTTPException(status_code=400, detail="Amount must be greater than 0")
        
        user = UserService.deduct_wallet(db, user_id, payload.amount)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "wallet_balance": user.wallet_balance
            },
            "walletBalance": user.wallet_balance
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ==================== ADMIN ONLY ENDPOINTS ====================

@router.post("", status_code=201, response_model=dict)
def create_user(payload: UserCreate, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(require_admin)):
    """Create a new user (admin only)"""
    try:
        if not payload.name or not payload.email or not payload.password:
            raise HTTPException(status_code=400, detail="Name, email, and password are required")
        
        password_hash = AuthService.hash_password(payload.password)
        new_user = UserService.create_user_with_password(
            db,
            name=payload.name,
            email=payload.email,
            password_hash=password_hash,
            role=payload.role
        )
        return {
            "success": True,
            "message": "User created successfully",
            "user": {
                "id": new_user.id,
                "name": new_user.name,
                "email": new_user.email,
                "role": new_user.role,
                "wallet_balance": new_user.wallet_balance
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(require_admin)):
    """Delete a user (admin only)"""
    try:
        # Prevent self-deletion
        if current_user.get("user_id") == user_id:
            raise HTTPException(status_code=400, detail="Cannot delete your own account")
        
        success = UserService.delete_user(db, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "message": "User deleted successfully"
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/role", response_model=dict)
def update_user_role(user_id: int, new_role: str, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(require_admin)):
    """Update user role (admin only)"""
    try:
        if new_role not in ["user", "admin"]:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        user = UserService.update_user_role(db, user_id, new_role)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "success": True,
            "message": f"User role updated to {new_role}",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
