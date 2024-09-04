#!/bin/bash
set -e

echo "Starting PostgreSQL service..."
# Start the PostgreSQL service
pg_ctlcluster 16 main start

echo "Waiting for PostgreSQL to be available..."
# Wait for the PostgreSQL service to be available
until pg_isready -U postgres -d cruise; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "Restoring the database from the dump file..."
# Restore the database from the dump file
if pg_restore -U postgres -d cruise /docker-entrypoint-initdb.d/cruise_backup.dump; then
  echo "Database restored successfully."
else
  echo "Database restoration failed." >&2
  exit 1
fi

echo "Stopping PostgreSQL service..."
# Stop the PostgreSQL service after the restoration
pg_ctlcluster 16 main stop

echo "PostgreSQL service stopped."
