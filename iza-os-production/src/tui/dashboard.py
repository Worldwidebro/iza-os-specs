#!/usr/bin/env python3
"""
IZA OS TUI Dashboard
Interactive Terminal User Interface inspired by LazySSH and K9s
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import (
    Header, Footer, DataTable, Static, Input, Button, 
    ListView, ListItem, Label, Log, TabbedContent, TabPane,
    ProgressBar, Sparkline
)
from textual.binding import Binding
from textual.reactive import reactive
from textual.message import Message
from textual import events
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text

# Import IZA OS modules
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from core.memory_core import MemoryCore
from core.agent_orchestration import AgentOrchestrator  
from core.venture_factory import VentureFactory
from core.problem_discovery import ProblemDiscovery
from utils.config import load_config
from utils.logger_simple import setup_logger


class IZADashboard(App):
    """
    IZA OS Interactive Dashboard - Your AI CEO Command Center
    """
    
    CSS = """
    Screen {
        background: $background;
    }
    
    Header {
        background: $primary;
        color: $text;
        height: 3;
    }
    
    Footer {
        background: $primary;
        color: $text;
        height: 3;
    }
    
    .container {
        background: $surface;
        border: solid $primary;
        padding: 1;
        margin: 1;
    }
    
    .status-good {
        color: $success;
        background: $success 10%;
    }
    
    .status-warning {
        color: $warning;  
        background: $warning 10%;
    }
    
    .status-error {
        color: $error;
        background: $error 10%;
    }
    
    .metric-card {
        height: 8;
        width: 1fr;
        border: solid $accent;
        padding: 1;
        margin: 1;
        background: $panel;
    }
    
    .agent-list {
        height: 100%;
        border: solid $accent;
        padding: 1;
        margin: 1;
    }
    
    .venture-list {
        height: 100%;
        border: solid $accent;
        padding: 1;
        margin: 1;
    }
    
    .logs {
        height: 100%;
        border: solid $accent;
        padding: 1;
        margin: 1;
        background: $panel;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("r", "refresh", "Refresh", priority=True),
        Binding("s", "scan", "Scan Problems"),
        Binding("v", "ventures", "Ventures"),
        Binding("a", "agents", "Agents"),
        Binding("m", "memory", "Memory"),
        Binding("b", "brief", "Brief"),
        Binding("h", "help", "Help"),
        Binding("1", "tab_overview", "Overview"),
        Binding("2", "tab_ventures", "Ventures"),
        Binding("3", "tab_agents", "Agents"),
        Binding("4", "tab_logs", "Logs"),
    ]
    
    # Reactive state
    current_tab = reactive("overview")
    system_status = reactive("initializing")
    agent_count = reactive(0)
    venture_count = reactive(0)
    revenue = reactive(0.0)
    
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.logger = setup_logger(__name__)
        self.iza_components_initialized = False
        
        # Mock data - replace with real data
        self.agents = [
            {"name": "Venture Creator", "status": "active", "task": "Creating CRM wireframes", "efficiency": 97},
            {"name": "Market Analyst", "status": "active", "task": "Reddit trend analysis", "efficiency": 94},
            {"name": "Revenue Optimizer", "status": "working", "task": "Testing pricing models", "efficiency": 89},
            {"name": "Repository Manager", "status": "idle", "task": "Awaiting instructions", "efficiency": 100},
        ]
        
        self.ventures = [
            {"name": "AI Newsletter Platform", "status": "production", "revenue": 1200, "growth": 15},
            {"name": "WhatsApp CRM", "status": "development", "revenue": 890, "growth": 22},
            {"name": "Math Visualization App", "status": "planning", "revenue": 0, "growth": 0},
            {"name": "Inventory Tracker", "status": "beta", "revenue": 340, "growth": 8},
        ]
        
        self.problems = [
            {"title": "Small businesses struggle with inventory tracking", "pain": 87, "market": 150000},
            {"title": "Students need better math visualization tools", "pain": 73, "market": 50000},
            {"title": "Remote teams lack async communication structure", "pain": 69, "market": 200000},
        ]
        
        self.system_logs = []
        self.revenue_history = [3800, 3900, 4000, 4100, 4247]  # Last 5 weeks

    def compose(self) -> ComposeResult:
        """Create the dashboard layout"""
        yield Header(show_clock=True, name="🧠 IZA OS - AI CEO Command Center")
        
        with TabbedContent(initial="overview"):
            with TabPane("📊 Overview", id="overview"):
                yield from self._compose_overview()
            
            with TabPane("🏭 Ventures", id="ventures"):
                yield from self._compose_ventures()
            
            with TabPane("🤖 Agents", id="agents"):
                yield from self._compose_agents()
                
            with TabPane("📝 Logs", id="logs"):
                yield from self._compose_logs()
        
        yield Footer()
    
    def _compose_overview(self) -> ComposeResult:
        """Compose the overview tab"""
        with Horizontal():
            # Metrics Cards
            with Vertical(classes="metric-card"):
                yield Static("💰 Monthly Revenue", classes="status-good")
                yield Static("$4,247", id="revenue-value")
                yield Static("+$389 (+10.1%)", classes="status-good")
                
            with Vertical(classes="metric-card"):
                yield Static("🏢 Active Ventures", classes="status-good")
                yield Static("15/478", id="venture-count")
                yield Static("+31% MoM", classes="status-good")
                
            with Vertical(classes="metric-card"):
                yield Static("🤖 AI Agents", classes="status-good")
                yield Static("4 Active", id="agent-count")
                yield Static("95% Efficiency", classes="status-good")
                
            with Vertical(classes="metric-card"):
                yield Static("📈 System Health", classes="status-good")
                yield Static("Operational", id="system-health")
                yield Static("99.97% Uptime", classes="status-good")
        
        with Horizontal():
            # Quick Agent Status
            with Vertical(classes="agent-list"):
                yield Static("🤖 Agent Status", classes="status-good")
                agent_table = DataTable()
                agent_table.add_columns("Agent", "Status", "Task", "Efficiency")
                for agent in self.agents:
                    status_class = "status-good" if agent["status"] == "active" else "status-warning"
                    agent_table.add_row(
                        agent["name"], 
                        agent["status"].title(),
                        agent["task"],
                        f"{agent['efficiency']}%"
                    )
                yield agent_table
            
            # Revenue Trend & Problems
            with Vertical(classes="venture-list"):
                yield Static("📈 Revenue Trend", classes="status-good")
                yield Sparkline(self.revenue_history, summary_function=max)
                yield Static("🔥 Top Problems", classes="status-warning")
                for i, problem in enumerate(self.problems[:3], 1):
                    yield Static(f"💡 {i}. {problem['title'][:40]}...", classes="status-warning")

    def _compose_ventures(self) -> ComposeResult:
        """Compose the ventures tab"""
        with Vertical():
            yield Static("🏢 Active Venture Portfolio", classes="status-good")
            
            venture_table = DataTable()
            venture_table.add_columns("Name", "Status", "Revenue/mo", "Growth", "Actions")
            
            for venture in self.ventures:
                status_emoji = {
                    "production": "🟢",
                    "development": "🟡", 
                    "planning": "🔵",
                    "beta": "🟠"
                }.get(venture["status"], "⚪")
                
                venture_table.add_row(
                    venture["name"],
                    f"{status_emoji} {venture['status'].title()}",
                    f"${venture['revenue']}/mo" if venture['revenue'] > 0 else "$0/mo",
                    f"+{venture['growth']}%" if venture['growth'] > 0 else "N/A",
                    "Deploy | Edit | Delete"
                )
            
            yield venture_table
            
            with Horizontal():
                yield Button("➕ Create Venture", id="create-venture")
                yield Button("📊 Analytics", id="venture-analytics") 
                yield Button("🚀 Deploy All", id="deploy-ventures")

    def _compose_agents(self) -> ComposeResult:
        """Compose the agents tab"""
        with Vertical():
            yield Static("🤖 AI Agent Network Status", classes="status-good")
            
            agent_table = DataTable()
            agent_table.add_columns("Agent", "Status", "Current Task", "Queue", "Performance", "Actions")
            
            for agent in self.agents:
                status_emoji = {
                    "active": "🟢",
                    "working": "🟡",
                    "idle": "🔵",
                    "error": "🔴"
                }.get(agent["status"], "⚪")
                
                agent_table.add_row(
                    agent["name"],
                    f"{status_emoji} {agent['status'].title()}",
                    agent["task"],
                    f"{hash(agent['name']) % 5} tasks",  # Mock queue
                    f"{agent['efficiency']}% efficiency",
                    "Configure | Stop | Logs"
                )
            
            yield agent_table
            
            with Horizontal():
                yield Button("🔄 Restart All", id="restart-agents")
                yield Button("⚙️ Configure", id="configure-agents")
                yield Button("📊 Performance", id="agent-performance")

    def _compose_logs(self) -> ComposeResult:
        """Compose the logs tab"""
        with Vertical():
            yield Static("📝 System Logs", classes="status-good")
            
            logs = Log(highlight=True)
            
            # Add some sample logs
            sample_logs = [
                "[2025-09-04 04:56:32] 🧠 [INFO] IZA OS initialized successfully",
                "[2025-09-04 04:56:33] 🤖 [INFO] Agent Orchestrator started with 4 agents",
                "[2025-09-04 04:56:34] 🏭 [INFO] Venture Factory ready for business creation",
                "[2025-09-04 04:56:35] 🔍 [INFO] Problem Discovery scanning 5 platforms",
                "[2025-09-04 04:56:36] 💰 [INFO] Revenue Engine optimization active",
                "[2025-09-04 04:56:37] 🧠 [INFO] Memory Core persistent state active",
                "[2025-09-04 04:56:38] 📊 [INFO] System health check: All systems operational",
            ]
            
            for log_entry in sample_logs:
                logs.write_line(log_entry)
            
            yield logs
            
            with Horizontal():
                yield Button("🔄 Refresh", id="refresh-logs")
                yield Button("📥 Export", id="export-logs")
                yield Button("🗑️ Clear", id="clear-logs")

    async def on_mount(self) -> None:
        """Initialize the dashboard when mounted"""
        await self._initialize_iza_components()
        self.set_interval(5.0, self._update_metrics)
        self._add_system_log("🧠 IZA OS Dashboard initialized")

    async def _initialize_iza_components(self) -> None:
        """Initialize IZA OS components"""
        try:
            self.system_status = "initializing"
            self._add_system_log("🔄 Initializing IZA OS components...")
            
            # Simulate component initialization
            await asyncio.sleep(1)
            
            self.iza_components_initialized = True
            self.system_status = "operational"
            self.agent_count = len(self.agents)
            self.venture_count = len(self.ventures)
            self.revenue = sum(v["revenue"] for v in self.ventures)
            
            self._add_system_log("✅ All IZA OS components initialized successfully")
            
        except Exception as e:
            self.system_status = "error"
            self._add_system_log(f"❌ Initialization failed: {str(e)}")

    def _update_metrics(self) -> None:
        """Update dashboard metrics periodically"""
        if not self.iza_components_initialized:
            return
            
        # Simulate metric updates
        current_time = datetime.now().strftime("%H:%M:%S")
        self._add_system_log(f"📊 [{current_time}] Metrics updated")
        
        # Update agent efficiency (simulate fluctuation)
        for agent in self.agents:
            if agent["status"] == "active":
                import random
                agent["efficiency"] = max(85, min(100, agent["efficiency"] + random.randint(-2, 2)))

    def _add_system_log(self, message: str) -> None:
        """Add a message to system logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.system_logs.append(log_entry)
        
        # Keep only last 100 logs
        if len(self.system_logs) > 100:
            self.system_logs = self.system_logs[-100:]

    # Action handlers
    async def action_refresh(self) -> None:
        """Refresh all data"""
        self._add_system_log("🔄 Refreshing dashboard data...")
        await self._initialize_iza_components()
        
    async def action_scan(self) -> None:
        """Trigger problem scan"""
        self._add_system_log("🔍 Starting global problem scan...")
        # Simulate scanning
        await asyncio.sleep(2)
        self._add_system_log("📊 Found 23 new problems worth investigating")
        
    async def action_ventures(self) -> None:
        """Focus on ventures tab"""
        self.current_tab = "ventures"
        
    async def action_agents(self) -> None:
        """Focus on agents tab"""
        self.current_tab = "agents"
        
    async def action_memory(self) -> None:
        """Query memory system"""
        self._add_system_log("🧠 Accessing system memory...")
        
    async def action_brief(self) -> None:
        """Generate executive brief"""
        self._add_system_log("📋 Generating daily executive brief...")
        
    async def action_help(self) -> None:
        """Show help"""
        self._add_system_log("❓ Help: Use q=quit, r=refresh, 1-4=tabs, s=scan")

    # Tab navigation
    async def action_tab_overview(self) -> None:
        """Switch to overview tab"""
        self.current_tab = "overview"
        
    async def action_tab_ventures(self) -> None:
        """Switch to ventures tab"""
        self.current_tab = "ventures"
        
    async def action_tab_agents(self) -> None:
        """Switch to agents tab"""
        self.current_tab = "agents"
        
    async def action_tab_logs(self) -> None:
        """Switch to logs tab"""
        self.current_tab = "logs"

    # Button handlers
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "create-venture":
            self._add_system_log("🏭 Creating new venture...")
        elif button_id == "restart-agents":
            self._add_system_log("🔄 Restarting all agents...")
        elif button_id == "refresh-logs":
            self._add_system_log("🔄 Logs refreshed")
        elif button_id == "clear-logs":
            self.system_logs.clear()
            self._add_system_log("🗑️ Logs cleared")

def run_dashboard():
    """Run the IZA OS TUI Dashboard"""
    app = IZADashboard()
    app.title = "IZA OS - AI CEO Dashboard"
    app.sub_title = "Your Autonomous AI Executive Command Center"
    app.run()

if __name__ == "__main__":
    run_dashboard()
