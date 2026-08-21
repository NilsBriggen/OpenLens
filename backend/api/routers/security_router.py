"""
Security Router

API endpoints for Enterprise Security (7 modules)
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta

from backend.security import rbac, audit_logger, encryption_service, authentication_service, authorization_service

router = APIRouter()
# Auth plumbing lives in backend/api/deps.py; this router imports it so
# every router shares one mechanism.
from backend.api.deps import auth_required, get_current_user, oauth2_scheme


# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class RoleCreate(BaseModel):
    name: str
    description: Optional[str] = None


class PermissionCreate(BaseModel):
    name: str
    description: Optional[str] = None


class AuditLogRequest(BaseModel):
    event_type: str
    resource: str
    action: str
    details: Optional[Dict[str, Any]] = None


class RefreshRequest(BaseModel):
    refresh_token: str


def _require(current_user: Dict[str, Any], resource: str, action: str) -> None:
    """Raise 403 unless the caller holds `action` on `resource`."""
    if not auth_required():
        return
    if not authorization_service.check_permission(current_user["user_id"], resource, action):
        raise HTTPException(status_code=403, detail="Permission denied")


# Authentication
@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, Any]:
    """Get JWT token"""
    result = authentication_service.authenticate(form_data.username, form_data.password)
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.error or "Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    refresh_token = authentication_service.generate_refresh_token(result.user_id, result.username)

    expires_in = 3600
    if result.expires_at:
        expires_in = max(0, int((result.expires_at - datetime.utcnow()).total_seconds()))

    return {
        "access_token": result.token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": expires_in,
        "user": {"user_id": result.user_id, "username": result.username},
    }


@router.post("/refresh")
async def refresh_access_token(payload: RefreshRequest) -> Dict[str, Any]:
    """Refresh access token"""
    result = authentication_service.refresh_token(payload.refresh_token)
    if not result.success:
        raise HTTPException(status_code=401, detail=result.error or "Invalid refresh token")

    expires_in = 3600
    if result.expires_at:
        expires_in = max(0, int((result.expires_at - datetime.utcnow()).total_seconds()))

    return {
        "access_token": result.token,
        "token_type": "bearer",
        "expires_in": expires_in,
    }


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """Logout and invalidate token"""
    authentication_service.invalidate_token(token)
    return {"status": "logged out"}


# Users
@router.get("/users")
async def list_users(current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    """List all users. Serialised via UserOut so password_hash never leaks."""
    from backend.api.schemas import UserOut
    _require(current_user, "security", "manage")
    return [UserOut.model_validate(u).model_dump(by_alias=True)
            for u in rbac.list_users()]


@router.get("/permissions")
async def list_permissions(current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    """List all permissions"""
    from backend.api.schemas import PermissionOut
    _require(current_user, "security", "manage")
    return [PermissionOut.model_validate(p).model_dump(by_alias=True)
            for p in rbac.list_permissions()]


@router.get("/users/me")
async def read_current_user(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Details of the authenticated caller."""
    user = rbac.get_user(current_user["user_id"])
    if not user:
        return current_user
    return user.to_dict()


@router.post("/users")
async def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Create a new user"""
    _require(current_user, "security", "manage")

    new_user = rbac.create_user(
        username=user.username,
        email=user.email or '',
        password=user.password,
    )
    return new_user.to_dict()


@router.get("/users/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Get user details"""
    _require(current_user, "security", "manage")

    user = rbac.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()


@router.put("/users/{user_id}")
async def update_user(user_id: str, user: UserUpdate, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Update user"""
    _require(current_user, "security", "manage")

    existing = rbac.get_user(user_id)
    if not existing:
        raise HTTPException(status_code=404, detail="User not found")

    changes = user.model_dump(exclude_unset=True)
    if 'email' in changes and changes['email'] is not None:
        existing.email = changes['email']
    if changes.get('password'):
        existing.password_hash = rbac._hash_password(changes['password'])

    return existing.to_dict()


# RBAC
@router.post("/roles")
async def create_role(role: RoleCreate, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Create a new role"""
    _require(current_user, "security", "manage")

    new_role = rbac.create_role(role.name, role.description or '')
    return new_role.to_dict()


@router.get("/roles")
async def list_roles(current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    """List all roles"""
    _require(current_user, "security", "manage")

    return [r.to_dict() for r in rbac.list_roles()]


@router.post("/permissions")
async def create_permission(permission: PermissionCreate, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Create a new permission"""
    _require(current_user, "security", "manage")

    new_permission = rbac.create_permission(permission.name, permission.description or '')
    return new_permission.to_dict()


# Audit Logging
@router.post("/audit")
async def log_audit_event(event: AuditLogRequest, current_user: dict = Depends(get_current_user)) -> Dict[str, str]:
    """Log an audit event"""
    audit_logger.log(
        event_type=event.event_type,
        user_id=current_user.get("user_id", ""),
        username=current_user.get("username", "system"),
        resource=event.resource,
        action=event.action,
        details=event.details,
    )
    return {"status": "logged"}


@router.get("/audit")
async def get_audit_logs(limit: int = 100, current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    """Get audit logs"""
    _require(current_user, "security", "manage")

    return [event.to_dict() for event in audit_logger.get_recent_events(limit)]


# Encryption
@router.post("/encrypt")
async def encrypt_data(data: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Encrypt data"""
    _require(current_user, "security", "manage")

    encrypted = encryption_service.encrypt_symmetric(data)
    return {"encrypted": encrypted.to_dict() if hasattr(encrypted, 'to_dict') else encrypted}


@router.post("/decrypt")
async def decrypt_data(data: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Decrypt data"""
    _require(current_user, "security", "manage")

    decrypted = encryption_service.decrypt_symmetric(data)
    return {"decrypted": decrypted}
