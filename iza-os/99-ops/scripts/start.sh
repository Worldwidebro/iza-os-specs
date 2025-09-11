#!/bin/bash
# Start all services in the AI Orchestrator system

echo "🚀 Starting all system services..."

# Start docker-compose in detached mode
docker-compose up -d

echo "
✅ System services are starting in the background.
"

# Give services a moment to initialize
sleep 5

# Display status of running containers
echo "📊 Current container status:"
docker-compose ps
