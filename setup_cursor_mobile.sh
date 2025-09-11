#!/bin/bash

echo "📱 Setting up Cursor Mobile Access"
echo "==================================="

# Create mobile-optimized configuration
cat > .cursor-mobile.json << 'JSON'
{
  "mobile": {
    "enabled": true,
    "port": 3000,
    "host": "0.0.0.0",
    "ssl": false,
    "cors": true
  },
  "services": {
    "main_api": {
      "port": 8000,
      "path": "/api"
    },
    "agent_orchestrator": {
      "port": 8001,
      "path": "/agents"
    },
    "dashboard": {
      "port": 3000,
      "path": "/"
    }
  },
  "mobile_features": {
    "touch_optimized": true,
    "offline_support": true,
    "push_notifications": true,
    "voice_control": true
  }
}
JSON

echo "✅ Cursor mobile config created"

# Start services for mobile
echo "🚀 Starting services for mobile access..."
docker-compose up -d

echo "📱 Mobile access ready!"
echo "Use Cursor mobile app to connect to your Mac"
echo "Or use one of the tunnel solutions above"
