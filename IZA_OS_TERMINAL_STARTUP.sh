#!/bin/bash
# IZA OS TERMINAL STARTUP SCRIPT
# Auto-launches IZA OS Command Center when terminal starts

# IZA OS ASCII Art Banner
show_iza_banner() {
    echo ""
    echo "   ██╗███████╗ █████╗      ██████╗ ███████╗"
    echo "   ██║╚══███╔╝██╔══██╗    ██╔═══██╗██╔════╝"
    echo "   ██║  ███╔╝ ███████║    ██║   ██║███████╗"
    echo "   ██║ ███╔╝  ██╔══██║    ██║   ██║╚════██║"
    echo "   ██║███████╗██║  ██║    ╚██████╔╝███████║"
    echo "   ╚═╝╚══════╝╚═╝  ╚═╝     ╚═════╝ ╚══════╝"
    echo ""
    echo "   🏛️ INTELLIGENT ZONE ARCHITECTURE OS 🏛️"
    echo "   ═══════════════════════════════════════════"
    echo "   👑 Your AI Empire Command Center"
    echo "   🌐 Sovereign Digital Nation Operating System"
    echo "   ═══════════════════════════════════════════"
    echo ""
}

# IZA OS Quick Status
show_iza_status() {
    echo "📊 IZA OS STATUS:"
    
    # Check if Python is available
    if command -v python3 &> /dev/null; then
        echo "  ✅ Python Runtime: Ready"
    else
        echo "  ❌ Python Runtime: Missing"
        return
    fi
    
    # Check if IZA OS files exist
    if [ -f "/Users/divinejohns/memU/IZA_OS_COMMAND_CENTER.py" ]; then
        echo "  ✅ IZA OS Kernel: Installed"
    else
        echo "  ❌ IZA OS Kernel: Missing"
        return
    fi
    
    # Check if Universal API Orchestrator exists
    if [ -f "/Users/divinejohns/memU/UNIVERSAL_API_ORCHESTRATOR.py" ]; then
        echo "  ✅ Universal API: Available"
    else
        echo "  ❌ Universal API: Missing"
    fi
    
    # Check if Integration Bridge exists
    if [ -f "/Users/divinejohns/memU/REPOSITORY_INTEGRATION_BRIDGE.py" ]; then
        echo "  ✅ Integration Bridge: Ready"
    else
        echo "  ❌ Integration Bridge: Missing"
    fi
    
    # Check memory system
    if [ -f "/Users/divinejohns/memU/UNIFIED_MEMORY_ORCHESTRATOR.py" ]; then
        echo "  ✅ Unified Memory: Operational"
    else
        echo "  ❌ Unified Memory: Missing"
    fi
    
    # Check for API keys
    local api_keys=0
    [ ! -z "$OPENAI_API_KEY" ] && ((api_keys++))
    [ ! -z "$ANTHROPIC_API_KEY" ] && ((api_keys++))
    [ ! -z "$OPENROUTER_API_KEY" ] && ((api_keys++))
    [ ! -z "$GROQ_API_KEY" ] && ((api_keys++))
    [ ! -z "$GOOGLE_AI_API_KEY" ] && ((api_keys++))
    
    echo "  🔑 API Keys: ${api_keys}/5 configured"
    
    echo ""
}

# IZA OS Quick Commands Menu
show_iza_commands() {
    echo "💡 IZA OS QUICK COMMANDS:"
    echo "  iza-launch       - Launch full IZA OS interface"
    echo "  iza-status       - Show detailed system status"
    echo "  iza-memory       - Access unified memory system"
    echo "  iza-api          - Test universal API orchestrator"
    echo "  iza-bridge       - Repository integration bridge"
    echo "  iza-empire       - Empire status and management"
    echo "  iza-agents       - Deploy and manage agents"
    echo "  iza-revenue      - Revenue tracking and optimization"
    echo "  iza-help         - Show detailed help"
    echo ""
}

# Define IZA OS commands as functions
iza-launch() {
    echo "🚀 Launching IZA OS Command Center..."
    cd /Users/divinejohns/memU
    python3 IZA_OS_COMMAND_CENTER.py
}

iza-status() {
    echo "📊 Detailed IZA OS System Status:"
    cd /Users/divinejohns/memU
    python3 -c "
import asyncio
from IZA_OS_COMMAND_CENTER import IzaOSCommandCenter

async def show_status():
    iza = IzaOSCommandCenter()
    status = await iza._empire_status_report()
    
    print(f'🏛️ Empire: {status[\"empire_name\"]}')
    print(f'🖥️ OS Version: {status[\"operating_system\"]}')
    print(f'📊 Sovereignty: {status[\"sovereignty_status\"]}')
    print(f'🧠 Total Memories: {status[\"memory_intelligence\"][\"total_memories\"]}')
    print(f'🤖 Total Agents: {status[\"agent_workforce\"][\"total_agents\"]}')
    print(f'🏢 Active Divisions: {len([d for d in status[\"divisions\"].values() if d[\"status\"] == \"active\"])}')
    
    print(f'\\n🎯 Next Imperial Objectives:')
    for obj in status['next_imperial_objectives']:
        print(f'  • {obj}')

asyncio.run(show_status())
"
}

iza-memory() {
    echo "🧠 Accessing Unified Memory System..."
    cd /Users/divinejohns/memU
    python3 UNIFIED_MEMORY_ORCHESTRATOR.py
}

