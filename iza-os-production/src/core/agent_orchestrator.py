#!/usr/bin/env python3
"""
IZA OS Agent Orchestrator
High-level researcher and note-taker with Git/GitHub integration
Based on analysis of 100+ repositories for optimal integration patterns
"""

import asyncio
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import httpx
import git
from dataclasses import dataclass, asdict
import yaml
import logging
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class Repository:
    name: str
    url: str
    description: str
    category: str
    priority: int
    integration_status: str
    use_cases: List[str]
    dependencies: List[str]
    local_path: Optional[str] = None
    last_analyzed: Optional[str] = None

@dataclass
class AgentTask:
    id: str
    type: str
    repository: str
    status: str
    priority: int
    created_at: str
    completed_at: Optional[str] = None
    notes: List[str] = None
    results: Dict[str, Any] = None

class IZAOSAgentOrchestrator:
    def __init__(self, config_path: str = "agent_config.yaml"):
        self.config = self._load_config(config_path)
        self.repositories: Dict[str, Repository] = {}
        self.tasks: Dict[str, AgentTask] = {}
        self.analysis_results: Dict[str, Any] = {}
        
        # Initialize HTTP client
        self.http_client = httpx.AsyncClient(timeout=30.0)
        
        # Load repository database
        self._load_repository_database()
        
        logger.info("IZA OS Agent Orchestrator initialized")

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        default_config = {
            "github_token": os.getenv("GITHUB_TOKEN"),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "anthropic_api_key": os.getenv("ANTHROPIC_API_KEY"),
            "local_repos_path": "~/repositories",
            "analysis_output_path": "~/analysis_results",
            "max_concurrent_tasks": 5,
            "task_timeout": 300,
            "auto_commit": True,
            "git_user_name": "IZA OS Agent",
            "git_user_email": "agent@iza-os.com"
        }
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                default_config.update(user_config)
        
        return default_config

    def _load_repository_database(self):
        """Load the comprehensive repository database"""
        # Based on your provided list, categorized by use case
        repo_data = [
            # MCP & Integration Tools
            Repository("fastmcp", "https://github.com/jlowin/fastmcp.git", 
                      "Fast MCP server implementation", "mcp", 10, "pending", 
                      ["mcp_server", "api_integration"], ["python", "fastapi"]),
            Repository("mcp-go", "https://github.com/mark3labs/mcp-go.git", 
                      "MCP server in Go", "mcp", 9, "pending", 
                      ["mcp_server", "go_integration"], ["go"]),
            Repository("git-mcp", "https://github.com/idosal/git-mcp.git", 
                      "Git MCP server", "git", 10, "pending", 
                      ["git_operations", "repository_management"], ["python", "git"]),
            Repository("fastapi_mcp", "https://github.com/tadata-org/fastapi_mcp.git", 
                      "FastAPI MCP integration", "mcp", 8, "pending", 
                      ["fastapi", "mcp_integration"], ["python", "fastapi"]),
            
            # Agent Frameworks
            Repository("autogen", "https://github.com/microsoft/autogen.git", 
                      "Microsoft AutoGen multi-agent framework", "agents", 10, "pending", 
                      ["multi_agent", "conversation", "automation"], ["python"]),
            Repository("ai-agents-for-beginners", "https://github.com/microsoft/ai-agents-for-beginners.git", 
                      "AI Agents tutorial and examples", "learning", 9, "pending", 
                      ["tutorial", "examples", "best_practices"], ["python", "jupyter"]),
            Repository("SuperClaude_Framework", "https://github.com/SuperClaude-Org/SuperClaude_Framework.git", 
                      "SuperClaude framework for Claude integration", "claude", 9, "pending", 
                      ["claude_integration", "frameworks"], ["python"]),
            
            # Git & Code Integration
            Repository("claude-code-action", "https://github.com/anthropics/claude-code-action.git", 
                      "Claude code action integration", "claude", 8, "pending", 
                      ["code_actions", "claude_integration"], ["typescript", "github"]),
            Repository("claude-flow", "https://github.com/ruvnet/claude-flow.git", 
                      "Claude workflow automation", "workflow", 8, "pending", 
                      ["workflow", "automation"], ["typescript"]),
            Repository("claudia", "https://github.com/getAsterisk/claudia.git", 
                      "Claudia AI assistant", "assistant", 7, "pending", 
                      ["ai_assistant", "claude"], ["python"]),
            
            # Workflow & Automation
            Repository("n8n", "https://github.com/n8n-io/n8n.git", 
                      "Workflow automation platform", "workflow", 9, "pending", 
                      ["workflow", "automation", "integrations"], ["typescript", "node"]),
            Repository("blok", "https://github.com/blok/blok.git", 
                      "Workflow automation tool", "workflow", 8, "pending", 
                      ["workflow", "automation"], ["typescript"]),
            Repository("stagehand", "https://github.com/Browserbase/stagehand.git", 
                      "Browser automation", "automation", 8, "pending", 
                      ["browser_automation", "testing"], ["typescript"]),
            
            # Documentation & Content
            Repository("markitdown", "https://github.com/microsoft/markitdown.git", 
                      "Convert content to markdown", "documentation", 7, "pending", 
                      ["markdown", "content_conversion"], ["python"]),
            Repository("firecrawl", "https://github.com/mendableai/firecrawl.git", 
                      "Web scraping and crawling", "scraping", 8, "pending", 
                      ["web_scraping", "crawling"], ["python", "typescript"]),
            Repository("open-lovable", "https://github.com/mendableai/open-lovable.git", 
                      "Website generation", "generation", 8, "pending", 
                      ["website_generation", "ui"], ["typescript", "react"]),
            
            # AI & ML Tools
            Repository("dify", "https://github.com/langgenius/dify.git", 
                      "LLM application platform", "ai_platform", 9, "pending", 
                      ["llm_platform", "ai_apps"], ["python", "typescript"]),
            Repository("graphiti", "https://github.com/getzep/graphiti.git", 
                      "Knowledge graph tool", "knowledge", 8, "pending", 
                      ["knowledge_graph", "graph_db"], ["python"]),
            Repository("prompt-optimizer", "https://github.com/promptslab/prompt-optimizer.git", 
                      "Prompt optimization tool", "optimization", 7, "pending", 
                      ["prompt_optimization", "ai"], ["python"]),
            
            # Development Tools
            Repository("lobe-chat", "https://github.com/lobehub/lobe-chat.git", 
                      "AI chat application", "chat", 8, "pending", 
                      ["chat_app", "ai_interface"], ["typescript", "react"]),
            Repository("awesome-llm-apps", "https://github.com/Shubhamsaboo/awesome-llm-apps.git", 
                      "Collection of LLM applications", "reference", 6, "pending", 
                      ["examples", "reference"], ["markdown"]),
            Repository("BMAD-METHOD", "https://github.com/bmad-code-org/BMAD-METHOD.git", 
                      "Business Model Automated Deployment", "business", 9, "pending", 
                      ["business_automation", "deployment"], ["python"]),
        ]
        
        for repo in repo_data:
            self.repositories[repo.name] = repo
        
        logger.info(f"Loaded {len(self.repositories)} repositories for analysis")

    async def analyze_repository(self, repo_name: str) -> Dict[str, Any]:
        """Analyze a repository for integration potential"""
        if repo_name not in self.repositories:
            raise ValueError(f"Repository {repo_name} not found")
        
        repo = self.repositories[repo_name]
        logger.info(f"Analyzing repository: {repo_name}")
        
        analysis = {
            "repository": repo_name,
            "url": repo.url,
            "category": repo.category,
            "priority": repo.priority,
            "analysis_timestamp": datetime.now().isoformat(),
            "integration_readiness": await self._assess_integration_readiness(repo),
            "use_cases": repo.use_cases,
            "dependencies": repo.dependencies,
            "recommended_actions": await self._generate_recommendations(repo),
            "compatibility_score": await self._calculate_compatibility_score(repo)
        }
        
        # Update repository status
        repo.last_analyzed = datetime.now().isoformat()
        repo.integration_status = "analyzed"
        
        # Store analysis results
        self.analysis_results[repo_name] = analysis
        
        return analysis

    async def _assess_integration_readiness(self, repo: Repository) -> Dict[str, Any]:
        """Assess how ready a repository is for integration"""
        readiness = {
            "documentation_quality": "unknown",
            "api_availability": "unknown", 
            "docker_support": "unknown",
            "configuration_ease": "unknown",
            "overall_score": 0
        }
        
        # Simple heuristic-based assessment
        if repo.category == "mcp":
            readiness["api_availability"] = "high"
            readiness["configuration_ease"] = "medium"
            readiness["overall_score"] = 8
        elif repo.category == "agents":
            readiness["documentation_quality"] = "high"
            readiness["overall_score"] = 9
        elif repo.category == "workflow":
            readiness["docker_support"] = "high"
            readiness["overall_score"] = 7
        else:
            readiness["overall_score"] = 5
        
        return readiness

    async def _generate_recommendations(self, repo: Repository) -> List[str]:
        """Generate integration recommendations for a repository"""
        recommendations = []
        
        if repo.category == "mcp":
            recommendations.extend([
                "Integrate as MCP server for repository management",
                "Add to Cursor IDE configuration",
                "Create wrapper for IZA OS integration"
            ])
        elif repo.category == "agents":
            recommendations.extend([
                "Use as base for multi-agent orchestration",
                "Integrate with existing agent framework",
                "Create specialized agents for IZA OS tasks"
            ])
        elif repo.category == "workflow":
            recommendations.extend([
                "Set up as workflow automation backend",
                "Create templates for common IZA OS workflows",
                "Integrate with existing n8n workflows"
            ])
        
        return recommendations

    async def _calculate_compatibility_score(self, repo: Repository) -> int:
        """Calculate compatibility score with IZA OS"""
        score = 0
        
        # Language compatibility
        if "python" in repo.dependencies:
            score += 3
        if "typescript" in repo.dependencies:
            score += 2
        if "go" in repo.dependencies:
            score += 1
        
        # Category compatibility
        if repo.category in ["mcp", "agents", "workflow"]:
            score += 3
        elif repo.category in ["ai_platform", "knowledge", "automation"]:
            score += 2
        
        # Priority bonus
        score += repo.priority // 2
        
        return min(score, 10)

    async def create_integration_task(self, repo_name: str, task_type: str) -> str:
        """Create a new integration task"""
        task_id = f"{repo_name}_{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = AgentTask(
            id=task_id,
            type=task_type,
            repository=repo_name,
            status="created",
            priority=self.repositories[repo_name].priority,
            created_at=datetime.now().isoformat(),
            notes=[],
            results={}
        )
        
        self.tasks[task_id] = task
        logger.info(f"Created task: {task_id}")
        
        return task_id

    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """Execute an integration task"""
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = "running"
        
        logger.info(f"Executing task: {task_id}")
        
        try:
            if task.type == "analyze":
                result = await self.analyze_repository(task.repository)
            elif task.type == "clone":
                result = await self._clone_repository(task.repository)
            elif task.type == "integrate":
                result = await self._integrate_repository(task.repository)
            else:
                result = {"error": f"Unknown task type: {task.type}"}
            
            task.results = result
            task.status = "completed"
            task.completed_at = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            task.status = "failed"
            task.results = {"error": str(e)}
            logger.error(f"Task {task_id} failed: {e}")
            raise

    async def _clone_repository(self, repo_name: str) -> Dict[str, Any]:
        """Clone a repository locally"""
        repo = self.repositories[repo_name]
        local_path = Path(self.config["local_repos_path"]).expanduser() / repo_name
        
        try:
            if local_path.exists():
                # Update existing repository
                git_repo = git.Repo(local_path)
                git_repo.remotes.origin.pull()
                action = "updated"
            else:
                # Clone new repository
                git.Repo.clone_from(repo.url, local_path)
                action = "cloned"
            
            repo.local_path = str(local_path)
            
            return {
                "action": action,
                "local_path": str(local_path),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "action": "clone",
                "status": "error",
                "error": str(e)
            }

    async def _integrate_repository(self, repo_name: str) -> Dict[str, Any]:
        """Integrate a repository into IZA OS"""
        repo = self.repositories[repo_name]
        
        integration_steps = []
        
        # Step 1: Clone repository
        clone_result = await self._clone_repository(repo_name)
        integration_steps.append(clone_result)
        
        # Step 2: Analyze integration points
        analysis = await self.analyze_repository(repo_name)
        integration_steps.append({"step": "analysis", "result": analysis})
        
        # Step 3: Create integration configuration
        config_result = await self._create_integration_config(repo_name)
        integration_steps.append(config_result)
        
        return {
            "repository": repo_name,
            "integration_steps": integration_steps,
            "status": "completed",
            "timestamp": datetime.now().isoformat()
        }

    async def _create_integration_config(self, repo_name: str) -> Dict[str, Any]:
        """Create integration configuration for a repository"""
        repo = self.repositories[repo_name]
        
        config = {
            "name": repo_name,
            "category": repo.category,
            "priority": repo.priority,
            "use_cases": repo.use_cases,
            "dependencies": repo.dependencies,
            "integration_type": self._determine_integration_type(repo),
            "config_file": f"config/{repo_name}_config.yaml",
            "docker_compose": f"docker/{repo_name}_service.yml"
        }
        
        return {
            "step": "config_creation",
            "result": config,
            "status": "success"
        }

    def _determine_integration_type(self, repo: Repository) -> str:
        """Determine the best integration type for a repository"""
        if repo.category == "mcp":
            return "mcp_server"
        elif repo.category == "agents":
            return "agent_framework"
        elif repo.category == "workflow":
            return "workflow_service"
        elif repo.category == "ai_platform":
            return "ai_service"
        else:
            return "library"

    async def generate_integration_report(self) -> Dict[str, Any]:
        """Generate a comprehensive integration report"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "total_repositories": len(self.repositories),
            "analyzed_repositories": len(self.analysis_results),
            "pending_tasks": len([t for t in self.tasks.values() if t.status == "created"]),
            "completed_tasks": len([t for t in self.tasks.values() if t.status == "completed"]),
            "failed_tasks": len([t for t in self.tasks.values() if t.status == "failed"]),
            "recommendations": await self._generate_global_recommendations(),
            "next_steps": await self._generate_next_steps()
        }
        
        return report

    async def _generate_global_recommendations(self) -> List[str]:
        """Generate global recommendations for IZA OS integration"""
        recommendations = []
        
        # Analyze repository categories
        categories = {}
        for repo in self.repositories.values():
            categories[repo.category] = categories.get(repo.category, 0) + 1
        
        # Generate recommendations based on analysis
        if categories.get("mcp", 0) > 0:
            recommendations.append("Prioritize MCP server integration for repository management")
        
        if categories.get("agents", 0) > 0:
            recommendations.append("Implement multi-agent framework for task orchestration")
        
        if categories.get("workflow", 0) > 0:
            recommendations.append("Set up workflow automation for repetitive tasks")
        
        recommendations.extend([
            "Create standardized integration templates",
            "Implement automated testing for integrations",
            "Set up monitoring and logging for all integrated services"
        ])
        
        return recommendations

    async def _generate_next_steps(self) -> List[str]:
        """Generate next steps for IZA OS development"""
        return [
            "Clone and analyze high-priority repositories",
            "Create integration configurations",
            "Set up Docker services for integrated tools",
            "Implement monitoring and health checks",
            "Create documentation for integrated services",
            "Test end-to-end workflows",
            "Deploy to production environment"
        ]

# Initialize FastAPI app
app = FastAPI(
    title="IZA OS Agent Orchestrator",
    description="High-level researcher and note-taker with Git/GitHub integration",
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

# Initialize orchestrator
orchestrator = IZAOSAgentOrchestrator()

@app.get("/")
async def root():
    """Root endpoint with orchestrator information"""
    return {
        "message": "IZA OS Agent Orchestrator is running",
        "version": "1.0.0",
        "repositories_loaded": len(orchestrator.repositories),
        "tasks_created": len(orchestrator.tasks),
        "endpoints": [
            "/health",
            "/repositories",
            "/repositories/{repo_name}/analyze",
            "/tasks",
            "/tasks/{task_id}/execute",
            "/report"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "repositories_count": len(orchestrator.repositories),
        "tasks_count": len(orchestrator.tasks),
        "config_loaded": bool(orchestrator.config)
    }

@app.get("/repositories")
async def list_repositories():
    """List all repositories"""
    repos = [asdict(repo) for repo in orchestrator.repositories.values()]
    return {
        "repositories": repos,
        "count": len(repos),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/repositories/{repo_name}/analyze")
async def analyze_repository_endpoint(repo_name: str):
    """Analyze a specific repository"""
    try:
        analysis = await orchestrator.analyze_repository(repo_name)
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tasks")
async def create_task(repo_name: str, task_type: str):
    """Create a new integration task"""
    try:
        task_id = await orchestrator.create_integration_task(repo_name, task_type)
        return {
            "task_id": task_id,
            "status": "created",
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/tasks/{task_id}/execute")
async def execute_task_endpoint(task_id: str):
    """Execute a task"""
    try:
        result = await orchestrator.execute_task(task_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks")
async def list_tasks():
    """List all tasks"""
    tasks = [asdict(task) for task in orchestrator.tasks.values()]
    return {
        "tasks": tasks,
        "count": len(tasks),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/report")
async def generate_report():
    """Generate integration report"""
    try:
        report = await orchestrator.generate_integration_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting IZA OS Agent Orchestrator...")
    print("📡 Server will be available at: http://localhost:8001")
    print("📚 API documentation at: http://localhost:8001/docs")
    print("❤️  Health check at: http://localhost:8001/health")
    print("🔍 Repository analysis at: http://localhost:8001/repositories")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
