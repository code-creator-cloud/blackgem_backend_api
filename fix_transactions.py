#!/usr/bin/env python3
"""
Fix transactions table schema issues
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from sqlalchemy import text

def fix_transactions_table():
    """Fix the transactions table schema"""
    print("🔧 Fixing transactions table schema...")
    
    db = SessionLocal()
    
    try:
        # Check current columns
        result = db.execute(text("PRAGMA table_info(transactions)"))
        columns = [row[1] for row in result.fetchall()]
        print(f"Current columns: {columns}")
        
        # Add missing columns if they don't exist
        missing_columns = [
            ("currency", "VARCHAR DEFAULT 'XAF'"),
            ("transaction_id", "VARCHAR"),
            ("phone_number", "VARCHAR"),
            ("provider", "VARCHAR"),
            ("description", "TEXT"),
            ("updated_at", "DATETIME")
        ]
        
        for col_name, col_type in missing_columns:
            if col_name not in columns:
                print(f"📝 Adding {col_name} column...")
                db.execute(text(f"ALTER TABLE transactions ADD COLUMN {col_name} {col_type}"))
                print(f"✅ {col_name} column added")
        
        # Rename timestamp to created_at if it exists
        if 'timestamp' in columns and 'created_at' not in columns:
            print("📝 Renaming timestamp to created_at...")
            # SQLite doesn't support RENAME COLUMN directly, so we need to recreate the table
            # For now, let's just add created_at column and copy data
            db.execute(text("ALTER TABLE transactions ADD COLUMN created_at DATETIME"))
            db.execute(text("UPDATE transactions SET created_at = timestamp WHERE created_at IS NULL"))
            print("✅ created_at column added and data copied")
        
        db.commit()
        print("✅ Transactions table schema fixed!")
        
        # Verify the fix
        result = db.execute(text("PRAGMA table_info(transactions)"))
        columns = [row[1] for row in result.fetchall()]
        print(f"Updated columns: {columns}")
        
    except Exception as e:
        print(f"❌ Fix failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Fixing Transactions Table")
    print("=" * 50)
    
    fix_transactions_table()
    
    print("\n🎉 Schema fix completed!") 