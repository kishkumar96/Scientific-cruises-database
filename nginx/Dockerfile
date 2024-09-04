# Use an official Nginx runtime as a parent image
FROM nginx:latest

# Set the working directory
WORKDIR /code

# Copy custom nginx config
COPY nginx.conf /etc/nginx/nginx.conf

# Create static and media directories if they don't exist
RUN mkdir -p /code/staticfiles /code/media

# Copy static and media files to the appropriate directory
COPY staticfiles /code/staticfiles
COPY media /code/media
