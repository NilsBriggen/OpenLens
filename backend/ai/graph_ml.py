"""
Graph Machine Learning Module for OpenLens

Provides ML over the graph structure:
- Node embeddings (spectral; node2vec when installed)
- Node classification from structural features
- Per-pair link scoring via embedding similarity
- Node ranking (PageRank, degree, betweenness)
- Structural feature extraction
"""

import time
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

# Try to import networkx
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("NetworkX not available. Install with: pip install networkx")

# Try to import numpy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("NumPy not available. Install with: pip install numpy")

# Try to import scikit-learn
try:
    from sklearn.manifold import SpectralEmbedding
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not available. Install with: pip install scikit-learn")

# Try to import node2vec (optional; spectral is the default CPU path)
try:
    from node2vec import Node2Vec
    NODE2VEC_AVAILABLE = True
except ImportError:
    NODE2VEC_AVAILABLE = False


@dataclass
class NodeEmbedding:
    """Represents an embedding vector for one node."""
    node_id: str
    vector: List[float] = field(default_factory=list)
    method: str = ''
    dimensions: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'node_id': self.node_id,
            'vector': self.vector,
            'method': self.method,
            'dimensions': self.dimensions,
        }


@dataclass
class GraphMLResult:
    """Result of a graph-ML task."""
    task: str
    method: str = ''
    items: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'task': self.task,
            'method': self.method,
            'items': self.items,
            'metrics': self.metrics,
            'execution_time': self.execution_time,
        }


@dataclass
class GraphMLConfig:
    """Configuration for graph ML."""
    dimensions: int = 16
    walk_length: int = 30
    num_walks: int = 10
    random_state: int = 42
    test_size: float = 0.2

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'dimensions': self.dimensions,
            'walk_length': self.walk_length,
            'num_walks': self.num_walks,
            'random_state': self.random_state,
            'test_size': self.test_size,
        }


