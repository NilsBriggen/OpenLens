"""
Shared auth dependencies for the OpenLens API.

Extracted from security_router (which now imports from here) so every router
uses one authentication and one authorization mechanism.

OPENLENS_REQUIRE_AUTH (default "1"): when "0", get_current_user returns a
synthetic anonymous admin principal and require_permission no-ops. Never
default to open - the flag exists only for local development.
"""

import os
from typing import Any, Dict

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend.security import authentication_service, authorization_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/security/token', auto_error=False)


def auth_required() -> bool:
    """Whether authentication is enforced (OPENLENS_REQUIRE_AUTH, default on)."""
    return os.getenv('OPENLENS_REQUIRE_AUTH', '1') != '0'


_ANONYMOUS = {'user_id': 'anonymous', 'username': 'anonymous', 'expires_at': None}


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Resolve the caller from their bearer token, or reject the request."""
    if not auth_required():
        return dict(_ANONYMOUS)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    validated = authentication_service.validate_token(token)
    if not validated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return {
        'user_id': validated.user_id,
        'username': validated.username,
        'expires_at': validated.expires_at.isoformat() if validated.expires_at else None,
    }


def require_permission(resource: str, action: str):
    """
    Authorization dependency: 403 unless the caller holds action on resource.

    Returns the current user dict, so endpoints can also consume it:
        current_user: dict = require_permission('graph', 'read')
    """
    async def _dep(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if not auth_required():
            return current_user
        if not authorization_service.check_permission(
                current_user['user_id'], resource, action):
            raise HTTPException(status_code=403, detail='Permission denied')
        return current_user

    return Depends(_dep)
