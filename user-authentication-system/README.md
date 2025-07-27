# User Authentication System - Phase 2

Enhanced secure user authentication system with JWT tokens, comprehensive security measures, rate limiting, and advanced features.

## 🚀 Features

### Core Authentication
- JWT-based authentication with access and refresh tokens
- Role-based access control (User, Admin)
- Secure password hashing with bcrypt
- User registration and login with validation

### Phase 2 Security Enhancements
- **Rate Limiting**: Different limits for sensitive endpoints
  - Login attempts: 5 per minute per IP
  - Registration: 3 per minute per IP
  - Password reset: 1 per minute per IP
  - General API: 100 per minute per IP
- **Input Sanitization**: Clean and validate all user inputs
- **CORS Configuration**: Proper cross-origin policies
- **Security Headers**: HTTPS, HSTS, and other security headers
- **Token Blacklisting**: Invalidate tokens on logout
- **Error Handling**: Custom exception handlers with proper HTTP codes

### New Endpoints
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/logout` - Logout user (invalidate token)
- `POST /auth/forgot-password` - Password reset request
- `GET /health` - Enhanced health check endpoint

## 📋 Requirements

- Python 3.8+
- FastAPI
- SQLAlchemy
- Redis (optional, for enhanced token management)
- Other dependencies listed in requirements.txt

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd user-authentication-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Optional: Setup Redis (for enhanced security features)**
   ```bash
   # On macOS
   brew install redis
   brew services start redis
   
   # On Ubuntu/Debian
   sudo apt update
   sudo apt install redis-server
   sudo systemctl start redis-server
   
   # On Windows (using WSL or Docker)
   docker run -d -p 6379:6379 redis:alpine
   ```

5. **Run the application**
   ```bash
   python main.py
   ```

   Or using uvicorn directly:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 🔧 Configuration

### Environment Variables (Optional)
Create a `.env` file in the project root:

```env
SECRET_KEY=your-super-secret-key-change-in-production
REFRESH_SECRET_KEY=your-refresh-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///./user_auth.db
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

### Security Settings
- Change the `SECRET_KEY` and `REFRESH_SECRET_KEY` in production
- Configure allowed hosts for your domain
- Set up HTTPS in production
- Configure Redis for production token management

## 📚 API Documentation

Once the server is running, visit:
- **Interactive API Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "SecurePass123!"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "testuser",
  "password": "SecurePass123!"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Refresh Token
```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Logout
```http
POST /auth/logout
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "token": "optional_token_to_invalidate"
}
```

#### Forgot Password
```http
POST /auth/forgot-password
Content-Type: application/json

{
  "email": "test@example.com"
}
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <access_token>
```

### Admin Endpoints

#### Get All Users (Admin Only)
```http
GET /users?skip=0&limit=100
Authorization: Bearer <admin_access_token>
```

#### Update User Role (Admin Only)
```http
PUT /users/{user_id}/role
Authorization: Bearer <admin_access_token>
Content-Type: application/json

{
  "role": "ADMIN"
}
```

#### Delete User (Admin Only)
```http
DELETE /users/{user_id}
Authorization: Bearer <admin_access_token>
```

### Health Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "version": "2.0.0",
  "database_status": "healthy",
  "redis_status": "healthy"
}
```

## 🛡️ Security Features

### Rate Limiting
The API implements rate limiting with the following rules:
- **Login**: 5 attempts per minute per IP
- **Registration**: 3 attempts per minute per IP
- **Password Reset**: 1 attempt per minute per IP
- **General API**: 100 requests per minute per IP

### Input Validation
- Username: 3-50 characters, alphanumeric with underscores and hyphens
- Password: 8-128 characters with uppercase, lowercase, digit, and special character
- Email: Valid email format with sanitization

### Security Headers
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`
- `Referrer-Policy: strict-origin-when-cross-origin`

### Token Management
- Access tokens expire in 30 minutes
- Refresh tokens expire in 7 days
- Token blacklisting on logout
- Separate secret keys for access and refresh tokens

## 🧪 Testing

### Create Admin User
```bash
python create_admin.py
```

### Run API Tests
```bash
python test_api.py
```

### Manual Testing Examples

1. **Register a new user**:
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
        -H "Content-Type: application/json" \
        -d '{"username": "testuser", "email": "test@example.com", "password": "SecurePass123!"}'
   ```

2. **Login**:
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "testuser", "password": "SecurePass123!"}'
   ```

3. **Access protected endpoint**:
   ```bash
   curl -X GET "http://localhost:8000/auth/me" \
        -H "Authorization: Bearer <your_access_token>"
   ```

## 🚀 Production Deployment

### Security Checklist
- [ ] Change default secret keys
- [ ] Set up HTTPS with SSL certificates
- [ ] Configure proper CORS origins
- [ ] Set up Redis for production
- [ ] Configure proper database (PostgreSQL recommended)
- [ ] Set up monitoring and logging
- [ ] Configure firewall rules
- [ ] Set up rate limiting at reverse proxy level
- [ ] Enable database connection pooling
- [ ] Set up automated backups

### Docker Deployment (Optional)
```dockerfile
# Example Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🐛 Troubleshooting

### Common Issues

1. **Redis Connection Error**:
   - The system works without Redis but with reduced functionality
   - Install and start Redis server for full features

2. **Rate Limiting Not Working**:
   - Check if slowapi is installed: `pip install slowapi`
   - Ensure Redis is running for persistent rate limiting

3. **CORS Issues**:
   - Update allowed origins in main.py
   - Check browser console for CORS errors

4. **Token Errors**:
   - Ensure tokens are included in Authorization header
   - Check token expiry times
   - Verify secret keys are consistent

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the API documentation at `/docs`
- Review this README
- Check the troubleshooting section
- Open an issue on the repository 