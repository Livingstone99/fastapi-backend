"""
Script to initialize the database.
Run this after setting up your .env file and creating the PostgreSQL database.
"""
from app.core.database import engine, Base
from app.models import User  # Import all models

if __name__ == "__main__":
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


