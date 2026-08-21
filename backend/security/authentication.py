"""
Authentication Service for OpenLens

Provides authentication capabilities:
- User authentication
- Session management
- Token-based authentication
- Multi-factor authentication
- Password policies
"""

import os
import time
import json
import secrets
import hashlib
import threading
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

# Try to import jwt
try:
    import jwt
    from jwt import PyJWKClient
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("PyJWT not available. Install with: pip install PyJWT")

# Try to import bcrypt
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    print("bcrypt not available. Install with: pip install bcrypt")


@dataclass
class UserCredentials:
    """User credentials for authentication."""
    username: str
    password: str
    email: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'username': self.username,
            'password': '*****' if self.password else '',
            'email': self.email,
        }


@dataclass
class AuthenticationResult:
    """Result of authentication."""
    success: bool
    user_id: str = ''
    username: str = ''
    token: str = ''
    expires_at: datetime = None
    error: str = ''
    requires_mfa: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'user_id': self.user_id,
            'username': self.username,
            'token': '*****' if self.token else '',
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'error': self.error,
            'requires_mfa': self.requires_mfa,
        }


@dataclass
class Session:
    """Represents a user session."""
    session_id: str
    user_id: str
    username: str
    token: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = None
    ip_address: str = ''
    user_agent: str = ''
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'username': self.username,
            'token': '*****' if self.token else '',
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'is_active': self.is_active,
        }


@dataclass
class Token:
    """Represents an authentication token."""
    token: str
    user_id: str
    username: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: datetime = None
    token_type: str = 'access'  # access, refresh
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'token': '*****' if self.token else '',
            'user_id': self.user_id,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'token_type': self.token_type,
        }


@dataclass
class PasswordPolicy:
    """Password policy configuration."""
    min_length: int = 8
    max_length: int = 64
    require_uppercase: bool = True
    require_lowercase: bool = True
    require_digit: bool = True
    require_special: bool = True
    special_characters: str = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    max_attempts: int = 5
    lockout_duration: int = 300  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'min_length': self.min_length,
            'max_length': self.max_length,
            'require_uppercase': self.require_uppercase,
            'require_lowercase': self.require_lowercase,
            'require_digit': self.require_digit,
            'require_special': self.require_special,
            'special_characters': self.special_characters,
            'max_attempts': self.max_attempts,
            'lockout_duration': self.lockout_duration,
        }


@dataclass
class AuthenticationConfig:
    """Configuration for authentication service."""
    secret_key: str = ''
    token_expiration: int = 3600  # seconds (1 hour)
    refresh_token_expiration: int = 86400  # seconds (24 hours)
    session_expiration: int = 3600  # seconds (1 hour)
    password_policy: PasswordPolicy = field(default_factory=PasswordPolicy)
    enable_mfa: bool = False
    mfa_issuer: str = 'OpenLens'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'secret_key': '*****' if self.secret_key else '',
            'token_expiration': self.token_expiration,
            'refresh_token_expiration': self.refresh_token_expiration,
            'session_expiration': self.session_expiration,
            'password_policy': self.password_policy.to_dict(),
            'enable_mfa': self.enable_mfa,
            'mfa_issuer': self.mfa_issuer,
        }


