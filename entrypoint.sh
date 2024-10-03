#!/bin/bash
set -e

# Ensure gosu is available and appuser exists
if ! command -v gosu &> /dev/null; then
  echo "gosu could not be found"
  exit 1
fi

if ! id "appuser" &> /dev/null; then
  echo "User appuser does not exist"
  exit 1
fi

# Set default values if variables are not set
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
RABBITMQ_HOST=${RABBITMQ_HOST:-rabbitmq}
RABBITMQ_PORT=${RABBITMQ_PORT:-5672}
POSTGRES_USER=${POSTGRES_USER:-postgres}

# Wait for PostgreSQL to be ready
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER"; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Wait for RabbitMQ
echo "Waiting for RabbitMQ..."
while ! nc -z "$RABBITMQ_HOST" "$RABBITMQ_PORT"; do
  sleep 2
done
echo "RabbitMQ started"

# Adjust permissions
echo "Adjusting permissions..."
chown -R appuser:appuser /code/staticfiles /code/media

# Ensure staticfiles directory exists
mkdir -p /code/staticfiles

# Apply database migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start the server or worker
echo "Starting service"
exec gosu appuser "$@"
