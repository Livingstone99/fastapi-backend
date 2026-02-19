from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.config import settings
from app.api.v1 import api_router
from app.core.database import engine
from app.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    """Return 422 with clear validation errors."""
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )


@app.exception_handler(IntegrityError)
async def integrity_error_handler(_request: Request, exc: IntegrityError):
    """Duplicate or constraint violation -> 400 with safe message."""
    msg = (str(getattr(exc, "orig", exc))).lower()
    if "unique" in msg or "duplicate" in msg or "already exists" in msg:
        if "phone" in msg or "users_phone" in msg:
            return JSONResponse(status_code=400, content={"detail": "Phone number already registered"})
        if "email" in msg or "users_email" in msg:
            return JSONResponse(status_code=400, content={"detail": "Email already registered"})
        return JSONResponse(status_code=400, content={"detail": "A resource with this value already exists"})
    return JSONResponse(status_code=400, content={"detail": "Invalid data for this operation"})


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_error_handler(_request: Request, exc: SQLAlchemyError):
    """Other DB errors -> 503 so client can retry."""
    return JSONResponse(
        status_code=503,
        content={"detail": "Service temporarily unavailable. Please try again."},
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    return {"message": "Welcome to Waren Voyage API"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


