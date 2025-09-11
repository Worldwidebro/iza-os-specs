#!/bin/bash

# Stop Mobile Services

echo "🛑 Stopping IZA OS Mobile Services..."

# Kill MCP server
MCP_PID=$(ps aux | grep "repository_mcp_server_fastapi" | grep -v grep | awk '{print $2}')
if [ -n "$MCP_PID" ]; then
    kill $MCP_PID
    echo "✅ MCP Server stopped (PID: $MCP_PID)"
else
    echo "ℹ️  MCP Server not running"
fi

# Kill agent orchestrator
ORCHESTRATOR_PID=$(ps aux | grep "agent_orchestrator" | grep -v grep | awk '{print $2}')
if [ -n "$ORCHESTRATOR_PID" ]; then
    kill $ORCHESTRATOR_PID
    echo "✅ Agent Orchestrator stopped (PID: $ORCHESTRATOR_PID)"
else
    echo "ℹ️  Agent Orchestrator not running"
fi

echo "✅ All mobile services stopped"
