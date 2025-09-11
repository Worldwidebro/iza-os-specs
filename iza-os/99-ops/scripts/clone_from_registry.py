#!/usr/bin/env python3
"""
Clone all repositories from the IZA OS registry.json file
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List

def clone_repositories(registry_path: str, base_dir: str = "."):
    """Clone all repositories from the IZA OS registry"""
    
    with open(registry_path, 'r') as f:
        registry = json.load(f)
    
    print(f"🚀 IZA OS Repository Cloning")
    print(f"==========================")
    print(f"Cloning repositories for: {registry['iza_os']['name']}")
    print(f"Version: {registry['iza_os']['version']}")
    print("")
    
    for category, repos in registry['repositories'].items():
        category_dir = Path(base_dir) / category.replace('_', '-')
        category_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 {category.upper()}: {len(repos)} repositories")
        
        for repo_url in repos:
            repo_name = repo_url.split('/')[-1].replace('.git', '')
            repo_dir = category_dir / repo_name
            
            if repo_dir.exists():
                print(f"  🔄 Updating {repo_name}...")
                subprocess.run(['git', '-C', str(repo_dir), 'pull'], check=False)
            else:
                print(f"  📥 Cloning {repo_name}...")
                subprocess.run(['git', 'clone', '--depth', '1', repo_url, str(repo_dir)], check=False)
        
        print("")
    
    print("✅ IZA OS repository cloning complete!")
    print("📱 Mobile access ready at: http://YOUR_IP:3000")

if __name__ == "__main__":
    import sys
    registry_path = sys.argv[1] if len(sys.argv) > 1 else "00-meta/registry/repos.json"
    clone_repositories(registry_path)
