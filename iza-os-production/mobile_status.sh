#!/bin/bash

# Mobile Status Check Script

echo "📱 IZA OS Mobile Status"
echo "======================"

# Check services
echo "🔍 Service Status:"
if curl -s http://localhost:8000/health >/dev/null; then
    echo "✅ MCP Server: Running"
else
    echo "❌ MCP Server: Not responding"
fi

if curl -s http://localhost:8001/health >/dev/null; then
    echo "✅ Agent Orchestrator: Running"
else
    echo "❌ Agent Orchestrator: Not responding"
fi

# Check processes
echo ""
echo "🔍 Process Status:"
MCP_PID=$(ps aux | grep "repository_mcp_server_fastapi" | grep -v grep | awk '{print $2}')
ORCHESTRATOR_PID=$(ps aux | grep "agent_orchestrator" | grep -v grep | awk '{print $2}')

if [ -n "$MCP_PID" ]; then
    echo "✅ MCP Server PID: $MCP_PID"
else
    echo "❌ MCP Server: Not running"
fi

if [ -n "$ORCHESTRATOR_PID" ]; then
    echo "✅ Agent Orchestrator PID: $ORCHESTRATOR_PID"
else
    echo "❌ Agent Orchestrator: Not running"
fi

# Check logs
echo ""
echo "📋 Recent Logs:"
echo "MCP Server (last 3 lines):"
tail -3 logs/mcp_mobile.log 2>/dev/null || echo "No logs found"

echo ""
echo "Agent Orchestrator (last 3 lines):"
tail -3 logs/orchestrator_mobile.log 2>/dev/null || echo "No logs found"
