"""
Anomaly Detection Module for OpenLens

Provides advanced anomaly detection capabilities:
- Statistical anomaly detection
- Machine learning-based anomaly detection
- Graph-based anomaly detection
- Temporal anomaly detection
- Ensemble methods
"""

import time
import json
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import math

# Try to import numpy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("NumPy not available. Install with: pip install numpy")

# Try to import pandas
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Pandas not available. Install with: pip install pandas")

# Try to import scikit-learn
try:
    from sklearn.ensemble import IsolationForest, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN
    from sklearn.neighbors import LocalOutlierFactor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not available. Install with: pip install scikit-learn")

# Try to import pyod
try:
    from pyod.models.iforest import IForest
    from pyod.models.knn import KNN
    from pyod.models.pca import PCA
    PYOD_AVAILABLE = True
except ImportError:
    PYOD_AVAILABLE = False
    print("PyOD not available. Install with: pip install pyod")


@dataclass
class Anomaly:
    """Represents a detected anomaly."""
    anomaly_id: str
    entity_id: str
    entity_type: str  # node, edge, pattern
    score: float
    features: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = None
    method: str = ''
    explanation: str = ''
    severity: str = 'medium'  # low, medium, high, critical
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'anomaly_id': self.anomaly_id,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'score': self.score,
            'features': self.features,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'method': self.method,
            'explanation': self.explanation,
            'severity': self.severity,
        }


@dataclass
class AnomalyDetectionResult:
    """Result of anomaly detection."""
    method: str
    anomalies: List[Anomaly] = field(default_factory=list)
    total_entities: int = 0
    anomalous_entities: int = 0
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'method': self.method,
            'anomalies': [a.to_dict() for a in self.anomalies],
            'total_entities': self.total_entities,
            'anomalous_entities': self.anomalous_entities,
            'execution_time': self.execution_time,
        }


@dataclass
class AnomalyDetectionConfig:
    """Configuration for anomaly detection."""
    methods: List[str] = field(default_factory=lambda: ['statistical', 'isolation_forest', 'local_outlier'])
    contamination: float = 0.1  # Expected proportion of anomalies
    threshold: float = 0.5  # Anomaly score threshold
    features: List[str] = field(default_factory=list)
    temporal_window: float = 7.0  # Days for temporal analysis
    min_entities: int = 10  # Minimum number of entities for detection
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'methods': self.methods,
            'contamination': self.contamination,
            'threshold': self.threshold,
            'features': self.features,
            'temporal_window': self.temporal_window,
            'min_entities': self.min_entities,
        }


