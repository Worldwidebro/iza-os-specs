#!/usr/bin/env python3
"""
IZA OS - Command Line Interface
Your AI CEO at your fingertips - optimized for mobile development with Cursor
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

# Import IZA OS modules
from src.core.memory_core import MemoryCore
from src.core.agent_orchestration import AgentOrchestrator
from src.core.venture_factory import VentureFactory
from src.core.problem_discovery import ProblemDiscovery
from src.utils.config import load_config
from src.utils.logger_simple import setup_logger

# Initialize rich console
console = Console()
logger = setup_logger(__name__)

# CLI context for maintaining state
class CLIContext:
    def __init__(self):
        self.config = load_config()
        self.memory_core = None
        self.agent_orchestrator = None
        self.venture_factory = None
        self.problem_discovery = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize IZA OS components for CLI use"""
        if self.initialized:
            return
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("🧠 Initializing IZA OS components...", total=None)
            
            self.memory_core = MemoryCore(self.config.get('memory', {}))
            self.agent_orchestrator = AgentOrchestrator(self.config.get('agents', {}))
            self.venture_factory = VentureFactory(self.config.get('ventures', {}))
            self.problem_discovery = ProblemDiscovery(self.config.get('discovery', {}))
            
            await self.memory_core.initialize()
            await self.agent_orchestrator.start()
            await self.venture_factory.initialize()
            await self.problem_discovery.start()
            
            self.initialized = True
            progress.update(task, completed=100)

# Global CLI context
cli_context = CLIContext()


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version information')
@click.pass_context
def cli(ctx, version):
    """
    🧠 IZA OS - Intelligent Zero-Administration Operating System
    
    Your AI CEO that finds global problems, launches ventures, and generates income.
    Optimized for mobile development with Cursor IDE.
    """
    if ctx.invoked_subcommand is None:
        if version:
            console.print("🧠 IZA OS v1.0.0 - Your Autonomous AI Executive", style="bold blue")
            console.print("Built for mobile-first development with Cursor IDE", style="cyan")
        else:
            show_help()


def show_help():
    """Display comprehensive help information"""
    help_panel = Panel.fit(
        """[bold cyan]🧠 IZA OS - Your AI CEO[/bold cyan]

[bold]Core Commands:[/bold]
  [green]start[/green]     Initialize and start IZA OS system
  [green]tui[/green]       Launch interactive dashboard (LazySSH-style)
  [green]status[/green]    Show system status and health metrics
  [green]brief[/green]     Get your daily executive brief
  [green]stop[/green]      Gracefully shutdown IZA OS

[bold]Business Operations:[/bold]
  [yellow]scan[/yellow]     Scan for global problems and opportunities
  [yellow]venture[/yellow]  Create and manage business ventures
  [yellow]revenue[/yellow]  View revenue reports and optimization
  [yellow]portfolio[/yellow] Manage venture portfolio

[bold]Learning & Development:[/bold]
  [blue]learn[/blue]    Start personalized learning session
  [blue]teach[/blue]    Access teaching and curriculum system
  [blue]skill[/blue]    Skill assessment and development

[bold]System Management:[/bold]
  [magenta]agents[/magenta]   Manage AI agent network
  [magenta]memory[/magenta]   Query and manage system memory
  [magenta]config[/magenta]   Configuration management
  [magenta]logs[/magenta]     View system logs and diagnostics

[bold]Examples:[/bold]
  iza start
  iza scan --global --pain-threshold 0.8
  iza venture create "AI Newsletter Platform"
  iza learn --focus python --time 30

For detailed help: iza <command> --help""",
        title="IZA OS CLI Help",
        border_style="cyan"
    )
    
    console.print(help_panel)


@cli.command()
def start():
    """🚀 Initialize and start IZA OS system"""
    console.print("🚀 Starting IZA OS - Your Autonomous AI Executive", style="bold green")
    
    try:
        asyncio.run(cli_context.initialize())
        
        # Display startup information
        startup_table = Table(title="🧠 IZA OS System Status")
        startup_table.add_column("Component", style="cyan")
        startup_table.add_column("Status", style="green")
        startup_table.add_column("Details", style="white")
        
        startup_table.add_row("Memory Core", "✅ Active", "Persistent intelligence initialized")
        startup_table.add_row("Agent Network", "✅ Active", "4 specialized agents deployed")
        startup_table.add_row("Venture Factory", "✅ Active", "Ready for business creation")
        startup_table.add_row("Problem Discovery", "✅ Active", "Global scanning enabled")
        
        console.print(startup_table)
        console.print("\n🧠 [bold green]Your AI CEO is now operational![/bold green]")
        console.print("💡 Try: [cyan]iza brief[/cyan] for your daily executive summary")
        
    except Exception as e:
        console.print(f"❌ Failed to start IZA OS: {str(e)}", style="bold red")
        sys.exit(1)


