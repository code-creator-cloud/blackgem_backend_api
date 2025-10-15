#!/usr/bin/env python3
"""
Database connection test script for PostgreSQL migration
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test PostgreSQL database connection"""
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/black_germ_db")
        
        print(f"Testing connection to: {database_url}")
        
        # Create engine
        engine = create_engine(database_url)
        
        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Successfully connected to PostgreSQL!")
            print(f"PostgreSQL version: {version}")
            
            # Test if database exists
            result = connection.execute(text("SELECT current_database();"))
            db_name = result.fetchone()[0]
            print(f"Connected to database: {db_name}")
            
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ Database connection failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        # Get database URL and extract components
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/black_germ_db")
        
        # Parse URL to get database name
        if "postgresql://" in database_url:
            # Extract database name from URL
            db_name = database_url.split("/")[-1]
            base_url = database_url.rsplit("/", 1)[0] + "/postgres"
            
            print(f"Creating database '{db_name}' if it doesn't exist...")
            
            # Connect to default postgres database to create our database
            engine = create_engine(base_url)
            
            with engine.connect() as connection:
                # Check if database exists
                result = connection.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';"))
                if result.fetchone() is None:
                    # Create database
                    connection.execute(text(f"CREATE DATABASE {db_name};"))
                    connection.commit()
                    print(f"✅ Database '{db_name}' created successfully!")
                else:
                    print(f"✅ Database '{db_name}' already exists!")
            
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ Database creation failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 PostgreSQL Database Setup Test")
    print("=" * 50)
    
    # Test if PostgreSQL is running
    print("1. Testing PostgreSQL connection...")
    if test_database_connection():
        print("\n✅ PostgreSQL is running and accessible!")
    else:
        print("\n❌ PostgreSQL connection failed!")
        print("\n📋 Setup Instructions:")
        print("1. Install PostgreSQL:")
        print("   sudo apt update")
        print("   sudo apt install postgresql postgresql-contrib")
        print("\n2. Start PostgreSQL service:")
        print("   sudo systemctl start postgresql")
        print("   sudo systemctl enable postgresql")
        print("\n3. Create a database user:")
        print("   sudo -u postgres psql")
        print("   CREATE USER your_username WITH PASSWORD 'your_password';")
        print("   ALTER USER your_username CREATEDB;")
        print("   \\q")
        print("\n4. Create the database:")
        print("   sudo -u postgres createdb black_germ_db")
        print("\n5. Update your .env file with the correct DATABASE_URL:")
        print("   DATABASE_URL=postgresql://your_username:your_password@localhost:5432/black_germ_db")
        print("\n6. Install Python dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Run your FastAPI application: python -m app.main")
    print("2. The database tables will be created automatically")
