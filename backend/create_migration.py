#!/usr/bin/env python3
"""
Create initial migration for the database
"""
import subprocess
import sys
import os

def create_initial_migration():
    """Create the initial migration file"""
    print("🔄 Creating initial database migration...")
    
    try:
        # Initialize alembic (if not already done)
        print("📋 Initializing Alembic...")
        result = subprocess.run(
            ["alembic", "init", "alembic"], 
            capture_output=True, 
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode != 0 and "already exists" not in result.stderr:
            print(f"Warning: {result.stderr}")
        
        # Create initial migration
        print("📝 Creating initial migration...")
        result = subprocess.run(
            ["alembic", "revision", "--autogenerate", "-m", "Initial migration"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        if result.returncode == 0:
            print("✅ Initial migration created successfully!")
            print("📄 Migration file created in alembic/versions/")
            print("\n🚀 To apply the migration, run:")
            print("   alembic upgrade head")
        else:
            print(f"❌ Failed to create migration: {result.stderr}")
            sys.exit(1)
            
    except FileNotFoundError:
        print("❌ Alembic not found. Please install it with: pip install alembic")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error creating migration: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    create_initial_migration()