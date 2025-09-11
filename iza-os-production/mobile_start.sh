#!/bin/bash

# IZA OS Mobile Startup Script
# Optimized for Cursor mobile development

echo "📱 Starting IZA OS Mobile Development Environment..."

# Load mobile environment
if [ -f .env.mobile ]; then
    export $(cat .env.mobile | grep -v '^#' | xargs)
    echo "✅ Mobile environment loaded"
else
    echo "⚠️  Mobile environment not found, using default"
fi

# Start services with mobile-optimized settings
echo "🚀 Starting core services..."

# Start MCP server in background with mobile config
nohup python src/integrations/repository_mcp_server_fastapi.py > logs/mcp_mobile.log 2>&1 &
MCP_PID=$!
echo "✅ MCP Server started (PID: $MCP_PID)"

# Start agent orchestrator in background
nohup python src/core/agent_orchestrator.py > logs/orchestrator_mobile.log 2>&1 &
ORCHESTRATOR_PID=$!
echo "✅ Agent Orchestrator started (PID: $ORCHESTRATOR_PID)"

# Wait for services to start
sleep 3

# Test services
echo "🧪 Testing services..."
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ MCP Server responding"
else
    echo "⚠️  MCP Server not responding"
fi

if curl -s http://localhost:8001/health >/dev/null; then
    echo "✅ Agent Orchestrator responding"
else
    echo "⚠️  Agent Orchestrator not responding"
fi

echo ""
echo "🎉 IZA OS Mobile Environment Ready!"
echo ""
echo "Services:"
echo "- MCP Server: http://localhost:8000"
echo "- Agent Orchestrator: http://localhost:8001"
echo "- Mobile Dashboard: http://localhost:3000"
echo ""
echo "Quick Commands:"
echo "- Check status: ./mobile_status.sh"
echo "- Run orchestrator: ./mobile_orchestrator.sh"
echo "- Stop services: ./mobile_stop.sh"
echo ""
