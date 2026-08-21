"""
Path Finding Module for OpenLens

Provides advanced path finding capabilities:
- Shortest path algorithms
- All paths finding
- Path with constraints
- Temporal path finding
- Weighted path finding
- Path analysis and metrics
"""

import time
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict, deque
import heapq

# Try to import networkx
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("NetworkX not available. Install with: pip install networkx")


@dataclass
class Path:
    """Represents a path in the graph."""
    nodes: List[str] = field(default_factory=list)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    length: int = 0
    weight: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'nodes': self.nodes,
            'edges': self.edges,
            'length': self.length,
            'weight': self.weight,
        }


@dataclass
class PathResult:
    """Result of path finding operation."""
    source: str
    target: str
    paths: List[Path] = field(default_factory=list)
    shortest_path: Optional[Path] = None
    all_paths: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'source': self.source,
            'target': self.target,
            'paths': [p.to_dict() for p in self.paths],
            'shortest_path': self.shortest_path.to_dict() if self.shortest_path else None,
            'all_paths': self.all_paths,
        }


@dataclass
class PathConstraints:
    """Constraints for path finding."""
    max_length: int = 10
    max_weight: float = float('inf')
    required_labels: List[str] = field(default_factory=list)
    forbidden_labels: List[str] = field(default_factory=list)
    required_relationships: List[str] = field(default_factory=list)
    forbidden_relationships: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'max_length': self.max_length,
            'max_weight': self.max_weight,
            'required_labels': self.required_labels,
            'forbidden_labels': self.forbidden_labels,
            'required_relationships': self.required_relationships,
            'forbidden_relationships': self.forbidden_relationships,
        }


