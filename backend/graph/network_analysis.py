"""
Network Analysis Module for OpenLens

Provides advanced network analysis capabilities similar to Palantir Gotham:
- Centrality analysis (degree, betweenness, closeness, eigenvector)
- Community detection
- Path analysis
- Network metrics
- Graph algorithms
"""

import time
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter
import math

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

# Try to import scipy
try:
    import scipy
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    print("SciPy not available. Install with: pip install scipy")


@dataclass
class CentralityResult:
    """Result of centrality analysis."""
    node_id: str
    degree: float = 0.0
    betweenness: float = 0.0
    closeness: float = 0.0
    eigenvector: float = 0.0
    page_rank: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'node_id': self.node_id,
            'degree': self.degree,
            'betweenness': self.betweenness,
            'closeness': self.closeness,
            'eigenvector': self.eigenvector,
            'page_rank': self.page_rank,
        }


@dataclass
class Community:
    """Represents a community in the graph."""
    community_id: str
    nodes: List[str] = field(default_factory=list)
    size: int = 0
    density: float = 0.0
    modularity: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'community_id': self.community_id,
            'nodes': self.nodes,
            'size': self.size,
            'density': self.density,
            'modularity': self.modularity,
        }


@dataclass
class PathResult:
    """Result of path finding."""
    source: str
    target: str
    path: List[str] = field(default_factory=list)
    length: int = 0
    weight: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'source': self.source,
            'target': self.target,
            'path': self.path,
            'length': self.length,
            'weight': self.weight,
        }


@dataclass
class NetworkMetrics:
    """Network metrics."""
    num_nodes: int = 0
    num_edges: int = 0
    density: float = 0.0
    average_degree: float = 0.0
    diameter: float = 0.0
    average_path_length: float = 0.0
    clustering_coefficient: float = 0.0
    connected_components: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'num_nodes': self.num_nodes,
            'num_edges': self.num_edges,
            'density': self.density,
            'average_degree': self.average_degree,
            'diameter': self.diameter,
            'average_path_length': self.average_path_length,
            'clustering_coefficient': self.clustering_coefficient,
            'connected_components': self.connected_components,
        }


