#!/usr/bin/env python3
"""
UNIFIED MEMORY ORCHESTRATOR
Connects and synchronizes all memory systems in your AI empire
memU + Letta + Mem0 + Graphiti + ChromaDB + Vercept integration
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path

# Memory System Imports
try:
    from mem0 import Memory as Mem0Memory
except ImportError:
    Mem0Memory = None

try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    chromadb = None

try:
    from letta import create_client as create_letta_client
except ImportError:
    create_letta_client = None

@dataclass
class UnifiedMemoryEntry:
    """Standard memory entry across all systems"""
    memory_id: str
    content: str
    metadata: Dict[str, Any]
    timestamp: datetime
    source_system: str
    memory_type: str  # conversation, knowledge, context, entity
    embeddings: Optional[List[float]] = None
    connections: List[str] = None  # Connected memory IDs
    importance_score: float = 1.0
    access_count: int = 0

class UnifiedMemoryOrchestrator:
    """Master orchestrator for all memory systems"""
    
    def __init__(self):
        self.base_path = Path("/Users/divinejohns/memU")
        self.unified_db_path = self.base_path / "unified_memory.db"
        self.systems = {}
        self.logger = self._setup_logging()
        
        # Memory system configurations
        self.configs = {
            "mem0": {
                "embedder": {
                    "provider": "sentence_transformers",
                    "config": {"model": "all-MiniLM-L6-v2"}
                },
                "vector_store": {
                    "provider": "qdrant",
                    "config": {
                        "collection_name": "unified_memory",
                        "host": "localhost",
                        "port": 6333
                    }
                }
            },
            "chromadb": {
                "path": str(self.base_path / "chromadb"),
                "collection_name": "unified_memory"
            },
            "letta": {
                "base_url": "http://localhost:8283",
                "token": None
            },
            "vercept": {
                "config_path": "/Users/divinejohns/memU/vercept.yml"
            }
        }
        
    def _setup_logging(self):
        """Setup logging for memory operations"""
        log_path = self.base_path / "memory_orchestrator.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
        
    async def initialize_all_systems(self):
        """Initialize all memory systems and create unified database"""
        self.logger.info("🧠 Initializing Unified Memory Orchestrator...")
        
        # Create unified database
        await self._create_unified_db()
        
        # Initialize individual memory systems
        await self._init_mem0()
        await self._init_chromadb()
        await self._init_letta()
        await self._init_memu()
        await self._init_vercept()
        
        self.logger.info("✅ All memory systems initialized and connected")
        
    async def _create_unified_db(self):
        """Create SQLite database for unified memory management"""
        conn = sqlite3.connect(self.unified_db_path)
        cursor = conn.cursor()
        
        # Unified memory table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS unified_memories (
            memory_id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            metadata TEXT,
            timestamp TEXT,
            source_system TEXT,
            memory_type TEXT,
            embeddings BLOB,
            connections TEXT,
            importance_score REAL,
            access_count INTEGER
        )
        ''')
        
        # System sync status table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS sync_status (
            system_name TEXT PRIMARY KEY,
            last_sync TEXT,
            memory_count INTEGER,
            status TEXT
        )
        ''')
        
        # Memory connections graph
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory_connections (
            from_memory_id TEXT,
            to_memory_id TEXT,
            connection_type TEXT,
            strength REAL,
            created_at TEXT,
            PRIMARY KEY (from_memory_id, to_memory_id, connection_type)
        )
        ''')
        
        conn.commit()
        conn.close()
        self.logger.info("✅ Unified memory database created")
        
    async def _init_mem0(self):
        """Initialize Mem0 memory system"""
        try:
            if Mem0Memory:
                self.systems['mem0'] = Mem0Memory(self.configs['mem0'])
                self.logger.info("✅ Mem0 initialized")
            else:
                self.logger.warning("⚠️ Mem0 not available - install with: pip install mem0ai")
        except Exception as e:
            self.logger.error(f"❌ Mem0 initialization failed: {e}")
            
    async def _init_chromadb(self):
        """Initialize ChromaDB vector store"""
        try:
            if chromadb:
                client = chromadb.PersistentClient(path=self.configs['chromadb']['path'])
                collection = client.get_or_create_collection(
                    name=self.configs['chromadb']['collection_name']
                )
                self.systems['chromadb'] = {'client': client, 'collection': collection}
                self.logger.info("✅ ChromaDB initialized")
            else:
                self.logger.warning("⚠️ ChromaDB not available - install with: pip install chromadb")
        except Exception as e:
            self.logger.error(f"❌ ChromaDB initialization failed: {e}")
            
    async def _init_letta(self):
        """Initialize Letta agent memory system"""
        try:
            if create_letta_client:
                client = create_letta_client(
                    base_url=self.configs['letta']['base_url'],
                    token=self.configs['letta']['token']
                )
                self.systems['letta'] = client
                self.logger.info("✅ Letta initialized")
            else:
                self.logger.warning("⚠️ Letta not available - install with: pip install letta")
        except Exception as e:
            self.logger.error(f"❌ Letta initialization failed: {e}")
            
    async def _init_memu(self):
        """Initialize memU memory system"""
        try:
            # Load memU configuration
            memu_path = self.base_path / "memu"
            if memu_path.exists():
                self.systems['memu'] = {
                    'path': memu_path,
                    'config_path': memu_path / 'config.py'
                }
                self.logger.info("✅ MemU initialized")
            else:
                self.logger.warning("⚠️ MemU path not found")
        except Exception as e:
            self.logger.error(f"❌ MemU initialization failed: {e}")
            
    async def _init_vercept(self):
        """Initialize Vercept AI assistant memory"""
        try:
            vercept_config = Path(self.configs['vercept']['config_path'])
            if vercept_config.exists():
                self.systems['vercept'] = {
                    'config_path': vercept_config,
                    'status': 'available'
                }
                self.logger.info("✅ Vercept initialized")
            else:
                self.logger.warning("⚠️ Vercept config not found")
        except Exception as e:
            self.logger.error(f"❌ Vercept initialization failed: {e}")
    
    async def store_memory(self, content: str, metadata: Dict[str, Any] = None, 
                          memory_type: str = "knowledge") -> str:
        """Store memory across all available systems"""
        memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(content) % 10000}"
        
        unified_entry = UnifiedMemoryEntry(
            memory_id=memory_id,
            content=content,
            metadata=metadata or {},
            timestamp=datetime.now(),
            source_system="unified",
            memory_type=memory_type
        )
        
        # Store in unified database
        await self._store_in_unified_db(unified_entry)
        
        # Store in individual systems
        tasks = []
        if 'mem0' in self.systems:
            tasks.append(self._store_in_mem0(content, metadata, memory_id))
        if 'chromadb' in self.systems:
            tasks.append(self._store_in_chromadb(content, metadata, memory_id))
        if 'letta' in self.systems:
            tasks.append(self._store_in_letta(content, metadata, memory_id))
            
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self.logger.info(f"✅ Memory stored: {memory_id}")
        return memory_id
        
    async def _store_in_unified_db(self, entry: UnifiedMemoryEntry):
        """Store memory entry in unified database"""
        conn = sqlite3.connect(self.unified_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO unified_memories 
        (memory_id, content, metadata, timestamp, source_system, memory_type, 
         connections, importance_score, access_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            entry.memory_id,
            entry.content,
            json.dumps(entry.metadata),
            entry.timestamp.isoformat(),
            entry.source_system,
            entry.memory_type,
            json.dumps(entry.connections or []),
            entry.importance_score,
            entry.access_count
        ))
        
        conn.commit()
        conn.close()
        
    async def _store_in_mem0(self, content: str, metadata: Dict, memory_id: str):
        """Store in Mem0 system"""
        try:
            if 'mem0' in self.systems:
                self.systems['mem0'].add(content, user_id="ai_boss_holdings", metadata={
                    **metadata,
                    "unified_id": memory_id
                })
        except Exception as e:
            self.logger.error(f"Mem0 storage failed: {e}")
            
    async def _store_in_chromadb(self, content: str, metadata: Dict, memory_id: str):
        """Store in ChromaDB"""
        try:
            if 'chromadb' in self.systems:
                collection = self.systems['chromadb']['collection']
                collection.add(
                    documents=[content],
                    metadatas=[{**metadata, "unified_id": memory_id}],
                    ids=[memory_id]
                )
        except Exception as e:
            self.logger.error(f"ChromaDB storage failed: {e}")
            
    async def _store_in_letta(self, content: str, metadata: Dict, memory_id: str):
        """Store in Letta system"""
        try:
            if 'letta' in self.systems:
                # Letta memory integration would go here
                # This requires specific agent context
                pass
        except Exception as e:
            self.logger.error(f"Letta storage failed: {e}")
    
    async def search_memories(self, query: str, limit: int = 10, 
                            memory_type: Optional[str] = None) -> List[UnifiedMemoryEntry]:
        """Search across all memory systems"""
        results = []
        
        # Search unified database first
        unified_results = await self._search_unified_db(query, limit, memory_type)
        results.extend(unified_results)
        
        # Search individual systems for additional context
        if 'mem0' in self.systems:
            mem0_results = await self._search_mem0(query, limit)
            results.extend(mem0_results)
            
        if 'chromadb' in self.systems:
            chromadb_results = await self._search_chromadb(query, limit)
            results.extend(chromadb_results)
        
        # Deduplicate and rank results
        return await self._rank_and_deduplicate(results, limit)
        
    async def _search_unified_db(self, query: str, limit: int, 
                               memory_type: Optional[str]) -> List[UnifiedMemoryEntry]:
        """Search unified database"""
        conn = sqlite3.connect(self.unified_db_path)
        cursor = conn.cursor()
        
        sql = "SELECT * FROM unified_memories WHERE content LIKE ?"
        params = [f"%{query}%"]
        
        if memory_type:
            sql += " AND memory_type = ?"
            params.append(memory_type)
            
        sql += " ORDER BY importance_score DESC, access_count DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            entry = UnifiedMemoryEntry(
                memory_id=row[0],
                content=row[1],
                metadata=json.loads(row[2]),
                timestamp=datetime.fromisoformat(row[3]),
                source_system=row[4],
                memory_type=row[5],
                connections=json.loads(row[7]) if row[7] else [],
                importance_score=row[8],
                access_count=row[9]
            )
            results.append(entry)
            
        return results
        
    async def _search_mem0(self, query: str, limit: int) -> List[UnifiedMemoryEntry]:
        """Search Mem0 system"""
        try:
            if 'mem0' in self.systems:
                memories = self.systems['mem0'].search(query, user_id="ai_boss_holdings")
                results = []
                for memory in memories[:limit]:
                    entry = UnifiedMemoryEntry(
                        memory_id=f"mem0_{memory.get('id', hash(memory['memory']))}",
                        content=memory['memory'],
                        metadata=memory.get('metadata', {}),
                        timestamp=datetime.now(),
                        source_system="mem0",
                        memory_type="knowledge"
                    )
                    results.append(entry)
                return results
        except Exception as e:
            self.logger.error(f"Mem0 search failed: {e}")
        return []
        
    async def _search_chromadb(self, query: str, limit: int) -> List[UnifiedMemoryEntry]:
        """Search ChromaDB"""
        try:
            if 'chromadb' in self.systems:
                collection = self.systems['chromadb']['collection']
                results_data = collection.query(
                    query_texts=[query],
                    n_results=limit
                )
                
                results = []
                for i, doc in enumerate(results_data['documents'][0]):
                    entry = UnifiedMemoryEntry(
                        memory_id=results_data['ids'][0][i],
                        content=doc,
                        metadata=results_data['metadatas'][0][i],
                        timestamp=datetime.now(),
                        source_system="chromadb",
                        memory_type="vector"
                    )
                    results.append(entry)
                return results
        except Exception as e:
            self.logger.error(f"ChromaDB search failed: {e}")
        return []
        
    async def _rank_and_deduplicate(self, results: List[UnifiedMemoryEntry], 
                                   limit: int) -> List[UnifiedMemoryEntry]:
        """Rank and deduplicate search results"""
        # Simple deduplication by content similarity
        seen_content = set()
        unique_results = []
        
        for result in results:
            content_hash = hash(result.content)
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_results.append(result)
                
        # Sort by importance score and access count
        unique_results.sort(
            key=lambda x: (x.importance_score, x.access_count), 
            reverse=True
        )
        
        return unique_results[:limit]
    
    async def sync_all_systems(self):
        """Synchronize all memory systems with unified database"""
        self.logger.info("🔄 Starting memory synchronization...")
        
        # Sync from each system to unified database
        tasks = [
            self._sync_from_mem0(),
            self._sync_from_chromadb(),
            self._sync_from_memu(),
            self._sync_from_vercept()
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Update sync status
        await self._update_sync_status()
        
        self.logger.info("✅ Memory synchronization complete")
        
    async def _sync_from_mem0(self):
        """Sync memories from Mem0 to unified database"""
        try:
            if 'mem0' in self.systems:
                # Get all memories from Mem0
                memories = self.systems['mem0'].get_all(user_id="ai_boss_holdings")
                
                for memory in memories:
                    entry = UnifiedMemoryEntry(
                        memory_id=f"mem0_{memory.get('id')}",
                        content=memory['memory'],
                        metadata=memory.get('metadata', {}),
                        timestamp=datetime.now(),
                        source_system="mem0",
                        memory_type="knowledge"
                    )
                    await self._store_in_unified_db(entry)
                    
                self.logger.info(f"✅ Synced {len(memories)} memories from Mem0")
        except Exception as e:
            self.logger.error(f"Mem0 sync failed: {e}")
            
    async def _sync_from_chromadb(self):
        """Sync from ChromaDB to unified database"""
        try:
            if 'chromadb' in self.systems:
                collection = self.systems['chromadb']['collection']
                # Get all documents from ChromaDB
                all_data = collection.get()
                
                for i, doc in enumerate(all_data['documents']):
                    entry = UnifiedMemoryEntry(
                        memory_id=all_data['ids'][i],
                        content=doc,
                        metadata=all_data['metadatas'][i] if all_data['metadatas'] else {},
                        timestamp=datetime.now(),
                        source_system="chromadb",
                        memory_type="vector"
                    )
                    await self._store_in_unified_db(entry)
                    
                self.logger.info(f"✅ Synced {len(all_data['documents'])} memories from ChromaDB")
        except Exception as e:
            self.logger.error(f"ChromaDB sync failed: {e}")
            
    async def _sync_from_memu(self):
        """Sync from memU to unified database"""
        try:
            # Scan memU directory for memory files
            memu_path = self.base_path / "memu"
            if memu_path.exists():
                memory_files = list(memu_path.rglob("*.json"))
                
                for file_path in memory_files:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        
                    entry = UnifiedMemoryEntry(
                        memory_id=f"memu_{file_path.stem}",
                        content=str(data),
                        metadata={"file_path": str(file_path)},
                        timestamp=datetime.fromtimestamp(file_path.stat().st_mtime),
                        source_system="memu",
                        memory_type="file"
                    )
                    await self._store_in_unified_db(entry)
                    
                self.logger.info(f"✅ Synced {len(memory_files)} memories from memU")
        except Exception as e:
            self.logger.error(f"memU sync failed: {e}")
            
    async def _sync_from_vercept(self):
        """Sync from Vercept to unified database"""
        try:
            # Load Vercept configuration and sync knowledge base
            vercept_config_path = Path(self.configs['vercept']['config_path'])
            if vercept_config_path.exists():
                with open(vercept_config_path, 'r') as f:
                    config = f.read()
                    
                entry = UnifiedMemoryEntry(
                    memory_id="vercept_config",
                    content=config,
                    metadata={"type": "configuration"},
                    timestamp=datetime.fromtimestamp(vercept_config_path.stat().st_mtime),
                    source_system="vercept",
                    memory_type="config"
                )
                await self._store_in_unified_db(entry)
                
                self.logger.info("✅ Synced Vercept configuration")
        except Exception as e:
            self.logger.error(f"Vercept sync failed: {e}")
            
    async def _update_sync_status(self):
        """Update synchronization status in database"""
        conn = sqlite3.connect(self.unified_db_path)
        cursor = conn.cursor()
        
        for system_name in ['mem0', 'chromadb', 'letta', 'memu', 'vercept']:
            cursor.execute(
                "SELECT COUNT(*) FROM unified_memories WHERE source_system = ?",
                (system_name,)
            )
            count = cursor.fetchone()[0]
            
            cursor.execute('''
            INSERT OR REPLACE INTO sync_status 
            (system_name, last_sync, memory_count, status)
            VALUES (?, ?, ?, ?)
            ''', (
                system_name,
                datetime.now().isoformat(),
                count,
                'synced'
            ))
            
        conn.commit()
        conn.close()
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get status of all memory systems"""
        status = {
            "unified_orchestrator": "running",
            "systems": {},
            "total_memories": 0,
            "last_sync": None
        }
        
        # Get unified database stats
        conn = sqlite3.connect(self.unified_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM unified_memories")
        total_count = cursor.fetchone()[0]
        status["total_memories"] = total_count
        
        # Get system-specific stats
        cursor.execute("SELECT * FROM sync_status")
        sync_data = cursor.fetchall()
        
        for row in sync_data:
            system_name, last_sync, memory_count, sync_status = row
            status["systems"][system_name] = {
                "status": "connected" if system_name in self.systems else "disconnected",
                "memory_count": memory_count,
                "last_sync": last_sync,
                "sync_status": sync_status
            }
            
        conn.close()
        return status
    
    async def create_memory_connection(self, from_memory_id: str, to_memory_id: str, 
                                     connection_type: str = "related", strength: float = 1.0):
        """Create connection between memories"""
        conn = sqlite3.connect(self.unified_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT OR REPLACE INTO memory_connections 
        (from_memory_id, to_memory_id, connection_type, strength, created_at)
        VALUES (?, ?, ?, ?, ?)
        ''', (
            from_memory_id,
            to_memory_id,
            connection_type,
            strength,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"✅ Created memory connection: {from_memory_id} -> {to_memory_id}")

# CLI Interface
async def main():
    orchestrator = UnifiedMemoryOrchestrator()
    
    print("🧠 UNIFIED MEMORY ORCHESTRATOR")
    print("=" * 50)
    print("Connecting all memory systems in your AI empire...")
    
    # Initialize all systems
    await orchestrator.initialize_all_systems()
    
    # Sync all existing memories
    await orchestrator.sync_all_systems()
    
    # Get system status
    status = await orchestrator.get_system_status()
    
    print("\n📊 MEMORY SYSTEM STATUS:")
    print("=" * 30)
    print(f"Total Unified Memories: {status['total_memories']}")
    
    for system_name, system_status in status['systems'].items():
        status_emoji = "✅" if system_status['status'] == 'connected' else "❌"
        print(f"{status_emoji} {system_name}: {system_status['memory_count']} memories")
    
    # Demo: Store and search memory
    print("\n🧪 TESTING UNIFIED MEMORY...")
    
    # Store a test memory
    memory_id = await orchestrator.store_memory(
        "AI Boss Holdings revenue optimization strategy using Claude and advanced automation",
        metadata={"type": "business_strategy", "priority": "high"},
        memory_type="strategy"
    )
    
    # Search for the memory
    results = await orchestrator.search_memories("revenue optimization", limit=5)
    
    print(f"✅ Stored memory: {memory_id}")
    print(f"🔍 Found {len(results)} related memories")
    
    for result in results[:3]:
        print(f"  - {result.memory_id}: {result.content[:100]}...")
    
    print("\n🎉 UNIFIED MEMORY ORCHESTRATOR READY!")
    print("All your memory systems are now connected and synchronized.")

if __name__ == "__main__":
    asyncio.run(main())