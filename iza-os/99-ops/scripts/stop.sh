#!/bin/bash
# Stop all services in the AI Orchestrator system

echo "🛑 Stopping all system services..."

# Stop and remove docker-compose containers, networks, and volumes
docker-compose down

echo "
✅ System has been shut down.
"