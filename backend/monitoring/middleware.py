"""
Logging Middleware for Flask

Provides automatic request/response logging for Flask applications.
"""

import time
import json
from typing import Callable, Optional
from flask import Flask, request, g
from datetime import datetime
import logging

from .logger import get_logger


class LoggingMiddleware:
    """
    Flask middleware for automatic request/response logging.
    """
    
    def __init__(self, app: Flask = None, log_level: int = logging.INFO):
        """
        Initialize logging middleware.
        
        Args:
            app: Flask application.
            log_level: Minimum log level for requests.
        """
        self.app = app
        self.log_level = log_level
        self.logger = get_logger('middleware')
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """
        Initialize middleware with Flask app.
        
        Args:
            app: Flask application.
        """
        self.app = app
        
        # Register before_request handler
        @app.before_request
        def before_request():
            g.request_start_time = time.time()
            g.request_id = self._generate_request_id()
        
        # Register after_request handler
        @app.after_request
        def after_request(response):
            self._log_request(response)
            return response
        
        # Register error handler
        @app.errorhandler(Exception)
        def handle_exception(e):
            self._log_error(e)
            return e
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _log_request(self, response):
        """Log request details."""
        try:
            # Calculate duration
            duration = time.time() - g.request_start_time
            duration_ms = duration * 1000
            
            # Get request info
            request_info = {
                'request_id': g.get('request_id', 'unknown'),
                'method': request.method,
                'path': request.path,
                'url': request.url,
                'remote_addr': request.remote_addr,
                'user_agent': request.user_agent.string if request.user_agent else None,
                'status_code': response.status_code,
                'duration_ms': duration_ms,
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            # Add query parameters (sanitized)
            if request.args:
                request_info['query_params'] = dict(request.args)
            
            # Add headers (sanitized)
            headers = {}
            for key in ['Content-Type', 'Authorization', 'User-Agent', 'Accept']:
                if key in request.headers:
                    headers[key] = request.headers[key]
            if headers:
                request_info['headers'] = headers
            
            # Add user info if authenticated
            if hasattr(request, 'user'):
                request_info['user'] = {
                    'id': request.user.get('sub'),
                    'username': request.user.get('username'),
                    'role': request.user.get('role'),
                }
            
            # Log based on status code
            if response.status_code >= 500:
                self.logger.error("Request failed", extra=request_info)
            elif response.status_code >= 400:
                self.logger.warning("Request warning", extra=request_info)
            else:
                self.logger.info("Request completed", extra=request_info)
        except Exception as e:
            self.logger.error(f"Failed to log request: {e}")
    
    def _log_error(self, exception: Exception):
        """Log error details."""
        try:
            error_info = {
                'request_id': g.get('request_id', 'unknown'),
                'method': request.method,
                'path': request.path,
                'error': str(exception),
                'error_type': type(exception).__name__,
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            # Add user info if authenticated
            if hasattr(request, 'user'):
                error_info['user'] = {
                    'id': request.user.get('sub'),
                    'username': request.user.get('username'),
                }
            
            self.logger.error("Request error", extra=error_info, exc_info=True)
        except Exception as e:
            self.logger.error(f"Failed to log error: {e}")


def init_logging_middleware(app: Flask):
    """
    Initialize logging middleware with Flask app.
    
    Args:
        app: Flask application.
    """
    middleware = LoggingMiddleware(app)
    return middleware
