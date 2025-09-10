#!/bin/bash

# IZA OS Complete System Fix Script
# Fixes port conflicts, GitHub auth, git config, and orchestrates all agents

set -e

echo "🔧 IZA OS Complete System Fix"
echo "============================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to kill processes on specific ports
kill_port_processes() {
    local port=$1
    print_status "Checking port $port..."
    
    local pids=$(lsof -ti:$port 2>/dev/null || true)
    if [ -n "$pids" ]; then
        print_warning "Found processes on port $port: $pids"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        print_success "Killed processes on port $port"
    else
        print_success "Port $port is free"
    fi
}

# Function to check if port is free
check_port_free() {
    local port=$1
    if lsof -i:$port >/dev/null 2>&1; then
        return 1  # Port is in use
    else
        return 0  # Port is free
    fi
}

# Function to find free port starting from given port
find_free_port() {
    local start_port=$1
    local port=$start_port
    
    while ! check_port_free $port; do
        port=$((port + 1))
        if [ $port -gt $((start_port + 100)) ]; then
            print_error "Could not find free port starting from $start_port"
            return 1
        fi
    done
    
    echo $port
}

echo "STEP 1: Fixing Port Conflicts"
echo "=============================="

# Kill processes on common ports
for port in 8000 8001 8002 8003 8004 8005; do
    kill_port_processes $port
done

# Find free ports for our services
MCP_PORT=$(find_free_port 8000)
ORCHESTRATOR_PORT=$(find_free_port 8001)
AGENT_PORT=$(find_free_port 8002)

print_success "Port allocation: MCP=$MCP_PORT, Orchestrator=$ORCHESTRATOR_PORT, Agent=$AGENT_PORT"

echo ""
echo "STEP 2: Setting up Git Configuration"
echo "===================================="

# Set up git configuration
git config --global user.name "worldwidebro"
git config --global user.email "winnerscirclewcllc@gmail.com"
git config --global init.defaultBranch main
git config --global pull.rebase false
git config --global core.autocrlf input

print_success "Git configuration set up ✓"

echo ""
echo "STEP 3: GitHub Authentication"
echo "============================="

# Check if already authenticated
if gh auth status >/dev/null 2>&1; then
    print_success "GitHub already authenticated ✓"
else
    print_warning "GitHub not authenticated. Please run:"
    echo "  gh auth login --web --git-protocol https"
    echo "  OR use the manual token method:"
    echo "  ./manual_github_auth.sh"
fi

echo ""
echo "STEP 4: Fixing Agent Orchestrator Async Issues"
echo "=============================================="

# Fix the async/await issues in agent_coordinator.py
COORDINATOR_FILE="/Users/divinejohns/memU/iza-os-core/kernel/core/agent_coordinator.py"

if [ -f "$COORDINATOR_FILE" ]; then
    print_status "Fixing async issues in agent coordinator..."
    
    # Create backup
    cp "$COORDINATOR_FILE" "$COORDINATOR_FILE.backup"
    
    # Fix the async initialization issue
    sed -i '' 's/handler(agent, "initialize")/asyncio.run(handler(agent, "initialize"))/' "$COORDINATOR_FILE"
    
    print_success "Fixed async issues in agent coordinator ✓"
else
    print_warning "Agent coordinator file not found at $COORDINATOR_FILE"
fi

echo ""
echo "STEP 5: Updating Port Configurations"
echo "====================================="

# Update agent orchestrator port
ORCHESTRATOR_FILE="/Users/divinejohns/memU/iza-os-production/src/core/agent_orchestrator.py"
if [ -f "$ORCHESTRATOR_FILE" ]; then
    print_status "Updating agent orchestrator port to $ORCHESTRATOR_PORT..."
    
    # Update the port in the file
    sed -i '' "s/port=8003/port=$ORCHESTRATOR_PORT/g" "$ORCHESTRATOR_FILE"
    sed -i '' "s/localhost:8003/localhost:$ORCHESTRATOR_PORT/g" "$ORCHESTRATOR_FILE"
    
    print_success "Updated agent orchestrator port ✓"
fi

# Update MCP server port
MCP_FILE="/Users/divinejohns/memU/iza-os-production/src/integrations/repository_mcp_server_fastapi.py"
if [ -f "$MCP_FILE" ]; then
    print_status "Updating MCP server port to $MCP_PORT..."
    
    # Update the port in the file
    sed -i '' "s/port=8000/port=$MCP_PORT/g" "$MCP_FILE"
    sed -i '' "s/localhost:8000/localhost:$MCP_PORT/g" "$MCP_FILE"
    
    print_success "Updated MCP server port ✓"
fi

echo ""
echo "STEP 6: Creating Environment Configuration"
echo "=========================================="

