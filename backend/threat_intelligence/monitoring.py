"""
Threat Monitoring for OpenLens

Provides real-time threat monitoring capabilities:
- Health monitoring
- Performance monitoring
- Alert monitoring
- System status monitoring
- Dashboard data
"""

import os
import time
import json
import threading
import psutil
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class SystemMetrics:
    """Represents system metrics."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    memory_available: float = 0.0
    disk_usage: float = 0.0
    disk_available: float = 0.0
    network_in: float = 0.0
    network_out: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'memory_available': self.memory_available,
            'disk_usage': self.disk_usage,
            'disk_available': self.disk_available,
            'network_in': self.network_in,
            'network_out': self.network_out,
        }


@dataclass
class ComponentStatus:
    """Represents the status of a component."""
    component: str
    status: str = 'healthy'  # healthy, degraded, unavailable
    last_check: datetime = None
    last_error: str = ''
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'component': self.component,
            'status': self.status,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'last_error': self.last_error,
            'metrics': self.metrics,
        }


@dataclass
class AlertMetrics:
    """Represents alert metrics."""
    total_alerts: int = 0
    new_alerts: int = 0
    acknowledged_alerts: int = 0
    resolved_alerts: int = 0
    by_severity: Dict[str, int] = field(default_factory=dict)
    by_source: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_alerts': self.total_alerts,
            'new_alerts': self.new_alerts,
            'acknowledged_alerts': self.acknowledged_alerts,
            'resolved_alerts': self.resolved_alerts,
            'by_severity': self.by_severity,
            'by_source': self.by_source,
        }


@dataclass
class ThreatMetrics:
    """Represents threat metrics."""
    total_iocs: int = 0
    active_iocs: int = 0
    by_indicator_type: Dict[str, int] = field(default_factory=dict)
    by_threat_type: Dict[str, int] = field(default_factory=dict)
    by_severity: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_iocs': self.total_iocs,
            'active_iocs': self.active_iocs,
            'by_indicator_type': self.by_indicator_type,
            'by_threat_type': self.by_threat_type,
            'by_severity': self.by_severity,
        }


@dataclass
class DashboardData:
    """Represents dashboard data."""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    system_metrics: SystemMetrics = field(default_factory=SystemMetrics)
    component_statuses: List[ComponentStatus] = field(default_factory=list)
    alert_metrics: AlertMetrics = field(default_factory=AlertMetrics)
    threat_metrics: ThreatMetrics = field(default_factory=ThreatMetrics)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'system_metrics': self.system_metrics.to_dict(),
            'component_statuses': [c.to_dict() for c in self.component_statuses],
            'alert_metrics': self.alert_metrics.to_dict(),
            'threat_metrics': self.threat_metrics.to_dict(),
        }


@dataclass
class MonitorConfig:
    """Configuration for threat monitor."""
    check_interval: int = 60  # seconds
    max_history: int = 100  # Number of historical data points to keep
    components: List[str] = field(default_factory=lambda: [
        'graph_engine',
        'ioc_manager',
        'threat_analyzer',
        'alert_manager',
        'threat_feed_manager',
    ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'check_interval': self.check_interval,
            'max_history': self.max_history,
            'components': self.components,
        }


class ThreatMonitor:
    """
    Threat monitor for OpenLens.
    
    Provides:
    - Health monitoring
    - Performance monitoring
    - Alert monitoring
    - System status monitoring
    - Dashboard data
    """
    
    def __init__(self, config: MonitorConfig = None, 
                 graph_engine=None, ioc_manager=None, 
                 threat_analyzer=None, alert_manager=None,
                 threat_feed_manager=None):
        """
        Initialize the threat monitor.
        
        Args:
            config: MonitorConfig instance.
            graph_engine: GraphEngine instance.
            ioc_manager: IOCManager instance.
            threat_analyzer: ThreatAnalyzer instance.
            alert_manager: AlertManager instance.
            threat_feed_manager: ThreatFeedManager instance.
        """
        self.config = config or MonitorConfig()
        self.graph_engine = graph_engine
        self.ioc_manager = ioc_manager
        self.threat_analyzer = threat_analyzer
        self.alert_manager = alert_manager
        self.threat_feed_manager = threat_feed_manager
        
        self._metrics_history: List[SystemMetrics] = []
        self._component_status_history: List[Dict[str, ComponentStatus]] = []
        self._lock = threading.Lock()
        self._monitor_thread = None
        self._running = False
    
    def start_monitoring(self, interval: int = None):
        """
        Start monitoring.
        
        Args:
            interval: Monitoring interval in seconds (None for config default).
        """
        if self._running:
            return
        
        interval = interval or self.config.check_interval
        
        def monitor_loop():
            while self._running:
                self._collect_metrics()
                time.sleep(interval)
        
        self._monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._running = True
        self._monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop monitoring."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
            self._monitor_thread = None
    
    def _collect_metrics(self):
        """Collect all metrics."""
        # Collect system metrics
        system_metrics = self._collect_system_metrics()
        
        # Collect component statuses
        component_statuses = self._collect_component_statuses()
        
        # Collect alert metrics
        alert_metrics = self._collect_alert_metrics()
        
        # Collect threat metrics
        threat_metrics = self._collect_threat_metrics()
        
        with self._lock:
            # Store system metrics
            self._metrics_history.append(system_metrics)
            if len(self._metrics_history) > self.config.max_history:
                self._metrics_history.pop(0)
            
            # Store component statuses
            self._component_status_history.append(component_statuses)
            if len(self._component_status_history) > self.config.max_history:
                self._component_status_history.pop(0)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect system metrics."""
        try:
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            memory_available = memory.available / (1024 ** 3)  # GB
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            disk_available = disk.free / (1024 ** 3)  # GB
            
            # Network usage
            net_io = psutil.net_io_counters()
            network_in = net_io.bytes_recv / (1024 ** 2)  # MB
            network_out = net_io.bytes_sent / (1024 ** 2)  # MB
            
            return SystemMetrics(
                timestamp=datetime.utcnow(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                memory_available=memory_available,
                disk_usage=disk_usage,
                disk_available=disk_available,
                network_in=network_in,
                network_out=network_out,
            )
        
        except Exception as e:
            print(f"Error collecting system metrics: {e}")
            return SystemMetrics()
    
    def _collect_component_statuses(self) -> Dict[str, ComponentStatus]:
        """Collect component statuses."""
        statuses = {}
        
        for component in self.config.components:
            status = self._check_component(component)
            statuses[component] = status
        
        return statuses
    
    def _check_component(self, component: str) -> ComponentStatus:
        """Check the status of a component."""
        status = ComponentStatus(component=component)
        
        try:
            if component == 'graph_engine' and self.graph_engine:
                # Check if graph engine is connected
                if self.graph_engine.verify_connection():
                    status.status = 'healthy'
                    status.metrics = {
                        'connected': True,
                        'stats': self.graph_engine.get_stats(),
                    }
                else:
                    status.status = 'unavailable'
                    status.last_error = 'Not connected to Neo4j'
            
            elif component == 'ioc_manager' and self.ioc_manager:
                stats = self.ioc_manager.get_stats()
                status.status = 'healthy'
                status.metrics = {
                    'total_iocs': stats.total_iocs,
                    'active_iocs': stats.active_iocs,
                }
            
            elif component == 'threat_analyzer' and self.threat_analyzer:
                # get_stats() returns a plain dict here (unlike ioc_manager's
                # IOCStats object) - attribute access made this component
                # permanently report 'degraded'.
                stats = self.threat_analyzer.get_stats()
                status.status = 'healthy'
                status.metrics = {
                    'total_analyses': stats.get('total_analyses', 0),
                    'total_scores': stats.get('total_scores', 0),
                }

            elif component == 'alert_manager' and self.alert_manager:
                stats = self.alert_manager.get_stats()
                status.status = 'healthy'
                status.metrics = {
                    'total_alerts': stats.get('total_alerts', 0),
                    'new_alerts': stats.get('by_status', {}).get('new', 0),
                }
            
            elif component == 'threat_feed_manager' and self.threat_feed_manager:
                stats = self.threat_feed_manager.get_stats()
                status.status = 'healthy'
                status.metrics = {
                    'total_feeds': stats.total_feeds,
                    'active_feeds': stats.active_feeds,
                }
            
            else:
                status.status = 'unavailable'
                status.last_error = f"Component {component} not available"
            
            status.last_check = datetime.utcnow()
        
        except Exception as e:
            status.status = 'degraded'
            status.last_error = str(e)
            status.last_check = datetime.utcnow()
        
        return status
    
    def _collect_alert_metrics(self) -> AlertMetrics:
        """Collect alert metrics."""
        if not self.alert_manager:
            return AlertMetrics()
        
        stats = self.alert_manager.get_stats()
        
        return AlertMetrics(
            total_alerts=stats.get('total_alerts', 0),
            new_alerts=stats.get('by_status', {}).get('new', 0),
            acknowledged_alerts=stats.get('by_status', {}).get('acknowledged', 0),
            resolved_alerts=stats.get('by_status', {}).get('resolved', 0),
            by_severity=stats.get('by_severity', {}),
            by_source=stats.get('by_source', {}),
        )
    
    def _collect_threat_metrics(self) -> ThreatMetrics:
        """Collect threat metrics."""
        if not self.ioc_manager:
            return ThreatMetrics()
        
        stats = self.ioc_manager.get_stats()
        
        return ThreatMetrics(
            total_iocs=stats.total_iocs,
            active_iocs=stats.active_iocs,
            by_indicator_type=stats.by_indicator_type,
            by_threat_type=stats.by_threat_type,
            by_severity=stats.by_severity,
        )
    
    def get_dashboard_data(self) -> DashboardData:
        """
        Get dashboard data.
        
        Returns:
            DashboardData.
        """
        with self._lock:
            # Get latest system metrics
            system_metrics = self._metrics_history[-1] if self._metrics_history else SystemMetrics()
            
            # Get latest component statuses
            component_statuses = []
            if self._component_status_history:
                latest_statuses = self._component_status_history[-1]
                for component, status in latest_statuses.items():
                    component_statuses.append(status)
            
            # Get alert metrics
            alert_metrics = self._collect_alert_metrics()
            
            # Get threat metrics
            threat_metrics = self._collect_threat_metrics()
            
            return DashboardData(
                timestamp=datetime.utcnow(),
                system_metrics=system_metrics,
                component_statuses=component_statuses,
                alert_metrics=alert_metrics,
                threat_metrics=threat_metrics,
            )
    
    def get_system_metrics_history(self, limit: int = 100) -> List[SystemMetrics]:
        """
        Get system metrics history.
        
        Args:
            limit: Maximum number of data points.
            
        Returns:
            List of SystemMetrics.
        """
        with self._lock:
            return self._metrics_history[-limit:] if limit else self._metrics_history
    
    def get_component_status_history(self, component: str = None, limit: int = 100) -> List[ComponentStatus]:
        """
        Get component status history.
        
        Args:
            component: Filter by component (None for all).
            limit: Maximum number of data points.
            
        Returns:
            List of ComponentStatus.
        """
        with self._lock:
            results = []
            
            for statuses in self._component_status_history[-limit:] if limit else self._component_status_history:
                if component:
                    if component in statuses:
                        results.append(statuses[component])
                else:
                    results.extend(statuses.values())
            
            return results
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get overall health status.
        
        Returns:
            Health status dictionary.
        """
        with self._lock:
            # Check all components
            all_healthy = True
            issues = []
            
            if self._component_status_history:
                latest_statuses = self._component_status_history[-1]
                for component, status in latest_statuses.items():
                    if status.status != 'healthy':
                        all_healthy = False
                        issues.append({
                            'component': component,
                            'status': status.status,
                            'error': status.last_error,
                        })
            
            # Check system metrics
            if self._metrics_history:
                latest_metrics = self._metrics_history[-1]
                if latest_metrics.cpu_usage > 90:
                    all_healthy = False
                    issues.append({
                        'component': 'system',
                        'status': 'degraded',
                        'error': f"High CPU usage: {latest_metrics.cpu_usage:.1f}%",
                    })
                
                if latest_metrics.memory_usage > 90:
                    all_healthy = False
                    issues.append({
                        'component': 'system',
                        'status': 'degraded',
                        'error': f"High memory usage: {latest_metrics.memory_usage:.1f}%",
                    })
                
                if latest_metrics.disk_usage > 90:
                    all_healthy = False
                    issues.append({
                        'component': 'system',
                        'status': 'degraded',
                        'error': f"High disk usage: {latest_metrics.disk_usage:.1f}%",
                    })
            
            # No samples means nothing was checked: 'healthy' here would be a
            # false green. Report 'unknown' until monitoring has produced data.
            has_data = bool(self._component_status_history or self._metrics_history)
            if not has_data:
                overall = 'unknown'
            else:
                overall = 'healthy' if all_healthy else 'degraded'

            return {
                'status': overall,
                'issues': issues,
                'monitoring_running': self._running,
                'samples': len(self._metrics_history),
                'timestamp': datetime.utcnow().isoformat(),
            }

    def get_stats(self) -> Dict[str, Any]:
        """
        Aggregate monitor statistics: threats, alerts, component statuses,
        performance, and monitoring loop state.
        """
        components: Dict[str, Any] = {}
        with self._lock:
            if self._component_status_history:
                for name, status in self._component_status_history[-1].items():
                    components[name] = status.to_dict() if hasattr(status, 'to_dict') else {
                        'status': getattr(status, 'status', 'unknown'),
                    }
            samples = len(self._metrics_history)
            running = self._running

        return {
            'threats': self.get_threat_summary(),
            'alerts': self.get_alert_summary(),
            'components': components,
            'performance': self.get_performance_metrics(),
            'monitoring': {
                'running': running,
                'samples': samples,
                'interval': self.config.check_interval if hasattr(self.config, 'check_interval') else None,
            },
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Get performance metrics.
        
        Returns:
            Performance metrics dictionary.
        """
        with self._lock:
            if not self._metrics_history:
                return {}
            
            # Calculate averages
            cpu_usage = sum(m.cpu_usage for m in self._metrics_history) / len(self._metrics_history)
            memory_usage = sum(m.memory_usage for m in self._metrics_history) / len(self._metrics_history)
            disk_usage = sum(m.disk_usage for m in self._metrics_history) / len(self._metrics_history)
            
            # Calculate trends
            if len(self._metrics_history) >= 2:
                latest = self._metrics_history[-1]
                previous = self._metrics_history[-2]
                
                cpu_trend = latest.cpu_usage - previous.cpu_usage
                memory_trend = latest.memory_usage - previous.memory_usage
                disk_trend = latest.disk_usage - previous.disk_usage
            else:
                cpu_trend = 0
                memory_trend = 0
                disk_trend = 0
            
            return {
                'averages': {
                    'cpu_usage': cpu_usage,
                    'memory_usage': memory_usage,
                    'disk_usage': disk_usage,
                },
                'trends': {
                    'cpu_usage': cpu_trend,
                    'memory_usage': memory_trend,
                    'disk_usage': disk_trend,
                },
                'latest': self._metrics_history[-1].to_dict(),
            }
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """
        Get alert summary.
        
        Returns:
            Alert summary dictionary.
        """
        if not self.alert_manager:
            return {}
        
        stats = self.alert_manager.get_stats()
        
        return {
            'total': stats.get('total_alerts', 0),
            'by_status': stats.get('by_status', {}),
            'by_severity': stats.get('by_severity', {}),
            'by_source': stats.get('by_source', {}),
        }
    
    def get_threat_summary(self) -> Dict[str, Any]:
        """
        Get threat summary.
        
        Returns:
            Threat summary dictionary.
        """
        if not self.ioc_manager:
            return {}
        
        stats = self.ioc_manager.get_stats()
        
        return {
            'total': stats.total_iocs,
            'active': stats.active_iocs,
            'by_indicator_type': stats.by_indicator_type,
            'by_threat_type': stats.by_threat_type,
            'by_severity': stats.by_severity,
        }
    
    def export_to_json(self) -> str:
        """
        Export monitoring data to JSON.
        
        Returns:
            JSON string.
        """
        data = {
            'metrics_history': [m.to_dict() for m in self._metrics_history],
            'component_status_history': [
                {comp: status.to_dict() for comp, status in statuses.items()}
                for statuses in self._component_status_history
            ],
            'config': self.config.to_dict(),
        }
        
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: str) -> bool:
        """
        Import monitoring data from JSON.
        
        Args:
            json_data: JSON string.
            
        Returns:
            True if imported.
        """
        try:
            data = json.loads(json_data)
            
            # Import metrics history
            self._metrics_history = []
            for metrics_data in data.get('metrics_history', []):
                metrics = SystemMetrics(
                    timestamp=datetime.fromisoformat(metrics_data['timestamp']),
                    cpu_usage=metrics_data['cpu_usage'],
                    memory_usage=metrics_data['memory_usage'],
                    memory_available=metrics_data['memory_available'],
                    disk_usage=metrics_data['disk_usage'],
                    disk_available=metrics_data['disk_available'],
                    network_in=metrics_data['network_in'],
                    network_out=metrics_data['network_out'],
                )
                self._metrics_history.append(metrics)
            
            # Import component status history
            self._component_status_history = []
            for statuses_data in data.get('component_status_history', []):
                statuses = {}
                for comp, comp_data in statuses_data.items():
                    status = ComponentStatus(
                        component=comp,
                        status=comp_data['status'],
                        last_check=datetime.fromisoformat(comp_data['last_check']) if comp_data.get('last_check') else None,
                        last_error=comp_data.get('last_error', ''),
                        metrics=comp_data.get('metrics', {}),
                    )
                    statuses[comp] = status
                self._component_status_history.append(statuses)
            
            # Import config
            config_data = data.get('config', {})
            self.config = MonitorConfig(
                check_interval=config_data.get('check_interval', 60),
                max_history=config_data.get('max_history', 100),
                components=config_data.get('components', []),
            )
            
            return True
        
        except Exception as e:
            print(f"Error importing monitoring data: {e}")
            return False


# Global threat monitor instance
threat_monitor = ThreatMonitor()
