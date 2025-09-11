#!/usr/bin/env python3
"""
IZA OS - Main Application Entry Point
Intelligent Zero-Administration Operating System

This is the main entry point for the IZA OS system.
It initializes the core components and starts the autonomous AI executive system.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import IZA OS core modules
from src.core.memory_core import MemoryCore
from src.core.agent_orchestration import AgentOrchestrator
from src.core.venture_factory import VentureFactory
from src.core.command_center import CommandCenter
from src.core.problem_discovery import ProblemDiscovery
from src.utils.logger import setup_logger
from src.utils.config import load_config

# Set up logging
logger = setup_logger(__name__)

# Global app instance
app: Optional[FastAPI] = None
iza_system: Optional["IZASystem"] = None


class IZASystem:
    """
    Main IZA OS System Coordinator
    
    This class orchestrates all the core components of IZA OS and provides
    the main interface for system operations.
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.is_running = False
        
        # Initialize core components
        logger.info("🧠 Initializing IZA OS Core Components...")
        
        self.memory_core = MemoryCore(config.get('memory', {}))
        self.agent_orchestrator = AgentOrchestrator(config.get('agents', {}))
        self.venture_factory = VentureFactory(config.get('ventures', {}))
        self.command_center = CommandCenter(config.get('commands', {}))
        self.problem_discovery = ProblemDiscovery(config.get('discovery', {}))
        
        logger.info("✅ IZA OS Core Components Initialized")
    
    async def start(self):
        """Start the IZA OS system"""
        if self.is_running:
            logger.warning("⚠️  IZA OS is already running")
            return
        
        logger.info("🚀 Starting IZA OS - Your Autonomous AI Executive")
        
        try:
            # Start core components
            await self.memory_core.initialize()
            await self.agent_orchestrator.start()
            await self.venture_factory.initialize()
            await self.command_center.start()
            await self.problem_discovery.start()
            
            self.is_running = True
            
            logger.info("✅ IZA OS is now fully operational")
            logger.info("🧠 Your AI CEO is ready to revolutionize your business")
            
            # Perform initial system health check
            await self.health_check()
            
        except Exception as e:
            logger.error(f"❌ Failed to start IZA OS: {str(e)}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the IZA OS system gracefully"""
        if not self.is_running:
            logger.info("ℹ️  IZA OS is already stopped")
            return
        
        logger.info("🛑 Stopping IZA OS gracefully...")
        
        try:
            # Stop components in reverse order
            await self.problem_discovery.stop()
            await self.command_center.stop()
            await self.venture_factory.shutdown()
            await self.agent_orchestrator.stop()
            await self.memory_core.save_state()
            
            self.is_running = False
            logger.info("✅ IZA OS stopped successfully")
            
        except Exception as e:
            logger.error(f"❌ Error during IZA OS shutdown: {str(e)}")
            raise
    
    async def health_check(self) -> dict:
        """Perform comprehensive system health check"""
        logger.info("🔍 Performing system health check...")
        
        health_status = {
            "system": "IZA OS",
            "status": "operational",
            "timestamp": asyncio.get_event_loop().time(),
            "components": {}
        }
        
        # Check each component
        components = {
            "memory_core": self.memory_core,
            "agent_orchestrator": self.agent_orchestrator,
            "venture_factory": self.venture_factory,
            "command_center": self.command_center,
            "problem_discovery": self.problem_discovery
        }
        
        for name, component in components.items():
            try:
                if hasattr(component, 'health_check'):
                    component_health = await component.health_check()
                else:
                    component_health = {"status": "unknown"}
                
                health_status["components"][name] = component_health
                
            except Exception as e:
                logger.error(f"❌ Health check failed for {name}: {str(e)}")
                health_status["components"][name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Overall system status
        failed_components = [
            name for name, status in health_status["components"].items()
            if status.get("status") not in ["healthy", "operational"]
        ]
        
        if failed_components:
            health_status["status"] = "degraded"
            health_status["failed_components"] = failed_components
            logger.warning(f"⚠️  System health degraded: {failed_components}")
        else:
            logger.info("✅ All systems operational - IZA OS health check passed")
        
        return health_status
    
    async def get_status(self) -> dict:
        """Get current system status"""
        health = await self.health_check()
        
        # Add additional system metrics
        status = {
            **health,
            "uptime": asyncio.get_event_loop().time() if self.is_running else 0,
            "active_ventures": await self.venture_factory.get_active_count() if hasattr(self.venture_factory, 'get_active_count') else 0,
            "agent_count": await self.agent_orchestrator.get_agent_count() if hasattr(self.agent_orchestrator, 'get_agent_count') else 0,
            "memory_usage": await self.memory_core.get_usage_stats() if hasattr(self.memory_core, 'get_usage_stats') else {},
        }
        
        return status


def create_app(config: dict) -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title="IZA OS",
        description="Intelligent Zero-Administration Operating System - Your AI CEO",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get('cors', {}).get('origins', ["*"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=config.get('security', {}).get('allowed_hosts', ["*"])
    )
    
    return app


# FastAPI route handlers
@app.get("/")
async def root():
    """Root endpoint - IZA OS welcome"""
    return {
        "message": "🧠 Welcome to IZA OS - Your Intelligent AI Executive",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs"
    }


@app.get("/health")
async def health():
    """System health check endpoint"""
    if not iza_system:
        return JSONResponse(
            status_code=503,
            content={"status": "service_unavailable", "message": "IZA OS not initialized"}
        )
    
    health_status = await iza_system.health_check()
    status_code = 200 if health_status["status"] == "operational" else 503
    
    return JSONResponse(
        status_code=status_code,
        content=health_status
    )


@app.get("/status")
async def status():
    """Detailed system status endpoint"""
    if not iza_system:
        return JSONResponse(
            status_code=503,
            content={"status": "service_unavailable", "message": "IZA OS not initialized"}
        )
    
    return await iza_system.get_status()


@app.post("/start")
async def start_system():
    """Start IZA OS system"""
    global iza_system
    
    if not iza_system:
        return JSONResponse(
            status_code=503,
            content={"error": "IZA OS not initialized"}
        )
    
    if iza_system.is_running:
        return {"message": "IZA OS is already running", "status": "running"}
    
    try:
        await iza_system.start()
        return {"message": "IZA OS started successfully", "status": "running"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to start IZA OS: {str(e)}"}
        )


@app.post("/stop")
async def stop_system():
    """Stop IZA OS system"""
    global iza_system
    
    if not iza_system:
        return JSONResponse(
            status_code=503,
            content={"error": "IZA OS not initialized"}
        )
    
    try:
        await iza_system.stop()
        return {"message": "IZA OS stopped successfully", "status": "stopped"}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to stop IZA OS: {str(e)}"}
        )


async def handle_shutdown(signal_num: int):
    """Handle shutdown signals gracefully"""
    logger.info(f"📡 Received signal {signal_num}, initiating graceful shutdown...")
    
    if iza_system and iza_system.is_running:
        await iza_system.stop()
    
    # Stop the event loop
    loop = asyncio.get_event_loop()
    loop.stop()


def setup_signal_handlers():
    """Set up signal handlers for graceful shutdown"""
    if sys.platform != "win32":  # Unix-like systems
        loop = asyncio.get_event_loop()
        
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(
                sig,
                lambda s=sig: asyncio.create_task(handle_shutdown(s))
            )


async def main():
    """Main application entry point"""
    global app, iza_system
    
    logger.info("🚀 Initializing IZA OS - Intelligent Zero-Administration Operating System")
    
    # Load configuration
    config = load_config()
    
    # Initialize IZA OS system
    iza_system = IZASystem(config)
    
    # Create FastAPI app
    app = create_app(config)
    
    # Set up signal handlers
    setup_signal_handlers()
    
    # Start IZA OS system
    await iza_system.start()
    
    # Start web server
    server_config = config.get('server', {})
    host = server_config.get('host', '0.0.0.0')
    port = server_config.get('port', 3000)
    
    logger.info(f"🌐 Starting IZA OS web server on {host}:{port}")
    
    server_config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        reload=config.get('development', False)
    )
    
    server = uvicorn.Server(server_config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("⌨️  Keyboard interrupt received")
    finally:
        if iza_system:
            await iza_system.stop()


def run_cli():
    """Run IZA OS from command line"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # CLI mode - import and run CLI handler
        from src.cli import main as cli_main
        cli_main()
    else:
        # Web server mode
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("👋 IZA OS shutdown complete. Until next time!")
        except Exception as e:
            logger.error(f"❌ Fatal error: {str(e)}")
            sys.exit(1)


if __name__ == "__main__":
    run_cli()
