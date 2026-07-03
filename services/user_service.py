from sqlalchemy.orm import Session
from models.user import User
from typing import Optional, List


class UserService:
    """Service for handling user business logic"""
    
    @staticmethod
    def get_all_users(db: Session) -> List[User]:
        """Get all users from database"""
        return db.query(User).all()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, name: str, email: str, password: str, role: str = "user") -> User:
        """Create a new user with plain password (hashes automatically)"""
        from services.auth_service import AuthService
        password_hash = AuthService.hash_password(password)
        return UserService.create_user_with_password(db, name, email, password_hash, role)

    
    @staticmethod
    def create_user_with_password(db: Session, name: str, email: str, password_hash: str, role: str = "user") -> User:
        """Create a new user with password hash"""
        # Check if email already exists
        if UserService.get_user_by_email(db, email):
            raise ValueError(f"Email {email} already exists")
        
        new_user = User(
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            wallet_balance=0.0,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    @staticmethod
    def add_wallet(db: Session, user_id: int, amount: float) -> Optional[User]:
        """Add money to user's wallet"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        
        user.wallet_balance += amount
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_wallet_balance(db: Session, user_id: int) -> Optional[float]:
        """Get user's wallet balance"""
        user = UserService.get_user_by_id(db, user_id)
        return user.wallet_balance if user else None
    
    @staticmethod
    def deduct_wallet(db: Session, user_id: int, amount: float) -> Optional[User]:
        """Deduct money from user's wallet"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        
        if user.wallet_balance < amount:
            raise ValueError("Insufficient wallet balance")
        
        user.wallet_balance -= amount
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user (admin only)"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True
    
    @staticmethod
    def update_user_role(db: Session, user_id: int, new_role: str) -> Optional[User]:
        """Update user role (admin only)"""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        if new_role not in ["user", "admin"]:
            raise ValueError("Invalid role")
        
        user.role = new_role
        db.commit()
        db.refresh(user)
        return user
