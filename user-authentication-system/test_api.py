import requests
import json

BASE_URL = "http://localhost:8000"

def test_user_registration():
    """Test user registration endpoint"""
    print("Testing user registration...")
    
    # Test valid user registration
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Registration Response: {response.status_code}")
    if response.status_code == 201:
        print(f"User registered: {response.json()}")
    else:
        print(f"Registration failed: {response.text}")
    
    # Test duplicate username
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Duplicate registration response: {response.status_code}")
    
    return response.status_code == 201

def test_admin_registration():
    """Register an admin user for testing"""
    print("Registering admin user...")
    
    admin_data = {
        "username": "admin",
        "email": "admin@example.com",
        "password": "AdminPass123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=admin_data)
    print(f"Admin Registration Response: {response.status_code}")
    return response.status_code == 201

def test_user_login():
    """Test user login endpoint"""
    print("Testing user login...")
    
    login_data = {
        "username": "testuser",
        "password": "SecurePass123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Login Response: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print(f"Login successful: {token_data}")
        return token_data["access_token"]
    else:
        print(f"Login failed: {response.text}")
        return None

def test_admin_login():
    """Test admin login"""
    print("Testing admin login...")
    
    login_data = {
        "username": "admin",
        "password": "AdminPass123!"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Admin Login Response: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print(f"Admin login successful: {token_data}")
        return token_data["access_token"]
    else:
        print(f"Admin login failed: {response.text}")
        return None

def test_get_current_user(token):
    """Test getting current user info"""
    print("Testing get current user...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Get current user response: {response.status_code}")
    if response.status_code == 200:
        user_info = response.json()
        print(f"Current user: {user_info}")
        return user_info
    else:
        print(f"Get current user failed: {response.text}")
        return None

def test_get_all_users(admin_token):
    """Test getting all users (admin only)"""
    print("Testing get all users (admin only)...")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/users", headers=headers)
    print(f"Get all users response: {response.status_code}")
    if response.status_code == 200:
        users = response.json()
        print(f"All users: {users}")
        return users
    else:
        print(f"Get all users failed: {response.text}")
        return None

def test_change_user_role(admin_token, user_id):
    """Test changing user role (admin only)"""
    print("Testing change user role...")
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    role_data = {"role": "admin"}
    
    response = requests.put(f"{BASE_URL}/users/{user_id}/role", json=role_data, headers=headers)
    print(f"Change role response: {response.status_code}")
    if response.status_code == 200:
        updated_user = response.json()
        print(f"Updated user: {updated_user}")
        return updated_user
    else:
        print(f"Change role failed: {response.text}")
        return None

def test_unauthorized_access():
    """Test accessing protected routes without token"""
    print("Testing unauthorized access...")
    
    # Try to access protected route without token
    response = requests.get(f"{BASE_URL}/auth/me")
    print(f"Unauthorized access response: {response.status_code}")
    
    # Try to access admin route without token
    response = requests.get(f"{BASE_URL}/users")
    print(f"Unauthorized admin access response: {response.status_code}")

def test_invalid_credentials():
    """Test login with invalid credentials"""
    print("Testing invalid credentials...")
    
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Invalid login response: {response.status_code}")
    if response.status_code != 200:
        print(f"Invalid login correctly rejected: {response.text}")

def test_weak_password():
    """Test registration with weak password"""
    print("Testing weak password validation...")
    
    user_data = {
        "username": "weakuser",
        "email": "weak@example.com",
        "password": "weak"  # Too short, no special characters
    }
    
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Weak password response: {response.status_code}")
    if response.status_code != 201:
        print(f"Weak password correctly rejected: {response.text}")

def run_all_tests():
    """Run all API tests"""
    print("=" * 50)
    print("STARTING API TESTS")
    print("=" * 50)
    
    # Test health check
    print("Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code} - {response.json()}")
    
    # Test weak password validation
    test_weak_password()
    
    # Test user registration
    if not test_user_registration():
        print("User registration failed, stopping tests")
        return
    
    # Test admin registration
    if not test_admin_registration():
        print("Admin registration failed, stopping tests")
        return
    
    # Test login
    user_token = test_user_login()
    admin_token = test_admin_login()
    
    if not user_token or not admin_token:
        print("Login failed, stopping tests")
        return
    
    # Test protected routes
    user_info = test_get_current_user(user_token)
    
    # Test admin operations
    users = test_get_all_users(admin_token)
    
    if user_info and users:
        # Test role change
        user_id = user_info["id"]
        test_change_user_role(admin_token, user_id)
    
    # Test unauthorized access
    test_unauthorized_access()
    
    # Test invalid credentials
    test_invalid_credentials()
    
    print("=" * 50)
    print("API TESTS COMPLETED")
    print("=" * 50)

if __name__ == "__main__":
    run_all_tests() 