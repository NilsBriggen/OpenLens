"""
Authorization Service for OpenLens

Provides authorization capabilities:
- Permission checking
- Role-based access control
- Resource-level permissions
- Policy evaluation
- Access decision logging
"""

import hashlib
import time
import json
import threading
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class AuthorizationRequest:
    """Represents an authorization request."""
    user_id: str
    resource: str
    action: str
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'user_id': self.user_id,
            'resource': self.resource,
            'action': self.action,
            'context': self.context,
        }


@dataclass
class AuthorizationResult:
    """Result of authorization."""
    allowed: bool
    reason: str = ''
    permissions: List[str] = field(default_factory=list)
    missing_permissions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'allowed': self.allowed,
            'reason': self.reason,
            'permissions': self.permissions,
            'missing_permissions': self.missing_permissions,
        }


@dataclass
class AccessPolicy:
    """Represents an access policy."""
    policy_id: str
    name: str
    description: str = ''
    conditions: Dict[str, Any] = field(default_factory=dict)
    effect: str = 'allow'  # allow, deny
    priority: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'policy_id': self.policy_id,
            'name': self.name,
            'description': self.description,
            'conditions': self.conditions,
            'effect': self.effect,
            'priority': self.priority,
        }
    
    def matches(self, request: AuthorizationRequest) -> bool:
        """Check if this policy matches a request."""
        for key, value in self.conditions.items():
            if key == 'user_id':
                if request.user_id != value:
                    return False
            elif key == 'resource':
                if request.resource != value:
                    return False
            elif key == 'action':
                if request.action != value:
                    return False
            elif key == 'resource_type':
                # Extract resource type from resource
                if ':' in request.resource:
                    resource_type = request.resource.split(':')[0]
                    if resource_type != value:
                        return False
                else:
                    if request.resource != value:
                        return False
            elif key == 'user_role':
                # Check if user has the required role
                # This would require access to the RBAC service
                pass
            elif key.startswith('context.'):
                # Check context field
                context_key = key[8:]  # Remove 'context.' prefix
                if request.context.get(context_key) != value:
                    return False
        
        return True


@dataclass
class AuthorizationConfig:
    """Configuration for authorization service."""
    default_policy: str = 'deny'  # deny, allow
    enable_logging: bool = True
    cache_size: int = 1000
    cache_ttl: int = 300  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'default_policy': self.default_policy,
            'enable_logging': self.enable_logging,
            'cache_size': self.cache_size,
            'cache_ttl': self.cache_ttl,
        }


