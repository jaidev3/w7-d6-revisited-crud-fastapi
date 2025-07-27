#!/usr/bin/env python3
"""
Setup script for QuickMed - Medicine Delivery Platform
Run this script to initialize the application with sample data.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible!")
    return True

def install_dependencies():
    """Install required dependencies."""
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing dependencies"):
        return False
    
    return True

def create_directories():
    """Create necessary directories."""
    directories = [
        "uploads",
        "uploads/prescriptions"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    return True

def initialize_database():
    """Initialize database with sample data."""
    return run_command(f"{sys.executable} sample_data.py", "Initializing database with sample data")

def show_startup_instructions():
    """Show instructions for starting the application."""
    print("\n" + "="*60)
    print("🎉 SETUP COMPLETED SUCCESSFULLY!")
    print("="*60)
    
    print("\n📋 TEST ACCOUNTS:")
    print("   👤 Customer:   customer@example.com   / password123")
    print("   💊 Pharmacist: pharmacist@example.com / pharmacist123")
    print("   🏥 Admin:      admin@example.com      / admin123")
    print("   🚚 Delivery:   delivery@example.com   / delivery123")
    
    print("\n🚀 TO START THE APPLICATION:")
    print("   1. Start FastAPI backend:")
    print("      python main.py")
    print("      └── API available at: http://localhost:8000")
    print("      └── API docs at: http://localhost:8000/docs")
    print("")
    print("   2. In a new terminal, start Streamlit frontend:")
    print("      streamlit run streamlit_app.py")
    print("      └── UI available at: http://localhost:8501")
    
    print("\n💡 QUICK START TIPS:")
    print("   • Use the customer account to browse medicines and place orders")
    print("   • Use the pharmacist account to verify prescriptions")
    print("   • Use the admin account to manage medicine catalog")
    print("   • Check the README.md for detailed feature walkthrough")
    
    print("\n🆘 NEED HELP?")
    print("   • Read the README.md for detailed documentation")
    print("   • Check API documentation at http://localhost:8000/docs")
    print("   • Emergency delivery hotline: +91 9876543210")
    
    print("\n" + "="*60)

def main():
    """Main setup function."""
    print("🏥 QuickMed - Medicine Delivery Platform Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    print("\n📦 Installing Dependencies...")
    if not install_dependencies():
        print("\n❌ Failed to install dependencies. Please check your internet connection and try again.")
        sys.exit(1)
    
    # Create directories
    print("\n📁 Creating Directories...")
    if not create_directories():
        print("\n❌ Failed to create directories.")
        sys.exit(1)
    
    # Initialize database
    print("\n🗄️ Setting Up Database...")
    if not initialize_database():
        print("\n❌ Failed to initialize database. Please check for any error messages above.")
        sys.exit(1)
    
    # Show startup instructions
    show_startup_instructions()

if __name__ == "__main__":
    main() 