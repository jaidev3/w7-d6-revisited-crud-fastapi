import redis
import json
from datetime import datetime, timedelta
from typing import Optional, Set
from fastapi import Request, HTTPException, status
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import bleach
import re

# Redis connection for token blacklist and rate limiting
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    redis_client = None
    REDIS_AVAILABLE = False

# In-memory fallback for token blacklist when Redis is not available
blacklisted_tokens: Set[str] = set()

# Rate limiter configuration
limiter = Limiter(key_func=get_remote_address)

class TokenBlacklist:
    """Token blacklist management"""
    
    @staticmethod
    def add_token(token: str, expires_at: datetime):
        """Add token to blacklist"""
        if REDIS_AVAILABLE:
            # Calculate TTL in seconds
            ttl = int((expires_at - datetime.utcnow()).total_seconds())
            if ttl > 0:
                redis_client.setex(f"blacklist:{token}", ttl, "true")
        else:
            blacklisted_tokens.add(token)
    
    @staticmethod
    def is_blacklisted(token: str) -> bool:
        """Check if token is blacklisted"""
        if REDIS_AVAILABLE:
            return redis_client.exists(f"blacklist:{token}") > 0
        return token in blacklisted_tokens
    
    @staticmethod
    def cleanup_expired():
        """Cleanup expired tokens (only needed for in-memory storage)"""
        if not REDIS_AVAILABLE:
            # In production, you'd want to track expiry times
            # For simplicity, we'll clear periodically
            pass

class InputSanitizer:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Remove HTML tags and sanitize input"""
        return bleach.clean(text.strip())
    
    @staticmethod
    def validate_email_format(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        pattern = r'^[a-zA-Z0-9_-]{3,50}$'
        return re.match(pattern, username) is not None

class SecurityHeaders:
    """Security headers middleware"""
    
    @staticmethod
    def add_security_headers(response):
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

def get_client_ip(request: Request) -> str:
    """Get client IP address with proxy support"""
    # Check for forwarded headers (for proxy/load balancer setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"

def check_redis_connection() -> bool:
    """Check Redis connection status"""
    if not REDIS_AVAILABLE:
        return False
    try:
        redis_client.ping()
        return True
    except:
        return False 