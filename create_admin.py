#!/usr/bin/env python3
"""
Script to create a default admin user
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app import models
from app.admin_auth import get_password_hash

def create_default_admin():
    """Create a default admin user"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(models.Admin).filter(models.Admin.email == "admin@blackgerm.com").first()
        if existing_admin:
            print("✅ Admin with email admin@blackgerm.com already exists")
            return
        
        # Create super admin
        hashed_password = get_password_hash("admin123")
        super_admin = models.Admin(
            email="admin@blackgerm.com",
            hashed_password=hashed_password,
            role="super_admin",
            permissions='["user_management", "transaction_management", "system_monitoring", "security_monitoring", "notifications", "reports", "admin_management"]',
            is_active="active"
        )
        
        db.add(super_admin)
        db.commit()
        
        print("✅ Super admin created successfully!")
        print("📧 Email: admin@blackgerm.com")
        print("🔑 Password: admin123")
        print("🔐 Role: super_admin")
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creating default admin user...")
    create_default_admin()
