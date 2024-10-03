#!/bin/sh

set -e
# Set default values if variables are not set
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
RABBITMQ_HOST=${RABBITMQ_HOST:-rabbitmq}
RABBITMQ_PORT=${RABBITMQ_PORT:-5672}
# Wait for PostgreSQL
echo "Waiting for postgres..."

while ! nc -z $DB_HOST $DB_PORT; do
  sleep 1
done

echo "postgres started"

# Wait for RabbitMQ
echo "Waiting for RabbitMQ..."
while ! nc -z rabbitmq 5672; do
  sleep 1
done
echo "RabbitMQ started"

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations"
python manage.py migrate

# Start server
echo "Starting server"
exec "$@"
