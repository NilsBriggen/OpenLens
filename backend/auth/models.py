"""
User and Role Models for Authentication

Provides SQLAlchemy models for user authentication and authorization.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import enum
import secrets

# SQLAlchemy base (import from database to avoid circular imports)
Base = declarative_base()


class RoleType(enum.Enum):
    """User role types."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(Base):
    """
    User model for authentication.
    """
    __tablename__ = 'auth_users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(RoleType), default=RoleType.USER)
    
    # Password reset fields
    password_reset_token = Column(String(255))
    password_reset_token_expires = Column(DateTime)
    
    # Preferences
    preferences = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    # API Keys (for programmatic access)
    api_keys = relationship('APIKey', back_populates='user')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password: str):
        """
        Set user password (hashed).
        
        Args:
            password: Plain text password.
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password: str) -> bool:
        """
        Check if password matches.
        
        Args:
            password: Plain text password to check.
            
        Returns:
            True if password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)
    
    def has_role(self, role: RoleType) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            role: Role to check.
            
        Returns:
            True if user has the role, False otherwise.
        """
        return self.role == role
    
    def is_admin(self) -> bool:
        """Check if user is an admin."""
        return self.role == RoleType.ADMIN
    
    def generate_password_reset_token(self) -> str:
        """
        Generate a password reset token.
        
        Returns:
            Reset token string.
        """
        token = secrets.token_urlsafe(32)
        self.password_reset_token = generate_password_hash(token)
        self.password_reset_token_expires = datetime.utcnow() + timedelta(hours=24)
        return token
    
    def verify_password_reset_token(self, token: str) -> bool:
        """
        Verify a password reset token.
        
        Args:
            token: Token to verify.
            
        Returns:
            True if token is valid and not expired, False otherwise.
        """
        if not self.password_reset_token or not self.password_reset_token_expires:
            return False
        
        if datetime.utcnow() > self.password_reset_token_expires:
            # Token expired, clear it
            self.password_reset_token = None
            self.password_reset_token_expires = None
            return False
        
        return check_password_hash(self.password_reset_token, token)
    
    def clear_password_reset_token(self):
        """Clear the password reset token."""
        self.password_reset_token = None
        self.password_reset_token_expires = None
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (safe for JSON serialization)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role.value,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }


class APIKey(Base):
    """
    API Key model for programmatic access.
    """
    __tablename__ = 'api_keys'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    key_hash = Column(String(255), unique=True, nullable=False, index=True)  # Store hashed key only
    key_prefix = Column(String(10))  # First 10 chars of the key for display purposes
    name = Column(String(100))
    permissions = Column(JSON, default=['read'])
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=100)  # Requests per minute
    last_used = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    rotated_at = Column(DateTime)  # When the key was last rotated
    rotation_count = Column(Integer, default=0)  # Number of times the key has been rotated
    
    # Relationships
    user = relationship('User', back_populates='api_keys')
    
    def __repr__(self):
        return f'<APIKey {self.name} ({self.key_prefix}...)>'
    
    def is_expired(self) -> bool:
        """Check if API key is expired."""
        return self.expires_at and self.expires_at < datetime.utcnow()
    
    def can_access(self, permission: str) -> bool:
        """
        Check if API key has a specific permission.
        
        Args:
            permission: Permission to check.
            
        Returns:
            True if has permission, False otherwise.
        """
        return permission in self.permissions
    
    def needs_rotation(self, max_age_days: int = 90) -> bool:
        """
        Check if API key should be rotated based on age.
        
        Args:
            max_age_days: Maximum age in days before rotation is recommended.
            
        Returns:
            True if key should be rotated, False otherwise.
        """
        if not self.created_at:
            return False
        age = datetime.utcnow() - self.created_at
        return age.days >= max_age_days
    
    def to_dict(self) -> dict:
        """Convert API key to dictionary (safe for JSON serialization)."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'key_prefix': self.key_prefix,
            'permissions': self.permissions,
            'is_active': self.is_active,
            'rate_limit': self.rate_limit,
            'last_used': self.last_used.isoformat() if self.last_used else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'rotated_at': self.rotated_at.isoformat() if self.rotated_at else None,
            'rotation_count': self.rotation_count,
        }


class RefreshToken(Base):
    """
    Refresh Token model for JWT refresh tokens.
    """
    __tablename__ = 'refresh_tokens'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_revoked = Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<RefreshToken {self.id}>'
    
    def is_expired(self) -> bool:
        """Check if refresh token is expired."""
        return self.expires_at < datetime.utcnow()
    
    def is_valid(self) -> bool:
        """Check if refresh token is valid (not expired and not revoked)."""
        return not self.is_expired() and not self.is_revoked


# Import timedelta for password reset
from datetime import timedelta
