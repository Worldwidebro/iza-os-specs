#!/bin/bash
# 🚀 IZA OS: Unified Startup Script
# Complete system startup with dependency checking and health monitoring

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# IZA OS configuration
IZA_OS_ROOT="/Users/divinejohns/memU/IZA_OS"
AGENTS_DIR="$IZA_OS_ROOT/02_AGENT_ORCHESTRATION/workers"
MCP_SERVERS_DIR="$IZA_OS_ROOT/mcp_servers"
LOGS_DIR="$IZA_OS_ROOT/logs"
OPENLOVABLE_DIR="$IZA_OS_ROOT/open-lovable"

# Create logs directory if it doesn't exist
mkdir -p "$LOGS_DIR"

echo -e "${CYAN}🚀 IZA OS: The Most Advanced Autonomous Business System${NC}"
echo -e "${BLUE}=====================================================${NC}"
echo ""

# Function to print status messages
print_status() {
    local status=$1
    local message=$2
    case $status in
        "info")
            echo -e "${BLUE}ℹ️  $message${NC}"
            ;;
        "success")
            echo -e "${GREEN}✅ $message${NC}"
            ;;
        "warning")
            echo -e "${YELLOW}⚠️  $message${NC}"
            ;;
        "error")
            echo -e "${RED}❌ $message${NC}"
            ;;
        "step")
            echo -e "${PURPLE}📋 $message${NC}"
            ;;
    esac
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is available
port_available() {
    local port=$1
    ! lsof -i :$port >/dev/null 2>&1
}

# Function to wait for a service to be ready
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    print_status "info" "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s "$url/health" >/dev/null 2>&1; then
            print_status "success" "$service_name is ready!"
            return 0
        fi
        
        print_status "info" "Attempt $attempt/$max_attempts - $service_name not ready yet..."
        sleep 2
        ((attempt++))
    done
    
    print_status "error" "$service_name failed to start after $max_attempts attempts"
    return 1
}

# Phase 1: Dependency Checking
echo -e "${CYAN}📦 Phase 1: Checking Dependencies${NC}"
echo "=================================="

# Check Python
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    print_status "success" "Python 3 found: $PYTHON_VERSION"
else
    print_status "error" "Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check Node.js
if command_exists node; then
    NODE_VERSION=$(node --version)
    print_status "success" "Node.js found: $NODE_VERSION"
else
    print_status "error" "Node.js not found. Please install Node.js 16+"
    exit 1
fi

# Check Docker
if command_exists docker; then
    DOCKER_VERSION=$(docker --version)
    print_status "success" "Docker found: $DOCKER_VERSION"
else
    print_status "warning" "Docker not found. Some services may not start"
fi

# Check required Python packages
print_status "info" "Checking Python packages..."
REQUIRED_PACKAGES=("asyncio" "requests" "uvicorn" "fastapi")
for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        print_status "success" "Python package '$package' found"
    else
        print_status "warning" "Python package '$package' not found"
    fi
done

echo ""

# Phase 2: Port Availability Check
echo -e "${CYAN}🔌 Phase 2: Checking Port Availability${NC}"
echo "====================================="

REQUIRED_PORTS=(8001 6333 5432 6379 7474 8000 9090 3000)
for port in "${REQUIRED_PORTS[@]}"; do
    if port_available $port; then
        print_status "success" "Port $port is available"
    else
        print_status "warning" "Port $port is already in use"
    fi
done

echo ""

# Phase 3: Starting Docker Services
echo -e "${CYAN}🐳 Phase 3: Starting Docker Services${NC}"
echo "=================================="

if command_exists docker; then
    print_status "info" "Starting Docker services..."
    
    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_status "error" "Docker is not running. Please start Docker Desktop"
        exit 1
    fi
    
    # Start Docker services
    cd "$IZA_OS_ROOT"
    if [ -f "docker-compose.yml" ]; then
        print_status "info" "Starting Docker Compose services..."
        docker-compose up -d
        
        # Wait for key services
        print_status "info" "Waiting for PostgreSQL to be ready..."
        sleep 10
        
        print_status "info" "Waiting for Redis to be ready..."
        sleep 5
        
        print_status "success" "Docker services started successfully"
    else
        print_status "warning" "docker-compose.yml not found, skipping Docker services"
    fi
else
    print_status "warning" "Docker not available, skipping Docker services"
fi

echo ""

