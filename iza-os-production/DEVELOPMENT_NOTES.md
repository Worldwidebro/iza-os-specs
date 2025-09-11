# IZA OS Development Notes
*Last Updated: January 5, 2025*

## Project Overview
IZA OS is an ambitious AI-powered operating system designed to orchestrate multiple autonomous agents, manage venture creation and deployment, and provide a unified interface for AI-driven business operations.

## Current System State

### Infrastructure Status ✅ PARTIALLY OPERATIONAL
**Docker Services Running:**
- PostgreSQL (port 5433) - Database: `civilization`, User: `postgres`, Password: `civilization_dev_2025`
- Redis - Caching and message queuing
- N8N - Workflow automation
- Grafana - Monitoring and analytics
- Neo4j - Graph database
- MinIO - Object storage
- Prometheus - Metrics collection
- Portainer - Container management
- Nginx - Reverse proxy

**Issues Identified:**
- ChromaDB appears unhealthy
- Business model manager service experiencing restart loops
- Some containers may need configuration alignment

### Python Environment ✅ CONFIGURED
**Core Dependencies Installed:**
- `psycopg2-binary` - PostgreSQL adapter
- `python-dotenv` - Environment variable management
- `click` - CLI framework
- `rich` - Rich text and formatting
- `rich-click` - Enhanced CLI styling
- `textual` - TUI framework
- `pyyaml` - YAML processing

**Environment Configuration:**
- `.env` file updated with correct PostgreSQL credentials
- PYTHONPATH configured for module resolution
- Database connection tested and verified

### CLI System ✅ IMPLEMENTED
**IZA CLI Features:**
- Command-line interface with rich formatting
- Async command handling with proper synchronization
- Multiple command categories (ventures, agents, memory, system)
- Shell alias support (`iza` command)

**Available Commands:**
```bash
# System commands
iza brief          # System overview
iza start          # Initialize system
iza status         # Check system health
iza tui            # Launch terminal UI

# Venture management
iza ventures list  # List all ventures
iza ventures create # Create new venture
iza ventures deploy # Deploy venture

# Agent orchestration
iza agents list    # List running agents
iza agents start   # Start agent processes
iza agents stop    # Stop agent processes

# Memory management
iza memory query   # Query memory systems
iza memory sync    # Synchronize memory
iza memory backup  # Backup memory state
```

### Terminal User Interface (TUI) ✅ IMPLEMENTED
**Inspired by LazySSH architecture**, featuring:
- **Multi-tab interface**: Overview, Ventures, Agents, Logs
- **Real-time metrics**: System health, agent status, venture analytics
- **Interactive tables**: Sortable, filterable data views
- **Keyboard navigation**: Vim-style shortcuts and standard navigation
- **Rich styling**: Color-coded status indicators, progress bars
- **Live updates**: Real-time data refresh

**TUI Keyboard Shortcuts:**
- `Tab/Shift+Tab` - Navigate between tabs
- `q` - Quit application
- `r` - Refresh current view
- `h` - Show help
- `j/k` - Navigate up/down in lists
- `Enter` - Select/activate item

### Core Modules ✅ STUBBED
**Created foundational modules:**
- `memory_core.py` - Memory management system
- `agent_orchestration.py` - Multi-agent coordination
- `venture_factory.py` - Automated venture creation
- `problem_discovery.py` - Market opportunity identification

### Logging System ✅ SIMPLIFIED
**Streamlined logging implementation:**
- Console output with color coding
- Optional file logging
- Configurable log levels
- No complex external dependencies
- Async-compatible design

## Development Journey

### Phase 1: Infrastructure Setup
- Diagnosed PostgreSQL connection issues
- Identified credential mismatch between running containers and config files
- Updated `.env` with correct database URL: `postgresql://postgres:civilization_dev_2025@localhost:5433/civilization`
- Verified database connectivity with test scripts

### Phase 2: CLI Development
- Built comprehensive Click-based CLI framework
- Implemented async command handling with `asyncio.run()` wrappers
- Created rich help system with enhanced formatting
- Added shell alias setup for ease of use (`iza` command)

### Phase 3: TUI Implementation
- Studied LazySSH project for UI/UX inspiration
- Implemented Textual-based terminal dashboard
- Created multi-tab interface with real-time updates
- Fixed widget mounting and parameter compatibility issues
- Integrated TUI into main CLI system

### Phase 4: Core Module Scaffolding
- Created stub implementations for all major system components
- Ensured proper Python module structure
- Set up PYTHONPATH for reliable imports
- Prepared foundation for AI integration and business logic

## Technical Architecture

### Database Layer
- **PostgreSQL**: Primary data store for ventures, agents, and system state
- **Neo4j**: Graph relationships and knowledge mapping
- **Redis**: Caching, session management, and real-time data
- **ChromaDB**: Vector embeddings and semantic search (needs fixing)

### Application Layer
- **CLI Interface**: Command-line management and scripting
- **TUI Dashboard**: Interactive terminal interface for monitoring
- **Agent Scripts**: Individual Python processes for specific tasks
- **Core Modules**: Business logic and system orchestration

