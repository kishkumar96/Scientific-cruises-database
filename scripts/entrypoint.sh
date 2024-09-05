#!/bin/bash
set -e

# Display startup banner
figlet -t "Kartoza Docker GeoServer & Django"

# Gosu preparations for GeoServer
USER_ID=${GEOSERVER_UID:-1000}
GROUP_ID=${GEOSERVER_GID:-1000}
USER_NAME=${USER:-geoserveruser}
GEO_GROUP_NAME=${GROUP_NAME:-geoserverusers}

# Add GeoServer group
if [ ! "$(getent group "${GEO_GROUP_NAME}")" ]; then
  groupadd -r "${GEO_GROUP_NAME}" -g "${GROUP_ID}"
fi

# Add GeoServer user to system
if ! id -u "${USER_NAME}" >/dev/null 2>&1; then
    useradd -l -m -d /home/"${USER_NAME}"/ -u "${USER_ID}" --gid "${GROUP_ID}" -s /bin/bash -G "${GEO_GROUP_NAME}" "${USER_NAME}"
fi

# Import GeoServer environment and functions
source /scripts/functions.sh
source /scripts/env-data.sh

# Create necessary directories for GeoServer
dir_creation=("${GEOSERVER_DATA_DIR}" "${CERT_DIR}" "${FOOTPRINTS_DATA_DIR}" "${FONTS_DIR}" "${GEOWEBCACHE_CACHE_DIR}"
"${GEOSERVER_HOME}" "${EXTRA_CONFIG_DIR}" "/docker-entrypoint-geoserver.d")
for directory in "${dir_creation[@]}"; do
  create_dir "${directory}"
done

# Rename context root for GeoServer if needed
if [ x"${GEOSERVER_CONTEXT_ROOT}" != xgeoserver ]; then
  echo "INFO: changing context-root to '${GEOSERVER_CONTEXT_ROOT}'."
  GEOSERVER_INSTALL_DIR="$(detect_install_dir)"
  if [ -e "${GEOSERVER_INSTALL_DIR}/webapps/geoserver" ]; then
    mkdir -p "$(dirname -- "${GEOSERVER_INSTALL_DIR}/webapps/${GEOSERVER_CONTEXT_ROOT}")"
    mv "${GEOSERVER_INSTALL_DIR}/webapps/geoserver" "${GEOSERVER_INSTALL_DIR}/webapps/${GEOSERVER_CONTEXT_ROOT}"
  else
    echo "WARN: '${GEOSERVER_INSTALL_DIR}/webapps/geoserver' not found, probably already renamed as this is probably a container restart and not first run."
  fi
fi

# Set GeoServer variables
set_vars
export  READONLY CLUSTER_DURABILITY BROKER_URL EMBEDDED_BROKER TOGGLE_MASTER TOGGLE_SLAVE BROKER_URL
export CLUSTER_CONFIG_DIR MONITOR_AUDIT_PATH INSTANCE_STRING  CLUSTER_CONNECTION_RETRY_COUNT CLUSTER_CONNECTION_MAX_WAIT

# Environment variable defaults and validation for PostgreSQL and Django
: "${POSTGRES_HOST:=localhost}"
: "${POSTGRES_PORT:=5432}"
: "${POSTGRES_USER:=postgres}"
: "${POSTGRES_DB:=cruise}"

if [ -z "$POSTGRES_PASSWORD" ]; then
    echo "ERROR: POSTGRES_PASSWORD is not set."
    exit 1
fi

echo "PostgreSQL Host: $POSTGRES_HOST"
echo "PostgreSQL Port: $POSTGRES_PORT"
echo "PostgreSQL User: $POSTGRES_USER"
echo "PostgreSQL Database: $POSTGRES_DB"

# Retry logic for PostgreSQL readiness check with improved error handling
MAX_RETRIES=300
RETRY_COUNT=0
SUCCESS=false

echo "Waiting for database and PostGIS extension to be ready..."
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT 1" 2>/dev/null && \
       psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "\dx" | grep -qw postgis; then
        SUCCESS=true
        break
    else
        echo "Database or PostGIS extension not ready yet. Retrying in 5 seconds... (Attempt $((RETRY_COUNT+1))/$MAX_RETRIES)"
        RETRY_COUNT=$((RETRY_COUNT+1))
        sleep 5
    fi
done

if [ "$SUCCESS" = false ]; then
    echo "ERROR: Timeout waiting for database and PostGIS extension."
    exit 1
fi

# Create PostGIS extension if it doesn't exist
echo "Creating PostGIS extension if not exists..."
if ! output=$(psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE EXTENSION IF NOT EXISTS postgis;" 2>&1); then
    echo "ERROR: Failed to create PostGIS extension: $output"
    exit 1
fi

# Run Django migrations
echo "Running Django migrations..."
if ! output=$(python manage.py migrate 2>&1); then
    echo "ERROR: Failed to run Django migrations: $output"
    exit 1
fi

# Prepare the JVM command line arguments for GeoServer
export GEOSERVER_OPTS="-Djava.awt.headless=true -server -Xms${INITIAL_MEMORY} -Xmx${MAXIMUM_MEMORY} \
       -XX:PerfDataSamplingInterval=500 -Dorg.geotools.referencing.forceXY=true \
       -XX:SoftRefLRUPolicyMSPerMB=36000   \
       -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:ParallelGCThreads=20 -XX:ConcGCThreads=5 \
       -XX:InitiatingHeapOccupancyPercent=${INITIAL_HEAP_OCCUPANCY_PERCENT}  \
       -Djts.overlay=ng \
       -Dfile.encoding=${ENCODING} \
       -Duser.timezone=${TIMEZONE} \
       -Duser.language=${LANGUAGE} \
       -Duser.region=${REGION} \
       -Duser.country=${COUNTRY} \
       -DENABLE_JSONP=${ENABLE_JSONP} \
       -DMAX_FILTER_RULES=${MAX_FILTER_RULES} \
       -DOPTIMIZE_LINE_WIDTH=${OPTIMIZE_LINE_WIDTH} \
       -DALLOW_ENV_PARAMETRIZATION=${PROXY_BASE_URL_PARAMETRIZATION} \
       -Djavax.servlet.request.encoding=${CHARACTER_ENCODING} \
       -Djavax.servlet.response.encoding=${CHARACTER_ENCODING} \
       -DCLUSTER_CONFIG_DIR=${CLUSTER_CONFIG_DIR} \
       -DGEOSERVER_DATA_DIR=${GEOSERVER_DATA_DIR} \
       -DGEOSERVER_FILEBROWSER_HIDEFS=${GEOSERVER_FILEBROWSER_HIDEFS} \
       -DGEOSERVER_AUDIT_PATH=${MONITOR_AUDIT_PATH} \
       -Dorg.geotools.shapefile.datetime=${USE_DATETIME_IN_SHAPEFILE} \
       -Dorg.geotools.localDateTimeHandling=true \
       -Dsun.java2d.renderer.useThreadLocal=false \
       -Dsun.java2d.renderer.pixelsize=8192 -server -XX:NewSize=300m \
       -Dlog4j.configuration=${CATALINA_HOME}/log4j.properties \
       --patch-module java.desktop=${CATALINA_HOME}/marlin-render.jar  \
       -Dsun.java2d.renderer=org.marlin.pisces.PiscesRenderingEngine \
       -Dgeoserver.login.autocomplete=${LOGIN_STATUS} \
       -DUPDATE_BUILT_IN_LOGGING_PROFILES=${UPDATE_LOGGING_PROFILES} \
       -DRELINQUISH_LOG4J_CONTROL=${RELINQUISH_LOG4J_CONTROL} \
       -DGEOSERVER_CONSOLE_DISABLED=${DISABLE_WEB_INTERFACE} \
       -DGWC_DISKQUOTA_DISABLED=${DISKQUOTA_DISABLED} \
       -DGEOSERVER_CSRF_WHITELIST=${CSRF_WHITELIST} \
       -Dgeoserver.xframe.shouldSetPolicy=${XFRAME_OPTIONS} \
       -DGEOSERVER_REQUIRE_FILE=${GEOSERVER_REQUIRE_FILE} \
       -DENTITY_RESOLUTION_ALLOWLIST='"${ENTITY_RESOLUTION_ALLOWLIST}"' \
       -DGEOSERVER_DISABLE_STATIC_WEB_FILES=${GEOSERVER_DISABLE_STATIC_WEB_FILES} \
       ${ADDITIONAL_JAVA_STARTUP_OPTIONS} "

# Prepare the JVM command line arguments for Django
export JAVA_OPTS="${JAVA_OPTS} ${GEOSERVER_OPTS}"

# Start the Django application using Gunicorn
echo "Starting Django application..."
exec gunicorn pacific_cruises.wsgi:application --bind 0.0.0.0:8000 &

# Start GeoServer
echo "Starting GeoServer..."
if [[ ${RUN_AS_ROOT} =~ [Ff][Aa][Ll][Ss][Ee] ]]; then
  if [[ -f ${GEOSERVER_HOME}/start.jar ]]; then
    exec gosu "${USER_NAME}" "${GEOSERVER_HOME}"/bin/startup.sh
  else
    exec gosu "${USER_NAME}" /usr/local/tomcat/bin/catalina.sh run
  fi
else
  if [[ -f ${GEOSERVER_HOME}/start.jar ]]; then
    exec "${GEOSERVER_HOME}"/bin/startup.sh
  else
    exec /usr/local/tomcat/bin/catalina.sh run
  fi
fi
