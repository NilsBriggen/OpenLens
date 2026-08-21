"""
Role-Based Access Control (RBAC) for OpenLens

Provides fine-grained access control:
- Role management
- Permission management
- User-role assignment
- Resource-level permissions
- Permission inheritance
- Permission checking
"""

import time
import json
import hashlib
import uuid
from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class Permission:
    """Represents a permission."""
    permission_id: str
    name: str
    description: str = ''
    resource: str = ''  # Resource type (e.g., 'graph', 'scraper', 'ai')
    action: str = ''  # Action (e.g., 'read', 'write', 'delete', 'execute')
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'permission_id': self.permission_id,
            'name': self.name,
            'description': self.description,
            'resource': self.resource,
            'action': self.action,
            'created_at': self.created_at.isoformat(),
        }
    
    def matches(self, resource: str, action: str) -> bool:
        """Check if this permission matches a resource and action."""
        # Wildcard matching. Each wildcard only widens its own axis: with the
        # old `or`, a permission scoped to one resource with action '*'
        # granted every resource in the system.
        resource_ok = self.resource == '*' or self.resource == resource
        action_ok = self.action == '*' or self.action == action
        if resource_ok and action_ok:
            return True
        
        if self.resource == resource and self.action == action:
            return True
        
        # Resource wildcard (e.g., 'graph:*')
        if self.resource.endswith(':*') and resource.startswith(self.resource[:-2]):
            return self.action == action
        
        # Action wildcard (e.g., 'graph:read:*')
        if ':' in self.resource:
            resource_parts = self.resource.split(':')
            if len(resource_parts) >= 2 and resource_parts[-1] == '*':
                if resource.startswith(':'.join(resource_parts[:-1]) + ':'):
                    return self.action == action
        
        return False


@dataclass
class Role:
    """Represents a role."""
    role_id: str
    name: str
    description: str = ''
    permissions: List[str] = field(default_factory=list)  # List of permission IDs
    parent_roles: List[str] = field(default_factory=list)  # List of parent role IDs
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'role_id': self.role_id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions,
            'parent_roles': self.parent_roles,
            'created_at': self.created_at.isoformat(),
        }
    
    def has_permission(self, permission_id: str, permission_map: Dict[str, Permission]) -> bool:
        """Check if this role has a specific permission."""
        # Check direct permissions
        if permission_id in self.permissions:
            return True
        
        # Check parent roles
        for parent_role_id in self.parent_roles:
            # In a real implementation, we would look up the parent role
            # For now, assume we have a role map
            pass
        
        return False


@dataclass
class User:
    """Represents a user."""
    user_id: str
    username: str
    email: str = ''
    password_hash: str = ''
    roles: List[str] = field(default_factory=list)  # List of role IDs
    is_active: bool = True
    last_login: datetime = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'roles': self.roles,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
        }
    
    def has_role(self, role_id: str) -> bool:
        """Check if user has a specific role."""
        return role_id in self.roles


@dataclass
class Resource:
    """Represents a resource."""
    resource_id: str
    type: str  # Resource type (e.g., 'graph', 'scraper', 'ai')
    name: str
    owner_id: str = ''  # User ID of the owner
    permissions: Dict[str, Set[str]] = field(default_factory=dict)  # {role_id: {action1, action2}}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'resource_id': self.resource_id,
            'type': self.type,
            'name': self.name,
            'owner_id': self.owner_id,
            'permissions': {k: list(v) for k, v in self.permissions.items()},
        }


