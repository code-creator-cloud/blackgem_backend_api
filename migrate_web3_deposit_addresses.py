#!/usr/bin/env python3
"""
Migration script to add Web3DepositAddress table and update Transaction table
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.database import SQLALCHEMY_DATABASE_URL
from app.models import Base

def migrate_web3_deposit_addresses():
    """Add Web3DepositAddress table and update Transaction table"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if web3_deposit_addresses table exists
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='web3_deposit_addresses'
        """))
        
        if not result.fetchone():
            print("Creating web3_deposit_addresses table...")
            conn.execute(text("""
                CREATE TABLE web3_deposit_addresses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    address VARCHAR NOT NULL UNIQUE,
                    network VARCHAR NOT NULL,
                    amount FLOAT NOT NULL,
                    status VARCHAR DEFAULT 'pending',
                    expires_at DATETIME NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    completed_at DATETIME,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """))
            print("✅ web3_deposit_addresses table created")
        else:
            print("✅ web3_deposit_addresses table already exists")
        
        # Check if network column exists in transactions table
        result = conn.execute(text("""
            PRAGMA table_info(transactions)
        """))
        columns = [row[1] for row in result.fetchall()]
        
        if 'network' not in columns:
            print("Adding network column to transactions table...")
            conn.execute(text("ALTER TABLE transactions ADD COLUMN network VARCHAR"))
            print("✅ network column added to transactions table")
        else:
            print("✅ network column already exists in transactions table")
        
        if 'deposit_address_id' not in columns:
            print("Adding deposit_address_id column to transactions table...")
            conn.execute(text("ALTER TABLE transactions ADD COLUMN deposit_address_id INTEGER"))
            print("✅ deposit_address_id column added to transactions table")
        else:
            print("✅ deposit_address_id column already exists in transactions table")
        
        # Create index on address for faster lookups
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_web3_deposit_addresses_address'
        """))
        
        if not result.fetchone():
            print("Creating index on web3_deposit_addresses.address...")
            conn.execute(text("""
                CREATE INDEX idx_web3_deposit_addresses_address 
                ON web3_deposit_addresses (address)
            """))
            print("✅ Index created on web3_deposit_addresses.address")
        else:
            print("✅ Index already exists on web3_deposit_addresses.address")
        
        # Create index on expires_at for faster expiration checks
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name='idx_web3_deposit_addresses_expires'
        """))
        
        if not result.fetchone():
            print("Creating index on web3_deposit_addresses.expires_at...")
            conn.execute(text("""
                CREATE INDEX idx_web3_deposit_addresses_expires 
                ON web3_deposit_addresses (expires_at)
            """))
            print("✅ Index created on web3_deposit_addresses.expires_at")
        else:
            print("✅ Index already exists on web3_deposit_addresses.expires_at")
        
        conn.commit()
        print("🎉 Web3 deposit addresses migration completed successfully!")

if __name__ == "__main__":
    migrate_web3_deposit_addresses() 