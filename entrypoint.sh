#!/bin/bash

# Wait for database
echo "Waiting for MySQL..."
while ! nc -z db 3306; do
    sleep 1
done

# Wait for Redis
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
    sleep 1
done

export DJANGO_SETTINGS_MODULE=driverapp.settings

# Apply migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start Daphne
exec daphne -b 0.0.0.0 -p 8000 driverapp.asgi:application