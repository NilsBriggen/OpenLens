"""
Alert Manager for OpenLens

Provides alerting capabilities:
- Alert creation and management
- Alert deduplication
- Alert escalation
- Alert notification
- Alert lifecycle management
- Alert querying and filtering
"""

import os
import time
import json
import smtplib
import threading
import hashlib

import requests

from .ioc_manager import IOC
from .threat_analysis import ThreatAnalysis
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


@dataclass
class Alert:
    """Represents a security alert."""
    alert_id: str
    title: str
    description: str = ''
    severity: str = 'medium'  # low, medium, high, critical
    status: str = 'new'  # new, acknowledged, investigated, resolved, closed
    source: str = ''
    source_type: str = ''  # ioc, anomaly, threat_analysis, etc.
    source_id: str = ''
    ioc_id: str = ''
    indicator: str = ''
    indicator_type: str = ''
    threat_types: List[str] = field(default_factory=list)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    acknowledged_at: datetime = None
    acknowledged_by: str = ''
    resolved_at: datetime = None
    resolved_by: str = ''
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'alert_id': self.alert_id,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'status': self.status,
            'source': self.source,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'ioc_id': self.ioc_id,
            'indicator': self.indicator,
            'indicator_type': self.indicator_type,
            'threat_types': self.threat_types,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'acknowledged_by': self.acknowledged_by,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by,
            'tags': self.tags,
            'metadata': self.metadata,
        }


@dataclass
class AlertRule:
    """Represents an alert rule."""
    rule_id: str
    name: str
    description: str = ''
    condition: Dict[str, Any] = field(default_factory=dict)
    severity: str = 'medium'
    is_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'rule_id': self.rule_id,
            'name': self.name,
            'description': self.description,
            'condition': self.condition,
            'severity': self.severity,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    def matches(self, context: Dict[str, Any]) -> bool:
        """Check if this rule matches a context."""
        for key, value in self.condition.items():
            if key == 'severity':
                if context.get('severity') != value:
                    return False
            elif key == 'threat_type':
                if value not in context.get('threat_types', []):
                    return False
            elif key == 'indicator_type':
                if context.get('indicator_type') != value:
                    return False
            elif key == 'source':
                if context.get('source') != value:
                    return False
            elif key == 'confidence_min':
                if context.get('confidence', 0) < value:
                    return False
            elif key.startswith('metadata.'):
                metadata_key = key[9:]  # Remove 'metadata.' prefix
                if context.get('metadata', {}).get(metadata_key) != value:
                    return False
        
        return True


@dataclass
class AlertNotification:
    """Represents an alert notification."""
    notification_id: str
    alert_id: str
    method: str = ''  # email, webhook, siem, slack
    recipient: str = ''
    status: str = 'pending'  # pending, sent, failed
    sent_at: datetime = None
    error: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'notification_id': self.notification_id,
            'alert_id': self.alert_id,
            'method': self.method,
            'recipient': self.recipient,
            'status': self.status,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'error': self.error,
        }


@dataclass
class AlertConfig:
    """Configuration for alert manager."""
    deduplication_window: int = 3600  # seconds
    escalation_rules: List[Dict[str, Any]] = field(default_factory=list)
    notification_methods: List[str] = field(default_factory=lambda: ['email', 'webhook'])
    email_settings: Dict[str, Any] = field(default_factory=dict)
    webhook_settings: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'deduplication_window': self.deduplication_window,
            'escalation_rules': self.escalation_rules,
            'notification_methods': self.notification_methods,
            'email_settings': self.email_settings,
            'webhook_settings': self.webhook_settings,
        }