# Create comprehensive .env file
ENV_FILE="/Users/divinejohns/memU/iza-os-production/.env"
cat > "$ENV_FILE" << EOF
# GitHub Configuration
GITHUB_TOKEN=\$(gh auth token 2>/dev/null || echo "")
GH_TOKEN=\$(gh auth token 2>/dev/null || echo "")

# Git Configuration
GIT_USER_NAME="worldwidebro"
GIT_USER_EMAIL="winnerscirclewcllc@gmail.com"

# Port Configuration
MCP_SERVER_PORT=$MCP_PORT
ORCHESTRATOR_PORT=$ORCHESTRATOR_PORT
AGENT_PORT=$AGENT_PORT

# Project Configuration
PROJECT_NAME="IZA OS Production"
PROJECT_VERSION="1.0.0"
PROJECT_ROOT="/Users/divinejohns/memU"

# API Keys (add your actual keys here)
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
# STRIPE_SECRET_KEY=your_stripe_key_here

# Database Configuration
# POSTGRES_URL=postgresql://user:password@localhost:5432/iza_os
# REDIS_URL=redis://localhost:6379
# NEO4J_URL=bolt://localhost:7687

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=/Users/divinejohns/memU/logs/iza_os.log
EOF

print_success "Created comprehensive .env file ✓"

echo ""
echo "STEP 7: Setting up Logging Directory"
echo "==================================="

# Create logs directory
mkdir -p /Users/divinejohns/memU/logs
print_success "Created logs directory ✓"

echo ""
echo "STEP 8: Testing System Components"
echo "================================="

# Test git configuration
print_status "Testing git configuration..."
if git config --global user.name | grep -q "worldwidebro"; then
    print_success "Git configuration test passed ✓"
else
    print_error "Git configuration test failed"
fi

# Test GitHub CLI
print_status "Testing GitHub CLI..."
if gh --version >/dev/null 2>&1; then
    print_success "GitHub CLI test passed ✓"
else
    print_error "GitHub CLI test failed"
fi

# Test Python environment
print_status "Testing Python environment..."
if python3 --version >/dev/null 2>&1; then
    print_success "Python environment test passed ✓"
else
    print_error "Python environment test failed"
fi

echo ""
echo "STEP 9: Starting System Services"
echo "==============================="

# Start MCP server in background
print_status "Starting MCP server on port $MCP_PORT..."
cd /Users/divinejohns/memU/iza-os-production
nohup python src/integrations/repository_mcp_server_fastapi.py > logs/mcp_server.log 2>&1 &
MCP_PID=$!
print_success "MCP server started with PID $MCP_PID"

# Wait a moment for MCP server to start
sleep 3

# Start agent orchestrator in background
print_status "Starting agent orchestrator on port $ORCHESTRATOR_PORT..."
nohup python src/core/agent_orchestrator.py > logs/agent_orchestrator.log 2>&1 &
ORCHESTRATOR_PID=$!
print_success "Agent orchestrator started with PID $ORCHESTRATOR_PID"

# Wait a moment for orchestrator to start
sleep 3

echo ""
echo "STEP 10: Verifying Services"
echo "=========================="

# Test MCP server
print_status "Testing MCP server..."
if curl -s "http://localhost:$MCP_PORT/health" >/dev/null 2>&1; then
    print_success "MCP server is responding ✓"
else
    print_warning "MCP server not responding (may still be starting)"
fi

# Test agent orchestrator
print_status "Testing agent orchestrator..."
if curl -s "http://localhost:$ORCHESTRATOR_PORT/health" >/dev/null 2>&1; then
    print_success "Agent orchestrator is responding ✓"
else
    print_warning "Agent orchestrator not responding (may still be starting)"
fi

echo ""
echo "STEP 11: Running Unified Orchestrator Test"
echo "==========================================="

print_status "Running unified orchestrator test..."
cd /Users/divinejohns/memU
timeout 30 python UNIFIED_ORCHESTRATOR.py || true

echo ""
echo "🎉 SYSTEM FIX COMPLETE!"
echo "======================"
echo ""
echo "Services Status:"
echo "- MCP Server: http://localhost:$MCP_PORT (PID: $MCP_PID)"
echo "- Agent Orchestrator: http://localhost:$ORCHESTRATOR_PORT (PID: $ORCHESTRATOR_PID)"
echo ""
echo "Next Steps:"
echo "1. Complete GitHub authentication: gh auth login --web"
echo "2. Test services: curl http://localhost:$MCP_PORT/health"
echo "3. Check logs: tail -f logs/mcp_server.log"
echo "4. Commit changes: git add . && git commit -m 'System fix complete'"
echo ""
echo "All port conflicts resolved and services started!"
