#!/bin/bash

# Variables
DB_CONTAINER_NAME=$(docker-compose ps -q db)
DB_USER="postgres"
DB_NAME="cruise"
DB_PASSWORD="postgres123"
BACKUP_FILE="cruise_backup.dump"

# Drop the existing database and recreate it
docker exec -it $DB_CONTAINER_NAME bash -c "PGPASSWORD=$DB_PASSWORD dropdb -U $DB_USER $DB_NAME"
docker exec -it $DB_CONTAINER_NAME bash -c "PGPASSWORD=$DB_PASSWORD createdb -U $DB_USER $DB_NAME"

# Copy the backup file to the database container
docker cp $BACKUP_FILE $DB_CONTAINER_NAME:/tmp/$BACKUP_FILE

# Restore the database
docker exec -it $DB_CONTAINER_NAME bash -c "PGPASSWORD=$DB_PASSWORD pg_restore --clean --if-exists -U $DB_USER -d $DB_NAME -v /tmp/$BACKUP_FILE"