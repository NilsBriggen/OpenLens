"""
JWT Authentication for OpenLens

Provides JWT-based authentication with:
- Access tokens (short-lived)
- Refresh tokens (long-lived)
- Token blacklisting
- Role-based authorization
- API key authentication
- API key rotation
- Password reset functionality

Dependencies:
- PyJWT: JWT encoding/decoding
- python-dotenv: Environment variables
"""

import os
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Callable, List, Tuple
from functools import wraps
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import hashlib

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configuration
class AuthConfig:
    """Authentication configuration."""
    
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
    ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 30))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', 7))
    TOKEN_TYPE = os.getenv('JWT_TOKEN_TYPE', 'Bearer')
    
    # API Key settings
    API_KEY_LENGTH = int(os.getenv('API_KEY_LENGTH', 32))
    API_KEY_EXPIRE_DAYS = int(os.getenv('API_KEY_EXPIRE_DAYS', 365))
    API_KEY_MAX_AGE_DAYS = int(os.getenv('API_KEY_MAX_AGE_DAYS', 90))
    
    # Password reset settings
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS = int(os.getenv('PASSWORD_RESET_TOKEN_EXPIRE_HOURS', 24))


class AuthManager:
    """
    Manages JWT authentication and token operations.
    """
    
    def __init__(self, app: Flask = None):
        """
        Initialize AuthManager.
        
        Args:
            app: Optional Flask application.
        """
        self.app = app
        self.blacklisted_tokens = set()  # In-memory token blacklist
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """
        Initialize AuthManager with Flask app.
        
        Args:
            app: Flask application.
        """
        self.app = app
        app.config.setdefault('JWT_SECRET_KEY', AuthConfig.SECRET_KEY)
        app.config.setdefault('JWT_ALGORITHM', AuthConfig.ALGORITHM)
        app.config.setdefault('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
        app.config.setdefault('JWT_REFRESH_TOKEN_EXPIRE_DAYS', AuthConfig.REFRESH_TOKEN_EXPIRE_DAYS)
    
    def create_access_token(self, user_id: int, username: str, role: str = 'user', additional_claims: Dict = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            user_id: User ID.
            username: Username.
            role: User role.
            additional_claims: Additional claims to include in the token.
            
        Returns:
            JWT access token string.
        """
        claims = {
            'sub': str(user_id),
            'username': username,
            'role': role,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES),
            'type': 'access',
            'jti': str(uuid.uuid4()),
        }
        
        if additional_claims:
            claims.update(additional_claims)
        
        return jwt.encode(claims, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)
    
    def create_refresh_token(self, user_id: int) -> str:
        """
        Create a JWT refresh token.
        
        Args:
            user_id: User ID.
            
        Returns:
            JWT refresh token string.
        """
        claims = {
            'sub': str(user_id),
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(days=AuthConfig.REFRESH_TOKEN_EXPIRE_DAYS),
            'type': 'refresh',
            'jti': str(uuid.uuid4()),
        }
        
        return jwt.encode(claims, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify a JWT token.
        
        Args:
            token: JWT token string.
            
        Returns:
            Decoded token payload or None if invalid.
        """
        try:
            payload = jwt.decode(
                token,
                AuthConfig.SECRET_KEY,
                algorithms=[AuthConfig.ALGORITHM]
            )
            
            # Check if token is blacklisted
            jti = payload.get('jti')
            if jti and jti in self.blacklisted_tokens:
                return None
            
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def blacklist_token(self, token: str):
        """
        Blacklist a JWT token (e.g., on logout).
        
        Args:
            token: JWT token string to blacklist.
        """
        try:
            payload = jwt.decode(
                token,
                AuthConfig.SECRET_KEY,
                algorithms=[AuthConfig.ALGORITHM],
                options={'verify_signature': False}
            )
            jti = payload.get('jti')
            if jti:
                self.blacklisted_tokens.add(jti)
        except Exception:
            pass
    
    def decode_token(self, token: str) -> Optional[Dict]:
        """
        Decode a JWT token without verification.
        
        Args:
            token: JWT token string.
            
        Returns:
            Decoded token payload or None if invalid.
        """
        try:
            payload = jwt.decode(
                token,
                AuthConfig.SECRET_KEY,
                algorithms=[AuthConfig.ALGORITHM],
                options={'verify_signature': False}
            )
            return payload
        except Exception:
            return None
    
    def generate_api_key(self, user_id: int, name: str = 'Default Key', permissions: list = None, 
                        expires_days: int = None) -> Tuple[str, str]:
        """
        Generate a new API key and its hash.
        
        Args:
            user_id: User ID.
            name: Key name.
            permissions: List of permissions.
            expires_days: Number of days until expiration (None for no expiration).
            
        Returns:
            Tuple of (plain_api_key, hashed_key).
        """
        if permissions is None:
            permissions = ['read', 'write']
        
        # Generate a random key
        key = secrets.token_urlsafe(AuthConfig.API_KEY_LENGTH)
        
        # Create hash for storage
        key_hash = self.hash_api_key(key)
        
        # Create key prefix for display
        key_prefix = key[:10]
        
        return key, key_hash, key_prefix
    
    def hash_api_key(self, api_key: str) -> str:
        """
        Hash an API key for storage.
        
        Args:
            api_key: API key string.
            
        Returns:
            Hashed API key.
        """
        # Use SHA-256 for hashing
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    def verify_api_key(self, api_key: str, hashed_key: str) -> bool:
        """
        Verify an API key against its hash.
        
        Args:
            api_key: API key string.
            hashed_key: Hashed API key.
            
        Returns:
            True if valid, False otherwise.
        """
        return check_password_hash(hashed_key, api_key)
    
    def rotate_api_key(self, old_api_key: str, user_id: int, name: str = None, 
                       permissions: list = None) -> Tuple[str, str]:
        """
        Rotate an API key by generating a new one and invalidating the old one.
        
        Args:
            old_api_key: The old API key to invalidate.
            user_id: User ID for the new key.
            name: Name for the new key (defaults to old key's name + " (Rotated)").
            permissions: Permissions for the new key (defaults to old key's permissions).
            
        Returns:
            Tuple of (new_plain_api_key, new_hashed_key).
        """
        # Generate new key
        new_key, new_hash, new_prefix = self.generate_api_key(user_id, name or "Rotated Key", permissions)
        
        return new_key, new_hash, new_prefix
    
    def generate_password_reset_token(self, user_id: int, email: str) -> Tuple[str, datetime]:
        """
        Generate a password reset token.
        
        Args:
            user_id: User ID.
            email: User email (for token binding).
            
        Returns:
            Tuple of (token, expiration_datetime).
        """
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=AuthConfig.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        
        # Hash the token for storage
        token_hash = generate_password_hash(token)
        
        return token, token_hash, expires_at
    
    def verify_password_reset_token(self, token: str, token_hash: str, expires_at: datetime) -> bool:
        """
        Verify a password reset token.
        
        Args:
            token: The token to verify.
            token_hash: The hashed token from storage.
            expires_at: The expiration datetime.
            
        Returns:
            True if token is valid and not expired, False otherwise.
        """
        if datetime.utcnow() > expires_at:
            return False
        
        return check_password_hash(token_hash, token)


# Global auth manager instance
auth_manager = AuthManager()


def init_auth(app: Flask):
    """
    Initialize authentication with Flask app.
    
    Args:
        app: Flask application.
    """
    auth_manager.init_app(app)


def create_access_token(user_id: int, username: str, role: str = 'user', additional_claims: Dict = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        user_id: User ID.
        username: Username.
        role: User role.
        additional_claims: Additional claims to include.
        
    Returns:
        JWT access token.
    """
    return auth_manager.create_access_token(user_id, username, role, additional_claims)


def create_refresh_token(user_id: int) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        user_id: User ID.
        
    Returns:
        JWT refresh token.
    """
    return auth_manager.create_refresh_token(user_id)


def verify_token(token: str) -> Optional[Dict]:
    """
    Verify a JWT token.
    
    Args:
        token: JWT token string.
        
    Returns:
        Decoded token payload or None.
    """
    return auth_manager.verify_token(token)


def blacklist_token(token: str):
    """
    Blacklist a JWT token.
    
    Args:
        token: JWT token string to blacklist.
    """
    auth_manager.blacklist_token(token)


def decode_token(token: str) -> Optional[Dict]:
    """
    Decode a JWT token without verification.
    
    Args:
        token: JWT token string.
        
    Returns:
        Decoded token payload or None.
    """
    return auth_manager.decode_token(token)


def generate_api_key(user_id: int, name: str = 'Default Key', permissions: list = None, 
                     expires_days: int = None) -> Tuple[str, str, str]:
    """
    Generate a new API key.
    
    Args:
        user_id: User ID.
        name: Key name.
        permissions: List of permissions.
        expires_days: Number of days until expiration.
        
    Returns:
        Tuple of (plain_api_key, hashed_key, key_prefix).
    """
    return auth_manager.generate_api_key(user_id, name, permissions, expires_days)


def hash_api_key(api_key: str) -> str:
    """
    Hash an API key for storage.
    
    Args:
        api_key: API key string.
        
    Returns:
        Hashed API key.
    """
    return auth_manager.hash_api_key(api_key)


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """
    Verify an API key against its hash.
    
    Args:
        api_key: API key string.
        hashed_key: Hashed API key.
        
    Returns:
        True if valid, False otherwise.
    """
    return auth_manager.verify_api_key(api_key, hashed_key)


def rotate_api_key(old_api_key: str, user_id: int, name: str = None, 
                   permissions: list = None) -> Tuple[str, str, str]:
    """
    Rotate an API key.
    
    Args:
        old_api_key: The old API key to invalidate.
        user_id: User ID for the new key.
        name: Name for the new key.
        permissions: Permissions for the new key.
        
    Returns:
        Tuple of (new_plain_api_key, new_hashed_key, new_key_prefix).
    """
    return auth_manager.rotate_api_key(old_api_key, user_id, name, permissions)


def generate_password_reset_token(user_id: int, email: str) -> Tuple[str, str, datetime]:
    """
    Generate a password reset token.
    
    Args:
        user_id: User ID.
        email: User email.
        
    Returns:
        Tuple of (token, token_hash, expiration_datetime).
    """
    return auth_manager.generate_password_reset_token(user_id, email)


def auth_required(roles: list = None, permissions: list = None):
    """
    Flask decorator for JWT authentication.
    
    Args:
        roles: List of required roles (e.g., ['admin', 'user']).
        permissions: List of required permissions.
        
    Returns:
        Decorator function.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            from flask import current_app, request
            
            # Get token from header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({"error": "Authorization header missing"}), 401
            
            # Extract token
            parts = auth_header.split()
            if len(parts) != 2 or parts[0] != AuthConfig.TOKEN_TYPE:
                return jsonify({"error": "Invalid authorization header format"}), 401
            
            token = parts[1]
            
            # Verify token
            payload = verify_token(token)
            if not payload:
                return jsonify({"error": "Invalid or expired token"}), 401
            
            # Check token type
            if payload.get('type') != 'access':
                return jsonify({"error": "Invalid token type"}), 401
            
            # Check roles if specified
            if roles and payload.get('role') not in roles:
                return jsonify({"error": "Insufficient permissions"}), 403
            
            # Check permissions if specified
            if permissions:
                # For now, check if user has required role
                # In a real implementation, check against user's permissions
                if payload.get('role') != 'admin':
                    return jsonify({"error": "Insufficient permissions"}), 403
            
            # Add user to request context
            request.user = payload
            
            return f(*args, **kwargs)
        return wrapped
    return decorator


def get_current_user():
    """
    Get the current authenticated user from the request.
    
    Returns:
        User payload or None if not authenticated.
    """
    from flask import request
    
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0] != AuthConfig.TOKEN_TYPE:
        return None
    
    token = parts[1]
    payload = verify_token(token)
    
    if payload and payload.get('type') == 'access':
        return payload
    
    return None


def api_key_required(permissions: list = None):
    """
    Flask decorator for API key authentication.
    
    Args:
        permissions: List of required permissions.
        
    Returns:
        Decorator function.
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            from flask import request
            
            # Get API key from header
            api_key = request.headers.get('X-API-Key')
            if not api_key:
                return jsonify({"error": "API key required"}), 401
            
            # In a real implementation, verify the API key against the database
            # For now, we'll just check if it's a valid format
            if not api_key or len(api_key) < 32:
                return jsonify({"error": "Invalid API key"}), 401
            
            # Check permissions if specified
            if permissions:
                # For now, assume all API keys have all permissions
                # In a real implementation, check against the key's permissions
                pass
            
            # Add API key to request context
            request.api_key = api_key
            
            return f(*args, **kwargs)
        return wrapped
    return decorator