class AuthenticationService:
    """
    Authentication service for OpenLens.
    
    Provides:
    - User authentication
    - Session management
    - Token-based authentication
    - Multi-factor authentication
    - Password policies
    """
    
    def __init__(self, config: AuthenticationConfig = None, rbac_service=None):
        """
        Initialize the authentication service.
        
        Args:
            config: AuthenticationConfig instance.
            rbac_service: RBAC service instance.
        """
        self.config = config or AuthenticationConfig()
        self.rbac_service = rbac_service
        self._sessions: Dict[str, Session] = {}
        self._tokens: Dict[str, Token] = {}
        self._failed_attempts: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self._lock = threading.Lock()
        
        # Generate secret key if not provided
        if not self.config.secret_key:
            self.config.secret_key = secrets.token_hex(32)
    
    def authenticate(self, username: str, password: str, 
                    ip_address: str = '', user_agent: str = '') -> AuthenticationResult:
        """
        Authenticate a user.
        
        Args:
            username: Username.
            password: Password.
            ip_address: IP address.
            user_agent: User agent.
            
        Returns:
            AuthenticationResult.
        """
        # Check if user is locked out
        if self._is_user_locked_out(username):
            return AuthenticationResult(
                success=False,
                error='Account locked due to too many failed attempts',
            )
        
        # Get user from RBAC
        user = self.rbac_service.get_user_by_username(username) if self.rbac_service else None
        
        if not user:
            # Record failed attempt
            self._record_failed_attempt(username)
            return AuthenticationResult(
                success=False,
                error='Invalid username or password',
            )
        
        # Verify password
        if not self._verify_password(user, password):
            # Record failed attempt
            self._record_failed_attempt(username)
            return AuthenticationResult(
                success=False,
                error='Invalid username or password',
            )
        
        # Check if user is active
        if not user.is_active:
            return AuthenticationResult(
                success=False,
                error='Account is disabled',
            )
        
        # Reset failed attempts
        self._reset_failed_attempts(username)
        
        # Generate token
        token = self._generate_token(user.user_id, user.username)
        
        # Create session
        session = self._create_session(user.user_id, user.username, token, ip_address, user_agent)
        
        # Check if MFA is required
        requires_mfa = self.config.enable_mfa and self._requires_mfa(user)
        
        return AuthenticationResult(
            success=True,
            user_id=user.user_id,
            username=user.username,
            token=token,
            expires_at=session.expires_at,
            requires_mfa=requires_mfa,
        )
    
    def _verify_password(self, user, password: str) -> bool:
        """Verify a user's password."""
        if not user.password_hash:
            return False
        
        # Use bcrypt if available
        if BCRYPT_AVAILABLE and user.password_hash.startswith('$2b$'):
            return bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8'))
        
        # Fall back to SHA256
        salt = 'openlens_salt'  # In production, use a random salt per user
        expected_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        return secrets.compare_digest(user.password_hash, expected_hash)
    
    def _generate_token(self, user_id: str, username: str) -> str:
        """Generate an authentication token."""
        if JWT_AVAILABLE:
            # Use JWT
            payload = {
                'user_id': user_id,
                'username': username,
                'exp': datetime.utcnow() + timedelta(seconds=self.config.token_expiration),
                'iat': datetime.utcnow(),
            }
            
            token = jwt.encode(payload, self.config.secret_key, algorithm='HS256')
            return token
        else:
            # Fall back to simple token
            token_data = f"{user_id}:{username}:{int(time.time())}"
            return hashlib.sha256((token_data + self.config.secret_key).encode()).hexdigest()
    
    def _create_session(self, user_id: str, username: str, token: str, 
                       ip_address: str, user_agent: str) -> Session:
        """Create a new session."""
        session_id = str(secrets.token_hex(16))
        expires_at = datetime.utcnow() + timedelta(seconds=self.config.session_expiration)
        
        session = Session(
            session_id=session_id,
            user_id=user_id,
            username=username,
            token=token,
            expires_at=expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        
        with self._lock:
            self._sessions[session_id] = session
            self._tokens[token] = Token(
                token=token,
                user_id=user_id,
                username=username,
                expires_at=expires_at,
                token_type='access',
            )
        
        return session
    
    def _is_user_locked_out(self, username: str) -> bool:
        """Check if a user is locked out."""
        with self._lock:
            attempts = self._failed_attempts.get(username, {})
            last_attempt = attempts.get('last_attempt')
            count = attempts.get('count', 0)
            
            if count >= self.config.password_policy.max_attempts:
                lockout_expires = last_attempt + timedelta(seconds=self.config.password_policy.lockout_duration)
                if datetime.utcnow() < lockout_expires:
                    return True
        
        return False
    
    def _record_failed_attempt(self, username: str):
        """Record a failed authentication attempt."""
        with self._lock:
            if username not in self._failed_attempts:
                self._failed_attempts[username] = {'count': 0, 'last_attempt': None}
            
            self._failed_attempts[username]['count'] += 1
            self._failed_attempts[username]['last_attempt'] = datetime.utcnow()
    
    def _reset_failed_attempts(self, username: str):
        """Reset failed attempts for a user."""
        with self._lock:
            if username in self._failed_attempts:
                del self._failed_attempts[username]
    
    def _requires_mfa(self, user) -> bool:
        """Check if MFA is required for a user."""
        # In a real implementation, this would check user settings
        # For now, always return False
        return False
    
    def validate_token(self, token: str) -> Optional[Token]:
        """
        Validate an authentication token.
        
        Args:
            token: Token to validate.
            
        Returns:
            Token object or None.
        """
        with self._lock:
            # Check in-memory tokens first
            if token in self._tokens:
                stored_token = self._tokens[token]
                if stored_token.expires_at > datetime.utcnow():
                    return stored_token
                else:
                    # Token expired, remove it
                    del self._tokens[token]
            
            # Try to decode JWT
            if JWT_AVAILABLE:
                try:
                    payload = jwt.decode(token, self.config.secret_key, algorithms=['HS256'])
                    
                    # Check expiration
                    exp = payload.get('exp')
                    if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                        return None
                    
                    # Create a new token object
                    return Token(
                        token=token,
                        user_id=payload.get('user_id', ''),
                        username=payload.get('username', ''),
                        expires_at=datetime.fromtimestamp(exp) if exp else None,
                        token_type='access',
                    )
                except jwt.ExpiredSignatureError:
                    return None
                except jwt.InvalidTokenError:
                    return None
        
        return None
    
    def invalidate_token(self, token: str) -> bool:
        """
        Invalidate a token.
        
        Args:
            token: Token to invalidate.
            
        Returns:
            True if invalidated.
        """
        with self._lock:
            if token in self._tokens:
                del self._tokens[token]
                return True
            return False
    
    def invalidate_session(self, session_id: str) -> bool:
        """
        Invalidate a session.
        
        Args:
            session_id: Session ID.
            
        Returns:
            True if invalidated.
        """
        with self._lock:
            if session_id in self._sessions:
                session = self._sessions[session_id]
                if session.token in self._tokens:
                    del self._tokens[session.token]
                del self._sessions[session_id]
                return True
            return False
    
    def invalidate_user_sessions(self, user_id: str) -> int:
        """
        Invalidate all sessions for a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            Number of sessions invalidated.
        """
        with self._lock:
            count = 0
            session_ids_to_remove = []
            
            for session_id, session in self._sessions.items():
                if session.user_id == user_id:
                    session_ids_to_remove.append(session_id)
                    if session.token in self._tokens:
                        del self._tokens[session.token]
                    count += 1
            
            for session_id in session_ids_to_remove:
                del self._sessions[session_id]
            
            return count
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session ID.
            
        Returns:
            Session or None.
        """
        with self._lock:
            session = self._sessions.get(session_id)
            if session and session.expires_at > datetime.utcnow():
                return session
            return None
    
    def get_session_by_token(self, token: str) -> Optional[Session]:
        """
        Get a session by token.
        
        Args:
            token: Authentication token.
            
        Returns:
            Session or None.
        """
        with self._lock:
            for session in self._sessions.values():
                if session.token == token and session.expires_at > datetime.utcnow():
                    return session
            return None
    
    def refresh_token(self, refresh_token: str) -> AuthenticationResult:
        """
        Refresh an access token using a refresh token.
        
        Args:
            refresh_token: Refresh token.
            
        Returns:
            AuthenticationResult.
        """
        with self._lock:
            # Check if refresh token exists
            token_obj = self._tokens.get(refresh_token)
            
            if not token_obj or token_obj.token_type != 'refresh':
                return AuthenticationResult(
                    success=False,
                    error='Invalid refresh token',
                )
            
            if token_obj.expires_at < datetime.utcnow():
                return AuthenticationResult(
                    success=False,
                    error='Refresh token expired',
                )
            
            # Get user
            user = self.rbac_service.get_user(token_obj.user_id) if self.rbac_service else None
            
            if not user:
                return AuthenticationResult(
                    success=False,
                    error='User not found',
                )
            
            # Generate new access token
            new_token = self._generate_token(user.user_id, user.username)
            new_expires_at = datetime.utcnow() + timedelta(seconds=self.config.token_expiration)
            
            # Update token
            self._tokens[new_token] = Token(
                token=new_token,
                user_id=user.user_id,
                username=user.username,
                expires_at=new_expires_at,
                token_type='access',
            )
            
            return AuthenticationResult(
                success=True,
                user_id=user.user_id,
                username=user.username,
                token=new_token,
                expires_at=new_expires_at,
            )
    
    def generate_refresh_token(self, user_id: str, username: str) -> str:
        """
        Generate a refresh token.
        
        Args:
            user_id: User ID.
            username: Username.
            
        Returns:
            Refresh token.
        """
        if JWT_AVAILABLE:
            # Use JWT
            payload = {
                'user_id': user_id,
                'username': username,
                'exp': datetime.utcnow() + timedelta(seconds=self.config.refresh_token_expiration),
                'iat': datetime.utcnow(),
                'type': 'refresh',
            }
            
            token = jwt.encode(payload, self.config.secret_key, algorithm='HS256')
            
            with self._lock:
                self._tokens[token] = Token(
                    token=token,
                    user_id=user_id,
                    username=username,
                    expires_at=datetime.utcnow() + timedelta(seconds=self.config.refresh_token_expiration),
                    token_type='refresh',
                )
            
            return token
        else:
            # Fall back to simple token
            token_data = f"refresh:{user_id}:{username}:{int(time.time())}"
            token = hashlib.sha256((token_data + self.config.secret_key).encode()).hexdigest()
            
            with self._lock:
                self._tokens[token] = Token(
                    token=token,
                    user_id=user_id,
                    username=username,
                    expires_at=datetime.utcnow() + timedelta(seconds=self.config.refresh_token_expiration),
                    token_type='refresh',
                )
            
            return token
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change a user's password.
        
        Args:
            user_id: User ID.
            old_password: Old password.
            new_password: New password.
            
        Returns:
            True if password changed.
        """
        # Get user
        user = self.rbac_service.get_user(user_id) if self.rbac_service else None
        
        if not user:
            return False
        
        # Verify old password
        if not self._verify_password(user, old_password):
            return False
        
        # Validate new password
        if not self.validate_password(new_password):
            return False
        
        # Hash new password
        if BCRYPT_AVAILABLE:
            new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        else:
            salt = 'openlens_salt'
            new_hash = hashlib.sha256((new_password + salt).encode()).hexdigest()
        
        # Update user
        user.password_hash = new_hash
        
        # Invalidate all sessions
        self.invalidate_user_sessions(user_id)
        
        return True
    
    def validate_password(self, password: str) -> Tuple[bool, List[str]]:
        """
        Validate a password against the password policy.
        
        Args:
            password: Password to validate.
            
        Returns:
            Tuple of (is_valid, list of errors).
        """
        errors = []
        
        # Check length
        if len(password) < self.config.password_policy.min_length:
            errors.append(f"Password must be at least {self.config.password_policy.min_length} characters")
        
        if len(password) > self.config.password_policy.max_length:
            errors.append(f"Password must be at most {self.config.password_policy.max_length} characters")
        
        # Check for uppercase
        if self.config.password_policy.require_uppercase and not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check for lowercase
        if self.config.password_policy.require_lowercase and not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check for digit
        if self.config.password_policy.require_digit and not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one digit")
        
        # Check for special character
        if self.config.password_policy.require_special:
            special_chars = set(self.config.password_policy.special_characters)
            if not any(c in special_chars for c in password):
                errors.append("Password must contain at least one special character")
        
        return (len(errors) == 0, errors)
    
    def get_user_sessions(self, user_id: str) -> List[Session]:
        """
        Get all active sessions for a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            List of Session objects.
        """
        with self._lock:
            return [s for s in self._sessions.values() 
                    if s.user_id == user_id and s.expires_at > datetime.utcnow()]
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up.
        """
        with self._lock:
            now = datetime.utcnow()
            expired_sessions = [sid for sid, s in self._sessions.items() if s.expires_at < now]
            expired_tokens = [t for t, tok in self._tokens.items() if tok.expires_at < now]
            
            for sid in expired_sessions:
                session = self._sessions[sid]
                if session.token in self._tokens:
                    del self._tokens[session.token]
                del self._sessions[sid]
            
            for t in expired_tokens:
                del self._tokens[t]
            
            return len(expired_sessions) + len(expired_tokens)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get authentication statistics.
        
        Returns:
            Dictionary with statistics.
        """
        with self._lock:
            return {
                'active_sessions': len([s for s in self._sessions.values() if s.expires_at > datetime.utcnow()]),
                'active_tokens': len([t for t in self._tokens.values() if t.expires_at > datetime.utcnow()]),
                'failed_attempts': sum(a.get('count', 0) for a in self._failed_attempts.values()),
                'locked_users': len([u for u, a in self._failed_attempts.items() 
                                   if a.get('count', 0) >= self.config.password_policy.max_attempts]),
            }


# Global authentication service instance
authentication_service = AuthenticationService()
