#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Wait for MySQL
echo "Waiting for MySQL..."
while ! nc -z db 3306; do
    sleep 1
done
echo "MySQL is up!"

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
    sleep 1
done
echo "Redis is up!"

export DJANGO_SETTINGS_MODULE=driverapp.settings

# Apply migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Daphne
echo "Starting Daphne server..."
exec daphne -b 0.0.0.0 -p 8000 driverapp.asgi:application
