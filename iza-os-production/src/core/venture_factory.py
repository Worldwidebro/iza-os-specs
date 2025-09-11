"""
IZA OS Venture Factory
Creates and manages business ventures
"""

import asyncio
from typing import Dict, Any, List
import logging


class VentureFactory:
    """
    Factory for creating and managing business ventures
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.ventures = []
        self.initialized = False
    
    async def initialize(self) -> None:
        """Initialize venture factory"""
        self.logger.info("Initializing Venture Factory...")
        
        # Simulate initialization
        await asyncio.sleep(0.1)
        
        self.initialized = True
        self.logger.info("Venture Factory initialized successfully")
    
    async def create_venture(self, name: str, template: str = None) -> Dict[str, Any]:
        """Create a new venture"""
        if not self.initialized:
            raise RuntimeError("Venture Factory not initialized")
        
        template = template or self.config.get("default_template", "saas")
        
        venture = {
            "id": f"venture_{len(self.ventures) + 1}",
            "name": name,
            "template": template,
            "status": "created",
            "revenue": 0.0
        }
        
        self.ventures.append(venture)
        self.logger.info(f"Created venture: {name} (ID: {venture['id']})")
        
        return venture
    
    def get_ventures(self) -> List[Dict[str, Any]]:
        """Get all ventures"""
        return self.ventures.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """Get venture factory status"""
        total_revenue = sum(venture.get("revenue", 0) for venture in self.ventures)
        
        return {
            "initialized": self.initialized,
            "total_ventures": len(self.ventures),
            "max_concurrent": self.config.get("max_concurrent", 0),
            "total_revenue": total_revenue,
            "templates_path": self.config.get("templates_path", "unknown")
        }
