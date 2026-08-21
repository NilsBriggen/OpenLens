"""
Analytics Dashboard for OpenLens

Provides a comprehensive dashboard with:
- Real-time metrics
- Historical data analysis
- User activity tracking
- System health monitoring
- Customizable widgets
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import json
import hashlib


@dataclass
class DashboardWidget:
    """Represents a dashboard widget."""
    widget_id: str
    widget_type: str  # 'metric', 'chart', 'table', 'status'
    title: str
    description: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    position: Dict[str, int] = field(default_factory=lambda: {'x': 0, 'y': 0, 'w': 4, 'h': 2})
    refresh_interval: int = 0  # seconds, 0 for no auto-refresh
    is_visible: bool = True
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Dashboard:
    """Represents a user dashboard."""
    dashboard_id: str
    user_id: int
    name: str
    widgets: List[DashboardWidget] = field(default_factory=list)
    layout: str = "grid"  # 'grid', 'list', 'custom'
    theme: str = "light"  # 'light', 'dark', 'system'
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_shared: bool = False
    shared_with: List[int] = field(default_factory=list)


class AnalyticsDashboard:
    """
    Manages analytics dashboards for users.
    """
    
    def __init__(self):
        """Initialize the analytics dashboard manager."""
        self.dashboards: Dict[str, Dashboard] = {}
        self.user_dashboards: Dict[int, List[str]] = defaultdict(list)
        self.widget_templates: Dict[str, Dict] = self._load_widget_templates()
    
    def _load_widget_templates(self) -> Dict[str, Dict]:
        """Load default widget templates."""
        return {
            'total_users': {
                'type': 'metric',
                'title': 'Total Users',
                'description': 'Number of registered users',
                'data_source': 'users.count',
                'icon': 'users',
                'color': '#3B82F6',
            },
            'active_sessions': {
                'type': 'metric',
                'title': 'Active Sessions',
                'description': 'Currently active user sessions',
                'data_source': 'sessions.active_count',
                'icon': 'activity',
                'color': '#10B981',
            },
            'api_requests': {
                'type': 'chart',
                'title': 'API Requests',
                'description': 'API requests over time',
                'chart_type': 'line',
                'data_source': 'metrics.api_requests',
                'time_range': '24h',
            },
            'scraping_jobs': {
                'type': 'chart',
                'title': 'Scraping Jobs',
                'description': 'Scraping jobs by status',
                'chart_type': 'bar',
                'data_source': 'metrics.scraping_jobs',
            },
            'system_health': {
                'type': 'status',
                'title': 'System Health',
                'description': 'Overall system status',
                'data_source': 'health.status',
                'indicators': ['database', 'cache', 'queue'],
            },
            'recent_activity': {
                'type': 'table',
                'title': 'Recent Activity',
                'description': 'Latest user actions',
                'data_source': 'activity.recent',
                'columns': ['timestamp', 'user', 'action', 'details'],
                'limit': 10,
            },
        }
    
    def create_dashboard(self, user_id: int, name: str = 'My Dashboard', 
                        layout: str = 'grid') -> Dashboard:
        """
        Create a new dashboard for a user.
        
        Args:
            user_id: User ID.
            name: Dashboard name.
            layout: Dashboard layout type.
            
        Returns:
            Created Dashboard object.
        """
        dashboard_id = hashlib.sha256(f"{user_id}_{name}_{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]
        
        dashboard = Dashboard(
            dashboard_id=dashboard_id,
            user_id=user_id,
            name=name,
            layout=layout,
        )
        
        self.dashboards[dashboard_id] = dashboard
        self.user_dashboards[user_id].append(dashboard_id)
        
        return dashboard
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """
        Get a dashboard by ID.
        
        Args:
            dashboard_id: Dashboard ID.
            
        Returns:
            Dashboard object or None if not found.
        """
        return self.dashboards.get(dashboard_id)
    
    def get_user_dashboards(self, user_id: int) -> List[Dashboard]:
        """
        Get all dashboards for a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            List of Dashboard objects.
        """
        dashboard_ids = self.user_dashboards.get(user_id, [])
        return [self.dashboards[did] for did in dashboard_ids if did in self.dashboards]
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """
        Delete a dashboard.
        
        Args:
            dashboard_id: Dashboard ID.
            
        Returns:
            True if deleted, False if not found.
        """
        if dashboard_id not in self.dashboards:
            return False
        
        dashboard = self.dashboards[dashboard_id]
        
        # Remove from user's dashboards
        if dashboard.user_id in self.user_dashboards:
            self.user_dashboards[dashboard.user_id].remove(dashboard_id)
        
        del self.dashboards[dashboard_id]
        return True
    
    def add_widget(self, dashboard_id: str, widget_type: str, 
                   title: str = '', position: Dict = None, **kwargs) -> Optional[DashboardWidget]:
        """
        Add a widget to a dashboard.
        
        Args:
            dashboard_id: Dashboard ID.
            widget_type: Widget type.
            title: Widget title.
            position: Widget position.
            **kwargs: Additional widget configuration.
            
        Returns:
            Created DashboardWidget or None if dashboard not found.
        """
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return None
        
        widget_id = hashlib.sha256(f"{dashboard_id}_{widget_type}_{datetime.utcnow().isoformat()}".encode()).hexdigest()[:8]
        
        # Get widget template
        template = self.widget_templates.get(widget_type, {})
        
        widget = DashboardWidget(
            widget_id=widget_id,
            widget_type=widget_type,
            title=title or template.get('title', widget_type),
            description=template.get('description', ''),
            data=kwargs.get('data', {}),
            position=position or template.get('position', {'x': 0, 'y': 0, 'w': 4, 'h': 2}),
            refresh_interval=kwargs.get('refresh_interval', template.get('refresh_interval', 0)),
            config=kwargs.get('config', template.get('config', {})),
        )
        
        dashboard.widgets.append(widget)
        dashboard.updated_at = datetime.utcnow()
        
        return widget
    
    def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        """
        Remove a widget from a dashboard.
        
        Args:
            dashboard_id: Dashboard ID.
            widget_id: Widget ID.
            
        Returns:
            True if removed, False if not found.
        """
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return False
        
        for i, widget in enumerate(dashboard.widgets):
            if widget.widget_id == widget_id:
                dashboard.widgets.pop(i)
                dashboard.updated_at = datetime.utcnow()
                return True
        
        return False
    
    def update_widget(self, dashboard_id: str, widget_id: str, **kwargs) -> bool:
        """
        Update a widget in a dashboard.
        
        Args:
            dashboard_id: Dashboard ID.
            widget_id: Widget ID.
            **kwargs: Fields to update.
            
        Returns:
            True if updated, False if not found.
        """
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return False
        
        for widget in dashboard.widgets:
            if widget.widget_id == widget_id:
                for key, value in kwargs.items():
                    if hasattr(widget, key):
                        setattr(widget, key, value)
                dashboard.updated_at = datetime.utcnow()
                return True
        
        return False
    
    def get_widget_data(self, widget: DashboardWidget, user_id: int = None) -> Dict[str, Any]:
        """
        Get data for a widget.
        
        Args:
            widget: DashboardWidget object.
            user_id: Optional user ID for user-specific data.
            
        Returns:
            Dictionary with widget data.
        """
        data_source = widget.config.get('data_source', '')
        
        # Parse data source (e.g., 'users.count', 'metrics.api_requests')
        if '.' in data_source:
            source_type, source_key = data_source.split('.', 1)
        else:
            source_type = data_source
            source_key = None
        
        # Get data based on source type
        if source_type == 'users':
            return self._get_user_data(source_key, user_id)
        elif source_type == 'metrics':
            return self._get_metric_data(source_key, user_id)
        elif source_type == 'health':
            return self._get_health_data(source_key)
        elif source_type == 'activity':
            return self._get_activity_data(source_key, user_id)
        else:
            return {'error': f'Unknown data source: {data_source}'}
    
    def _get_user_data(self, key: str, user_id: int = None) -> Dict[str, Any]:
        """Get user-related data."""
        # In a real implementation, this would query the database
        # For now, return mock data
        if key == 'count':
            return {'value': 42, 'label': 'Total Users'}
        elif key == 'active':
            return {'value': 15, 'label': 'Active Users'}
        elif key == 'recent':
            return {
                'users': [
                    {'id': 1, 'username': 'user1', 'last_active': datetime.utcnow().isoformat()},
                    {'id': 2, 'username': 'user2', 'last_active': (datetime.utcnow() - timedelta(hours=1)).isoformat()},
                ]
            }
        return {}
    
    def _get_metric_data(self, key: str, user_id: int = None) -> Dict[str, Any]:
        """Get metric data."""
        # In a real implementation, this would query the metrics system
        # For now, return mock data
        if key == 'api_requests':
            return {
                'labels': [f"{i}:00" for i in range(24)],
                'datasets': [{
                    'label': 'Requests',
                    'data': [100 + i * 10 for i in range(24)],
                    'borderColor': '#3B82F6',
                    'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                }]
            }
        elif key == 'scraping_jobs':
            return {
                'labels': ['Pending', 'Running', 'Completed', 'Failed'],
                'datasets': [{
                    'label': 'Jobs',
                    'data': [5, 2, 15, 3],
                    'backgroundColor': ['#FBBF24', '#3B82F6', '#10B981', '#EF4444'],
                }]
            }
        return {}
    
    def _get_health_data(self, key: str) -> Dict[str, Any]:
        """Get health data."""
        if key == 'status':
            return {
                'status': 'healthy',
                'indicators': {
                    'database': {'status': 'healthy', 'message': 'Connected'},
                    'cache': {'status': 'healthy', 'message': 'Connected'},
                    'queue': {'status': 'healthy', 'message': 'Running'},
                }
            }
        return {}
    
    def _get_activity_data(self, key: str, user_id: int = None) -> Dict[str, Any]:
        """Get activity data."""
        if key == 'recent':
            return {
                'activities': [
                    {
                        'timestamp': datetime.utcnow().isoformat(),
                        'user': 'user1',
                        'action': 'scraping_started',
                        'details': {'platform': 'twitter', 'target': 'user123'},
                    },
                    {
                        'timestamp': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                        'user': 'user2',
                        'action': 'analysis_completed',
                        'details': {'type': 'sentiment', 'count': 100},
                    },
                ]
            }
        return {}
    
    def refresh_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Refresh all widgets in a dashboard.
        
        Args:
            dashboard_id: Dashboard ID.
            
        Returns:
            Dictionary with refreshed widget data.
        """
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return {'error': 'Dashboard not found'}
        
        result = {
            'dashboard_id': dashboard_id,
            'widgets': [],
        }
        
        for widget in dashboard.widgets:
            if widget.refresh_interval > 0:
                data = self.get_widget_data(widget)
                result['widgets'].append({
                    'widget_id': widget.widget_id,
                    'data': data,
                })
        
        return result
    
    def share_dashboard(self, dashboard_id: str, user_ids: List[int]) -> bool:
        """
        Share a dashboard with other users.
        
        Args:
            dashboard_id: Dashboard ID.
            user_ids: List of user IDs to share with.
            
        Returns:
            True if successful, False if dashboard not found.
        """
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return False
        
        dashboard.is_shared = True
        dashboard.shared_with = list(set(dashboard.shared_with + user_ids))
        dashboard.updated_at = datetime.utcnow()
        
        return True
    
    def unshare_dashboard(self, dashboard_id: str, user_id: int = None) -> bool:
        """
        Unshare a dashboard.
        
        Args:
            dashboard_id: Dashboard ID.
            user_id: Optional user ID to remove from shared list.
            
        Returns:
            True if successful, False if dashboard not found.
        """
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return False
        
        if user_id:
            if user_id in dashboard.shared_with:
                dashboard.shared_with.remove(user_id)
        else:
            dashboard.is_shared = False
            dashboard.shared_with = []
        
        dashboard.updated_at = datetime.utcnow()
        return True
    
    def export_dashboard(self, dashboard_id: str, format: str = 'json') -> Dict[str, Any]:
        """
        Export a dashboard in a specific format.
        
        Args:
            dashboard_id: Dashboard ID.
            format: Export format ('json', 'pdf', 'png').
            
        Returns:
            Dictionary with export data.
        """
        dashboard = self.get_dashboard(dashboard_id)
        if not dashboard:
            return {'error': 'Dashboard not found'}
        
        if format == 'json':
            return {
                'dashboard': {
                    'id': dashboard.dashboard_id,
                    'name': dashboard.name,
                    'layout': dashboard.layout,
                    'widgets': [
                        {
                            'id': w.widget_id,
                            'type': w.widget_type,
                            'title': w.title,
                            'position': w.position,
                            'data': self.get_widget_data(w),
                        } for w in dashboard.widgets
                    ],
                }
            }
        else:
            return {'error': f'Export format {format} not yet supported'}


# Global dashboard instance
analytics_dashboard = AnalyticsDashboard()
