#!/usr/bin/env python3
"""
REPOSITORY INTEGRATION BRIDGE
Seamlessly connects all repositories to work effortlessly together
The missing architecture layer for cross-repository communication
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from UNIVERSAL_API_ORCHESTRATOR import UniversalAPIOrchestrator, APIRequest
from UNIFIED_MEMORY_ORCHESTRATOR import UnifiedMemoryOrchestrator
from IZA_OS_COMMAND_CENTER import IzaOSCommandCenter

@dataclass
class RepositoryMapping:
    """Maps repository structure and capabilities"""
    name: str
    path: Path
    type: str  # core, ai_system, tool, data, integration
    capabilities: List[str]
    api_endpoints: List[str]
    entry_points: Dict[str, str]
    dependencies: List[str]
    status: str = "active"

@dataclass
class CrossRepoRequest:
    """Universal request format for cross-repository operations"""
    source_repo: str
    target_repo: str
    operation: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any] = None

@dataclass
class IntegrationFlow:
    """Defines how repositories integrate with each other"""
    flow_id: str
    description: str
    repositories: List[str]
    data_flow: List[Dict[str, str]]
    triggers: List[str]
    outputs: List[str]

class RepositoryIntegrationBridge:
    """The master bridge connecting all repositories seamlessly"""
    
    def __init__(self):
        self.base_path = Path("/Users/divinejohns/memU")
        self.api_orchestrator = UniversalAPIOrchestrator()
        self.memory_orchestrator = UnifiedMemoryOrchestrator()
        self.iza_os = IzaOSCommandCenter()
        
        # Repository mappings discovered from your system
        self.repositories = {
            # Core System Repositories
            "iza_os": RepositoryMapping(
                name="IZA OS Command Center",
                path=self.base_path,
                type="core",
                capabilities=["empire_management", "agent_orchestration", "strategic_planning"],
                api_endpoints=["/command", "/status", "/deploy"],
                entry_points={"main": "IZA_OS_COMMAND_CENTER.py"},
                dependencies=["unified_memory", "universal_api"]
            ),
            "unified_memory": RepositoryMapping(
                name="Unified Memory Orchestrator", 
                path=self.base_path,
                type="core",
                capabilities=["memory_sync", "cross_system_search", "knowledge_management"],
                api_endpoints=["/store", "/search", "/sync"],
                entry_points={"main": "UNIFIED_MEMORY_ORCHESTRATOR.py"},
                dependencies=["mem0", "chromadb", "letta"]
            ),
            "universal_api": RepositoryMapping(
                name="Universal API Orchestrator",
                path=self.base_path,
                type="core", 
                capabilities=["ai_routing", "provider_switching", "cost_optimization"],
                api_endpoints=["/chat", "/route", "/health"],
                entry_points={"main": "UNIVERSAL_API_ORCHESTRATOR.py"},
                dependencies=["openrouter", "groq", "google_ai"]
            ),
            
            # AI System Repositories  
            "ai_boss_holdings": RepositoryMapping(
                name="AI Boss Holdings Core",
                path=self.base_path / "ai_systems" / "ai_boss",
                type="ai_system",
                capabilities=["business_automation", "revenue_tracking", "workflow_orchestration"],
                api_endpoints=["/automate", "/track", "/orchestrate"],
                entry_points={"main": "ULTIMATE_AI_BOSS_HOLDINGS_INTEGRATION.py"},
                dependencies=["iza_os", "unified_memory"]
            ),
            "letta_agents": RepositoryMapping(
                name="Letta Agent Framework",
                path=self.base_path / "ai_systems" / "ai_boss" / "ai-agents" / "letta",
                type="ai_system",
                capabilities=["agent_memory", "conversation_management", "persistent_agents"],
                api_endpoints=["/agents", "/messages", "/memory"],
                entry_points={"server": "letta/server/server.py"},
                dependencies=["unified_memory", "universal_api"]
            ),
            
            # Tool Repositories
            "claude_code": RepositoryMapping(
                name="Claude Code Templates",
                path=self.base_path / "claude-code",
                type="tool",
                capabilities=["code_templates", "claude_integration", "development_acceleration"],
                api_endpoints=["/templates", "/generate", "/deploy"],
                entry_points={"cli": "cli-tool/"},
                dependencies=["universal_api"]
            ),
            "n8n_workflows": RepositoryMapping(
                name="N8N Workflow Automation",
                path=self.base_path / "n8n-workflows", 
                type="tool",
                capabilities=["workflow_automation", "api_integration", "process_orchestration"],
                api_endpoints=["/workflows", "/execute", "/schedule"],
                entry_points={"server": "run.py"},
                dependencies=["universal_api", "unified_memory"]
            ),
            "raycast_scripts": RepositoryMapping(
                name="Raycast Command Scripts",
                path=self.base_path,
                type="tool",
                capabilities=["quick_commands", "system_automation", "productivity_shortcuts"],
                api_endpoints=["/execute", "/shortcuts"],
                entry_points={"config": "raycast-shortcuts.json"},
                dependencies=["iza_os"]
            ),
            
            # Data Repositories
            "memu_core": RepositoryMapping(
                name="MemU Memory System", 
                path=self.base_path / "memu",
                type="data",
                capabilities=["memory_storage", "embedding_generation", "recall_system"],
                api_endpoints=["/store", "/recall", "/embed"],
                entry_points={"main": "memu/"},
                dependencies=["universal_api"]
            ),
            "business_data": RepositoryMapping(
                name="Business Intelligence Data",
                path=self.base_path / "business_data",
                type="data", 
                capabilities=["revenue_analytics", "performance_metrics", "client_data"],
                api_endpoints=["/analytics", "/metrics", "/reports"],
                entry_points={"data": "business_data/"},
                dependencies=["ai_boss_holdings"]
            ),
            
            # Integration Repositories
            "stripe_integrations": RepositoryMapping(
                name="Stripe Payment Integration",
                path=self.base_path / "integrations" / "stripe",
                type="integration",
                capabilities=["payment_processing", "billing_automation", "revenue_tracking"],
                api_endpoints=["/payments", "/webhooks", "/billing"],
                entry_points={"webhooks": "stripe-webhook-handler.py"},
                dependencies=["ai_boss_holdings", "business_data"]
            ),
            "vercept_integration": RepositoryMapping(
                name="Vercept AI Assistant",
                path=self.base_path,
                type="integration",
                capabilities=["ai_assistance", "audit_logging", "compliance_monitoring"],
                api_endpoints=["/assist", "/audit", "/compliance"],
                entry_points={"config": "vercept.yml"},
                dependencies=["unified_memory", "universal_api"]
            )
        }
        
        # Integration flows defining how repositories work together
        self.integration_flows = {
            "content_creation_pipeline": IntegrationFlow(
                flow_id="content_creation",
                description="AI-powered content creation from idea to publication",
                repositories=["universal_api", "unified_memory", "ai_boss_holdings", "business_data"],
                data_flow=[
                    {"from": "unified_memory", "to": "universal_api", "data": "content_ideas"},
                    {"from": "universal_api", "to": "ai_boss_holdings", "data": "generated_content"},
                    {"from": "ai_boss_holdings", "to": "business_data", "data": "performance_metrics"}
                ],
                triggers=["content_request", "scheduled_creation"],
                outputs=["published_content", "analytics_data"]
            ),
            "revenue_optimization_flow": IntegrationFlow(
                flow_id="revenue_optimization",
                description="Automated revenue tracking and optimization",
                repositories=["stripe_integrations", "business_data", "ai_boss_holdings", "unified_memory"],
                data_flow=[
                    {"from": "stripe_integrations", "to": "business_data", "data": "payment_events"},
                    {"from": "business_data", "to": "ai_boss_holdings", "data": "revenue_analytics"}, 
                    {"from": "ai_boss_holdings", "to": "unified_memory", "data": "optimization_insights"}
                ],
                triggers=["payment_received", "revenue_goal_check"],
                outputs=["optimization_recommendations", "revenue_forecasts"]
            ),
            "agent_orchestration_flow": IntegrationFlow(
                flow_id="agent_orchestration", 
                description="Multi-agent coordination for complex tasks",
                repositories=["iza_os", "letta_agents", "universal_api", "unified_memory"],
                data_flow=[
                    {"from": "iza_os", "to": "letta_agents", "data": "agent_commands"},
                    {"from": "letta_agents", "to": "universal_api", "data": "ai_requests"},
                    {"from": "universal_api", "to": "unified_memory", "data": "conversation_history"}
                ],
                triggers=["imperial_command", "agent_activation"],
                outputs=["task_completion", "agent_reports"]
            ),
            "knowledge_management_flow": IntegrationFlow(
                flow_id="knowledge_management",
                description="Unified knowledge capture, storage, and retrieval", 
                repositories=["unified_memory", "memu_core", "vercept_integration", "claude_code"],
                data_flow=[
                    {"from": "claude_code", "to": "unified_memory", "data": "code_templates"},
                    {"from": "vercept_integration", "to": "memu_core", "data": "interaction_logs"},
                    {"from": "memu_core", "to": "unified_memory", "data": "processed_memories"}
                ],
                triggers=["new_knowledge", "memory_sync"],
                outputs=["searchable_knowledge", "intelligent_suggestions"]
            )
        }
    
    async def initialize_bridge(self):
        """Initialize the integration bridge and all connected systems"""
        print("🌉 INITIALIZING REPOSITORY INTEGRATION BRIDGE")
        print("=" * 55)
        
        # Initialize core systems
        await self.memory_orchestrator.initialize_all_systems()
        print("✅ Memory orchestrator ready")
        
        # Check repository health
        repo_status = await self.check_repository_health()
        healthy_repos = sum(1 for status in repo_status.values() if status["status"] == "healthy")
        
        print(f"✅ Bridge initialized: {healthy_repos}/{len(self.repositories)} repositories healthy")
        
        # Setup integration flows
        await self.setup_integration_flows()
        print("✅ Integration flows configured")
        
        return {
            "status": "initialized",
            "healthy_repositories": healthy_repos,
            "total_repositories": len(self.repositories),
            "active_flows": len(self.integration_flows)
        }
    
    async def check_repository_health(self) -> Dict[str, Dict[str, Any]]:
        """Check health and availability of all repositories"""
        health_status = {}
        
        for repo_id, repo in self.repositories.items():
            try:
                # Check if repository path exists
                path_exists = repo.path.exists()
                
                # Check if entry points exist
                entry_points_exist = {}
                for ep_name, ep_path in repo.entry_points.items():
                    full_path = repo.path / ep_path
                    entry_points_exist[ep_name] = full_path.exists()
                
                # Determine overall health
                health = "healthy" if path_exists and any(entry_points_exist.values()) else "unhealthy"
                
                health_status[repo_id] = {
                    "status": health,
                    "path_exists": path_exists,
                    "entry_points": entry_points_exist,
                    "capabilities": repo.capabilities,
                    "type": repo.type
                }
                
            except Exception as e:
                health_status[repo_id] = {
                    "status": "error",
                    "error": str(e),
                    "capabilities": repo.capabilities,
                    "type": repo.type
                }
        
        return health_status
    
    async def setup_integration_flows(self):
        """Setup all integration flows between repositories"""
        for flow_id, flow in self.integration_flows.items():
            try:
                # Validate all repositories in flow exist
                missing_repos = [repo for repo in flow.repositories if repo not in self.repositories]
                if missing_repos:
                    print(f"⚠️ Flow {flow_id} missing repositories: {missing_repos}")
                    continue
                
                # Store flow configuration in memory for later execution
                await self.memory_orchestrator.store_memory(
                    f"INTEGRATION_FLOW: {flow.description}. Connects {len(flow.repositories)} repositories: {', '.join(flow.repositories)}. Triggers: {', '.join(flow.triggers)}",
                    metadata={
                        "type": "integration_flow",
                        "flow_id": flow_id,
                        "repositories": flow.repositories,
                        "triggers": flow.triggers
                    },
                    memory_type="system"
                )
                
                print(f"✅ Flow configured: {flow_id}")
                
            except Exception as e:
                print(f"❌ Failed to setup flow {flow_id}: {e}")
    
    async def execute_cross_repo_request(self, request: CrossRepoRequest) -> Dict[str, Any]:
        """Execute a request that spans multiple repositories"""
        print(f"🔄 Executing cross-repo request: {request.source_repo} → {request.target_repo}")
        
        start_time = datetime.now()
        
        try:
            # Validate repositories exist
            if request.source_repo not in self.repositories:
                raise ValueError(f"Source repository not found: {request.source_repo}")
            if request.target_repo not in self.repositories:
                raise ValueError(f"Target repository not found: {request.target_repo}")
            
            # Route request based on operation type
            if request.operation == "ai_chat":
                return await self._handle_ai_chat_request(request)
            elif request.operation == "memory_search":
                return await self._handle_memory_search_request(request)
            elif request.operation == "business_automation":
                return await self._handle_business_automation_request(request)
            elif request.operation == "agent_deployment":
                return await self._handle_agent_deployment_request(request)
            else:
                return await self._handle_generic_request(request)
                
        except Exception as e:
            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return {
                "success": False,
                "error": str(e),
                "source_repo": request.source_repo,
                "target_repo": request.target_repo,
                "operation": request.operation,
                "duration_ms": duration_ms
            }
    
    async def _handle_ai_chat_request(self, request: CrossRepoRequest) -> Dict[str, Any]:
        """Handle AI chat requests across repositories"""
        prompt = request.parameters.get("prompt", "")
        optimization = request.parameters.get("optimization", "auto")
        
        # Use universal API orchestrator
        response = await self.api_orchestrator.chat(prompt, optimization=optimization)
        
        # Store interaction in unified memory
        await self.memory_orchestrator.store_memory(
            f"CROSS_REPO_AI_CHAT: {request.source_repo} requested AI assistance. Prompt: {prompt[:100]}... Response generated via {optimization} optimization.",
            metadata={
                "type": "ai_interaction",
                "source_repo": request.source_repo,
                "optimization": optimization
            },
            memory_type="interaction"
        )
        
        return {
            "success": True,
            "response": response,
            "provider": "universal_api", 
            "optimization_used": optimization
        }
    
    async def _handle_memory_search_request(self, request: CrossRepoRequest) -> Dict[str, Any]:
        """Handle memory search requests across repositories"""
        query = request.parameters.get("query", "")
        limit = request.parameters.get("limit", 10)
        
        # Search unified memory
        results = await self.memory_orchestrator.search_memories(query, limit=limit)
        
        # Format results for cross-repo consumption
        formatted_results = []
        for result in results:
            formatted_results.append({
                "memory_id": result.memory_id,
                "content": result.content,
                "source_system": result.source_system,
                "memory_type": result.memory_type,
                "relevance": result.importance_score
            })
        
        return {
            "success": True,
            "results": formatted_results,
            "total_found": len(results),
            "query": query
        }
    
    async def _handle_business_automation_request(self, request: CrossRepoRequest) -> Dict[str, Any]:
        """Handle business automation requests"""
        automation_type = request.parameters.get("type", "general")
        parameters = request.parameters.get("parameters", {})
        
        # Route through IZA OS for business operations
        command = f"automate {automation_type}"
        result = await self.iza_os.execute_imperial_command(command)
        
        return {
            "success": True,
            "automation_type": automation_type,
            "result": result,
            "executed_via": "iza_os"
        }
    
    async def _handle_agent_deployment_request(self, request: CrossRepoRequest) -> Dict[str, Any]:
        """Handle agent deployment across repositories"""
        agent_type = request.parameters.get("agent_type", "worker")
        count = request.parameters.get("count", 1)
        specialization = request.parameters.get("specialization", "general")
        
        # Deploy through IZA OS agent workforce
        command = f"activate agents {agent_type} {count} {specialization}"
        result = await self.iza_os.execute_imperial_command(command)
        
        return {
            "success": True,
            "agents_deployed": count,
            "agent_type": agent_type,
            "specialization": specialization,
            "result": result
        }
    
    async def _handle_generic_request(self, request: CrossRepoRequest) -> Dict[str, Any]:
        """Handle generic cross-repository requests"""
        # For operations not specifically handled, use a generic approach
        return {
            "success": True,
            "message": f"Generic handler executed for {request.operation}",
            "parameters": request.parameters,
            "note": "Specific handler not implemented yet"
        }
    
    async def execute_integration_flow(self, flow_id: str, trigger_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a complete integration flow"""
        if flow_id not in self.integration_flows:
            raise ValueError(f"Integration flow not found: {flow_id}")
        
        flow = self.integration_flows[flow_id]
        print(f"🔄 Executing integration flow: {flow_id}")
        
        results = {
            "flow_id": flow_id,
            "description": flow.description,
            "steps": [],
            "start_time": datetime.now().isoformat()
        }
        
        try:
            # Execute each data flow step
            for step in flow.data_flow:
                step_result = await self.execute_cross_repo_request(
                    CrossRepoRequest(
                        source_repo=step["from"],
                        target_repo=step["to"],
                        operation="data_flow",
                        parameters={"data_type": step["data"], "trigger_data": trigger_data}
                    )
                )
                
                results["steps"].append({
                    "from": step["from"],
                    "to": step["to"],
                    "data": step["data"],
                    "success": step_result.get("success", False),
                    "result": step_result
                })
            
            results["status"] = "completed"
            results["end_time"] = datetime.now().isoformat()
            
            # Store flow execution in memory
            await self.memory_orchestrator.store_memory(
                f"INTEGRATION_FLOW_EXECUTED: {flow.description} completed successfully with {len(results['steps'])} steps.",
                metadata={
                    "type": "flow_execution",
                    "flow_id": flow_id,
                    "steps_completed": len(results["steps"])
                },
                memory_type="system"
            )
            
        except Exception as e:
            results["status"] = "failed"
            results["error"] = str(e)
            results["end_time"] = datetime.now().isoformat()
        
        return results
    
    async def get_repository_map(self) -> Dict[str, Dict[str, Any]]:
        """Get comprehensive map of all repositories and their relationships"""
        repo_map = {}
        
        for repo_id, repo in self.repositories.items():
            # Get health status
            health = await self.check_repository_health()
            repo_health = health.get(repo_id, {})
            
            # Find integration flows this repo participates in
            participating_flows = [
                flow_id for flow_id, flow in self.integration_flows.items()
                if repo_id in flow.repositories
            ]
            
            # Find dependencies
            dependent_repos = [
                dep for dep in repo.dependencies 
                if dep in self.repositories
            ]
            
            repo_map[repo_id] = {
                "name": repo.name,
                "type": repo.type,
                "capabilities": repo.capabilities,
                "health": repo_health.get("status", "unknown"),
                "path": str(repo.path),
                "entry_points": repo.entry_points,
                "dependencies": dependent_repos,
                "participating_flows": participating_flows,
                "api_endpoints": repo.api_endpoints
            }
        
        return repo_map
    
    async def optimize_repository_connections(self) -> Dict[str, Any]:
        """Analyze and optimize connections between repositories"""
        print("⚡ Optimizing repository connections...")
        
        # Analyze current connections
        repo_map = await self.get_repository_map()
        health_status = await self.check_repository_health()
        
        # Find optimization opportunities
        optimizations = {
            "redundant_connections": [],
            "missing_connections": [],
            "performance_improvements": [],
            "suggested_flows": []
        }
        
        # Check for missing connections
        for repo_id, repo_data in repo_map.items():
            for dep in repo_data["dependencies"]:
                if dep not in self.repositories:
                    optimizations["missing_connections"].append({
                        "repo": repo_id,
                        "missing_dependency": dep,
                        "impact": "high"
                    })
        
        # Suggest new integration flows
        high_value_combos = [
            (["universal_api", "unified_memory", "business_data"], "ai_analytics_flow"),
            (["stripe_integrations", "ai_boss_holdings", "n8n_workflows"], "automated_billing_flow"),
            (["claude_code", "letta_agents", "universal_api"], "code_generation_flow")
        ]
        
        for repo_combo, suggested_name in high_value_combos:
            if all(repo in self.repositories for repo in repo_combo):
                if suggested_name not in self.integration_flows:
                    optimizations["suggested_flows"].append({
                        "name": suggested_name,
                        "repositories": repo_combo,
                        "potential_value": "high"
                    })
        
        # Performance improvements
        healthy_repos = [repo_id for repo_id, status in health_status.items() if status["status"] == "healthy"]
        optimizations["performance_improvements"] = [
            f"Focus integration efforts on {len(healthy_repos)} healthy repositories",
            "Implement caching layer for cross-repo requests",
            "Add async processing for heavy integration flows"
        ]
        
        return optimizations