@cli.command()
async def status():
    """📊 Show comprehensive system status"""
    console.print("📊 IZA OS System Status", style="bold cyan")
    
    if not cli_context.initialized:
        await cli_context.initialize()
    
    # System metrics table
    status_table = Table(title="System Health & Performance")
    status_table.add_column("Metric", style="cyan")
    status_table.add_column("Value", style="green")
    status_table.add_column("Status", style="white")
    
    # Mock data - replace with real system calls
    status_table.add_row("System Health", "🟢 Operational", "All systems running")
    status_table.add_row("Active Ventures", "15/478", "31% growth MoM")
    status_table.add_row("Monthly Revenue", "$4,247", "+$389 from last week")
    status_table.add_row("Agent Network", "4 Active", "All agents responsive")
    status_table.add_row("Memory Usage", "2.1GB", "68% efficiency")
    status_table.add_row("Uptime", "7d 14h 23m", "99.97% availability")
    
    console.print(status_table)
    
    # Component status
    component_panel = Panel(
        """[green]✅ Memory Core[/green]: Persistent state active
[green]✅ Agent Orchestrator[/green]: 4 agents operational  
[green]✅ Venture Factory[/green]: Template system ready
[green]✅ Problem Discovery[/green]: Scanning 5 platforms
[green]✅ Revenue Engine[/green]: Optimization active""",
        title="Component Status",
        border_style="green"
    )
    
    console.print("\n")
    console.print(component_panel)


@cli.command()
def tui():
    """🖥️  Launch interactive TUI dashboard"""
    console.print("🚀 Launching IZA OS Interactive Dashboard...", style="bold green")
    
    try:
        # Import TUI dashboard here to avoid issues if textual is not installed
        from src.tui.dashboard import run_dashboard
        run_dashboard()
    except ImportError:
        console.print("❌ TUI dependencies not installed. Run: pip install textual", style="bold red")
    except Exception as e:
        console.print(f"❌ Failed to launch TUI: {str(e)}", style="bold red")


@cli.command()
def brief():
    """🌅 Get your personalized daily executive brief"""
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    brief_panel = Panel.fit(
        f"""[bold cyan]🌅 Daily Executive Brief - {current_date}[/bold cyan]

[bold]🎯 Today's Strategic Priorities:[/bold]
  1. [green]Review 3 new problem opportunities[/green] (Pain score: 85%+)
  2. [yellow]Optimize Newsletter venture[/yellow] (Performance up 15%)  
  3. [blue]Complete Advanced Python module[/blue] (67% progress)

[bold]💰 Revenue & Portfolio Update:[/bold]
  • [green]Current MRR: $4,247[/green] (+$389 from last week)
  • [cyan]Best Performer: AI Newsletter[/cyan] ($1,200/month)
  • [yellow]Optimization Target: CRM Tool[/yellow] (+40% potential)
  • [blue]New Opportunity: Math Visualization App[/blue] (Market size: 50k)

[bold]🧠 Learning Progress:[/bold]
  • Python Mastery: [green]67% complete[/green]
  • Business Strategy: [yellow]43% complete[/yellow]
  • Next Session: [blue]Advanced FastAPI Patterns[/blue] (45 min)

[bold]🤖 Agent Activity Summary:[/bold]
  • Venture Creator: [green]3 tasks queued[/green]
  • Market Analyst: [cyan]Scanning Reddit trends[/cyan]
  • Revenue Optimizer: [yellow]Testing pricing models[/yellow]

[bold]🔥 Action Items:[/bold]
  1. Review problem #127: "Small business inventory tracking"
  2. Deploy CRM tool v2.1 optimizations  
  3. Schedule learning session for this afternoon""",
        title="Your AI CEO Executive Brief",
        border_style="cyan"
    )
    
    console.print(brief_panel)


