#!/bin/bash
# Initialize PostgreSQL database

set -e

echo "Initializing Digital Nomads database..."

# Create database if not exists
PGPASSWORD=medical_password psql -h db -U medical_user -d medical_qa -c "SELECT 1" > /dev/null 2>&1 || {
  echo "Database not ready, waiting..."
  sleep 5
}

# Create extensions
PGPASSWORD=medical_password psql -h db -U medical_user -d medical_qa -c "CREATE EXTENSION IF NOT EXISTS uuid-ossp;"

echo "Database initialization complete"
