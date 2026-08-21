"""
Health Check for OpenLens

Provides health check endpoints and system monitoring.
"""

import os
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import socket
import psutil

from .logger import get_logger


class HealthCheck:
    """
    Performs health checks on system components.
    """
    
    def __init__(self):
        """Initialize health checker."""
        self.logger = get_logger('health')
        self.start_time = datetime.utcnow()
    
    def check_database(self, db_type: str = 'postgres') -> Dict[str, Any]:
        """
        Check database connectivity.
        
        Args:
            db_type: Database type ('postgres', 'neo4j', 'redis').
            
        Returns:
            Dictionary with health status.
        """
        try:
            if db_type == 'postgres':
                return self._check_postgres()
            elif db_type == 'neo4j':
                return self._check_neo4j()
            elif db_type == 'redis':
                return self._check_redis()
            else:
                return {
                    'status': 'error',
                    'message': f'Unsupported database type: {db_type}',
                }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
            }
    
    def _check_postgres(self) -> Dict[str, Any]:
        """Check PostgreSQL connectivity."""
        try:
            import psycopg2
            from psycopg2 import OperationalError
            
            conn = psycopg2.connect(
                dsn=os.getenv('POSTGRES_URL', 'postgresql://postgres:postgres@localhost:5432/openlens'),
                connect_timeout=5,
            )
            conn.close()
            
            return {
                'status': 'healthy',
                'database': 'postgres',
                'message': 'Connected successfully',
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'database': 'postgres',
                'message': str(e),
            }
    
    def _check_neo4j(self) -> Dict[str, Any]:
        """Check Neo4j connectivity."""
        try:
            from neo4j import GraphDatabase, BoltStatementResult
            
            uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
            username = os.getenv('NEO4J_USERNAME', 'neo4j')
            password = os.getenv('NEO4J_PASSWORD', 'password')
            
            driver = GraphDatabase.driver(uri, auth=(username, password))
            with driver.session() as session:
                result = session.run("RETURN 1")
                result.consume()
            driver.close()
            
            return {
                'status': 'healthy',
                'database': 'neo4j',
                'message': 'Connected successfully',
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'database': 'neo4j',
                'message': str(e),
            }
    
    def _check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity."""
        try:
            import redis
            
            r = redis.Redis.from_url(
                os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
                socket_timeout=5,
            )
            r.ping()
            
            return {
                'status': 'healthy',
                'database': 'redis',
                'message': 'Connected successfully',
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'database': 'redis',
                'message': str(e),
            }
    
    def check_system(self) -> Dict[str, Any]:
        """
        Check system health.
        
        Returns:
            Dictionary with system health status.
        """
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used
            memory_total = memory.total
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_used = disk.used
            disk_total = disk.total
            
            # Process info
            process = psutil.Process(os.getpid())
            process_cpu = process.cpu_percent()
            process_memory = process.memory_info().rss
            
            return {
                'status': 'healthy',
                'system': {
                    'hostname': socket.gethostname(),
                    'cpu': {
                        'percent': cpu_percent,
                        'count': cpu_count,
                    },
                    'memory': {
                        'percent': memory_percent,
                        'used': memory_used,
                        'total': memory_total,
                    },
                    'disk': {
                        'percent': disk_percent,
                        'used': disk_used,
                        'total': disk_total,
                    },
                    'process': {
                        'cpu_percent': process_cpu,
                        'memory_rss': process_memory,
                    },
                },
                'uptime': (datetime.utcnow() - self.start_time).total_seconds(),
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
            }
    
    def check_all(self) -> Dict[str, Any]:
        """
        Check all system components.
        
        Returns:
            Dictionary with health status of all components.
        """
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {
                'system': self.check_system(),
                'postgres': self.check_database('postgres'),
                'neo4j': self.check_database('neo4j'),
                'redis': self.check_database('redis'),
            },
        }


# Global health check instance
health_checker = HealthCheck()


def health_check() -> Dict[str, Any]:
    """
    Perform a comprehensive health check.
    
    Returns:
        Dictionary with health status.
    """
    return health_checker.check_all()


def check_database(db_type: str) -> Dict[str, Any]:
    """
    Check a specific database.
    
    Args:
        db_type: Database type ('postgres', 'neo4j', 'redis').
        
    Returns:
        Dictionary with database health status.
    """
    return health_checker.check_database(db_type)


def check_system() -> Dict[str, Any]:
    """
    Check system health.
    
    Returns:
        Dictionary with system health status.
    """
    return health_checker.check_system()
