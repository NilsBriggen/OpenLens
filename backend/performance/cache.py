"""
Cache Module for OpenLens

Provides caching functionality using:
- Redis (for distributed caching)
- In-memory cache (for single-instance deployments)
- LRU cache for function results

Dependencies:
- redis: For Redis caching
- functools: For LRU cache
"""

import os
import json
import time
import hashlib
import pickle
from typing import Dict, Any, Optional, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from functools import wraps
from collections import OrderedDict

# Try to import Redis
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Redis not available. Install with: pip install redis")


@dataclass
class CacheEntry:
    """Represents a cache entry."""
    key: str
    value: Any
    expires_at: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    
    def is_expired(self) -> bool:
        """Check if the cache entry is expired."""
        return datetime.utcnow() > self.expires_at
    
    def touch(self):
        """Update the access count."""
        self.access_count += 1


class InMemoryCache:
    """
    Simple in-memory cache with TTL support.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Initialize the in-memory cache.
        
        Args:
            max_size: Maximum number of entries.
            default_ttl: Default time-to-live in seconds.
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = {}
        self._access_order = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key.
            
        Returns:
            Cached value or None if not found or expired.
        """
        entry = self.cache.get(key)
        
        if not entry:
            return None
        
        if entry.is_expired():
            del self.cache[key]
            if key in self._access_order:
                del self._access_order[key]
            return None
        
        entry.touch()
        
        # Move to end (most recently used)
        if key in self._access_order:
            del self._access_order[key]
        self._access_order[key] = None
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl: int = None):
        """
        Set a value in the cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time-to-live in seconds (defaults to default_ttl).
        """
        ttl = ttl or self.default_ttl
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        entry = CacheEntry(
            key=key,
            value=value,
            expires_at=expires_at,
        )
        
        self.cache[key] = entry
        
        # Update access order
        if key in self._access_order:
            del self._access_order[key]
        self._access_order[key] = None
        
        # Evict if over max size
        while len(self.cache) > self.max_size:
            # Remove least recently used
            oldest_key = next(iter(self._access_order))
            del self.cache[oldest_key]
            del self._access_order[oldest_key]
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key.
            
        Returns:
            True if deleted, False if not found.
        """
        if key in self.cache:
            del self.cache[key]
        if key in self._access_order:
            del self._access_order[key]
        return key in self.cache
    
    def clear(self):
        """Clear all cache entries."""
        self.cache.clear()
        self._access_order.clear()
    
    def cleanup_expired(self):
        """Remove all expired entries."""
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]
        for key in expired_keys:
            del self.cache[key]
            if key in self._access_order:
                del self._access_order[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics.
        """
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'default_ttl': self.default_ttl,
        }


