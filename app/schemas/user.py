from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.user import UserRole  # Import enum for validation


class UserBase(BaseModel):
    phone: str = Field(..., pattern=r"^\+225[0-9]{8}$", description="Ivorian phone number format")
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: UserRole = UserRole.CLIENT


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    # On registration, most users start as CLIENT; drivers register via separate flow or flag


class UserCreateDriver(BaseModel):
    """Specialized create for drivers (individual or company)"""
    phone: str = Field(..., pattern=r"^\+225[0-9]{8}$")
    email: Optional[EmailStr] = None
    full_name: str
    password: str = Field(..., min_length=8)
    role: UserRole = Field(..., description="Use driver_individual or driver_company")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_active: Optional[bool] = None
    # Admins can update role/kyc in separate privileged endpoint


class UserInDB(BaseModel):
    id: UUID
    phone: str
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: UserRole
    is_kyc_verified: bool
    kyc_verified_at: Optional[datetime] = None
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # orm_mode in older Pydantic v1; still works in v2


class UserOut(UserInDB):
    """Public-facing response (hide sensitive fields)"""
    pass  # Can add .exclude = {"hashed_password"} in router if needed


# Alias for API response
User = UserOut