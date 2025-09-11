#!/bin/bash

# IZA OS Bootstrap Script
echo "🚀 IZA OS Bootstrap"
echo "=================="

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required"
    exit 1
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install IZA OS core
echo "🔧 Installing IZA OS core..."
pip install -e 40-mcp-agents/mcp-servers/llm-core/

# Clone external repositories
echo "📥 Cloning external repositories..."
python 99-ops/scripts/clone_from_registry.py

# Setup mobile access
echo "📱 Setting up mobile access..."
./99-ops/scripts/setup_mobile_access.sh

echo "✅ IZA OS bootstrap complete!"
echo ""
echo "🎯 Next steps:"
echo "1. make start-orchestrator"
echo "2. make start-dashboard"
echo "3. make mobile-access"
echo ""
echo "📱 Mobile access: http://YOUR_IP:3000"
