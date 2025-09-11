"""
GitToDoc synchronization utilities
"""

import asyncio
import httpx
import json
from typing import Dict, List, Any
from pathlib import Path

class GitToDocClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.gittodoc.com/v1"
        
    async def create_project(self, repo_url: str, name: str, 
                           description: str = None) -> Dict[str, Any]:
        """Create a new GitToDoc project"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/projects",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "repository_url": repo_url,
                    "name": name,
                    "description": description or f"Auto-generated docs for {name}",
                    "auto_sync": True,
                    "build_settings": {
                        "include_readme": True,
                        "include_code_comments": True,
                        "generate_api_docs": True,
                        "custom_sections": [
                            "Installation",
                            "Usage",
                            "API Reference",
                            "Examples"
                        ]
                    }
                }
            )
            
            if response.status_code in [200, 201]:
                return {"success": True, **response.json()}
            else:
                return {"success": False, "error": response.text}
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """List all GitToDoc projects"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/projects",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code == 200:
                return response.json().get("projects", [])
            return []
    
    async def sync_project(self, project_id: str) -> Dict[str, Any]:
        """Manually trigger project sync"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/projects/{project_id}/sync",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code == 200:
                return {"success": True, **response.json()}
            else:
                return {"success": False, "error": response.text}
    
    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get project build/sync status"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/projects/{project_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code == 200:
                return response.json()
            return {}

async def bulk_sync_repositories(api_key: str, repositories: List[Dict[str, Any]]):
    """Sync multiple repositories to GitToDoc"""
    client = GitToDocClient(api_key)
    results = []
    
    for repo in repositories:
        print(f"🔄 Syncing {repo['name']} to GitToDoc...")
        
        result = await client.create_project(
            repo_url=repo["url"],
            name=repo["name"],
            description=repo.get("description")
        )
        
        if result.get("success"):
            print(f"✅ Successfully created GitToDoc project for {repo['name']}")
            print(f"📖 Documentation URL: {result.get('url')}")
        else:
            print(f"❌ Failed to create project for {repo['name']}: {result.get('error')}")
        
        results.append({
            "repo_name": repo["name"],
            "success": result.get("success", False),
            "url": result.get("url"),
            "error": result.get("error")
        })
        
        # Rate limiting
        await asyncio.sleep(1)
    
    return results
