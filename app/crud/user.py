from sqlalchemy.orm import Session
from typing import Optional, Union
from uuid import UUID

from app.models import User, UserRole
from app.schemas.user import UserCreate, UserCreateDriver, UserUpdate
from app.core.security import get_password_hash, verify_password


def get_user(db: Session, user_id: UUID) -> Optional[User]:
    """Get a user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_phone(db: Session, phone: str) -> Optional[User]:
    """Get a user by phone number."""
    return db.query(User).filter(User.phone == phone).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Get a list of users"""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(
    db: Session,
    user_in: Union[UserCreate, UserCreateDriver],
) -> User:
    """Create a new user (client or driver)."""
    hashed_password = get_password_hash(user_in.password)
    role = user_in.role if isinstance(user_in.role, UserRole) else UserRole(user_in.role)
    db_user = User(
        phone=user_in.phone,
        email=user_in.email,
        hashed_password=hashed_password,
        full_name=user_in.full_name,
        role=role,
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
    """Update a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: UUID) -> bool:
    """Delete a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, identifier: str, password: str) -> Optional[User]:
    """Authenticate a user by phone and password."""
    user = get_user_by_phone(db, identifier)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

