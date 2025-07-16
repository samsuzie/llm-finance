#!/bin/bash

echo "🚀 Setting up Personal Finance Coach Database..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start PostgreSQL and Redis with Docker Compose
echo "🐳 Starting PostgreSQL and Redis containers..."
docker-compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check if PostgreSQL is ready
until docker-compose exec postgres pg_isready -U postgres; do
    echo "⏳ PostgreSQL is still starting up..."
    sleep 2
done

echo "✅ PostgreSQL is ready!"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

# Initialize database
echo "🗄️ Initializing database..."
python init_db.py

# Create and run migrations
echo "🔄 Setting up database migrations..."
python create_migration.py
alembic upgrade head

echo "🎉 Database setup completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Start the backend: cd backend && python main.py"
echo "2. Start the frontend: cd frontend && npm install && npm start"
echo "3. Visit http://localhost:3000 to use the application"