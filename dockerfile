# Use the official Python image from the Docker Hub
FROM python:3.11.5-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CPLUS_INCLUDE_PATH=/usr/include/gdal \
    C_INCLUDE_PATH=/usr/include/gdal

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    dos2unix \
    postgresql-client \
    netcat \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    curl \
    ca-certificates \
    gosu && \
    rm -rf /var/lib/apt/lists/* && ldconfig /usr/local/lib

# Set up a non-root user
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd -g $GROUP_ID appgroup && \
    useradd -m -u $USER_ID -g appgroup appuser

# Set working directory
WORKDIR /code

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . /code/

# Convert entrypoint to Unix format and ensure permissions
RUN dos2unix /code/entrypoint.sh && \
    chmod +x /code/entrypoint.sh && \
    chown -R appuser:appgroup /code

# Switch to the non-root user
USER appuser

# Run the entrypoint script
ENTRYPOINT ["/code/entrypoint.sh"]
