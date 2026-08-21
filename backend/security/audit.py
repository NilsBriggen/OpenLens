"""
Audit Logging for OpenLens

Provides comprehensive audit logging:
- Event logging
- User activity tracking
- System events
- Security events
- Log filtering
- Log export
"""

import os
import time
import json
import logging
import threading
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from enum import Enum


class AuditEventType(Enum):
    """Types of audit events."""
    AUTHENTICATION = 'authentication'
    AUTHORIZATION = 'authorization'
    DATA_ACCESS = 'data_access'
    DATA_MODIFICATION = 'data_modification'
    DATA_DELETION = 'data_deletion'
    CONFIGURATION_CHANGE = 'configuration_change'
    SYSTEM_EVENT = 'system_event'
    SECURITY_EVENT = 'security_event'
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'


class AuditEventSeverity(Enum):
    """Severity levels for audit events."""
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    INFO = 'info'


@dataclass
class AuditEvent:
    """Represents an audit event."""
    event_id: str
    event_type: str
    severity: str = 'info'
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: str = ''
    username: str = ''
    resource: str = ''
    action: str = ''
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: str = ''
    user_agent: str = ''
    success: bool = True
    error: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'severity': self.severity,
            'timestamp': self.timestamp.isoformat(),
            'user_id': self.user_id,
            'username': self.username,
            'resource': self.resource,
            'action': self.action,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'success': self.success,
            'error': self.error,
        }


@dataclass
class AuditQuery:
    """Query for audit logs."""
    event_types: List[str] = field(default_factory=list)
    severities: List[str] = field(default_factory=list)
    user_ids: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    start_time: datetime = None
    end_time: datetime = None
    limit: int = 100
    offset: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_types': self.event_types,
            'severities': self.severities,
            'user_ids': self.user_ids,
            'resources': self.resources,
            'actions': self.actions,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'limit': self.limit,
            'offset': self.offset,
        }


@dataclass
class AuditConfig:
    """Configuration for audit logging."""
    log_file: str = '/var/log/openlens/audit.log'
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    max_files: int = 10
    log_level: str = 'INFO'
    enable_console: bool = False
    enable_file: bool = True
    enable_database: bool = False
    database_url: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'log_file': self.log_file,
            'max_file_size': self.max_file_size,
            'max_files': self.max_files,
            'log_level': self.log_level,
            'enable_console': self.enable_console,
            'enable_file': self.enable_file,
            'enable_database': self.enable_database,
            'database_url': self.database_url,
        }


