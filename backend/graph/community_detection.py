"""
Community Detection Module for OpenLens

Provides advanced community detection capabilities:
- Louvain method
- Label propagation
- Girvan-Newman
- Modularity optimization
- Community analysis
- Community visualization
"""

import time
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict, Counter

# Try to import networkx
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("NetworkX not available. Install with: pip install networkx")

# Try to import python-louvain
try:
    import community as community_louvain
    LOUVAIN_AVAILABLE = True
except ImportError:
    LOUVAIN_AVAILABLE = False
    print("python-louvain not available. Install with: pip install python-louvain")

# Try to import igraph
try:
    import igraph
    IGRAPH_AVAILABLE = True
except ImportError:
    IGRAPH_AVAILABLE = False
    print("igraph not available. Install with: pip install python-igraph")


@dataclass
class Community:
    """Represents a detected community."""
    community_id: str
    nodes: List[str] = field(default_factory=list)
    size: int = 0
    density: float = 0.0
    modularity: float = 0.0
    centrality: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'community_id': self.community_id,
            'nodes': self.nodes,
            'size': self.size,
            'density': self.density,
            'modularity': self.modularity,
            'centrality': self.centrality,
        }


@dataclass
class CommunityDetectionResult:
    """Result of community detection."""
    algorithm: str
    communities: List[Community] = field(default_factory=list)
    modularity: float = 0.0
    num_communities: int = 0
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'algorithm': self.algorithm,
            'communities': [c.to_dict() for c in self.communities],
            'modularity': self.modularity,
            'num_communities': self.num_communities,
            'execution_time': self.execution_time,
        }


@dataclass
class CommunityMetrics:
    """Metrics for a community."""
    community_id: str
    size: int = 0
    density: float = 0.0
    average_degree: float = 0.0
    diameter: float = 0.0
    clustering_coefficient: float = 0.0
    centrality: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'community_id': self.community_id,
            'size': self.size,
            'density': self.density,
            'average_degree': self.average_degree,
            'diameter': self.diameter,
            'clustering_coefficient': self.clustering_coefficient,
            'centrality': self.centrality,
        }


