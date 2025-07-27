#!/usr/bin/env python3
"""
Database migration script for production deployment.
This script ensures database tables are created and can be run safely multiple times.
"""

import os
import sys
from sqlalchemy import create_engine, inspect
from database import DATABASE_URL, Base
import models

def check_database_connection():
    """Check if database connection is working."""
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def create_tables():
    """Create database tables if they don't exist."""
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print(f"📋 Existing tables: {existing_tables}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Check what tables were created
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        new_tables = set(all_tables) - set(existing_tables)
        
        if new_tables:
            print(f"✅ Created new tables: {list(new_tables)}")
        else:
            print("✅ All tables already exist")
            
        print(f"📊 Total tables in database: {len(all_tables)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create tables: {e}")
        return False

def verify_tables():
    """Verify that all required tables exist."""
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        
        # Define expected tables based on models
        expected_tables = {
            'users',
            'medical_profiles', 
            'pharmacies',
            'medicines',
            'inventory',
            'prescriptions',
            'orders',
            'order_items',
            'deliveries',
            'payments',
            'reviews',
            'notifications'
        }
        
        missing_tables = expected_tables - existing_tables
        if missing_tables:
            print(f"⚠️  Missing tables: {list(missing_tables)}")
            return False
        else:
            print("✅ All required tables exist")
            return True
            
    except Exception as e:
        print(f"❌ Failed to verify tables: {e}")
        return False

def main():
    """Main migration function."""
    print("🚀 Starting database migration...")
    print(f"📍 Database URL: {DATABASE_URL.split('@')[0]}@***")  # Hide password
    
    # Check database connection
    if not check_database_connection():
        sys.exit(1)
    
    # Create tables
    if not create_tables():
        sys.exit(1)
    
    # Verify tables
    if not verify_tables():
        sys.exit(1)
    
    print("🎉 Database migration completed successfully!")

if __name__ == "__main__":
    main() 