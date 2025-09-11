#!/bin/bash

# IZA OS Book Mobile Status Check

echo "📱 IZA OS Book Mobile Status"
echo "============================"

# Check Docker services
echo "🐳 Docker Services:"
docker-compose ps

echo ""
echo "🔍 Service Health Checks:"

# Check main API
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ Main API: Running"
else
    echo "❌ Main API: Not responding"
fi

# Check dashboard
if curl -s http://localhost:3000 >/dev/null; then
    echo "✅ Dashboard: Running"
else
    echo "❌ Dashboard: Not responding"
fi

# Check metrics
if curl -s http://localhost:9090 >/dev/null; then
    echo "✅ Metrics: Running"
else
    echo "❌ Metrics: Not responding"
fi

echo ""
echo "📱 Mobile Access URLs:"
MAC_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
echo "- Main API: http://$MAC_IP:8000"
echo "- Dashboard: http://$MAC_IP:3000"
echo "- Metrics: http://$MAC_IP:9090"
