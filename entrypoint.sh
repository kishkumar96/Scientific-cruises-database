#!/bin/bash
set -e

# PostgreSQL environment variable defaults and validation
: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_USER:=postgres}"
: "${POSTGRES_DB:=cruise}"

# Ensure POSTGRES_PASSWORD is set
if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "ERROR: POSTGRES_PASSWORD is not set."
    exit 1
fi

echo "PostgreSQL Host: $POSTGRES_HOST"
echo "PostgreSQL Port: $POSTGRES_PORT"
echo "PostgreSQL User: $POSTGRES_USER"
echo "PostgreSQL Database: $POSTGRES_DB"

# Check if PostgreSQL is ready using nc
echo "Waiting for PostgreSQL to start..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
    sleep 0.1
done
echo "PostgreSQL started."

# Retry logic for PostgreSQL readiness check with SQL validation
MAX_RETRIES=10
RETRY_COUNT=0
SUCCESS=false

echo "Checking PostgreSQL and PostGIS readiness..."
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1" 2>/dev/null && \
       psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "\dx" | grep -qw postgis; then
        SUCCESS=true
        break
    else
        echo "Database or PostGIS extension not ready yet. Retrying... (Attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
        RETRY_COUNT=$((RETRY_COUNT+1))
        sleep 5
    fi
done

if [ "$SUCCESS" = false ]; then
    echo "ERROR: Timeout waiting for database and PostGIS extension."
    exit 1
fi

# Create PostGIS extension if it doesn't exist
echo "Ensuring PostGIS extension exists..."
if ! psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE EXTENSION IF NOT EXISTS postgis;" 2>&1; then
    echo "ERROR: Failed to create PostGIS extension."
    exit 1
fi

# Run Django migrations
echo "Running Django migrations..."
if ! python manage.py migrate; then
    echo "ERROR: Failed to run Django migrations."
    exit 1
fi

# Collect static files
echo "Collecting static files..."
if ! python manage.py collectstatic --noinput; then
    echo "ERROR: Failed to collect static files."
    exit 1
fi

# (Optional) Create Django superuser
if [ -n "$SUPERUSER_EMAIL" ] && [ -n "$SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --email "$SUPERUSER_EMAIL" --username admin --noinput || true
fi

# Start the Django application using Gunicorn
echo "Starting Django application with Gunicorn..."
exec gunicorn pacific_cruises.wsgi:application --bind 0.0.0.0:8000


# GeoServer startup script (GeoServer and Tomcat configurations)

figlet -t "Kartoza Docker GeoServer"

# Gosu preparations
USER_ID=${GEOSERVER_UID:-1000}
GROUP_ID=${GEOSERVER_GID:-1000}
USER_NAME=${USER:-geoserveruser}
GEO_GROUP_NAME=${GROUP_NAME:-geoserverusers}

# Add group
if [ ! "$(getent group "${GEO_GROUP_NAME}")" ]; then
  groupadd -r "${GEO_GROUP_NAME}" -g "${GROUP_ID}"
fi

# Add user to system
if ! id -u "${USER_NAME}" >/dev/null 2>&1; then
    useradd -l -m -d /home/"${USER_NAME}"/ -u "${USER_ID}" --gid "${GROUP_ID}" -s /bin/bash -G "${GEO_GROUP_NAME}" "${USER_NAME}"
fi

# Import env and functions
source /scripts/functions.sh
source /scripts/env-data.sh

# Create necessary directories for GeoServer
dirs_to_create=("${GEOSERVER_DATA_DIR}" "${CERT_DIR}" "${FOOTPRINTS_DATA_DIR}" "${FONTS_DIR}" "${GEOWEBCACHE_CACHE_DIR}" "${GEOSERVER_HOME}" "${EXTRA_CONFIG_DIR}" "/docker-entrypoint-geoserver.d")
for dir in "${dirs_to_create[@]}"; do
  create_dir "${dir}"
done

# Rename context-root to match GeoServer setup
if [ x"${GEOSERVER_CONTEXT_ROOT}" != xgeoserver ]; then
  echo "INFO: changing context-root to '${GEOSERVER_CONTEXT_ROOT}'."
  GEOSERVER_INSTALL_DIR="$(detect_install_dir)"
  if [ -e "${GEOSERVER_INSTALL_DIR}/webapps/geoserver" ]; then
    mkdir -p "$(dirname -- "${GEOSERVER_INSTALL_DIR}/webapps/${GEOSERVER_CONTEXT_ROOT}")"
    mv "${GEOSERVER_INSTALL_DIR}/webapps/geoserver" "${GEOSERVER_INSTALL_DIR}/webapps/${GEOSERVER_CONTEXT_ROOT}"
  else
    echo "WARN: '${GEOSERVER_INSTALL_DIR}/webapps/geoserver' not found, possibly renamed already."
  fi
fi

# Prepare JVM arguments for GeoServer
export GEOSERVER_OPTS="-Djava.awt.headless=true -server -Xms${INITIAL_MEMORY} -Xmx${MAXIMUM_MEMORY} \
       -XX:PerfDataSamplingInterval=500 -Dorg.geotools.referencing.forceXY=true \
       -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:ParallelGCThreads=20 -XX:ConcGCThreads=5 \
       -Djts.overlay=ng -Dfile.encoding=${ENCODING} -Duser.timezone=${TIMEZONE} -Duser.language=${LANGUAGE} \
       -DCLUSTER_CONFIG_DIR=${CLUSTER_CONFIG_DIR} -DGEOSERVER_DATA_DIR=${GEOSERVER_DATA_DIR}"

# Start GeoServer
if [[ ${RUN_AS_ROOT} =~ [Ff][Aa][Ll][Ss][Ee] ]]; then
  exec gosu "${USER_NAME}" /usr/local/tomcat/bin/catalina.sh run
else
  exec /usr/local/tomcat/bin/catalina.sh run
fi
