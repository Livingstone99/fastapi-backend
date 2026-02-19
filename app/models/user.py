import uuid
from enum import Enum as PyEnum
from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class UserRole(str, PyEnum):
    CLIENT = "client"              # Passenger / Traveler
    DRIVER_INDIVIDUAL = "driver_individual"
    DRIVER_COMPANY = "driver_company"
    ADMIN = "admin"
    SUPERADMIN = "superadmin"      # Optional: for platform owners


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=True)          # Optional if phone-first
    phone = Column(String, unique=True, index=True, nullable=False)        # e.g. +225xxxxxxxxxx
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(
        Enum(UserRole, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        index=True,
        default=UserRole.CLIENT,
    )
    
    # KYC & Verification
    is_kyc_verified = Column(Boolean, default=False, nullable=False)
    kyc_verified_at = Column(DateTime(timezone=True), nullable=True)
    kyc_documents_status = Column(String, nullable=True)                   # e.g. "pending", "approved", "rejected", JSON later if needed
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)          # Keep for flexibility, but role covers most cases
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)