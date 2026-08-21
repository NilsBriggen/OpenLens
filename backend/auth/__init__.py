"""
Authentication Module for OpenLens

Provides JWT-based authentication and authorization.

Usage:
    from auth.authentication import AuthManager, auth_required, get_current_user
    from auth.models import User
"""

from .authentication import AuthManager, auth_required, get_current_user, create_access_token, verify_token
from .models import User, Role

__all__ = [
    'AuthManager',
    'auth_required',
    'get_current_user',
    'create_access_token',
    'verify_token',
    'User',
    'Role',
]
