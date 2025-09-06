#!/bin/bash

# Exit on any error
set -e

echo "Starting Secure Task Tracker application..."

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! pg_isready -h "${DATABASE_HOST:-db}" -p "${DATABASE_PORT:-5432}" -U "${DATABASE_USER:-postgres}" -d "${DATABASE_NAME:-secure_task_tracker_db}" > /dev/null 2>&1; do
    echo "Database is unavailable - sleeping"
    sleep 2
done

echo "Database is ready!"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

echo "Starting FastAPI application..."

# Start the FastAPI application with Uvicorn
if [ "$ENVIRONMENT" = "production" ]; then
    # Production settings
    uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --workers 4 \
        --log-config logging.conf
else
    # Development settings
    uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-level debug
fi