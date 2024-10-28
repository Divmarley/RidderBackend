#!/bin/bash

# Ensure the database is ready before running migrations
mysql_ready() {
python << END
import sys
import MySQLdb  # mysqlclient's module

try:
    conn = MySQLdb.connect(
        host="${MYSQL_HOST}",
        user="${MYSQL_USER}",
        passwd="${MYSQL_PASSWORD}",
        db="${MYSQL_DATABASE}",
        port=int("${DB_PORT}")
    )
    conn.close()
except MySQLdb.OperationalError as e:
    print(e)
    sys.exit(-1)
sys.exit(0)
END
}

# Wait until the MySQL database is available
until mysql_ready; do
  >&2 echo 'Waiting for MySQL to become available...'
  sleep 1
done

>&2 echo 'MySQL is available'

# Run Django commands
python manage.py migrate
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input

# Start Gunicorn server
exec daphne driverapp.wsgi:application --bind 0.0.0.0:8000