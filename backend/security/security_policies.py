"""
Security Policy Manager for OpenLens

Provides security policy management:
- Policy definition
- Policy evaluation
- Policy enforcement
- Policy monitoring
- Policy compliance checking
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class SecurityPolicy:
    """Represents a security policy."""
    policy_id: str
    name: str
    description: str = ''
    category: str = ''  # authentication, authorization, data, network, etc.
    rules: List[Dict[str, Any]] = field(default_factory=list)
    severity: str = 'medium'  # low, medium, high, critical
    is_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'policy_id': self.policy_id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'rules': self.rules,
            'severity': self.severity,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    def evaluate(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Evaluate the policy against a context.
        
        Args:
            context: Context to evaluate.
            
        Returns:
            Tuple of (is_compliant, list of violations).
        """
        violations = []
        
        for rule in self.rules:
            if not self._evaluate_rule(rule, context):
                violations.append(rule.get('description', f"Rule {rule.get('rule_id', 'unknown')}"))
        
        return (len(violations) == 0, violations)
    
    def _evaluate_rule(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a single rule."""
        rule_type = rule.get('type', 'condition')
        
        if rule_type == 'condition':
            return self._evaluate_condition(rule, context)
        elif rule_type == 'requirement':
            return self._evaluate_requirement(rule, context)
        elif rule_type == 'prohibition':
            return not self._evaluate_condition(rule, context)
        else:
            return True
    
    def _evaluate_condition(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a condition rule."""
        field = rule.get('field')
        operator = rule.get('operator', '==')
        value = rule.get('value')
        
        if field not in context:
            return False
        
        context_value = context[field]
        
        if operator == '==':
            return context_value == value
        elif operator == '!=':
            return context_value != value
        elif operator == '>':
            return context_value > value
        elif operator == '<':
            return context_value < value
        elif operator == '>=':
            return context_value >= value
        elif operator == '<=':
            return context_value <= value
        elif operator == 'in':
            return context_value in value
        elif operator == 'not in':
            return context_value not in value
        elif operator == 'contains':
            return value in context_value
        elif operator == 'starts_with':
            return str(context_value).startswith(str(value))
        elif operator == 'ends_with':
            return str(context_value).endswith(str(value))
        elif operator == 'regex':
            import re
            pattern = re.compile(value)
            return bool(pattern.match(str(context_value)))
        else:
            return False
    
    def _evaluate_requirement(self, rule: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a requirement rule."""
        # Requirement rules are similar to conditions but with different semantics
        return self._evaluate_condition(rule, context)


@dataclass
class PolicyEvaluationResult:
    """Result of policy evaluation."""
    policy_id: str
    policy_name: str
    is_compliant: bool
    violations: List[str] = field(default_factory=list)
    severity: str = 'medium'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'policy_id': self.policy_id,
            'policy_name': self.policy_name,
            'is_compliant': self.is_compliant,
            'violations': self.violations,
            'severity': self.severity,
        }


@dataclass
class SecurityPolicyConfig:
    """Configuration for security policy manager."""
    policy_dir: str = '/etc/openlens/policies'
    auto_reload: bool = True
    reload_interval: int = 300  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'policy_dir': self.policy_dir,
            'auto_reload': self.auto_reload,
            'reload_interval': self.reload_interval,
        }


class SecurityPolicyManager:
    """
    Security policy manager for OpenLens.
    
    Provides:
    - Policy definition
    - Policy evaluation
    - Policy enforcement
    - Policy monitoring
    - Policy compliance checking
    """
    
    def __init__(self, config: SecurityPolicyConfig = None):
        """
        Initialize the security policy manager.
        
        Args:
            config: SecurityPolicyConfig instance.
        """
        self.config = config or SecurityPolicyConfig()
        self._policies: Dict[str, SecurityPolicy] = {}
        self._lock = threading.Lock()
        self._last_reload = 0
        
        # Initialize with default policies
        self._initialize_default_policies()
    
    def _initialize_default_policies(self):
        """Initialize default security policies."""
        # Password policy
        password_policy = SecurityPolicy(
            policy_id='password_policy',
            name='Password Policy',
            description='Enforces strong password requirements',
            category='authentication',
            severity='high',
            rules=[
                {
                    'rule_id': 'password_min_length',
                    'type': 'requirement',
                    'field': 'password_length',
                    'operator': '>=',
                    'value': 8,
                    'description': 'Password must be at least 8 characters',
                },
                {
                    'rule_id': 'password_max_length',
                    'type': 'requirement',
                    'field': 'password_length',
                    'operator': '<=',
                    'value': 64,
                    'description': 'Password must be at most 64 characters',
                },
                {
                    'rule_id': 'password_uppercase',
                    'type': 'requirement',
                    'field': 'has_uppercase',
                    'operator': '==',
                    'value': True,
                    'description': 'Password must contain at least one uppercase letter',
                },
                {
                    'rule_id': 'password_lowercase',
                    'type': 'requirement',
                    'field': 'has_lowercase',
                    'operator': '==',
                    'value': True,
                    'description': 'Password must contain at least one lowercase letter',
                },
                {
                    'rule_id': 'password_digit',
                    'type': 'requirement',
                    'field': 'has_digit',
                    'operator': '==',
                    'value': True,
                    'description': 'Password must contain at least one digit',
                },
            ],
        )
        self._policies[password_policy.policy_id] = password_policy
        
        # Session policy
        session_policy = SecurityPolicy(
            policy_id='session_policy',
            name='Session Policy',
            description='Enforces session security requirements',
            category='authentication',
            severity='medium',
            rules=[
                {
                    'rule_id': 'session_timeout',
                    'type': 'requirement',
                    'field': 'session_timeout',
                    'operator': '<=',
                    'value': 3600,  # 1 hour
                    'description': 'Session timeout must be at most 1 hour',
                },
                {
                    'rule_id': 'session_inactivity',
                    'type': 'requirement',
                    'field': 'inactivity_timeout',
                    'operator': '<=',
                    'value': 1800,  # 30 minutes
                    'description': 'Inactivity timeout must be at most 30 minutes',
                },
            ],
        )
        self._policies[session_policy.policy_id] = session_policy
        
        # Data encryption policy
        encryption_policy = SecurityPolicy(
            policy_id='encryption_policy',
            name='Data Encryption Policy',
            description='Requires encryption for sensitive data',
            category='data',
            severity='high',
            rules=[
                {
                    'rule_id': 'encrypt_sensitive_data',
                    'type': 'requirement',
                    'field': 'data_type',
                    'operator': 'not in',
                    'value': ['public', 'non-sensitive'],
                    'description': 'Sensitive data must be encrypted',
                },
                {
                    'rule_id': 'encryption_algorithm',
                    'type': 'requirement',
                    'field': 'encryption_algorithm',
                    'operator': 'in',
                    'value': ['AES-256', 'RSA-2048', 'RSA-4096'],
                    'description': 'Encryption must use approved algorithms',
                },
            ],
        )
        self._policies[encryption_policy.policy_id] = encryption_policy
        
        # Access control policy
        access_policy = SecurityPolicy(
            policy_id='access_policy',
            name='Access Control Policy',
            description='Enforces access control requirements',
            category='authorization',
            severity='high',
            rules=[
                {
                    'rule_id': 'least_privilege',
                    'type': 'requirement',
                    'field': 'access_level',
                    'operator': '==',
                    'value': 'minimum',
                    'description': 'Users must have least privilege access',
                },
                {
                    'rule_id': 'separation_of_duties',
                    'type': 'requirement',
                    'field': 'has_separation',
                    'operator': '==',
                    'value': True,
                    'description': 'Sensitive operations require separation of duties',
                },
            ],
        )
        self._policies[access_policy.policy_id] = access_policy
        
        # Network security policy
        network_policy = SecurityPolicy(
            policy_id='network_policy',
            name='Network Security Policy',
            description='Enforces network security requirements',
            category='network',
            severity='medium',
            rules=[
                {
                    'rule_id': 'use_https',
                    'type': 'requirement',
                    'field': 'protocol',
                    'operator': '==',
                    'value': 'https',
                    'description': 'All communications must use HTTPS',
                },
                {
                    'rule_id': 'rate_limiting',
                    'type': 'requirement',
                    'field': 'rate_limit_enabled',
                    'operator': '==',
                    'value': True,
                    'description': 'Rate limiting must be enabled',
                },
            ],
        )
        self._policies[network_policy.policy_id] = network_policy
    
    def add_policy(self, policy: SecurityPolicy) -> bool:
        """
        Add a security policy.
        
        Args:
            policy: SecurityPolicy to add.
            
        Returns:
            True if added.
        """
        with self._lock:
            if policy.policy_id in self._policies:
                return False
            
            self._policies[policy.policy_id] = policy
            return True
    
    def remove_policy(self, policy_id: str) -> bool:
        """
        Remove a security policy.
        
        Args:
            policy_id: Policy ID.
            
        Returns:
            True if removed.
        """
        with self._lock:
            if policy_id not in self._policies:
                return False
            
            del self._policies[policy_id]
            return True
    
    def get_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        """
        Get a security policy.
        
        Args:
            policy_id: Policy ID.
            
        Returns:
            SecurityPolicy or None.
        """
        return self._policies.get(policy_id)
    
    def list_policies(self, category: str = None) -> List[SecurityPolicy]:
        """
        List all security policies.
        
        Args:
            category: Filter by category (None for all).
            
        Returns:
            List of SecurityPolicy objects.
        """
        with self._lock:
            if category:
                return [p for p in self._policies.values() if p.category == category]
            return list(self._policies.values())
    
    def evaluate_policy(self, policy_id: str, context: Dict[str, Any]) -> PolicyEvaluationResult:
        """
        Evaluate a specific policy.
        
        Args:
            policy_id: Policy ID.
            context: Context to evaluate.
            
        Returns:
            PolicyEvaluationResult.
        """
        policy = self.get_policy(policy_id)
        
        if not policy:
            return PolicyEvaluationResult(
                policy_id=policy_id,
                policy_name='Unknown',
                is_compliant=False,
                violations=[f"Policy {policy_id} not found"],
                severity='high',
            )
        
        is_compliant, violations = policy.evaluate(context)
        
        return PolicyEvaluationResult(
            policy_id=policy.policy_id,
            policy_name=policy.name,
            is_compliant=is_compliant,
            violations=violations,
            severity=policy.severity,
        )
    
    def evaluate_all_policies(self, context: Dict[str, Any]) -> List[PolicyEvaluationResult]:
        """
        Evaluate all policies.
        
        Args:
            context: Context to evaluate.
            
        Returns:
            List of PolicyEvaluationResult objects.
        """
        results = []
        
        for policy in self._policies.values():
            if policy.is_enabled:
                result = self.evaluate_policy(policy.policy_id, context)
                results.append(result)
        
        return results
    
    def is_compliant(self, context: Dict[str, Any]) -> Tuple[bool, List[PolicyEvaluationResult]]:
        """
        Check if a context is compliant with all policies.
        
        Args:
            context: Context to evaluate.
            
        Returns:
            Tuple of (is_compliant, list of non-compliant results).
        """
        results = self.evaluate_all_policies(context)
        non_compliant = [r for r in results if not r.is_compliant]
        
        return (len(non_compliant) == 0, non_compliant)
    
    def get_compliance_score(self, context: Dict[str, Any]) -> float:
        """
        Get a compliance score (0-100).
        
        Args:
            context: Context to evaluate.
            
        Returns:
            Compliance score.
        """
        results = self.evaluate_all_policies(context)
        total_policies = len(results)
        
        if total_policies == 0:
            return 100.0
        
        compliant_policies = len([r for r in results if r.is_compliant])
        
        return (compliant_policies / total_policies) * 100.0
    
    def get_violations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get all policy violations for a context.
        
        Args:
            context: Context to evaluate.
            
        Returns:
            List of violation dictionaries.
        """
        results = self.evaluate_all_policies(context)
        violations = []
        
        for result in results:
            if not result.is_compliant:
                for violation in result.violations:
                    violations.append({
                        'policy_id': result.policy_id,
                        'policy_name': result.policy_name,
                        'severity': result.severity,
                        'violation': violation,
                    })
        
        return violations
    
    def enable_policy(self, policy_id: str) -> bool:
        """
        Enable a security policy.
        
        Args:
            policy_id: Policy ID.
            
        Returns:
            True if enabled.
        """
        policy = self.get_policy(policy_id)
        
        if not policy:
            return False
        
        policy.is_enabled = True
        policy.updated_at = datetime.utcnow()
        
        return True
    
    def disable_policy(self, policy_id: str) -> bool:
        """
        Disable a security policy.
        
        Args:
            policy_id: Policy ID.
            
        Returns:
            True if disabled.
        """
        policy = self.get_policy(policy_id)
        
        if not policy:
            return False
        
        policy.is_enabled = False
        policy.updated_at = datetime.utcnow()
        
        return True
    
    def export_to_json(self) -> str:
        """
        Export security policies to JSON.
        
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
        Import security policies from JSON.
        
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
                policy = SecurityPolicy(
                    policy_id=policy_data['policy_id'],
                    name=policy_data['name'],
                    description=policy_data.get('description', ''),
                    category=policy_data.get('category', ''),
                    rules=policy_data.get('rules', []),
                    severity=policy_data.get('severity', 'medium'),
                    is_enabled=policy_data.get('is_enabled', True),
                    created_at=datetime.fromisoformat(policy_data['created_at']),
                    updated_at=datetime.fromisoformat(policy_data['updated_at']),
                )
                self._policies[policy.policy_id] = policy
            
            # Import config
            config_data = data.get('config', {})
            self.config = SecurityPolicyConfig(
                policy_dir=config_data.get('policy_dir', '/etc/openlens/policies'),
                auto_reload=config_data.get('auto_reload', True),
                reload_interval=config_data.get('reload_interval', 300),
            )
            
            return True
        
        except Exception as e:
            print(f"Error importing security policies: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get security policy statistics.
        
        Returns:
            Dictionary with statistics.
        """
        with self._lock:
            stats = {
                'total_policies': len(self._policies),
                'enabled_policies': len([p for p in self._policies.values() if p.is_enabled]),
                'disabled_policies': len([p for p in self._policies.values() if not p.is_enabled]),
                'by_category': defaultdict(int),
                'by_severity': defaultdict(int),
            }
            
            for policy in self._policies.values():
                stats['by_category'][policy.category] += 1
                stats['by_severity'][policy.severity] += 1
            
            # Convert defaultdict to dict
            for key in stats:
                if isinstance(stats[key], defaultdict):
                    stats[key] = dict(stats[key])
            
            return stats


# Global security policy manager instance
security_policy_manager = SecurityPolicyManager()
