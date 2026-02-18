# Waren Voyage Backend

FastAPI backend with PostgreSQL database, authentication, and user management.

## Project Structure

```
backend/
├── app/
│   ├── api/           # API routes
│   │   ├── auth.py    # Authentication endpoints
│   │   ├── users.py   # User management endpoints
│   │   ├── deps.py    # Dependencies (auth, db)
│   │   └── v1.py      # API router
│   ├── core/          # Core configuration
│   │   ├── config.py  # Settings
│   │   ├── database.py # Database connection
│   │   └── security.py # Security utilities
│   ├── crud/          # Database operations
│   │   └── user.py    # User CRUD operations
│   ├── models/        # SQLAlchemy models
│   │   └── user.py    # User model
│   └── schemas/       # Pydantic schemas
│       ├── user.py    # User schemas
│       └── token.py   # Token schemas
├── main.py            # Application entry point
└── requirements.txt   # Python dependencies
```

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Create a `.env` file:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/waren_voyage_db
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
PROJECT_NAME=Waren Voyage API
API_V1_STR=/api/v1
```

3. **Create PostgreSQL database:**
```bash
createdb waren_voyage_db
```

4. **Run the application:**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login and get access token

### Users
- `GET /api/v1/users/me` - Get current user info
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users/` - List all users (superuser only)
- `GET /api/v1/users/{user_id}` - Get user by ID (superuser only)
- `PUT /api/v1/users/{user_id}` - Update user (superuser only)
- `DELETE /api/v1/users/{user_id}` - Delete user (superuser only)

## Authentication

The API uses JWT tokens for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-token>
```

