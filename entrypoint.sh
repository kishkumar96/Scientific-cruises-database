#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
until pg_isready -h db -p 5432 -U $POSTGRES_USER; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Use Python to check Redis availability
echo "Checking Redis availability..."
python -c "
import sys
import redis
try:
    r = redis.StrictRedis(host='redis', port=6379)
    r.ping()
    print('Redis is ready!')
except redis.ConnectionError:
    print('Redis is unavailable - sleeping')
    sys.exit(1)
"

# Apply migrations and collect static files
echo "Applying database migrations..."
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the service
echo "Starting the service..."
exec "$@"
