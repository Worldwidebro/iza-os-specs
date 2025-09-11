#!/bin/bash
# Complete setup script for AI Orchestrator

set -e

echo " Setting up Enhanced AI Orchestrator"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
check_prerequisites() {
    echo " Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is required but not installed${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose is required but not installed${NC}"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is required but not installed${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Prerequisites check passed${NC}"
}

# Create directory structure
create_directories() {
    echo " Creating directory structure..."
    
    directories=(
        "agents/finance_agent"
        "agents/marketing_agent"
        "agents/operations_agent"
        "mcp_servers/apple_notes"
        "mcp_servers/google_drive"
        "mcp_servers/github"
        "mcp_servers/calendar"
        "config"
        "credentials"
        "logs"
        "monitoring"
        "tests"
        "docs"
        "scripts"
        "data"
    )
    
    for dir in "${directories[@]}"; do
        mkdir -p "$dir"
        echo "  Created: $dir"
    done
    
    echo -e "${GREEN}✅ Directory structure created${NC}"
}

# Setup configuration files
setup_config() {
    echo "⚙️ Setting up configuration files..."
    
    # Copy environment file
    if [ ! -f .env ]; then
        cp .env.example .env
        echo -e "${YELLOW} Created .env file - please edit with your API keys${NC}"
    fi
    
    # Create MCP tools configuration
    cat > config/mcp_tools.yaml << EOF
tools:
  apple_notes:
    endpoint: "http://localhost:8001"
    capabilities: ["list_notes", "get_note_content", "search_notes"]
    auth_required: false
    rate_limit: 100
  
  google_drive:
    endpoint: "http://localhost:8002"
    capabilities: ["search_files", "get_file_content", "list_files"]
    auth_required: true
    rate_limit: 50
  
  github:
    endpoint: "http://localhost:8003"
    capabilities: ["search_repos", "get_repo_info", "list_issues"]
    auth_required: true
    rate_limit: 60
  
  calendar:
    endpoint: "http://localhost:8004"
    capabilities: ["get_events", "create_event", "search_events"]
    auth_required: true
    rate_limit: 30
EOF

    # Create Prometheus configuration
    mkdir -p monitoring
    cat > monitoring/prometheus.yml << EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'orchestrator'
    static_configs:
      - targets: ['orchestrator:8000']
  
  - job_name: 'finance-agent'
    static_configs:
      - targets: ['finance-agent:8000']
  
  - job_name: 'marketing-agent'
    static_configs:
      - targets: ['marketing-agent:8000']
  
  - job_name: 'operations-agent'
    static_configs:
      - targets: ['operations-agent:8000']
EOF

    echo -e "${GREEN}✅ Configuration files created${NC}"
}

# Main setup function
main() {
    echo " Enhanced AI Orchestrator Setup"
    echo "================================="
    
    check_prerequisites
    # create_directories # Already done in the parent step
    setup_config
    
    echo ""
    echo -e "${GREEN} Setup completed successfully!${NC}"
    echo ""
    echo " Next steps:"
    echo "1. Edit .env file with your API keys"
    echo "2. Run: ./scripts/start.sh"
    echo "3. Test: ./scripts/test.sh"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi