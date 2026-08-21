"""
Rate Limiter for OpenLens Distributed Scraping

Provides rate limiting capabilities:
- Token bucket algorithm
- Leaky bucket algorithm
- Fixed window
- Sliding window
- Per-domain rate limiting
- Global rate limiting
"""

import time
import threading
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class RateLimitConfig:
    """Configuration for rate limiter."""
    algorithm: str = 'token_bucket'  # token_bucket, leaky_bucket, fixed_window, sliding_window
    max_requests: int = 100  # Maximum requests
    time_window: float = 60.0  # Time window in seconds
    burst_size: int = 10  # Maximum burst size
    refill_rate: float = 1.0  # Tokens per second
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'algorithm': self.algorithm,
            'max_requests': self.max_requests,
            'time_window': self.time_window,
            'burst_size': self.burst_size,
            'refill_rate': self.refill_rate,
        }


@dataclass
class RateLimitStatus:
    """Status of rate limiter."""
    allowed: bool
    remaining: int
    reset_time: float

    @property
    def reset_in(self) -> float:
        """Seconds until reset - derived, since reset_time is an absolute epoch."""
        return max(0.0, self.reset_time - time.time())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'allowed': self.allowed,
            'remaining': self.remaining,
            'reset_time': self.reset_time,
            'reset_in': self.reset_in,
        }


class TokenBucket:
    """
    Token bucket rate limiter.
    
    Allows bursts of requests up to a maximum size,
    with tokens refilling at a constant rate.
    """
    
    def __init__(self, max_tokens: int, refill_rate: float):
        """
        Initialize the token bucket.
        
        Args:
            max_tokens: Maximum number of tokens (bucket size).
            refill_rate: Tokens per second.
        """
        self.max_tokens = max_tokens
        self.refill_rate = refill_rate
        self.tokens = max_tokens
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def allow(self, tokens: int = 1) -> bool:
        """
        Check if a request is allowed.
        
        Args:
            tokens: Number of tokens to consume.
            
        Returns:
            True if allowed.
        """
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on elapsed time
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.max_tokens, self.tokens + new_tokens)
        self.last_refill = now
    
    def get_status(self) -> RateLimitStatus:
        """
        Get the current status.
        
        Returns:
            RateLimitStatus.
        """
        with self.lock:
            self._refill()
            
            return RateLimitStatus(
                allowed=self.tokens >= 1,
                remaining=int(self.tokens),
                reset_time=self.last_refill + (self.max_tokens - self.tokens) / self.refill_rate,
            )


class LeakyBucket:
    """
    Leaky bucket rate limiter.
    
    Requests are processed at a constant rate.
    If the bucket is full, new requests are rejected.
    """
    
    def __init__(self, capacity: int, leak_rate: float):
        """
        Initialize the leaky bucket.
        
        Args:
            capacity: Maximum capacity of the bucket.
            leak_rate: Items per second that leak from the bucket.
        """
        self.capacity = capacity
        self.leak_rate = leak_rate
        self.water = 0.0
        self.last_leak = time.time()
        self.lock = threading.Lock()
    
    def allow(self, items: int = 1) -> bool:
        """
        Check if a request is allowed.
        
        Args:
            items: Number of items to add.
            
        Returns:
            True if allowed.
        """
        with self.lock:
            self._leak()
            
            if self.water + items <= self.capacity:
                self.water += items
                return True
            
            return False
    
    def _leak(self):
        """Leak water from the bucket."""
        now = time.time()
        elapsed = now - self.last_leak
        
        # Remove water based on elapsed time
        leaked = elapsed * self.leak_rate
        self.water = max(0, self.water - leaked)
        self.last_leak = now
    
    def get_status(self) -> RateLimitStatus:
        """
        Get the current status.
        
        Returns:
            RateLimitStatus.
        """
        with self.lock:
            self._leak()
            
            return RateLimitStatus(
                allowed=self.water < self.capacity,
                remaining=int(self.capacity - self.water),
                reset_time=self.last_leak + (self.water / self.leak_rate) if self.water > 0 else 0,
            )