class CommunityDetector:
    """
    Community detector for graph data.
    
    Provides advanced community detection similar to Palantir Gotham.
    """
    
    def __init__(self, graph_engine=None):
        """
        Initialize the community detector.
        
        Args:
            graph_engine: GraphEngine instance.
        """
        self.graph_engine = graph_engine
        self._graph = None
        self._last_updated = 0
        self._cache_ttl = 300  # 5 minutes
    
    def _get_networkx_graph(self, force_refresh: bool = False) -> Optional[nx.Graph]:
        """
        Get the graph as a NetworkX graph.
        
        Args:
            force_refresh: Force refresh from database.
            
        Returns:
            NetworkX Graph or None.
        """
        if not NETWORKX_AVAILABLE:
            return None
        
        if not self.graph_engine:
            return None
        
        current_time = time.time()
        if not force_refresh and self._graph and (current_time - self._last_updated) < self._cache_ttl:
            return self._graph
        
        try:
            # Fetch all nodes and relationships
            query = "MATCH (n) RETURN n"
            result = self.graph_engine.execute_query(query)
            
            if not result:
                return None
            
            self._graph = nx.Graph()
            
            # Add nodes
            for node in result.nodes:
                self._graph.add_node(
                    node.node_id,
                    labels=node.labels,
                    **node.properties
                )
            
            # Add edges
            query = "MATCH ()-[r]->() RETURN r"
            result = self.graph_engine.execute_query(query)
            
            if result:
                for rel in result.relationships:
                    self._graph.add_edge(
                        rel.source_id,
                        rel.target_id,
                        type=rel.rel_type,
                        **rel.properties
                    )
            
            self._last_updated = current_time
            return self._graph
        
        except Exception as e:
            print(f"Error building NetworkX graph: {e}")
            return None
    
    def detect_louvain(self, resolution: float = 1.0, 
                      random_state: int = None) -> CommunityDetectionResult:
        """
        Detect communities using the Louvain method.
        
        Args:
            resolution: Resolution parameter (higher values lead to more communities).
            random_state: Random seed for reproducibility.
            
        Returns:
            CommunityDetectionResult.
        """
        if not LOUVAIN_AVAILABLE:
            print("Louvain not available. Falling back to label propagation.")
            return self.detect_label_propagation()
        
        graph = self._get_networkx_graph()
        if not graph:
            return CommunityDetectionResult(algorithm='louvain')
        
        start_time = time.time()
        
        try:
            partition = community_louvain.best_partition(
                graph.to_undirected(),
                resolution=resolution,
                random_state=random_state
            )
            
            # Calculate modularity
            modularity = community_louvain.modularity(partition, graph.to_undirected())
            
            # Group nodes by community
            community_map = defaultdict(list)
            for node_id, community_id in partition.items():
                community_map[community_id].append(node_id)
            
            communities = []
            for community_id, nodes in community_map.items():
                subgraph = graph.subgraph(nodes)
                communities.append(Community(
                    community_id=str(community_id),
                    nodes=nodes,
                    size=len(nodes),
                    density=nx.density(subgraph) if len(nodes) > 1 else 0.0,
                    modularity=modularity,
                ))
            
            execution_time = time.time() - start_time
            
            return CommunityDetectionResult(
                algorithm='louvain',
                communities=communities,
                modularity=modularity,
                num_communities=len(communities),
                execution_time=execution_time,
            )
        
        except Exception as e:
            print(f"Louvain detection error: {e}")
            return CommunityDetectionResult(algorithm='louvain')
    
    def detect_label_propagation(self, max_iter: int = 100) -> CommunityDetectionResult:
        """
        Detect communities using label propagation.
        
        Args:
            max_iter: Maximum number of iterations.
            
        Returns:
            CommunityDetectionResult.
        """
        if not NETWORKX_AVAILABLE:
            return CommunityDetectionResult(algorithm='label_propagation')
        
        graph = self._get_networkx_graph()
        if not graph:
            return CommunityDetectionResult(algorithm='label_propagation')
        
        start_time = time.time()
        
        try:
            communities_list = list(nx.algorithms.community.label_propagation_communities(
                graph.to_undirected()
            ))
            
            communities = []
            for i, community_nodes in enumerate(communities_list):
                subgraph = graph.subgraph(community_nodes)
                communities.append(Community(
                    community_id=str(i),
                    nodes=list(community_nodes),
                    size=len(community_nodes),
                    density=nx.density(subgraph) if len(community_nodes) > 1 else 0.0,
                ))
            
            # Calculate modularity
            partition = {}
            for i, community_nodes in enumerate(communities_list):
                for node in community_nodes:
                    partition[node] = i
            
            modularity = nx.algorithms.community.modularity(graph.to_undirected(), communities_list)
            
            execution_time = time.time() - start_time
            
            return CommunityDetectionResult(
                algorithm='label_propagation',
                communities=communities,
                modularity=modularity,
                num_communities=len(communities),
                execution_time=execution_time,
            )
        
        except Exception as e:
            print(f"Label propagation error: {e}")
            return CommunityDetectionResult(algorithm='label_propagation')
    
    def detect_girvan_newman(self) -> CommunityDetectionResult:
        """
        Detect communities using Girvan-Newman algorithm.
        
        Returns:
            CommunityDetectionResult.
        """
        if not NETWORKX_AVAILABLE:
            return CommunityDetectionResult(algorithm='girvan_newman')
        
        graph = self._get_networkx_graph()
        if not graph:
            return CommunityDetectionResult(algorithm='girvan_newman')
        
        start_time = time.time()
        
        try:
            comp = nx.algorithms.community.girvan_newman(graph.to_undirected())
            
            # Get communities at maximum modularity
            communities_list = []
            max_modularity = -1
            best_communities = []
            
            for communities in comp:
                modularity = nx.algorithms.community.modularity(graph.to_undirected(), communities)
                if modularity > max_modularity:
                    max_modularity = modularity
                    best_communities = [list(c) for c in communities]
            
            communities = []
            for i, community_nodes in enumerate(best_communities):
                subgraph = graph.subgraph(community_nodes)
                communities.append(Community(
                    community_id=str(i),
                    nodes=community_nodes,
                    size=len(community_nodes),
                    density=nx.density(subgraph) if len(community_nodes) > 1 else 0.0,
                    modularity=max_modularity,
                ))
            
            execution_time = time.time() - start_time
            
            return CommunityDetectionResult(
                algorithm='girvan_newman',
                communities=communities,
                modularity=max_modularity,
                num_communities=len(communities),
                execution_time=execution_time,
            )
        
        except Exception as e:
            print(f"Girvan-Newman error: {e}")
            return CommunityDetectionResult(algorithm='girvan_newman')
    
    def detect_connected_components(self) -> CommunityDetectionResult:
        """
        Detect connected components.
        
        Returns:
            CommunityDetectionResult.
        """
        if not NETWORKX_AVAILABLE:
            return CommunityDetectionResult(algorithm='connected_components')
        
        graph = self._get_networkx_graph()
        if not graph:
            return CommunityDetectionResult(algorithm='connected_components')
        
        start_time = time.time()
        
        try:
            components = list(nx.connected_components(graph.to_undirected()))
            
            communities = []
            for i, component in enumerate(components):
                subgraph = graph.subgraph(component)
                communities.append(Community(
                    community_id=str(i),
                    nodes=list(component),
                    size=len(component),
                    density=nx.density(subgraph) if len(component) > 1 else 0.0,
                ))
            
            execution_time = time.time() - start_time
            
            return CommunityDetectionResult(
                algorithm='connected_components',
                communities=communities,
                num_communities=len(communities),
                execution_time=execution_time,
            )
        
        except Exception as e:
            print(f"Connected components error: {e}")
            return CommunityDetectionResult(algorithm='connected_components')
    
    def detect_kernighan_lin(self, max_iter: int = 100) -> CommunityDetectionResult:
        """
        Detect communities using Kernighan-Lin algorithm.
        
        Args:
            max_iter: Maximum number of iterations.
            
        Returns:
            CommunityDetectionResult.
        """
        if not NETWORKX_AVAILABLE:
            return CommunityDetectionResult(algorithm='kernighan_lin')
        
        graph = self._get_networkx_graph()
        if not graph:
            return CommunityDetectionResult(algorithm='kernighan_lin')
        
        start_time = time.time()
        
        try:
            # Kernighan-Lin requires initial partition
            # Use connected components as initial partition
            components = list(nx.connected_components(graph.to_undirected()))
            
            if len(components) < 2:
                # If graph is connected, create initial partition
                nodes = list(graph.nodes())
                partition = [nodes[:len(nodes)//2], nodes[len(nodes)//2:]]
            else:
                partition = [list(c) for c in components]
            
            # Apply Kernighan-Lin
            communities_list = nx.algorithms.community.kernighan_lin_bisection(
                graph.to_undirected(),
                max_iter=max_iter,
                initial_partition=partition
            )
            
            communities = []
            for i, community_nodes in enumerate(communities_list):
                subgraph = graph.subgraph(community_nodes)
                communities.append(Community(
                    community_id=str(i),
                    nodes=list(community_nodes),
                    size=len(community_nodes),
                    density=nx.density(subgraph) if len(community_nodes) > 1 else 0.0,
                ))
            
            modularity = nx.algorithms.community.modularity(graph.to_undirected(), communities_list)
            execution_time = time.time() - start_time
            
            return CommunityDetectionResult(
                algorithm='kernighan_lin',
                communities=communities,
                modularity=modularity,
                num_communities=len(communities),
                execution_time=execution_time,
            )
        
        except Exception as e:
            print(f"Kernighan-Lin error: {e}")
            return CommunityDetectionResult(algorithm='kernighan_lin')
    
    def detect_igraph_communities(self, algorithm: str = 'louvain') -> CommunityDetectionResult:
        """
        Detect communities using igraph.
        
        Args:
            algorithm: Algorithm to use ('louvain', 'fastgreedy', 'walktrap', 'leading_eigenvector').
            
        Returns:
            CommunityDetectionResult.
        """
        if not IGRAPH_AVAILABLE:
            print("igraph not available. Falling back to NetworkX.")
            return self.detect_louvain()
        
        if not self.graph_engine:
            return CommunityDetectionResult(algorithm=f'igraph_{algorithm}')
        
        start_time = time.time()
        
        try:
            # Build igraph graph
            query = "MATCH (n) RETURN n"
            result = self.graph_engine.execute_query(query)
            
            if not result:
                return CommunityDetectionResult(algorithm=f'igraph_{algorithm}')
            
            g = igraph.Graph(directed=False)
            node_map = {}
            
            # Add nodes
            for node in result.nodes:
                node_id = node.node_id
                node_map[node_id] = len(g.vs)
                g.add_vertex(node_id)
            
            # Add edges
            query = "MATCH ()-[r]->() RETURN r"
            result = self.graph_engine.execute_query(query)
            
            if result:
                for rel in result.relationships:
                    if rel.source_id in node_map and rel.target_id in node_map:
                        g.add_edge(node_map[rel.source_id], node_map[rel.target_id])
            
            # Detect communities
            if algorithm == 'louvain':
                communities = g.community_multilevel()
            elif algorithm == 'fastgreedy':
                communities = g.community_fastgreedy()
            elif algorithm == 'walktrap':
                communities = g.community_walktrap()
            elif algorithm == 'leading_eigenvector':
                communities = g.community_leading_eigenvector()
            else:
                communities = g.community_multilevel()
            
            # Convert to our format
            community_list = []
            for i, community in enumerate(communities):
                node_ids = [g.vs[idx]['name'] for idx in community]
                community_list.append(Community(
                    community_id=str(i),
                    nodes=node_ids,
                    size=len(node_ids),
                ))
            
            modularity = communities.modularity
            execution_time = time.time() - start_time
            
            return CommunityDetectionResult(
                algorithm=f'igraph_{algorithm}',
                communities=community_list,
                modularity=modularity,
                num_communities=len(community_list),
                execution_time=execution_time,
            )
        
        except Exception as e:
            print(f"igraph community detection error: {e}")
            return CommunityDetectionResult(algorithm=f'igraph_{algorithm}')
    
    def calculate_community_metrics(self, community_id: str) -> Optional[CommunityMetrics]:
        """
        Calculate metrics for a specific community.
        
        Args:
            community_id: Community ID.
            
        Returns:
            CommunityMetrics or None.
        """
        if not NETWORKX_AVAILABLE:
            return None
        
        graph = self._get_networkx_graph()
        if not graph:
            return None
        
        # Find the community
        detection_result = self.detect_louvain()
        community = None
        
        for c in detection_result.communities:
            if c.community_id == community_id:
                community = c
                break
        
        if not community:
            return None
        
        try:
            subgraph = graph.subgraph(community.nodes)
            
            metrics = CommunityMetrics(
                community_id=community_id,
                size=community.size,
                density=nx.density(subgraph) if len(community.nodes) > 1 else 0.0,
            )
            
            if len(community.nodes) > 0:
                degrees = [d for _, d in subgraph.degree()]
                metrics.average_degree = sum(degrees) / len(degrees)
            
            if len(community.nodes) > 1 and nx.is_connected(subgraph):
                metrics.diameter = nx.diameter(subgraph)
            
            if len(community.nodes) > 2:
                metrics.clustering_coefficient = nx.average_clustering(subgraph)
            
            # Calculate centrality for nodes in community
            if len(community.nodes) > 1:
                degree_centrality = nx.degree_centrality(subgraph)
                betweenness_centrality = nx.betweenness_centrality(subgraph)
                closeness_centrality = nx.closeness_centrality(subgraph)
                
                for node_id in community.nodes:
                    if node_id in degree_centrality:
                        metrics.centrality[node_id] = {
                            'degree': degree_centrality[node_id],
                            'betweenness': betweenness_centrality.get(node_id, 0.0),
                            'closeness': closeness_centrality.get(node_id, 0.0),
                        }
            
            return metrics
        
        except Exception as e:
            print(f"Community metrics error: {e}")
            return None
    
    def find_community_overlaps(self, min_overlap: int = 2) -> List[Dict[str, Any]]:
        """
        Find overlaps between communities.
        
        Args:
            min_overlap: Minimum number of overlapping nodes to report.
            
        Returns:
            List of overlap dictionaries.
        """
        if not NETWORKX_AVAILABLE:
            return []
        
        detection_result = self.detect_louvain()
        communities = detection_result.communities
        
        overlaps = []
        
        for i in range(len(communities)):
            for j in range(i + 1, len(communities)):
                set_i = set(communities[i].nodes)
                set_j = set(communities[j].nodes)
                overlap = set_i & set_j
                
                if len(overlap) >= min_overlap:
                    overlaps.append({
                        'community_1': communities[i].community_id,
                        'community_2': communities[j].community_id,
                        'overlap_nodes': list(overlap),
                        'overlap_size': len(overlap),
                    })
        
        return overlaps
    
    def find_community_hubs(self, community_id: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Find hub nodes in a community.
        
        Args:
            community_id: Community ID.
            top_n: Number of top hubs to return.
            
        Returns:
            List of hub node dictionaries.
        """
        metrics = self.calculate_community_metrics(community_id)
        if not metrics:
            return []
        
        # Sort nodes by degree centrality
        sorted_nodes = sorted(
            metrics.centrality.items(),
            key=lambda x: x[1].get('degree', 0),
            reverse=True
        )
        
        hubs = []
        for node_id, centrality in sorted_nodes[:top_n]:
            hubs.append({
                'node_id': node_id,
                'degree_centrality': centrality.get('degree', 0),
                'betweenness_centrality': centrality.get('betweenness', 0),
                'closeness_centrality': centrality.get('closeness', 0),
            })
        
        return hubs
    
    def compare_communities(self, community_id_1: str, community_id_2: str) -> Dict[str, Any]:
        """
        Compare two communities.
        
        Args:
            community_id_1: First community ID.
            community_id_2: Second community ID.
            
        Returns:
            Comparison dictionary.
        """
        metrics_1 = self.calculate_community_metrics(community_id_1)
        metrics_2 = self.calculate_community_metrics(community_id_2)
        
        if not metrics_1 or not metrics_2:
            return {}
        
        return {
            'community_1': {
                'id': community_id_1,
                'size': metrics_1.size,
                'density': metrics_1.density,
                'average_degree': metrics_1.average_degree,
            },
            'community_2': {
                'id': community_id_2,
                'size': metrics_2.size,
                'density': metrics_2.density,
                'average_degree': metrics_2.average_degree,
            },
            'differences': {
                'size_diff': metrics_1.size - metrics_2.size,
                'density_diff': metrics_1.density - metrics_2.density,
                'avg_degree_diff': metrics_1.average_degree - metrics_2.average_degree,
            },
        }


# Global community detector instance
community_detector = CommunityDetector()
