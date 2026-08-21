"""
Result Cache for OpenLens Distributed Scraping

Provides caching capabilities for scraping results:
- In-memory caching
- Disk-based caching
- Redis caching
- TTL-based expiration
- Cache invalidation
- Statistics and monitoring
"""

import os
import time
import json
import hashlib
import pickle
import threading
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, OrderedDict
from pathlib import Path


@dataclass
class CacheEntry:
    """Represents a cache entry."""
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    accessed_at: datetime
    size: int = 0  # Size in bytes
    
    def __post_init__(self):
        """Initialize cache entry."""
        if isinstance(self.value, (dict, list)):
            self.size = len(json.dumps(self.value))
        elif isinstance(self.value, str):
            self.size = len(self.value.encode('utf-8'))
        else:
            self.size = 0
    
    def is_expired(self) -> bool:
        """Check if the entry has expired."""
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'accessed_at': self.accessed_at.isoformat(),
            'size': self.size,
        }


@dataclass
class CacheConfig:
    """Configuration for result cache."""
    cache_type: str = 'memory'  # memory, disk, redis
    max_size: int = 1000  # Maximum number of entries
    max_memory: int = 100 * 1024 * 1024  # 100MB
    default_ttl: int = 3600  # Default TTL in seconds (1 hour)
    cleanup_interval: int = 300  # Cleanup interval in seconds
    cache_dir: str = '/tmp/openlens_cache'  # Cache directory for disk cache
    redis_url: str = 'redis://localhost:6379/2'  # Redis URL for Redis cache
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'cache_type': self.cache_type,
            'max_size': self.max_size,
            'max_memory': self.max_memory,
            'default_ttl': self.default_ttl,
            'cleanup_interval': self.cleanup_interval,
            'cache_dir': self.cache_dir,
            'redis_url': self.redis_url,
        }


@dataclass
class CacheStats:
    """Statistics for the cache."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    size: int = 0
    memory_usage: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': self.hits / (self.hits + self.misses) if (self.hits + self.misses) > 0 else 0,
            'evictions': self.evictions,
            'expirations': self.expirations,
            'size': self.size,
            'memory_usage': self.memory_usage,
        }


class MemoryCache:
    """
    In-memory cache implementation.
    
    Uses LRU (Least Recently Used) eviction policy.
    """
    
    def __init__(self, config: CacheConfig):
        """
        Initialize the memory cache.
        
        Args:
            config: CacheConfig instance.
        """
        self.config = config
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._stats = CacheStats()
        self._lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key.
            
        Returns:
            Cached value or None.
        """
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                
                if entry.is_expired():
                    # Remove expired entry
                    del self._cache[key]
                    self._stats.expirations += 1
                    self._stats.misses += 1
                    return None
                
                # Move to end (most recently used)
                self._cache.move_to_end(key)
                
                # Update access time
                entry.accessed_at = datetime.utcnow()
                
                self._stats.hits += 1
                return entry.value
            
            self._stats.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time to live in seconds (None for default).
            
        Returns:
            True if set.
        """
        with self._lock:
            ttl = ttl or self.config.default_ttl
            
            # Check if key exists
            if key in self._cache:
                # Remove old entry
                old_entry = self._cache[key]
                self._stats.memory_usage -= old_entry.size
            
            # Create new entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(seconds=ttl),
                accessed_at=datetime.utcnow(),
            )
            
            # Check size limits
            while (len(self._cache) >= self.config.max_size or 
                   self._stats.memory_usage + entry.size >= self.config.max_memory) and self._cache:
                # Remove least recently used
                oldest_key, oldest_entry = self._cache.popitem(last=False)
                self._stats.memory_usage -= oldest_entry.size
                self._stats.evictions += 1
            
            # Add new entry
            self._cache[key] = entry
            self._stats.memory_usage += entry.size
            self._stats.size = len(self._cache)
            
            return True
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key.
            
        Returns:
            True if deleted.
        """
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                self._stats.memory_usage -= entry.size
                del self._cache[key]
                self._stats.size = len(self._cache)
                return True
            return False
    
    def clear(self):
        """Clear the cache."""
        with self._lock:
            self._cache.clear()
            self._stats = CacheStats()
    
    def cleanup(self):
        """Clean up expired entries."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                entry = self._cache[key]
                self._stats.memory_usage -= entry.size
                del self._cache[key]
                self._stats.expirations += 1
            
            self._stats.size = len(self._cache)
    
    def get_stats(self) -> CacheStats:
        """
        Get cache statistics.
        
        Returns:
            CacheStats object.
        """
        with self._lock:
            return self._stats


class DiskCache:
    """
    Disk-based cache implementation.
    
    Stores cache entries as files on disk.
    """
    
    def __init__(self, config: CacheConfig):
        """
        Initialize the disk cache.
        
        Args:
            config: CacheConfig instance.
        """
        self.config = config
        self._cache_dir = Path(config.cache_dir)
        self._stats = CacheStats()
        self._lock = threading.Lock()
        
        # Create cache directory if it doesn't exist
        self._cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> Path:
        """Get the cache file path for a key."""
        # Hash the key to create a safe filename
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self._cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key.
            
        Returns:
            Cached value or None.
        """
        with self._lock:
            cache_path = self._get_cache_path(key)
            
            if not cache_path.exists():
                self._stats.misses += 1
                return None
            
            try:
                with open(cache_path, 'rb') as f:
                    entry = pickle.load(f)
                
                if entry.is_expired():
                    # Remove expired entry
                    cache_path.unlink()
                    self._stats.expirations += 1
                    self._stats.misses += 1
                    return None
                
                # Update access time
                entry.accessed_at = datetime.utcnow()
                
                # Save updated entry
                with open(cache_path, 'wb') as f:
                    pickle.dump(entry, f)
                
                self._stats.hits += 1
                return entry.value
            
            except Exception as e:
                print(f"Error reading cache file: {e}")
                self._stats.misses += 1
                return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time to live in seconds (None for default).
            
        Returns:
            True if set.
        """
        with self._lock:
            ttl = ttl or self.config.default_ttl
            
            # Create entry
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(seconds=ttl),
                accessed_at=datetime.utcnow(),
            )
            
            # Check size limits
            self._cleanup_if_needed()
            
            # Save to disk
            cache_path = self._get_cache_path(key)
            try:
                with open(cache_path, 'wb') as f:
                    pickle.dump(entry, f)
                
                self._stats.size = len(list(self._cache_dir.glob('*.cache')))
                self._stats.memory_usage += entry.size
                return True
            
            except Exception as e:
                print(f"Error writing cache file: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key.
            
        Returns:
            True if deleted.
        """
        with self._lock:
            cache_path = self._get_cache_path(key)
            
            if cache_path.exists():
                try:
                    # Get size before deleting
                    with open(cache_path, 'rb') as f:
                        entry = pickle.load(f)
                    self._stats.memory_usage -= entry.size
                    
                    cache_path.unlink()
                    self._stats.size = len(list(self._cache_dir.glob('*.cache')))
                    return True
                except Exception as e:
                    print(f"Error deleting cache file: {e}")
                    return False
            
            return False
    
    def clear(self):
        """Clear the cache."""
        with self._lock:
            for cache_file in self._cache_dir.glob('*.cache'):
                try:
                    cache_file.unlink()
                except Exception as e:
                    print(f"Error deleting cache file: {e}")
            
            self._stats = CacheStats()
    
    def cleanup(self):
        """Clean up expired entries."""
        with self._lock:
            for cache_file in self._cache_dir.glob('*.cache'):
                try:
                    with open(cache_file, 'rb') as f:
                        entry = pickle.load(f)
                    
                    if entry.is_expired():
                        cache_file.unlink()
                        self._stats.expirations += 1
                        self._stats.memory_usage -= entry.size
                except Exception as e:
                    print(f"Error checking cache file: {e}")
            
            self._stats.size = len(list(self._cache_dir.glob('*.cache')))
    
    def _cleanup_if_needed(self):
        """Clean up if cache is full."""
        # Count files
        file_count = len(list(self._cache_dir.glob('*.cache')))
        
        if file_count >= self.config.max_size:
            # Delete oldest files
            files_with_time = []
            for cache_file in self._cache_dir.glob('*.cache'):
                try:
                    with open(cache_file, 'rb') as f:
                        entry = pickle.load(f)
                    files_with_time.append((cache_file, entry.created_at))
                except:
                    continue
            
            # Sort by creation time
            files_with_time.sort(key=lambda x: x[1])
            
            # Delete oldest files
            for cache_file, _ in files_with_time[:file_count - self.config.max_size + 1]:
                try:
                    with open(cache_file, 'rb') as f:
                        entry = pickle.load(f)
                    self._stats.memory_usage -= entry.size
                    cache_file.unlink()
                    self._stats.evictions += 1
                except Exception as e:
                    print(f"Error deleting old cache file: {e}")
    
    def get_stats(self) -> CacheStats:
        """
        Get cache statistics.
        
        Returns:
            CacheStats object.
        """
        with self._lock:
            # Update size
            self._stats.size = len(list(self._cache_dir.glob('*.cache')))
            return self._stats


class RedisCache:
    """
    Redis-based cache implementation.
    
    Uses Redis for distributed caching.
    """
    
    def __init__(self, config: CacheConfig):
        """
        Initialize the Redis cache.
        
        Args:
            config: CacheConfig instance.
        """
        self.config = config
        self._stats = CacheStats()
        self._lock = threading.Lock()
        
        # Try to import redis
        try:
            import redis
            self._redis = redis.Redis.from_url(config.redis_url, decode_responses=True)
            self._available = True
        except Exception as e:
            print(f"Redis not available: {e}")
            self._available = False
            self._redis = None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key.
            
        Returns:
            Cached value or None.
        """
        if not self._available:
            return None
        
        with self._lock:
            try:
                # Get the value
                value = self._redis.get(key)
                
                if value is None:
                    self._stats.misses += 1
                    return None
                
                # Parse the cached entry
                try:
                    entry_data = json.loads(value)
                    entry = CacheEntry(
                        key=entry_data['key'],
                        value=entry_data['value'],
                        created_at=datetime.fromisoformat(entry_data['created_at']),
                        expires_at=datetime.fromisoformat(entry_data['expires_at']),
                        accessed_at=datetime.fromisoformat(entry_data['accessed_at']),
                        size=entry_data.get('size', 0),
                    )
                    
                    if entry.is_expired():
                        # Remove expired entry
                        self._redis.delete(key)
                        self._stats.expirations += 1
                        self._stats.misses += 1
                        return None
                    
                    # Update access time
                    entry.accessed_at = datetime.utcnow()
                    
                    # Save updated entry
                    self._redis.setex(
                        key,
                        int((entry.expires_at - datetime.utcnow()).total_seconds()),
                        json.dumps(entry.to_dict())
                    )
                    
                    self._stats.hits += 1
                    return entry.value
                
                except Exception as e:
                    print(f"Error parsing cached entry: {e}")
                    self._stats.misses += 1
                    return None
            
            except Exception as e:
                print(f"Redis error: {e}")
                self._stats.misses += 1
                return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time to live in seconds (None for default).
            
        Returns:
            True if set.
        """
        if not self._available:
            return False
        
        with self._lock:
            ttl = ttl or self.config.default_ttl
            
            try:
                # Create entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    created_at=datetime.utcnow(),
                    expires_at=datetime.utcnow() + timedelta(seconds=ttl),
                    accessed_at=datetime.utcnow(),
                )
                
                # Save to Redis
                self._redis.setex(
                    key,
                    ttl,
                    json.dumps(entry.to_dict())
                )
                
                self._stats.size = self._redis.dbsize()
                self._stats.memory_usage += entry.size
                return True
            
            except Exception as e:
                print(f"Redis error: {e}")
                return False
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key.
            
        Returns:
            True if deleted.
        """
        if not self._available:
            return False
        
        with self._lock:
            try:
                result = self._redis.delete(key)
                if result > 0:
                    self._stats.size = self._redis.dbsize()
                    return True
                return False
            
            except Exception as e:
                print(f"Redis error: {e}")
                return False
    
    def clear(self):
        """Clear the cache."""
        if not self._available:
            return
        
        with self._lock:
            try:
                self._redis.flushdb()
                self._stats = CacheStats()
            
            except Exception as e:
                print(f"Redis error: {e}")
    
    def cleanup(self):
        """Clean up expired entries."""
        # Redis automatically expires keys, so we don't need to do anything
        pass
    
    def get_stats(self) -> CacheStats:
        """
        Get cache statistics.
        
        Returns:
            CacheStats object.
        """
        if not self._available:
            return self._stats
        
        with self._lock:
            try:
                self._stats.size = self._redis.dbsize()
                return self._stats
            
            except Exception as e:
                print(f"Redis error: {e}")
                return self._stats


class ResultCache:
    """
    Result cache for distributed scraping.
    
    Provides:
    - Multiple cache backends (memory, disk, Redis)
    - TTL-based expiration
    - Cache invalidation
    - Statistics and monitoring
    """
    
    def __init__(self, config: CacheConfig = None):
        """
        Initialize the result cache.
        
        Args:
            config: CacheConfig instance.
        """
        self.config = config or CacheConfig()
        
        # Initialize the appropriate cache backend
        if self.config.cache_type == 'redis':
            self._cache = RedisCache(self.config)
        elif self.config.cache_type == 'disk':
            self._cache = DiskCache(self.config)
        else:
            self._cache = MemoryCache(self.config)
        
        self._cleanup_thread = None
        self._running = False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key.
            
        Returns:
            Cached value or None.
        """
        return self._cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """
        Set a value in the cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time to live in seconds (None for default).
            
        Returns:
            True if set.
        """
        return self._cache.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """
        Delete a value from the cache.
        
        Args:
            key: Cache key.
            
        Returns:
            True if deleted.
        """
        return self._cache.delete(key)
    
    def clear(self):
        """Clear the cache."""
        self._cache.clear()
    
    def cleanup(self):
        """Clean up expired entries."""
        self._cache.cleanup()
    
    def get_stats(self) -> CacheStats:
        """
        Get cache statistics.
        
        Returns:
            CacheStats object.
        """
        return self._cache.get_stats()
    
    def start_cleanup_thread(self, interval: int = None):
        """
        Start a background thread for cleanup.
        
        Args:
            interval: Cleanup interval in seconds (None for config default).
        """
        if self._running:
            return
        
        interval = interval or self.config.cleanup_interval
        
        def cleanup_loop():
            while self._running:
                self.cleanup()
                time.sleep(interval)
        
        self._cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self._running = True
        self._cleanup_thread.start()
    
    def stop_cleanup_thread(self):
        """Stop the cleanup thread."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
            self._cleanup_thread = None
    
    def generate_key(self, url: str, params: Dict = None, method: str = 'GET') -> str:
        """
        Generate a cache key.
        
        Args:
            url: URL to cache.
            params: Request parameters.
            method: HTTP method.
            
        Returns:
            Cache key.
        """
        key_data = {
            'url': url,
            'params': params or {},
            'method': method,
        }
        
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def get_cached_response(self, url: str, params: Dict = None, method: str = 'GET') -> Optional[Dict]:
        """
        Get a cached HTTP response.
        
        Args:
            url: URL to get.
            params: Request parameters.
            method: HTTP method.
            
        Returns:
            Cached response or None.
        """
        key = self.generate_key(url, params, method)
        return self.get(key)
    
    def cache_response(self, url: str, response: Dict, params: Dict = None, method: str = 'GET', ttl: int = None):
        """
        Cache an HTTP response.
        
        Args:
            url: URL to cache.
            response: Response to cache.
            params: Request parameters.
            method: HTTP method.
            ttl: Time to live in seconds.
        """
        key = self.generate_key(url, params, method)
        self.set(key, response, ttl)


# Global result cache instance
result_cache = ResultCache()
