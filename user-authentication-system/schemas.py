from pydantic import BaseModel, EmailStr, field_validator, validator
from typing import Optional
from datetime import datetime
from models import UserRole
import re
import bleach

class UserBase(BaseModel):
    username: str
    email: EmailStr
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        # Sanitize input
        v = bleach.clean(v.strip())
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters long')
        if not re.match("^[a-zA-Z0-9_-]+$", v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v

class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if len(v) > 128:
            raise ValueError('Password must be less than 128 characters long')
        
        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in v)
        
        if not all([has_upper, has_lower, has_digit, has_special]):
            raise ValueError('Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character')
        
        return v

class UserLogin(BaseModel):
    username: str
    password: str
    
    @field_validator('username')
    @classmethod
    def sanitize_username(cls, v):
        return bleach.clean(v.strip())

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    role: UserRole

class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: Optional[int] = None

class RefreshToken(BaseModel):
    refresh_token: str

class TokenData(BaseModel):
    username: Optional[str] = None
    token_type: Optional[str] = "access"

class LogoutRequest(BaseModel):
    token: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str
    
class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    database_status: str
    redis_status: Optional[str] = None

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime 