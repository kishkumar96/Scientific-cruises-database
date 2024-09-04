# Generic stuff all Dockerfiles should start with so we get caching
ARG IMAGE_VERSION=9.0.91-jdk11-temurin-focal
ARG JAVA_HOME=/opt/java/openjdk

##############################################################################
# Plugin downloader stage                                                    #
##############################################################################
FROM --platform=$BUILDPLATFORM python:alpine3.20 AS geoserver-plugin-downloader
ARG GS_VERSION=2.25.2
ARG STABLE_PLUGIN_BASE_URL=https://sourceforge.net/projects/geoserver/files/GeoServer
ARG WAR_URL=https://downloads.sourceforge.net/project/geoserver/GeoServer/${GS_VERSION}/geoserver-${GS_VERSION}-war.zip

RUN apk update && apk add curl py3-pip
RUN pip3 install beautifulsoup4 requests

WORKDIR /work
ADD \
    build_data/community_plugins.py \
    build_data/stable_plugins.py \
    build_data/extensions.sh \
    build_data/required_plugins.txt \
    build_data/plugin_download.sh \
    /work/

RUN echo ${GS_VERSION} > /tmp/pass.txt && chmod 0755 /work/extensions.sh && /work/extensions.sh
RUN /work/plugin_download.sh

##############################################################################
# Production stage for GeoServer                                             #
##############################################################################
FROM tomcat:$IMAGE_VERSION AS geoserver-prod

LABEL maintainer="Tim Sutton<tim@linfiniti.com>"
ARG GS_VERSION=2.25.2
ARG STABLE_PLUGIN_BASE_URL=https://sourceforge.net/projects/geoserver/files/GeoServer
ARG HTTPS_PORT=8443
ARG ACTIVATE_GDAL_PLUGIN=true
ENV DEBIAN_FRONTEND=noninteractive

# Install extra fonts and other dependencies
RUN set -eux; \
    apt-get update; \
    apt-get -y --no-install-recommends install \
        locales gnupg2 ca-certificates software-properties-common iputils-ping \
        apt-transport-https fonts-cantarell fonts-liberation lmodern ttf-aenigma \
        ttf-bitstream-vera ttf-sjfonts tv-fonts libapr1-dev libssl-dev git \
        zip unzip curl xsltproc certbot cabextract gettext postgresql-client figlet gosu gdal-bin; \
    dpkg-divert --local --rename --add /sbin/initctl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*; \
    gosu nobody true

# Install GDAL if enabled
RUN if [ "${ACTIVATE_GDAL_PLUGIN}" = "true" ]; then \
    apt update -y && apt install -y gdal-bin libgdal-java; \
fi

ENV \
    JAVA_HOME=${JAVA_HOME} \
    GEOSERVER_DATA_DIR=/opt/geoserver/data_dir \
    GDAL_DATA=/usr/share/gdal \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/tomcat/native-jni-lib:/usr/lib/jni:/usr/local/apr/lib:/opt/libjpeg-turbo/lib64:/usr/lib:/usr/lib/x86_64-linux-gnu" \
    FOOTPRINTS_DATA_DIR=/opt/footprints_dir \
    GEOWEBCACHE_CACHE_DIR=/opt/geoserver/data_dir/gwc \
    CERT_DIR=/etc/certs \
    RANDFILE=/etc/certs/.rnd \
    FONTS_DIR=/opt/fonts \
    GEOSERVER_HOME=/geoserver \
    EXTRA_CONFIG_DIR=/settings \
    COMMUNITY_PLUGINS_DIR=/community_plugins  \
    STABLE_PLUGINS_DIR=/stable_plugins \
    REQUIRED_PLUGINS_DIR=/required_plugins

WORKDIR /scripts
ADD resources /tmp/resources
ADD build_data /build_data
ADD scripts /scripts

COPY --from=geoserver-plugin-downloader /work/required_plugins/*.zip ${REQUIRED_PLUGINS_DIR}/
COPY --from=geoserver-plugin-downloader /work/required_plugins.txt ${REQUIRED_PLUGINS_DIR}/
COPY --from=geoserver-plugin-downloader /work/stable_plugins/*.zip ${STABLE_PLUGINS_DIR}/
COPY --from=geoserver-plugin-downloader /work/community_plugins/*.zip ${COMMUNITY_PLUGINS_DIR}/
COPY --from=geoserver-plugin-downloader /work/geoserver_war/geoserver.* ${REQUIRED_PLUGINS_DIR}/
COPY --from=geoserver-plugin-downloader /work/community_plugins.txt ${COMMUNITY_PLUGINS_DIR}/
COPY --from=geoserver-plugin-downloader /work/stable_plugins.txt ${STABLE_PLUGINS_DIR}/

RUN echo ${GS_VERSION} > /scripts/geoserver_version.txt && echo ${STABLE_PLUGIN_BASE_URL} > /scripts/geoserver_gs_url.txt ;\
    chmod +x /scripts/*.sh;/scripts/setup.sh \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

EXPOSE ${HTTPS_PORT}

RUN echo 'figlet -t "Kartoza Docker GeoServer"' >> ~/.bashrc

WORKDIR ${GEOSERVER_HOME}

ENTRYPOINT ["/bin/bash", "/scripts/entrypoint.sh"]

##############################################################################
# Testing Stage for GeoServer                                                #
##############################################################################
FROM geoserver-prod AS geoserver-test

COPY ./scenario_tests/utils/requirements.txt /lib/utils/requirements.txt

RUN set -eux \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get update \
    && apt-get -y --no-install-recommends install python3-pip procps \
    && apt-get -y --purge autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install -r /lib/utils/requirements.txt;pip3 install numpy --upgrade

##############################################################################
# Django Application Setup                                                   #
##############################################################################
FROM python:3.12-slim

# Install system dependencies required for psycopg and PostGIS
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    binutils \
    libproj-dev \
    gdal-bin \
    postgresql-client \
    iputils-ping && \
    rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Django project files into the container
COPY . /app/

# Expose the port Django will run on
EXPOSE 8000

# Add health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:8000/ || exit 1

# Run the Django application with Gunicorn
CMD ["gunicorn", "pacific_cruises.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "9", "--timeout", "120"]

RUN python manage.py collectstatic --noinput
RUN apt-get update && apt-get install -y curl