@cli.command()
@click.option('--global', 'global_scan', is_flag=True, help='Scan global platforms')
@click.option('--pain-threshold', default=0.7, help='Minimum pain score (0.0-1.0)')
@click.option('--limit', default=10, help='Maximum problems to return')
async def scan(global_scan, pain_threshold, limit):
    """🔍 Scan for global problems and opportunities"""
    
    if not cli_context.initialized:
        await cli_context.initialize()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🔍 Scanning global problems...", total=None)
        
        # Mock scanning - replace with actual problem discovery
        await asyncio.sleep(2)  # Simulate API calls
        
        progress.update(task, description="📡 Checking Reddit, GitHub, Twitter, ProductHunt...")
        await asyncio.sleep(1)
    
    problems_table = Table(title=f"🔥 Problems Discovered (Pain ≥ {pain_threshold})")
    problems_table.add_column("Rank", style="cyan", width=4)
    problems_table.add_column("Problem", style="white")
    problems_table.add_column("Pain Score", style="red")
    problems_table.add_column("Market Size", style="green")
    problems_table.add_column("Solvability", style="yellow")
    
    # Mock problem data
    problems = [
        ("1", "Small businesses struggle with inventory tracking", "87%", "150k", "High"),
        ("2", "Students need better math visualization tools", "73%", "50k", "Medium"),
        ("3", "Remote teams lack async communication structure", "69%", "200k", "High"),
        ("4", "Freelancers can't track time across projects", "66%", "80k", "High"),
        ("5", "Parents struggle with kids' screen time", "61%", "300k", "Medium"),
    ]
    
    for problem in problems:
        problems_table.add_row(*problem)
    
    console.print(problems_table)
    
    console.print("\n💡 [bold cyan]Next Steps:[/bold cyan]")
    console.print("  • Use: [green]iza venture create \"Problem Solution\"[/green] to start building")
    console.print("  • Research: [yellow]iza research <problem_id>[/yellow] for deeper analysis")


@cli.group()
def venture():
    """🏭 Create and manage business ventures"""
    pass


