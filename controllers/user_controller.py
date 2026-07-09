from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from config.database import get_db
from services.user_service import UserService
from services.auth_service import AuthService
from schemas.user import (
    UserCreate, AddWallet, DeductWallet,
    UserProfileUpdate, AdminUserUpdate,
    AddressCreate, AddressUpdate
)
from controllers.permissions import get_current_user, require_admin, check_resource_owner

router = APIRouter(prefix="/api/v1/users", tags=["users"])


def _fmt_address(a):
    return {
        "id": a.id,
        "user_id": a.user_id,
        "street": a.street,
        "city": a.city,
        "state": a.state,
        "postal_code": a.postal_code,
        "country": a.country,
        "is_default": a.is_default,
    }


def _fmt_user(u, address=None):
    data = {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "role": u.role,
        "wallet_balance": u.wallet_balance,
        "is_active": u.is_active,
        "address": _fmt_address(address) if address else None,
    }
    return data


# ==================== PUBLIC ENDPOINTS ====================

@router.get("", response_model=dict)
def get_users(db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(require_admin)):
    """Get all users with their address (admin only)"""
    try:
        users = UserService.get_all_users(db)
        result = []
        for u in users:
            address = UserService.get_user_address(db, u.id)
            result.append(_fmt_user(u, address))
        return {
            "success": True,
            "users": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}", response_model=dict)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get a specific user with their address (authenticated user/admin)"""
    if not check_resource_owner(user_id, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    address = UserService.get_user_address(db, user_id)
    return {
        "success": True,
        "user": _fmt_user(user, address)
    }


# ==================== PROFILE UPDATE ENDPOINTS ====================

@router.put("/{user_id}/profile", response_model=dict)
def update_profile(
    user_id: int,
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Update own profile — name, email, password + address (role NOT allowed).
    A user can only update their own profile; admin can also use this route.
    """
    if not check_resource_owner(user_id, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        user = UserService.update_profile(
            db,
            user_id=user_id,
            name=payload.name,
            email=payload.email,
            password=payload.password,
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update address in the same call if any address field is provided
        address = UserService.upsert_default_address(
            db,
            user_id=user_id,
            street=payload.street,
            city=payload.city,
            state=payload.state,
            postal_code=payload.postal_code,
            country=payload.country,
        )

        # Fetch fresh address after potential upsert
        address = UserService.get_user_address(db, user_id)
        response = {
            "success": True,
            "message": "Profile updated successfully",
            "user": _fmt_user(user, address)
        }
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/admin-update", response_model=dict)
def admin_update_user(
    user_id: int,
    payload: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(require_admin)
):
    """
    Admin update — can modify all fields: name, email, password, role, is_active + address.
    Admin only endpoint.
    """
    try:
        user = UserService.admin_update_user(
            db,
            user_id=user_id,
            name=payload.name,
            email=payload.email,
            password=payload.password,
            role=payload.role,
            is_active=payload.is_active,
        )
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update address in the same call if any address field is provided
        address = UserService.upsert_default_address(
            db,
            user_id=user_id,
            street=payload.street,
            city=payload.city,
            state=payload.state,
            postal_code=payload.postal_code,
            country=payload.country,
        )

        response = {
            "success": True,
            "message": "User updated successfully",
            "user": _fmt_user(user, UserService.get_user_address(db, user_id))
        }
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== AUTHENTICATED ENDPOINTS ====================

@router.get("/{user_id}/wallet", response_model=dict)
def get_wallet(user_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get user's wallet balance (authenticated users only)"""
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
            "user": {"id": user.id, "name": user.name, "email": user.email, "wallet_balance": user.wallet_balance},
            "walletBalance": user.wallet_balance
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{user_id}/wallet/deduct", response_model=dict)
def deduct_wallet(user_id: int, payload: AddWallet, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(get_current_user)):
    """Deduct money from wallet (authenticated users only)"""
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
            "user": {"id": user.id, "name": user.name, "email": user.email, "wallet_balance": user.wallet_balance},
            "walletBalance": user.wallet_balance
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== ADDRESS ENDPOINTS ====================


# ==================== ADDRESS ENDPOINTS (ONE ADDRESS PER USER) ====================

@router.get("/{user_id}/address", response_model=dict)
def get_address(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get the user's address (owner or admin)"""
    if not check_resource_owner(user_id, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    address = UserService.get_user_address(db, user_id)
    if not address:
        raise HTTPException(status_code=404, detail="No address found for this user")

    return {
        "success": True,
        "address": _fmt_address(address)
    }


@router.post("/{user_id}/address", response_model=dict)
def save_address(
    user_id: int,
    payload: AddressCreate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create or update the user's address (one address per user).
    If an address already exists it will be updated, not duplicated.
    Owner or admin only.
    """
    if not check_resource_owner(user_id, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        address = UserService.upsert_default_address(
            db,
            user_id=user_id,
            street=payload.street,
            city=payload.city,
            state=payload.state,
            postal_code=payload.postal_code,
            country=payload.country,
        )
        return {
            "success": True,
            "message": "Address saved successfully",
            "address": _fmt_address(address)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{user_id}/address", response_model=dict)
def update_address(
    user_id: int,
    payload: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update the user's existing address (owner or admin)"""
    if not check_resource_owner(user_id, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        address = UserService.get_user_address(db, user_id)
        if not address:
            raise HTTPException(status_code=404, detail="No address found. Use POST to create one first.")

        updated = UserService.update_address(
            db,
            address_id=address.id,
            user_id=user_id,
            street=payload.street,
            city=payload.city,
            state=payload.state,
            postal_code=payload.postal_code,
            country=payload.country,
            is_default=None,  # always default since one address per user
        )
        return {
            "success": True,
            "message": "Address updated successfully",
            "address": _fmt_address(updated)
        }
    except HTTPException as e:
        raise e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}/address", response_model=dict)
def delete_address(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete the user's address (owner or admin)"""
    if not check_resource_owner(user_id, current_user):
        raise HTTPException(status_code=403, detail="Forbidden")

    address = UserService.get_user_address(db, user_id)
    if not address:
        raise HTTPException(status_code=404, detail="No address found for this user")

    UserService.delete_address(db, address_id=address.id, user_id=user_id)
    return {
        "success": True,
        "message": "Address deleted successfully"
    }



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
            "user": _fmt_user(new_user, UserService.get_user_address(db, new_user.id))
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: Dict[str, Any] = Depends(require_admin)):
    """Delete a user (admin only)"""
    try:
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

        addresses = UserService.get_user_address(db, user_id)
        return {
            "success": True,
            "message": f"User role updated to {new_role}",
            "user": _fmt_user(user, addresses)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