iza-api() {
    echo "🌐 Testing Universal API Orchestrator..."
    cd /Users/divinejohns/memU
    python3 UNIVERSAL_API_ORCHESTRATOR.py
}

iza-bridge() {
    echo "🌉 Repository Integration Bridge..."
    cd /Users/divinejohns/memU
    python3 REPOSITORY_INTEGRATION_BRIDGE.py
}

iza-empire() {
    echo "🏛️ Empire Management Interface..."
    cd /Users/divinejohns/memU
    python3 -c "
import asyncio
from IZA_OS_COMMAND_CENTER import IzaOSCommandCenter

async def empire_interface():
    iza = IzaOSCommandCenter()
    print('👑 IMPERIAL COMMAND INTERFACE')
    print('Available commands:')
    print('  • deploy venture [name]')
    print('  • activate agents [type] [count]')
    print('  • empire status')
    print('  • revenue report')
    print('  • strategic analysis [topic]')
    
    command = input('\\n👑 Enter Imperial Command: ').strip()
    if command:
        result = await iza.execute_imperial_command(command)
        print(f'\\n📋 Result: {result}')

asyncio.run(empire_interface())
"
}

iza-agents() {
    echo "🤖 Agent Management System..."
    cd /Users/divinejohns/memU
    python3 -c "
import asyncio
from IZA_OS_COMMAND_CENTER import IzaOSCommandCenter

async def agent_management():
    iza = IzaOSCommandCenter()
    print('🤖 AGENT WORKFORCE MANAGEMENT')
    print('Agent Types Available:')
    print('  • workers - Single-task agents')
    print('  • managers - Orchestration agents') 
    print('  • strategists - Planning agents')
    
    agent_type = input('\\nAgent type to activate: ').strip()
    count = input('Number of agents: ').strip() or '1'
    
    if agent_type:
        command = f'activate agents {agent_type} {count}'
        result = await iza.execute_imperial_command(command)
        print(f'\\n🤖 Agent Deployment Result: {result}')

asyncio.run(agent_management())
"
}

iza-revenue() {
    echo "💰 Revenue Tracking and Optimization..."
    cd /Users/divinejohns/memU
    python3 -c "
import asyncio
from IZA_OS_COMMAND_CENTER import IzaOSCommandCenter

async def revenue_system():
    iza = IzaOSCommandCenter()
    print('💰 REVENUE OPTIMIZATION SYSTEM')
    print('Generating revenue report...')
    
    result = await iza.execute_imperial_command('revenue report')
    print(f'\\n📊 Revenue Report: {result}')
    
    optimize = input('\\nRun revenue optimization? (y/n): ').strip().lower()
    if optimize == 'y':
        opt_result = await iza.execute_imperial_command('optimize revenue')
        print(f'\\n⚡ Optimization Result: {opt_result}')

asyncio.run(revenue_system())
"
}

iza-help() {
    echo "📚 IZA OS HELP SYSTEM"
    echo "═══════════════════════"
    echo ""
    echo "🏛️ WHAT IS IZA OS?"
    echo "   IZA OS (Intelligent Zone Architecture Operating System)"
    echo "   is your AI Empire's sovereign operating system that:"
    echo "   • Manages 12+ integrated repositories"
    echo "   • Routes AI requests across 7 providers"
    echo "   • Orchestrates multi-agent workflows"
    echo "   • Tracks revenue and business metrics"
    echo "   • Unifies memory across all systems"
    echo ""
    echo "🎯 CORE COMMANDS:"
    echo "   iza-launch    - Full IZA OS interface"
    echo "   iza-status    - System health check"
    echo "   iza-empire    - Imperial command center"
    echo "   iza-agents    - Agent workforce management"
    echo "   iza-revenue   - Business optimization"
    echo ""
    echo "🔧 SYSTEM COMMANDS:"
    echo "   iza-memory    - Memory system access"
    echo "   iza-api       - API orchestrator test"
    echo "   iza-bridge    - Repository integration"
    echo ""
    echo "🚀 QUICK START:"
    echo "   1. Run: iza-status (check system)"
    echo "   2. Run: iza-launch (full interface)"
    echo "   3. Use: Imperial commands for operations"
    echo ""
    echo "📖 FULL DOCUMENTATION:"
    echo "   /Users/divinejohns/memU/NEXT_WEEK_REVENUE_PLAYBOOK.md"
    echo ""
}

# Main startup function
iza_startup() {
    # Only show if this is an interactive terminal
    if [[ $- == *i* ]]; then
        show_iza_banner
        show_iza_status
        show_iza_commands
        
        # Export functions so they're available in the shell
        export -f iza-launch iza-status iza-memory iza-api iza-bridge iza-empire iza-agents iza-revenue iza-help
        
        # Set IZA OS environment variables
        export IZA_OS_HOME="/Users/divinejohns/memU"
        export IZA_OS_VERSION="2.0.0"
        export AI_EMPIRE_STATUS="OPERATIONAL"
        
        # Add IZA OS to PATH for easy access
        export PATH="$IZA_OS_HOME:$PATH"
        
        echo "🎉 IZA OS READY - Your AI Empire Awaits Your Command!"
        echo "💡 Type any iza-* command to begin, or 'iza-help' for full documentation"
        echo ""
    fi
}

# Run startup if sourced
iza_startup