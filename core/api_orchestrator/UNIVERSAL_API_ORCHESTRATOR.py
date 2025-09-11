#!/usr/bin/env python3
"""
UNIVERSAL API ORCHESTRATOR
The missing link connecting all AI services seamlessly
OpenRouter + Groq + Google AI Studio + All Repository APIs
"""

import asyncio
import os
import json
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import httpx
from pathlib import Path

# Import existing LLM clients
try:
    from memu.llm.base import BaseLLMClient, LLMResponse
    from memu.llm.openai_client import OpenAIClient
    from memu.llm.anthropic_client import AnthropicClient
    from memu.llm.deepseek_client import DeepSeekClient
    LLM_CLIENTS_AVAILABLE = True
except ImportError:
    LLM_CLIENTS_AVAILABLE = False
    # Fallback minimal classes
    @dataclass
    class LLMResponse:
        content: str
        model: str
        success: bool
        error: Optional[str] = None

@dataclass
class APIProvider:
    """Universal API provider configuration"""
    name: str
    base_url: str
    api_key_env: str
    models: List[str]
    capabilities: List[str]
    cost_per_token: float
    speed_rating: int  # 1-10, 10 being fastest
    status: str = "active"

@dataclass
class APIRequest:
    """Universal API request format"""
    provider: str
    model: str
    messages: List[Dict[str, str]]
    temperature: float = 0.7
    max_tokens: int = 4000
    stream: bool = False
    tools: Optional[List[Dict]] = None
    metadata: Dict[str, Any] = None

@dataclass
class APIResponse:
    """Universal API response format"""
    content: str
    provider: str
    model: str
    tokens_used: Dict[str, int]
    cost: float
    latency_ms: int
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

