# Use the official Python image from the Docker Hub
FROM python:3.11.5-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    dos2unix \
    postgresql-client \
    netcat \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Accept build arguments for UID and GID
ARG USER_ID=1000
ARG GROUP_ID=1000

# Create a non-root user with the same UID and GID as the host
RUN groupadd -g $GROUP_ID appgroup && \
    useradd -m -u $USER_ID -g appgroup appuser

# Set the working directory
WORKDIR /code

# Copy the requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code
COPY . /code/

# Convert entrypoint.sh to Unix format
RUN dos2unix /code/entrypoint.sh

# Ensure entrypoint.sh has executable permissions
RUN chmod +x /code/entrypoint.sh

# Change ownership of /code to appuser
RUN chown -R appuser:appgroup /code

# Switch to the non-root user
USER appuser

# Run entrypoint.sh
ENTRYPOINT ["/code/entrypoint.sh"]
