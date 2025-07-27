#!/usr/bin/env python3
"""
Comprehensive test suite for Phase 2 Authentication System
Tests all new security features, rate limiting, and endpoints
"""

import requests
import json
import time
from datetime import datetime
import sys

# Base URL for the API
BASE_URL = "http://localhost:8000"

# Test data
TEST_USER = {
    "username": "phase2testuser",
    "email": "phase2test@example.com",
    "password": "SecurePass123!"
}

WEAK_PASSWORD_USER = {
    "username": "weakuser",
    "email": "weak@example.com",
    "password": "weak"
}

INVALID_USERNAME_USER = {
    "username": "user@invalid",
    "email": "test@example.com",
    "password": "SecurePass123!"
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_test_header(test_name):
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}Testing: {test_name}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.END}")

def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")

def test_health_check():
    """Test enhanced health check endpoint"""
    print_test_header("Enhanced Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["status", "timestamp", "version", "database_status"]
            
            if all(field in data for field in required_fields):
                print_success("Health check endpoint returns all required fields")
                print_info(f"Status: {data['status']}")
                print_info(f"Version: {data['version']}")
                print_info(f"Database: {data['database_status']}")
                
                if "redis_status" in data:
                    print_info(f"Redis: {data['redis_status']}")
                else:
                    print_warning("Redis status not available (Redis not configured)")
                
                return True
            else:
                print_error("Health check missing required fields")
                return False
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to the API. Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_input_validation():
    """Test enhanced input validation"""
    print_test_header("Input Validation")
    
    # Test weak password
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=WEAK_PASSWORD_USER)
        if response.status_code == 422:
            print_success("Weak password rejected correctly")
        else:
            print_error(f"Weak password validation failed: {response.status_code}")
    except Exception as e:
        print_error(f"Weak password test error: {str(e)}")
    
    # Test invalid username format
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=INVALID_USERNAME_USER)
        if response.status_code in [400, 422]:
            print_success("Invalid username format rejected")
        else:
            print_error(f"Invalid username validation failed: {response.status_code}")
    except Exception as e:
        print_error(f"Invalid username test error: {str(e)}")
    
    # Test valid registration
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=TEST_USER)
        if response.status_code == 201:
            print_success("Valid user registration accepted")
            return True
        else:
            print_error(f"Valid registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Registration test error: {str(e)}")
        return False

def test_login_and_tokens():
    """Test login with refresh token functionality"""
    print_test_header("Login and Token Management")
    
    try:
        # Login
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        })
        
        if response.status_code == 200:
            data = response.json()
            required_fields = ["access_token", "token_type", "expires_in"]
            
            if all(field in data for field in required_fields):
                print_success("Login successful with enhanced token response")
                
                # Check if refresh token is included
                if "refresh_token" in data:
                    print_success("Refresh token included in login response")
                    return data["access_token"], data.get("refresh_token")
                else:
                    print_warning("Refresh token not included (fallback mode)")
                    return data["access_token"], None
            else:
                print_error("Login response missing required fields")
                return None, None
        else:
            print_error(f"Login failed: {response.status_code} - {response.text}")
            return None, None
            
    except Exception as e:
        print_error(f"Login test error: {str(e)}")
        return None, None

