"""
Rate Limiting Middleware for Flask

Provides rate limiting functionality to prevent abuse of the API.
Uses a simple in-memory store for rate limiting (suitable for single-instance deployments).
For production, consider using Redis or a dedicated rate limiting service.

Supports:
- Per-IP rate limiting
- Per-user rate limiting (when authenticated)
- Per-endpoint rate limiting
- API key rate limiting
"""

from flask import Flask, request, jsonify, current_app, g
from functools import wraps
from datetime import datetime, timedelta
from collections import defaultdict
import time
import hashlib


class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    Attributes:
        store: Dictionary to store request counts per key.
        user_store: Dictionary to store request counts per user.
        default_limit: Default number of requests allowed per window.
        default_window: Default time window in seconds.
        user_default_limit: Default number of requests allowed per user per window.
        user_default_window: Default time window in seconds for user rate limiting.
    """
    
    def __init__(self, default_limit: int = 100, default_window: int = 60, 
                 user_default_limit: int = 1000, user_default_window: int = 3600):
        """
        Initialize the rate limiter.
        
        Args:
            default_limit: Default number of requests allowed per window (per IP).
            default_window: Default time window in seconds (per IP).
            user_default_limit: Default number of requests allowed per user per window.
            user_default_window: Default time window in seconds for user rate limiting.
        """
        self.store = defaultdict(list)  # IP-based rate limiting
        self.user_store = defaultdict(list)  # User-based rate limiting
        self.api_key_store = defaultdict(list)  # API key-based rate limiting
        self.endpoint_store = defaultdict(list)  # Endpoint-based rate limiting
        self.default_limit = default_limit
        self.default_window = default_window
        self.user_default_limit = user_default_limit
        self.user_default_window = user_default_window
    
    def is_rate_limited(self, ip: str, limit: int = None, window: int = None) -> bool:
        """
        Check if an IP has exceeded its rate limit.
        
        Args:
            ip: IP address to check.
            limit: Number of requests allowed (defaults to default_limit).
            window: Time window in seconds (defaults to default_window).
            
        Returns:
            True if rate limited, False otherwise.
        """
        limit = limit or self.default_limit
        window = window or self.default_window
        
        now = time.time()
        # Remove timestamps older than the window
        self.store[ip] = [t for t in self.store[ip] if now - t < window]
        
        if len(self.store[ip]) >= limit:
            return True
        
        # Add current timestamp
        self.store[ip].append(now)
        return False
    
    def is_user_rate_limited(self, user_id: str, limit: int = None, window: int = None) -> bool:
        """
        Check if a user has exceeded their rate limit.
        
        Args:
            user_id: User ID to check.
            limit: Number of requests allowed (defaults to user_default_limit).
            window: Time window in seconds (defaults to user_default_window).
            
        Returns:
            True if rate limited, False otherwise.
        """
        limit = limit or self.user_default_limit
        window = window or self.user_default_window
        
        now = time.time()
        # Remove timestamps older than the window
        self.user_store[user_id] = [t for t in self.user_store[user_id] if now - t < window]
        
        if len(self.user_store[user_id]) >= limit:
            return True
        
        # Add current timestamp
        self.user_store[user_id].append(now)
        return False
    
    def is_api_key_rate_limited(self, api_key: str, limit: int = None, window: int = None) -> bool:
        """
        Check if an API key has exceeded its rate limit.
        
        Args:
            api_key: API key to check.
            limit: Number of requests allowed (defaults to default_limit).
            window: Time window in seconds (defaults to default_window).
            
        Returns:
            True if rate limited, False otherwise.
        """
        # Hash the API key for storage (security)
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        limit = limit or self.default_limit
        window = window or self.default_window
        
        now = time.time()
        # Remove timestamps older than the window
        self.api_key_store[key_hash] = [t for t in self.api_key_store[key_hash] if now - t < window]
        
        if len(self.api_key_store[key_hash]) >= limit:
            return True
        
        # Add current timestamp
        self.api_key_store[key_hash].append(now)
        return False
    
    def is_endpoint_rate_limited(self, endpoint: str, limit: int = None, window: int = None) -> bool:
        """
        Check if an endpoint has exceeded its rate limit.
        
        Args:
            endpoint: Endpoint path to check.
            limit: Number of requests allowed (defaults to default_limit * 10).
            window: Time window in seconds (defaults to default_window).
            
        Returns:
            True if rate limited, False otherwise.
        """
        limit = limit or self.default_limit * 10
        window = window or self.default_window
        
        now = time.time()
        # Remove timestamps older than the window
        self.endpoint_store[endpoint] = [t for t in self.endpoint_store[endpoint] if now - t < window]
        
        if len(self.endpoint_store[endpoint]) >= limit:
            return True
        
        # Add current timestamp
        self.endpoint_store[endpoint].append(now)
        return False
    
    def reset(self, ip: str = None, user_id: str = None, api_key: str = None, endpoint: str = None):
        """
        Reset rate limiting for a specific key or all keys.
        
        Args:
            ip: IP address to reset. If None, resets all IPs.
            user_id: User ID to reset.
            api_key: API key to reset.
            endpoint: Endpoint to reset.
        """
        if ip:
            self.store[ip] = []
        if user_id:
            self.user_store[user_id] = []
        if api_key:
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            self.api_key_store[key_hash] = []
        if endpoint:
            self.endpoint_store[endpoint] = []
        
        if not any([ip, user_id, api_key, endpoint]):
            # Reset all
            self.store.clear()
            self.user_store.clear()
            self.api_key_store.clear()
            self.endpoint_store.clear()
    
    def get_remaining_requests(self, ip: str = None, user_id: str = None, api_key: str = None) -> int:
        """
        Get remaining requests for a given key.
        
        Args:
            ip: IP address to check.
            user_id: User ID to check.
            api_key: API key to check.
            
        Returns:
            Number of remaining requests.
        """
        if ip:
            now = time.time()
            self.store[ip] = [t for t in self.store[ip] if now - t < self.default_window]
            return max(0, self.default_limit - len(self.store[ip]))
        elif user_id:
            now = time.time()
            self.user_store[user_id] = [t for t in self.user_store[user_id] if now - t < self.user_default_window]
            return max(0, self.user_default_limit - len(self.user_store[user_id]))
        elif api_key:
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            now = time.time()
            self.api_key_store[key_hash] = [t for t in self.api_key_store[key_hash] if now - t < self.default_window]
            return max(0, self.default_limit - len(self.api_key_store[key_hash]))
        return 0


def rate_limit(limit: int = None, window: int = None, key_func=None, user_limit: int = None, 
               user_window: int = None, endpoint_limit: int = None):
    """
    Flask decorator for rate limiting.
    
    Args:
        limit: Number of requests allowed per window (per IP).
        window: Time window in seconds (per IP).
        key_func: Function to extract the key (e.g., IP address) from the request.
                  Defaults to request.remote_addr.
        user_limit: Number of requests allowed per user per window.
        user_window: Time window in seconds for user rate limiting.
        endpoint_limit: Number of requests allowed per endpoint per window.
    
    Returns:
        Decorator function.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            from flask import current_app
            
            # Get or create rate limiter
            if not hasattr(current_app, 'rate_limiter'):
                current_app.rate_limiter = RateLimiter()
            
            rate_limiter = current_app.rate_limiter
            
            # Get key (default: IP address)
            key = key_func(request) if key_func else request.remote_addr
            
            # Check IP rate limit
            if rate_limiter.is_rate_limited(key, limit, window):
                return jsonify({
                    "error": f"Rate limit exceeded. Please try again in {window or 60} seconds.",
                    "retry_after": window or 60
                }), 429
            
            # Check user rate limit if authenticated
            if user_limit or user_window:
                user = getattr(request, 'user', None)
                if user:
                    user_id = str(user.get('sub', user.get('id', '')))
                    if user_id:
                        if rate_limiter.is_user_rate_limited(user_id, user_limit, user_window):
                            return jsonify({
                                "error": f"User rate limit exceeded. Please try again later.",
                                "retry_after": user_window or 3600
                            }), 429
            
            # Check endpoint rate limit
            if endpoint_limit:
                endpoint = request.path
                if rate_limiter.is_endpoint_rate_limited(endpoint, endpoint_limit):
                    return jsonify({
                        "error": f"Endpoint rate limit exceeded. Please try again later.",
                        "retry_after": 60
                    }), 429
            
            return f(*args, **kwargs)
        return wrapped
    return decorator


