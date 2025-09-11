#!/usr/bin/env python3
"""
Database Manager for IZA OS - Production
Provides robust database abstraction with automatic failover and synchronization
"""

import asyncio
import json
import logging
import sqlite3
import time
from abc import ABC, abstractmethod
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from queue import Queue
from typing import Any, Dict, List, Optional, Tuple, Union
import threading

# Import management with fallbacks
import sys
sys.path.append('/Users/divinejohns/memU/iza-os-production/src')

try:
    from utils.import_manager import safe_import, import_from
    
    # Database imports
    psycopg2 = safe_import('psycopg2')
    asyncpg = safe_import('asyncpg')
    sqlalchemy = safe_import('sqlalchemy', required=True)
    redis = safe_import('redis')
    
except ImportError:
    # Fallback imports
    psycopg2 = None
    asyncpg = None
    sqlalchemy = None
    redis = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionStatus(Enum):
    """Database connection status"""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    RECONNECTING = "reconnecting"

class OperationType(Enum):
    """Types of database operations"""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE_TABLE = "create_table"
    DROP_TABLE = "drop_table"
    TRANSACTION = "transaction"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "iza_os"
    username: str = "postgres"
    password: str = ""
    pool_size: int = 5
    max_overflow: int = 10
    timeout: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class QueuedOperation:
    """Represents a queued database operation for sync"""
    id: str
    operation_type: OperationType
    table_name: str
    query: str
    params: Optional[Dict[str, Any]]
    timestamp: datetime
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'operation_type': self.operation_type.value,
            'table_name': self.table_name,
            'query': self.query,
            'params': self.params,
            'timestamp': self.timestamp.isoformat(),
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }

@dataclass
class QueryResult:
    """Result of a database query"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    duration: float = 0.0
    rows_affected: int = 0
    source: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class DatabaseConnection(ABC):
    """Abstract base class for database connections"""
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.status = ConnectionStatus.DISCONNECTED
        self.last_error: Optional[str] = None
        self.connection = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to database"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close database connection"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute a database query"""
        pass
    
    @abstractmethod
    async def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> QueryResult:
        """Execute query with multiple parameter sets"""
        pass
    
    @abstractmethod
    async def begin_transaction(self):
        """Begin a database transaction"""
        pass
    
    @abstractmethod
    async def commit_transaction(self):
        """Commit current transaction"""
        pass
    
    @abstractmethod
    async def rollback_transaction(self):
        """Rollback current transaction"""
        pass
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        return {
            'status': self.status.value,
            'last_error': self.last_error,
            'config': self.config.to_dict()
        }

