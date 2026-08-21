"""
Performance Module for OpenLens

Provides performance optimization features:
- Caching (Redis, in-memory)
- Query optimization
- Database connection pooling
- Async task processing
"""

from .cache import CacheManager, cache_manager, redis_cache
from .query_optimizer import QueryOptimizer, query_optimizer
from .connection_pool import ConnectionPool, db_connection_pool

__all__ = [
    'CacheManager',
    'cache_manager',
    'redis_cache',
    'QueryOptimizer',
    'query_optimizer',
    'ConnectionPool',
    'db_connection_pool',
]
