#!/usr/bin/env python3
"""
Script to initialize admin database and create default super admin
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from app import models
from app.admin_auth import get_password_hash
from sqlalchemy import text

def init_admin_database():
    """Initialize admin database tables"""
    print("Creating admin database tables...")
    
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    print("✅ Admin database tables created successfully")

def create_super_admin(email: str, password: str):
    """Create a super admin user"""
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(models.Admin).filter(models.Admin.email == email).first()
        if existing_admin:
            print(f"⚠️  Admin with email {email} already exists")
            return
        
        # Create super admin
        hashed_password = get_password_hash(password)
        super_admin = models.Admin(
            email=email,
            hashed_password=hashed_password,
            role="super_admin",
            permissions='["user_management", "transaction_management", "system_monitoring", "security_monitoring", "notifications", "reports", "admin_management"]',
            is_active="active"
        )
        
        db.add(super_admin)
        db.commit()
        
        print(f"✅ Super admin created successfully with email: {email}")
        print("🔑 Default permissions granted:")
        print("   - user_management")
        print("   - transaction_management") 
        print("   - system_monitoring")
        print("   - security_monitoring")
        print("   - notifications")
        print("   - reports")
        print("   - admin_management")
        
    except Exception as e:
        print(f"❌ Error creating super admin: {e}")
        db.rollback()
    finally:
        db.close()

def create_sample_data():
    """Create sample data for testing"""
    db = SessionLocal()
    
    try:
        # Create sample security alerts
        sample_alerts = [
            models.SecurityAlert(
                alert_type="failed_login",
                severity="medium",
                message="Multiple failed login attempts detected",
                ip_address="192.168.1.100",
                resolved="false"
            ),
            models.SecurityAlert(
                alert_type="suspicious_transaction",
                severity="high",
                message="Large withdrawal request detected",
                resolved="false"
            )
        ]
        
        for alert in sample_alerts:
            existing = db.query(models.SecurityAlert).filter(
                models.SecurityAlert.alert_type == alert.alert_type,
                models.SecurityAlert.message == alert.message
            ).first()
            
            if not existing:
                db.add(alert)
        
        # Create sample system logs
        sample_logs = [
            models.SystemLog(
                log_type="info",
                message="System startup completed",
                details='{"startup_time": "2.3s", "services": ["api", "database", "cache"]}'
            ),
            models.SystemLog(
                log_type="warning",
                message="High memory usage detected",
                details='{"memory_usage": "85%", "threshold": "80%"}'
            )
        ]
        
        for log in sample_logs:
            existing = db.query(models.SystemLog).filter(
                models.SystemLog.log_type == log.log_type,
                models.SystemLog.message == log.message
            ).first()
            
            if not existing:
                db.add(log)
        
        db.commit()
        print("✅ Sample data created successfully")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Initializing Black Germ Admin Database...")
    print("=" * 50)
    
    # Initialize database
    init_admin_database()
    
    # Create super admin
    print("\n📧 Creating super admin...")
    email = input("Enter super admin email (default: admin@blackgerm.com): ").strip()
    if not email:
        email = "admin@blackgerm.com"
    
    password = input("Enter super admin password (default: admin123): ").strip()
    if not password:
        password = "admin123"
    
    create_super_admin(email, password)
    
    # Create sample data
    print("\n📊 Creating sample data...")
    create_sample_data()
    
    print("\n🎉 Admin database initialization completed!")
    print("=" * 50)
    print("📋 Next steps:")
    print("1. Start the backend server: python -m uvicorn app.main:app --reload")
    print("2. Access admin API at: http://localhost:8000/api/admin")
    print("3. Use the super admin credentials to login")
    print("4. Build the admin frontend dashboard") 