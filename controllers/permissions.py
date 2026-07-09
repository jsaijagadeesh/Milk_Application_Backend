"""
Permission & Role Utilities
Decorators and functions for role-based access control
"""

from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from services.auth_service import AuthService

security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency to get current authenticated user from JWT token using HTTPBearer
    """
    token = credentials.credentials
    payload = AuthService.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {
        "user_id": payload.get("user_id"),
        "email": payload.get("email"),
        "role": payload.get("role")
    }


async def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency to require admin role
    
    Usage:
    @app.delete("/products/{id}")
    def delete_product(id: int, current_user = Depends(require_admin)):
        # Only admin can access this
        return {"message": "Product deleted"}
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    return current_user


async def require_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency to require user role
    
    Usage:
    @app.post("/users/{id}/wallet/add")
    def add_wallet(id: int, current_user = Depends(require_user)):
        # User or admin can access this
        return {"message": "Wallet updated"}
    """
    if current_user.get("role") not in ["user", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="User access required"
        )
    return current_user


def check_resource_owner(user_id: int, current_user: Dict[str, Any]) -> bool:
    """
    Check if user owns the resource or is admin
    
    Usage:
    @app.get("/users/{user_id}")
    def get_user_profile(user_id: int, current_user = Depends(get_current_user)):
        if not check_resource_owner(user_id, current_user):
            raise HTTPException(status_code=403, detail="Forbidden")
        # ...
    """
    # Admin can access any resource
    if current_user.get("role") == "admin":
        return True
    # User can only access their own resource
    return current_user.get("user_id") == user_id