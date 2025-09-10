#!/usr/bin/env python3
"""
Test script for Repository MCP Server
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append('src')

from integrations.repository_mcp_server import RepositoryMCPServer

async def test_mcp_server():
    """Test basic MCP server functionality"""
    print("🧪 Testing Repository MCP Server...")
    
    # Initialize server
    server = RepositoryMCPServer()
    print("✅ MCP Server initialized")
    
    # Test local repository scanning
    print("🔍 Testing local repository scanning...")
    local_repos = await server._scan_local_repos()
    print(f"✅ Found {len(local_repos)} local repositories")
    
    # Test repository listing
    print("📋 Testing repository listing...")
    repos = await server.list_repositories(include_local=True)
    print(f"✅ Listed {len(repos)} repositories")
    
    # Test configuration
    print("⚙️ Testing configuration...")
    print(f"✅ Local repos path: {server.config['local_repos_path']}")
    print(f"✅ GitHub token configured: {'Yes' if server.config['github_token'] else 'No'}")
    print(f"✅ OpenAI API key configured: {'Yes' if server.config['embedding']['api_key'] else 'No'}")
    
    print("\n🎉 All tests passed! MCP Server is ready to use.")
    
    # Show available repositories
    if repos:
        print("\n📚 Available repositories:")
        for repo in repos[:5]:  # Show first 5
            print(f"  - {repo['name']} ({repo.get('language', 'Unknown')})")
        if len(repos) > 5:
            print(f"  ... and {len(repos) - 5} more")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
