"""
Cursor IDE Integration Script
Connects the Repository MCP Server to Cursor
"""

import json
import os
from pathlib import Path

def setup_cursor_mcp_integration():
    """Setup Cursor to connect to our MCP server"""
    
    # Cursor configuration path (adjust for your OS)
    if os.name == 'nt':  # Windows
        cursor_config_path = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json"
    else:  # macOS/Linux
        cursor_config_path = Path.home() / ".cursor" / "settings.json"
    
    # MCP server configuration
    mcp_config = {
        "mcp.servers": {
            "repository-server": {
                "command": "python",
                "args": ["/Users/divinejohns/memU/iza-os-production/src/integrations/repository_mcp_server.py"],
                "env": {
                    "GITHUB_TOKEN": "${GITHUB_TOKEN}",
                    "OPENAI_API_KEY": "${OPENAI_API_KEY}"
                }
            }
        },
        "mcp.client.timeout": 30000,
        "mcp.client.retries": 3
    }
    
    # Read existing Cursor settings
    existing_config = {}
    if cursor_config_path.exists():
        with open(cursor_config_path, 'r') as f:
            try:
                existing_config = json.load(f)
            except json.JSONDecodeError:
                existing_config = {}
    
    # Merge configurations
    existing_config.update(mcp_config)
    
    # Write back to Cursor config
    cursor_config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cursor_config_path, 'w') as f:
        json.dump(existing_config, f, indent=2)
    
    print(f"✅ Updated Cursor configuration at {cursor_config_path}")
    print("Restart Cursor to enable MCP integration")

if __name__ == "__main__":
    setup_cursor_mcp_integration()