class RedisCache:
    """
    Redis-based cache.
    """
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 db: int = 0, password: str = None, default_ttl: int = 3600):
        """
        Initialize the Redis cache.
        
        Args:
            host: Redis host.
            port: Redis port.
            db: Redis database number.
            password: Redis password.
            default_ttl: Default time-to-live in seconds.
        """
        if not REDIS_AVAILABLE:
            raise RuntimeError("Redis is not available. Install with: pip install redis")
        
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.default_ttl = default_ttl
        self.client = None
        
        self._connect()
    
    def _connect(self):
        """Connect to Redis."""
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
            )
            
            # Test connection
            self.client.ping()
            print(f"Connected to Redis at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key.
            
        Returns:
            Cached value or None if not found or expired.
        """
        if not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value is None:
                return None
            
            # Try to deserialize
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        except Exception as e:
            print(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """
        Set a value in the cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time-to-live in seconds (defaults to default_ttl).
        """
        if not self.client:
            return
        
        ttl = ttl or self.default_ttl
        
        try:
            # Serialize value
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            self.client.setex(key, ttl, value)
        except Exception as e:
            print(f"Redis set error: {e}")
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key.
            
        Returns:
            True if deleted, False if not found.
        """
        if not self.client:
            return False
        
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False
    
    def clear(self):
        """Clear all cache entries."""
        if not self.client:
            return
        
        try:
            self.client.flushdb()
        except Exception as e:
            print(f"Redis clear error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics.
        """
        if not self.client:
            return {'error': 'Not connected to Redis'}
        
        try:
            info = self.client.info()
            return {
                'host': self.host,
                'port': self.port,
                'db': self.db,
                'default_ttl': self.default_ttl,
                'keys': info.get('db0', {}).get('keys', 0),
                'memory_used': info.get('used_memory', 0),
            }
        except Exception as e:
            return {'error': str(e)}


class CacheManager:
    """
    Manages caching with fallback from Redis to in-memory.
    """
    
    def __init__(self, use_redis: bool = True, redis_config: Dict = None,
                 in_memory_config: Dict = None):
        """
        Initialize the cache manager.
        
        Args:
            use_redis: Whether to use Redis.
            redis_config: Redis configuration.
            in_memory_config: In-memory cache configuration.
        """
        self.use_redis = use_redis and REDIS_AVAILABLE
        self.redis_cache = None
        self.in_memory_cache = None
        
        if self.use_redis:
            redis_config = redis_config or {}
            self.redis_cache = RedisCache(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                password=redis_config.get('password'),
                default_ttl=redis_config.get('default_ttl', 3600),
            )
        
        in_memory_config = in_memory_config or {}
        self.in_memory_cache = InMemoryCache(
            max_size=in_memory_config.get('max_size', 1000),
            default_ttl=in_memory_config.get('default_ttl', 3600),
        )
    
    def get(self, key: str, use_redis_first: bool = True) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key.
            use_redis_first: Whether to try Redis first.
            
        Returns:
            Cached value or None if not found.
        """
        if self.use_redis and use_redis_first:
            value = self.redis_cache.get(key)
            if value is not None:
                return value
        
        return self.in_memory_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = None, use_redis: bool = True):
        """
        Set a value in the cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time-to-live in seconds.
            use_redis: Whether to use Redis.
        """
        if self.use_redis and use_redis:
            self.redis_cache.set(key, value, ttl)
        
        self.in_memory_cache.set(key, value, ttl)
    
    def delete(self, key: str, use_redis: bool = True) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key.
            use_redis: Whether to use Redis.
            
        Returns:
            True if deleted from any cache.
        """
        deleted = False
        
        if self.use_redis and use_redis:
            deleted = self.redis_cache.delete(key) or deleted
        
        deleted = self.in_memory_cache.delete(key) or deleted
        
        return deleted
    
    def clear(self, use_redis: bool = True):
        """
        Clear all cache entries.
        
        Args:
            use_redis: Whether to clear Redis.
        """
        if self.use_redis and use_redis:
            self.redis_cache.clear()
        
        self.in_memory_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics.
        """
        stats = {
            'in_memory': self.in_memory_cache.get_stats(),
        }
        
        if self.use_redis:
            stats['redis'] = self.redis_cache.get_stats()
        
        return stats
    
    def cached(self, key_prefix: str = "", ttl: int = None, use_redis: bool = True):
        """
        Decorator to cache function results.
        
        Args:
            key_prefix: Prefix for cache keys.
            ttl: Time-to-live in seconds.
            use_redis: Whether to use Redis.
            
        Returns:
            Decorator function.
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                key = self._generate_cache_key(key_prefix, func, args, kwargs)
                
                # Try to get from cache
                cached_value = self.get(key, use_redis_first=use_redis)
                if cached_value is not None:
                    return cached_value
                
                # Call function and cache result
                result = func(*args, **kwargs)
                self.set(key, result, ttl, use_redis)
                
                return result
            
            return wrapper
        return decorator
    
    def _generate_cache_key(self, prefix: str, func: Callable, args: tuple, kwargs: Dict) -> str:
        """
        Generate a cache key for a function call.
        
        Args:
            prefix: Key prefix.
            func: Function being cached.
            args: Function arguments.
            kwargs: Function keyword arguments.
            
        Returns:
            Cache key string.
        """
        # Create a hashable representation of the arguments
        key_parts = [
            prefix,
            func.__module__,
            func.__name__,
            str(args),
            str(sorted(kwargs.items())),
        ]
        
        key = '|'.join(key_parts)
        return hashlib.sha256(key.encode()).hexdigest()
    
    def cache_with_key(self, key_func: Callable, ttl: int = None, use_redis: bool = True):
        """
        Decorator to cache function results with a custom key function.
        
        Args:
            key_func: Function to generate cache key from arguments.
            ttl: Time-to-live in seconds.
            use_redis: Whether to use Redis.
            
        Returns:
            Decorator function.
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key using custom function
                key = key_func(*args, **kwargs)
                
                # Try to get from cache
                cached_value = self.get(key, use_redis_first=use_redis)
                if cached_value is not None:
                    return cached_value
                
                # Call function and cache result
                result = func(*args, **kwargs)
                self.set(key, result, ttl, use_redis)
                
                return result
            
            return wrapper
        return decorator
    
    def invalidate(self, key: str, use_redis: bool = True):
        """
        Invalidate a cache entry.
        
        Args:
            key: Cache key to invalidate.
            use_redis: Whether to invalidate in Redis.
        """
        self.delete(key, use_redis)
    
    def invalidate_pattern(self, pattern: str):
        """
        Invalidate all cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match (only works with Redis).
        """
        if self.use_redis:
            try:
                keys = self.redis_cache.client.keys(pattern)
                for key in keys:
                    self.redis_cache.delete(key.decode())
            except Exception as e:
                print(f"Error invalidating pattern: {e}")


# Global cache manager instance
cache_manager = CacheManager(
    use_redis=REDIS_AVAILABLE and os.getenv('REDIS_URL'),
    redis_config={
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'db': int(os.getenv('REDIS_DB', 0)),
        'password': os.getenv('REDIS_PASSWORD'),
        'default_ttl': int(os.getenv('REDIS_DEFAULT_TTL', 3600)),
    },
    in_memory_config={
        'max_size': int(os.getenv('CACHE_MAX_SIZE', 1000)),
        'default_ttl': int(os.getenv('CACHE_DEFAULT_TTL', 3600)),
    },
)

# Global Redis cache instance (if available)
redis_cache = None
if REDIS_AVAILABLE and os.getenv('REDIS_URL'):
    redis_cache = RedisCache(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 0)),
        password=os.getenv('REDIS_PASSWORD'),
        default_ttl=int(os.getenv('REDIS_DEFAULT_TTL', 3600)),
    )