def user_rate_limit(limit: int = None, window: int = None):
    """
    Flask decorator for user-specific rate limiting.
    
    Args:
        limit: Number of requests allowed per user per window.
        window: Time window in seconds.
        
    Returns:
        Decorator function.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            from flask import current_app
            
            # Get or create rate limiter
            if not hasattr(current_app, 'rate_limiter'):
                current_app.rate_limiter = RateLimiter()
            
            rate_limiter = current_app.rate_limiter
            
            # Check if user is authenticated
            user = getattr(request, 'user', None)
            if not user:
                return jsonify({"error": "Authentication required"}), 401
            
            user_id = str(user.get('sub', user.get('id', '')))
            if not user_id:
                return jsonify({"error": "Invalid user"}), 401
            
            # Check user rate limit
            if rate_limiter.is_user_rate_limited(user_id, limit, window):
                return jsonify({
                    "error": f"User rate limit exceeded. Please try again in {window or 3600} seconds.",
                    "retry_after": window or 3600
                }), 429
            
            return f(*args, **kwargs)
        return wrapped
    return decorator


def api_key_rate_limit(limit: int = None, window: int = None):
    """
    Flask decorator for API key-specific rate limiting.
    
    Args:
        limit: Number of requests allowed per API key per window.
        window: Time window in seconds.
        
    Returns:
        Decorator function.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            from flask import current_app
            
            # Get or create rate limiter
            if not hasattr(current_app, 'rate_limiter'):
                current_app.rate_limiter = RateLimiter()
            
            rate_limiter = current_app.rate_limiter
            
            # Get API key from header
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({"error": "API key required"}), 401
            
            # Check API key rate limit
            if rate_limiter.is_api_key_rate_limited(api_key, limit, window):
                return jsonify({
                    "error": f"API key rate limit exceeded. Please try again in {window or 60} seconds.",
                    "retry_after": window or 60
                }), 429
            
            return f(*args, **kwargs)
        return wrapped
    return decorator


