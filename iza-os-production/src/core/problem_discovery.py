"""
IZA OS Problem Discovery
Scans for global problems and business opportunities
"""

import asyncio
from typing import Dict, Any, List
import logging
import json
from pathlib import Path
from datetime import datetime


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
        
        # Persist as business ideas in the ideas database
        try:
            self._write_new_ideas_to_db(filtered_problems)
        except Exception as e:
            self.logger.error(f"Failed to write ideas to BUSINESS_IDEAS.json: {e}")
        
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

    # Internal utilities
    def _ideas_db_path(self) -> Path:
        # Place database at repository root
        return Path(__file__).resolve().parents[3] / "BUSINESS_IDEAS.json"

    def _load_existing_ideas(self) -> List[Dict[str, Any]]:
        ideas_path = self._ideas_db_path()
        if not ideas_path.exists():
            return []
        try:
            with ideas_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                # Support object format {"ideas": [...]} if present
                if isinstance(data, dict) and isinstance(data.get("ideas"), list):
                    return data.get("ideas", [])
        except Exception:
            # If corrupted, start fresh but do not raise
            return []
        return []

    def _save_ideas(self, ideas: List[Dict[str, Any]]) -> None:
        ideas_path = self._ideas_db_path()
        # Ensure parent exists
        ideas_path.parent.mkdir(parents=True, exist_ok=True)
        with ideas_path.open("w", encoding="utf-8") as f:
            json.dump(ideas, f, ensure_ascii=False, indent=2)

    def _write_new_ideas_to_db(self, problems: List[Dict[str, Any]]) -> None:
        existing = self._load_existing_ideas()
        existing_titles = {idea.get("title", "").strip().lower() for idea in existing}
        now_iso = datetime.utcnow().isoformat() + "Z"
        new_ideas: List[Dict[str, Any]] = []
        for p in problems:
            title = p.get("title", "").strip()
            if not title:
                continue
            if title.lower() in existing_titles:
                continue
            new_ideas.append({
                "title": title,
                "source": p.get("source", "unknown"),
                "pain_score": p.get("pain_score"),
                "status": "pending",
                "created_at": now_iso
            })
        if not new_ideas:
            return
        # Append and save
        existing.extend(new_ideas)
        self._save_ideas(existing)