class NetworkAnalyzer:
    """
    Network analyzer for graph data.
    
    Provides advanced network analysis similar to Palantir Gotham.
    """
    
    def __init__(self, graph_engine=None):
        """
        Initialize the network analyzer.
        
        Args:
            graph_engine: GraphEngine instance.
        """
        self.graph_engine = graph_engine
        self._graph = None
        self._last_updated = 0
        self._cache_ttl = 300  # 5 minutes
    
    def _get_networkx_graph(self, force_refresh: bool = False) -> Optional[nx.Graph]:
        """
        Materialise the graph via the engine, which is the single
        correct implementation (business ids, hydrated edge endpoints).
        """
        if not self.graph_engine:
            return None
        graph = self.graph_engine.to_networkx(force_refresh=force_refresh)
        self._graph = graph
        self._last_updated = time.time()
        return graph
    def calculate_centrality(self, node_ids: List[str] = None) -> List[CentralityResult]:
        """
        Calculate centrality metrics for nodes.
        
        Args:
            node_ids: List of node IDs to analyze. If None, analyze all nodes.
            
        Returns:
            List of CentralityResult objects.
        """
        if not NETWORKX_AVAILABLE:
            return []
        
        graph = self._get_networkx_graph()
        if not graph:
            return []
        
        nodes_to_analyze = node_ids if node_ids else list(graph.nodes())
        results = []
        
        for node_id in nodes_to_analyze:
            if node_id not in graph:
                continue
            
            result = CentralityResult(node_id=node_id)
            
            # Degree centrality
            result.degree = graph.degree(node_id)
            
            # Betweenness centrality
            if len(graph) > 2:
                betweenness = nx.betweenness_centrality(graph, weight='weight')
                result.betweenness = betweenness.get(node_id, 0.0)
            
            # Closeness centrality
            if len(graph) > 1:
                closeness = nx.closeness_centrality(graph, distance='weight')
                result.closeness = closeness.get(node_id, 0.0)
            
            # Eigenvector centrality
            if len(graph) > 0:
                try:
                    eigenvector = nx.eigenvector_centrality(graph, weight='weight')
                    result.eigenvector = eigenvector.get(node_id, 0.0)
                except nx.PowerIterationFailedConvergence:
                    result.eigenvector = 0.0
            
            # PageRank
            if len(graph) > 0:
                pagerank = nx.pagerank(graph, weight='weight')
                result.page_rank = pagerank.get(node_id, 0.0)
            
            results.append(result)
        
        return results
    
    def detect_communities(self, algorithm: str = 'louvain', 
                          resolution: float = 1.0) -> List[Community]:
        """
        Detect communities in the graph.
        
        Args:
            algorithm: Community detection algorithm ('louvain', 'girvan_newman', 'label_propagation').
            resolution: Resolution parameter for Louvain algorithm.
            
        Returns:
            List of Community objects.
        """
        if not NETWORKX_AVAILABLE:
            return []
        
        graph = self._get_networkx_graph()
        if not graph:
            return []
        
        communities = []
        
        try:
            if algorithm == 'louvain':
                # Try to import python-louvain
                try:
                    import community as community_louvain
                    partition = community_louvain.best_partition(
                        graph.to_undirected(),
                        resolution=resolution
                    )
                    
                    # Group nodes by community
                    community_map = defaultdict(list)
                    for node_id, community_id in partition.items():
                        community_map[community_id].append(node_id)
                    
                    for community_id, nodes in community_map.items():
                        subgraph = graph.subgraph(nodes)
                        communities.append(Community(
                            community_id=str(community_id),
                            nodes=nodes,
                            size=len(nodes),
                            density=nx.density(subgraph) if len(nodes) > 1 else 0.0,
                        ))
                except ImportError:
                    print("python-louvain not available. Install with: pip install python-louvain")
                    # Fall back to label propagation
                    algorithm = 'label_propagation'
            
            if algorithm == 'girvan_newman':
                comp = nx.algorithms.community.girvan_newman(graph)
                for i, component in enumerate(comp):
                    communities.append(Community(
                        community_id=str(i),
                        nodes=list(component),
                        size=len(component),
                    ))
            
            elif algorithm == 'label_propagation':
                communities_list = list(nx.algorithms.community.label_propagation_communities(graph))
                for i, community_nodes in enumerate(communities_list):
                    subgraph = graph.subgraph(community_nodes)
                    communities.append(Community(
                        community_id=str(i),
                        nodes=list(community_nodes),
                        size=len(community_nodes),
                        density=nx.density(subgraph) if len(community_nodes) > 1 else 0.0,
                    ))
            
            else:
                # Default to connected components
                for i, component in enumerate(nx.connected_components(graph.to_undirected())):
                    communities.append(Community(
                        community_id=str(i),
                        nodes=list(component),
                        size=len(component),
                    ))
        
        except Exception as e:
            print(f"Community detection error: {e}")
        
        return communities
    
    def find_shortest_path(self, source: str, target: str, 
                          weight: str = None) -> Optional[PathResult]:
        """
        Find the shortest path between two nodes.
        
        Args:
            source: Source node ID.
            target: Target node ID.
            weight: Edge weight attribute.
            
        Returns:
            PathResult or None if no path exists.
        """
        if not NETWORKX_AVAILABLE:
            return None
        
        graph = self._get_networkx_graph()
        if not graph:
            return None
        
        if source not in graph or target not in graph:
            return None
        
        try:
            if weight and nx.has_path(graph, source, target):
                path = nx.shortest_path(graph, source, target, weight=weight)
                path_length = nx.shortest_path_length(graph, source, target, weight=weight)
                path_weight = sum(
                    graph[path[i]][path[i+1]].get(weight, 1)
                    for i in range(len(path) - 1)
                )
            else:
                path = nx.shortest_path(graph, source, target)
                path_length = len(path) - 1
                path_weight = path_length
            
            return PathResult(
                source=source,
                target=target,
                path=path,
                length=path_length,
                weight=path_weight,
            )
        
        except nx.NetworkXNoPath:
            return None
        except Exception as e:
            print(f"Path finding error: {e}")
            return None
    
    def find_all_paths(self, source: str, target: str, 
                       max_length: int = 10) -> List[PathResult]:
        """
        Find all paths between two nodes.
        
        Args:
            source: Source node ID.
            target: Target node ID.
            max_length: Maximum path length.
            
        Returns:
            List of PathResult objects.
        """
        if not NETWORKX_AVAILABLE:
            return []
        
        graph = self._get_networkx_graph()
        if not graph:
            return []
        
        if source not in graph or target not in graph:
            return []
        
        try:
            all_paths = list(nx.all_simple_paths(graph, source, target, cutoff=max_length))
            results = []
            
            for path in all_paths:
                results.append(PathResult(
                    source=source,
                    target=target,
                    path=path,
                    length=len(path) - 1,
                ))
            
            return results
        
        except Exception as e:
            print(f"All paths finding error: {e}")
            return []
    
    def calculate_metrics(self) -> NetworkMetrics:
        """
        Calculate overall network metrics.
        
        Returns:
            NetworkMetrics object.
        """
        if not NETWORKX_AVAILABLE:
            return NetworkMetrics()
        
        graph = self._get_networkx_graph()
        if not graph:
            return NetworkMetrics()
        
        metrics = NetworkMetrics()
        
        try:
            metrics.num_nodes = len(graph.nodes())
            metrics.num_edges = len(graph.edges())
            
            if metrics.num_nodes > 1:
                metrics.density = nx.density(graph)
            
            degrees = [d for _, d in graph.degree()]
            if degrees:
                metrics.average_degree = sum(degrees) / len(degrees)
            
            if metrics.num_nodes > 1 and nx.is_connected(graph):
                metrics.diameter = nx.diameter(graph)
                metrics.average_path_length = nx.average_shortest_path_length(graph)
            
            if metrics.num_nodes > 2:
                metrics.clustering_coefficient = nx.average_clustering(graph)
            
            metrics.connected_components = nx.number_connected_components(graph.to_undirected())
        
        except Exception as e:
            print(f"Metrics calculation error: {e}")
        
        return metrics
    
    def get_neighbors(self, node_id: str, depth: int = 1) -> Dict[str, List[str]]:
        """
        Get neighbors of a node at different depths.
        
        Args:
            node_id: Node ID.
            depth: Maximum depth.
            
        Returns:
            Dictionary with depth as key and list of node IDs as value.
        """
        if not NETWORKX_AVAILABLE:
            return {}
        
        graph = self._get_networkx_graph()
        if not graph or node_id not in graph:
            return {}
        
        neighbors = {}
        
        try:
            for d in range(1, depth + 1):
                nodes_at_depth = set()
                
                if d == 1:
                    nodes_at_depth = set(graph.neighbors(node_id))
                else:
                    # Get nodes at previous depth
                    prev_nodes = neighbors.get(d - 1, set([node_id]))
                    
                    for prev_node in prev_nodes:
                        nodes_at_depth.update(graph.neighbors(prev_node))
                    
                    # Remove nodes from previous depths
                    for i in range(1, d):
                        nodes_at_depth -= set(neighbors.get(i, []))
                
                neighbors[d] = list(nodes_at_depth)
        
        except Exception as e:
            print(f"Neighbors error: {e}")
        
        return neighbors
    
    def find_bridges(self) -> List[Tuple[str, str]]:
        """
        Find bridge edges (edges whose removal increases the number of connected components).
        
        Returns:
            List of (source, target) tuples.
        """
        if not NETWORKX_AVAILABLE:
            return []
        
        graph = self._get_networkx_graph()
        if not graph:
            return []
        
        try:
            bridges = list(nx.bridges(graph))
            return [(str(u), str(v)) for u, v in bridges]
        except Exception as e:
            print(f"Bridge finding error: {e}")
            return []
    
    def find_articulation_points(self) -> List[str]:
        """
        Find articulation points (nodes whose removal increases the number of connected components).
        
        Returns:
            List of node IDs.
        """
        if not NETWORKX_AVAILABLE:
            return []
        
        graph = self._get_networkx_graph()
        if not graph:
            return []
        
        try:
            articulation_points = list(nx.articulation_points(graph))
            return [str(node) for node in articulation_points]
        except Exception as e:
            print(f"Articulation points error: {e}")
            return []
    
    def calculate_transitivity(self) -> float:
        """
        Calculate the transitivity of the graph (fraction of transitive triples).
        
        Returns:
            Transitivity value (0-1).
        """
        if not NETWORKX_AVAILABLE:
            return 0.0
        
        graph = self._get_networkx_graph()
        if not graph or len(graph) < 3:
            return 0.0
        
        try:
            return nx.transitivity(graph)
        except Exception as e:
            print(f"Transitivity calculation error: {e}")
            return 0.0
    
    def get_degree_distribution(self) -> Dict[int, int]:
        """
        Get the degree distribution of the graph.
        
        Returns:
            Dictionary with degree as key and count as value.
        """
        if not NETWORKX_AVAILABLE:
            return {}
        
        graph = self._get_networkx_graph()
        if not graph:
            return {}
        
        try:
            degrees = [d for _, d in graph.degree()]
            return dict(Counter(degrees))
        except Exception as e:
            print(f"Degree distribution error: {e}")
            return {}


# Global network analyzer instance
network_analyzer = NetworkAnalyzer()
