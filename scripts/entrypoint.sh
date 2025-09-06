#!/bin/bash

# Exit on any error
set -e

echo "Starting Secure Task Tracker application..."

# Log environment variables for debugging
echo "Environment Variables:"
echo "ENVIRONMENT: ${ENVIRONMENT:-development}"
echo "DB_HOST: ${DB_HOST:-db}"
echo "DB_PORT: ${DB_PORT:-5432}"
echo "DB_USER: ${DB_USER:-postgres}"
echo "DB_NAME: ${DB_NAME:-secure_task_tracker_db}"
echo "DB_PASSWORD: ${DB_PASSWORD:-password}"

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-postgres}" -d "${DB_NAME:-secure_task_tracker_db}" > /dev/null 2>&1; do
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