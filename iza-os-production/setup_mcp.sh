#!/bin/bash
# Setup script for Repository MCP Server

set -e

echo "🚀 Setting up Repository MCP Server..."

# Create directories
mkdir -p repositories config logs

# Copy environment file
if [ ! -f .env ]; then
    cp env.mcp.example .env
    echo "📝 Created .env file - please edit with your credentials"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.mcp.txt

# Setup pre-commit hooks (optional)
echo "🔧 Setting up development tools..."
pip install pre-commit
pre-commit install

# Initialize Neo4j schema
echo "🗃️  Setting up Neo4j schema..."
python scripts/init_neo4j.py

# Start services
echo "🐳 Starting Docker services..."
docker-compose -f deploy/docker/docker-compose.mcp.yml up -d neo4j qdrant

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Test MCP server
echo "🧪 Testing MCP server..."
python -m pytest tests/ -v

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your API keys"
echo "2. Update mcp_config.yaml with your preferences"
echo "3. Run: python src/integrations/repository_mcp_server.py"
echo "4. Connect Cursor to MCP server at localhost:8000"
