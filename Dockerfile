# Common Arguments
ARG IMAGE_VERSION
ARG GS_VERSION=2.25.2
ARG JAVA_HOME=/opt/java/openjdk

##############################################################################
# GeoServer Plugin Downloader Stage                                          #
##############################################################################
FROM python:3.12.5-slim-bullseye AS geoserver-plugin-downloader

# Install dependencies
RUN apt-get update && apt-get install -y curl python3-pip && pip install beautifulsoup4 requests && apt-get install -y figlet

WORKDIR /work
COPY build_data/ /work/
RUN /work/extensions.sh && /work/plugin_download.sh

##############################################################################
# GeoServer Production Stage                                                 #
##############################################################################
FROM tomcat:9.0.91-jdk11-temurin-focal AS geoserver-prod

# Install required packages for GeoServer
RUN apt-get update && apt-get install -y gdal-bin libgdal-java && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=${JAVA_HOME} \
    GEOSERVER_DATA_DIR=/opt/geoserver/data_dir

WORKDIR /scripts
COPY --from=geoserver-plugin-downloader /work/required_plugins/*.zip /required_plugins/
COPY build_data/setup.sh /scripts/setup.sh
RUN /scripts/setup.sh

# Expose GeoServer port
EXPOSE 8080

# Start GeoServer
ENTRYPOINT ["/bin/bash", "/scripts/entrypoint.sh"]

##############################################################################
# Django Application Setup Stage                                             #
##############################################################################
# Django Application Setup Stage
FROM python:3.12.5-slim-bullseye AS django-app

# Set work directory
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y figlet libpq-dev gcc gdal-bin postgresql-client && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /code/

# Expose port
EXPOSE 8000

# Start the Django application with Gunicorn
CMD ["gunicorn", "pacific_cruises.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "9", "--timeout", "120"]

##############################################################################
# Nginx for serving Django static/media files                                #
##############################################################################
FROM nginx:alpine AS nginx-app

# Set the working directory
WORKDIR /code
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Create static and media directories
RUN mkdir -p /code/staticfiles /code/media

# Expose HTTP and HTTPS ports
EXPOSE 80 443

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]

##############################################################################
# Entry point setup for Django                                               #
##############################################################################
FROM python:3.12.5-slim-bullseye AS pacific-cruises-celery

# Install figlet
RUN apt-get update && apt-get install -y figlet

# Create the code directory
WORKDIR /code/

# Copy the entrypoint script
COPY scripts/entrypoint.sh /code/
RUN chmod +x /code/entrypoint.sh
RUN sed -i 's/\r$//g' /code/entrypoint.sh

# Set the entrypoint command
ENTRYPOINT ["/code/entrypoint.sh"]