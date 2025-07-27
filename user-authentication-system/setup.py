#!/usr/bin/env python3
"""
Setup script for Phase 2 Authentication System
Installs dependencies and provides setup guidance
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a shell command with error handling"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported. Please use Python 3.8 or higher.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Python dependencies...")
    
    # Check if pip is available
    if not run_command("pip --version", "Checking pip availability"):
        print("❌ pip is not available. Please install pip first.")
        return False
    
    # Install requirements
    if os.path.exists("requirements.txt"):
        return run_command("pip install -r requirements.txt", "Installing requirements")
    else:
        print("❌ requirements.txt not found")
        return False

def check_redis():
    """Check Redis availability"""
    print("🔴 Checking Redis availability...")
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is running and accessible")
        return True
    except ImportError:
        print("⚠️  Redis package not installed (will be installed with requirements)")
        return False
    except Exception as e:
        print(f"⚠️  Redis not available: {str(e)}")
        print("ℹ️  The system will work without Redis but with reduced functionality")
        return False

def create_admin_user():
    """Create admin user if create_admin.py exists"""
    if os.path.exists("create_admin.py"):
        print("👤 Creating admin user...")
        return run_command("python create_admin.py", "Creating admin user")
    else:
        print("ℹ️  create_admin.py not found, skipping admin user creation")
        return True

def run_tests():
    """Run the test suite"""
    print("🧪 Running Phase 2 test suite...")
    if os.path.exists("test_phase2_api.py"):
        print("ℹ️  Starting API server for testing...")
        print("ℹ️  Please run 'python main.py' in another terminal first, then run:")
        print("ℹ️  python test_phase2_api.py")
        return True
    else:
        print("⚠️  test_phase2_api.py not found")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("🚀 PHASE 2 AUTHENTICATION SYSTEM SETUP")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Check Redis
    check_redis()
    
    # Create admin user
    create_admin_user()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    
    print("\n📋 NEXT STEPS:")
    print("1. Start the API server:")
    print("   python main.py")
    print("\n2. View API documentation:")
    print("   http://localhost:8000/docs")
    print("\n3. Run comprehensive tests:")
    print("   python test_phase2_api.py")
    print("\n4. Optional - Install Redis for full functionality:")
    print("   # macOS: brew install redis && brew services start redis")
    print("   # Ubuntu: sudo apt install redis-server")
    print("   # Windows: Use Docker or WSL")
    
    print("\n🛡️  PHASE 2 FEATURES INCLUDED:")
    print("✓ Rate limiting on sensitive endpoints")
    print("✓ Input sanitization and validation")
    print("✓ CORS configuration")
    print("✓ Security headers")
    print("✓ Token blacklisting (with Redis)")
    print("✓ Custom exception handlers")
    print("✓ Refresh token functionality")
    print("✓ Logout endpoint")
    print("✓ Forgot password endpoint")
    print("✓ Enhanced health check")
    
    print("\n🔧 CONFIGURATION:")
    print("- Edit main.py to configure CORS origins")
    print("- Change SECRET_KEY and REFRESH_SECRET_KEY for production")
    print("- Set up HTTPS for production deployment")
    
    print("\n📞 SUPPORT:")
    print("- Check README.md for detailed documentation")
    print("- Visit /docs for interactive API documentation")
    print("- Run health check: curl http://localhost:8000/health")

if __name__ == "__main__":
    main() 