def test_refresh_token(refresh_token):
    """Test refresh token functionality"""
    print_test_header("Refresh Token")
    
    if not refresh_token:
        print_warning("No refresh token available to test")
        return None
    
    try:
        response = requests.post(f"{BASE_URL}/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print_success("Token refresh successful")
                return data["access_token"]
            else:
                print_error("Refresh response missing access_token")
                return None
        else:
            print_error(f"Token refresh failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print_error(f"Refresh token test error: {str(e)}")
        return None

def test_logout(access_token):
    """Test logout functionality"""
    print_test_header("Logout")
    
    if not access_token:
        print_warning("No access token available to test logout")
        return
    
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.post(f"{BASE_URL}/auth/logout", 
                               json={"token": access_token}, 
                               headers=headers)
        
        if response.status_code == 200:
            print_success("Logout successful")
            
            # Try to use the token after logout
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            if response.status_code == 401:
                print_success("Token invalidated after logout")
            else:
                print_warning("Token still valid after logout (token blacklisting may not be configured)")
        else:
            print_error(f"Logout failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print_error(f"Logout test error: {str(e)}")

def test_forgot_password():
    """Test forgot password functionality"""
    print_test_header("Forgot Password")
    
    try:
        # Test with existing email
        response = requests.post(f"{BASE_URL}/auth/forgot-password", json={
            "email": TEST_USER["email"]
        })
        
        if response.status_code == 200:
            data = response.json()
            if "message" in data:
                print_success("Forgot password request processed (existing email)")
            else:
                print_error("Forgot password response missing message")
        else:
            print_error(f"Forgot password failed: {response.status_code}")
        
        # Test with non-existing email
        response = requests.post(f"{BASE_URL}/auth/forgot-password", json={
            "email": "nonexistent@example.com"
        })
        
        if response.status_code == 200:
            print_success("Forgot password request processed (non-existing email - no enumeration)")
        else:
            print_error(f"Forgot password with non-existing email failed: {response.status_code}")
            
    except Exception as e:
        print_error(f"Forgot password test error: {str(e)}")

def test_rate_limiting():
    """Test rate limiting functionality"""
    print_test_header("Rate Limiting")
    
    print_info("Testing registration rate limiting (3/minute)...")
    
    # Try to register multiple users quickly
    rate_limit_hit = False
    for i in range(5):
        test_user = {
            "username": f"ratetest{i}",
            "email": f"ratetest{i}@example.com",
            "password": "SecurePass123!"
        }
        
        response = requests.post(f"{BASE_URL}/auth/register", json=test_user)
        
        if response.status_code == 429:
            print_success(f"Rate limit hit on attempt {i+1} (as expected)")
            rate_limit_hit = True
            break
        elif response.status_code in [201, 400]:  # 400 for duplicate users
            print_info(f"Registration attempt {i+1}: {response.status_code}")
        else:
            print_warning(f"Unexpected response {response.status_code} on attempt {i+1}")
        
        # Small delay to avoid overwhelming
        time.sleep(0.1)
    
    if not rate_limit_hit:
        print_warning("Rate limiting may not be configured or limits are higher than expected")
    
    print_info("Testing login rate limiting (5/minute)...")
    
    # Try multiple login attempts
    login_rate_limit_hit = False
    for i in range(7):
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "username": "nonexistent",
            "password": "wrongpassword"
        })
        
        if response.status_code == 429:
            print_success(f"Login rate limit hit on attempt {i+1}")
            login_rate_limit_hit = True
            break
        elif response.status_code == 401:
            print_info(f"Login attempt {i+1}: Unauthorized (expected)")
        else:
            print_warning(f"Unexpected login response {response.status_code} on attempt {i+1}")
        
        time.sleep(0.1)
    
    if not login_rate_limit_hit:
        print_warning("Login rate limiting may not be configured")

def test_security_headers():
    """Test security headers"""
    print_test_header("Security Headers")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy"
        ]
        
        headers_found = 0
        for header in security_headers:
            if header in response.headers:
                print_success(f"Security header present: {header}")
                headers_found += 1
            else:
                print_warning(f"Security header missing: {header}")
        
        if headers_found >= len(security_headers) // 2:
            print_success("Security headers are configured")
        else:
            print_warning("Security headers may not be fully configured")
            
    except Exception as e:
        print_error(f"Security headers test error: {str(e)}")

def test_protected_endpoints(access_token):
    """Test protected endpoints with authentication"""
    print_test_header("Protected Endpoints")
    
    if not access_token:
        print_warning("No access token available for protected endpoint testing")
        return
    
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        # Test /auth/me endpoint
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            print_success("Protected endpoint /auth/me accessible with valid token")
        else:
            print_error(f"Protected endpoint failed: {response.status_code}")
        
        # Test without token
        response = requests.get(f"{BASE_URL}/auth/me")
        if response.status_code == 401:
            print_success("Protected endpoint correctly rejects requests without token")
        else:
            print_warning(f"Protected endpoint without token returned: {response.status_code}")
            
    except Exception as e:
        print_error(f"Protected endpoints test error: {str(e)}")

def main():
    """Run all Phase 2 authentication tests"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 70)
    print("         PHASE 2 AUTHENTICATION SYSTEM TEST SUITE")
    print("=" * 70)
    print(f"{Colors.END}")
    
    # Test sequence
    tests = [
        ("Health Check", test_health_check),
        ("Input Validation", test_input_validation),
        ("Security Headers", test_security_headers),
        ("Rate Limiting", test_rate_limiting),
        ("Forgot Password", test_forgot_password),
    ]
    
    # Run basic tests
    for test_name, test_func in tests:
        try:
            if test_name == "Input Validation":
                result = test_func()
                if not result:
                    print_error("Registration failed, skipping token-dependent tests")
                    continue
            else:
                test_func()
        except Exception as e:
            print_error(f"Test {test_name} failed with exception: {str(e)}")
    
    # Run token-dependent tests
    print_info("Running token-dependent tests...")
    access_token, refresh_token = test_login_and_tokens()
    
    if access_token:
        test_protected_endpoints(access_token)
        
        if refresh_token:
            new_access_token = test_refresh_token(refresh_token)
            if new_access_token:
                access_token = new_access_token
        
        test_logout(access_token)
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 70)
    print("                    TEST SUITE COMPLETED")
    print("=" * 70)
    print(f"{Colors.END}")
    
    print_info("Notes:")
    print_info("- Some warnings are expected if Redis is not configured")
    print_info("- Rate limiting may take time to trigger depending on configuration")
    print_info("- Security features work in fallback mode without Redis")

if __name__ == "__main__":
    main() 