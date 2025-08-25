#!/bin/bash
# 🖥️ OPTIMAL TERMINAL WORKFLOW SETUP FOR IZA OS EMPIRE
# ═══════════════════════════════════════════════════════════════
# Configures 4-terminal workflow optimized for AI empire management
# with tmux session persistence, token optimization, and revenue focus

echo "🖥️ SETTING UP OPTIMAL TERMINAL WORKFLOW FOR IZA OS EMPIRE"
echo "═══════════════════════════════════════════════════════════"

# Terminal Workflow Configuration
setup_terminal_workflow() {
    echo "🔧 Configuring 4-Terminal IZA OS Workflow..."
    
    # Terminal 1: IZA Command Center
    echo "📱 Terminal 1 - IZA Command Center:"
    echo "  Purpose: Primary IZA OS operations and empire management"
    echo "  Commands: iza-launch, iza-status, iza-empire, iza-agents"
    echo "  Tmux Session: iza-main"
    
    # Terminal 2: Development Hub  
    echo "📱 Terminal 2 - Development Hub:"
    echo "  Purpose: Active development and AI-powered coding"
    echo "  Commands: code ., qwen, gemini chat, claude-cli"
    echo "  Tmux Session: dev"
    
    # Terminal 3: System Monitoring
    echo "📱 Terminal 3 - System Monitoring:"
    echo "  Purpose: Real-time monitoring and system health"
    echo "  Commands: tail -f logs, iza-api, system monitoring"
    echo "  Tmux Session: monitoring"
    
    # Terminal 4: Revenue Operations
    echo "📱 Terminal 4 - Revenue Operations:"  
    echo "  Purpose: Business operations and revenue tracking"
    echo "  Commands: iza-revenue, iza-agents, business analytics"
    echo "  Tmux Session: revenue"
}

# Create Tmux Session Scripts
create_tmux_sessions() {
    echo "⚡ Creating persistent tmux sessions..."
    
    # Create tmux configuration
    cat > ~/.tmux.conf << 'EOF'
# IZA OS Tmux Configuration
set -g prefix C-a
unbind C-b
bind C-a send-prefix

# Session management
bind r source-file ~/.tmux.conf \; display "Reloaded!"
bind | split-window -h
bind - split-window -v

# IZA OS session shortcuts
bind-key I new-session -d -s iza-main -c "/Users/divinejohns/memU" "bash"
bind-key D new-session -d -s dev -c "/Users/divinejohns/memU" "bash"
bind-key M new-session -d -s monitoring -c "/Users/divinejohns/memU" "bash"
bind-key R new-session -d -s revenue -c "/Users/divinejohns/memU" "bash"

# Window navigation
bind-key -n M-1 select-session -t iza-main
bind-key -n M-2 select-session -t dev
bind-key -n M-3 select-session -t monitoring
bind-key -n M-4 select-session -t revenue

# IZA OS empire status
set -g status-left "#[fg=green]👑 IZA OS #[fg=blue]#S #[default]"
set -g status-right "#[fg=yellow]%Y-%m-%d %H:%M #[fg=green]Empire: OPERATIONAL"
EOF
    
    echo "✅ Tmux configuration created"
}

