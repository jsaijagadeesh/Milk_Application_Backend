from sqlalchemy.orm import Session
from models.user import User
from models.address import Address
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
    def update_profile(db: Session, user_id: int, name: Optional[str], email: Optional[str], password: Optional[str]) -> Optional[User]:
        """Update user's own profile (name, email, password — role NOT allowed)"""
        from services.auth_service import AuthService
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        if name is not None:
            user.name = name
        if email is not None:
            # Ensure the new email is not taken by another user
            existing = UserService.get_user_by_email(db, email)
            if existing and existing.id != user_id:
                raise ValueError("Email already in use by another account")
            user.email = email
        if password is not None:
            user.password_hash = AuthService.hash_password(password)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def admin_update_user(
        db: Session,
        user_id: int,
        name: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[User]:
        """Admin update — can modify all fields including role and is_active"""
        from services.auth_service import AuthService
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None

        if name is not None:
            user.name = name
        if email is not None:
            existing = UserService.get_user_by_email(db, email)
            if existing and existing.id != user_id:
                raise ValueError("Email already in use by another account")
            user.email = email
        if password is not None:
            user.password_hash = AuthService.hash_password(password)
        if role is not None:
            if role not in ["user", "admin"]:
                raise ValueError("Invalid role. Must be 'user' or 'admin'")
            user.role = role
        if is_active is not None:
            user.is_active = is_active

        db.commit()
        db.refresh(user)
        return user

    # ==================== WALLET ====================

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

    # ==================== ADDRESS ====================

    @staticmethod
    def get_addresses(db: Session, user_id: int) -> List[Address]:
        """Get all addresses for a user"""
        return db.query(Address).filter(Address.user_id == user_id).all()

    @staticmethod
    def get_address_by_id(db: Session, address_id: int) -> Optional[Address]:
        """Get a specific address by ID"""
        return db.query(Address).filter(Address.id == address_id).first()

    @staticmethod
    def get_user_address(db: Session, user_id: int) -> Optional[Address]:
        """Get the single address for a user (enforces one address per user)"""
        # Return default first, fallback to first address
        address = db.query(Address).filter(
            Address.user_id == user_id, Address.is_default == True
        ).first()
        if not address:
            address = db.query(Address).filter(Address.user_id == user_id).first()
        return address

    @staticmethod
    def upsert_default_address(
        db: Session,
        user_id: int,
        street: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
    ) -> Optional[Address]:
        """
        Create the user's default address if they don't have one yet,
        or update the existing default address. Used by register & profile update.
        At least one address field must be provided to do anything.
        """
        has_data = any(v is not None for v in [street, city, state, postal_code, country])
        if not has_data:
            return None

        default_address = db.query(Address).filter(
            Address.user_id == user_id, Address.is_default == True
        ).first()

        if default_address:
            # Update existing default
            if street is not None:
                default_address.street = street
            if city is not None:
                default_address.city = city
            if state is not None:
                default_address.state = state
            if postal_code is not None:
                default_address.postal_code = postal_code
            if country is not None:
                default_address.country = country
            db.commit()
            db.refresh(default_address)
            return default_address
        else:
            # No address yet — create a new default one
            # All required fields must be present to create
            if not all([street, city, state, postal_code]):
                raise ValueError("street, city, state, and postal_code are required when adding address for the first time")
            new_address = Address(
                user_id=user_id,
                street=street,
                city=city,
                state=state,
                postal_code=postal_code,
                country=country or "India",
                is_default=True,
            )
            db.add(new_address)
            db.commit()
            db.refresh(new_address)
            return new_address

    @staticmethod
    def create_address(
        db: Session,
        user_id: int,
        street: str,
        city: str,
        state: str,
        postal_code: str,
        country: str = "India",
        is_default: bool = False,
    ) -> Address:
        """Create a new address for a user"""
        # If this is the first address or is_default requested, manage defaults
        if is_default:
            # Unset previous default
            db.query(Address).filter(Address.user_id == user_id, Address.is_default == True).update({"is_default": False})

        # If no addresses exist yet, make this one the default automatically
        existing_count = db.query(Address).filter(Address.user_id == user_id).count()
        if existing_count == 0:
            is_default = True

        address = Address(
            user_id=user_id,
            street=street,
            city=city,
            state=state,
            postal_code=postal_code,
            country=country,
            is_default=is_default,
        )
        db.add(address)
        db.commit()
        db.refresh(address)
        return address

    @staticmethod
    def update_address(
        db: Session,
        address_id: int,
        user_id: int,
        street: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        postal_code: Optional[str] = None,
        country: Optional[str] = None,
        is_default: Optional[bool] = None,
    ) -> Optional[Address]:
        """Update an existing address"""
        address = db.query(Address).filter(Address.id == address_id, Address.user_id == user_id).first()
        if not address:
            return None

        if street is not None:
            address.street = street
        if city is not None:
            address.city = city
        if state is not None:
            address.state = state
        if postal_code is not None:
            address.postal_code = postal_code
        if country is not None:
            address.country = country
        if is_default is True:
            # Unset previous default for this user
            db.query(Address).filter(Address.user_id == user_id, Address.is_default == True).update({"is_default": False})
            address.is_default = True
        elif is_default is False:
            address.is_default = False

        db.commit()
        db.refresh(address)
        return address

    @staticmethod
    def delete_address(db: Session, address_id: int, user_id: int) -> bool:
        """Delete an address"""
        address = db.query(Address).filter(Address.id == address_id, Address.user_id == user_id).first()
        if not address:
            return False

        db.delete(address)
        db.commit()
        return True

    @staticmethod
    def set_default_address(db: Session, address_id: int, user_id: int) -> Optional[Address]:
        """Set an address as the default for a user"""
        address = db.query(Address).filter(Address.id == address_id, Address.user_id == user_id).first()
        if not address:
            return None

        # Unset current default
        db.query(Address).filter(Address.user_id == user_id, Address.is_default == True).update({"is_default": False})
        address.is_default = True
        db.commit()
        db.refresh(address)
        return address