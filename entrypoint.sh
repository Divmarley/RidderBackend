#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Function to wait for a service
wait_for_service() {
  local host=$1
  local port=$2
  local name=$3
  echo "Waiting for $name at $host:$port..."
  while ! nc -z "$host" "$port"; do
    echo "  $name is unavailable - sleeping"
    sleep 2
  done
  echo "$name is up!"
}

# Wait for MySQL
wait_for_service "db" 3306 "MySQL"

# Wait for Redis
wait_for_service "redis" 6379 "Redis"

# Set Django settings module
export DJANGO_SETTINGS_MODULE=driverapp.settings

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Daphne server
echo "Starting Daphne server on 0.0.0.0:8000..."
exec daphne -b 0.0.0.0 -p 8000 driverapp.asgi:application