class FixedWindow:
    """
    Fixed window rate limiter.
    
    Allows a maximum number of requests per fixed time window.
    """
    
    def __init__(self, max_requests: int, window_size: float):
        """
        Initialize the fixed window.
        
        Args:
            max_requests: Maximum requests per window.
            window_size: Size of the window in seconds.
        """
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests = []
        self.lock = threading.Lock()
    
    def allow(self) -> bool:
        """
        Check if a request is allowed.
        
        Returns:
            True if allowed.
        """
        with self.lock:
            now = time.time()
            
            # Remove old requests
            self.requests = [t for t in self.requests if now - t < self.window_size]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def get_status(self) -> RateLimitStatus:
        """
        Get the current status.
        
        Returns:
            RateLimitStatus.
        """
        with self.lock:
            now = time.time()
            
            # Remove old requests
            self.requests = [t for t in self.requests if now - t < self.window_size]
            
            # Find reset time (start of next window)
            if self.requests:
                oldest = min(self.requests)
                reset_time = oldest + self.window_size
            else:
                reset_time = now + self.window_size
            
            return RateLimitStatus(
                allowed=len(self.requests) < self.max_requests,
                remaining=self.max_requests - len(self.requests),
                reset_time=reset_time,
            )


class SlidingWindow:
    """
    Sliding window rate limiter.
    
    Allows a maximum number of requests in a sliding time window.
    """
    
    def __init__(self, max_requests: int, window_size: float):
        """
        Initialize the sliding window.
        
        Args:
            max_requests: Maximum requests per window.
            window_size: Size of the window in seconds.
        """
        self.max_requests = max_requests
        self.window_size = window_size
        self.requests = []
        self.lock = threading.Lock()
    
    def allow(self) -> bool:
        """
        Check if a request is allowed.
        
        Returns:
            True if allowed.
        """
        with self.lock:
            now = time.time()
            
            # Remove old requests
            self.requests = [t for t in self.requests if now - t < self.window_size]
            
            if len(self.requests) < self.max_requests:
                self.requests.append(now)
                return True
            
            return False
    
    def get_status(self) -> RateLimitStatus:
        """
        Get the current status.
        
        Returns:
            RateLimitStatus.
        """
        with self.lock:
            now = time.time()
            
            # Remove old requests
            self.requests = [t for t in self.requests if now - t < self.window_size]
            
            # Find reset time (when oldest request will expire)
            if self.requests:
                oldest = min(self.requests)
                reset_time = oldest + self.window_size
            else:
                reset_time = now
            
            return RateLimitStatus(
                allowed=len(self.requests) < self.max_requests,
                remaining=self.max_requests - len(self.requests),
                reset_time=reset_time,
            )


