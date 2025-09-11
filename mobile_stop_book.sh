#!/bin/bash

# Stop IZA OS Book Mobile Services

echo "🛑 Stopping IZA OS Book Mobile Services..."

# Stop Docker services
docker-compose down

echo "✅ All IZA OS Book services stopped"
