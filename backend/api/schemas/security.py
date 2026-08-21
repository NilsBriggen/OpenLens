"""Security response models. UserOut's explicit field list is the guard that
keeps password_hash off the wire."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, Field

from backend.api.schemas.base import ApiModel


class UserOut(ApiModel):
    """A user account. Never carries the password hash."""
    id: str = Field(validation_alias=AliasChoices('id', 'user_id'))
    username: str
    email: str = ''
    roles: List[str] = []
    is_active: bool = True
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None


class RoleOut(ApiModel):
    """A role."""
    id: str = Field(validation_alias=AliasChoices('id', 'role_id'))
    name: str
    description: str = ''
    permissions: List[str] = []


class PermissionOut(ApiModel):
    """A permission."""
    id: str = Field(validation_alias=AliasChoices('id', 'permission_id'))
    name: str
    description: str = ''
    resource: str = ''
    action: str = ''


class AuditEventOut(ApiModel):
    """One audit-log event."""
    id: str = Field(default='', validation_alias=AliasChoices('id', 'event_id'))
    event_type: str = ''
    severity: str = 'info'
    user_id: str = ''
    username: str = ''
    resource: str = ''
    action: str = ''
    details: Dict[str, Any] = {}
    timestamp: Optional[datetime] = None


class TokenOut(ApiModel):
    """Login/refresh response. Field names are part of the OAuth2 contract
    and must stay snake_case on the wire."""
    model_config = ApiModel.model_config | {'alias_generator': None}

    access_token: str
    refresh_token: str = ''
    token_type: str = 'bearer'
    expires_in: int = 3600
    user: Optional[Dict[str, Any]] = None
