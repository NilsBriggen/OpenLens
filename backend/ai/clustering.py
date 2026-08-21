"""
Clustering Module for OpenLens

Provides feature-space clustering:
- K-Means clustering with automatic k selection
- DBSCAN density clustering
- Hierarchical (agglomerative) clustering
- Graph-topology clustering (delegated to the community detector)
- Cluster quality metrics (silhouette)

Graph-topology clustering belongs to backend.graph.community_detection; the
cluster_graph method delegates there rather than reimplementing it.
"""

import time
import uuid
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

# Try to import numpy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("NumPy not available. Install with: pip install numpy")

# Try to import scikit-learn
try:
    from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("scikit-learn not available. Install with: pip install scikit-learn")


@dataclass
class Cluster:
    """Represents a cluster of items."""
    cluster_id: str
    members: List[str] = field(default_factory=list)
    centroid: List[float] = field(default_factory=list)
    size: int = 0
    cohesion: float = 0.0
    label: str = ''

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'cluster_id': self.cluster_id,
            'members': self.members,
            'centroid': self.centroid,
            'size': self.size,
            'cohesion': self.cohesion,
            'label': self.label,
        }


@dataclass
class ClusteringResult:
    """Result of a clustering run."""
    method: str
    clusters: List[Cluster] = field(default_factory=list)
    noise: List[str] = field(default_factory=list)
    n_clusters: int = 0
    silhouette: float = 0.0
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'method': self.method,
            'clusters': [c.to_dict() for c in self.clusters],
            'noise': self.noise,
            'n_clusters': self.n_clusters,
            'silhouette': self.silhouette,
            'execution_time': self.execution_time,
        }


@dataclass
class ClusteringConfig:
    """Configuration for clustering."""
    method: str = 'kmeans'
    n_clusters: int = 5
    eps: float = 0.5
    min_samples: int = 5
    features: List[str] = field(default_factory=list)
    auto_k: bool = True
    max_k: int = 10
    random_state: int = 42

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'method': self.method,
            'n_clusters': self.n_clusters,
            'eps': self.eps,
            'min_samples': self.min_samples,
            'features': self.features,
            'auto_k': self.auto_k,
            'max_k': self.max_k,
            'random_state': self.random_state,
        }


