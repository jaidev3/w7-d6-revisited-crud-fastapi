# User Authentication System

A secure user authentication system built with FastAPI, featuring JWT tokens and role-based access control.

## Features

### 🔐 Authentication & Security
- **Password Hashing**: Secure bcrypt password hashing
- **JWT Tokens**: Stateless authentication with 30-minute expiration
- **Role-based Access Control**: USER and ADMIN roles
- **Password Validation**: Minimum 8 characters with special characters required
- **Duplicate Prevention**: Username and email uniqueness enforcement

### 🛡️ Security Features
- Secure password storage with bcrypt
- JWT token validation and expiration
- Protected routes with dependency injection
- Admin-only endpoints with role verification
- Proper error handling for authentication failures
- User role included in JWT payload

## API Endpoints

### Authentication Endpoints

#### POST `/auth/register`
Register a new user with password validation.

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!"
}
```

**Response (201):**
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z"
}
```

#### POST `/auth/login`
Login user and receive JWT token.

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
}
```

#### GET `/auth/me`
Get current user information (requires authentication).

**Headers:**
```
Authorization: Bearer <your-jwt-token>
```

**Response (200):**
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T12:00:00Z"
}
```

### User Management Endpoints (Admin Only)

#### GET `/users`
Get all users with pagination (admin only).

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum number of records to return (default: 100)

**Headers:**
```
Authorization: Bearer <admin-jwt-token>
```

#### PUT `/users/{user_id}/role`
Change user role (admin only).

**Request Body:**
```json
{
    "role": "admin"
}
```

#### DELETE `/users/{user_id}`
Delete a user (admin only).

**Response:** 204 No Content

## Setup and Installation

### Prerequisites
- Python 3.8+
- pip

### Installation Steps

1. **Clone or navigate to the project directory:**
```bash
cd user-authentication-system
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python main.py
```

The API will be available at `http://localhost:8000`

### API Documentation
Once running, visit:
- **Interactive API docs:** `http://localhost:8000/docs`
- **ReDoc documentation:** `http://localhost:8000/redoc`

## Testing

### Automated Testing
Run the comprehensive test suite:
```bash
python test_api.py
```

This will test:
- User registration with password validation
- User login and JWT token generation
- Protected route access
- Admin-only operations
- Unauthorized access attempts
- Invalid credentials handling

### Manual Testing with curl

#### Register a new user:
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "email": "test@example.com",
       "password": "SecurePass123!"
     }'
```

#### Login:
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "testuser",
       "password": "SecurePass123!"
     }'
```

#### Access protected route:
```bash
curl -X GET "http://localhost:8000/auth/me" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

## Security Considerations

### Password Requirements
- Minimum 8 characters
- Must contain at least one special character
- Hashed using bcrypt before storage

### JWT Configuration
- 30-minute token expiration
- Includes user role in payload
- Uses HS256 algorithm
- **Important:** Change the `SECRET_KEY` in `auth.py` for production

### Role-based Access
- **USER**: Can access `/auth/me` endpoint
- **ADMIN**: Can access all user management endpoints

## Project Structure

```
user-authentication-system/
├── main.py              # FastAPI application and route definitions
├── models.py            # SQLAlchemy database models
├── schemas.py           # Pydantic request/response schemas
├── database.py          # Database configuration and session management
├── auth.py              # Authentication utilities and JWT handling
├── crud.py              # Database operations
├── test_api.py          # Comprehensive API tests
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Error Handling

The API provides detailed error messages for various scenarios:

- **400 Bad Request**: Invalid input, duplicate username/email, weak password
- **401 Unauthorized**: Invalid credentials, missing/invalid token
- **403 Forbidden**: Insufficient permissions (non-admin accessing admin routes)
- **404 Not Found**: User not found
- **500 Internal Server Error**: Server-side errors

## Production Deployment

### Before deploying to production:

1. **Change the secret key** in `auth.py`:
```python
SECRET_KEY = "your-secure-production-secret-key"
```

2. **Use environment variables** for sensitive configuration
3. **Use a production database** (PostgreSQL, MySQL)
4. **Enable HTTPS** for secure token transmission
5. **Configure proper CORS** settings
6. **Set up monitoring** and logging

### Environment Variables
Consider using these environment variables:
- `SECRET_KEY`: JWT secret key
- `DATABASE_URL`: Database connection string
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

## License

This project is provided as an educational example for secure user authentication with FastAPI. 