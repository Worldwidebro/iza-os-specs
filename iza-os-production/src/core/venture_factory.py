"""
IZA OS Venture Factory
Creates and manages business ventures
"""

import asyncio
from typing import Dict, Any, List, Optional
import logging
import json
import subprocess
from pathlib import Path
from datetime import datetime
import shutil


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

    # Methods referenced by main.py (stubs)
    async def shutdown(self) -> None:
        self.initialized = False

    async def get_active_count(self) -> int:
        return len(self.ventures)

    # Idea database integration
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
                if isinstance(data, dict) and isinstance(data.get("ideas"), list):
                    return data.get("ideas", [])
        except Exception:
            return []
        return []

    def _save_ideas(self, ideas: List[Dict[str, Any]]) -> None:
        ideas_path = self._ideas_db_path()
        ideas_path.parent.mkdir(parents=True, exist_ok=True)
        with ideas_path.open("w", encoding="utf-8") as f:
            json.dump(ideas, f, ensure_ascii=False, indent=2)

    def get_pending_ideas(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        ideas = self._load_existing_ideas()
        pending = [i for i in ideas if i.get("status") in ("pending", "new")]
        if limit is not None:
            return pending[:limit]
        return pending

    def _update_idea_status(self, title: str, status: str, extra: Optional[Dict[str, Any]] = None) -> None:
        ideas = self._load_existing_ideas()
        updated = False
        for idea in ideas:
            if idea.get("title", "").strip().lower() == title.strip().lower():
                idea["status"] = status
                if extra:
                    idea.update(extra)
                updated = True
                break
        if updated:
            self._save_ideas(ideas)

    async def scaffold_pending_idea(self, title: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Scaffold a venture from the first pending idea (or matching title).

        Returns the scaffolded venture metadata if successful, else None.
        """
        if not self.initialized:
            raise RuntimeError("Venture Factory not initialized")

        idea_to_use: Optional[Dict[str, Any]] = None
        if title:
            for idea in self._load_existing_ideas():
                if idea.get("status") in ("pending", "new") and idea.get("title", "").strip().lower() == title.strip().lower():
                    idea_to_use = idea
                    break
        else:
            pending = self.get_pending_ideas(limit=1)
            idea_to_use = pending[0] if pending else None

        if not idea_to_use:
            self.logger.info("No pending ideas found to scaffold")
            return None

        idea_title = idea_to_use.get("title", "New Venture")
        slug = idea_title.lower().replace(" ", "-")
        ventures_root = Path(__file__).resolve().parents[3] / "companies"
        target_dir = ventures_root / slug
        target_dir.mkdir(parents=True, exist_ok=True)

        # Mark as in-progress
        self._update_idea_status(idea_title, "scaffolding_started", {"scaffolding_started_at": datetime.utcnow().isoformat() + "Z"})

        # Try to run claudable via npx if available
        venture_meta: Dict[str, Any] = {
            "id": f"venture_{len(self.ventures) + 1}",
            "name": idea_title,
            "template": self.config.get("default_template", "saas"),
            "status": "scaffolding",
            "revenue": 0.0,
            "path": str(target_dir)
        }

        npx_path = shutil.which("npx")
        try:
            if npx_path is not None:
                cmd = [npx_path, "-y", "claudable@latest"]
                subprocess.run(cmd, cwd=str(target_dir), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                venture_meta["status"] = "scaffolded"
                self._update_idea_status(idea_title, "scaffolded", {"scaffolded_at": datetime.utcnow().isoformat() + "Z", "project_path": str(target_dir)})
            else:
                # If npx not available, simulate scaffolding
                readme = target_dir / "README.md"
                if not readme.exists():
                    readme.write_text(f"# {idea_title}\n\nScaffolded project placeholder.", encoding="utf-8")
                venture_meta["status"] = "scaffolded (simulated)"
                self._update_idea_status(idea_title, "scaffolded", {"scaffolded_at": datetime.utcnow().isoformat() + "Z", "project_path": str(target_dir), "note": "npx not found, scaffold simulated"})
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Scaffolding failed: {e}")
            self._update_idea_status(idea_title, "error", {"error_message": str(e), "failed_at": datetime.utcnow().isoformat() + "Z"})
            return None

        # Track in-memory venture as well
        self.ventures.append(venture_meta)
        return venture_meta
