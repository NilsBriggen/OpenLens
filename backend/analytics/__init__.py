"""
Analytics Module for OpenLens

Provides advanced analytics and dashboard functionality.
"""

from .dashboard import AnalyticsDashboard, analytics_dashboard
from .metrics import MetricsCollector, metrics_collector
from .visualizations import VisualizationGenerator, visualization_generator

__all__ = [
    'AnalyticsDashboard',
    'analytics_dashboard',
    'MetricsCollector',
    'metrics_collector',
    'VisualizationGenerator',
    'visualization_generator',
]