# Create Terminal Session Scripts
create_session_scripts() {
    echo "📜 Creating terminal session startup scripts..."
    
    # IZA Main Session
    cat > ~/iza-main-session.sh << 'EOF'
#!/bin/bash
# IZA OS Main Command Session
cd /Users/divinejohns/memU
clear
echo "👑 IZA OS EMPIRE COMMAND CENTER"
echo "═══════════════════════════════════"
iza-status
echo ""
echo "💡 Available Commands:"
echo "  iza-launch    - Full empire interface"
echo "  iza-empire    - Imperial command center"
echo "  iza-agents    - Agent management"
echo "  iza-revenue   - Revenue operations"
echo "  iza-api       - API health check"
echo ""
EOF
    
    # Development Session
    cat > ~/dev-session.sh << 'EOF'
#!/bin/bash
# Development Hub Session  
cd /Users/divinejohns/memU
clear
echo "💻 IZA OS DEVELOPMENT HUB"
echo "═══════════════════════════"
echo "🎯 AI-Powered Development Environment Ready"
echo ""
echo "🛠️ Available Tools:"
echo "  code .        - Open VS Code"
echo "  qwen          - Qwen AI assistant"
echo "  gemini chat   - Gemini AI chat"
echo "  iza-memory    - Memory system access"
echo ""
EOF
    
    # Monitoring Session
    cat > ~/monitoring-session.sh << 'EOF'
#!/bin/bash
# System Monitoring Session
cd /Users/divinejohns/memU
clear
echo "📊 IZA OS SYSTEM MONITORING"
echo "═══════════════════════════════"
echo "🔍 Real-time Empire Health Monitoring"
echo ""
echo "📈 Monitoring Commands:"
echo "  tail -f memory_orchestrator.log  - Memory system logs"
echo "  iza-api                          - API health check"
echo "  python3 IZA_OS_MASTER_DASHBOARD.py - Full dashboard"
echo ""
# Start log monitoring
tail -f memory_orchestrator.log 2>/dev/null || echo "Logs will appear here when available"
EOF
    
    # Revenue Operations Session
    cat > ~/revenue-session.sh << 'EOF'
#!/bin/bash
# Revenue Operations Session
cd /Users/divinejohns/memU
clear
echo "💰 IZA OS REVENUE OPERATIONS"
echo "═══════════════════════════════"
echo "📈 Empire Revenue Command Center"
echo ""
echo "💎 Revenue Commands:"
echo "  iza-revenue   - Revenue tracking and optimization"
echo "  iza-agents    - Agent workforce management"
echo "  iza-empire    - Deploy revenue ventures"
echo ""
iza-revenue
EOF
    
    # Make scripts executable
    chmod +x ~/iza-main-session.sh
    chmod +x ~/dev-session.sh
    chmod +x ~/monitoring-session.sh
    chmod +x ~/revenue-session.sh
    
    echo "✅ Session startup scripts created"
}

# Token Optimization Setup
setup_token_optimization() {
    echo "⚡ Setting up token optimization strategies..."
    
    # Create token optimization aliases
    cat >> ~/.zshrc << 'EOF'

# IZA OS Token Optimization
alias qwen-code="ollama run qwen3:30b"
alias gemini-research="gemini chat"
alias local-ai="qwen-code"
alias smart-route="python3 -c 'from UNIVERSAL_API_ORCHESTRATOR import *; asyncio.run(UniversalAPIOrchestrator().smart_chat(input(\"Query: \")))'"

# Token-efficient development aliases  
alias ai-code="qwen-code"
alias ai-research="gemini-research"
alias ai-quick="smart-route"
alias token-status="python3 -c 'from UNIVERSAL_API_ORCHESTRATOR import *; asyncio.run(UniversalAPIOrchestrator().get_usage_stats())'"
EOF
    
    echo "✅ Token optimization aliases added"
}

# Browser Optimization Guide
create_browser_guide() {
    echo "🌐 Creating browser optimization guide..."
    
    cat > ~/arc-browser-setup.md << 'EOF'
# 🌐 ARC BROWSER OPTIMIZATION FOR IZA OS EMPIRE

## Optimal Workspace Configuration

### Workspace 1: Command Center 👑
- IZA OS Master Dashboard
- System Status Monitoring  
- API Health Dashboard
- Empire Performance Metrics

### Workspace 2: Development 💻
- Claude Desktop (primary development)
- GitHub repositories
- Technical documentation
- API documentation and testing

### Workspace 3: Business 💼
- Revenue Dashboard
- Client Portal and Communications
- Business Analytics
- Payment Processing

### Workspace 4: Research 🔍
- AI Tools Discovery
- Competitive Analysis
- Integration Opportunities
- Market Research

## Recommended Settings
- Total Tabs: 12-16 (3-4 per workspace)
- Tab Grouping: By project/client
- Workspace Switching: Cmd+1,2,3,4
- AI-Powered Search: Enabled for research

## Productivity Features
- Little Arc for quick tasks
- Split View for development
- Picture-in-Picture for monitoring
- Instant Search across all workspaces
EOF
    
    echo "✅ Arc browser optimization guide created"
}

