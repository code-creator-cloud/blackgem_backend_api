#!/usr/bin/env python3
"""
Database migration script to initialize database schema
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from sqlalchemy import text
import logging
from app import models

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/migration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def migrate_database():
    """Initialize or migrate the database schema"""
    logger.info("Starting database migration...")
    
    db = SessionLocal()
    
    try:
        # Check if users table exists
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='users'"))
        if not result.fetchone():
            logger.info("Users table does not exist, creating all tables...")
            models.Base.metadata.create_all(bind=engine)
            logger.info("All tables created successfully")
        else:
            logger.info("Users table already exists, checking schema...")
            # Check if columns exist in users table
            result = db.execute(text("PRAGMA table_info(users)"))
            columns = [row[1] for row in result.fetchall()]
            logger.info(f"Current users table columns: {columns}")
            
            # Add status column if missing
            if 'status' not in columns:
                logger.info("Adding status column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR DEFAULT 'active'"))
                logger.info("Status column added successfully")
            
            # Add username column if missing
            if 'username' not in columns:
                logger.info("Adding username column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR"))
                logger.info("Username column added successfully")
                
                # Set default usernames for existing users (if any)
                logger.info("Setting default usernames for existing users...")
                db.execute(text("UPDATE users SET username = 'user_' || id WHERE username IS NULL"))
                logger.info("Default usernames set successfully")
                
                # Create a new table with NOT NULL and UNIQUE constraints
                logger.info("Creating new table with NOT NULL and UNIQUE constraints for username...")
                db.execute(text("""
                    CREATE TABLE users_temp (
                        id INTEGER PRIMARY KEY,
                        email VARCHAR UNIQUE NOT NULL,
                        username VARCHAR UNIQUE NOT NULL,
                        hashed_password VARCHAR NOT NULL,
                        balance FLOAT DEFAULT 0.0,
                        wallet_address VARCHAR,
                        status VARCHAR DEFAULT 'active',
                        created_at DATETIME,
                        updated_at DATETIME
                    )
                """))
                # Copy data from old table to new table, including username
                logger.info("Copying data to new table...")
                db.execute(text("""
                    INSERT INTO users_temp (id, email, username, hashed_password, balance, wallet_address, status, created_at, updated_at)
                    SELECT id, email, COALESCE(username, 'user_' || id), hashed_password, balance, wallet_address, status, created_at, updated_at
                    FROM users
                """))
                logger.info("Data copied successfully")
                
                # Drop old table and rename new table
                logger.info("Dropping old users table and renaming new table...")
                db.execute(text("DROP TABLE users"))
                db.execute(text("ALTER TABLE users_temp RENAME TO users"))
                logger.info("Table renamed successfully")
                
                # Add unique index on username
                logger.info("Creating unique index on username...")
                db.execute(text("CREATE UNIQUE INDEX idx_users_username ON users(username)"))
                logger.info("Unique index on username created successfully")
            else:
                logger.info("Username column already exists")
                # Ensure NOT NULL constraint and unique index if column exists but constraints are missing
                result = db.execute(text("PRAGMA table_info(users)"))
                username_info = [row for row in result.fetchall() if row[1] == 'username']
                if username_info and username_info[0][3] == 0:  # Check if NOT NULL is missing
                    logger.info("Adding NOT NULL constraint to existing username column...")
                    db.execute(text("""
                        CREATE TABLE users_temp (
                            id INTEGER PRIMARY KEY,
                            email VARCHAR UNIQUE NOT NULL,
                            username VARCHAR UNIQUE NOT NULL,
                            hashed_password VARCHAR NOT NULL,
                            balance FLOAT DEFAULT 0.0,
                            wallet_address VARCHAR,
                            status VARCHAR DEFAULT 'active',
                            created_at DATETIME,
                            updated_at DATETIME
                        )
                    """))
                    db.execute(text("""
                        INSERT INTO users_temp (id, email, username, hashed_password, balance, wallet_address, status, created_at, updated_at)
                        SELECT id, email, COALESCE(username, 'user_' || id), hashed_password, balance, wallet_address, status, created_at, updated_at
                        FROM users
                    """))
                    db.execute(text("DROP TABLE users"))
                    db.execute(text("ALTER TABLE users_temp RENAME TO users"))
                    db.execute(text("CREATE UNIQUE INDEX idx_users_username ON users(username)"))
                    logger.info("NOT NULL constraint and unique index applied successfully")
        
        # Check if admin tables exist
        result = db.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='admins'"))
        if not result.fetchone():
            logger.info("Creating admin tables...")
            models.Base.metadata.create_all(bind=engine)
            logger.info("Admin tables created successfully")
        else:
            logger.info("Admin tables already exist")
        
        # Update existing users to have 'active' status
        logger.info("Updating status for users with NULL status...")
        db.execute(text("UPDATE users SET status = 'active' WHERE status IS NULL"))
        logger.info("Status update completed")
        
        db.commit()
        logger.info("Database migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()

def verify_database():
    """Verify the database structure"""
    logger.info("Verifying database structure...")
    
    db = SessionLocal()
    
    try:
        # Check users table
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]
        logger.info(f"Users table columns: {columns}")
        
        # Check admins table
        result = db.execute(text("PRAGMA table_info(admins)"))
        columns = [row[1] for row in result.fetchall()]
        logger.info(f"Admins table columns: {columns}")
        
        # Check transactions table
        result = db.execute(text("PRAGMA table_info(transactions)"))
        columns = [row[1] for row in result.fetchall()]
        logger.info(f"Transactions table columns: {columns}")
        
        # Count records
        result = db.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.fetchone()[0]
        logger.info(f"Total users: {user_count}")
        
        result = db.execute(text("SELECT COUNT(*) FROM admins"))
        admin_count = result.fetchone()[0]
        logger.info(f"Total admins: {admin_count}")
        
        result = db.execute(text("SELECT COUNT(*) FROM transactions"))
        transaction_count = result.fetchone()[0]
        logger.info(f"Total transactions: {transaction_count}")
        
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}", exc_info=True)
    finally:
        db.close()

if __name__ == "__main__":
    logger.info("Black Germ Database Migration Started")
    logger.info("=" * 50)
    
    migrate_database()
    verify_database()
    
    logger.info("\nMigration process completed!")
    logger.info("Next steps:")
    logger.info("1. Restart the server if it's running")
    logger.info("2. Run the test again: python3 test_admin.py")