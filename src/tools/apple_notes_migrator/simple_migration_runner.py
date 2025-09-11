#!/usr/bin/env python3
"""
Simple Apple Notes to Obsidian Migration Runner
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path so we can import the migration script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def run_migration():
    if len(sys.argv) < 2:
        print("Usage: python simple_migration_runner.py /path/to/obsidian/vault")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    vault_path = str(Path(vault_path).expanduser().resolve())
    
    print(f"➡️ Starting Apple Notes Migration to {vault_path}")
    
    vault_dir = Path(vault_path)
    if not vault_dir.exists():
        vault_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        from real_migration_script import migrate_with_mcp
        results = await migrate_with_mcp(vault_path)
        
        if results.get('status') == 'success':
            print("✅ SUCCESS! Your Apple Notes have been migrated to Obsidian!")
            print(f"  Notes migrated: {results.get('notes_processed', 0)}")
        else:
            print(f"❌ Migration failed: {results.get('error', 'Unknown error')}")
    
    except ImportError as e:
        print(f"❌ Could not import migration script: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(run_migration())
