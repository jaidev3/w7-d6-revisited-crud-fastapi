from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta, datetime
import logging

# Import all necessary modules
from database import get_db, create_tables
from models import User, UserRole
from schemas import (
    UserCreate, UserLogin, UserResponse, UserUpdate, Token, RefreshToken,
    LogoutRequest, ForgotPasswordRequest, ForgotPasswordResponse, 
    HealthCheckResponse, ErrorResponse, TokenData
)
from auth import (
    create_access_token, create_refresh_token, get_current_active_user, 
    require_admin, verify_token, invalidate_token, get_token_expiry,
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
)
from crud import (
    create_user, get_users, update_user_role, delete_user, 
    authenticate_user, get_user_by_email
)

# Import security modules (will be created)
try:
    from security import (
        limiter, TokenBlacklist, InputSanitizer, SecurityHeaders,
        get_client_ip, check_redis_connection
    )
    from slowapi import _rate_limit_exceeded_handler
    from slowapi.errors import RateLimitExceeded
    SECURITY_AVAILABLE = True
except ImportError:
    # Fallback if security modules aren't available
    SECURITY_AVAILABLE = False
    limiter = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="User Authentication System - Phase 2",
    description="Enhanced secure user authentication system with JWT tokens, rate limiting, and comprehensive security measures",
    version="2.0.0"
)

# Add security middleware
if SECURITY_AVAILABLE:
    # Rate limiting middleware
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],  # Adjust for your frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    if SECURITY_AVAILABLE:
        response = SecurityHeaders.add_security_headers(response)
    return response

# Custom Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            detail=exc.detail,
            error_code=f"HTTP_{exc.status_code}",
            timestamp=datetime.utcnow()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            detail="Internal server error",
            error_code="INTERNAL_ERROR",
            timestamp=datetime.utcnow()
        ).dict()
    )

# Create database tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()
    logger.info("Database tables created successfully")

# Rate limiting decorators (conditionally applied)
def rate_limit(limit_string: str):
    """Conditional rate limiting decorator"""
    def decorator(func):
        if SECURITY_AVAILABLE and limiter:
            return limiter.limit(limit_string)(func)
        return func
    return decorator

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@rate_limit("3/minute")
def register_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with rate limiting"""
    try:
        # Additional input validation
        if SECURITY_AVAILABLE:
            if not InputSanitizer.validate_username(user.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid username format"
                )
            if not InputSanitizer.validate_email_format(user.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid email format"
                )
        
        db_user = create_user(db, user)
        logger.info(f"New user registered: {user.username}")
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@app.post("/auth/login", response_model=Token)
@rate_limit("5/minute")
def login_user(request: Request, user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT tokens with rate limiting"""
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        logger.warning(f"Failed login attempt for username: {user_credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create access and refresh tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value}, 
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "role": user.role.value}
    )
    
    logger.info(f"User logged in: {user.username}")
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "refresh_token": refresh_token
    }

@app.post("/auth/refresh", response_model=Token)
@rate_limit("10/minute")
def refresh_token(request: Request, refresh_data: RefreshToken, db: Session = Depends(get_db)):
    """Refresh JWT token using refresh token"""
    try:
        # Verify refresh token
        token_data = verify_token(refresh_data.refresh_token, "refresh")
        user = db.query(User).filter(User.username == token_data.username).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role.value},
            expires_delta=access_token_expires
        )
        
        logger.info(f"Token refreshed for user: {user.username}")
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )

@app.post("/auth/logout", response_model=dict)
def logout_user(logout_data: LogoutRequest, current_user: User = Depends(get_current_active_user)):
    """Logout user and invalidate token"""
    try:
        # Get token from request header or body
        from fastapi.security import HTTPBearer
        from fastapi import Request
        
        # In a real implementation, you'd extract the token from the Authorization header
        # For now, we'll assume it's provided or extract it from the dependency
        # This is a simplified version - in production, you'd want to extract the actual token
        
        logger.info(f"User logged out: {current_user.username}")
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error during logout"
        )

@app.post("/auth/forgot-password", response_model=ForgotPasswordResponse)
@rate_limit("1/minute")
def forgot_password(request: Request, forgot_data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Handle password reset request"""
    try:
        user = get_user_by_email(db, forgot_data.email)
        
        # Always return success to prevent email enumeration
        # In production, you'd send an actual email with reset token
        if user:
            logger.info(f"Password reset requested for: {user.email}")
            # TODO: Implement actual email sending with reset token
        else:
            logger.info(f"Password reset requested for non-existent email: {forgot_data.email}")
        
        return ForgotPasswordResponse(
            message="If the email exists in our system, you will receive password reset instructions"
        )
        
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing password reset request"
        )

@app.get("/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information (protected route)"""
    return current_user

# User management endpoints (admin only)
@app.get("/users", response_model=List[UserResponse])
@rate_limit("100/minute")
def get_all_users(
    request: Request,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Get all users (admin only)"""
    users = get_users(db, skip=skip, limit=limit)
    return users

@app.put("/users/{user_id}/role", response_model=UserResponse)
@rate_limit("50/minute")
def change_user_role(
    request: Request,
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Change user role (admin only)"""
    try:
        updated_user = update_user_role(db, user_id, user_update)
        logger.info(f"User role updated: {updated_user.username} -> {user_update.role}")
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Role update error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during role update"
        )

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@rate_limit("20/minute")
def delete_user_endpoint(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete user (admin only)"""
    try:
        delete_user(db, user_id)
        logger.info(f"User deleted by admin: {current_user.username}")
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User deletion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user deletion"
        )

# Enhanced Health check endpoint
@app.get("/health", response_model=HealthCheckResponse)
def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check endpoint"""
    try:
        # Check database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    # Check Redis connection if available
    redis_status = None
    if SECURITY_AVAILABLE:
        redis_status = "healthy" if check_redis_connection() else "unhealthy"
    
    overall_status = "healthy" if db_status == "healthy" else "unhealthy"
    
    return HealthCheckResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="2.0.0",
        database_status=db_status,
        redis_status=redis_status
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 