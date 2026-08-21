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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()


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


# Authentication
@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:
    """Get JWT token"""
    user = authentication_service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = authentication_service.create_access_token(user)
    refresh_token = authentication_service.create_refresh_token(user)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 3600
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str) -> Dict[str, str]:
    """Refresh access token"""
    user = authentication_service.verify_refresh_token(refresh_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    new_access_token = authentication_service.create_access_token(user)
    return {"access_token": new_access_token, "token_type": "bearer", "expires_in": 3600}


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """Logout and invalidate token"""
    authentication_service.invalidate_token(token)
    return {"status": "logged out"}


# Users
@router.post("/users")
async def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Create a new user"""
    if not authorization_service.check_permission(current_user, "user", "create"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    new_user = authentication_service.create_user(
        user.username, user.password, user.email, user.full_name
    )
    return new_user.to_dict()


@router.get("/users/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Get user details"""
    if not authorization_service.check_permission(current_user, "user", "read"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    user = authentication_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.to_dict()


@router.put("/users/{user_id}")
async def update_user(user_id: str, user: UserUpdate, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Update user"""
    if not authorization_service.check_permission(current_user, "user", "update"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    updated_user = authentication_service.update_user(user_id, user.dict(exclude_unset=True))
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user.to_dict()


# RBAC
@router.post("/roles")
async def create_role(role: RoleCreate, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Create a new role"""
    if not authorization_service.check_permission(current_user, "role", "create"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    new_role = rbac.create_role(role.name, role.description)
    return new_role.to_dict()


@router.get("/roles")
async def list_roles(current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    """List all roles"""
    if not authorization_service.check_permission(current_user, "role", "read"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    roles = rbac.list_roles()
    return [r.to_dict() for r in roles]


@router.post("/permissions")
async def create_permission(permission: PermissionCreate, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Create a new permission"""
    if not authorization_service.check_permission(current_user, "permission", "create"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    new_permission = rbac.create_permission(permission.name, permission.description)
    return new_permission.to_dict()


# Audit Logging
@router.post("/audit")
async def log_audit_event(event: AuditLogRequest, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Log an audit event"""
    audit_logger.log_event(
        event.event_type,
        current_user.get("username", "system"),
        event.resource,
        event.action,
        event.details
    )
    return {"status": "logged"}


@router.get("/audit")
async def get_audit_logs(limit: int = 100, current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    """Get audit logs"""
    if not authorization_service.check_permission(current_user, "audit", "read"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    logs = audit_logger.get_logs(limit)
    return [log.to_dict() for log in logs]


# Encryption
@router.post("/encrypt")
async def encrypt_data(data: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Encrypt data"""
    if not authorization_service.check_permission(current_user, "encrypt", "use"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    encrypted = encryption_service.encrypt_symmetric(data)
    return {"encrypted": encrypted}


@router.post("/decrypt")
async def decrypt_data(data: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Decrypt data"""
    if not authorization_service.check_permission(current_user, "encrypt", "use"):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    decrypted = encryption_service.decrypt_symmetric(data)
    return {"decrypted": decrypted}


# Helper function
async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Get current user from token"""
    user = authentication_service.verify_access_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user.to_dict()