class AnomalyDetector:
    """
    Anomaly detector for OpenLens.
    
    Provides multiple anomaly detection methods:
    - Statistical (z-score, IQR)
    - Isolation Forest
    - Local Outlier Factor
    - DBSCAN
    - Graph-based
    - Temporal
    """
    
    def __init__(self, graph_engine=None, config: AnomalyDetectionConfig = None):
        """
        Initialize the anomaly detector.
        
        Args:
            graph_engine: GraphEngine instance.
            config: AnomalyDetectionConfig.
        """
        self.graph_engine = graph_engine
        self.config = config or AnomalyDetectionConfig()
        self._scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self._models = {}
    
    def detect_anomalies(self, data: List[Dict[str, Any]], 
                        method: str = None) -> AnomalyDetectionResult:
        """
        Detect anomalies in data.
        
        Args:
            data: List of dictionaries with entity data.
            method: Specific method to use (None for all methods).
            
        Returns:
            AnomalyDetectionResult.
        """
        start_time = time.time()
        
        methods = [method] if method else self.config.methods
        all_anomalies = []
        total_entities = len(data)
        
        for method in methods:
            if method == 'statistical':
                anomalies = self._detect_statistical_anomalies(data)
            elif method == 'isolation_forest':
                anomalies = self._detect_isolation_forest_anomalies(data)
            elif method == 'local_outlier':
                anomalies = self._detect_local_outlier_anomalies(data)
            elif method == 'dbscan':
                anomalies = self._detect_dbscan_anomalies(data)
            elif method == 'graph':
                anomalies = self._detect_graph_anomalies(data)
            elif method == 'temporal':
                anomalies = self._detect_temporal_anomalies(data)
            else:
                continue
            
            all_anomalies.extend(anomalies)
        
        execution_time = time.time() - start_time
        
        return AnomalyDetectionResult(
            method=', '.join(methods),
            anomalies=all_anomalies,
            total_entities=total_entities,
            anomalous_entities=len(all_anomalies),
            execution_time=execution_time,
        )
    
    def _detect_statistical_anomalies(self, data: List[Dict[str, Any]]) -> List[Anomaly]:
        """Detect anomalies using statistical methods."""
        if not data or len(data) < self.config.min_entities:
            return []
        
        anomalies = []
        
        try:
            # Extract features
            features = self.config.features or list(data[0].keys())
            
            for feature in features:
                if feature not in ['id', 'entity_id', 'entity_type', 'timestamp']:
                    values = [d.get(feature, 0) for d in data if isinstance(d.get(feature), (int, float))]
                    
                    if len(values) < self.config.min_entities:
                        continue
                    
                    # Calculate statistics
                    mean = sum(values) / len(values)
                    std = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
                    
                    # Z-score method
                    for i, d in enumerate(data):
                        if feature in d and isinstance(d[feature], (int, float)):
                            z_score = (d[feature] - mean) / std if std > 0 else 0
                            
                            if abs(z_score) > 3:  # 3 standard deviations
                                anomalies.append(Anomaly(
                                    anomaly_id=f"stat_{feature}_{i}",
                                    entity_id=d.get('id', str(i)),
                                    entity_type=d.get('entity_type', 'node'),
                                    score=abs(z_score),
                                    features={feature: d[feature]},
                                    timestamp=d.get('timestamp'),
                                    method='z_score',
                                    explanation=f"Value {d[feature]} is {abs(z_score):.2f} standard deviations from mean",
                                    severity='high' if abs(z_score) > 4 else 'medium',
                                ))
                    
                    # IQR method
                    sorted_values = sorted(values)
                    q1 = sorted_values[len(sorted_values) // 4]
                    q3 = sorted_values[3 * len(sorted_values) // 4]
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    for i, d in enumerate(data):
                        if feature in d and isinstance(d[feature], (int, float)):
                            if d[feature] < lower_bound or d[feature] > upper_bound:
                                anomalies.append(Anomaly(
                                    anomaly_id=f"iqr_{feature}_{i}",
                                    entity_id=d.get('id', str(i)),
                                    entity_type=d.get('entity_type', 'node'),
                                    score=1.0,
                                    features={feature: d[feature]},
                                    timestamp=d.get('timestamp'),
                                    method='iqr',
                                    explanation=f"Value {d[feature]} is outside IQR range [{lower_bound:.2f}, {upper_bound:.2f}]",
                                    severity='high',
                                ))
        
        except Exception as e:
            print(f"Statistical anomaly detection error: {e}")
        
        return anomalies
    
    def _detect_isolation_forest_anomalies(self, data: List[Dict[str, Any]]) -> List[Anomaly]:
        """Detect anomalies using Isolation Forest."""
        if not SKLEARN_AVAILABLE or not data or len(data) < self.config.min_entities:
            return []
        
        anomalies = []
        
        try:
            # Extract features
            features = self.config.features or list(data[0].keys())
            features = [f for f in features if f not in ['id', 'entity_id', 'entity_type', 'timestamp']]
            
            if not features:
                return []
            
            # Prepare data
            X = []
            for d in data:
                row = [d.get(f, 0) for f in features if isinstance(d.get(f), (int, float))]
                if len(row) == len(features):
                    X.append(row)
            
            if len(X) < self.config.min_entities:
                return []
            
            # Scale data
            X_scaled = self._scaler.fit_transform(X)
            
            # Train model
            model = IsolationForest(
                n_estimators=100,
                contamination=self.config.contamination,
                random_state=42
            )
            model.fit(X_scaled)
            
            # Predict anomalies
            scores = model.decision_function(X_scaled)
            preds = model.predict(X_scaled)
            
            for i, (d, score, pred) in enumerate(zip(data, scores, preds)):
                if pred == -1:  # Anomaly
                    anomalies.append(Anomaly(
                        anomaly_id=f"if_{i}",
                        entity_id=d.get('id', str(i)),
                        entity_type=d.get('entity_type', 'node'),
                        score=float(score),
                        features={f: d.get(f, 0) for f in features},
                        timestamp=d.get('timestamp'),
                        method='isolation_forest',
                        explanation=f"Isolation Forest detected anomaly with score {score:.4f}",
                        severity='high' if score < -0.5 else 'medium',
                    ))
        
        except Exception as e:
            print(f"Isolation Forest anomaly detection error: {e}")
        
        return anomalies
    
    def _detect_local_outlier_anomalies(self, data: List[Dict[str, Any]]) -> List[Anomaly]:
        """Detect anomalies using Local Outlier Factor."""
        if not SKLEARN_AVAILABLE or not data or len(data) < self.config.min_entities:
            return []
        
        anomalies = []
        
        try:
            # Extract features
            features = self.config.features or list(data[0].keys())
            features = [f for f in features if f not in ['id', 'entity_id', 'entity_type', 'timestamp']]
            
            if not features:
                return []
            
            # Prepare data
            X = []
            for d in data:
                row = [d.get(f, 0) for f in features if isinstance(d.get(f), (int, float))]
                if len(row) == len(features):
                    X.append(row)
            
            if len(X) < self.config.min_entities:
                return []
            
            # Scale data
            X_scaled = self._scaler.fit_transform(X)
            
            # Train model
            model = LocalOutlierFactor(
                n_neighbors=20,
                contamination=self.config.contamination
            )
            model.fit(X_scaled)
            
            # Predict anomalies
            scores = -model.negative_outlier_factor_
            preds = model.predict(X_scaled)
            
            for i, (d, score, pred) in enumerate(zip(data, scores, preds)):
                if pred == -1:  # Anomaly
                    anomalies.append(Anomaly(
                        anomaly_id=f"lof_{i}",
                        entity_id=d.get('id', str(i)),
                        entity_type=d.get('entity_type', 'node'),
                        score=float(score),
                        features={f: d.get(f, 0) for f in features},
                        timestamp=d.get('timestamp'),
                        method='local_outlier_factor',
                        explanation=f"Local Outlier Factor detected anomaly with score {score:.4f}",
                        severity='high' if score > 2 else 'medium',
                    ))
        
        except Exception as e:
            print(f"Local Outlier Factor error: {e}")
        
        return anomalies
    
    def _detect_dbscan_anomalies(self, data: List[Dict[str, Any]]) -> List[Anomaly]:
        """Detect anomalies using DBSCAN."""
        if not SKLEARN_AVAILABLE or not data or len(data) < self.config.min_entities:
            return []
        
        anomalies = []
        
        try:
            # Extract features
            features = self.config.features or list(data[0].keys())
            features = [f for f in features if f not in ['id', 'entity_id', 'entity_type', 'timestamp']]
            
            if not features:
                return []
            
            # Prepare data
            X = []
            for d in data:
                row = [d.get(f, 0) for f in features if isinstance(d.get(f), (int, float))]
                if len(row) == len(features):
                    X.append(row)
            
            if len(X) < self.config.min_entities:
                return []
            
            # Scale data
            X_scaled = self._scaler.fit_transform(X)
            
            # Train model
            model = DBSCAN(
                eps=0.5,
                min_samples=5
            )
            model.fit(X_scaled)
            
            # Find anomalies (noise points)
            for i, (d, label) in enumerate(zip(data, model.labels_)):
                if label == -1:  # Noise/outlier
                    anomalies.append(Anomaly(
                        anomaly_id=f"dbscan_{i}",
                        entity_id=d.get('id', str(i)),
                        entity_type=d.get('entity_type', 'node'),
                        score=1.0,
                        features={f: d.get(f, 0) for f in features},
                        timestamp=d.get('timestamp'),
                        method='dbscan',
                        explanation="DBSCAN identified as noise/outlier",
                        severity='medium',
                    ))
        
        except Exception as e:
            print(f"DBSCAN anomaly detection error: {e}")
        
        return anomalies
    
    def _detect_graph_anomalies(self, data: List[Dict[str, Any]]) -> List[Anomaly]:
        """Detect anomalies using graph-based methods."""
        if not self.graph_engine or not data:
            return []
        
        anomalies = []
        
        try:
            # Get graph data
            graph = self.graph_engine._get_networkx_graph()
            if not graph:
                return []
            
            # Calculate centrality metrics
            degree_centrality = nx.degree_centrality(graph)
            betweenness_centrality = nx.betweenness_centrality(graph)
            
            # Find nodes with unusually high centrality
            degree_values = list(degree_centrality.values())
            mean_degree = sum(degree_values) / len(degree_values)
            std_degree = (sum((x - mean_degree) ** 2 for x in degree_values) / len(degree_values)) ** 0.5
            
            for node in graph.nodes():
                degree = degree_centrality.get(node, 0)
                z_score = (degree - mean_degree) / std_degree if std_degree > 0 else 0
                
                if abs(z_score) > 3:
                    anomalies.append(Anomaly(
                        anomaly_id=f"graph_degree_{node}",
                        entity_id=str(node),
                        entity_type='node',
                        score=abs(z_score),
                        features={'degree_centrality': degree},
                        method='graph_degree_centrality',
                        explanation=f"Node has unusually high degree centrality (z-score: {z_score:.2f})",
                        severity='high' if abs(z_score) > 4 else 'medium',
                    ))
            
            # Find nodes with unusually high betweenness
            betweenness_values = list(betweenness_centrality.values())
            mean_betweenness = sum(betweenness_values) / len(betweenness_values)
            std_betweenness = (sum((x - mean_betweenness) ** 2 for x in betweenness_values) / len(betweenness_values)) ** 0.5
            
            for node in graph.nodes():
                betweenness = betweenness_centrality.get(node, 0)
                z_score = (betweenness - mean_betweenness) / std_betweenness if std_betweenness > 0 else 0
                
                if abs(z_score) > 3:
                    anomalies.append(Anomaly(
                        anomaly_id=f"graph_betweenness_{node}",
                        entity_id=str(node),
                        entity_type='node',
                        score=abs(z_score),
                        features={'betweenness_centrality': betweenness},
                        method='graph_betweenness_centrality',
                        explanation=f"Node has unusually high betweenness centrality (z-score: {z_score:.2f})",
                        severity='high' if abs(z_score) > 4 else 'medium',
                    ))
        
        except Exception as e:
            print(f"Graph anomaly detection error: {e}")
        
        return anomalies
    
    def _detect_temporal_anomalies(self, data: List[Dict[str, Any]]) -> List[Anomaly]:
        """Detect anomalies using temporal methods."""
        if not data or len(data) < self.config.min_entities:
            return []
        
        anomalies = []
        
        try:
            # Group data by entity
            entity_data = defaultdict(list)
            for d in data:
                entity_id = d.get('id', d.get('entity_id'))
                if entity_id:
                    entity_data[entity_id].append(d)
            
            # Detect temporal anomalies for each entity
            for entity_id, entity_records in entity_data.items():
                if len(entity_records) < 3:
                    continue
                
                # Sort by timestamp
                entity_records.sort(key=lambda x: x.get('timestamp') or datetime.min)
                
                # Calculate time intervals
                intervals = []
                for i in range(1, len(entity_records)):
                    try:
                        ts1 = entity_records[i-1].get('timestamp')
                        ts2 = entity_records[i].get('timestamp')
                        if ts1 and ts2:
                            interval = (ts2 - ts1).total_seconds() / 86400  # in days
                            intervals.append(interval)
                    except:
                        continue
                
                if len(intervals) < 2:
                    continue
                
                # Calculate statistics
                mean_interval = sum(intervals) / len(intervals)
                std_interval = (sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)) ** 0.5
                
                # Find anomalous intervals
                for i, interval in enumerate(intervals):
                    z_score = (interval - mean_interval) / std_interval if std_interval > 0 else 0
                    
                    if abs(z_score) > 3:
                        anomalies.append(Anomaly(
                            anomaly_id=f"temporal_{entity_id}_{i}",
                            entity_id=entity_id,
                            entity_type=entity_records[i].get('entity_type', 'node'),
                            score=abs(z_score),
                            features={'interval': interval, 'mean_interval': mean_interval},
                            timestamp=entity_records[i].get('timestamp'),
                            method='temporal_interval',
                            explanation=f"Unusually {'long' if z_score > 0 else 'short'} interval between events (z-score: {z_score:.2f})",
                            severity='high' if abs(z_score) > 4 else 'medium',
                        ))
        
        except Exception as e:
            print(f"Temporal anomaly detection error: {e}")
        
        return anomalies
    
    def detect_graph_anomalies(self) -> AnomalyDetectionResult:
        """
        Detect anomalies in the graph structure.
        
        Returns:
            AnomalyDetectionResult.
        """
        if not self.graph_engine:
            return AnomalyDetectionResult(method='graph')
        
        start_time = time.time()
        
        try:
            # Get all nodes
            query = "MATCH (n) RETURN n"
            result = self.graph_engine.execute_query(query)
            
            if not result:
                return AnomalyDetectionResult(method='graph')
            
            data = []
            for node in result.nodes:
                data.append({
                    'id': node.node_id,
                    'entity_type': 'node',
                    'labels': node.labels,
                    **node.properties
                })
            
            # Detect anomalies
            result = self.detect_anomalies(data, method='graph')
            result.method = 'graph'
            result.execution_time = time.time() - start_time
            
            return result
        
        except Exception as e:
            print(f"Graph anomaly detection error: {e}")
            return AnomalyDetectionResult(method='graph')
    
    def detect_temporal_anomalies(self) -> AnomalyDetectionResult:
        """
        Detect temporal anomalies.
        
        Returns:
            AnomalyDetectionResult.
        """
        if not self.graph_engine:
            return AnomalyDetectionResult(method='temporal')
        
        start_time = time.time()
        
        try:
            # Get all nodes with timestamps
            query = "MATCH (n) WHERE EXISTS(n.timestamp) RETURN n"
            result = self.graph_engine.execute_query(query)
            
            if not result:
                return AnomalyDetectionResult(method='temporal')
            
            data = []
            for node in result.nodes:
                data.append({
                    'id': node.node_id,
                    'entity_type': 'node',
                    'timestamp': node.properties.get('timestamp'),
                    **node.properties
                })
            
            # Detect anomalies
            result = self.detect_anomalies(data, method='temporal')
            result.method = 'temporal'
            result.execution_time = time.time() - start_time
            
            return result
        
        except Exception as e:
            print(f"Temporal anomaly detection error: {e}")
            return AnomalyDetectionResult(method='temporal')
    
    def get_anomaly_summary(self) -> Dict[str, Any]:
        """
        Get a summary of detected anomalies.
        
        Returns:
            Summary dictionary.
        """
        if not self.graph_engine:
            return {}
        
        try:
            # Detect all types of anomalies
            graph_result = self.detect_graph_anomalies()
            temporal_result = self.detect_temporal_anomalies()
            
            return {
                'graph_anomalies': graph_result.to_dict(),
                'temporal_anomalies': temporal_result.to_dict(),
                'total_anomalies': len(graph_result.anomalies) + len(temporal_result.anomalies),
                'high_severity': len([a for a in graph_result.anomalies if a.severity == 'high']) +
                               len([a for a in temporal_result.anomalies if a.severity == 'high']),
                'medium_severity': len([a for a in graph_result.anomalies if a.severity == 'medium']) +
                                  len([a for a in temporal_result.anomalies if a.severity == 'medium']),
            }
        
        except Exception as e:
            print(f"Anomaly summary error: {e}")
            return {}


# Global anomaly detector instance
anomaly_detector = AnomalyDetector()
