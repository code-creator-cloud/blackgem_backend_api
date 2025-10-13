#!/usr/bin/env python3
"""
Script to create admin user with a@gmail.com
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app import models
from app.admin_auth import get_password_hash

def create_admin_a():
    """Create admin user with a@gmail.com"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(models.Admin).filter(models.Admin.email == "a@gmail.com").first()
        if existing_admin:
            print("✅ Admin with email a@gmail.com already exists")
            return
        
        # Create admin
        hashed_password = get_password_hash("admin123")
        admin = models.Admin(
            email="a@gmail.com",
            hashed_password=hashed_password,
            role="admin",
            permissions='["user_management", "transaction_management", "system_monitoring", "security_monitoring", "notifications", "reports"]',
            is_active="active"
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ Admin created successfully!")
        print("📧 Email: a@gmail.com")
        print("🔑 Password: admin123")
        print("🔐 Role: admin")
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creating admin user with a@gmail.com...")
    create_admin_a()