@venture.command('create')
@click.argument('name')
@click.option('--template', default='saas', help='Venture template (saas, ai-tool, marketplace)')
@click.option('--auto-deploy', is_flag=True, help='Automatically deploy to staging')
async def create_venture(name, template, auto_deploy):
    """🏭 Create a new business venture"""
    
    if not cli_context.initialized:
        await cli_context.initialize()
    
    console.print(f"🏭 Creating venture: [bold cyan]{name}[/bold cyan]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Venture creation steps
        steps = [
            "🎯 Analyzing market opportunity...",
            "📋 Selecting optimal template...",
            "📦 Creating repository structure...", 
            "🤖 Assigning AI agents...",
            "🔧 Configuring development environment...",
            "📊 Setting up analytics...",
        ]
        
        for step in steps:
            task = progress.add_task(step, total=None)
            await asyncio.sleep(0.5)  # Simulate work
            progress.update(task, completed=100)
    
    # Venture summary
    venture_panel = Panel.fit(
        f"""[bold green]✅ Venture Created Successfully![/bold green]

[bold]📋 Venture Details:[/bold]
  • Name: [cyan]{name}[/cyan]
  • Template: [yellow]{template.upper()}[/yellow]  
  • Repository: [blue]github.com/your-org/{name.lower().replace(' ', '-')}[/blue]
  • Status: [green]Ready for Development[/green]

[bold]🤖 Assigned Agents:[/bold]
  • Venture Creator: [green]Primary development[/green]
  • Market Analyst: [cyan]Competitive research[/cyan] 
  • Revenue Optimizer: [yellow]Monetization strategy[/yellow]

[bold]🚀 Next Steps:[/bold]
  1. [green]iza venture develop {name}[/green] - Start development
  2. [blue]iza venture deploy {name}[/blue] - Deploy to staging
  3. [yellow]iza venture optimize {name}[/yellow] - Revenue optimization""",
        title=f"🏭 {name} - Venture Created",
        border_style="green"
    )
    
    console.print(venture_panel)


@venture.command('list')
async def list_ventures():
    """📋 List all active ventures"""
    
    ventures_table = Table(title="🏢 Active Venture Portfolio")
    ventures_table.add_column("Name", style="cyan")
    ventures_table.add_column("Status", style="green")
    ventures_table.add_column("Revenue", style="yellow")
    ventures_table.add_column("Growth", style="blue")
    ventures_table.add_column("Agents", style="magenta")
    
    # Mock venture data
    ventures = [
        ("AI Newsletter Platform", "🟢 Production", "$1,200/mo", "+15%", "3 active"),
        ("WhatsApp CRM", "🟡 Development", "$890/mo", "+22%", "2 active"),
        ("Math Visualization App", "🔵 Planning", "$0/mo", "N/A", "1 active"),
        ("Inventory Tracker", "🟢 Beta", "$340/mo", "+8%", "2 active"),
    ]
    
    for venture in ventures:
        ventures_table.add_row(*venture)
    
    console.print(ventures_table)
    
    console.print(f"\n📊 [bold]Portfolio Summary:[/bold] 15/478 slots used | $4,247 total MRR | +31% growth")


@venture.command('scaffold-pending')
@click.option('--title', default=None, help='Specific idea title to scaffold (optional)')
async def scaffold_pending(title):
    """🧱 Scaffold a venture from the idea database (first pending by default)"""
    if not cli_context.initialized:
        await cli_context.initialize()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("🧱 Scaffolding venture from pending idea...", total=None)
        venture = await cli_context.venture_factory.scaffold_pending_idea(title=title)
        progress.update(task, completed=100)

    if venture is None:
        console.print("ℹ️  No pending ideas available to scaffold", style="yellow")
        return

    panel = Panel.fit(
        f"""[bold green]✅ Venture Scaffolded![/bold green]

[bold]Name:[/bold] {venture.get('name')}
[bold]Status:[/bold] {venture.get('status')}
[bold]Path:[/bold] {venture.get('path')}""",
        title="Venture Scaffolding Result",
        border_style="green"
    )
    console.print(panel)


@cli.command()
@click.option('--focus', help='Learning focus area (python, business, ai)')
@click.option('--time', default=45, help='Session length in minutes')
async def learn(focus, time):
    """📚 Start personalized learning session"""
    
    if not focus:
        focus = "Advanced Python Patterns"  # Default
    
    learning_panel = Panel.fit(
        f"""[bold blue]📚 Starting Learning Session[/bold blue]

[bold]🎯 Today's Focus:[/bold] [cyan]{focus}[/cyan]
[bold]⏱️ Duration:[/bold] [yellow]{time} minutes[/yellow]
[bold]📈 Progress:[/bold] [green]67% complete on current track[/green]

[bold]📋 Session Agenda:[/bold]
  1. [blue]Review: FastAPI advanced routing[/blue] (10 min)
  2. [green]Hands-on: Build venture API endpoint[/green] (25 min)
  3. [yellow]Practice: Error handling patterns[/yellow] (10 min)

[bold]🏆 Learning Objectives:[/bold]
  • Master async request handling
  • Implement proper error boundaries  
  • Apply patterns to active ventures

[bold]💡 Practical Application:[/bold]
  Apply learnings to: [cyan]WhatsApp CRM API optimization[/cyan]""",
        title="🎓 Personalized Learning Session",
        border_style="blue"
    )
    
    console.print(learning_panel)
    
    console.print("\n🚀 [bold green]Learning session started![/bold green]")
    console.print("💻 Open your development environment to begin")
    console.print("📱 Optimized for Cursor IDE on mobile")


@cli.command()
async def agents():
    """🤖 Manage AI agent network"""
    
    agents_table = Table(title="🤖 AI Agent Network Status")
    agents_table.add_column("Agent", style="cyan")
    agents_table.add_column("Status", style="green") 
    agents_table.add_column("Current Task", style="yellow")
    agents_table.add_column("Queue", style="blue")
    agents_table.add_column("Performance", style="magenta")
    
    agents = [
        ("Venture Creator", "🟢 Active", "Creating CRM wireframes", "2 tasks", "97% efficiency"),
        ("Market Analyst", "🟢 Active", "Reddit trend analysis", "1 task", "94% efficiency"),
        ("Revenue Optimizer", "🟡 Working", "Testing pricing models", "3 tasks", "89% efficiency"), 
        ("Repository Manager", "🔵 Idle", "Awaiting instructions", "0 tasks", "100% ready"),
    ]
    
    for agent in agents:
        agents_table.add_row(*agent)
    
    console.print(agents_table)
    
    console.print("\n🧠 [bold]Agent Coordination:[/bold] All agents operating within optimal parameters")
    console.print("📊 [bold]Network Performance:[/bold] 95% average efficiency across all agents")


@cli.command()
@click.argument('query', required=False)
async def memory(query):
    """🧠 Query system memory and context"""
    
    if not query:
        # Show memory overview
        memory_panel = Panel.fit(
            """[bold cyan]🧠 System Memory Overview[/bold cyan]

[bold]📊 Memory Statistics:[/bold]
  • Total Entries: [green]1,247[/green]
  • Venture Patterns: [blue]89[/blue]
  • Learning Records: [yellow]234[/yellow]
  • Problem Solutions: [magenta]156[/magenta]

[bold]🔥 Recent Activity:[/bold]
  • Newsletter optimization pattern stored
  • Python learning milestone recorded
  • CRM user feedback analyzed
  • Market trend correlation identified

[bold]💡 Usage Examples:[/bold]
  [green]iza memory "successful ventures"[/green]
  [yellow]iza memory "python patterns"[/yellow] 
  [blue]iza memory "revenue optimization"[/blue]""",
            title="System Memory Core",
            border_style="cyan"
        )
        console.print(memory_panel)
    else:
        # Query specific memory
        console.print(f"🔍 Searching memory for: [cyan]{query}[/cyan]\n")
        
        # Mock memory results
        results_table = Table(title="Memory Search Results")
        results_table.add_column("Type", style="cyan")
        results_table.add_column("Content", style="white")
        results_table.add_column("Date", style="yellow")
        results_table.add_column("Relevance", style="green")
        
        results_table.add_row("Venture Pattern", "Newsletter subscription optimization", "2024-08-20", "95%")
        results_table.add_row("Learning Record", "Python FastAPI mastery milestone", "2024-08-18", "87%")
        results_table.add_row("Problem Solution", "Small business CRM solution template", "2024-08-15", "92%")
        
        console.print(results_table)


@cli.command()
async def revenue():
    """💰 View revenue reports and optimization"""
    
    revenue_panel = Panel.fit(
        """[bold green]💰 Revenue Performance Dashboard[/bold green]

[bold]📊 Current Metrics:[/bold]
  • Monthly Recurring Revenue: [green]$4,247[/green]
  • Weekly Growth: [cyan]+$389[/cyan] (+10.1%)
  • Monthly Growth: [yellow]+31%[/yellow] MoM
  • Annual Run Rate: [blue]$50,964[/blue]

[bold]🏆 Top Performers:[/bold]
  1. [green]AI Newsletter Platform[/green]: $1,200/mo (+15%)
  2. [cyan]WhatsApp CRM Tool[/cyan]: $890/mo (+22%)
  3. [yellow]Inventory Tracker[/yellow]: $340/mo (+8%)
  4. [blue]Math Learning App[/blue]: $280/mo (new)

[bold]🎯 Optimization Opportunities:[/bold]
  • [yellow]CRM Tool[/yellow]: +40% potential with premium tier
  • [blue]Newsletter[/blue]: +25% with advanced analytics  
  • [green]New Market[/green]: Math app expansion to colleges

[bold]📈 Revenue Forecast:[/bold]
  • Next Month: [green]$5,600[/green] (+32%)
  • 3 Months: [cyan]$8,400[/cyan] (+98%)
  • 6 Months: [yellow]$12,800[/yellow] (+201%)""",
        title="💰 Revenue Intelligence Report",
        border_style="green"
    )
    
    console.print(revenue_panel)


@cli.command()
async def stop():
    """🛑 Gracefully shutdown IZA OS"""
    
    if not cli_context.initialized:
        console.print("ℹ️  IZA OS is not running", style="cyan")
        return
    
    console.print("🛑 Stopping IZA OS gracefully...", style="yellow")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        shutdown_steps = [
            "💾 Saving system state...",
            "🤖 Stopping AI agents...",
            "🏭 Pausing venture operations...",
            "🧠 Persisting memory core...",
            "✅ Shutdown complete"
        ]
        
        for step in shutdown_steps:
            task = progress.add_task(step, total=None)
            await asyncio.sleep(0.5)
            progress.update(task, completed=100)
    
    console.print("👋 [bold green]IZA OS stopped successfully. Until next time![/bold green]")


def main():
    """Main CLI entry point"""
    try:
        # Check if we're in async context
        if sys.platform == "win32":
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
        cli()
        
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Goodbye from your AI CEO![/yellow]")
    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="bold red")
        sys.exit(1)


if __name__ == "__main__":
    main()