class AuditLogger:
    """
    Audit logger for OpenLens.
    
    Provides:
    - Event logging
    - User activity tracking
    - System events
    - Security events
    - Log filtering
    - Log export
    """
    
    def __init__(self, config: AuditConfig = None):
        """
        Initialize the audit logger.
        
        Args:
            config: AuditConfig instance.
        """
        self.config = config or AuditConfig()
        self._events: List[AuditEvent] = []
        self._lock = threading.Lock()
        self._event_counter = 0
        
        # Set up logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up Python logging."""
        self._logger = logging.getLogger('openlens.audit')
        self._logger.setLevel(getattr(logging, self.config.log_level.upper(), logging.INFO))
        
        # Clear existing handlers
        self._logger.handlers = []
        
        # Console handler
        if self.config.enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.config.log_level.upper(), logging.INFO))
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self._logger.addHandler(console_handler)
        
        # File handler
        if self.config.enable_file:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(self.config.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.handlers.RotatingFileHandler(
                self.config.log_file,
                maxBytes=self.config.max_file_size,
                backupCount=self.config.max_files,
            )
            file_handler.setLevel(getattr(logging, self.config.log_level.upper(), logging.INFO))
            file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self._logger.addHandler(file_handler)
    
    def log(self, event_type: str, severity: str = 'info', 
            user_id: str = '', username: str = '', resource: str = '',
            action: str = '', details: Dict = None, ip_address: str = '',
            user_agent: str = '', success: bool = True, error: str = '') -> AuditEvent:
        """
        Log an audit event.
        
        Args:
            event_type: Type of event.
            severity: Severity level.
            user_id: User ID.
            username: Username.
            resource: Resource.
            action: Action.
            details: Event details.
            ip_address: IP address.
            user_agent: User agent.
            success: Whether the action was successful.
            error: Error message.
            
        Returns:
            AuditEvent.
        """
        with self._lock:
            self._event_counter += 1
            event_id = f"audit_{self._event_counter}_{int(time.time() * 1000)}"
            
            event = AuditEvent(
                event_id=event_id,
                event_type=event_type,
                severity=severity,
                timestamp=datetime.utcnow(),
                user_id=user_id,
                username=username,
                resource=resource,
                action=action,
                details=details or {},
                ip_address=ip_address,
                user_agent=user_agent,
                success=success,
                error=error,
            )
            
            # Store in memory
            self._events.append(event)
            
            # Log to file/console
            self._log_to_file(event)
            
            # Log to database if enabled
            if self.config.enable_database:
                self._log_to_database(event)
            
            return event
    
    def _log_to_file(self, event: AuditEvent):
        """Log event to file."""
        log_message = f"[{event.event_type.upper()}] {event.username}@{event.ip_address} - {event.action} on {event.resource}"
        
        if event.error:
            log_message += f" - ERROR: {event.error}"
        
        if event.details:
            log_message += f" - DETAILS: {json.dumps(event.details, default=str)}"
        
        # Use appropriate log level
        if event.severity == 'critical':
            self._logger.critical(log_message)
        elif event.severity == 'high':
            self._logger.error(log_message)
        elif event.severity == 'medium':
            self._logger.warning(log_message)
        else:
            self._logger.info(log_message)
    
    def _log_to_database(self, event: AuditEvent):
        """Log event to database."""
        # In a real implementation, this would save to a database
        # For now, just print
        print(f"Database logging not implemented: {event.event_id}")
    
    def log_authentication(self, user_id: str, username: str, 
                          success: bool, error: str = '', 
                          ip_address: str = '', user_agent: str = '') -> AuditEvent:
        """
        Log an authentication event.
        
        Args:
            user_id: User ID.
            username: Username.
            success: Whether authentication was successful.
            error: Error message.
            ip_address: IP address.
            user_agent: User agent.
            
        Returns:
            AuditEvent.
        """
        severity = 'high' if not success else 'info'
        
        return self.log(
            event_type=AuditEventType.AUTHENTICATION.value,
            severity=severity,
            user_id=user_id,
            username=username,
            action='login' if success else 'login_failed',
            success=success,
            error=error,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    def log_authorization(self, user_id: str, username: str, 
                          resource: str, action: str, 
                          success: bool, error: str = '', 
                          ip_address: str = '', user_agent: str = '') -> AuditEvent:
        """
        Log an authorization event.
        
        Args:
            user_id: User ID.
            username: Username.
            resource: Resource.
            action: Action.
            success: Whether authorization was successful.
            error: Error message.
            ip_address: IP address.
            user_agent: User agent.
            
        Returns:
            AuditEvent.
        """
        severity = 'high' if not success else 'info'
        
        return self.log(
            event_type=AuditEventType.AUTHORIZATION.value,
            severity=severity,
            user_id=user_id,
            username=username,
            resource=resource,
            action=action,
            success=success,
            error=error,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    def log_data_access(self, user_id: str, username: str, 
                        resource: str, action: str = 'read',
                        details: Dict = None, ip_address: str = '',
                        user_agent: str = '') -> AuditEvent:
        """
        Log a data access event.
        
        Args:
            user_id: User ID.
            username: Username.
            resource: Resource.
            action: Action.
            details: Event details.
            ip_address: IP address.
            user_agent: User agent.
            
        Returns:
            AuditEvent.
        """
        return self.log(
            event_type=AuditEventType.DATA_ACCESS.value,
            severity='info',
            user_id=user_id,
            username=username,
            resource=resource,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    def log_data_modification(self, user_id: str, username: str, 
                              resource: str, action: str = 'update',
                              details: Dict = None, ip_address: str = '',
                              user_agent: str = '') -> AuditEvent:
        """
        Log a data modification event.
        
        Args:
            user_id: User ID.
            username: Username.
            resource: Resource.
            action: Action.
            details: Event details.
            ip_address: IP address.
            user_agent: User agent.
            
        Returns:
            AuditEvent.
        """
        return self.log(
            event_type=AuditEventType.DATA_MODIFICATION.value,
            severity='medium',
            user_id=user_id,
            username=username,
            resource=resource,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    def log_data_deletion(self, user_id: str, username: str, 
                          resource: str, details: Dict = None,
                          ip_address: str = '', user_agent: str = '') -> AuditEvent:
        """
        Log a data deletion event.
        
        Args:
            user_id: User ID.
            username: Username.
            resource: Resource.
            details: Event details.
            ip_address: IP address.
            user_agent: User agent.
            
        Returns:
            AuditEvent.
        """
        return self.log(
            event_type=AuditEventType.DATA_DELETION.value,
            severity='high',
            user_id=user_id,
            username=username,
            resource=resource,
            action='delete',
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    def log_configuration_change(self, user_id: str, username: str, 
                                resource: str, action: str, 
                                details: Dict = None, ip_address: str = '',
                                user_agent: str = '') -> AuditEvent:
        """
        Log a configuration change event.
        
        Args:
            user_id: User ID.
            username: Username.
            resource: Resource.
            action: Action.
            details: Event details.
            ip_address: IP address.
            user_agent: User agent.
            
        Returns:
            AuditEvent.
        """
        return self.log(
            event_type=AuditEventType.CONFIGURATION_CHANGE.value,
            severity='medium',
            user_id=user_id,
            username=username,
            resource=resource,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    def log_security_event(self, user_id: str, username: str, 
                           event_type: str, details: Dict = None,
                           ip_address: str = '', user_agent: str = '') -> AuditEvent:
        """
        Log a security event.
        
        Args:
            user_id: User ID.
            username: Username.
            event_type: Type of security event.
            details: Event details.
            ip_address: IP address.
            user_agent: User agent.
            
        Returns:
            AuditEvent.
        """
        return self.log(
            event_type=AuditEventType.SECURITY_EVENT.value,
            severity='high',
            user_id=user_id,
            username=username,
            action=event_type,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    def log_error(self, user_id: str, username: str, 
                  resource: str, action: str, error: str,
                  ip_address: str = '', user_agent: str = '') -> AuditEvent:
        """
        Log an error event.
        
        Args:
            user_id: User ID.
            username: Username.
            resource: Resource.
            action: Action.
            error: Error message.
            ip_address: IP address.
            user_agent: User agent.
            
        Returns:
            AuditEvent.
        """
        return self.log(
            event_type=AuditEventType.ERROR.value,
            severity='high',
            user_id=user_id,
            username=username,
            resource=resource,
            action=action,
            success=False,
            error=error,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    def query(self, query: AuditQuery = None) -> List[AuditEvent]:
        """
        Query audit logs.
        
        Args:
            query: AuditQuery object.
            
        Returns:
            List of AuditEvent objects.
        """
        with self._lock:
            query = query or AuditQuery()
            
            results = []
            for event in self._events:
                # Filter by event type
                if query.event_types and event.event_type not in query.event_types:
                    continue
                
                # Filter by severity
                if query.severities and event.severity not in query.severities:
                    continue
                
                # Filter by user ID
                if query.user_ids and event.user_id not in query.user_ids:
                    continue
                
                # Filter by resource
                if query.resources and event.resource not in query.resources:
                    continue
                
                # Filter by action
                if query.actions and event.action not in query.actions:
                    continue
                
                # Filter by time
                if query.start_time and event.timestamp < query.start_time:
                    continue
                
                if query.end_time and event.timestamp > query.end_time:
                    continue
                
                results.append(event)
            
            # Apply limit and offset
            return results[query.offset:query.offset + query.limit]
    
    def get_event(self, event_id: str) -> Optional[AuditEvent]:
        """
        Get a specific audit event.
        
        Args:
            event_id: Event ID.
            
        Returns:
            AuditEvent or None.
        """
        with self._lock:
            for event in self._events:
                if event.event_id == event_id:
                    return event
            return None
    
    def get_events_by_user(self, user_id: str, limit: int = 100) -> List[AuditEvent]:
        """
        Get all events for a specific user.
        
        Args:
            user_id: User ID.
            limit: Maximum number of events to return.
            
        Returns:
            List of AuditEvent objects.
        """
        with self._lock:
            return [e for e in self._events if e.user_id == user_id][:limit]
    
    def get_events_by_resource(self, resource: str, limit: int = 100) -> List[AuditEvent]:
        """
        Get all events for a specific resource.
        
        Args:
            resource: Resource.
            limit: Maximum number of events to return.
            
        Returns:
            List of AuditEvent objects.
        """
        with self._lock:
            return [e for e in self._events if e.resource == resource][:limit]
    
    def get_recent_events(self, limit: int = 100) -> List[AuditEvent]:
        """
        Get recent audit events.
        
        Args:
            limit: Maximum number of events to return.
            
        Returns:
            List of AuditEvent objects.
        """
        with self._lock:
            return sorted(self._events, key=lambda x: x.timestamp, reverse=True)[:limit]
    
    def get_events_by_time_range(self, start_time: datetime, end_time: datetime) -> List[AuditEvent]:
        """
        Get events within a time range.
        
        Args:
            start_time: Start time.
            end_time: End time.
            
        Returns:
            List of AuditEvent objects.
        """
        with self._lock:
            return [e for e in self._events if start_time <= e.timestamp <= end_time]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get audit log statistics.
        
        Returns:
            Dictionary with statistics.
        """
        with self._lock:
            stats = {
                'total_events': len(self._events),
                'by_type': defaultdict(int),
                'by_severity': defaultdict(int),
                'by_user': defaultdict(int),
                'by_resource': defaultdict(int),
                'by_action': defaultdict(int),
            }
            
            for event in self._events:
                stats['by_type'][event.event_type] += 1
                stats['by_severity'][event.severity] += 1
                stats['by_user'][event.user_id] += 1
                stats['by_resource'][event.resource] += 1
                stats['by_action'][event.action] += 1
            
            # Convert defaultdict to dict
            for key in stats:
                stats[key] = dict(stats[key])
            
            return stats
    
    def export_to_json(self, query: AuditQuery = None) -> str:
        """
        Export audit logs to JSON.
        
        Args:
            query: AuditQuery object.
            
        Returns:
            JSON string.
        """
        events = self.query(query)
        return json.dumps([e.to_dict() for e in events], indent=2)
    
    def export_to_csv(self, query: AuditQuery = None) -> str:
        """
        Export audit logs to CSV.
        
        Args:
            query: AuditQuery object.
            
        Returns:
            CSV string.
        """
        events = self.query(query)
        
        if not events:
            return ''
        
        # Get all field names
        fieldnames = set()
        for event in events:
            fieldnames.update(event.to_dict().keys())
        
        # Create CSV header
        csv_lines = [','.join(sorted(fieldnames))]
        
        # Add data rows
        for event in events:
            event_dict = event.to_dict()
            row = [str(event_dict.get(field, '')) for field in sorted(fieldnames)]
            csv_lines.append(','.join(f'"{value}"' for value in row))
        
        return '\n'.join(csv_lines)
    
    def clear(self):
        """Clear all audit logs."""
        with self._lock:
            self._events = []
    
    def cleanup(self, max_age: int = 30) -> int:
        """
        Clean up old audit logs.
        
        Args:
            max_age: Maximum age in days.
            
        Returns:
            Number of events deleted.
        """
        with self._lock:
            cutoff = datetime.utcnow() - timedelta(days=max_age)
            old_events = [e for e in self._events if e.timestamp < cutoff]
            self._events = [e for e in self._events if e.timestamp >= cutoff]
            return len(old_events)


# Global audit logger instance
audit_logger = AuditLogger()
