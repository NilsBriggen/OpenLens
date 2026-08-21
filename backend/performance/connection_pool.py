"""
Connection Pool Module for OpenLens

Provides connection pooling for:
- Database connections (PostgreSQL)
- HTTP connections
- Redis connections
- Thread pool for async tasks
"""

import os
import time
import threading
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from queue import Queue
from functools import wraps

# Try to import database libraries
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("SQLAlchemy not available. Install with: pip install sqlalchemy")

try:
    import psycopg2
    from psycopg2 import pool
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("Psycopg2 not available. Install with: pip install psycopg2-binary")

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from concurrent.futures import ThreadPoolExecutor
    CONURRENT_FUTURES_AVAILABLE = True
except ImportError:
    CONURRENT_FUTURES_AVAILABLE = False


@dataclass
class ConnectionConfig:
    """Configuration for a connection pool."""
    name: str
    connection_string: str
    min_connections: int = 1
    max_connections: int = 10
    connection_timeout: int = 30
    max_lifetime: int = 3600  # seconds
    idle_timeout: int = 600  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'min_connections': self.min_connections,
            'max_connections': self.max_connections,
            'connection_timeout': self.connection_timeout,
            'max_lifetime': self.max_lifetime,
            'idle_timeout': self.idle_timeout,
        }


class DatabaseConnectionPool:
    """
    Connection pool for database connections.
    """
    
    def __init__(self, config: ConnectionConfig = None):
        """
        Initialize the database connection pool.
        
        Args:
            config: Connection configuration.
        """
        self.config = config or ConnectionConfig(
            name='default',
            connection_string=os.getenv('POSTGRES_URL', 'postgresql://localhost/openlens'),
        )
        
        self.engine = None
        self.Session = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the connection pool."""
        if not SQLALCHEMY_AVAILABLE:
            return
        
        try:
            self.engine = create_engine(
                self.config.connection_string,
                pool_size=self.config.min_connections,
                max_overflow=self.config.max_connections - self.config.min_connections,
                pool_pre_ping=True,
                pool_recycle=self.config.max_lifetime,
                pool_timeout=self.config.connection_timeout,
                echo=False,
            )
            
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            
            print(f"Initialized database connection pool: {self.config.name}")
        except Exception as e:
            print(f"Failed to initialize database connection pool: {e}")
            self.engine = None
            self.Session = None
    
    def get_connection(self):
        """
        Get a database connection.
        
        Returns:
            Database connection or None if failed.
        """
        if not self.Session:
            return None
        
        return self.Session()
    
    def get_session(self):
        """
        Get a SQLAlchemy session.
        
        Returns:
            SQLAlchemy session or None if failed.
        """
        if not self.Session:
            return None
        
        return self.Session()
    
    def close(self):
        """Close the connection pool."""
        if self.engine:
            self.engine.dispose()
        if self.Session:
            self.Session.remove()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get connection pool statistics.
        
        Returns:
            Dictionary with pool statistics.
        """
        if not self.engine:
            return {'error': 'Pool not initialized'}
        
        try:
            pool = self.engine.pool
            return {
                'name': self.config.name,
                'size': pool.size(),
                'checkedin': pool.checkedin(),
                'checkedout': pool.checkedout(),
                'overflow': pool.overflow(),
                'timeout': self.config.connection_timeout,
            }
        except Exception as e:
            return {'error': str(e)}


class Psycopg2ConnectionPool:
    """
    Connection pool for psycopg2 connections.
    """
    
    def __init__(self, config: ConnectionConfig = None):
        """
        Initialize the psycopg2 connection pool.
        
        Args:
            config: Connection configuration.
        """
        if not PSYCOPG2_AVAILABLE:
            raise RuntimeError("Psycopg2 is not available")
        
        self.config = config or ConnectionConfig(
            name='psycopg2_default',
            connection_string=os.getenv('POSTGRES_URL', 'postgresql://localhost/openlens'),
        )
        
        self.pool = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the connection pool."""
        try:
            # Parse connection string
            import urllib.parse
            url = urllib.parse.urlparse(self.config.connection_string)
            
            self.pool = pool.SimpleConnectionPool(
                minconn=self.config.min_connections,
                maxconn=self.config.max_connections,
                host=url.hostname,
                port=url.port or 5432,
                dbname=url.path[1:] if url.path else 'postgres',
                user=url.username or 'postgres',
                password=url.password or '',
            )
            
            print(f"Initialized psycopg2 connection pool: {self.config.name}")
        except Exception as e:
            print(f"Failed to initialize psycopg2 connection pool: {e}")
            self.pool = None
    
    def get_connection(self):
        """
        Get a psycopg2 connection.
        
        Returns:
            Psycopg2 connection or None if failed.
        """
        if not self.pool:
            return None
        
        try:
            return self.pool.getconn()
        except Exception as e:
            print(f"Failed to get connection: {e}")
            return None
    
    def return_connection(self, connection):
        """
        Return a connection to the pool.
        
        Args:
            connection: Connection to return.
        """
        if self.pool and connection:
            try:
                self.pool.putconn(connection)
            except Exception as e:
                print(f"Failed to return connection: {e}")
    
    def close(self):
        """Close the connection pool."""
        if self.pool:
            self.pool.closeall()


class RedisConnectionPool:
    """
    Connection pool for Redis connections.
    """
    
    def __init__(self, config: ConnectionConfig = None):
        """
        Initialize the Redis connection pool.
        
        Args:
            config: Connection configuration.
        """
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis is not available")
        
        self.config = config or ConnectionConfig(
            name='redis_default',
            connection_string=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        )
        
        self.pool = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the connection pool."""
        try:
            # Parse connection string
            import urllib.parse
            url = urllib.parse.urlparse(self.config.connection_string)
            
            self.pool = redis.ConnectionPool(
                host=url.hostname or 'localhost',
                port=url.port or 6379,
                db=int(url.path[1:]) if url.path else 0,
                password=url.password or None,
                max_connections=self.config.max_connections,
            )
            
            print(f"Initialized Redis connection pool: {self.config.name}")
        except Exception as e:
            print(f"Failed to initialize Redis connection pool: {e}")
            self.pool = None
    
    def get_connection(self):
        """
        Get a Redis connection.
        
        Returns:
            Redis connection or None if failed.
        """
        if not self.pool:
            return None
        
        try:
            return redis.Redis(connection_pool=self.pool)
        except Exception as e:
            print(f"Failed to get Redis connection: {e}")
            return None
    
    def close(self):
        """Close the connection pool."""
        if self.pool:
            self.pool.close()


