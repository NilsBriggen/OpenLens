"""
Predictive Analytics Module for OpenLens

Provides predictive analytics capabilities:
- Link prediction
- Node classification
- Graph evolution prediction
- Threat prediction
- Risk scoring
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
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not available. Install with: pip install scikit-learn")

# Try to import networkx
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("NetworkX not available. Install with: pip install networkx")

# Try to import node2vec
try:
    from node2vec import Node2Vec
    NODE2VEC_AVAILABLE = True
except ImportError:
    NODE2VEC_AVAILABLE = False
    print("node2vec not available. Install with: pip install node2vec")

# Try to import karateclub
try:
    from karateclub import Graph2Vec, Walklets
    KARATECLUB_AVAILABLE = True
except ImportError:
    KARATECLUB_AVAILABLE = False
    print("karateclub not available. Install with: pip install karateclub")


@dataclass
class Prediction:
    """Represents a prediction."""
    prediction_id: str
    entity_id: str
    prediction_type: str  # link, classification, evolution, threat
    predicted_value: Any
    probability: float = 0.0
    features: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = None
    method: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'prediction_id': self.prediction_id,
            'entity_id': self.entity_id,
            'prediction_type': self.prediction_type,
            'predicted_value': self.predicted_value,
            'probability': self.probability,
            'features': self.features,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'method': self.method,
        }


@dataclass
class PredictionResult:
    """Result of predictive analytics."""
    method: str
    predictions: List[Prediction] = field(default_factory=list)
    total_predictions: int = 0
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'method': self.method,
            'predictions': [p.to_dict() for p in self.predictions],
            'total_predictions': self.total_predictions,
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'execution_time': self.execution_time,
        }


@dataclass
class PredictionConfig:
    """Configuration for predictive analytics."""
    methods: List[str] = field(default_factory=lambda: ['random_forest', 'logistic_regression'])
    test_size: float = 0.2
    random_state: int = 42
    n_estimators: int = 100
    max_depth: int = 10
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'methods': self.methods,
            'test_size': self.test_size,
            'random_state': self.random_state,
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
        }


class PredictiveAnalyzer:
    """
    Predictive analyzer for OpenLens.
    
    Provides predictive analytics capabilities:
    - Link prediction
    - Node classification
    - Graph evolution prediction
    - Threat prediction
    """
    
    def __init__(self, graph_engine=None, config: PredictionConfig = None):
        """
        Initialize the predictive analyzer.
        
        Args:
            graph_engine: GraphEngine instance.
            config: PredictionConfig.
        """
        self.graph_engine = graph_engine
        self.config = config or PredictionConfig()
        self._scaler = StandardScaler() if SKLEARN_AVAILABLE else None
        self._label_encoder = LabelEncoder() if SKLEARN_AVAILABLE else None
        self._models = {}
    
    def predict_links(self, method: str = None) -> PredictionResult:
        """
        Predict future links in the graph.
        
        Args:
            method: Specific method to use.
            
        Returns:
            PredictionResult.
        """
        if not self.graph_engine or not NETWORKX_AVAILABLE:
            return PredictionResult(method='link_prediction')
        
        start_time = time.time()
        
        try:
            # Get graph
            graph = self.graph_engine._get_networkx_graph()
            if not graph:
                return PredictionResult(method='link_prediction')
            
            # Generate negative samples (non-existent links)
            non_edges = list(nx.non_edges(graph))
            
            if len(non_edges) < 100:
                return PredictionResult(method='link_prediction')
            
            # Sample a subset for efficiency
            import random
            random.seed(self.config.random_state)
            sampled_non_edges = random.sample(non_edges, min(1000, len(non_edges)))
            
            # Prepare data
            X = []
            y = []
            
            # Positive samples (existing edges)
            for u, v in list(graph.edges())[:1000]:
                features = self._extract_link_features(graph, u, v)
                X.append(features)
                y.append(1)  # Positive
            
            # Negative samples (non-existing edges)
            for u, v in sampled_non_edges:
                features = self._extract_link_features(graph, u, v)
                X.append(features)
                y.append(0)  # Negative
            
            if len(X) < 10:
                return PredictionResult(method='link_prediction')
            
            # Train model
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.config.test_size, random_state=self.config.random_state
            )
            
            if SKLEARN_AVAILABLE:
                if method == 'random_forest' or not method:
                    model = RandomForestClassifier(
                        n_estimators=self.config.n_estimators,
                        max_depth=self.config.max_depth,
                        random_state=self.config.random_state
                    )
                elif method == 'logistic_regression':
                    model = LogisticRegression(random_state=self.config.random_state)
                elif method == 'svm':
                    model = SVC(probability=True, random_state=self.config.random_state)
                else:
                    model = RandomForestClassifier(
                        n_estimators=self.config.n_estimators,
                        max_depth=self.config.max_depth,
                        random_state=self.config.random_state
                    )
                
                model.fit(X_train, y_train)
                
                # Evaluate
                y_pred = model.predict(X_test)
                y_proba = model.predict_proba(X_test)
                
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, zero_division=0)
                recall = recall_score(y_test, y_pred, zero_division=0)
                f1 = f1_score(y_test, y_pred, zero_division=0)
                
                # Predict on all non-edges
                predictions = []
                for u, v in sampled_non_edges:
                    features = self._extract_link_features(graph, u, v)
                    proba = model.predict_proba([features])[0][1]
                    
                    if proba > 0.5:  # Threshold
                        predictions.append(Prediction(
                            prediction_id=f"link_{u}_{v}",
                            entity_id=f"{u}_{v}",
                            prediction_type='link',
                            predicted_value=(u, v),
                            probability=proba,
                            features={'nodes': [u, v]},
                            method=method or 'random_forest',
                        ))
                
                execution_time = time.time() - start_time
                
                return PredictionResult(
                    method=method or 'random_forest',
                    predictions=predictions,
                    total_predictions=len(predictions),
                    accuracy=accuracy,
                    precision=precision,
                    recall=recall,
                    f1_score=f1,
                    execution_time=execution_time,
                )
        
        except Exception as e:
            print(f"Link prediction error: {e}")
            return PredictionResult(method='link_prediction')
    
    # Column order of the feature matrix fed to the sklearn models. Named so
    # per-metric accessors index by key, never by position - a positional slip
    # here once made metrics silently interchangeable.
    _FEATURE_ORDER = ('degree_u', 'degree_v', 'common_neighbors', 'jaccard',
                      'preferential_attachment', 'adamic_adar', 'distance')

    def _link_features(self, graph: "nx.Graph", u: str, v: str) -> Dict[str, float]:
        """Named link-prediction features for a node pair."""
        features = {name: 0.0 for name in self._FEATURE_ORDER}
        features['distance'] = 100.0

        try:
            degree_u = graph.degree(u)
            degree_v = graph.degree(v)
            neighbors_u = set(graph.neighbors(u))
            neighbors_v = set(graph.neighbors(v))
            common = neighbors_u & neighbors_v
            union = len(neighbors_u | neighbors_v)

            features['degree_u'] = float(degree_u)
            features['degree_v'] = float(degree_v)
            features['common_neighbors'] = float(len(common))
            features['jaccard'] = len(common) / union if union > 0 else 0.0
            features['preferential_attachment'] = float(degree_u * degree_v)
            features['adamic_adar'] = sum(
                1.0 / math.log(graph.degree(n) + 1) for n in common
                if graph.degree(n) > 0
            )

            try:
                if graph.has_edge(u, v):
                    features['distance'] = 1.0
                else:
                    features['distance'] = float(nx.shortest_path_length(graph, u, v))
            except Exception:
                features['distance'] = 100.0
        except Exception as e:
            print(f"Feature extraction error: {e}")

        return features

    def _extract_link_features(self, graph: "nx.Graph", u: str, v: str) -> List[float]:
        """Feature vector in _FEATURE_ORDER (for the model pipelines)."""
        named = self._link_features(graph, u, v)
        return [named[key] for key in self._FEATURE_ORDER]

    def _link_metric(self, node_1: str, node_2: str, key: str) -> float:
        """One named metric for a pair, from the live graph."""
        if not NETWORKX_AVAILABLE or not self.graph_engine:
            return 0.0
        graph = self.graph_engine.to_networkx()
        if graph is None or node_1 not in graph or node_2 not in graph:
            return 0.0
        return self._link_features(graph, node_1, node_2)[key]

    def predict_link_common_neighbors(self, node_1: str, node_2: str) -> float:
        """Common-neighbours score for a node pair."""
        return self._link_metric(node_1, node_2, 'common_neighbors')

    def predict_link_jaccard(self, node_1: str, node_2: str) -> float:
        """Jaccard coefficient for a node pair."""
        return self._link_metric(node_1, node_2, 'jaccard')

    def predict_link_adamic_adar(self, node_1: str, node_2: str) -> float:
        """Adamic-Adar index for a node pair."""
        return self._link_metric(node_1, node_2, 'adamic_adar')

    def predict_link_preferential_attachment(self, node_1: str, node_2: str) -> float:
        """Preferential-attachment score for a node pair."""
        return self._link_metric(node_1, node_2, 'preferential_attachment')

    _LINK_METHODS = {
        'common_neighbors': 'common_neighbors',
        'jaccard': 'jaccard',
        'adamic_adar': 'adamic_adar',
        'preferential_attachment': 'preferential_attachment',
    }

    def score_link(self, node_1: str, node_2: str,
                   method: str = 'common_neighbors') -> float:
        """
        One-call per-pair link score.

        Raises:
            ValueError: For an unknown method.
        """
        key = self._LINK_METHODS.get(method)
        if key is None:
            raise ValueError(
                f"unknown link method {method!r}; "
                f"allowed: {sorted(self._LINK_METHODS)}")
        return self._link_metric(node_1, node_2, key)

    def predict_node_classification(self, node_id: str,
                                    features: Dict[str, float] = None,
                                    method: str = 'random_forest',
                                    label_attribute: str = 'label') -> Optional[Prediction]:
        """
        Predict the label of a single node.

        Trains via predict_node_labels (whole-graph) and picks out this node's
        prediction. The features argument is accepted for API compatibility
        and recorded on the result, but training features come from the graph.

        Returns:
            Prediction for the node, or None when the node is absent or the
            model could not be trained.
        """
        result = self.predict_node_labels(label_attribute=label_attribute,
                                          method=method)
        if not result or not result.predictions:
            return None

        for prediction in result.predictions:
            if prediction.entity_id == node_id:
                if features:
                    prediction.features = {**prediction.features, **features}
                return prediction
        return None
    
    def predict_node_labels(self, label_attribute: str = 'label', 
                           method: str = None) -> PredictionResult:
        """
        Predict node labels.
        
        Args:
            label_attribute: Attribute to predict.
            method: Specific method to use.
            
        Returns:
            PredictionResult.
        """
        if not self.graph_engine or not NETWORKX_AVAILABLE or not SKLEARN_AVAILABLE:
            return PredictionResult(method='node_classification')
        
        start_time = time.time()
        
        try:
            # Get graph
            graph = self.graph_engine._get_networkx_graph()
            if not graph:
                return PredictionResult(method='node_classification')
            
            # Check if label attribute exists
            has_label = False
            for node in graph.nodes():
                if label_attribute in graph.nodes[node]:
                    has_label = True
                    break
            
            if not has_label:
                return PredictionResult(method='node_classification')
            
            # Prepare data
            X = []
            y = []
            node_ids = []
            
            for node in graph.nodes():
                if label_attribute in graph.nodes[node]:
                    features = self._extract_node_features(graph, node)
                    label = graph.nodes[node][label_attribute]
                    
                    X.append(features)
                    y.append(label)
                    node_ids.append(node)
            
            if len(X) < 10:
                return PredictionResult(method='node_classification')
            
            # Encode labels
            y_encoded = self._label_encoder.fit_transform(y)
            
            # Train model
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=self.config.test_size, random_state=self.config.random_state
            )
            
            if method == 'random_forest' or not method:
                model = RandomForestClassifier(
                    n_estimators=self.config.n_estimators,
                    max_depth=self.config.max_depth,
                    random_state=self.config.random_state
                )
            elif method == 'logistic_regression':
                model = LogisticRegression(random_state=self.config.random_state)
            elif method == 'svm':
                model = SVC(probability=True, random_state=self.config.random_state)
            else:
                model = RandomForestClassifier(
                    n_estimators=self.config.n_estimators,
                    max_depth=self.config.max_depth,
                    random_state=self.config.random_state
                )
            
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            y_proba = model.predict_proba(X_test)
            
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            # Predict on all nodes
            predictions = []
            for i, node in enumerate(node_ids):
                proba = model.predict_proba([X[i]])[0]
                max_proba = max(proba)
                predicted_label = self._label_encoder.inverse_transform([np.argmax(proba)])[0]
                
                predictions.append(Prediction(
                    prediction_id=f"label_{node}",
                    entity_id=node,
                    prediction_type='classification',
                    predicted_value=predicted_label,
                    probability=max_proba,
                    features={'actual_label': y[i]},
                    method=method or 'random_forest',
                ))
            
            execution_time = time.time() - start_time
            
            return PredictionResult(
                method=method or 'random_forest',
                predictions=predictions,
                total_predictions=len(predictions),
                accuracy=accuracy,
                precision=precision,
                recall=recall,
                f1_score=f1,
                execution_time=execution_time,
            )
        
        except Exception as e:
            print(f"Node classification error: {e}")
            return PredictionResult(method='node_classification')
    
    def _extract_node_features(self, graph: nx.Graph, node: str) -> List[float]:
        """Extract features for node classification."""
        features = []
        
        try:
            # Degree features
            degree = graph.degree(node)
            features.append(degree)
            
            # Centrality features
            degree_centrality = nx.degree_centrality(graph).get(node, 0)
            betweenness_centrality = nx.betweenness_centrality(graph).get(node, 0)
            closeness_centrality = nx.closeness_centrality(graph).get(node, 0)
            
            features.extend([degree_centrality, betweenness_centrality, closeness_centrality])
            
            # Clustering coefficient
            clustering = nx.clustering(graph).get(node, 0)
            features.append(clustering)
            
            # Number of triangles
            triangles = nx.triangles(graph).get(node, 0)
            features.append(triangles)
            
            # PageRank
            pagerank = nx.pagerank(graph).get(node, 0)
            features.append(pagerank)
        
        except Exception as e:
            print(f"Node feature extraction error: {e}")
            features = [0, 0, 0, 0, 0, 0, 0]
        
        return features
    
    def predict_graph_evolution(self, steps: int = 5) -> PredictionResult:
        """
        Predict graph evolution.
        
        Args:
            steps: Number of evolution steps to predict.
            
        Returns:
            PredictionResult.
        """
        if not self.graph_engine or not NETWORKX_AVAILABLE:
            return PredictionResult(method='graph_evolution')
        
        start_time = time.time()
        
        try:
            # Get temporal graph
            from ..graph.temporal_analysis import TemporalAnalyzer
            temporal_analyzer = TemporalAnalyzer(self.graph_engine)
            temporal_graph = temporal_analyzer.get_temporal_graph()
            
            if not temporal_graph:
                return PredictionResult(method='graph_evolution')
            
            # Get evolution data
            evolution = temporal_analyzer.get_temporal_evolution(num_slices=10)
            
            if not evolution or len(evolution) < 3:
                return PredictionResult(method='graph_evolution')
            
            # Prepare time series data
            X = []
            y_nodes = []
            y_edges = []
            
            for i, slice_data in enumerate(evolution):
                if i >= 2:  # Need at least 2 previous points
                    # Use previous 2 slices as features
                    X.append([
                        evolution[i-2]['num_nodes'],
                        evolution[i-2]['num_edges'],
                        evolution[i-1]['num_nodes'],
                        evolution[i-1]['num_edges'],
                    ])
                    y_nodes.append(slice_data['num_nodes'])
                    y_edges.append(slice_data['num_edges'])
            
            if len(X) < 3:
                return PredictionResult(method='graph_evolution')
            
            # Train models
            if SKLEARN_AVAILABLE:
                model_nodes = RandomForestRegressor(
                    n_estimators=self.config.n_estimators,
                    max_depth=self.config.max_depth,
                    random_state=self.config.random_state
                )
                model_edges = RandomForestRegressor(
                    n_estimators=self.config.n_estimators,
                    max_depth=self.config.max_depth,
                    random_state=self.config.random_state
                )
                
                model_nodes.fit(X, y_nodes)
                model_edges.fit(X, y_edges)
                
                # Predict future evolution
                predictions = []
                last_X = X[-1]
                
                for step in range(steps):
                    # Predict next step
                    next_nodes = model_nodes.predict([last_X])[0]
                    next_edges = model_edges.predict([last_X])[0]
                    
                    predictions.append(Prediction(
                        prediction_id=f"evolution_{step}",
                        entity_id=f"step_{step}",
                        prediction_type='evolution',
                        predicted_value={'num_nodes': int(next_nodes), 'num_edges': int(next_edges)},
                        probability=1.0,
                        features={'step': step},
                        method='random_forest',
                    ))
                    
                    # Update last_X for next prediction
                    last_X = [last_X[1], last_X[2], last_X[3], next_nodes, next_edges]
                    if len(last_X) > 4:
                        last_X = last_X[-4:]
                
                execution_time = time.time() - start_time
                
                return PredictionResult(
                    method='random_forest',
                    predictions=predictions,
                    total_predictions=len(predictions),
                    execution_time=execution_time,
                )
        
        except Exception as e:
            print(f"Graph evolution prediction error: {e}")
            return PredictionResult(method='graph_evolution')
    
    def predict_threats(self, method: str = None) -> PredictionResult:
        """
        Predict potential threats.
        
        Args:
            method: Specific method to use.
            
        Returns:
            PredictionResult.
        """
        if not self.graph_engine:
            return PredictionResult(method='threat_prediction')
        
        start_time = time.time()
        
        try:
            # Get all nodes
            query = "MATCH (n) RETURN n"
            result = self.graph_engine.execute_query(query)
            
            if not result:
                return PredictionResult(method='threat_prediction')
            
            # Prepare data
            X = []
            y = []
            node_ids = []
            
            for node in result.nodes:
                features = self._extract_threat_features(node)
                
                # Check if node is marked as threat (simple heuristic)
                is_threat = 0
                if 'threat' in node.labels or node.properties.get('is_threat', False):
                    is_threat = 1
                
                X.append(features)
                y.append(is_threat)
                node_ids.append(node.node_id)
            
            if len(X) < 10 or sum(y) == 0:
                return PredictionResult(method='threat_prediction')
            
            # Train model
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.config.test_size, random_state=self.config.random_state
            )
            
            if SKLEARN_AVAILABLE:
                if method == 'random_forest' or not method:
                    model = RandomForestClassifier(
                        n_estimators=self.config.n_estimators,
                        max_depth=self.config.max_depth,
                        random_state=self.config.random_state
                    )
                elif method == 'logistic_regression':
                    model = LogisticRegression(random_state=self.config.random_state)
                else:
                    model = RandomForestClassifier(
                        n_estimators=self.config.n_estimators,
                        max_depth=self.config.max_depth,
                        random_state=self.config.random_state
                    )
                
                model.fit(X_train, y_train)
                
                # Evaluate
                y_pred = model.predict(X_test)
                y_proba = model.predict_proba(X_test)
                
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, zero_division=0)
                recall = recall_score(y_test, y_pred, zero_division=0)
                f1 = f1_score(y_test, y_pred, zero_division=0)
                
                # Predict on all nodes
                predictions = []
                for i, node_id in enumerate(node_ids):
                    proba = model.predict_proba([X[i]])[0][1]
                    
                    if proba > 0.5:
                        predictions.append(Prediction(
                            prediction_id=f"threat_{node_id}",
                            entity_id=node_id,
                            prediction_type='threat',
                            predicted_value='threat',
                            probability=proba,
                            features={},
                            method=method or 'random_forest',
                        ))
                
                execution_time = time.time() - start_time
                
                return PredictionResult(
                    method=method or 'random_forest',
                    predictions=predictions,
                    total_predictions=len(predictions),
                    accuracy=accuracy,
                    precision=precision,
                    recall=recall,
                    f1_score=f1,
                    execution_time=execution_time,
                )
        
        except Exception as e:
            print(f"Threat prediction error: {e}")
            return PredictionResult(method='threat_prediction')
    
    def _extract_threat_features(self, node) -> List[float]:
        """Extract features for threat prediction."""
        features = []
        
        try:
            # Count suspicious labels
            suspicious_labels = ['Malware', 'ThreatActor', 'Vulnerability', 'Attack', 'Exploit']
            has_suspicious = 1 if any(label in node.labels for label in suspicious_labels) else 0
            features.append(has_suspicious)
            
            # Count connections to suspicious nodes
            suspicious_connections = 0
            if self.graph_engine:
                query = f"MATCH (n)-[r]->(m) WHERE n.id = '{node.node_id}' AND ANY(label IN m.labels WHERE label IN ['Malware', 'ThreatActor', 'Vulnerability', 'Attack', 'Exploit']) RETURN count(m)"
                result = self.graph_engine.execute_query(query)
                if result and result.nodes:
                    suspicious_connections = int(result.nodes[0].properties.get('count(m)', 0))
            features.append(suspicious_connections)
            
            # Check for known threat indicators
            threat_indicators = ['malicious', 'suspicious', 'threat', 'attack', 'exploit', 'vulnerability']
            has_indicator = 1 if any(indicator in str(node.properties).lower() for indicator in threat_indicators) else 0
            features.append(has_indicator)
            
            # Node degree. size((n)--()) is Neo4j-4 syntax; COUNT {} is the
            # Neo4j 5 form, and the scalar arrives via .records, not .nodes.
            if self.graph_engine:
                query = "MATCH (n) WHERE n.id = $node_id RETURN COUNT { (n)--() } AS degree"
                records = self.graph_engine.execute_records(query, {'node_id': node.node_id})
                degree = int(records[0].get('degree', 0)) if records else 0
                features.append(degree)
            else:
                features.append(0)
            
            # Recent activity
            recent_activity = 0
            if 'timestamp' in node.properties:
                try:
                    ts = datetime.fromisoformat(node.properties['timestamp'])
                    if (datetime.utcnow() - ts).days < 7:
                        recent_activity = 1
                except:
                    pass
            features.append(recent_activity)
        
        except Exception as e:
            print(f"Threat feature extraction error: {e}")
            features = [0, 0, 0, 0, 0]
        
        return features
    
    def calculate_risk_scores(self) -> Dict[str, Any]:
        """
        Calculate risk scores for all entities.
        
        Returns:
            Dictionary with risk scores.
        """
        if not self.graph_engine:
            return {}
        
        try:
            # Get all nodes
            query = "MATCH (n) RETURN n"
            result = self.graph_engine.execute_query(query)
            
            if not result:
                return {}
            
            risk_scores = {}
            
            for node in result.nodes:
                score = self._calculate_entity_risk_score(node)
                risk_scores[node.node_id] = score
            
            return risk_scores
        
        except Exception as e:
            print(f"Risk score calculation error: {e}")
            return {}
    
    def _calculate_entity_risk_score(self, node) -> float:
        """Calculate risk score for an entity."""
        score = 0.0
        
        try:
            # Base score
            base_score = 10.0
            score += base_score
            
            # Suspicious labels
            suspicious_labels = ['Malware', 'ThreatActor', 'Vulnerability', 'Attack', 'Exploit']
            for label in node.labels:
                if label in suspicious_labels:
                    score += 30.0
            
            # Suspicious properties
            suspicious_keywords = ['malicious', 'suspicious', 'threat', 'attack', 'exploit', 'vulnerability']
            for key, value in node.properties.items():
                if any(keyword in str(value).lower() for keyword in suspicious_keywords):
                    score += 15.0
            
            # Connections to suspicious nodes
            if self.graph_engine:
                query = f"MATCH (n)-[r]->(m) WHERE n.id = '{node.node_id}' AND ANY(label IN m.labels WHERE label IN ['Malware', 'ThreatActor', 'Vulnerability', 'Attack', 'Exploit']) RETURN count(m)"
                result = self.graph_engine.execute_query(query)
                if result and result.nodes:
                    suspicious_connections = int(result.nodes[0].properties.get('count(m)', 0))
                    score += suspicious_connections * 10.0
            
            # Recent activity
            if 'timestamp' in node.properties:
                try:
                    ts = datetime.fromisoformat(node.properties['timestamp'])
                    days_old = (datetime.utcnow() - ts).days
                    if days_old < 7:
                        score += 5.0
                    elif days_old < 30:
                        score += 2.0
                except:
                    pass
            
            # Cap score at 100
            score = min(score, 100.0)
        
        except Exception as e:
            print(f"Entity risk score error: {e}")
        
        return score


# Global predictive analyzer instance
predictive_analyzer = PredictiveAnalyzer()
