#!/usr/bin/env python3
"""
Database migration script to initialize or migrate schema for both SQLite and PostgreSQL
"""

import sys
import os
import logging
from sqlalchemy import text
from app.database import engine, SessionLocal
from app import models

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/migration.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_dialect(db):
    """Return database dialect name (sqlite or postgresql)"""
    return db.bind.dialect.name


def table_exists(db, table_name, dialect):
    """Check if a table exists depending on database dialect"""
    if dialect == "sqlite":
        query = text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    else:  # postgresql
        query = text(f"SELECT table_name FROM information_schema.tables WHERE table_name='{table_name}'")
    result = db.execute(query)
    return bool(result.fetchone())


def get_table_columns(db, table_name, dialect):
    """Get list of columns for a given table"""
    if dialect == "sqlite":
        result = db.execute(text(f"PRAGMA table_info({table_name})"))
        return [row[1] for row in result.fetchall()]
    else:  # postgresql
        result = db.execute(text(f"""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = '{table_name}'
        """))
        return [row[0] for row in result.fetchall()]


def migrate_database():
    """Perform the migration logic"""
    logger.info("Starting database migration...")
    db = SessionLocal()
    dialect = get_dialect(db)
    logger.info(f"Detected database dialect: {dialect}")

    try:
        # Ensure all tables are created
        if not table_exists(db, "users", dialect):
            logger.info("Users table not found, creating all tables...")
            models.Base.metadata.create_all(bind=engine)
            logger.info("All tables created successfully.")
        else:
            logger.info("Users table exists, verifying columns...")
            columns = get_table_columns(db, "users", dialect)
            logger.info(f"Existing columns: {columns}")

            # Add missing columns for both SQLite and PostgreSQL
            if "status" not in columns:
                logger.info("Adding 'status' column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR DEFAULT 'active'"))
                logger.info("'status' column added.")

            if "username" not in columns:
                logger.info("Adding 'username' column to users table...")
                db.execute(text("ALTER TABLE users ADD COLUMN username VARCHAR"))
                logger.info("'username' column added.")

                logger.info("Populating default usernames...")
                if dialect == "sqlite":
                    db.execute(text("UPDATE users SET username = 'user_' || id WHERE username IS NULL"))
                else:  # PostgreSQL string concatenation uses ||
                    db.execute(text("UPDATE users SET username = 'user_' || id WHERE username IS NULL"))
                logger.info("Usernames updated successfully.")

                logger.info("Creating unique index on username...")
                db.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON users(username)"))
                logger.info("Index created successfully.")
            else:
                logger.info("'username' column already exists.")

        # Create admin and transaction tables if missing
        for tbl in ["admins", "transactions"]:
            if not table_exists(db, tbl, dialect):
                logger.info(f"{tbl} table missing — creating it...")
                models.Base.metadata.create_all(bind=engine)
                logger.info(f"{tbl} table created successfully.")
            else:
                logger.info(f"{tbl} table already exists.")

        # Ensure user status values are set
        logger.info("Ensuring all users have active status...")
        db.execute(text("UPDATE users SET status = 'active' WHERE status IS NULL"))
        logger.info("Status normalization completed.")

        db.commit()
        logger.info("✅ Database migration completed successfully!")

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}", exc_info=True)
        db.rollback()
    finally:
        db.close()


def verify_database():
    """Verify schema and record counts"""
    logger.info("Verifying database structure...")
    db = SessionLocal()
    dialect = get_dialect(db)

    try:
        for tbl in ["users", "admins", "transactions"]:
            if table_exists(db, tbl, dialect):
                columns = get_table_columns(db, tbl, dialect)
                logger.info(f"{tbl} columns: {columns}")

                count = db.execute(text(f"SELECT COUNT(*) FROM {tbl}")).fetchone()[0]
                logger.info(f"Total records in {tbl}: {count}")
            else:
                logger.warning(f"{tbl} table not found!")

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
