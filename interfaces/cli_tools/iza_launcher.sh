#!/bin/bash
# IZA OS Enhanced CLI Launcher Script
# Makes the IZA CLI globally accessible and optimized

# Set up environment
export PYTHONPATH="/Users/divinejohns/memU:/Users/divinejohns/memU/core:/Users/divinejohns/memU/workflows:$PYTHONPATH"
export IZA_HOME="/Users/divinejohns/memU"
export IZA_CLI_PATH="/Users/divinejohns/memU/interfaces/cli_tools"

# Install required dependencies if not present
install_dependencies() {
    echo "🔧 Installing CLI dependencies..."
    pip install click rich asyncio uuid pathlib > /dev/null 2>&1
    echo "✅ Dependencies installed"
}

# Check if dependencies are installed
check_dependencies() {
    if ! python3 -c "import click, rich" > /dev/null 2>&1; then
        install_dependencies
    fi
}

# Main CLI execution
run_iza_cli() {
    cd "$IZA_HOME"
    check_dependencies
    python3 "$IZA_CLI_PATH/iza_cli_enhanced.py" "$@"
}

# Create global command aliases
create_global_commands() {
    echo "🌐 Creating global IZA commands..."
    
    # Add to .zshrc for global access
    if [[ -f ~/.zshrc ]]; then
        if ! grep -q "# IZA OS CLI Commands" ~/.zshrc; then
            echo "" >> ~/.zshrc
            echo "# IZA OS CLI Commands" >> ~/.zshrc
            echo "alias iza='$IZA_CLI_PATH/iza_launcher.sh'" >> ~/.zshrc
            echo "alias iza-demo-app='$IZA_CLI_PATH/iza_launcher.sh demo-app'" >> ~/.zshrc
            echo "alias iza-demo-analysis='$IZA_CLI_PATH/iza_launcher.sh demo-analysis'" >> ~/.zshrc
            echo "alias iza-demo-agent='$IZA_CLI_PATH/iza_launcher.sh demo-agent'" >> ~/.zshrc
            echo "alias iza-gen-code='$IZA_CLI_PATH/iza_launcher.sh gen-code'" >> ~/.zshrc
            echo "alias iza-gen-api='$IZA_CLI_PATH/iza_launcher.sh gen-api'" >> ~/.zshrc
            echo "alias iza-recall='$IZA_CLI_PATH/iza_launcher.sh recall'" >> ~/.zshrc
            echo "alias iza-learn='$IZA_CLI_PATH/iza_launcher.sh learn'" >> ~/.zshrc
            echo "alias iza-showcase='$IZA_CLI_PATH/iza_launcher.sh showcase'" >> ~/.zshrc
            echo "alias iza-status='$IZA_CLI_PATH/iza_launcher.sh status'" >> ~/.zshrc
            echo "alias iza-interactive='$IZA_CLI_PATH/iza_launcher.sh interactive'" >> ~/.zshrc
            echo "✅ Global commands added to .zshrc"
        else
            echo "✅ Global commands already configured"
        fi
    fi
}

# Show IZA CLI banner
show_banner() {
    echo ""
    echo "   ██╗███████╗ █████╗      ██████╗ ███████╗"
    echo "   ██║╚══███╔╝██╔══██╗    ██╔═══██╗██╔════╝"
    echo "   ██║  ███╔╝ ███████║    ██║   ██║███████╗"
    echo "   ██║ ███╔╝  ██╔══██║    ██║   ██║╚════██║"
    echo "   ██║███████╗██║  ██║    ╚██████╔╝███████║"
    echo "   ╚═╝╚══════╝╚═╝  ╚═╝     ╚═════╝ ╚══════╝"
    echo ""
    echo "   🔧 ENHANCED CLI - SUPREME AI COMMAND INTERFACE"
    echo "   ═══════════════════════════════════════════════"
    echo "   💻 Memory-Integrated Commands"
    echo "   🎯 Customer Experience Optimized"  
    echo "   🚀 Instant AI Capability Showcase"
    echo "   ═══════════════════════════════════════════════"
    echo ""
}

# Setup mode
if [[ "$1" == "--setup" ]]; then
    show_banner
    echo "🔧 Setting up IZA OS Enhanced CLI..."
    create_global_commands
    echo ""
    echo "✅ Setup complete! Restart your terminal or run 'source ~/.zshrc'"
    echo "💡 Try: iza --help"
    exit 0
fi

# Help mode
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]] || [[ -z "$1" ]]; then
    show_banner
    echo "🔧 ENHANCED CLI COMMANDS:"
    echo ""
    echo "🎯 CUSTOMER DEMONSTRATIONS:"
    echo "  iza demo-app <description>     - Generate complete application"
    echo "  iza demo-analysis <query>      - Intelligent data analysis"  
    echo "  iza demo-agent <task>          - Deploy autonomous agent"
    echo "  iza showcase                   - Launch AI showcase"
    echo ""
    echo "💻 DEVELOPMENT TOOLS:"
    echo "  iza gen-code <description>     - Generate optimized code"
    echo "  iza gen-api <description>      - Generate REST API"
    echo ""
    echo "🧠 MEMORY SYSTEM:"
    echo "  iza recall <query>             - Search memory system"
    echo "  iza learn <information>        - Store in memory"
    echo ""
    echo "🖥️  SYSTEM OPERATIONS:"
    echo "  iza status                     - Empire status report"
    echo "  iza interactive                - Interactive mode"
    echo ""
    echo "⚙️  SETUP:"
    echo "  iza --setup                    - Configure global commands"
    echo ""
    echo "💡 Quick Start:"
    echo "  1. Run: iza --setup"
    echo "  2. Restart terminal"
    echo "  3. Try: iza demo-app 'todo app with AI suggestions'"
    echo ""
    exit 0
fi

# Run the CLI with provided arguments
run_iza_cli "$@"