class PostgreSQLConnection(DatabaseConnection):
    """PostgreSQL database connection implementation"""
    
    def __init__(self, config: DatabaseConfig):
        super().__init__(config)
        self.pool = None
    
    async def connect(self) -> bool:
        """Establish connection to PostgreSQL"""
        try:
            if asyncpg:
                # Use asyncpg for better async support
                connection_string = (
                    f"postgresql://{self.config.username}:{self.config.password}@"
                    f"{self.config.host}:{self.config.port}/{self.config.database}"
                )
                
                self.pool = await asyncpg.create_pool(
                    connection_string,
                    min_size=1,
                    max_size=self.config.pool_size,
                    command_timeout=self.config.timeout
                )
                
            elif psycopg2 and sqlalchemy:
                # Fallback to SQLAlchemy with psycopg2
                connection_string = (
                    f"postgresql+psycopg2://{self.config.username}:{self.config.password}@"
                    f"{self.config.host}:{self.config.port}/{self.config.database}"
                )
                
                engine = sqlalchemy.create_engine(
                    connection_string,
                    pool_size=self.config.pool_size,
                    max_overflow=self.config.max_overflow,
                    echo=False
                )
                
                self.pool = engine
            else:
                raise ImportError("No PostgreSQL driver available (asyncpg or psycopg2)")
            
            self.status = ConnectionStatus.CONNECTED
            logger.info("PostgreSQL connection established")
            return True
            
        except Exception as e:
            self.last_error = str(e)
            self.status = ConnectionStatus.ERROR
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Close PostgreSQL connection"""
        try:
            if self.pool:
                if asyncpg and hasattr(self.pool, 'close'):
                    await self.pool.close()
                elif sqlalchemy and hasattr(self.pool, 'dispose'):
                    self.pool.dispose()
                
                self.pool = None
            
            self.status = ConnectionStatus.DISCONNECTED
            logger.info("PostgreSQL connection closed")
            
        except Exception as e:
            logger.error(f"Error closing PostgreSQL connection: {e}")
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute query on PostgreSQL"""
        if not self.pool or self.status != ConnectionStatus.CONNECTED:
            return QueryResult(
                success=False,
                error="PostgreSQL connection not available",
                source="PostgreSQL"
            )
        
        start_time = time.time()
        
        try:
            if asyncpg and hasattr(self.pool, 'fetch'):
                # Using asyncpg
                async with self.pool.acquire() as conn:
                    if query.strip().lower().startswith('select'):
                        rows = await conn.fetch(query, **(params or {}))
                        data = [dict(row) for row in rows]
                        rows_affected = len(data)
                    else:
                        result = await conn.execute(query, **(params or {}))
                        data = None
                        rows_affected = int(result.split()[-1]) if result else 0
                    
            elif sqlalchemy:
                # Using SQLAlchemy
                with self.pool.connect() as conn:
                    result = conn.execute(sqlalchemy.text(query), params or {})
                    
                    if query.strip().lower().startswith('select'):
                        data = [dict(row) for row in result]
                        rows_affected = len(data)
                    else:
                        data = None
                        rows_affected = result.rowcount
                        conn.commit()
            
            else:
                raise Exception("No PostgreSQL driver available")
            
            duration = time.time() - start_time
            
            return QueryResult(
                success=True,
                data=data,
                duration=duration,
                rows_affected=rows_affected,
                source="PostgreSQL"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"PostgreSQL query failed: {str(e)}"
            logger.error(error_msg)
            
            return QueryResult(
                success=False,
                error=error_msg,
                duration=duration,
                source="PostgreSQL"
            )
    
    async def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> QueryResult:
        """Execute query with multiple parameter sets"""
        if not self.pool or self.status != ConnectionStatus.CONNECTED:
            return QueryResult(
                success=False,
                error="PostgreSQL connection not available",
                source="PostgreSQL"
            )
        
        start_time = time.time()
        
        try:
            total_affected = 0
            
            if asyncpg and hasattr(self.pool, 'executemany'):
                async with self.pool.acquire() as conn:
                    await conn.executemany(query, params_list)
                    total_affected = len(params_list)
                    
            elif sqlalchemy:
                with self.pool.connect() as conn:
                    result = conn.execute(sqlalchemy.text(query), params_list)
                    total_affected = result.rowcount
                    conn.commit()
            
            duration = time.time() - start_time
            
            return QueryResult(
                success=True,
                duration=duration,
                rows_affected=total_affected,
                source="PostgreSQL"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"PostgreSQL executemany failed: {str(e)}"
            logger.error(error_msg)
            
            return QueryResult(
                success=False,
                error=error_msg,
                duration=duration,
                source="PostgreSQL"
            )
    
    async def begin_transaction(self):
        """Begin transaction"""
        # Implementation depends on specific use case
        pass
    
    async def commit_transaction(self):
        """Commit transaction"""
        pass
    
    async def rollback_transaction(self):
        """Rollback transaction"""
        pass

class SQLiteConnection(DatabaseConnection):
    """SQLite database connection implementation"""
    
    def __init__(self, config: DatabaseConfig, db_path: str = "data/fallback.db"):
        super().__init__(config)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = None
        self._lock = threading.Lock()
    
    async def connect(self) -> bool:
        """Establish connection to SQLite"""
        try:
            # SQLite doesn't need explicit connection setup, but we can verify
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("SELECT 1")
            
            self.status = ConnectionStatus.CONNECTED
            logger.info(f"SQLite connection established at {self.db_path}")
            return True
            
        except Exception as e:
            self.last_error = str(e)
            self.status = ConnectionStatus.ERROR
            logger.error(f"Failed to connect to SQLite: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Close SQLite connection"""
        try:
            if self._connection:
                self._connection.close()
                self._connection = None
            
            self.status = ConnectionStatus.DISCONNECTED
            logger.info("SQLite connection closed")
            
        except Exception as e:
            logger.error(f"Error closing SQLite connection: {e}")
    
    @contextmanager
    def _get_connection(self):
        """Get thread-safe SQLite connection"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
            try:
                yield conn
            finally:
                conn.close()
    
    async def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> QueryResult:
        """Execute query on SQLite"""
        if self.status != ConnectionStatus.CONNECTED:
            return QueryResult(
                success=False,
                error="SQLite connection not available",
                source="SQLite"
            )
        
        start_time = time.time()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Convert dict params to tuple for SQLite if needed
                if params:
                    # Handle named parameters
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if query.strip().lower().startswith('select'):
                    rows = cursor.fetchall()
                    data = [dict(row) for row in rows]
                    rows_affected = len(data)
                else:
                    conn.commit()
                    data = None
                    rows_affected = cursor.rowcount
            
            duration = time.time() - start_time
            
            return QueryResult(
                success=True,
                data=data,
                duration=duration,
                rows_affected=rows_affected,
                source="SQLite"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"SQLite query failed: {str(e)}"
            logger.error(error_msg)
            
            return QueryResult(
                success=False,
                error=error_msg,
                duration=duration,
                source="SQLite"
            )
    
    async def execute_many(self, query: str, params_list: List[Dict[str, Any]]) -> QueryResult:
        """Execute query with multiple parameter sets"""
        if self.status != ConnectionStatus.CONNECTED:
            return QueryResult(
                success=False,
                error="SQLite connection not available",
                source="SQLite"
            )
        
        start_time = time.time()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                conn.commit()
                
                total_affected = cursor.rowcount
            
            duration = time.time() - start_time
            
            return QueryResult(
                success=True,
                duration=duration,
                rows_affected=total_affected,
                source="SQLite"
            )
            
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"SQLite executemany failed: {str(e)}"
            logger.error(error_msg)
            
            return QueryResult(
                success=False,
                error=error_msg,
                duration=duration,
                source="SQLite"
            )
    
    async def begin_transaction(self):
        """Begin transaction"""
        pass
    
    async def commit_transaction(self):
        """Commit transaction"""
        pass
    
    async def rollback_transaction(self):
        """Rollback transaction"""
        pass
    
    async def create_table_from_schema(self, table_name: str, postgres_schema: str) -> bool:
        """Create SQLite table from PostgreSQL schema"""
        try:
            # Convert PostgreSQL schema to SQLite
            sqlite_schema = self._convert_postgres_to_sqlite_schema(postgres_schema)
            
            create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({sqlite_schema})"
            result = await self.execute_query(create_query)
            
            return result.success
            
        except Exception as e:
            logger.error(f"Failed to create SQLite table {table_name}: {e}")
            return False
    
    def _convert_postgres_to_sqlite_schema(self, postgres_schema: str) -> str:
        """Convert PostgreSQL schema to SQLite compatible schema"""
        converted = postgres_schema.strip()
        
        # Handle SERIAL PRIMARY KEY specifically
        import re
        
        # Remove existing PRIMARY KEY constraints if SERIAL is present
        if 'SERIAL' in converted.upper():
            converted = re.sub(r'\s+PRIMARY\s+KEY', '', converted, flags=re.IGNORECASE)
        
        # Basic type conversions - escape special regex characters
        type_mappings = [
            (r'\bSERIAL\b', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
            (r'\bBIGSERIAL\b', 'INTEGER PRIMARY KEY AUTOINCREMENT'),
            (r'\bUUID\b', 'TEXT'),
            (r'\bTIMESTAMP\s+DEFAULT\s+CURRENT_TIMESTAMP\b', 'TEXT DEFAULT CURRENT_TIMESTAMP'),
            (r'\bTIMESTAMP\b', 'TEXT'),
            (r'\bTIMESTAMPTZ\b', 'TEXT'),
            (r'\bBOOLEAN\b', 'INTEGER'),
            (r'\bJSONB\b', 'TEXT'),
            (r'\bJSON\b', 'TEXT'),
            (r'\bVARCHAR\(', 'TEXT('),  # Keep length specification
            (r'\bVARCHAR\b', 'TEXT'),
        ]
        
        for pattern, replacement in type_mappings:
            converted = re.sub(pattern, replacement, converted, flags=re.IGNORECASE)
        
        # Clean up multiple spaces and extra commas
        converted = re.sub(r'\s+', ' ', converted)
        converted = re.sub(r',\s*,', ',', converted)
        
        return converted

class DataSyncManager:
    """Manages data synchronization between primary and fallback databases"""
    
    def __init__(self, sync_interval: int = 60):
        self.sync_queue = Queue()
        self.sync_interval = sync_interval
        self.running = False
        self.sync_thread = None
        self.logger = logger
    
    def queue_operation(self, operation: QueuedOperation) -> None:
        """Add operation to sync queue"""
        self.sync_queue.put(operation)
        logger.debug(f"Queued operation: {operation.id}")
    
    def start_sync_worker(self, database_manager) -> None:
        """Start background sync worker"""
        if self.running:
            return
        
        self.running = True
        self.sync_thread = threading.Thread(
            target=self._sync_worker,
            args=(database_manager,),
            daemon=True
        )
        self.sync_thread.start()
        logger.info("Data sync worker started")
    
    def stop_sync_worker(self) -> None:
        """Stop background sync worker"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        logger.info("Data sync worker stopped")
    
    def _sync_worker(self, database_manager) -> None:
        """Background worker for data synchronization"""
        while self.running:
            try:
                # Process queued operations
                operations_processed = 0
                
                while not self.sync_queue.empty() and operations_processed < 100:
                    try:
                        operation = self.sync_queue.get_nowait()
                        success = asyncio.run(self._replay_operation(database_manager, operation))
                        
                        if success:
                            logger.debug(f"Replayed operation: {operation.id}")
                        else:
                            operation.retry_count += 1
                            if operation.retry_count <= operation.max_retries:
                                self.sync_queue.put(operation)
                                logger.warning(f"Retrying operation: {operation.id}")
                            else:
                                logger.error(f"Failed to replay operation after max retries: {operation.id}")
                        
                        operations_processed += 1
                        
                    except Exception as e:
                        logger.error(f"Error processing sync operation: {e}")
                
                # Wait before next sync cycle
                time.sleep(self.sync_interval)
                
            except Exception as e:
                logger.error(f"Error in sync worker: {e}")
                time.sleep(5)  # Brief pause before retrying
    
    async def _replay_operation(self, database_manager, operation: QueuedOperation) -> bool:
        """Replay operation on primary database"""
        try:
            # Check if primary database is available
            if database_manager.primary.status != ConnectionStatus.CONNECTED:
                await database_manager.primary.connect()
            
            if database_manager.primary.status != ConnectionStatus.CONNECTED:
                return False
            
            # Execute the operation on primary database
            result = await database_manager.primary.execute_query(
                operation.query,
                operation.params
            )
            
            return result.success
            
        except Exception as e:
            logger.error(f"Failed to replay operation {operation.id}: {e}")
            return False
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get sync queue status"""
        return {
            'queue_size': self.sync_queue.qsize(),
            'running': self.running,
            'sync_interval': self.sync_interval
        }

class DatabaseManager:
    """Main database manager with failover and synchronization"""
    
    def __init__(
        self,
        primary_config: DatabaseConfig,
        fallback_db_path: str = "data/fallback.db"
    ):
        self.primary = PostgreSQLConnection(primary_config)
        self.fallback = SQLiteConnection(primary_config, fallback_db_path)
        self.sync_manager = DataSyncManager()
        self.logger = logger
        
        # Health check interval
        self._last_health_check = 0
        self._health_check_interval = 30  # seconds
    
    async def initialize(self) -> bool:
        """Initialize database connections"""
        logger.info("Initializing database manager...")
        
        # Try to connect to primary database
        primary_connected = await self.primary.connect()
        
        # Always ensure fallback is available
        fallback_connected = await self.fallback.connect()
        
        if not fallback_connected:
            logger.error("Failed to initialize fallback database")
            return False
        
        # Start sync worker if primary is available
        if primary_connected:
            self.sync_manager.start_sync_worker(self)
        
        logger.info(f"Database manager initialized. Primary: {'✓' if primary_connected else '✗'}, Fallback: {'✓' if fallback_connected else '✗'}")
        return True
    
    async def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        force_primary: bool = False
    ) -> QueryResult:
        """Execute query with automatic failover"""
        
        # Periodic health check
        await self._periodic_health_check()
        
        # Determine which database to use
        use_primary = (
            not force_primary or 
            self.primary.status == ConnectionStatus.CONNECTED
        )
        
        if use_primary and self.primary.status == ConnectionStatus.CONNECTED:
            # Try primary database first
            result = await self.primary.execute_query(query, params)
            
            if result.success:
                return result
            else:
                logger.warning("Primary database query failed, falling back to SQLite")
        
        # Use fallback database
        if self.fallback.status == ConnectionStatus.CONNECTED:
            result = await self.fallback.execute_query(query, params)
            
            # Queue write operations for sync when primary comes back
            if result.success and not query.strip().lower().startswith('select'):
                operation = QueuedOperation(
                    id=f"{int(time.time() * 1000)}_{hash(query) % 10000}",
                    operation_type=self._determine_operation_type(query),
                    table_name=self._extract_table_name(query),
                    query=query,
                    params=params,
                    timestamp=datetime.now()
                )
                self.sync_manager.queue_operation(operation)
            
            return result
        
        # Both databases failed
        return QueryResult(
            success=False,
            error="Both primary and fallback databases unavailable",
            source="None"
        )
    
    async def execute_many(
        self,
        query: str,
        params_list: List[Dict[str, Any]],
        force_primary: bool = False
    ) -> QueryResult:
        """Execute query with multiple parameter sets"""
        
        # Try primary first
        if not force_primary and self.primary.status == ConnectionStatus.CONNECTED:
            result = await self.primary.execute_many(query, params_list)
            if result.success:
                return result
        
        # Use fallback
        if self.fallback.status == ConnectionStatus.CONNECTED:
            result = await self.fallback.execute_many(query, params_list)
            
            # Queue for sync if successful
            if result.success:
                for params in params_list:
                    operation = QueuedOperation(
                        id=f"{int(time.time() * 1000)}_{hash(query) % 10000}_{hash(str(params)) % 1000}",
                        operation_type=self._determine_operation_type(query),
                        table_name=self._extract_table_name(query),
                        query=query,
                        params=params,
                        timestamp=datetime.now()
                    )
                    self.sync_manager.queue_operation(operation)
            
            return result
        
        return QueryResult(
            success=False,
            error="Both databases unavailable for executemany",
            source="None"
        )
    
    async def create_table(
        self,
        table_name: str,
        schema: str,
        create_in_fallback: bool = True
    ) -> QueryResult:
        """Create table in both databases"""
        
        # Create in primary
        primary_result = None
        if self.primary.status == ConnectionStatus.CONNECTED:
            create_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema})"
            primary_result = await self.primary.execute_query(create_query)
        
        # Create in fallback
        fallback_result = None
        if create_in_fallback and self.fallback.status == ConnectionStatus.CONNECTED:
            success = await self.fallback.create_table_from_schema(table_name, schema)
            fallback_result = QueryResult(success=success, source="SQLite")
        
        # Return the successful result or the primary result
        if primary_result and primary_result.success:
            return primary_result
        elif fallback_result and fallback_result.success:
            return fallback_result
        else:
            return QueryResult(
                success=False,
                error="Failed to create table in any database",
                source="None"
            )
    
    async def _periodic_health_check(self) -> None:
        """Perform periodic health check on connections"""
        current_time = time.time()
        
        if current_time - self._last_health_check < self._health_check_interval:
            return
        
        self._last_health_check = current_time
        
        # Check primary connection
        if self.primary.status != ConnectionStatus.CONNECTED:
            logger.info("Attempting to reconnect to primary database...")
            await self.primary.connect()
            
            if self.primary.status == ConnectionStatus.CONNECTED and not self.sync_manager.running:
                self.sync_manager.start_sync_worker(self)
        
        # Check fallback connection
        if self.fallback.status != ConnectionStatus.CONNECTED:
            logger.info("Attempting to reconnect to fallback database...")
            await self.fallback.connect()
    
    def _determine_operation_type(self, query: str) -> OperationType:
        """Determine operation type from query"""
        query_lower = query.strip().lower()
        
        if query_lower.startswith('select'):
            return OperationType.SELECT
        elif query_lower.startswith('insert'):
            return OperationType.INSERT
        elif query_lower.startswith('update'):
            return OperationType.UPDATE
        elif query_lower.startswith('delete'):
            return OperationType.DELETE
        elif query_lower.startswith('create table'):
            return OperationType.CREATE_TABLE
        elif query_lower.startswith('drop table'):
            return OperationType.DROP_TABLE
        else:
            return OperationType.TRANSACTION
    
    def _extract_table_name(self, query: str) -> str:
        """Extract table name from query"""
        try:
            query_lower = query.strip().lower()
            
            if 'from ' in query_lower:
                # SELECT query
                parts = query_lower.split('from ')[1].split()
                return parts[0] if parts else 'unknown'
            elif 'into ' in query_lower:
                # INSERT query
                parts = query_lower.split('into ')[1].split()
                return parts[0] if parts else 'unknown'
            elif 'update ' in query_lower:
                # UPDATE query
                parts = query_lower.split('update ')[1].split()
                return parts[0] if parts else 'unknown'
            elif 'table ' in query_lower:
                # CREATE/DROP TABLE query
                parts = query_lower.split('table ')[1].split()
                return parts[0] if parts else 'unknown'
            else:
                return 'unknown'
                
        except Exception:
            return 'unknown'
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive database status"""
        return {
            'primary': self.primary.health_check(),
            'fallback': self.fallback.health_check(),
            'sync_manager': self.sync_manager.get_queue_status(),
            'last_health_check': self._last_health_check
        }
    
    async def cleanup(self) -> None:
        """Clean up database connections and resources"""
        logger.info("Cleaning up database manager...")
        
        self.sync_manager.stop_sync_worker()
        
        await self.primary.disconnect()
        await self.fallback.disconnect()
        
        logger.info("Database manager cleanup completed")

# Example usage and testing
async def main():
    """Example usage of the database manager"""
    print("🗄️  Database Manager Test")
    
    # Configuration
    config = DatabaseConfig(
        host="localhost",
        port=5433,  # IZA OS PostgreSQL port
        database="iza_os",
        username="postgres",
        password=""
    )
    
    # Initialize database manager
    db_manager = DatabaseManager(config)
    
    # Initialize connections
    success = await db_manager.initialize()
    print(f"Database initialization: {'✓' if success else '✗'}")
    
    # Get status
    status = db_manager.get_status()
    print(f"Primary DB: {status['primary']['status']}")
    print(f"Fallback DB: {status['fallback']['status']}")
    print(f"Sync queue: {status['sync_manager']['queue_size']} operations")
    
    # Test table creation
    print("\n📋 Testing table creation...")
    schema = """
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        data JSONB,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    """
    
    result = await db_manager.create_table("test_table", schema)
    print(f"Table creation: {'✓' if result.success else '✗'} ({result.source})")
    
    # Test insert operation
    print("\n➕ Testing insert operation...")
    insert_query = """
        INSERT INTO test_table (name, data) VALUES (:name, :data)
    """
    insert_params = {
        'name': 'Test Record',
        'data': '{"test": true}'
    }
    
    result = await db_manager.execute_query(insert_query, insert_params)
    print(f"Insert operation: {'✓' if result.success else '✗'} ({result.source})")
    
    # Test select operation
    print("\n🔍 Testing select operation...")
    select_query = "SELECT * FROM test_table WHERE name = :name"
    select_params = {'name': 'Test Record'}
    
    result = await db_manager.execute_query(select_query, select_params)
    print(f"Select operation: {'✓' if result.success else '✗'} ({result.source})")
    
    if result.success and result.data:
        print(f"Records found: {len(result.data)}")
        for record in result.data:
            print(f"  - {record}")
    
    # Cleanup
    await db_manager.cleanup()
    print("\n✅ Test completed")

if __name__ == "__main__":
    asyncio.run(main())
