#!/bin/bash

# Remove stopped containers
docker container prune -f

# Remove dangling images
docker image prune -f

# Remove unused images
docker image prune -af

# Remove unused networks
docker network prune -f

# Remove unused volumes
docker volume prune -f

# Remove build cache
docker builder prune -f
