"""
AI/ML Module for OpenLens

Provides AI-powered insights and anomaly detection:
- Anomaly detection
- Entity resolution
- Predictive analytics
- Similarity matching
- Clustering
- Graph-based ML
- Threat intelligence facade
"""

from .anomaly_detection import AnomalyDetector, anomaly_detector
from .entity_resolution import EntityResolver, entity_resolver
from .predictive_analytics import PredictiveAnalyzer, predictive_analyzer
from .similarity_matching import SimilarityMatcher, similarity_matcher
from .clustering import ClusterAnalyzer, cluster_analyzer
from .graph_ml import GraphML, graph_ml
from .threat_intelligence import ThreatIntelligence, threat_intelligence

__all__ = [
    'AnomalyDetector',
    'anomaly_detector',
    'EntityResolver',
    'entity_resolver',
    'PredictiveAnalyzer',
    'predictive_analyzer',
    'SimilarityMatcher',
    'similarity_matcher',
    'ClusterAnalyzer',
    'cluster_analyzer',
    'GraphML',
    'graph_ml',
    'ThreatIntelligence',
    'threat_intelligence',
]
