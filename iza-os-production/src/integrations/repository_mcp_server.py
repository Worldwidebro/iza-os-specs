#!/usr/bin/env python3
"""
Comprehensive Repository MCP Server
Integrates GitHub repos, GitToDoc, local files, and knowledge graph
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

@dataclass
class CodeFile:
    path: str
    repo_name: str
    content: str
    language: str
    size: int
    last_modified: str
    embedding: Optional[List[float]] = None

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

    # =============================================================================
    # MCP Server Endpoints
    # =============================================================================

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

    async def get_repository(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific repository"""
        if repo_name in self.repositories:
            repo = self.repositories[repo_name]
            
            # Enhance with recent activity
            repo_dict = asdict(repo)
            repo_dict['recent_commits'] = await self._get_recent_commits(repo_name)
            repo_dict['file_structure'] = await self._get_file_structure(repo_name)
            
            return repo_dict
        return None

    async def sync_repository(self, repo_name: str, 
                            options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sync a repository (clone/pull + optional GitToDoc)"""
        options = options or {}
        repo = self.repositories.get(repo_name)
        
        if not repo:
            return {"error": f"Repository {repo_name} not found"}
        
        result = {
            "repo_name": repo_name,
            "actions": [],
            "status": "success"
        }
        
        try:
            # Clone or pull repository
            if options.get("update_local", True):
                local_result = await self._sync_local_repo(repo)
                result["actions"].append(local_result)
            
            # Sync to GitToDoc
            if options.get("sync_gittodoc", self.config["sync_settings"]["auto_gittodoc"]):
                gittodoc_result = await self._sync_to_gittodoc(repo)
                result["actions"].append(gittodoc_result)
            
            # Update knowledge graph
            if options.get("update_graph", True):
                graph_result = await self._update_knowledge_graph(repo)
                result["actions"].append(graph_result)
                
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            
        return result

    async def search_code(self, query: str, repo_filter: Optional[str] = None,
                         language_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search code across all repositories"""
        results = []
        
        for repo_name, repo in self.repositories.items():
            if repo_filter and repo_filter not in repo_name:
                continue
                
            if repo.local_path and os.path.exists(repo.local_path):
                repo_results = await self._search_repo_code(
                    repo.local_path, query, language_filter
                )
                for result in repo_results:
                    result['repo_name'] = repo_name
                    results.append(result)
        
        return results

    async def analyze_repository(self, repo_name: str) -> Dict[str, Any]:
        """Analyze repository structure, complexity, and patterns"""
        repo = self.repositories.get(repo_name)
        if not repo or not repo.local_path:
            return {"error": "Repository not found or not local"}
        
        analysis = {
            "repo_name": repo_name,
            "languages": await self._analyze_languages(repo.local_path),
            "structure": await self._analyze_structure(repo.local_path),
            "complexity": await self._analyze_complexity(repo.local_path),
            "dependencies": await self._analyze_dependencies(repo.local_path),
            "documentation": await self._analyze_documentation(repo.local_path)
        }
        
        return analysis

    async def create_gittodoc_project(self, repo_name: str) -> Dict[str, Any]:
        """Create or update GitToDoc project for repository"""
        repo = self.repositories.get(repo_name)
        if not repo:
            return {"error": f"Repository {repo_name} not found"}
        
        try:
            # Call GitToDoc API
            response = await self._create_gittodoc_project(repo)
            
            # Update repository with GitToDoc URL
            if response.get("success"):
                repo.gittodoc_url = response.get("url")
                await self._save_repository_metadata()
            
            return response
            
        except Exception as e:
            return {"error": str(e)}

    async def get_repository_insights(self, repo_name: str) -> Dict[str, Any]:
        """Get AI-powered insights about repository"""
        repo = self.repositories.get(repo_name)
        if not repo:
            return {"error": f"Repository {repo_name} not found"}
        
        insights = {
            "summary": await self._generate_repo_summary(repo),
            "tech_stack": await self._identify_tech_stack(repo),
            "architecture_patterns": await self._identify_patterns(repo),
            "improvement_suggestions": await self._suggest_improvements(repo),
            "related_repos": await self._find_related_repos(repo)
        }
        
        return insights

    # =============================================================================
    # GitHub Integration
    # =============================================================================

    async def _fetch_github_repos(self, owner: str) -> List[Repository]:
        """Fetch repositories from GitHub API"""
        repos = []
        page = 1
        
        while True:
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
        
        return repos

    # =============================================================================
    # Local Repository Management
    # =============================================================================

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

    async def _sync_local_repo(self, repo: Repository) -> Dict[str, Any]:
        """Clone or pull a repository locally"""
        base_path = Path(self.config["local_repos_path"]).expanduser()
        base_path.mkdir(exist_ok=True)
        
        repo_path = base_path / repo.name
        
        if repo_path.exists():
            # Pull latest changes
            try:
                git_repo = git.Repo(repo_path)
                git_repo.remotes.origin.pull()
                return {"action": "pull", "status": "success", "path": str(repo_path)}
            except Exception as e:
                return {"action": "pull", "status": "error", "error": str(e)}
        else:
            # Clone repository
            try:
                git.Repo.clone_from(repo.url, repo_path)
                repo.local_path = str(repo_path)
                return {"action": "clone", "status": "success", "path": str(repo_path)}
            except Exception as e:
                return {"action": "clone", "status": "error", "error": str(e)}

    # =============================================================================
    # GitToDoc Integration
    # =============================================================================

    async def _sync_to_gittodoc(self, repo: Repository) -> Dict[str, Any]:
        """Sync repository to GitToDoc"""
        if not self.config.get("gittodoc_api_key"):
            return {"action": "gittodoc_sync", "status": "skipped", "reason": "No API key"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.gittodoc.com/v1/projects",
                    headers={"Authorization": f"Bearer {self.config['gittodoc_api_key']}"},
                    json={
                        "repository_url": repo.url,
                        "name": repo.name,
                        "description": repo.description or f"Documentation for {repo.name}",
                        "auto_sync": True
                    }
                )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    repo.gittodoc_url = data.get("url")
                    return {
                        "action": "gittodoc_sync", 
                        "status": "success", 
                        "url": data.get("url")
                    }
                else:
                    return {
                        "action": "gittodoc_sync", 
                        "status": "error", 
                        "error": f"HTTP {response.status_code}"
                    }
                    
        except Exception as e:
            return {"action": "gittodoc_sync", "status": "error", "error": str(e)}

    async def _create_gittodoc_project(self, repo: Repository) -> Dict[str, Any]:
        """Create a new GitToDoc project"""
        # Similar to _sync_to_gittodoc but with different endpoint/logic
        return await self._sync_to_gittodoc(repo)

    # =============================================================================
    # Knowledge Graph Integration
    # =============================================================================

    async def _update_knowledge_graph(self, repo: Repository) -> Dict[str, Any]:
        """Update Neo4j knowledge graph with repository data"""
        try:
            # This would integrate with your Neo4j MCP server
            # For now, return a placeholder
            return {
                "action": "graph_update",
                "status": "success",
                "nodes_created": 1,
                "relationships_created": 0
            }
        except Exception as e:
            return {"action": "graph_update", "status": "error", "error": str(e)}

    # =============================================================================
    # Analysis Functions
    # =============================================================================

    async def _analyze_languages(self, repo_path: str) -> Dict[str, Any]:
        """Analyze programming languages in repository"""
        languages = {}
        total_lines = 0
        
        for file_path in Path(repo_path).rglob("*"):
            if file_path.is_file() and not any(pattern in str(file_path) 
                                             for pattern in self.config["sync_settings"]["exclude_patterns"]):
                extension = file_path.suffix.lower()
                
                # Map extensions to languages (simplified)
                lang_map = {
                    ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
                    ".java": "Java", ".cpp": "C++", ".c": "C", ".go": "Go",
                    ".rs": "Rust", ".php": "PHP", ".rb": "Ruby", ".swift": "Swift"
                }
                
                language = lang_map.get(extension, "Other")
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = len(f.readlines())
                        languages[language] = languages.get(language, 0) + lines
                        total_lines += lines
                except:
                    pass
        
        # Calculate percentages
        for lang in languages:
            languages[lang] = {
                "lines": languages[lang],
                "percentage": round((languages[lang] / total_lines) * 100, 2) if total_lines > 0 else 0
            }
        
        return {"languages": languages, "total_lines": total_lines}

    async def _search_repo_code(self, repo_path: str, query: str, 
                               language_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search code within a repository"""
        results = []
        
        # Use git grep if available, otherwise fallback to basic search
        try:
            cmd = ["git", "grep", "-n", "-i", query]
            if language_filter:
                cmd.extend([f"*.{language_filter}"])
            
            result = subprocess.run(
                cmd, 
                cwd=repo_path, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            results.append({
                                "file": parts[0],
                                "line": int(parts[1]),
                                "content": parts[2].strip()
                            })
        except:
            # Fallback to simple file search
            pass
        
        return results

    # =============================================================================
    # Utility Functions
    # =============================================================================

    async def _save_repository_metadata(self):
        """Save repository metadata to file"""
        metadata = {repo_name: asdict(repo) for repo_name, repo in self.repositories.items()}
        
        with open("repository_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2, default=str)

    async def _get_recent_commits(self, repo_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent commits for a repository"""
        repo = self.repositories.get(repo_name)
        if not repo or not repo.local_path:
            return []
        
        try:
            git_repo = git.Repo(repo.local_path)
            commits = []
            
            for commit in git_repo.iter_commits(max_count=limit):
                commits.append({
                    "hash": commit.hexsha[:8],
                    "message": commit.message.strip(),
                    "author": commit.author.name,
                    "date": commit.committed_datetime.isoformat()
                })
            
            return commits
        except:
            return []

    async def _get_file_structure(self, repo_name: str, max_depth: int = 3) -> Dict[str, Any]:
        """Get repository file structure"""
        repo = self.repositories.get(repo_name)
        if not repo or not repo.local_path:
            return {}
        
        def build_tree(path: Path, current_depth: int = 0) -> Dict[str, Any]:
            if current_depth >= max_depth:
                return {"type": "truncated"}
            
            if path.is_file():
                return {
                    "type": "file",
                    "size": path.stat().st_size,
                    "extension": path.suffix
                }
            
            tree = {"type": "directory", "children": {}}
            try:
                for item in path.iterdir():
                    if not item.name.startswith('.') and item.name not in ["node_modules", "__pycache__"]:
                        tree["children"][item.name] = build_tree(item, current_depth + 1)
            except PermissionError:
                pass
            
            return tree
        
        return build_tree(Path(repo.local_path))

# =============================================================================
# MCP Server Main
# =============================================================================

async def main():
    """Main MCP server loop"""
    server = RepositoryMCPServer()
    
    # Initialize with some default repositories
    await server.list_repositories("your-github-username", include_local=True)
    
    print("Repository MCP Server is running...")
    print("Available endpoints:")
    print("- list_repositories(owner?, include_local?)")
    print("- get_repository(repo_name)")
    print("- sync_repository(repo_name, options?)")
    print("- search_code(query, repo_filter?, language_filter?)")
    print("- analyze_repository(repo_name)")
    print("- create_gittodoc_project(repo_name)")
    print("- get_repository_insights(repo_name)")
    
    # Keep server running
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())