class UniversalAPIOrchestrator:
    """The universal API router connecting ALL AI services"""
    
    def __init__(self):
        self.base_path = Path("/Users/divinejohns/memU")
        
        # All supported providers
        self.providers = {
            "openrouter": APIProvider(
                name="OpenRouter",
                base_url="https://openrouter.ai/api/v1",
                api_key_env="OPENROUTER_API_KEY",
                models=[
                    "anthropic/claude-3.5-sonnet",
                    "openai/gpt-4o",
                    "openai/gpt-4o-mini", 
                    "meta-llama/llama-3.2-90b-instruct",
                    "google/gemini-pro-1.5",
                    "mistralai/mistral-large",
                    "cohere/command-r-plus"
                ],
                capabilities=["chat", "vision", "function_calling", "streaming"],
                cost_per_token=0.00001,
                speed_rating=8
            ),
            "groq": APIProvider(
                name="Groq Cloud",
                base_url="https://api.groq.com/openai/v1", 
                api_key_env="GROQ_API_KEY",
                models=[
                    "llama3-8b-8192",
                    "llama3-70b-8192",
                    "mixtral-8x7b-32768",
                    "gemma2-9b-it",
                    "gemma-7b-it"
                ],
                capabilities=["chat", "function_calling", "ultra_fast"],
                cost_per_token=0.0000005,
                speed_rating=10  # Groq is fastest
            ),
            "google_ai": APIProvider(
                name="Google AI Studio",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                api_key_env="GOOGLE_AI_API_KEY",
                models=[
                    "gemini-1.5-pro-latest",
                    "gemini-1.5-flash-latest", 
                    "gemini-1.0-pro",
                    "text-bison-001"
                ],
                capabilities=["chat", "vision", "code_generation", "function_calling"],
                cost_per_token=0.000007,
                speed_rating=7
            ),
            "anthropic": APIProvider(
                name="Anthropic",
                base_url="https://api.anthropic.com",
                api_key_env="ANTHROPIC_API_KEY",
                models=[
                    "claude-3-5-sonnet-20241022",
                    "claude-3-5-haiku-20241022",
                    "claude-3-opus-20240229"
                ],
                capabilities=["chat", "vision", "function_calling", "long_context"],
                cost_per_token=0.000015,
                speed_rating=6
            ),
            "openai": APIProvider(
                name="OpenAI",
                base_url="https://api.openai.com/v1",
                api_key_env="OPENAI_API_KEY",
                models=[
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-4-turbo",
                    "gpt-3.5-turbo"
                ],
                capabilities=["chat", "vision", "function_calling", "streaming"],
                cost_per_token=0.00003,
                speed_rating=7
            ),
            "deepseek": APIProvider(
                name="DeepSeek",
                base_url="https://api.deepseek.com",
                api_key_env="DEEPSEEK_API_KEY",
                models=[
                    "deepseek-reasoner",
                    "deepseek-chat",
                    "deepseek-coder"
                ],
                capabilities=["chat", "coding", "reasoning"],
                cost_per_token=0.000002,
                speed_rating=8
            ),
            "ollama": APIProvider(
                name="Ollama (Local)",
                base_url="http://localhost:11434",
                api_key_env="OLLAMA_API_KEY",  # Not needed but for consistency
                models=[
                    "llama3.2:3b",
                    "llama3.2:1b", 
                    "qwen2.5-coder:7b",
                    "codellama:7b"
                ],
                capabilities=["chat", "local_inference", "privacy"],
                cost_per_token=0.0,  # Free local inference
                speed_rating=5  # Depends on hardware
            )
        }
        
        # Load existing LLM clients if available
        self.llm_clients = {}
        if LLM_CLIENTS_AVAILABLE:
            self._initialize_existing_clients()
        
        # HTTP client for API requests
        self.http_client = httpx.AsyncClient(timeout=60.0)
        
        # Route optimization based on request type
        self.optimization_rules = {
            "speed_priority": "groq",
            "cost_priority": "ollama",
            "quality_priority": "anthropic",
            "coding_priority": "deepseek",
            "local_priority": "ollama",
            "vision_priority": "openai"
        }
        
    def _initialize_existing_clients(self):
        """Initialize existing memu LLM clients"""
        try:
            self.llm_clients = {
                "openai": OpenAIClient(),
                "anthropic": AnthropicClient(),
                "deepseek": DeepSeekClient()
            }
        except Exception as e:
            print(f"Warning: Could not initialize existing clients: {e}")
    
    async def route_request(self, request: APIRequest, 
                           optimization: str = "auto") -> APIResponse:
        """Route request to optimal provider"""
        
        start_time = datetime.now()
        
        # Determine best provider
        if optimization == "auto":
            provider = self._auto_select_provider(request)
        elif optimization in self.optimization_rules:
            provider = self.optimization_rules[optimization]
        else:
            provider = request.provider
            
        # Execute request
        try:
            response = await self._execute_request(provider, request)
            response.latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return response
        except Exception as e:
            return APIResponse(
                content="",
                provider=provider,
                model=request.model,
                tokens_used={"input": 0, "output": 0},
                cost=0.0,
                latency_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                success=False,
                error=str(e)
            )
    
    def _auto_select_provider(self, request: APIRequest) -> str:
        """Automatically select best provider based on request"""
        
        # Check if specific model is requested
        for provider_name, provider in self.providers.items():
            if request.model in provider.models:
                return provider_name
        
        # Check message content for optimization hints
        content = " ".join([msg.get("content", "") for msg in request.messages])
        
        if any(keyword in content.lower() for keyword in ["code", "programming", "python", "javascript"]):
            return "deepseek"
        elif any(keyword in content.lower() for keyword in ["fast", "quick", "urgent"]):
            return "groq"
        elif any(keyword in content.lower() for keyword in ["analyze", "vision", "image"]):
            return "openai"  
        elif len(content) > 10000:  # Long context
            return "anthropic"
        else:
            return "groq"  # Default to fastest
    
    async def _execute_request(self, provider: str, request: APIRequest) -> APIResponse:
        """Execute request with specific provider"""
        
        if provider not in self.providers:
            raise ValueError(f"Unknown provider: {provider}")
            
        provider_config = self.providers[provider]
        
        # Route to appropriate implementation
        if provider == "openrouter":
            return await self._call_openrouter(provider_config, request)
        elif provider == "groq":
            return await self._call_groq(provider_config, request)
        elif provider == "google_ai":
            return await self._call_google_ai(provider_config, request)
        elif provider == "ollama":
            return await self._call_ollama(provider_config, request)
        elif provider in self.llm_clients:
            return await self._call_existing_client(provider, request)
        else:
            return await self._call_openai_compatible(provider_config, request)
    
    async def _call_openrouter(self, provider: APIProvider, request: APIRequest) -> APIResponse:
        """Call OpenRouter API"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            raise ValueError(f"Missing {provider.api_key_env}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ai-boss-holdings.com",
            "X-Title": "AI Boss Holdings Empire"
        }
        
        payload = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": request.stream
        }
        
        response = await self.http_client.post(
            f"{provider.base_url}/chat/completions",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            choice = data["choices"][0]
            usage = data.get("usage", {})
            
            return APIResponse(
                content=choice["message"]["content"],
                provider="openrouter",
                model=request.model,
                tokens_used={
                    "input": usage.get("prompt_tokens", 0),
                    "output": usage.get("completion_tokens", 0)
                },
                cost=self._calculate_cost(provider, usage),
                latency_ms=0,  # Will be set by caller
                success=True
            )
        else:
            raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
    
    async def _call_groq(self, provider: APIProvider, request: APIRequest) -> APIResponse:
        """Call Groq Cloud API (OpenAI compatible)"""
        return await self._call_openai_compatible(provider, request, provider_name="groq")
    
    async def _call_google_ai(self, provider: APIProvider, request: APIRequest) -> APIResponse:
        """Call Google AI Studio API"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            raise ValueError(f"Missing {provider.api_key_env}")
        
        # Convert OpenAI format to Google format
        parts = []
        for msg in request.messages:
            if msg["role"] == "user":
                parts.append({"text": msg["content"]})
        
        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": request.temperature,
                "maxOutputTokens": request.max_tokens
            }
        }
        
        url = f"{provider.base_url}/models/{request.model}:generateContent?key={api_key}"
        
        response = await self.http_client.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            content = data["candidates"][0]["content"]["parts"][0]["text"]
            
            return APIResponse(
                content=content,
                provider="google_ai",
                model=request.model,
                tokens_used={"input": 0, "output": 0},  # Google doesn't provide exact counts
                cost=0.0,  # Would need to estimate
                latency_ms=0,
                success=True
            )
        else:
            raise Exception(f"Google AI error: {response.status_code} - {response.text}")
    
    async def _call_ollama(self, provider: APIProvider, request: APIRequest) -> APIResponse:
        """Call local Ollama API"""
        payload = {
            "model": request.model,
            "messages": request.messages,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens
            }
        }
        
        try:
            response = await self.http_client.post(
                f"{provider.base_url}/api/chat",
                json=payload
            )
            
            if response.status_code == 200:
                data = response.json()
                return APIResponse(
                    content=data["message"]["content"],
                    provider="ollama",
                    model=request.model,
                    tokens_used={"input": 0, "output": 0},
                    cost=0.0,  # Local is free
                    latency_ms=0,
                    success=True
                )
            else:
                raise Exception(f"Ollama error: {response.status_code}")
        except httpx.ConnectError:
            raise Exception("Ollama not running. Start with: ollama serve")
    
    async def _call_deepseek(self, provider: APIProvider, request: APIRequest) -> APIResponse:
        """Call DeepSeek API"""
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise ValueError("Missing DEEPSEEK_API_KEY")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": request.model or "deepseek-reasoner",
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": request.stream
        }
        
        try:
            response = await self.http_client.post(
                f"{provider.base_url}/v1/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                choice = data["choices"][0]
                usage = data.get("usage", {})
                
                return APIResponse(
                    content=choice["message"]["content"],
                    provider="deepseek",
                    model=request.model or "deepseek-chat",
                    tokens_used={
                        "input": usage.get("prompt_tokens", 0),
                        "output": usage.get("completion_tokens", 0)
                    },
                    cost=self._calculate_cost(provider, usage),
                    latency_ms=0,
                    success=True
                )
            else:
                raise Exception(f"DeepSeek API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            return APIResponse(
                content="",
                provider="deepseek", 
                model=request.model or "deepseek-chat",
                tokens_used={"input": 0, "output": 0},
                cost=0.0,
                latency_ms=0,
                success=False,
                error=str(e)
            )
    
    async def _call_openai_compatible(self, provider: APIProvider, 
                                     request: APIRequest, 
                                     provider_name: str = None) -> APIResponse:
        """Call OpenAI-compatible APIs (Groq, Anthropic via proxy, etc.)"""
        api_key = os.getenv(provider.api_key_env)
        if not api_key:
            raise ValueError(f"Missing {provider.api_key_env}")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        
        response = await self.http_client.post(
            f"{provider.base_url}/chat/completions",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            choice = data["choices"][0]
            usage = data.get("usage", {})
            
            return APIResponse(
                content=choice["message"]["content"],
                provider=provider_name or provider.name.lower(),
                model=request.model,
                tokens_used={
                    "input": usage.get("prompt_tokens", 0),
                    "output": usage.get("completion_tokens", 0)
                },
                cost=self._calculate_cost(provider, usage),
                latency_ms=0,
                success=True
            )
        else:
            raise Exception(f"{provider.name} API error: {response.status_code} - {response.text}")
    
    async def _call_existing_client(self, provider: str, request: APIRequest) -> APIResponse:
        """Use existing memu LLM clients"""
        if provider not in self.llm_clients:
            raise ValueError(f"Client not available: {provider}")
        
        client = self.llm_clients[provider]
        
        # Convert to existing client format
        llm_response = client.chat_completion(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return APIResponse(
            content=llm_response.content,
            provider=provider,
            model=llm_response.model,
            tokens_used=llm_response.usage,
            cost=0.0,  # Would need provider-specific calculation
            latency_ms=0,
            success=llm_response.success,
            error=llm_response.error
        )
    
    def _calculate_cost(self, provider: APIProvider, usage: Dict[str, int]) -> float:
        """Calculate request cost"""
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        total_tokens = input_tokens + output_tokens
        return total_tokens * provider.cost_per_token
    
    async def get_available_models(self, provider: str = None) -> Dict[str, List[str]]:
        """Get available models for provider(s)"""
        if provider:
            return {provider: self.providers[provider].models}
        else:
            return {name: config.models for name, config in self.providers.items()}
    
    async def health_check(self) -> Dict[str, Dict[str, Any]]:
        """Check health of all providers"""
        health_status = {}
        
        for provider_name, provider in self.providers.items():
            try:
                # Simple test request
                test_request = APIRequest(
                    provider=provider_name,
                    model=provider.models[0],
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=10
                )
                
                response = await self._execute_request(provider_name, test_request)
                
                health_status[provider_name] = {
                    "status": "healthy" if response.success else "unhealthy",
                    "latency_ms": response.latency_ms,
                    "error": response.error,
                    "models_available": len(provider.models),
                    "capabilities": provider.capabilities
                }
                
            except Exception as e:
                health_status[provider_name] = {
                    "status": "unhealthy",
                    "error": str(e),
                    "models_available": len(provider.models),
                    "capabilities": provider.capabilities
                }
        
        return health_status
    
    async def benchmark_providers(self, test_prompt: str = "Hello, how are you?") -> Dict[str, Dict[str, Any]]:
        """Benchmark all providers for speed and cost"""
        results = {}
        
        for provider_name, provider in self.providers.items():
            if not provider.models:
                continue
                
            try:
                test_request = APIRequest(
                    provider=provider_name,
                    model=provider.models[0],
                    messages=[{"role": "user", "content": test_prompt}],
                    max_tokens=100
                )
                
                response = await self.route_request(test_request, optimization="auto")
                
                results[provider_name] = {
                    "latency_ms": response.latency_ms,
                    "cost": response.cost,
                    "success": response.success,
                    "speed_rating": provider.speed_rating,
                    "tokens_per_second": response.tokens_used.get("output", 0) / max(response.latency_ms / 1000, 0.1)
                }
                
            except Exception as e:
                results[provider_name] = {
                    "latency_ms": -1,
                    "cost": -1,
                    "success": False,
                    "error": str(e),
                    "speed_rating": provider.speed_rating
                }
        
        return results
    
    # High-level convenience methods
    async def chat(self, prompt: str, optimization: str = "auto", **kwargs) -> str:
        """Simple chat interface"""
        request = APIRequest(
            provider="auto",
            model="auto",
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        
        response = await self.route_request(request, optimization=optimization)
        return response.content if response.success else f"Error: {response.error}"
    
    async def fast_chat(self, prompt: str, **kwargs) -> str:
        """Ultra-fast chat via Groq"""
        return await self.chat(prompt, optimization="speed_priority", **kwargs)
    
    async def cheap_chat(self, prompt: str, **kwargs) -> str:
        """Cost-effective chat via Ollama"""  
        return await self.chat(prompt, optimization="cost_priority", **kwargs)
    
    async def smart_chat(self, prompt: str, **kwargs) -> str:
        """High-quality chat via Claude"""
        return await self.chat(prompt, optimization="quality_priority", **kwargs)
    
    async def code_chat(self, prompt: str, **kwargs) -> str:
        """Coding-optimized chat via DeepSeek"""
        return await self.chat(prompt, optimization="coding_priority", **kwargs)

# CLI Interface
async def main():
    orchestrator = UniversalAPIOrchestrator()
    
    print("🌐 UNIVERSAL API ORCHESTRATOR")
    print("=" * 50)
    print("Connecting ALL AI services seamlessly...")
    
    # Health check
    print("\n🏥 PROVIDER HEALTH CHECK:")
    health = await orchestrator.health_check()
    for provider, status in health.items():
        emoji = "✅" if status["status"] == "healthy" else "❌"
        print(f"{emoji} {provider}: {status['status']}")
        if status.get('error'):
            print(f"    Error: {status['error']}")
    
    # Show available models
    print("\n🤖 AVAILABLE MODELS:")
    models = await orchestrator.get_available_models()
    for provider, model_list in models.items():
        print(f"📚 {provider}: {len(model_list)} models")
        for model in model_list[:3]:  # Show first 3
            print(f"  • {model}")
        if len(model_list) > 3:
            print(f"  • ... and {len(model_list) - 3} more")
    
    # Test different optimizations
    print("\n🧪 TESTING OPTIMIZATIONS:")
    test_prompt = "Write a Python function to calculate fibonacci numbers"
    
    optimizations = [
        ("speed_priority", "⚡ Fastest"),
        ("cost_priority", "💰 Cheapest"), 
        ("quality_priority", "🧠 Smartest"),
        ("coding_priority", "💻 Best for Code")
    ]
    
    for opt_key, opt_name in optimizations:
        try:
            response = await orchestrator.chat(test_prompt, optimization=opt_key, max_tokens=100)
            print(f"{opt_name}: {response[:100]}...")
        except Exception as e:
            print(f"{opt_name}: Error - {e}")
    
    print("\n🎉 UNIVERSAL API ORCHESTRATOR READY!")
    print("All your AI services are now seamlessly connected!")

if __name__ == "__main__":
    asyncio.run(main())