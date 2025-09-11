#!/bin/bash
# Run comprehensive tests

echo " Running AI Orchestrator tests..."

# Test main orchestrator
echo "Testing orchestrator health..."
curl -f http://localhost:8000/health || echo "❌ Orchestrator health check failed"

# Test agents
echo "Testing agents..."
curl -f http://localhost:9001/health || echo "❌ Finance agent health check failed"
curl -f http://localhost:9002/health || echo "❌ Marketing agent health check failed"
curl -f http://localhost:9003/health || echo "❌ Operations agent health check failed"

# Test task execution
echo "Testing task execution..."
curl -X POST http://localhost:8000/execute \
  -H "Content-Type: application/json" \
  -d '{"content": "test task execution", "priority": 1}' || echo "❌ Task execution test failed"

echo "✅ Tests completed!"