class AlertManager:
    """
    Alert manager for OpenLens.
    
    Provides:
    - Alert creation and management
    - Alert deduplication
    - Alert escalation
    - Alert notification
    - Alert lifecycle management
    - Alert querying and filtering
    """
    
    def __init__(self, config: AlertConfig = None, 
                 ioc_manager=None, threat_analyzer=None):
        """
        Initialize the alert manager.
        
        Args:
            config: AlertConfig instance.
            ioc_manager: IOCManager instance.
            threat_analyzer: ThreatAnalyzer instance.
        """
        self.config = config or AlertConfig()
        self.ioc_manager = ioc_manager
        self.threat_analyzer = threat_analyzer
        self._alerts: Dict[str, Alert] = {}
        self._rules: Dict[str, AlertRule] = {}
        self._notifications: Dict[str, AlertNotification] = {}
        self._deduplication_cache: Dict[str, str] = {}  # hash -> alert_id
        self._lock = threading.Lock()
        
        # Initialize with default rules
        self._initialize_default_rules()
    
    def _initialize_default_rules(self):
        """Initialize default alert rules."""
        # High severity alerts
        high_severity_rule = AlertRule(
            rule_id='high_severity_rule',
            name='High Severity Alerts',
            description='Create alerts for high severity threats',
            condition={'severity': 'high'},
            severity='high',
        )
        self._rules[high_severity_rule.rule_id] = high_severity_rule
        
        # Critical severity alerts
        critical_severity_rule = AlertRule(
            rule_id='critical_severity_rule',
            name='Critical Severity Alerts',
            description='Create alerts for critical severity threats',
            condition={'severity': 'critical'},
            severity='critical',
        )
        self._rules[critical_severity_rule.rule_id] = critical_severity_rule
        
        # Malware alerts
        malware_rule = AlertRule(
            rule_id='malware_rule',
            name='Malware Alerts',
            description='Create alerts for malware indicators',
            condition={'threat_type': 'malware'},
            severity='high',
        )
        self._rules[malware_rule.rule_id] = malware_rule
        
        # Phishing alerts
        phishing_rule = AlertRule(
            rule_id='phishing_rule',
            name='Phishing Alerts',
            description='Create alerts for phishing indicators',
            condition={'threat_type': 'phishing'},
            severity='medium',
        )
        self._rules[phishing_rule.rule_id] = phishing_rule
        
        # High confidence alerts
        high_confidence_rule = AlertRule(
            rule_id='high_confidence_rule',
            name='High Confidence Alerts',
            description='Create alerts for high confidence threats',
            condition={'confidence_min': 0.9},
            severity='medium',
        )
        self._rules[high_confidence_rule.rule_id] = high_confidence_rule
    
    def create_alert(self, title: str, description: str = '', 
                    severity: str = 'medium', source: str = '',
                    source_type: str = '', source_id: str = '',
                    ioc_id: str = '', indicator: str = '',
                    indicator_type: str = '', threat_types: List[str] = None,
                    confidence: float = 0.0, tags: List[str] = None,
                    metadata: Dict[str, Any] = None) -> Alert:
        """
        Create a new alert.
        
        Args:
            title: Alert title.
            description: Alert description.
            severity: Alert severity.
            source: Alert source.
            source_type: Source type.
            source_id: Source ID.
            ioc_id: IOC ID.
            indicator: Indicator.
            indicator_type: Indicator type.
            threat_types: List of threat types.
            confidence: Confidence score.
            tags: List of tags.
            metadata: Alert metadata.
            
        Returns:
            Alert object.
        """
        # Check for deduplication
        alert_hash = self._generate_alert_hash(
            title, indicator, indicator_type, source, source_type, source_id
        )
        
        with self._lock:
            # Check if this alert is a duplicate
            if alert_hash in self._deduplication_cache:
                existing_alert_id = self._deduplication_cache[alert_hash]
                existing_alert = self._alerts.get(existing_alert_id)
                
                if existing_alert and existing_alert.status == 'new':
                    # Update existing alert instead of creating a new one
                    existing_alert.updated_at = datetime.utcnow()
                    existing_alert.confidence = max(existing_alert.confidence, confidence)
                    
                    # Add new threat types
                    for threat_type in (threat_types or []):
                        if threat_type not in existing_alert.threat_types:
                            existing_alert.threat_types.append(threat_type)
                    
                    # Add new tags
                    for tag in (tags or []):
                        if tag not in existing_alert.tags:
                            existing_alert.tags.append(tag)
                    
                    return existing_alert
            
            # Generate alert ID
            alert_id = f"alert_{int(time.time() * 1000)}"
            
            alert = Alert(
                alert_id=alert_id,
                title=title,
                description=description,
                severity=severity,
                source=source,
                source_type=source_type,
                source_id=source_id,
                ioc_id=ioc_id,
                indicator=indicator,
                indicator_type=indicator_type,
                threat_types=threat_types or [],
                confidence=confidence,
                tags=tags or [],
                metadata=metadata or {},
            )
            
            self._alerts[alert_id] = alert
            self._deduplication_cache[alert_hash] = alert_id
            
            # Apply escalation rules
            self._apply_escalation_rules(alert)
            
            # Send notifications
            self._send_notifications(alert)
            
            return alert
    
    def _generate_alert_hash(self, title: str, indicator: str, indicator_type: str,
                           source: str, source_type: str, source_id: str) -> str:
        """Generate a hash for deduplication."""
        hash_data = f"{title}:{indicator}:{indicator_type}:{source}:{source_type}:{source_id}"
        return hashlib.sha256(hash_data.encode()).hexdigest()
    
    def _apply_escalation_rules(self, alert: Alert):
        """Apply escalation rules to an alert."""
        for rule in self.config.escalation_rules:
            if self._matches_escalation_rule(alert, rule):
                # Apply escalation actions
                if 'severity' in rule.get('actions', {}):
                    alert.severity = rule['actions']['severity']
                
                if 'tags' in rule.get('actions', {}):
                    for tag in rule['actions']['tags']:
                        if tag not in alert.tags:
                            alert.tags.append(tag)
                
                if 'notify' in rule.get('actions', {}):
                    self._send_notifications(alert, methods=rule['actions']['notify'])
    
    def _matches_escalation_rule(self, alert: Alert, rule: Dict[str, Any]) -> bool:
        """Check if an alert matches an escalation rule."""
        conditions = rule.get('conditions', {})
        
        for key, value in conditions.items():
            if key == 'severity':
                if alert.severity != value:
                    return False
            elif key == 'threat_type':
                if value not in alert.threat_types:
                    return False
            elif key == 'indicator_type':
                if alert.indicator_type != value:
                    return False
            elif key == 'source':
                if alert.source != value:
                    return False
            elif key == 'confidence_min':
                if alert.confidence < value:
                    return False
        
        return True
    
    def _send_notifications(self, alert: Alert, methods: List[str] = None):
        """
        Send notifications for an alert.

        A channel with no settings configured is skipped: attempting SMTP or a
        webhook POST against unconfigured defaults just burns a connection
        timeout per alert.
        """
        methods = methods or self.config.notification_methods

        for method in methods:
            if method == 'email' and 'email' in self.config.notification_methods:
                if not self.config.email_settings:
                    continue
                self._send_email_notification(alert)
            elif method == 'webhook' and 'webhook' in self.config.notification_methods:
                if not self.config.webhook_settings.get('url'):
                    continue
                self._send_webhook_notification(alert)
            elif method == 'siem':
                self._send_siem_notification(alert)
            elif method == 'slack':
                self._send_slack_notification(alert)
    
    def _send_email_notification(self, alert: Alert) -> AlertNotification:
        """Send an email notification."""
        notification_id = f"notification_{alert.alert_id}_email_{int(time.time() * 1000)}"
        
        try:
            # Get email settings
            settings = self.config.email_settings
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = settings.get('from_address', 'openlens@localhost')
            msg['To'] = settings.get('recipient', 'security@localhost')
            msg['Subject'] = f"[OpenLens Alert] {alert.severity.upper()}: {alert.title}"
            
            # Create email body
            body = f"""
            Alert ID: {alert.alert_id}
            Title: {alert.title}
            Severity: {alert.severity.upper()}
            Description: {alert.description}
            
            Indicator: {alert.indicator}
            Indicator Type: {alert.indicator_type}
            Threat Types: {', '.join(alert.threat_types)}
            Confidence: {alert.confidence:.2%}
            
            Source: {alert.source}
            Source Type: {alert.source_type}
            
            Created: {alert.created_at.isoformat()}
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(settings.get('smtp_host', 'localhost'), settings.get('smtp_port', 25)) as server:
                if settings.get('use_tls', False):
                    server.starttls()
                
                if settings.get('username') and settings.get('password'):
                    server.login(settings['username'], settings['password'])
                
                server.send_message(msg)
            
            notification = AlertNotification(
                notification_id=notification_id,
                alert_id=alert.alert_id,
                method='email',
                recipient=settings.get('recipient', 'security@localhost'),
                status='sent',
                sent_at=datetime.utcnow(),
            )
        
        except Exception as e:
            notification = AlertNotification(
                notification_id=notification_id,
                alert_id=alert.alert_id,
                method='email',
                recipient=settings.get('recipient', 'security@localhost'),
                status='failed',
                sent_at=datetime.utcnow(),
                error=str(e),
            )
        
        with self._lock:
            self._notifications[notification_id] = notification
        
        return notification
    
    def _send_webhook_notification(self, alert: Alert) -> AlertNotification:
        """Send a webhook notification."""
        notification_id = f"notification_{alert.alert_id}_webhook_{int(time.time() * 1000)}"
        
        try:
            settings = self.config.webhook_settings
            url = settings.get('url', '')
            
            if not url:
                raise ValueError("Webhook URL not configured")
            
            # Prepare payload
            payload = {
                'alert_id': alert.alert_id,
                'title': alert.title,
                'description': alert.description,
                'severity': alert.severity,
                'indicator': alert.indicator,
                'indicator_type': alert.indicator_type,
                'threat_types': alert.threat_types,
                'confidence': alert.confidence,
                'created_at': alert.created_at.isoformat(),
            }
            
            # Send request
            headers = {'Content-Type': 'application/json', 'User-Agent': 'OpenLens Alert Manager'}
            if settings.get('api_key'):
                headers['Authorization'] = f"Bearer {settings['api_key']}"
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=settings.get('timeout', 10),
            )
            
            if response.status_code >= 200 and response.status_code < 300:
                status = 'sent'
            else:
                status = 'failed'
                error = f"HTTP {response.status_code}: {response.text}"
            
            notification = AlertNotification(
                notification_id=notification_id,
                alert_id=alert.alert_id,
                method='webhook',
                recipient=url,
                status=status,
                sent_at=datetime.utcnow(),
                error=error if status == 'failed' else '',
            )
        
        except Exception as e:
            notification = AlertNotification(
                notification_id=notification_id,
                alert_id=alert.alert_id,
                method='webhook',
                recipient=settings.get('url', ''),
                status='failed',
                sent_at=datetime.utcnow(),
                error=str(e),
            )
        
        with self._lock:
            self._notifications[notification_id] = notification
        
        return notification
    
    def _send_siem_notification(self, alert: Alert) -> AlertNotification:
        """Send a SIEM notification."""
        # In a real implementation, this would send to a SIEM system
        # For now, just log
        notification_id = f"notification_{alert.alert_id}_siem_{int(time.time() * 1000)}"
        
        notification = AlertNotification(
            notification_id=notification_id,
            alert_id=alert.alert_id,
            method='siem',
            recipient='siem',
            status='sent',
            sent_at=datetime.utcnow(),
        )
        
        with self._lock:
            self._notifications[notification_id] = notification
        
        return notification
    
    def _send_slack_notification(self, alert: Alert) -> AlertNotification:
        """Send a Slack notification."""
        # In a real implementation, this would send to Slack
        # For now, just log
        notification_id = f"notification_{alert.alert_id}_slack_{int(time.time() * 1000)}"
        
        notification = AlertNotification(
            notification_id=notification_id,
            alert_id=alert.alert_id,
            method='slack',
            recipient='slack',
            status='sent',
            sent_at=datetime.utcnow(),
        )
        
        with self._lock:
            self._notifications[notification_id] = notification
        
        return notification
    
    def create_alert_from_ioc(self, ioc_id: str) -> Optional[Alert]:
        """
        Create an alert from an IOC.
        
        Args:
            ioc_id: IOC ID.
            
        Returns:
            Alert or None.
        """
        if not self.ioc_manager:
            return None
        
        ioc = self.ioc_manager.get_ioc_by_id(ioc_id)
        if not ioc:
            return None
        
        # Check if we should create an alert for this IOC
        if not self._should_create_alert_for_ioc(ioc):
            return None
        
        # Analyze the IOC if we have a threat analyzer
        threat_score = None
        if self.threat_analyzer:
            analysis = self.threat_analyzer.analyze_ioc(ioc_id)
            if analysis:
                threat_score = analysis.threat_score
        
        # Determine severity
        severity = ioc.severity
        if threat_score:
            severity = self.threat_analyzer._determine_severity(threat_score)
        
        # Create alert
        alert = self.create_alert(
            title=f"Threat Detected: {ioc.indicator}",
            description=f"Indicator {ioc.indicator} ({ioc.indicator_type}) detected with threat type {ioc.threat_type}",
            severity=severity,
            source='ioc_manager',
            source_type='ioc',
            source_id=ioc_id,
            ioc_id=ioc_id,
            indicator=ioc.indicator,
            indicator_type=ioc.indicator_type,
            threat_types=[ioc.threat_type] if ioc.threat_type else [],
            confidence=ioc.confidence,
            tags=ioc.tags,
            metadata={
                'threat_score': threat_score,
                'feed_source': ioc.source,
            },
        )
        
        return alert
    
    def create_alert_from_analysis(self, analysis_id: str) -> Optional[Alert]:
        """
        Create an alert from a threat analysis.
        
        Args:
            analysis_id: Analysis ID.
            
        Returns:
            Alert or None.
        """
        if not self.threat_analyzer:
            return None
        
        analysis = self.threat_analyzer.get_analysis(analysis_id)
        if not analysis:
            return None
        
        # Check if we should create an alert for this analysis
        if not self._should_create_alert_for_analysis(analysis):
            return None
        
        # Create alert
        alert = self.create_alert(
            title=f"Threat Analysis: {analysis.indicator}",
            description=f"Threat analysis completed for {analysis.indicator} with score {analysis.threat_score:.1f}",
            severity=analysis.severity,
            source='threat_analyzer',
            source_type='threat_analysis',
            source_id=analysis_id,
            ioc_id=analysis.ioc_id,
            indicator=analysis.indicator,
            indicator_type=analysis.indicator_type,
            threat_types=analysis.threat_types,
            confidence=analysis.confidence,
            tags=['threat_analysis'],
            metadata={
                'threat_score': analysis.threat_score,
                'findings': analysis.findings,
                'recommendations': analysis.recommendations,
            },
        )
        
        return alert
    
    def _should_create_alert_for_ioc(self, ioc: IOC) -> bool:
        """Check if we should create an alert for an IOC."""
        # Check if any rule matches
        for rule in self._rules.values():
            if rule.is_enabled:
                context = {
                    'severity': ioc.severity,
                    'threat_types': [ioc.threat_type] if ioc.threat_type else [],
                    'indicator_type': ioc.indicator_type,
                    'source': ioc.source,
                    'confidence': ioc.confidence,
                    'metadata': ioc.metadata,
                }
                
                if rule.matches(context):
                    return True
        
        return False
    
    def _should_create_alert_for_analysis(self, analysis: ThreatAnalysis) -> bool:
        """Check if we should create an alert for an analysis."""
        # Check if any rule matches
        for rule in self._rules.values():
            if rule.is_enabled:
                context = {
                    'severity': analysis.severity,
                    'threat_types': analysis.threat_types,
                    'indicator_type': analysis.indicator_type,
                    'source': analysis.source,
                    'confidence': analysis.confidence,
                    'metadata': analysis.context,
                }
                
                if rule.matches(context):
                    return True
        
        return False
    
    _SEVERITY_LADDER = ('low', 'medium', 'high', 'critical')

    def escalate_alert(self, alert_id: str, severity: str = None,
                       reason: str = '', user_id: str = '',
                       notify: bool = True) -> Optional[Alert]:
        """
        Manually escalate an alert.

        Distinct from _apply_escalation_rules, which applies *configured*
        rules during alert creation. This bumps severity one step on the
        ladder (or to an explicit level), records who/why in metadata, and
        optionally re-notifies.

        Args:
            alert_id: Alert ID.
            severity: Explicit target severity (None to bump one step).
            reason: Free-text reason for the escalation.
            user_id: Who escalated.
            notify: Whether to send notifications about the escalation.

        Returns:
            The updated Alert, or None if the alert or severity is unknown.
        """
        if severity is not None and severity not in self._SEVERITY_LADDER:
            return None

        with self._lock:
            alert = self._alerts.get(alert_id)
            if not alert:
                return None

            if severity is None:
                try:
                    idx = self._SEVERITY_LADDER.index(alert.severity)
                except ValueError:
                    idx = 0
                severity = self._SEVERITY_LADDER[min(idx + 1, len(self._SEVERITY_LADDER) - 1)]

            alert.severity = severity
            alert.updated_at = datetime.utcnow()
            if 'escalated' not in alert.tags:
                alert.tags.append('escalated')
            alert.metadata['escalated_by'] = user_id
            alert.metadata['escalated_at'] = datetime.utcnow().isoformat()
            if reason:
                alert.metadata['escalation_reason'] = reason

        if notify:
            self._send_notifications(alert)

        return alert

    def list_alerts(self, status: str = None, severity: str = None,
                    limit: int = 100, offset: int = 0) -> List[Alert]:
        """List alerts, optionally filtered. Thin wrapper over search_alerts."""
        return self.search_alerts(severity=severity, status=status,
                                  limit=limit, offset=offset)

    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: Alert ID.
            user_id: User ID.
            
        Returns:
            True if acknowledged.
        """
        with self._lock:
            if alert_id not in self._alerts:
                return False
            
            alert = self._alerts[alert_id]
            alert.status = 'acknowledged'
            alert.acknowledged_at = datetime.utcnow()
            alert.acknowledged_by = user_id
            alert.updated_at = datetime.utcnow()
            
            return True
    
    def resolve_alert(self, alert_id: str, user_id: str, 
                     resolution_notes: str = '') -> bool:
        """
        Resolve an alert.
        
        Args:
            alert_id: Alert ID.
            user_id: User ID.
            resolution_notes: Resolution notes.
            
        Returns:
            True if resolved.
        """
        with self._lock:
            if alert_id not in self._alerts:
                return False
            
            alert = self._alerts[alert_id]
            alert.status = 'resolved'
            alert.resolved_at = datetime.utcnow()
            alert.resolved_by = user_id
            alert.updated_at = datetime.utcnow()
            
            # Add resolution notes to description
            if resolution_notes:
                alert.description += f"\n\nResolution: {resolution_notes}"
            
            return True
    
    def close_alert(self, alert_id: str, user_id: str) -> bool:
        """
        Close an alert.
        
        Args:
            alert_id: Alert ID.
            user_id: User ID.
            
        Returns:
            True if closed.
        """
        with self._lock:
            if alert_id not in self._alerts:
                return False
            
            alert = self._alerts[alert_id]
            alert.status = 'closed'
            alert.updated_at = datetime.utcnow()
            
            return True
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """
        Get an alert.
        
        Args:
            alert_id: Alert ID.
            
        Returns:
            Alert or None.
        """
        with self._lock:
            return self._alerts.get(alert_id)
    
    def search_alerts(self, severity: str = None, status: str = None,
                     source: str = None, indicator: str = None,
                     indicator_type: str = None, threat_type: str = None,
                     min_confidence: float = 0.0, tags: List[str] = None,
                     start_date: datetime = None, end_date: datetime = None,
                     limit: int = 100, offset: int = 0) -> List[Alert]:
        """
        Search alerts.
        
        Args:
            severity: Filter by severity.
            status: Filter by status.
            source: Filter by source.
            indicator: Filter by indicator.
            indicator_type: Filter by indicator type.
            threat_type: Filter by threat type.
            min_confidence: Minimum confidence.
            tags: Filter by tags.
            start_date: Start date.
            end_date: End date.
            limit: Maximum number of results.
            offset: Offset.
            
        Returns:
            List of Alert objects.
        """
        with self._lock:
            results = []
            
            for alert in self._alerts.values():
                # Filter by severity
                if severity and alert.severity != severity:
                    continue
                
                # Filter by status
                if status and alert.status != status:
                    continue
                
                # Filter by source
                if source and alert.source != source:
                    continue
                
                # Filter by indicator
                if indicator and indicator.lower() not in alert.indicator.lower():
                    continue
                
                # Filter by indicator type
                if indicator_type and alert.indicator_type != indicator_type:
                    continue
                
                # Filter by threat type
                if threat_type and threat_type not in alert.threat_types:
                    continue
                
                # Filter by confidence
                if alert.confidence < min_confidence:
                    continue
                
                # Filter by tags
                if tags:
                    if not any(tag in alert.tags for tag in tags):
                        continue
                
                # Filter by date
                if start_date and alert.created_at < start_date:
                    continue
                
                if end_date and alert.created_at > end_date:
                    continue
                
                results.append(alert)
            
            # Sort by created_at (descending)
            results.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply limit and offset
            return results[offset:offset + limit]
    
    def get_alert_count(self, status: str = None) -> int:
        """
        Get the count of alerts.
        
        Args:
            status: Filter by status (None for all).
            
        Returns:
            Alert count.
        """
        with self._lock:
            if status:
                return len([a for a in self._alerts.values() if a.status == status])
            return len(self._alerts)
    
    def add_rule(self, rule: AlertRule) -> bool:
        """
        Add an alert rule.
        
        Args:
            rule: AlertRule to add.
            
        Returns:
            True if added.
        """
        with self._lock:
            if rule.rule_id in self._rules:
                return False
            
            self._rules[rule.rule_id] = rule
            return True
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        Remove an alert rule.
        
        Args:
            rule_id: Rule ID.
            
        Returns:
            True if removed.
        """
        with self._lock:
            if rule_id not in self._rules:
                return False
            
            del self._rules[rule_id]
            return True
    
    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """
        Get an alert rule.
        
        Args:
            rule_id: Rule ID.
            
        Returns:
            AlertRule or None.
        """
        return self._rules.get(rule_id)
    
    def list_rules(self) -> List[AlertRule]:
        """
        List all alert rules.
        
        Returns:
            List of AlertRule objects.
        """
        return list(self._rules.values())
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get alert statistics.
        
        Returns:
            Dictionary with statistics.
        """
        with self._lock:
            stats = {
                'total_alerts': len(self._alerts),
                'by_severity': defaultdict(int),
                'by_status': defaultdict(int),
                'by_source': defaultdict(int),
                'by_indicator_type': defaultdict(int),
                'by_threat_type': defaultdict(int),
                'total_rules': len(self._rules),
                'total_notifications': len(self._notifications),
            }
            
            for alert in self._alerts.values():
                stats['by_severity'][alert.severity] += 1
                stats['by_status'][alert.status] += 1
                stats['by_source'][alert.source] += 1
                stats['by_indicator_type'][alert.indicator_type] += 1
                for threat_type in alert.threat_types:
                    stats['by_threat_type'][threat_type] += 1
            
            # Convert defaultdict to dict
            for key in stats:
                if isinstance(stats[key], defaultdict):
                    stats[key] = dict(stats[key])
            
            return stats
    
    def cleanup_old_alerts(self, max_age: int = 30) -> int:
        """
        Clean up old alerts.
        
        Args:
            max_age: Maximum age in days.
            
        Returns:
            Number of alerts cleaned up.
        """
        with self._lock:
            cutoff = datetime.utcnow() - timedelta(days=max_age)
            old_alert_ids = [
                alert_id for alert_id, alert in self._alerts.items()
                if alert.status in ['resolved', 'closed'] and alert.updated_at < cutoff
            ]
            
            for alert_id in old_alert_ids:
                del self._alerts[alert_id]
            
            return len(old_alert_ids)
    
    def cleanup_deduplication_cache(self, max_age: int = 1) -> int:
        """
        Clean up old deduplication cache entries.
        
        Args:
            max_age: Maximum age in hours.
            
        Returns:
            Number of entries cleaned up.
        """
        with self._lock:
            cutoff = datetime.utcnow() - timedelta(hours=max_age)
            old_entries = [
                hash_value for hash_value, alert_id in self._deduplication_cache.items()
                if self._alerts.get(alert_id, Alert(created_at=cutoff)).created_at < cutoff
            ]
            
            for hash_value in old_entries:
                del self._deduplication_cache[hash_value]
            
            return len(old_entries)
    
    def export_to_json(self) -> str:
        """
        Export alert data to JSON.
        
        Returns:
            JSON string.
        """
        data = {
            'alerts': [a.to_dict() for a in self._alerts.values()],
            'rules': [r.to_dict() for r in self._rules.values()],
            'notifications': [n.to_dict() for n in self._notifications.values()],
            'config': self.config.to_dict(),
        }
        
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: str) -> bool:
        """
        Import alert data from JSON.
        
        Args:
            json_data: JSON string.
            
        Returns:
            True if imported.
        """
        try:
            data = json.loads(json_data)
            
            # Import alerts
            self._alerts = {}
            for alert_data in data.get('alerts', []):
                alert = Alert(
                    alert_id=alert_data['alert_id'],
                    title=alert_data['title'],
                    description=alert_data.get('description', ''),
                    severity=alert_data.get('severity', 'medium'),
                    status=alert_data.get('status', 'new'),
                    source=alert_data.get('source', ''),
                    source_type=alert_data.get('source_type', ''),
                    source_id=alert_data.get('source_id', ''),
                    ioc_id=alert_data.get('ioc_id', ''),
                    indicator=alert_data.get('indicator', ''),
                    indicator_type=alert_data.get('indicator_type', ''),
                    threat_types=alert_data.get('threat_types', []),
                    confidence=alert_data.get('confidence', 0.0),
                    created_at=datetime.fromisoformat(alert_data['created_at']),
                    updated_at=datetime.fromisoformat(alert_data['updated_at']),
                    acknowledged_at=datetime.fromisoformat(alert_data['acknowledged_at']) if alert_data.get('acknowledged_at') else None,
                    acknowledged_by=alert_data.get('acknowledged_by', ''),
                    resolved_at=datetime.fromisoformat(alert_data['resolved_at']) if alert_data.get('resolved_at') else None,
                    resolved_by=alert_data.get('resolved_by', ''),
                    tags=alert_data.get('tags', []),
                    metadata=alert_data.get('metadata', {}),
                )
                self._alerts[alert.alert_id] = alert
            
            # Import rules
            self._rules = {}
            for rule_data in data.get('rules', []):
                rule = AlertRule(
                    rule_id=rule_data['rule_id'],
                    name=rule_data['name'],
                    description=rule_data.get('description', ''),
                    condition=rule_data.get('condition', {}),
                    severity=rule_data.get('severity', 'medium'),
                    is_enabled=rule_data.get('is_enabled', True),
                    created_at=datetime.fromisoformat(rule_data['created_at']),
                    updated_at=datetime.fromisoformat(rule_data['updated_at']),
                )
                self._rules[rule.rule_id] = rule
            
            # Import notifications
            self._notifications = {}
            for notification_data in data.get('notifications', []):
                notification = AlertNotification(
                    notification_id=notification_data['notification_id'],
                    alert_id=notification_data['alert_id'],
                    method=notification_data.get('method', ''),
                    recipient=notification_data.get('recipient', ''),
                    status=notification_data.get('status', 'pending'),
                    sent_at=datetime.fromisoformat(notification_data['sent_at']) if notification_data.get('sent_at') else None,
                    error=notification_data.get('error', ''),
                )
                self._notifications[notification.notification_id] = notification
            
            # Import config
            config_data = data.get('config', {})
            self.config = AlertConfig(
                deduplication_window=config_data.get('deduplication_window', 3600),
                escalation_rules=config_data.get('escalation_rules', []),
                notification_methods=config_data.get('notification_methods', ['email', 'webhook']),
                email_settings=config_data.get('email_settings', {}),
                webhook_settings=config_data.get('webhook_settings', {}),
            )
            
            # Rebuild deduplication cache
            self._deduplication_cache = {}
            for alert in self._alerts.values():
                alert_hash = self._generate_alert_hash(
                    alert.title, alert.indicator, alert.indicator_type,
                    alert.source, alert.source_type, alert.source_id
                )
                self._deduplication_cache[alert_hash] = alert.alert_id
            
            return True
        
        except Exception as e:
            print(f"Error importing alert data: {e}")
            return False


# Global alert manager instance
alert_manager = AlertManager()