class AuthorizationService:
    """
    Authorization service for OpenLens.
    
    Provides:
    - Permission checking
    - Role-based access control
    - Resource-level permissions
    - Policy evaluation
    - Access decision logging
    """
    
    def __init__(self, config: AuthorizationConfig = None, 
                 rbac_service=None, audit_logger=None):
        """
        Initialize the authorization service.
        
        Args:
            config: AuthorizationConfig instance.
            rbac_service: RBAC service instance.
            audit_logger: Audit logger instance.
        """
        self.config = config or AuthorizationConfig()
        self.rbac_service = rbac_service
        self.audit_logger = audit_logger
        self._policies: Dict[str, AccessPolicy] = {}
        self._cache: Dict[str, Tuple[AuthorizationResult, datetime]] = {}
        self._lock = threading.Lock()
        
        # Initialize with default policies
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default access policies."""
        # Admin policy (highest priority)
        admin_policy = AccessPolicy(
            policy_id='admin_policy',
            name='Admin Access',
            description='Allow all actions for admin users',
            conditions={'user_role': 'admin'},
            effect='allow',
            priority=100,
        )
        self._policies[admin_policy.policy_id] = admin_policy
        
        # Graph read policy
        graph_read_policy = AccessPolicy(
            policy_id='graph_read_policy',
            name='Graph Read Access',
            description='Allow read access to graph data',
            conditions={'resource': 'graph', 'action': 'read'},
            effect='allow',
            priority=50,
        )
        self._policies[graph_read_policy.policy_id] = graph_read_policy
        
        # Graph write policy
        graph_write_policy = AccessPolicy(
            policy_id='graph_write_policy',
            name='Graph Write Access',
            description='Allow write access to graph data',
            conditions={'resource': 'graph', 'action': 'write'},
            effect='allow',
            priority=50,
        )
        self._policies[graph_write_policy.policy_id] = graph_write_policy
        
        # Scraper execute policy
        scraper_execute_policy = AccessPolicy(
            policy_id='scraper_execute_policy',
            name='Scraper Execute Access',
            description='Allow execution of scraping tasks',
            conditions={'resource': 'scraper', 'action': 'execute'},
            effect='allow',
            priority=50,
        )
        self._policies[scraper_execute_policy.policy_id] = scraper_execute_policy
        
        # AI analyze policy
        ai_analyze_policy = AccessPolicy(
            policy_id='ai_analyze_policy',
            name='AI Analyze Access',
            description='Allow AI analysis operations',
            conditions={'resource': 'ai', 'action': 'analyze'},
            effect='allow',
            priority=50,
        )
        self._policies[ai_analyze_policy.policy_id] = ai_analyze_policy
    
    def authorize(self, request: AuthorizationRequest) -> AuthorizationResult:
        """
        Authorize a request.
        
        Args:
            request: AuthorizationRequest.
            
        Returns:
            AuthorizationResult.
        """
        # Check cache first
        cache_key = self._generate_cache_key(request)
        with self._lock:
            if cache_key in self._cache:
                cached_result, cached_time = self._cache[cache_key]
                if (datetime.utcnow() - cached_time).seconds < self.config.cache_ttl:
                    return cached_result
        
        # Evaluate policies
        result = self._evaluate_policies(request)
        
        # Cache the result
        with self._lock:
            self._cache[cache_key] = (result, datetime.utcnow())
            # Clean up old cache entries
            if len(self._cache) > self.config.cache_size:
                self._cleanup_cache()
        
        # Log the authorization decision
        if self.audit_logger and self.config.enable_logging:
            self.audit_logger.log_authorization(
                user_id=request.user_id,
                username='',  # Would need to look up username
                resource=request.resource,
                action=request.action,
                success=result.allowed,
                error=result.reason if not result.allowed else '',
            )
        
        return result
    
    def _generate_cache_key(self, request: AuthorizationRequest) -> str:
        """Generate a cache key for a request."""
        key_data = f"{request.user_id}:{request.resource}:{request.action}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def _cleanup_cache(self):
        """Clean up old cache entries."""
        now = datetime.utcnow()
        to_remove = [
            key for key, (_, timestamp) in self._cache.items()
            if (now - timestamp).seconds > self.config.cache_ttl
        ]
        
        for key in to_remove:
            del self._cache[key]
    
    def _evaluate_policies(self, request: AuthorizationRequest) -> AuthorizationResult:
        """Evaluate policies for a request."""
        # Sort policies by priority (highest first)
        sorted_policies = sorted(
            self._policies.values(),
            key=lambda p: p.priority,
            reverse=True
        )
        
        # Evaluate each policy
        for policy in sorted_policies:
            if policy.matches(request):
                if policy.effect == 'allow':
                    return AuthorizationResult(
                        allowed=True,
                        reason=f"Allowed by policy: {policy.name}",
                        permissions=[policy.policy_id],
                    )
                elif policy.effect == 'deny':
                    return AuthorizationResult(
                        allowed=False,
                        reason=f"Denied by policy: {policy.name}",
                        permissions=[policy.policy_id],
                    )
        
        # Check RBAC if available
        if self.rbac_service:
            rbac_result = self.rbac_service.check_permission(
                request.user_id, request.resource, request.action
            )
            
            if rbac_result:
                return AuthorizationResult(
                    allowed=True,
                    reason='Allowed by RBAC',
                    permissions=['rbac'],
                )
        
        # Default policy
        if self.config.default_policy == 'allow':
            return AuthorizationResult(
                allowed=True,
                reason='Default allow policy',
                permissions=[],
            )
        else:
            return AuthorizationResult(
                allowed=False,
                reason='Default deny policy',
                permissions=[],
            )
    
    def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """
        Check if a user has permission for a resource and action.
        
        Args:
            user_id: User ID.
            resource: Resource.
            action: Action.
            
        Returns:
            True if permitted.
        """
        request = AuthorizationRequest(
            user_id=user_id,
            resource=resource,
            action=action,
        )
        
        result = self.authorize(request)
        return result.allowed
    
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
        if self.rbac_service:
            return self.rbac_service.check_resource_permission(
                user_id, resource_id, action
            )
        
        # Fall back to regular permission check
        return self.check_permission(user_id, '', action)
    
    def get_user_permissions(self, user_id: str) -> List[str]:
        """
        Get all permissions for a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            List of permission strings.
        """
        if self.rbac_service:
            permissions = self.rbac_service.get_user_permissions(user_id)
            return [f"{p.resource}:{p.action}" for p in permissions]
        
        return []
    
    def add_policy(self, policy: AccessPolicy) -> bool:
        """
        Add an access policy.
        
        Args:
            policy: AccessPolicy to add.
            
        Returns:
            True if added.
        """
        with self._lock:
            if policy.policy_id in self._policies:
                return False
            
            self._policies[policy.policy_id] = policy
            
            # Invalidate cache
            self._cache.clear()
            
            return True
    
    def remove_policy(self, policy_id: str) -> bool:
        """
        Remove an access policy.
        
        Args:
            policy_id: Policy ID.
            
        Returns:
            True if removed.
        """
        with self._lock:
            if policy_id not in self._policies:
                return False
            
            del self._policies[policy_id]
            
            # Invalidate cache
            self._cache.clear()
            
            return True
    
    def get_policy(self, policy_id: str) -> Optional[AccessPolicy]:
        """
        Get an access policy.
        
        Args:
            policy_id: Policy ID.
            
        Returns:
            AccessPolicy or None.
        """
        return self._policies.get(policy_id)
    
    def list_policies(self) -> List[AccessPolicy]:
        """
        List all access policies.
        
        Returns:
            List of AccessPolicy objects.
        """
        return list(self._policies.values())
    
    def create_resource_policy(self, resource_type: str, actions: List[str],
                              effect: str = 'allow', priority: int = 50) -> AccessPolicy:
        """
        Create a policy for a resource type.
        
        Args:
            resource_type: Resource type.
            actions: List of actions.
            effect: Policy effect (allow, deny).
            priority: Policy priority.
            
        Returns:
            AccessPolicy.
        """
        policy_id = f"{resource_type}_policy_{int(time.time())}"
        
        # For simplicity, create a policy for each action
        # In a real implementation, we might create a single policy with multiple conditions
        policies = []
        for action in actions:
            policy = AccessPolicy(
                policy_id=f"{policy_id}_{action}",
                name=f"{resource_type} {action} Access",
                description=f'{effect.capitalize()} {action} access to {resource_type} resources',
                conditions={'resource': resource_type, 'action': action},
                effect=effect,
                priority=priority,
            )
            self.add_policy(policy)
            policies.append(policy)
        
        return policies[0] if policies else None
    
    def create_user_policy(self, user_id: str, resource: str, action: str,
                          effect: str = 'allow', priority: int = 50) -> AccessPolicy:
        """
        Create a policy for a specific user.
        
        Args:
            user_id: User ID.
            resource: Resource.
            action: Action.
            effect: Policy effect (allow, deny).
            priority: Policy priority.
            
        Returns:
            AccessPolicy.
        """
        policy_id = f"user_{user_id}_{resource}_{action}_{int(time.time())}"
        
        policy = AccessPolicy(
            policy_id=policy_id,
            name=f"User {user_id} {action} {resource}",
            description=f'{effect.capitalize()} {user_id} to {action} on {resource}',
            conditions={'user_id': user_id, 'resource': resource, 'action': action},
            effect=effect,
            priority=priority,
        )
        
        self.add_policy(policy)
        return policy
    
    def get_effective_policies(self, user_id: str) -> List[AccessPolicy]:
        """
        Get all policies that apply to a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            List of AccessPolicy objects.
        """
        # In a real implementation, this would consider the user's roles
        # For now, return all policies that match the user_id
        matching_policies = []
        
        for policy in self._policies.values():
            if 'user_id' in policy.conditions and policy.conditions['user_id'] == user_id:
                matching_policies.append(policy)
        
        return matching_policies
    
    def export_to_json(self) -> str:
        """
        Export authorization data to JSON.
        
        Returns:
            JSON string.
        """
        data = {
            'policies': [p.to_dict() for p in self._policies.values()],
            'config': self.config.to_dict(),
        }
        
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: str) -> bool:
        """
        Import authorization data from JSON.
        
        Args:
            json_data: JSON string.
            
        Returns:
            True if imported.
        """
        try:
            data = json.loads(json_data)
            
            # Import policies
            self._policies = {}
            for policy_data in data.get('policies', []):
                policy = AccessPolicy(
                    policy_id=policy_data['policy_id'],
                    name=policy_data['name'],
                    description=policy_data.get('description', ''),
                    conditions=policy_data.get('conditions', {}),
                    effect=policy_data.get('effect', 'allow'),
                    priority=policy_data.get('priority', 0),
                )
                self._policies[policy.policy_id] = policy
            
            # Import config
            config_data = data.get('config', {})
            self.config = AuthorizationConfig(
                default_policy=config_data.get('default_policy', 'deny'),
                enable_logging=config_data.get('enable_logging', True),
                cache_size=config_data.get('cache_size', 1000),
                cache_ttl=config_data.get('cache_ttl', 300),
            )
            
            # Invalidate cache
            self._cache.clear()
            
            return True
        
        except Exception as e:
            print(f"Error importing authorization data: {e}")
            return False


# Global authorization service instance
authorization_service = AuthorizationService()
