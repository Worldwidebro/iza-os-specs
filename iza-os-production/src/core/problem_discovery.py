"""
IZA OS Problem Discovery
Scans for global problems and business opportunities
"""

import asyncio
from typing import Dict, Any, List
import logging


class ProblemDiscovery:
    """
    System for discovering problems and business opportunities
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.running = False
        self.discovered_problems = []
    
    async def start(self) -> None:
        """Start problem discovery system"""
        self.logger.info("Starting Problem Discovery...")
        
        # Simulate starting discovery services
        await asyncio.sleep(0.1)
        
        self.running = True
        self.logger.info("Problem Discovery started successfully")
    
    async def stop(self) -> None:
        """Stop problem discovery system"""
        self.logger.info("Stopping Problem Discovery...")
        
        self.running = False
        self.logger.info("Problem Discovery stopped")
    
    async def scan_problems(self, pain_threshold: float = 0.7, limit: int = 10) -> List[Dict[str, Any]]:
        """Scan for problems meeting the pain threshold"""
        if not self.running:
            raise RuntimeError("Problem Discovery not running")
        
        self.logger.info(f"Scanning for problems with pain threshold: {pain_threshold}")
        
        # Mock problem data
        mock_problems = [
            {
                "id": "prob_001",
                "title": "Small businesses struggle with inventory tracking",
                "pain_score": 0.87,
                "market_size": 150000,
                "solvability": "High",
                "source": "Reddit"
            },
            {
                "id": "prob_002", 
                "title": "Students need better math visualization tools",
                "pain_score": 0.73,
                "market_size": 50000,
                "solvability": "Medium",
                "source": "GitHub"
            },
            {
                "id": "prob_003",
                "title": "Remote teams lack async communication structure",
                "pain_score": 0.69,
                "market_size": 200000,
                "solvability": "High",
                "source": "Twitter"
            },
            {
                "id": "prob_004",
                "title": "Freelancers can't track time across projects",
                "pain_score": 0.66,
                "market_size": 80000,
                "solvability": "High",
                "source": "ProductHunt"
            },
            {
                "id": "prob_005",
                "title": "Parents struggle with kids' screen time",
                "pain_score": 0.61,
                "market_size": 300000,
                "solvability": "Medium",
                "source": "Reddit"
            }
        ]
        
        # Filter by pain threshold and limit
        filtered_problems = [
            p for p in mock_problems 
            if p["pain_score"] >= pain_threshold
        ][:limit]
        
        self.discovered_problems.extend(filtered_problems)
        
        return filtered_problems
    
    def get_status(self) -> Dict[str, Any]:
        """Get problem discovery status"""
        enabled_sources = self.config.get("enabled_sources", {})
        
        return {
            "running": self.running,
            "total_discovered": len(self.discovered_problems),
            "enabled_sources": [k for k, v in enabled_sources.items() if v],
            "pain_threshold": self.config.get("pain_threshold", 0.7),
            "scan_interval": self.config.get("scan_interval", 60)
        }
