#!/bin/bash

# IZA OS Book Mobile Startup Script

echo "📱 Starting IZA OS Book Mobile Environment..."

# Load mobile environment
if [ -f .env.mobile ]; then
    export $(cat .env.mobile | grep -v '^#' | xargs)
    echo "✅ Mobile environment loaded"
else
    echo "⚠️  Mobile environment not found, using default"
fi

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

echo "🚀 Starting IZA OS Book services..."

# Start services with mobile configuration
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 10

# Test services
echo "🧪 Testing services..."
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ Main API responding"
else
    echo "⚠️  Main API not responding yet"
fi

if curl -s http://localhost:3000 >/dev/null; then
    echo "✅ Dashboard responding"
else
    echo "⚠️  Dashboard not responding yet"
fi

echo ""
echo "🎉 IZA OS Book Mobile Environment Ready!"
echo ""
echo "📱 Access URLs for your phone:"
echo "- Main API: http://$MAC_IP:8000"
echo "- Dashboard: http://$MAC_IP:3000"
echo "- Metrics: http://$MAC_IP:9090"
echo "- Health Check: http://$MAC_IP:8000/health"
echo ""
echo "📋 Quick Commands:"
echo "- Check status: ./mobile_status_book.sh"
echo "- Stop services: ./mobile_stop_book.sh"
echo "- View logs: docker-compose logs -f"
echo ""
