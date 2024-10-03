FROM python:3.11.5-slim-bullseye
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-dev \
    default-libmysqlclient-dev \
    gcc \
    libpq-dev \
    musl-dev \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt-dev \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    netcat \
    netcat-openbsd \
    gdal-bin \
    postgresql-client \
    libgdal-dev && \
    rm -rf /var/lib/apt/lists/*

# Set GDAL environment variable
ENV GDAL_LIBRARY_PATH=/usr/lib/libgdal.so

# Install Python dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /code/

# Run collectstatic
RUN python /code/manage.py collectstatic --noinput

# Ensure the entrypoint script is executable
RUN chmod +x /code/entrypoint.sh
RUN sed -i 's/\r$//g' /code/entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/code/entrypoint.sh"]

# Define default command (optional)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