class RateLimiter:
    """
    Rate limiter for distributed scraping.
    
    Provides:
    - Multiple rate limiting algorithms
    - Per-domain rate limiting
    - Global rate limiting
    - Statistics and monitoring
    """
    
    def __init__(self, config: RateLimitConfig = None):
        """
        Initialize the rate limiter.
        
        Args:
            config: RateLimitConfig instance.
        """
        self.config = config or RateLimitConfig()
        self._global_limiter = self._create_limiter()
        self._domain_limiters: Dict[str, Any] = defaultdict(self._create_limiter)
        self._stats: Dict[str, Any] = {
            'total_requests': 0,
            'allowed_requests': 0,
            'rejected_requests': 0,
            'by_domain': defaultdict(lambda: {'allowed': 0, 'rejected': 0}),
        }
        self._lock = threading.Lock()
    
    def _create_limiter(self) -> Any:
        """Create a rate limiter based on configuration."""
        if self.config.algorithm == 'token_bucket':
            return TokenBucket(
                max_tokens=self.config.burst_size,
                refill_rate=self.config.refill_rate
            )
        elif self.config.algorithm == 'leaky_bucket':
            return LeakyBucket(
                capacity=self.config.max_requests,
                leak_rate=self.config.refill_rate
            )
        elif self.config.algorithm == 'fixed_window':
            return FixedWindow(
                max_requests=self.config.max_requests,
                window_size=self.config.time_window
            )
        elif self.config.algorithm == 'sliding_window':
            return SlidingWindow(
                max_requests=self.config.max_requests,
                window_size=self.config.time_window
            )
        else:
            return TokenBucket(
                max_tokens=self.config.burst_size,
                refill_rate=self.config.refill_rate
            )
    
    def allow(self, domain: str = None, tokens: int = 1) -> bool:
        """
        Check if a request is allowed.
        
        Args:
            domain: Domain to check (None for global).
            tokens: Number of tokens to consume.
            
        Returns:
            True if allowed.
        """
        with self._lock:
            self._stats['total_requests'] += 1
            
            # Check global limit
            if not self._global_limiter.allow(tokens):
                self._stats['rejected_requests'] += 1
                if domain:
                    self._stats['by_domain'][domain]['rejected'] += 1
                return False
            
            # Check domain limit
            if domain:
                domain_limiter = self._domain_limiters[domain]
                if not domain_limiter.allow(tokens):
                    self._stats['rejected_requests'] += 1
                    self._stats['by_domain'][domain]['rejected'] += 1
                    # Return token to global limiter
                    # (In a real implementation, we'd need to handle this)
                    return False
                
                self._stats['by_domain'][domain]['allowed'] += 1
            
            self._stats['allowed_requests'] += 1
            return True
    
    def get_status(self, domain: str = None) -> RateLimitStatus:
        """
        Get the current status.
        
        Args:
            domain: Domain to check (None for global).
            
        Returns:
            RateLimitStatus.
        """
        if domain:
            return self._domain_limiters[domain].get_status()
        else:
            return self._global_limiter.get_status()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get rate limiter statistics.
        
        Returns:
            Dictionary with statistics.
        """
        with self._lock:
            return {
                'total_requests': self._stats['total_requests'],
                'allowed_requests': self._stats['allowed_requests'],
                'rejected_requests': self._stats['rejected_requests'],
                'rejection_rate': self._stats['rejected_requests'] / self._stats['total_requests'] if self._stats['total_requests'] > 0 else 0,
                'by_domain': dict(self._stats['by_domain']),
                'global_status': self._global_limiter.get_status().to_dict(),
            }
    
    def reset(self, domain: str = None):
        """
        Reset the rate limiter.
        
        Args:
            domain: Domain to reset (None for all).
        """
        with self._lock:
            if domain:
                if domain in self._domain_limiters:
                    del self._domain_limiters[domain]
            else:
                self._global_limiter = self._create_limiter()
                self._domain_limiters.clear()
                self._stats = {
                    'total_requests': 0,
                    'allowed_requests': 0,
                    'rejected_requests': 0,
                    'by_domain': defaultdict(lambda: {'allowed': 0, 'rejected': 0}),
                }
    
    def wait_for_token(self, domain: str = None, timeout: float = 60.0) -> bool:
        """
        Wait for a token to be available.
        
        Args:
            domain: Domain to check (None for global).
            timeout: Maximum time to wait in seconds.
            
        Returns:
            True if token obtained.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.allow(domain):
                return True
            
            # Calculate wait time
            if domain:
                status = self._domain_limiters[domain].get_status()
            else:
                status = self._global_limiter.get_status()
            
            wait_time = max(0, status.reset_time - time.time())
            
            if wait_time > 0:
                time.sleep(min(wait_time, 1.0))  # Sleep for at most 1 second
            else:
                time.sleep(0.1)  # Small sleep to prevent busy waiting
        
        return False
    
    def set_rate_limit(self, domain: str, max_requests: int, time_window: float):
        """
        Set a custom rate limit for a domain.
        
        Args:
            domain: Domain to set limit for.
            max_requests: Maximum requests.
            time_window: Time window in seconds.
        """
        with self._lock:
            # Create a fixed window limiter for this domain
            self._domain_limiters[domain] = FixedWindow(
                max_requests=max_requests,
                window_size=time_window
            )


# Global rate limiter instance
rate_limiter = RateLimiter()