class ClusterAnalyzer:
    """
    Feature-space cluster analyzer for OpenLens.

    Provides:
    - K-Means (with silhouette-based k selection)
    - DBSCAN
    - Hierarchical clustering
    - Graph clustering (delegated to community_detector)
    """

    def __init__(self, graph_engine=None, config: ClusteringConfig = None):
        """
        Initialize the cluster analyzer.

        Args:
            graph_engine: GraphEngine instance.
            config: ClusteringConfig.
        """
        self.graph_engine = graph_engine
        self.config = config or ClusteringConfig()

    def _feature_matrix(self, data: List[Dict[str, Any]]) -> Tuple[List[str], Any]:
        """(item_ids, scaled feature matrix) from numeric fields."""
        if not data:
            return [], None

        features = self.config.features or sorted({
            key for item in data for key, value in item.items()
            if isinstance(value, (int, float)) and not isinstance(value, bool)
            and key not in ('id',)
        })
        if not features:
            return [], None

        ids: List[str] = []
        rows: List[List[float]] = []
        for index, item in enumerate(data):
            ids.append(str(item.get('id', index)))
            rows.append([float(item.get(f, 0) or 0) for f in features])

        matrix = np.array(rows)
        if SKLEARN_AVAILABLE:
            matrix = StandardScaler().fit_transform(matrix)
        return ids, matrix

    def _package(self, method: str, ids: List[str], labels, matrix,
                 started: float) -> ClusteringResult:
        """Group label assignments into Cluster objects."""
        clusters: Dict[int, Cluster] = {}
        noise: List[str] = []

        for item_id, label in zip(ids, labels):
            label = int(label)
            if label == -1:
                noise.append(item_id)
                continue
            if label not in clusters:
                clusters[label] = Cluster(cluster_id=f'{method}_{label}', label=str(label))
            clusters[label].members.append(item_id)

        for label, cluster in clusters.items():
            cluster.size = len(cluster.members)
            if matrix is not None:
                mask = [i for i, l in enumerate(labels) if int(l) == label]
                centroid = matrix[mask].mean(axis=0)
                cluster.centroid = [round(float(v), 4) for v in centroid]
                if len(mask) > 1:
                    distances = np.linalg.norm(matrix[mask] - centroid, axis=1)
                    cluster.cohesion = round(float(distances.mean()), 4)

        silhouette = 0.0
        unique = {int(l) for l in labels if int(l) != -1}
        if SKLEARN_AVAILABLE and matrix is not None and 1 < len(unique) < len(ids):
            try:
                valid = [i for i, l in enumerate(labels) if int(l) != -1]
                silhouette = float(silhouette_score(
                    matrix[valid], [int(labels[i]) for i in valid]))
            except Exception:
                silhouette = 0.0

        return ClusteringResult(
            method=method,
            clusters=sorted(clusters.values(), key=lambda c: c.size, reverse=True),
            noise=noise,
            n_clusters=len(clusters),
            silhouette=round(silhouette, 4),
            execution_time=time.time() - started,
        )

    def cluster(self, data: List[Dict[str, Any]], method: str = None,
                n_clusters: int = None) -> ClusteringResult:
        """
        Cluster items by their numeric features.

        Args:
            data: Items with numeric feature fields.
            method: 'kmeans', 'dbscan' or 'hierarchical' (None for config).
            n_clusters: Cluster count for kmeans/hierarchical.

        Returns:
            ClusteringResult.

        Raises:
            RuntimeError: When numpy/scikit-learn are unavailable.
            ValueError: For an unknown method.
        """
        method = method or self.config.method
        if method == 'kmeans':
            return self.cluster_kmeans(data, n_clusters)
        if method == 'dbscan':
            return self.cluster_dbscan(data)
        if method == 'hierarchical':
            return self.cluster_hierarchical(data, n_clusters)
        raise ValueError(
            f"unknown clustering method {method!r}; "
            "allowed: ['kmeans', 'dbscan', 'hierarchical']")

    def _require_sklearn(self):
        if not (SKLEARN_AVAILABLE and NUMPY_AVAILABLE):
            raise RuntimeError(
                'clustering requires numpy and scikit-learn; '
                'install with: pip install numpy scikit-learn')

    def cluster_kmeans(self, data: List[Dict[str, Any]],
                       n_clusters: int = None) -> ClusteringResult:
        """K-Means clustering (auto-k via silhouette when configured)."""
        self._require_sklearn()
        started = time.time()
        ids, matrix = self._feature_matrix(data)
        if matrix is None or len(ids) < 2:
            return ClusteringResult(method='kmeans', execution_time=time.time() - started)

        k = n_clusters or self.config.n_clusters
        if n_clusters is None and self.config.auto_k:
            k = self.find_optimal_k(data, (2, min(self.config.max_k, len(ids) - 1)))
        k = max(1, min(k, len(ids)))

        labels = KMeans(n_clusters=k, random_state=self.config.random_state,
                        n_init=10).fit_predict(matrix)
        return self._package('kmeans', ids, labels, matrix, started)

    def cluster_dbscan(self, data: List[Dict[str, Any]], eps: float = None,
                       min_samples: int = None) -> ClusteringResult:
        """DBSCAN clustering; unassigned points land in .noise."""
        self._require_sklearn()
        started = time.time()
        ids, matrix = self._feature_matrix(data)
        if matrix is None or len(ids) < 2:
            return ClusteringResult(method='dbscan', execution_time=time.time() - started)

        labels = DBSCAN(eps=eps or self.config.eps,
                        min_samples=min_samples or self.config.min_samples
                        ).fit_predict(matrix)
        return self._package('dbscan', ids, labels, matrix, started)

    def cluster_hierarchical(self, data: List[Dict[str, Any]],
                             n_clusters: int = None,
                             linkage: str = 'ward') -> ClusteringResult:
        """Agglomerative clustering."""
        self._require_sklearn()
        started = time.time()
        ids, matrix = self._feature_matrix(data)
        if matrix is None or len(ids) < 2:
            return ClusteringResult(method='hierarchical',
                                    execution_time=time.time() - started)

        k = max(1, min(n_clusters or self.config.n_clusters, len(ids)))
        labels = AgglomerativeClustering(n_clusters=k,
                                         linkage=linkage).fit_predict(matrix)
        return self._package('hierarchical', ids, labels, matrix, started)

    def cluster_graph(self, algorithm: str = 'louvain') -> ClusteringResult:
        """
        Graph-topology clustering, delegated to the community detector.

        Returns an empty result when the community detector or graph store is
        unavailable.
        """
        started = time.time()
        try:
            from backend.graph import community_detector
        except ImportError:
            return ClusteringResult(method=f'graph:{algorithm}',
                                    execution_time=time.time() - started)

        if algorithm == 'louvain':
            detection = community_detector.detect_louvain()
        elif algorithm == 'label_propagation':
            detection = community_detector.detect_label_propagation()
        else:
            detection = community_detector.detect_connected_components()

        clusters = []
        if detection and getattr(detection, 'communities', None):
            for community in detection.communities:
                clusters.append(Cluster(
                    cluster_id=str(getattr(community, 'community_id', uuid.uuid4())),
                    members=list(getattr(community, 'nodes', [])),
                    size=len(getattr(community, 'nodes', [])),
                ))

        return ClusteringResult(
            method=f'graph:{algorithm}',
            clusters=clusters,
            n_clusters=len(clusters),
            execution_time=time.time() - started,
        )

    def find_optimal_k(self, data: List[Dict[str, Any]],
                       k_range: Tuple[int, int] = (2, 10)) -> int:
        """Silhouette sweep for the best k."""
        self._require_sklearn()
        ids, matrix = self._feature_matrix(data)
        if matrix is None or len(ids) < 3:
            return self.config.n_clusters

        lo, hi = k_range
        hi = min(hi, len(ids) - 1)
        best_k, best_score = max(2, lo), -1.0
        for k in range(max(2, lo), hi + 1):
            try:
                labels = KMeans(n_clusters=k, random_state=self.config.random_state,
                                n_init=10).fit_predict(matrix)
                score = silhouette_score(matrix, labels)
                if score > best_score:
                    best_k, best_score = k, score
            except Exception:
                continue
        return best_k

    def get_cluster_summary(self, result: ClusteringResult) -> Dict[str, Any]:
        """Compact per-cluster summary of a result."""
        return {
            'method': result.method,
            'n_clusters': result.n_clusters,
            'silhouette': result.silhouette,
            'noise_count': len(result.noise),
            'sizes': {c.cluster_id: c.size for c in result.clusters},
        }

    def assign_to_cluster(self, item: Dict[str, Any],
                          result: ClusteringResult) -> Optional[str]:
        """Nearest-centroid assignment of a new item to an existing result."""
        if not NUMPY_AVAILABLE or not result.clusters:
            return None
        ids, matrix = self._feature_matrix([item])
        if matrix is None:
            return None
        row = matrix[0]

        best_id, best_distance = None, float('inf')
        for cluster in result.clusters:
            if not cluster.centroid or len(cluster.centroid) != len(row):
                continue
            distance = float(np.linalg.norm(row - np.array(cluster.centroid)))
            if distance < best_distance:
                best_id, best_distance = cluster.cluster_id, distance
        return best_id


# Global cluster analyzer instance
cluster_analyzer = ClusterAnalyzer()