### Infrastructure Layer
- **Docker Compose**: Container orchestration
- **Nginx**: Reverse proxy and load balancing
- **Prometheus + Grafana**: Monitoring and alerting
- **MinIO**: Object storage for files and assets

## Current Reality vs Vision

### ✅ What's Working
- Basic infrastructure is running
- Database connectivity established
- CLI system operational
- TUI dashboard functional
- Core module structure in place
- Development environment configured

### 🚧 Work in Progress
- Individual agent scripts exist but need integration
- Multi-agent orchestration needs RabbitMQ implementation
- Revenue tracking and Stripe integration pending
- API integrations (Warp.dev, devv.ai, bolt.new) not yet connected

### 📋 Planned Features
- 478 concurrent venture management
- Automated revenue optimization
- Seamless IDE integrations
- Real-time market analysis
- Autonomous business deployment

## Next Steps

### Immediate Priority (Week 1)
1. **Fix ChromaDB container health issues**
2. **Stabilize business model manager service**
3. **Implement RabbitMQ-based agent orchestration**
4. **Connect existing agent scripts to unified system**

### Short-term Goals (Month 1)
1. **Build IZA OS unified platform integration**
2. **Implement Stripe revenue tracking**
3. **Create MVP venture deployment pipeline**
4. **Add real AI API connections (OpenAI, Anthropic)**

### Medium-term Goals (Quarter 1)
1. **Launch first automated ventures**
2. **Integrate Warp.dev and devv.ai workflows**
3. **Implement bolt.new rapid prototyping**
4. **Build comprehensive monitoring and analytics**

### Long-term Vision (Year 1)
1. **Scale to hundreds of concurrent ventures**
2. **Achieve significant automated revenue generation**
3. **Create marketplace for AI agents and ventures**
4. **Establish IZA OS as leading AI business platform**

## Development Commands Reference

### Database Connection Test
```bash
python3 -c "
import psycopg2
from dotenv import load_dotenv
import os
load_dotenv()
conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()
cur.execute('SELECT version();')
print('Connected:', cur.fetchone()[0])
conn.close()
"
```

### CLI Usage Examples
```bash
# Setup alias (run once)
source setup_alias.sh

# Basic commands
iza brief
iza status
iza tui

# Venture management
iza ventures list
iza ventures create --name "AI SaaS Venture" --market "B2B Software"

# Agent operations
iza agents list
iza agents start --type "market-research"
```

### TUI Launch
```bash
iza tui  # Full-featured terminal dashboard
```

## File Structure
```
/Users/divinejohns/memU/iza-os-production/
├── .env                    # Environment configuration
├── iza_cli.py             # Main CLI application
├── iza_tui.py             # Terminal UI dashboard
├── setup_alias.sh         # Shell alias configuration
├── core/                  # Core system modules
│   ├── memory_core.py
│   ├── agent_orchestration.py
│   ├── venture_factory.py
│   └── problem_discovery.py
├── docker-compose.yml     # Container orchestration
├── logs/                  # System logs
└── README.md             # Project documentation
```

## Known Issues & Solutions

### Issue: PostgreSQL Connection Failed
**Solution**: Updated `.env` with correct credentials for running container
- Port: 5433 (not 5432)
- Password: `civilization_dev_2025`
- Database: `civilization`

### Issue: Async/Sync CLI Integration
**Solution**: Wrapped async functions with `asyncio.run()` for Click compatibility

### Issue: Textual Widget Mounting
**Solution**: Only mount widgets after component initialization, removed unsupported parameters

### Issue: Module Import Errors
**Solution**: Configured PYTHONPATH and simplified logging dependencies

## Contributing Notes

### Development Setup
```bash
# Install dependencies
pip install psycopg2-binary python-dotenv click rich rich-click textual pyyaml

# Set environment
export PYTHONPATH="/Users/divinejohns/memU/iza-os-production:$PYTHONPATH"

# Load environment variables
source .env

# Setup CLI alias
source setup_alias.sh
```

### Testing Commands
```bash
# Test database connection
python3 test_db_connection.py

# Test CLI commands
iza --help
iza brief
iza status

# Test TUI
iza tui
```

## Project Inspiration

This project draws inspiration from several successful open-source projects:
- **LazySSH**: Terminal UI design and navigation patterns
- **lazydocker**: Container management interface concepts
- **k9s**: Kubernetes dashboard interaction model

## Conclusion

The IZA OS project has achieved a solid foundation with working infrastructure, functional CLI, and beautiful terminal UI. While the grand vision of autonomous venture management and AI-driven business operations is still being built, the core system is operational and ready for the next phase of development.

The system successfully demonstrates the integration of modern DevOps practices, Python CLI development, and innovative terminal-based user interfaces. The next major milestone is connecting the individual components into a unified, AI-powered business automation platform.

---

*This document serves as a comprehensive record of the IZA OS development journey, current capabilities, and roadmap for future enhancements.*