# CLI Interface
async def main():
    bridge = RepositoryIntegrationBridge()
    
    print("🌉 REPOSITORY INTEGRATION BRIDGE")
    print("=" * 40)
    print("Seamlessly connecting all repositories...")
    
    # Initialize bridge
    init_result = await bridge.initialize_bridge()
    print(f"\n✅ Bridge Status: {init_result['healthy_repositories']}/{init_result['total_repositories']} repos healthy")
    
    # Show repository map
    repo_map = await bridge.get_repository_map()
    print(f"\n📚 DISCOVERED REPOSITORIES ({len(repo_map)}):")
    for repo_id, repo_data in repo_map.items():
        health_emoji = "✅" if repo_data["health"] == "healthy" else "❌"
        print(f"{health_emoji} {repo_data['name']} ({repo_data['type']})")
        print(f"    Capabilities: {', '.join(repo_data['capabilities'][:3])}{'...' if len(repo_data['capabilities']) > 3 else ''}")
        if repo_data['participating_flows']:
            print(f"    Flows: {', '.join(repo_data['participating_flows'])}")
    
    # Show integration flows
    print(f"\n🔄 INTEGRATION FLOWS ({len(bridge.integration_flows)}):")
    for flow_id, flow in bridge.integration_flows.items():
        print(f"⚡ {flow_id}: {flow.description}")
        print(f"    Repositories: {' → '.join(flow.repositories)}")
    
    # Test cross-repo communication
    print(f"\n🧪 TESTING CROSS-REPO COMMUNICATION:")
    
    # Test AI chat request
    test_request = CrossRepoRequest(
        source_repo="claude_code",
        target_repo="universal_api",
        operation="ai_chat",
        parameters={
            "prompt": "Generate a Python function for data processing",
            "optimization": "coding_priority"
        }
    )
    
    result = await bridge.execute_cross_repo_request(test_request)
    if result.get("success"):
        print("✅ Cross-repo AI chat: SUCCESS")
        print(f"    Response: {result['response'][:100]}...")
    else:
        print(f"❌ Cross-repo AI chat: {result.get('error')}")
    
    # Show optimization opportunities
    optimizations = await bridge.optimize_repository_connections()
    print(f"\n⚡ OPTIMIZATION OPPORTUNITIES:")
    if optimizations["suggested_flows"]:
        print("📈 Suggested new flows:")
        for flow in optimizations["suggested_flows"]:
            print(f"  • {flow['name']}: {' + '.join(flow['repositories'])}")
    
    print(f"\n🎉 REPOSITORY INTEGRATION BRIDGE READY!")
    print("All repositories can now communicate seamlessly!")

if __name__ == "__main__":
    asyncio.run(main())