def init_rate_limiter(app: Flask, default_limit: int = 100, default_window: int = 60,
                      user_default_limit: int = 1000, user_default_window: int = 3600):
    """
    Initialize rate limiter for a Flask app.
    
    Args:
        app: Flask application.
        default_limit: Default number of requests allowed per window (per IP).
        default_window: Default time window in seconds (per IP).
        user_default_limit: Default number of requests allowed per user per window.
        user_default_window: Default time window in seconds for user rate limiting.
    """
    app.rate_limiter = RateLimiter(default_limit, default_window, user_default_limit, user_default_window)
    
    @app.after_request
    def after_request(response):
        # Clean up old entries periodically
        if hasattr(app, 'rate_limiter') and request.path == '/':
            # Clean up every 100 requests to the root
            rate_limiter = app.rate_limiter
            if len(rate_limiter.store) > 100:
                # Remove IPs with no recent requests
                now = time.time()
                for ip in list(rate_limiter.store.keys()):
                    rate_limiter.store[ip] = [
                        t for t in rate_limiter.store[ip] 
                        if now - t < rate_limiter.default_window * 2
                    ]
                    if not rate_limiter.store[ip]:
                        del rate_limiter.store[ip]
                
                # Clean up user store
                for user_id in list(rate_limiter.user_store.keys()):
                    rate_limiter.user_store[user_id] = [
                        t for t in rate_limiter.user_store[user_id] 
                        if now - t < rate_limiter.user_default_window * 2
                    ]
                    if not rate_limiter.user_store[user_id]:
                        del rate_limiter.user_store[user_id]
                
                # Clean up API key store
                for key_hash in list(rate_limiter.api_key_store.keys()):
                    rate_limiter.api_key_store[key_hash] = [
                        t for t in rate_limiter.api_key_store[key_hash] 
                        if now - t < rate_limiter.default_window * 2
                    ]
                    if not rate_limiter.api_key_store[key_hash]:
                        del rate_limiter.api_key_store[key_hash]
                
                # Clean up endpoint store
                for endpoint in list(rate_limiter.endpoint_store.keys()):
                    rate_limiter.endpoint_store[endpoint] = [
                        t for t in rate_limiter.endpoint_store[endpoint] 
                        if now - t < rate_limiter.default_window * 2
                    ]
                    if not rate_limiter.endpoint_store[endpoint]:
                        del rate_limiter.endpoint_store[endpoint]
        return response
