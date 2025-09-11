#!/bin/bash
# Check the health and status of all system services

echo "📊 Checking system status..."

# Show the status of the docker containers
docker-compose ps

# You can add more checks here, e.g., curl to health endpoints
# curl -s http://localhost:8000/system/health
