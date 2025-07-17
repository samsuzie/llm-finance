#!/usr/bin/env python3
"""
Database setup script for Personal Finance Coach
This script helps you set up PostgreSQL database and run initial migrations
"""

import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'postgres',
    'password': 'password',
    'database': 'finance_coach_db'
}

def check_postgres_running():
    """Check if PostgreSQL is running"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'  # Connect to default postgres database
        )
        conn.close()
        print("✅ PostgreSQL is running")
        return True
    except psycopg2.OperationalError as e:
        print(f"❌ PostgreSQL is not running or connection failed: {e}")
        return False

def create_database():
    """Create the finance_coach_db database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server (not to our database)
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database='postgres'
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_CONFIG['database'],))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {DB_CONFIG['database']}")
            print(f"✅ Database '{DB_CONFIG['database']}' created successfully")
        else:
            print(f"✅ Database '{DB_CONFIG['database']}' already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Error creating database: {e}")
        return False

def test_database_connection():
    """Test connection to our application database"""
    try:
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        print(f"✅ Connected to database: {version}")
        cursor.close()
        conn.close()
        return True
    except psycopg2.Error as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def run_migrations():
    """Run Alembic migrations"""
    try:
        os.chdir('backend')
        
        # Initialize Alembic if not already done
        if not os.path.exists('alembic'):
            print("🔧 Initializing Alembic...")
            subprocess.run(['alembic', 'init', 'alembic'], check=True)
        
        # Run migrations
        print("🔧 Running database migrations...")
        result = subprocess.run(['alembic', 'upgrade', 'head'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database migrations completed successfully")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running migrations: {e}")
        return False
    except FileNotFoundError:
        print("❌ Alembic not found. Please install requirements first: pip install -r requirements.txt")
        return False
    finally:
        os.chdir('..')

def install_requirements():
    """Install Python requirements"""
    try:
        print("📦 Installing Python requirements...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'backend/requirements.txt'], 
                      check=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Personal Finance Coach Database")
    print("=" * 50)
    
    # Step 1: Install requirements
    if not install_requirements():
        sys.exit(1)
    
    # Step 2: Check if PostgreSQL is running
    if not check_postgres_running():
        print("\n📋 To start PostgreSQL:")
        print("   - On macOS with Homebrew: brew services start postgresql")
        print("   - On Ubuntu/Debian: sudo systemctl start postgresql")
        print("   - On Windows: Start PostgreSQL service from Services")
        print("   - With Docker: docker run -d --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres")
        sys.exit(1)
    
    # Step 3: Create database
    if not create_database():
        sys.exit(1)
    
    # Step 4: Test database connection
    if not test_database_connection():
        sys.exit(1)
    
    # Step 5: Run migrations
    if not run_migrations():
        sys.exit(1)
    
    print("\n🎉 Database setup completed successfully!")
    print("\n📋 Next steps:")
    print("   1. Update backend/.env with your actual API keys")
    print("   2. Start the backend server: cd backend && python main.py")
    print("   3. Start the frontend: cd frontend && npm start")

if __name__ == "__main__":
    main()