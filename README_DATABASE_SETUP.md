# Database Setup Guide

This guide will help you set up PostgreSQL database for the Personal Finance Coach application.

## Prerequisites

1. **PostgreSQL Installation**
   - **macOS**: `brew install postgresql`
   - **Ubuntu/Debian**: `sudo apt-get install postgresql postgresql-contrib`
   - **Windows**: Download from [PostgreSQL official website](https://www.postgresql.org/download/windows/)
   - **Docker**: `docker run -d --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 postgres`

2. **Python Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

## Quick Setup (Automated)

Run the automated setup script:

```bash
python setup_database.py
```

This script will:
- Install Python requirements
- Check PostgreSQL connection
- Create the database
- Run migrations
- Verify setup

## Manual Setup

### 1. Start PostgreSQL

**macOS (Homebrew):**
```bash
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**Docker:**
```bash
docker run -d \
  --name postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=finance_coach_db \
  -p 5432:5432 \
  postgres:15
```

### 2. Create Database

Connect to PostgreSQL and create the database:

```bash
psql -U postgres -h localhost
```

```sql
CREATE DATABASE finance_coach_db;
\q
```

### 3. Configure Environment

Update `backend/.env` with your database credentials:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/finance_coach_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=finance_coach_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 4. Run Migrations

```bash
cd backend
alembic upgrade head
```

### 5. Verify Setup

Test the database connection:

```bash
python -c "
from app.core.database import test_database_connection
print('Database connection:', test_database_connection())
"
```

## Database Schema

The application creates the following tables:

- **users**: User accounts and profiles
- **transactions**: Financial transactions
- **financial_goals**: User financial goals
- **chat_history**: AI chat conversations

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure PostgreSQL is running
   - Check if port 5432 is available
   - Verify credentials in `.env` file

2. **Database Does Not Exist**
   - Create database manually: `CREATE DATABASE finance_coach_db;`
   - Run the setup script again

3. **Permission Denied**
   - Check PostgreSQL user permissions
   - Ensure user has CREATE DATABASE privileges

4. **Migration Errors**
   - Drop and recreate database if needed
   - Check Alembic configuration in `alembic.ini`

### Reset Database

To completely reset the database:

```bash
# Drop database
psql -U postgres -c "DROP DATABASE IF EXISTS finance_coach_db;"

# Recreate database
psql -U postgres -c "CREATE DATABASE finance_coach_db;"

# Run migrations
cd backend
alembic upgrade head
```

## Production Considerations

1. **Security**
   - Use strong passwords
   - Enable SSL connections
   - Restrict database access

2. **Performance**
   - Configure connection pooling
   - Set up proper indexes
   - Monitor query performance

3. **Backup**
   - Set up regular database backups
   - Test backup restoration procedures

## Docker Compose Setup

For development with Docker:

```bash
docker-compose up postgres redis
```

This will start PostgreSQL and Redis containers with the correct configuration.