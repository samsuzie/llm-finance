#!/bin/bash

# Setup script for PostgreSQL database
# This script helps you set up PostgreSQL for the Personal Finance Coach app

set -e

echo "🚀 Setting up PostgreSQL for Personal Finance Coach"
echo "=================================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if PostgreSQL is running
check_postgres() {
    if command_exists psql; then
        if psql -h localhost -U postgres -d postgres -c "SELECT 1;" >/dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# Check if Docker is available
if command_exists docker; then
    echo "✅ Docker found"
    
    # Check if postgres container is already running
    if docker ps | grep -q "finance-postgres"; then
        echo "✅ PostgreSQL container is already running"
    else
        echo "🔧 Starting PostgreSQL with Docker Compose..."
        docker-compose up -d postgres
        
        # Wait for PostgreSQL to be ready
        echo "⏳ Waiting for PostgreSQL to be ready..."
        sleep 10
        
        # Check if it's running
        if docker ps | grep -q "finance-postgres"; then
            echo "✅ PostgreSQL container started successfully"
        else
            echo "❌ Failed to start PostgreSQL container"
            exit 1
        fi
    fi
    
elif check_postgres; then
    echo "✅ PostgreSQL is already running locally"
    
else
    echo "❌ PostgreSQL not found and Docker not available"
    echo ""
    echo "Please install PostgreSQL using one of these methods:"
    echo ""
    echo "🐳 Docker (Recommended):"
    echo "   Install Docker and run: docker-compose up -d postgres"
    echo ""
    echo "🍺 macOS (Homebrew):"
    echo "   brew install postgresql"
    echo "   brew services start postgresql"
    echo ""
    echo "🐧 Ubuntu/Debian:"
    echo "   sudo apt install postgresql postgresql-contrib"
    echo "   sudo systemctl start postgresql"
    echo ""
    echo "🪟 Windows:"
    echo "   Download from: https://www.postgresql.org/download/windows/"
    echo ""
    exit 1
fi

# Test database connection
echo "🔍 Testing database connection..."
if command_exists docker && docker ps | grep -q "finance-postgres"; then
    # Test with Docker
    if docker exec finance-postgres psql -U postgres -d finance_coach_db -c "SELECT 1;" >/dev/null 2>&1; then
        echo "✅ Database connection successful"
    else
        echo "❌ Database connection failed"
        echo "Creating database..."
        docker exec finance-postgres psql -U postgres -c "CREATE DATABASE finance_coach_db;" 2>/dev/null || true
    fi
else
    # Test with local PostgreSQL
    if psql -h localhost -U postgres -d finance_coach_db -c "SELECT 1;" >/dev/null 2>&1; then
        echo "✅ Database connection successful"
    else
        echo "❌ Database connection failed"
        echo "Creating database..."
        createdb -h localhost -U postgres finance_coach_db 2>/dev/null || true
    fi
fi

echo ""
echo "🎉 PostgreSQL setup completed!"
echo ""
echo "📋 Database Details:"
echo "   Host: localhost"
echo "   Port: 5432"
echo "   Database: finance_coach_db"
echo "   Username: postgres"
echo "   Password: password"
echo ""
echo "🔧 Next steps:"
echo "   1. cd backend"
echo "   2. pip install -r requirements.txt"
echo "   3. alembic upgrade head"
echo "   4. python main.py"