# Phase 4: Starting MCP Servers
echo -e "${CYAN}🔗 Phase 4: Starting MCP Servers${NC}"
echo "================================="

cd "$MCP_SERVERS_DIR"

# Start FastMCP Server
print_status "step" "Starting FastMCP Server (Business Automation)..."
if [ -f "fastmcp_server.py" ]; then
    nohup python3 fastmcp_server.py > fastmcp.log 2>&1 &
    FASTMCP_PID=$!
    echo $FASTMCP_PID > fastmcp.pid
    print_status "success" "FastMCP Server started with PID: $FASTMCP_PID"
else
    print_status "error" "fastmcp_server.py not found"
    exit 1
fi

# Start Graphiti Server
print_status "step" "Starting Graphiti Server (Knowledge Graph)..."
if [ -f "graphiti_mcp_server.py" ]; then
    nohup python3 graphiti_mcp_server.py > graphiti.log 2>&1 &
    GRAPHITI_PID=$!
    echo $GRAPHITI_PID > graphiti.pid
    print_status "success" "Graphiti Server started with PID: $GRAPHITI_PID"
else
    print_status "error" "graphiti_mcp_server.py not found"
    exit 1
fi

# Wait for MCP servers to start
print_status "info" "Waiting for MCP servers to start..."
sleep 5

# Check MCP server health
print_status "info" "Checking MCP server health..."

if wait_for_service "http://localhost:8001" "FastMCP Server"; then
    print_status "success" "FastMCP Server: http://localhost:8001 - HEALTHY"
else
    print_status "error" "FastMCP Server failed to start"
fi

if wait_for_service "http://localhost:6333" "Graphiti Server"; then
    print_status "success" "Graphiti Server: http://localhost:6333 - HEALTHY"
else
    print_status "error" "Graphiti Server failed to start"
fi

echo ""

# Phase 5: Starting IZA OS Agents
echo -e "${CYAN}🤖 Phase 5: Starting IZA OS Agents${NC}"
echo "================================="

cd "$AGENTS_DIR"

# Start Memory Integration Agent
print_status "step" "Starting Memory Integration Agent..."
if [ -f "memory_integration_agent_simple.py" ]; then
    nohup python3 memory_integration_agent_simple.py > memory.log 2>&1 &
    MEMORY_PID=$!
    echo $MEMORY_PID > memory.pid
    print_status "success" "Memory Integration Agent started with PID: $MEMORY_PID"
else
    print_status "error" "memory_integration_agent_simple.py not found"
    exit 1
fi

# Start SEAL Implementation Agent
print_status "step" "Starting SEAL Implementation Agent..."
if [ -f "seal_implementation_agent_simple.py" ]; then
    nohup python3 seal_implementation_agent_simple.py > seal.log 2>&1 &
    SEAL_PID=$!
    echo $SEAL_PID > seal.pid
    print_status "success" "SEAL Implementation Agent started with PID: $SEAL_PID"
else
    print_status "error" "seal_implementation_agent_simple.py not found"
    exit 1
fi

# Start MCP Integration Agent
print_status "step" "Starting MCP Integration Agent..."
if [ -f "mcp_integration_agent_simple.py" ]; then
    nohup python3 mcp_integration_agent_simple.py > mcp.log 2>&1 &
    MCP_PID=$!
    echo $MCP_PID > mcp.pid
    print_status "success" "MCP Integration Agent started with PID: $MCP_PID"
else
    print_status "error" "mcp_integration_agent_simple.py not found"
    exit 1
fi

# Start Agent-S Integration
print_status "step" "Starting Agent-S Integration..."
if [ -f "agent_s_integration.py" ]; then
    nohup python3 agent_s_integration.py > agent_s.log 2>&1 &
    AGENT_S_PID=$!
    echo $AGENT_S_PID > agent_s.pid
    print_status "success" "Agent-S Integration started with PID: $AGENT_S_PID"
else
    print_status "error" "agent_s_integration.py not found"
    exit 1
fi

echo ""

# Phase 6: Starting OpenLovable
echo -e "${CYAN}💝 Phase 6: Starting OpenLovable${NC}"
echo "==============================="