class PathFinder:
    """
    Path finder for graph data.
    
    Provides advanced path finding capabilities for OSINT analysis.
    """
    
    def __init__(self, graph_engine=None):
        """
        Initialize the path finder.
        
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
            
            # Add nodes with labels
            for node in result.nodes:
                self._graph.add_node(
                    node.node_id,
                    labels=node.labels,
                    **node.properties
                )
            
            # Add edges with types
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
    
    def find_shortest_path(self, source: str, target: str, 
                          weight: str = None) -> Optional[Path]:
        """
        Find the shortest path between two nodes.
        
        Args:
            source: Source node ID.
            target: Target node ID.
            weight: Edge weight attribute.
            
        Returns:
            Path or None if no path exists.
        """
        if not NETWORKX_AVAILABLE:
            return None
        
        graph = self._get_networkx_graph()
        if not graph:
            return None
        
        if source not in graph or target not in graph:
            return None
        
        try:
            if weight:
                path_nodes = nx.shortest_path(graph, source, target, weight=weight)
            else:
                path_nodes = nx.shortest_path(graph, source, target)
            
            path_edges = [(path_nodes[i], path_nodes[i+1]) for i in range(len(path_nodes) - 1)]
            path_weight = sum(
                graph[path_edges[i][0]][path_edges[i][1]].get(weight, 1)
                for i in range(len(path_edges))
            ) if weight else len(path_edges)
            
            return Path(
                nodes=path_nodes,
                edges=path_edges,
                length=len(path_edges),
                weight=path_weight,
            )
        
        except nx.NetworkXNoPath:
            return None
        except Exception as e:
            print(f"Shortest path error: {e}")
            return None
    
    def find_all_paths(self, source: str, target: str, 
                       max_length: int = 10) -> List[Path]:
        """
        Find all simple paths between two nodes.
        
        Args:
            source: Source node ID.
            target: Target node ID.
            max_length: Maximum path length.
            
        Returns:
            List of Path objects.
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
            
            for path_nodes in all_paths:
                path_edges = [(path_nodes[i], path_nodes[i+1]) for i in range(len(path_nodes) - 1)]
                results.append(Path(
                    nodes=path_nodes,
                    edges=path_edges,
                    length=len(path_edges),
                ))
            
            return results
        
        except Exception as e:
            print(f"All paths error: {e}")
            return []
    
    def find_paths_with_constraints(self, source: str, target: str,
                                   constraints: PathConstraints = None) -> List[Path]:
        """
        Find paths with constraints.
        
        Args:
            source: Source node ID.
            target: Target node ID.
            constraints: PathConstraints object.
            
        Returns:
            List of Path objects.
        """
        if not NETWORKX_AVAILABLE:
            return []
        
        graph = self._get_networkx_graph()
        if not graph:
            return []
        
        if source not in graph or target not in graph:
            return []
        
        constraints = constraints or PathConstraints()
        
        try:
            all_paths = list(nx.all_simple_paths(
                graph, source, target, 
                cutoff=constraints.max_length
            ))
            
            valid_paths = []
            
            for path_nodes in all_paths:
                # Check path length
                if len(path_nodes) - 1 > constraints.max_length:
                    continue
                
                # Check path weight
                path_edges = [(path_nodes[i], path_nodes[i+1]) for i in range(len(path_nodes) - 1)]
                path_weight = sum(
                    graph[edge[0]][edge[1]].get('weight', 1)
                    for edge in path_edges
                )
                if path_weight > constraints.max_weight:
                    continue
                
                # Check node labels
                valid = True
                for node in path_nodes:
                    node_labels = graph.nodes[node].get('labels', [])
                    
                    # Check required labels
                    for req_label in constraints.required_labels:
                        if req_label not in node_labels:
                            valid = False
                            break
                    
                    if not valid:
                        break
                    
                    # Check forbidden labels
                    for forb_label in constraints.forbidden_labels:
                        if forb_label in node_labels:
                            valid = False
                            break
                    
                    if not valid:
                        break
                
                if not valid:
                    continue
                
                # Check edge types
                for edge in path_edges:
                    edge_type = graph.edges[edge].get('type', '')
                    
                    # Check required relationships
                    for req_rel in constraints.required_relationships:
                        if req_rel != edge_type:
                            valid = False
                            break
                    
                    if not valid:
                        break
                    
                    # Check forbidden relationships
                    for forb_rel in constraints.forbidden_relationships:
                        if forb_rel == edge_type:
                            valid = False
                            break
                    
                    if not valid:
                        break
                
                if valid:
                    valid_paths.append(Path(
                        nodes=path_nodes,
                        edges=path_edges,
                        length=len(path_edges),
                        weight=path_weight,
                    ))
            
            return valid_paths
        
        except Exception as e:
            print(f"Paths with constraints error: {e}")
            return []
    
    def find_shortest_path_dijkstra(self, source: str, target: str,
                                    weight: str = 'weight') -> Optional[Path]:
        """
        Find shortest path using Dijkstra's algorithm.
        
        Args:
            source: Source node ID.
            target: Target node ID.
            weight: Edge weight attribute.
            
        Returns:
            Path or None if no path exists.
        """
        if not NETWORKX_AVAILABLE:
            return None
        
        graph = self._get_networkx_graph()
        if not graph:
            return None
        
        if source not in graph or target not in graph:
            return None
        
        try:
            path_nodes = nx.dijkstra_path(graph, source, target, weight=weight)
            path_edges = [(path_nodes[i], path_nodes[i+1]) for i in range(len(path_nodes) - 1)]
            path_weight = sum(
                graph[edge[0]][edge[1]].get(weight, 1)
                for edge in path_edges
            )
            
            return Path(
                nodes=path_nodes,
                edges=path_edges,
                length=len(path_edges),
                weight=path_weight,
            )
        
        except nx.NetworkXNoPath:
            return None
        except Exception as e:
            print(f"Dijkstra path error: {e}")
            return None
    
    def find_shortest_path_astar(self, source: str, target: str,
                                 weight: str = 'weight',
                                 heuristic=None) -> Optional[Path]:
        """
        Find shortest path using A* algorithm.
        
        Args:
            source: Source node ID.
            target: Target node ID.
            weight: Edge weight attribute.
            heuristic: Heuristic function for A*.
            
        Returns:
            Path or None if no path exists.
        """
        if not NETWORKX_AVAILABLE:
            return None
        
        graph = self._get_networkx_graph()
        if not graph:
            return None
        
        if source not in graph or target not in graph:
            return None
        
        try:
            if heuristic is None:
                # Default heuristic: straight-line distance (if nodes have coordinates)
                def heuristic(u, v):
                    try:
                        u_pos = graph.nodes[u].get('position', (0, 0))
                        v_pos = graph.nodes[v].get('position', (0, 0))
                        return math.sqrt((u_pos[0] - v_pos[0])**2 + (u_pos[1] - v_pos[1])**2)
                    except:
                        return 1
            
            path_nodes = nx.astar_path(graph, source, target, heuristic=heuristic, weight=weight)
            path_edges = [(path_nodes[i], path_nodes[i+1]) for i in range(len(path_nodes) - 1)]
            path_weight = sum(
                graph[edge[0]][edge[1]].get(weight, 1)
                for edge in path_edges
            )
            
            return Path(
                nodes=path_nodes,
                edges=path_edges,
                length=len(path_edges),
                weight=path_weight,
            )
        
        except nx.NetworkXNoPath:
            return None
        except Exception as e:
            print(f"A* path error: {e}")
            return None
    
    def find_negative_weight_path(self, source: str, target: str,
                                  weight: str = 'weight') -> Optional[Path]:
        """
        Find shortest path in graph with negative weights using Bellman-Ford.
        
        Args:
            source: Source node ID.
            target: Target node ID.
            weight: Edge weight attribute.
            
        Returns:
            Path or None if no path exists or negative cycle detected.
        """
        if not NETWORKX_AVAILABLE:
            return None
        
        graph = self._get_networkx_graph()
        if not graph:
            return None
        
        if source not in graph or target not in graph:
            return None
        
        try:
            # Check for negative cycles
            has_negative_cycle = nx.negative_cycle(graph, weight=weight)
            if has_negative_cycle:
                print("Graph contains negative weight cycle")
                return None
            
            path_nodes = nx.bellman_ford_path(graph, source, target, weight=weight)
            path_edges = [(path_nodes[i], path_nodes[i+1]) for i in range(len(path_nodes) - 1)]
            path_weight = sum(
                graph[edge[0]][edge[1]].get(weight, 1)
                for edge in path_edges
            )
            
            return Path(
                nodes=path_nodes,
                edges=path_edges,
                length=len(path_edges),
                weight=path_weight,
            )
        
        except nx.NetworkXNoPath:
            return None
        except Exception as e:
            print(f"Negative weight path error: {e}")
            return None
    
    def find_k_shortest_paths(self, source: str, target: str, k: int = 3,
                             weight: str = None) -> List[Path]:
        """
        Find k shortest paths between two nodes.
        
        Args:
            source: Source node ID.
            target: Target node ID.
            k: Number of shortest paths to find.
            weight: Edge weight attribute.
            
        Returns:
            List of Path objects.
        """
        if not NETWORKX_AVAILABLE:
            return []
        
        graph = self._get_networkx_graph()
        if not graph:
            return []
        
        if source not in graph or target not in graph:
            return []
        
        try:
            if weight:
                paths = list(nx.shortest_simple_paths(graph, source, target, weight=weight))
            else:
                paths = list(nx.shortest_simple_paths(graph, source, target))
            
            results = []
            for path_nodes in paths[:k]:
                path_edges = [(path_nodes[i], path_nodes[i+1]) for i in range(len(path_nodes) - 1)]
                path_weight = sum(
                    graph[edge[0]][edge[1]].get(weight, 1)
                    for edge in path_edges
                ) if weight else len(path_edges)
                
                results.append(Path(
                    nodes=path_nodes,
                    edges=path_edges,
                    length=len(path_edges),
                    weight=path_weight,
                ))
            
            return results
        
        except Exception as e:
            print(f"K shortest paths error: {e}")
            return []
    
    def find_paths_by_pattern(self, pattern: List[str]) -> List[Path]:
        """
        Find paths matching a specific pattern of node labels.
        
        Args:
            pattern: List of node labels to match (e.g., ['Person', 'Organization', 'Location'])
            
        Returns:
            List of Path objects.
        """
        if not self.graph_engine:
            return []
        
        if not pattern or len(pattern) < 2:
            return []
        
        try:
            # Build Cypher query for pattern matching
            query_parts = []
            params = {}
            
            for i, label in enumerate(pattern):
                var = f"n{i}"
                query_parts.append(f"({var}:{label})")
                
                if i > 0:
                    query_parts.append(f"-[:*]->")
            
            query = "MATCH " + "".join(query_parts) + " RETURN " + ", ".join([f"n{i}" for i in range(len(pattern))])
            
            result = self.graph_engine.execute_query(query)
            if not result or not result.nodes:
                return []
            
            # Group nodes by path
            paths = []
            current_path = []
            
            for node in result.nodes:
                current_path.append(node.node_id)
                if len(current_path) == len(pattern):
                    paths.append(Path(
                        nodes=current_path.copy(),
                        length=len(current_path) - 1,
                    ))
                    current_path = []
            
            return paths
        
        except Exception as e:
            print(f"Pattern path finding error: {e}")
            return []
    
    def find_paths_with_relationship_pattern(self, node_pattern: List[str],
                                              rel_pattern: List[str]) -> List[Path]:
        """
        Find paths matching specific node and relationship patterns.
        
        Args:
            node_pattern: List of node labels.
            rel_pattern: List of relationship types.
            
        Returns:
            List of Path objects.
        """
        if not self.graph_engine:
            return []
        
        if len(node_pattern) != len(rel_pattern) + 1:
            return []
        
        try:
            # Build Cypher query
            query_parts = [f"(n0:{node_pattern[0]})"]
            
            for i, rel_type in enumerate(rel_pattern):
                query_parts.append(f"-[:{rel_type}]->(n{i+1}:{node_pattern[i+1]})")
            
            query = "MATCH " + "".join(query_parts) + " RETURN " + ", ".join([f"n{i}" for i in range(len(node_pattern))])
            
            result = self.graph_engine.execute_query(query)
            if not result or not result.nodes:
                return []
            
            # Group nodes by path
            paths = []
            current_path = []
            
            for node in result.nodes:
                current_path.append(node.node_id)
                if len(current_path) == len(node_pattern):
                    paths.append(Path(
                        nodes=current_path.copy(),
                        length=len(current_path) - 1,
                    ))
                    current_path = []
            
            return paths
        
        except Exception as e:
            print(f"Relationship pattern path finding error: {e}")
            return []


# Global path finder instance
path_finder = PathFinder()


# Import math for A* heuristic
import math
