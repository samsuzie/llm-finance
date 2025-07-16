#!/usr/bin/env python3
"""
Database initialization script for Personal Finance Coach
"""
import asyncio
import sys
import os
from sqlalchemy import text

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

from app.core.database import engine, create_tables, SessionLocal
from app.models import User, Transaction, FinancialGoal


def init_database():
    """Initialize the database with tables and sample data"""
    print("🚀 Initializing Personal Finance Coach Database...")
    
    try:
        # Create all tables
        print("📋 Creating database tables...")
        create_tables()
        print("✅ Database tables created successfully!")
        
        # Test database connection
        print("🔍 Testing database connection...")
        with SessionLocal() as db:
            result = db.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
        
        print("🎉 Database initialization completed successfully!")
        print("\n📝 Next steps:")
        print("1. Start the backend server: python main.py")
        print("2. Start the frontend: cd frontend && npm start")
        print("3. Upload your transaction data through the web interface")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    init_database()