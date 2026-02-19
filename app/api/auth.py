from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.user import authenticate_user, create_user, get_user_by_email, get_user_by_phone
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserCreateDriver, User as UserSchema

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new client (passenger) — most common flow"""
    existing = get_user_by_phone(db, phone=user_in.phone)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    user = create_user(db, user_in)
    return user


@router.post("/register/driver", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
def register_driver(
    driver_in: UserCreateDriver,
    db: Session = Depends(get_db)
    # Optionally: add Depends(get_current_active_superuser) if only admins can create drivers
):
    """Register a driver (individual or company)"""
    existing = get_user_by_phone(db, phone=driver_in.phone)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already registered"
        )
    if driver_in.email:
        existing = get_user_by_email(db, email=driver_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    user = create_user(db, driver_in)  # CRUD will handle role
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate with phone number and password"""
    if not (form_data.username or "").strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number is required",
        )
    if not (form_data.password or "").strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required",
        )

    user = authenticate_user(db, identifier=form_data.username.strip(), password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive account",
        )

    try:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.phone, "role": user.role.value},
            expires_delta=access_token_expires,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service temporarily unavailable",
        )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.value,
        "user_id": str(user.id),
    }