class RBAC:
    """
    Role-Based Access Control system for OpenLens.
    
    Provides:
    - Role management
    - Permission management
    - User management
    - Access control checking
    - Resource-level permissions
    """
    
    def __init__(self):
        """Initialize the RBAC system."""
        self._permissions: Dict[str, Permission] = {}
        self._roles: Dict[str, Role] = {}
        self._users: Dict[str, User] = {}
        self._resources: Dict[str, Resource] = {}
        self._role_permission_cache: Dict[str, Set[str]] = {}
        self._user_permission_cache: Dict[str, Set[str]] = {}
        
        # Initialize with default roles and permissions
        self._initialize_defaults()
    
    def _initialize_defaults(self):
        """Initialize default roles and permissions."""
        # Create default permissions
        default_permissions = [
            Permission(
                permission_id='graph:read',
                name='Read Graph',
                description='Read access to graph data',
                resource='graph',
                action='read',
            ),
            Permission(
                permission_id='graph:write',
                name='Write Graph',
                description='Write access to graph data',
                resource='graph',
                action='write',
            ),
            Permission(
                permission_id='graph:delete',
                name='Delete Graph',
                description='Delete access to graph data',
                resource='graph',
                action='delete',
            ),
            Permission(
                permission_id='scraper:execute',
                name='Execute Scraper',
                description='Execute scraping tasks',
                resource='scraper',
                action='execute',
            ),
            Permission(
                permission_id='scraper:configure',
                name='Configure Scraper',
                description='Configure scraping settings',
                resource='scraper',
                action='configure',
            ),
            Permission(
                permission_id='ai:analyze',
                name='Run AI Analysis',
                description='Run AI/ML analysis',
                resource='ai',
                action='analyze',
            ),
            Permission(
                permission_id='ai:train',
                name='Train AI Models',
                description='Train AI/ML models',
                resource='ai',
                action='train',
            ),
            Permission(
                permission_id='security:manage',
                name='Manage Security',
                description='Manage security settings',
                resource='security',
                action='manage',
            ),
            Permission(
                permission_id='scraper:read',
                name='Read Scraper',
                description='Read access to scraping jobs and settings',
                resource='scraper',
                action='read',
            ),
            Permission(
                permission_id='threat:read',
                name='Read Threat Intelligence',
                description='Read access to threat feeds, IOCs and alerts',
                resource='threat',
                action='read',
            ),
            Permission(
                permission_id='threat:write',
                name='Write Threat Intelligence',
                description='Create and modify threat feeds, IOCs and alerts',
                resource='threat',
                action='write',
            ),
            Permission(
                permission_id='system:read',
                name='Read System',
                description='Read access to system status and configuration',
                resource='system',
                action='read',
            ),
            Permission(
                permission_id='admin:all',
                name='Admin Access',
                description='Full access to all resources',
                resource='*',
                action='*',
            ),
        ]
        
        for perm in default_permissions:
            self._permissions[perm.permission_id] = perm
        
        # Create default roles
        default_roles = [
            Role(
                role_id='viewer',
                name='Viewer',
                description='Read-only access to data',
                permissions=['graph:read', 'threat:read', 'system:read',
                             'scraper:read'],
            ),
            Role(
                role_id='analyst',
                name='Analyst',
                description='Access to analysis tools',
                permissions=['graph:read', 'graph:write', 'ai:analyze',
                             'threat:read', 'threat:write', 'system:read',
                             'scraper:read'],
            ),
            Role(
                role_id='scraper',
                name='Scraper',
                description='Access to scraping tools',
                permissions=['scraper:execute', 'scraper:configure'],
            ),
            Role(
                role_id='admin',
                name='Administrator',
                description='Full access to all features',
                permissions=['admin:all'],
            ),
        ]
        
        for role in default_roles:
            self._roles[role.role_id] = role
        
        # Create default admin user
        admin_user = User(
            user_id='admin',
            username='admin',
            email='admin@openlens.com',
            password_hash=self._hash_password('admin123'),
            roles=['admin'],
        )
        self._users[admin_user.user_id] = admin_user
    
    def _hash_password(self, password: str) -> str:
        """Hash a password."""
        salt = 'openlens_salt'  # In production, use a random salt per user
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def create_permission(self, name: str, description: str = '', 
                        resource: str = '', action: str = '') -> Permission:
        """
        Create a new permission.
        
        Args:
            name: Permission name.
            description: Permission description.
            resource: Resource type.
            action: Action.
            
        Returns:
            Permission object.
        """
        permission_id = f"{resource}:{action}" if resource and action else str(uuid.uuid4())
        
        permission = Permission(
            permission_id=permission_id,
            name=name,
            description=description,
            resource=resource,
            action=action,
        )
        
        self._permissions[permission_id] = permission
        
        # Invalidate caches
        self._role_permission_cache.clear()
        self._user_permission_cache.clear()
        
        return permission
    
    def get_permission(self, permission_id: str) -> Optional[Permission]:
        """
        Get a permission by ID.
        
        Args:
            permission_id: Permission ID.
            
        Returns:
            Permission or None.
        """
        return self._permissions.get(permission_id)
    
    def list_permissions(self) -> List[Permission]:
        """
        List all permissions.
        
        Returns:
            List of Permission objects.
        """
        return list(self._permissions.values())
    
    def delete_permission(self, permission_id: str) -> bool:
        """
        Delete a permission.
        
        Args:
            permission_id: Permission ID.
            
        Returns:
            True if deleted.
        """
        if permission_id in self._permissions:
            del self._permissions[permission_id]
            
            # Remove from roles
            for role in self._roles.values():
                if permission_id in role.permissions:
                    role.permissions.remove(permission_id)
            
            # Invalidate caches
            self._role_permission_cache.clear()
            self._user_permission_cache.clear()
            
            return True
        
        return False
    
    def create_role(self, name: str, description: str = '', 
                   permissions: List[str] = None, 
                   parent_roles: List[str] = None) -> Role:
        """
        Create a new role.
        
        Args:
            name: Role name.
            description: Role description.
            permissions: List of permission IDs.
            parent_roles: List of parent role IDs.
            
        Returns:
            Role object.
        """
        role_id = name.lower().replace(' ', '_')
        
        role = Role(
            role_id=role_id,
            name=name,
            description=description,
            permissions=permissions or [],
            parent_roles=parent_roles or [],
        )
        
        self._roles[role_id] = role
        
        # Invalidate caches
        self._role_permission_cache.clear()
        self._user_permission_cache.clear()
        
        return role
    
    def get_role(self, role_id: str) -> Optional[Role]:
        """
        Get a role by ID.
        
        Args:
            role_id: Role ID.
            
        Returns:
            Role or None.
        """
        return self._roles.get(role_id)
    
    def list_roles(self) -> List[Role]:
        """
        List all roles.
        
        Returns:
            List of Role objects.
        """
        return list(self._roles.values())
    
    def delete_role(self, role_id: str) -> bool:
        """
        Delete a role.
        
        Args:
            role_id: Role ID.
            
        Returns:
            True if deleted.
        """
        if role_id in self._roles:
            # Remove from users
            for user in self._users.values():
                if role_id in user.roles:
                    user.roles.remove(role_id)
            
            del self._roles[role_id]
            
            # Invalidate caches
            self._role_permission_cache.clear()
            self._user_permission_cache.clear()
            
            return True
        
        return False
    
    def create_user(self, username: str, email: str = '', 
                   password: str = '', roles: List[str] = None) -> User:
        """
        Create a new user.
        
        Args:
            username: Username.
            email: Email address.
            password: Password.
            roles: List of role IDs.
            
        Returns:
            User object.
        """
        user_id = str(uuid.uuid4())
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=self._hash_password(password) if password else '',
            roles=roles or [],
        )
        
        self._users[user_id] = user
        
        # Invalidate caches
        self._user_permission_cache.clear()
        
        return user
    
    def get_user(self, user_id: str) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: User ID.
            
        Returns:
            User or None.
        """
        return self._users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: Username.
            
        Returns:
            User or None.
        """
        for user in self._users.values():
            if user.username == username:
                return user
        return None
    
    def list_users(self) -> List[User]:
        """
        List all users.
        
        Returns:
            List of User objects.
        """
        return list(self._users.values())
    
    def delete_user(self, user_id: str) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            True if deleted.
        """
        if user_id in self._users:
            del self._users[user_id]
            
            # Invalidate caches
            self._user_permission_cache.clear()
            
            return True
        
        return False
    
    def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """
        Assign a role to a user.
        
        Args:
            user_id: User ID.
            role_id: Role ID.
            
        Returns:
            True if assigned.
        """
        if user_id in self._users and role_id in self._roles:
            user = self._users[user_id]
            if role_id not in user.roles:
                user.roles.append(role_id)
            
            # Invalidate caches
            self._user_permission_cache.pop(user_id, None)
            
            return True
        
        return False
    
    def remove_role_from_user(self, user_id: str, role_id: str) -> bool:
        """
        Remove a role from a user.
        
        Args:
            user_id: User ID.
            role_id: Role ID.
            
        Returns:
            True if removed.
        """
        if user_id in self._users:
            user = self._users[user_id]
            if role_id in user.roles:
                user.roles.remove(role_id)
            
            # Invalidate caches
            self._user_permission_cache.pop(user_id, None)
            
            return True
        
        return False
    
    def add_permission_to_role(self, role_id: str, permission_id: str) -> bool:
        """
        Add a permission to a role.
        
        Args:
            role_id: Role ID.
            permission_id: Permission ID.
            
        Returns:
            True if added.
        """
        if role_id in self._roles and permission_id in self._permissions:
            role = self._roles[role_id]
            if permission_id not in role.permissions:
                role.permissions.append(permission_id)
            
            # Invalidate caches
            self._role_permission_cache.pop(role_id, None)
            self._user_permission_cache.clear()
            
            return True
        
        return False
    
    def remove_permission_from_role(self, role_id: str, permission_id: str) -> bool:
        """
        Remove a permission from a role.
        
        Args:
            role_id: Role ID.
            permission_id: Permission ID.
            
        Returns:
            True if removed.
        """
        if role_id in self._roles:
            role = self._roles[role_id]
            if permission_id in role.permissions:
                role.permissions.remove(permission_id)
            
            # Invalidate caches
            self._role_permission_cache.pop(role_id, None)
            self._user_permission_cache.clear()
            
            return True
        
        return False
    
    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """
        Check if a user has permission for a resource and action.
        
        Args:
            user_id: User ID.
            resource: Resource type.
            action: Action.
            
        Returns:
            True if permitted.
        """
        # Check cache first
        if user_id in self._user_permission_cache:
            user_permissions = self._user_permission_cache[user_id]
            for perm_id in user_permissions:
                perm = self._permissions.get(perm_id)
                if perm and perm.matches(resource, action):
                    return True
            return False
        
        # Get user
        user = self._users.get(user_id)
        if not user:
            return False
        
        # Get all permissions for user
        user_permissions = self._get_user_permissions(user)
        self._user_permission_cache[user_id] = user_permissions
        
        # Check permissions
        for perm_id in user_permissions:
            perm = self._permissions.get(perm_id)
            if perm and perm.matches(resource, action):
                return True
        
        return False
    
    def _get_user_permissions(self, user: User) -> Set[str]:
        """Get all permissions for a user."""
        permissions = set()
        
        for role_id in user.roles:
            role = self._roles.get(role_id)
            if role:
                permissions.update(self._get_role_permissions(role))
        
        return permissions
    
    def _get_role_permissions(self, role: Role) -> Set[str]:
        """Get all permissions for a role (including parent roles)."""
        # Check cache first
        if role.role_id in self._role_permission_cache:
            return self._role_permission_cache[role.role_id]
        
        permissions = set(role.permissions)
        
        # Add permissions from parent roles
        for parent_role_id in role.parent_roles:
            parent_role = self._roles.get(parent_role_id)
            if parent_role:
                permissions.update(self._get_role_permissions(parent_role))
        
        # Cache the result
        self._role_permission_cache[role.role_id] = permissions
        
        return permissions
    
    def check_resource_permission(self, user_id: str, resource_id: str, 
                                action: str) -> bool:
        """
        Check if a user has permission for a specific resource.
        
        Args:
            user_id: User ID.
            resource_id: Resource ID.
            action: Action.
            
        Returns:
            True if permitted.
        """
        # First check global permissions
        if self.check_permission(user_id, '', action):
            return True
        
        # Check resource-specific permissions
        resource = self._resources.get(resource_id)
        if not resource:
            return False
        
        # Check if user is owner
        user = self._users.get(user_id)
        if user and user.user_id == resource.owner_id:
            return True
        
        # Check resource permissions
        for role_id, actions in resource.permissions.items():
            if user and role_id in user.roles and action in actions:
                return True
        
        return False
    
    def create_resource(self, resource_type: str, name: str, 
                       owner_id: str) -> Resource:
        """
        Create a new resource.
        
        Args:
            resource_type: Resource type.
            name: Resource name.
            owner_id: Owner user ID.
            
        Returns:
            Resource object.
        """
        resource_id = str(uuid.uuid4())
        
        resource = Resource(
            resource_id=resource_id,
            type=resource_type,
            name=name,
            owner_id=owner_id,
        )
        
        self._resources[resource_id] = resource
        
        return resource
    
    def get_resource(self, resource_id: str) -> Optional[Resource]:
        """
        Get a resource by ID.
        
        Args:
            resource_id: Resource ID.
            
        Returns:
            Resource or None.
        """
        return self._resources.get(resource_id)
    
    def set_resource_permission(self, resource_id: str, role_id: str, 
                               actions: List[str]) -> bool:
        """
        Set permissions for a role on a resource.
        
        Args:
            resource_id: Resource ID.
            role_id: Role ID.
            actions: List of actions.
            
        Returns:
            True if set.
        """
        if resource_id in self._resources:
            resource = self._resources[resource_id]
            resource.permissions[role_id] = set(actions)
            return True
        
        return False
    
    def get_user_permissions(self, user_id: str) -> List[Permission]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            List of Permission objects.
        """
        user = self._users.get(user_id)
        if not user:
            return []
        
        user_permissions = self._get_user_permissions(user)
        
        return [self._permissions[perm_id] for perm_id in user_permissions 
                if perm_id in self._permissions]
    
    def get_role_permissions(self, role_id: str) -> List[Permission]:
        """
        Get all permissions for a role.
        
        Args:
            role_id: Role ID.
            
        Returns:
            List of Permission objects.
        """
        role = self._roles.get(role_id)
        if not role:
            return []
        
        role_permissions = self._get_role_permissions(role)
        
        return [self._permissions[perm_id] for perm_id in role_permissions 
                if perm_id in self._permissions]
    
    def export_to_json(self) -> str:
        """
        Export RBAC data to JSON.
        
        Returns:
            JSON string.
        """
        data = {
            'permissions': [p.to_dict() for p in self._permissions.values()],
            'roles': [r.to_dict() for r in self._roles.values()],
            'users': [u.to_dict() for u in self._users.values()],
            'resources': [r.to_dict() for r in self._resources.values()],
        }
        
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: str) -> bool:
        """
        Import RBAC data from JSON.
        
        Args:
            json_data: JSON string.
            
        Returns:
            True if imported.
        """
        try:
            data = json.loads(json_data)
            
            # Import permissions
            self._permissions = {}
            for perm_data in data.get('permissions', []):
                perm = Permission(
                    permission_id=perm_data['permission_id'],
                    name=perm_data['name'],
                    description=perm_data.get('description', ''),
                    resource=perm_data.get('resource', ''),
                    action=perm_data.get('action', ''),
                    created_at=datetime.fromisoformat(perm_data['created_at']),
                )
                self._permissions[perm.permission_id] = perm
            
            # Import roles
            self._roles = {}
            for role_data in data.get('roles', []):
                role = Role(
                    role_id=role_data['role_id'],
                    name=role_data['name'],
                    description=role_data.get('description', ''),
                    permissions=role_data.get('permissions', []),
                    parent_roles=role_data.get('parent_roles', []),
                    created_at=datetime.fromisoformat(role_data['created_at']),
                )
                self._roles[role.role_id] = role
            
            # Import users
            self._users = {}
            for user_data in data.get('users', []):
                user = User(
                    user_id=user_data['user_id'],
                    username=user_data['username'],
                    email=user_data.get('email', ''),
                    password_hash=user_data.get('password_hash', ''),
                    roles=user_data.get('roles', []),
                    is_active=user_data.get('is_active', True),
                    last_login=datetime.fromisoformat(user_data['last_login']) if user_data.get('last_login') else None,
                    created_at=datetime.fromisoformat(user_data['created_at']),
                )
                self._users[user.user_id] = user
            
            # Import resources
            self._resources = {}
            for resource_data in data.get('resources', []):
                resource = Resource(
                    resource_id=resource_data['resource_id'],
                    type=resource_data['type'],
                    name=resource_data['name'],
                    owner_id=resource_data.get('owner_id', ''),
                    permissions={k: set(v) for k, v in resource_data.get('permissions', {}).items()},
                )
                self._resources[resource.resource_id] = resource
            
            # Invalidate caches
            self._role_permission_cache.clear()
            self._user_permission_cache.clear()
            
            return True
        
        except Exception as e:
            print(f"Error importing RBAC data: {e}")
            return False


# Global RBAC instance
rbac = RBAC()