if [ -d "$OPENLOVABLE_DIR" ]; then
    cd "$OPENLOVABLE_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "info" "Installing OpenLovable dependencies..."
        npm install
    fi
    
    # Start OpenLovable in background
    print_status "step" "Starting OpenLovable..."
    nohup npm run dev > openlovable.log 2>&1 &
    OPENLOVABLE_PID=$!
    echo $OPENLOVABLE_PID > openlovable.pid
    print_status "success" "OpenLovable started with PID: $OPENLOVABLE_PID"
    
    # Wait for OpenLovable to start
    print_status "info" "Waiting for OpenLovable to start..."
    sleep 10
    
    if curl -s "http://localhost:3000" >/dev/null 2>&1; then
        print_status "success" "OpenLovable: http://localhost:3000 - HEALTHY"
    else
        print_status "warning" "OpenLovable may still be starting up"
    fi
else
    print_status "warning" "OpenLovable directory not found, skipping"
fi

echo ""

# Phase 7: System Status and Verification
echo -e "${CYAN}📊 Phase 7: System Status and Verification${NC}"
echo "========================================="

# Wait for all services to stabilize
print_status "info" "Waiting for all services to stabilize..."
sleep 10

# Check all service statuses
print_status "info" "Checking system status..."

# Check MCP servers
if curl -s "http://localhost:8001/health" >/dev/null 2>&1; then
    print_status "success" "✅ FastMCP Server: HEALTHY"
else
    print_status "error" "❌ FastMCP Server: UNHEALTHY"
fi

if curl -s "http://localhost:6333/query" >/dev/null 2>&1; then
    print_status "success" "✅ Graphiti Server: HEALTHY"
else
    print_status "error" "❌ Graphiti Server: UNHEALTHY"
fi

# Check Docker services
if command_exists docker; then
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "iza-"; then
        print_status "success" "✅ Docker Services: RUNNING"
    else
        print_status "warning" "⚠️  Docker Services: NOT RUNNING"
    fi
fi

# Check OpenLovable
if curl -s "http://localhost:3000" >/dev/null 2>&1; then
    print_status "success" "✅ OpenLovable: HEALTHY"
else
    print_status "warning" "⚠️  OpenLovable: STARTING UP"
fi

echo ""

# Final Status
echo -e "${CYAN}🎉 IZA OS Startup Complete!${NC}"
echo "=============================="
echo ""
echo -e "${GREEN}🚀 All systems are now running and ready for business automation!${NC}"
echo ""
echo -e "${BLUE}📊 System Status:${NC}"
echo "  • FastMCP Server: http://localhost:8001"
echo "  • Graphiti Server: http://localhost:6333"
echo "  • OpenLovable: http://localhost:3000"
echo "  • PostgreSQL: localhost:5432"
echo "  • Redis: localhost:6379"
echo "  • Neo4j: localhost:7474"
echo ""
echo -e "${BLUE}📝 Log Files:${NC}"
echo "  • Agent logs: $AGENTS_DIR/*.log"
echo "  • MCP server logs: $MCP_SERVERS_DIR/*.log"
echo "  • OpenLovable logs: $OPENLOVABLE_DIR/openlovable.log"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "  • Check status: $IZA_OS_ROOT/status_iza_os.sh"
echo "  • Stop system: $IZA_OS_ROOT/stop_iza_os.sh"
echo "  • View logs: tail -f $AGENTS_DIR/*.log"
echo ""
echo -e "${GREEN}🎯 Your IZA OS empire is now operational and ready to generate revenue!${NC}"
echo ""
echo -e "${YELLOW}💡 Next Steps:${NC}"
echo "  1. Test business automation workflows"
echo "  2. Monitor system performance"
echo "  3. Start generating revenue with automated businesses"
echo "  4. Scale your empire with additional automation"
echo ""

# Save startup summary
STARTUP_SUMMARY="$LOGS_DIR/startup_summary_$(date +%Y%m%d_%H%M%S).log"
{
    echo "IZA OS Startup Summary - $(date)"
    echo "================================"
    echo "FastMCP Server PID: $FASTMCP_PID"
    echo "Graphiti Server PID: $GRAPHITI_PID"
    echo "Memory Agent PID: $MEMORY_PID"
    echo "SEAL Agent PID: $SEAL_PID"
    echo "MCP Agent PID: $MCP_PID"
    echo "Agent-S PID: $AGENT_S_PID"
    echo "OpenLovable PID: $OPENLOVABLE_PID"
    echo ""
    echo "All services started successfully!"
} > "$STARTUP_SUMMARY"

print_status "success" "Startup summary saved to: $STARTUP_SUMMARY"
