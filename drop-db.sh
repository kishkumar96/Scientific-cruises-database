#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f .env ]; then
  export $(cat .env | xargs)
fi

# Variables
DB_CONTAINER_NAME=$(docker-compose ps -q db)
DB_USER=${POSTGRES_USER:-postgres}
DB_PASSWORD=${POSTGRES_PASSWORD:-postgres123}
DB_NAME=${POSTGRES_DB:-cruise}

# Drop the existing database
docker exec -it $DB_CONTAINER_NAME bash -c "PGPASSWORD=$DB_PASSWORD dropdb -U $DB_USER $DB_NAME"