class ThreadPool:
    """
    Thread pool for async task processing.
    """
    
    def __init__(self, max_workers: int = 10, thread_name_prefix: str = 'openlens'):
        """
        Initialize the thread pool.
        
        Args:
            max_workers: Maximum number of worker threads.
            thread_name_prefix: Prefix for thread names.
        """
        if not CONURRENT_FUTURES_AVAILABLE:
            raise RuntimeError("Concurrent futures is not available")
        
        self.max_workers = max_workers
        self.thread_name_prefix = thread_name_prefix
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix=thread_name_prefix,
        )
        self._task_count = 0
        self._lock = threading.Lock()
    
    def submit(self, func: Callable, *args, **kwargs):
        """
        Submit a task to the thread pool.
        
        Args:
            func: Function to execute.
            *args: Function arguments.
            **kwargs: Function keyword arguments.
            
        Returns:
            Future object.
        """
        with self._lock:
            self._task_count += 1
        
        return self.executor.submit(func, *args, **kwargs)
    
    def map(self, func: Callable, *iterables, **kwargs):
        """
        Map a function over iterables.
        
        Args:
            func: Function to execute.
            *iterables: Iterables to map over.
            **kwargs: Additional keyword arguments.
            
        Returns:
            List of results.
        """
        return list(self.executor.map(func, *iterables, **kwargs))
    
    def shutdown(self, wait: bool = True):
        """
        Shutdown the thread pool.
        
        Args:
            wait: Whether to wait for pending tasks.
        """
        self.executor.shutdown(wait=wait)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get thread pool statistics.
        
        Returns:
            Dictionary with pool statistics.
        """
        with self._lock:
            task_count = self._task_count
        
        return {
            'max_workers': self.max_workers,
            'task_count': task_count,
            'thread_name_prefix': self.thread_name_prefix,
        }


class ConnectionPool:
    """
    Manages multiple connection pools.
    """
    
    def __init__(self):
        """Initialize the connection pool manager."""
        self.pools: Dict[str, Any] = {}
        self._initialize_default_pools()
    
    def _initialize_default_pools(self):
        """Initialize default connection pools."""
        # Database pool
        db_config = ConnectionConfig(
            name='database',
            connection_string=os.getenv('POSTGRES_URL', 'postgresql://localhost/openlens'),
            min_connections=1,
            max_connections=10,
        )
        
        if SQLALCHEMY_AVAILABLE:
            self.pools['database'] = DatabaseConnectionPool(db_config)
        
        # Psycopg2 pool
        if PSYCOPG2_AVAILABLE:
            self.pools['psycopg2'] = Psycopg2ConnectionPool(db_config)
        
        # Redis pool
        if REDIS_AVAILABLE and os.getenv('REDIS_URL'):
            redis_config = ConnectionConfig(
                name='redis',
                connection_string=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
                min_connections=1,
                max_connections=20,
            )
            self.pools['redis'] = RedisConnectionPool(redis_config)
        
        # Thread pool
        if CONURRENT_FUTURES_AVAILABLE:
            self.pools['thread'] = ThreadPool(
                max_workers=int(os.getenv('THREAD_POOL_SIZE', 10)),
            )
    
    def get_pool(self, name: str):
        """
        Get a connection pool by name.
        
        Args:
            name: Pool name.
            
        Returns:
            Connection pool or None if not found.
        """
        return self.pools.get(name)
    
    def get_database_session(self):
        """
        Get a database session.
        
        Returns:
            Database session or None if failed.
        """
        db_pool = self.get_pool('database')
        if db_pool:
            return db_pool.get_session()
        return None
    
    def get_redis_connection(self):
        """
        Get a Redis connection.
        
        Returns:
            Redis connection or None if failed.
        """
        redis_pool = self.get_pool('redis')
        if redis_pool:
            return redis_pool.get_connection()
        return None
    
    def submit_task(self, func: Callable, *args, **kwargs):
        """
        Submit a task to the thread pool.
        
        Args:
            func: Function to execute.
            *args: Function arguments.
            **kwargs: Function keyword arguments.
            
        Returns:
            Future object or None if thread pool not available.
        """
        thread_pool = self.get_pool('thread')
        if thread_pool:
            return thread_pool.submit(func, *args, **kwargs)
        return None
    
    def close_all(self):
        """Close all connection pools."""
        for name, pool in self.pools.items():
            try:
                if hasattr(pool, 'close'):
                    pool.close()
                elif hasattr(pool, 'shutdown'):
                    pool.shutdown()
            except Exception as e:
                print(f"Error closing pool {name}: {e}")
        
        self.pools.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all pools.
        
        Returns:
            Dictionary with pool statistics.
        """
        stats = {}
        
        for name, pool in self.pools.items():
            if hasattr(pool, 'get_stats'):
                stats[name] = pool.get_stats()
            else:
                stats[name] = {'type': type(pool).__name__}
        
        return stats


# Global connection pool instance
db_connection_pool = ConnectionPool()