class GraphML:
    """
    Graph machine learning for OpenLens.

    Embeddings default to spectral (sklearn, CPU-only, no extra deps).
    node2vec is honoured only when its package is installed - requesting it
    without the package raises rather than silently substituting, because a
    silently-swapped embedding method produces plausible-looking, meaningless
    vectors.
    """

    def __init__(self, graph_engine=None, config: GraphMLConfig = None):
        """
        Initialize graph ML.

        Args:
            graph_engine: GraphEngine instance.
            config: GraphMLConfig.
        """
        self.graph_engine = graph_engine
        self.config = config or GraphMLConfig()
        self._embedding_cache: Dict[str, Dict[str, NodeEmbedding]] = {}

    def _graph(self):
        """The live networkx graph, or None."""
        if not NETWORKX_AVAILABLE or not self.graph_engine:
            return None
        return self.graph_engine.to_networkx()

    def embed_nodes(self, method: str = 'spectral',
                    dimensions: int = None) -> List[NodeEmbedding]:
        """
        Compute embeddings for every node.

        Args:
            method: 'spectral' (default) or 'node2vec'.
            dimensions: Embedding size (None for config default).

        Returns:
            List of NodeEmbedding.

        Raises:
            RuntimeError: node2vec requested without the package, or the
                required libraries/graph are unavailable.
        """
        dimensions = dimensions or self.config.dimensions
        graph = self._graph()
        if graph is None or graph.number_of_nodes() < 3:
            raise RuntimeError('graph store unavailable or too small to embed')

        if method == 'node2vec':
            if not NODE2VEC_AVAILABLE:
                raise RuntimeError(
                    "node2vec not installed; install node2vec or use method='spectral'")
            model = Node2Vec(graph, dimensions=dimensions,
                             walk_length=self.config.walk_length,
                             num_walks=self.config.num_walks,
                             seed=self.config.random_state, quiet=True).fit()
            embeddings = [
                NodeEmbedding(node_id=str(node),
                              vector=[float(v) for v in model.wv[str(node)]],
                              method='node2vec', dimensions=dimensions)
                for node in graph.nodes()
            ]
        elif method == 'spectral':
            if not (SKLEARN_AVAILABLE and NUMPY_AVAILABLE):
                raise RuntimeError(
                    'spectral embedding requires numpy and scikit-learn')
            nodes = list(graph.nodes())
            adjacency = nx.to_numpy_array(graph, nodelist=nodes)
            n_components = min(dimensions, len(nodes) - 2)
            matrix = SpectralEmbedding(
                n_components=max(1, n_components),
                affinity='precomputed',
                random_state=self.config.random_state,
            ).fit_transform(adjacency + 1e-9)
            embeddings = [
                NodeEmbedding(node_id=str(node),
                              vector=[float(v) for v in row],
                              method='spectral', dimensions=len(row))
                for node, row in zip(nodes, matrix)
            ]
        else:
            raise ValueError(
                f"unknown embedding method {method!r}; allowed: ['spectral', 'node2vec']")

        self._embedding_cache[method] = {e.node_id: e for e in embeddings}
        return embeddings

    def get_embedding(self, node_id: str,
                      method: str = 'spectral') -> Optional[NodeEmbedding]:
        """Embedding for one node (computes the full set on first call)."""
        cache = self._embedding_cache.get(method)
        if cache is None:
            self.embed_nodes(method)
            cache = self._embedding_cache.get(method, {})
        return cache.get(str(node_id))

    def score_link(self, node_1: str, node_2: str,
                   method: str = 'embedding_cosine') -> float:
        """
        Per-pair link score.

        'embedding_cosine' compares spectral embeddings; anything else is
        delegated to the predictive analyzer's structural metrics.
        """
        if method == 'embedding_cosine':
            e1 = self.get_embedding(node_1)
            e2 = self.get_embedding(node_2)
            if not e1 or not e2 or not NUMPY_AVAILABLE:
                return 0.0
            v1, v2 = np.array(e1.vector), np.array(e2.vector)
            denom = float(np.linalg.norm(v1) * np.linalg.norm(v2))
            return float(np.dot(v1, v2) / denom) if denom else 0.0

        from backend.ai import predictive_analyzer
        return predictive_analyzer.score_link(node_1, node_2, method)

    def classify_nodes(self, label_attribute: str = 'label',
                       method: str = 'random_forest') -> GraphMLResult:
        """
        Classify unlabelled nodes from structural features + embeddings.

        Trains on nodes carrying label_attribute and predicts the rest.
        """
        started = time.time()
        if not (SKLEARN_AVAILABLE and NUMPY_AVAILABLE):
            raise RuntimeError('classification requires numpy and scikit-learn')
        graph = self._graph()
        if graph is None:
            raise RuntimeError('graph store unavailable')

        node_ids, feature_matrix = self.build_feature_matrix()
        labels = {n: d.get(label_attribute)
                  for n, d in graph.nodes(data=True) if d.get(label_attribute)}
        train_idx = [i for i, n in enumerate(node_ids) if n in labels]
        predict_idx = [i for i, n in enumerate(node_ids) if n not in labels]

        if len(train_idx) < 4 or len(set(labels.values())) < 2:
            return GraphMLResult(task='classification', method=method,
                                 metrics={'error': 'insufficient labelled nodes'},
                                 execution_time=time.time() - started)

        X = np.array(feature_matrix)
        y = [labels[node_ids[i]] for i in train_idx]

        if method == 'logistic_regression':
            model = LogisticRegression(max_iter=1000)
        elif method == 'random_forest':
            model = RandomForestClassifier(n_estimators=100,
                                           random_state=self.config.random_state)
        else:
            raise ValueError(
                f"unknown method {method!r}; "
                "allowed: ['random_forest', 'logistic_regression']")

        model.fit(X[train_idx], y)
        items = []
        if predict_idx:
            predicted = model.predict(X[predict_idx])
            probabilities = model.predict_proba(X[predict_idx]).max(axis=1)
            items = [
                {'node_id': node_ids[i], 'predicted_label': str(p),
                 'probability': round(float(prob), 4)}
                for i, p, prob in zip(predict_idx, predicted, probabilities)
            ]

        return GraphMLResult(
            task='classification', method=method, items=items,
            metrics={'trained_on': len(train_idx), 'predicted': len(items),
                     'classes': sorted({str(v) for v in labels.values()})},
            execution_time=time.time() - started,
        )

    def rank_nodes(self, method: str = 'pagerank', limit: int = 50) -> GraphMLResult:
        """Rank nodes by a structural importance measure."""
        started = time.time()
        graph = self._graph()
        if graph is None:
            raise RuntimeError('graph store unavailable')

        if method == 'pagerank':
            scores = nx.pagerank(graph)
        elif method == 'degree':
            scores = dict(nx.degree_centrality(graph))
        elif method == 'betweenness':
            scores = nx.betweenness_centrality(graph)
        else:
            raise ValueError(
                f"unknown ranking method {method!r}; "
                "allowed: ['pagerank', 'degree', 'betweenness']")

        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:limit]
        return GraphMLResult(
            task='ranking', method=method,
            items=[{'node_id': str(n), 'score': round(float(s), 6)}
                   for n, s in ranked],
            metrics={'total_nodes': graph.number_of_nodes()},
            execution_time=time.time() - started,
        )

    def extract_node_features(self, node_id: str) -> Dict[str, float]:
        """Structural features for one node."""
        graph = self._graph()
        if graph is None or node_id not in graph:
            return {}
        degree = graph.degree(node_id)
        neighbors = list(graph.neighbors(node_id))
        neighbor_degrees = [graph.degree(n) for n in neighbors]
        return {
            'degree': float(degree),
            'clustering': float(nx.clustering(graph, node_id)),
            'avg_neighbor_degree': (sum(neighbor_degrees) / len(neighbor_degrees)
                                    if neighbor_degrees else 0.0),
            'triangle_count': float(nx.triangles(graph, node_id))
            if not graph.is_directed() else 0.0,
        }

    def build_feature_matrix(self, nodes: List[str] = None) -> Tuple[List[str], List[List[float]]]:
        """(node_ids, structural feature matrix) for the given/all nodes."""
        graph = self._graph()
        if graph is None:
            return [], []
        node_ids = [str(n) for n in (nodes or graph.nodes())]
        matrix = []
        for node_id in node_ids:
            features = self.extract_node_features(node_id)
            matrix.append([
                features.get('degree', 0.0),
                features.get('clustering', 0.0),
                features.get('avg_neighbor_degree', 0.0),
                features.get('triangle_count', 0.0),
            ])
        return node_ids, matrix


# Global graph ML instance
graph_ml = GraphML()
