#!/usr/bin/env python3
"""
FastAPI-based Repository MCP Server
Provides HTTP endpoints for repository management
"""

import asyncio
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import httpx
import git
from dataclasses import dataclass, asdict
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

@dataclass
class Repository:
    name: str
    full_name: str
    url: str
    local_path: Optional[str] = None
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    last_updated: Optional[str] = None
    topics: List[str] = None
    is_fork: bool = False
    default_branch: str = "main"
    gittodoc_url: Optional[str] = None
    
    def __post_init__(self):
        if self.topics is None:
            self.topics = []

class RepositoryMCPServer:
    def __init__(self, config_path: str = "mcp_config.yaml"):
        self.config = self._load_config(config_path)
        self.repositories: Dict[str, Repository] = {}
        self.github_client = httpx.AsyncClient(
            headers={"Authorization": f"token {self.config['github_token']}"}
        )
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        default_config = {
            "github_token": os.getenv("GITHUB_TOKEN"),
            "gittodoc_api_key": os.getenv("GITTODOC_API_KEY"),
            "local_repos_path": "~/repositories",
            "neo4j": {
                "uri": "bolt://localhost:7687",
                "user": "neo4j",
                "password": os.getenv("NEO4J_PASSWORD")
            },
            "embedding": {
                "model": "text-embedding-3-small",
                "api_key": os.getenv("OPENAI_API_KEY")
            },
            "sync_settings": {
                "auto_clone": True,
                "auto_gittodoc": False,
                "include_private": True,
                "exclude_patterns": [".git", "node_modules", "__pycache__"]
            }
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config

    async def list_repositories(self, owner: Optional[str] = None, 
                               include_local: bool = True) -> List[Dict[str, Any]]:
        """List all repositories (GitHub + local)"""
        repos = []
        
        # GitHub repositories
        if owner:
            github_repos = await self._fetch_github_repos(owner)
            repos.extend(github_repos)
        
        # Local repositories
        if include_local:
            local_repos = await self._scan_local_repos()
            repos.extend(local_repos)
            
        return [asdict(repo) for repo in repos]

    async def _fetch_github_repos(self, owner: str) -> List[Repository]:
        """Fetch repositories from GitHub API"""
        repos = []
        page = 1
        
        while True:
            try:
                response = await self.github_client.get(
                    f"https://api.github.com/users/{owner}/repos",
                    params={"page": page, "per_page": 100, "type": "all"}
                )
                
                if response.status_code != 200:
                    break
                    
                data = response.json()
                if not data:
                    break
                
                for repo_data in data:
                    repo = Repository(
                        name=repo_data["name"],
                        full_name=repo_data["full_name"],
                        url=repo_data["clone_url"],
                        description=repo_data.get("description"),
                        language=repo_data.get("language"),
                        stars=repo_data["stargazers_count"],
                        forks=repo_data["forks_count"],
                        last_updated=repo_data["updated_at"],
                        topics=repo_data.get("topics", []),
                        is_fork=repo_data["fork"],
                        default_branch=repo_data["default_branch"]
                    )
                    
                    repos.append(repo)
                    self.repositories[repo.name] = repo
                
                page += 1
            except Exception as e:
                print(f"Error fetching GitHub repos: {e}")
                break
        
        return repos

    async def _scan_local_repos(self) -> List[Repository]:
        """Scan local directory for Git repositories"""
        repos = []
        base_path = Path(self.config["local_repos_path"]).expanduser()
        
        if not base_path.exists():
            return repos
        
        for item in base_path.iterdir():
            if item.is_dir() and (item / ".git").exists():
                try:
                    repo = git.Repo(item)
                    
                    # Try to get remote URL
                    remote_url = None
                    if repo.remotes:
                        remote_url = repo.remotes.origin.url
                    
                    local_repo = Repository(
                        name=item.name,
                        full_name=f"local/{item.name}",
                        url=remote_url or str(item),
                        local_path=str(item),
                        last_updated=datetime.fromtimestamp(
                            item.stat().st_mtime
                        ).isoformat()
                    )
                    
                    repos.append(local_repo)
                    self.repositories[local_repo.name] = local_repo
                    
                except Exception as e:
                    print(f"Error scanning {item}: {e}")
        
        return repos

# Initialize FastAPI app
app = FastAPI(
    title="Repository MCP Server",
    description="AI-powered repository management and analysis",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP server
mcp_server = RepositoryMCPServer()

@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "message": "Repository MCP Server is running",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/repositories",
            "/repositories/{repo_name}",
            "/sync/{repo_name}",
            "/search",
            "/analyze/{repo_name}"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "repositories_count": len(mcp_server.repositories),
        "config_loaded": bool(mcp_server.config),
        "github_token_set": bool(mcp_server.config.get("github_token")),
        "openai_key_set": bool(mcp_server.config.get("embedding", {}).get("api_key"))
    }

@app.get("/repositories")
async def list_repositories(owner: Optional[str] = None, include_local: bool = True):
    """List all repositories"""
    try:
        repos = await mcp_server.list_repositories(owner, include_local)
        return {
            "repositories": repos,
            "count": len(repos),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/repositories/{repo_name}")
async def get_repository(repo_name: str):
    """Get detailed information about a specific repository"""
    if repo_name not in mcp_server.repositories:
        raise HTTPException(status_code=404, detail=f"Repository {repo_name} not found")
    
    repo = mcp_server.repositories[repo_name]
    return {
        "repository": asdict(repo),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/sync/{repo_name}")
async def sync_repository(repo_name: str, options: Dict[str, Any] = None):
    """Sync a repository"""
    if repo_name not in mcp_server.repositories:
        raise HTTPException(status_code=404, detail=f"Repository {repo_name} not found")
    
    # For now, just return success
    return {
        "message": f"Repository {repo_name} sync initiated",
        "status": "success",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/search")
async def search_code(query: str, repo_filter: Optional[str] = None):
    """Search code across repositories"""
    return {
        "query": query,
        "repo_filter": repo_filter,
        "message": "Search functionality coming soon",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/analyze/{repo_name}")
async def analyze_repository(repo_name: str):
    """Analyze repository structure and patterns"""
    if repo_name not in mcp_server.repositories:
        raise HTTPException(status_code=404, detail=f"Repository {repo_name} not found")
    
    return {
        "repository": repo_name,
        "analysis": "Analysis functionality coming soon",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🚀 Starting Repository MCP Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("❤️  Health check at: http://localhost:8000/health")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
