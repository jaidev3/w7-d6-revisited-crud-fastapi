"""
Utility script to create an admin user
Run this after starting the server to create an admin user for testing
"""

from sqlalchemy.orm import Session
from database import SessionLocal, create_tables
from models import User, UserRole
from auth import get_password_hash

def create_admin_user():
    """Create an admin user"""
    # Create tables if they don't exist
    create_tables()
    
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        hashed_password = get_password_hash("AdminPass123!")
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hashed_password,
            role=UserRole.ADMIN
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("Admin user created successfully!")
        print(f"Username: admin")
        print(f"Password: AdminPass123!")
        print(f"Email: admin@example.com")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user() 