# Raycast Configuration
create_raycast_config() {
    echo "⚡ Creating Raycast shortcuts configuration..."
    
    cat > ~/raycast-iza-shortcuts.json << 'EOF'
{
  "shortcuts": {
    "empire_management": {
      "Empire Status": {
        "command": "iza-status",
        "description": "Check IZA OS empire status",
        "icon": "👑"
      },
      "Deploy Venture": {
        "command": "iza-empire",
        "description": "Launch imperial command center",
        "icon": "🚀"
      },
      "Agent Management": {
        "command": "iza-agents", 
        "description": "Manage agent workforce",
        "icon": "🤖"
      },
      "Revenue Operations": {
        "command": "iza-revenue",
        "description": "Revenue tracking and optimization",
        "icon": "💰"
      },
      "API Health Check": {
        "command": "iza-api",
        "description": "Test all API providers",
        "icon": "🌐"
      }
    },
    "development": {
      "Open MemU": {
        "command": "cd /Users/divinejohns/memU && code .",
        "description": "Open memU in VS Code",
        "icon": "💻"
      },
      "Qwen Chat": {
        "command": "qwen",
        "description": "Start Qwen AI assistant",
        "icon": "🧠"
      },
      "Gemini Chat": {
        "command": "gemini chat",
        "description": "Start Gemini AI chat",
        "icon": "✨"
      },
      "Master Dashboard": {
        "command": "python3 /Users/divinejohns/memU/IZA_OS_MASTER_DASHBOARD.py",
        "description": "Launch master dashboard",
        "icon": "📊"
      },
      "30-Day Plan": {
        "command": "python3 /Users/divinejohns/memU/IZA_OS_30_DAY_ACTION_PLAN.py",
        "description": "View 30-day action plan",
        "icon": "📚"
      }
    }
  }
}
EOF
    
    echo "✅ Raycast shortcuts configuration created"
}

# Main execution
main() {
    setup_terminal_workflow
    create_tmux_sessions
    create_session_scripts
    setup_token_optimization
    create_browser_guide
    create_raycast_config
    
    echo ""
    echo "🎉 OPTIMAL TERMINAL WORKFLOW SETUP COMPLETE!"
    echo "═══════════════════════════════════════════════════════"
    echo "🖥️ 4-Terminal Configuration Ready:"
    echo "  Terminal 1: ~/iza-main-session.sh"
    echo "  Terminal 2: ~/dev-session.sh" 
    echo "  Terminal 3: ~/monitoring-session.sh"
    echo "  Terminal 4: ~/revenue-session.sh"
    echo ""
    echo "⚡ Token Optimization: Enabled"
    echo "🌐 Browser Guide: ~/arc-browser-setup.md"
    echo "🎯 Raycast Config: ~/raycast-iza-shortcuts.json"
    echo ""
    echo "🚀 NEXT STEPS:"
    echo "1. Open 4 terminal windows"
    echo "2. Run session scripts in each terminal"
    echo "3. Set up Arc browser workspaces"
    echo "4. Import Raycast shortcuts"
    echo "5. Execute: python3 IZA_OS_MASTER_DASHBOARD.py"
    echo ""
    echo "👑 YOUR AI EMPIRE TERMINAL WORKFLOW IS READY!"
    echo "═══════════════════════════════════════════════════════"
}

main