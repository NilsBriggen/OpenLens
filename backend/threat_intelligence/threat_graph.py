"""
Threat Graph for OpenLens

Provides threat-specific graph operations:
- Threat graph construction
- Threat relationship analysis
- Threat propagation analysis
- Threat clustering
- Threat visualization
"""

import os
import time
import json
import threading
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

# Try to import networkx
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("NetworkX not available. Install with: pip install networkx")


@dataclass
class ThreatNode:
    """Represents a node in the threat graph."""
    node_id: str
    labels: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    threat_score: float = 0.0
    severity: str = 'medium'
    threat_types: List[str] = field(default_factory=list)
    is_ioc: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'node_id': self.node_id,
            'labels': self.labels,
            'properties': self.properties,
            'threat_score': self.threat_score,
            'severity': self.severity,
            'threat_types': self.threat_types,
            'is_ioc': self.is_ioc,
        }


@dataclass
class ThreatEdge:
    """Represents an edge in the threat graph."""
    edge_id: str
    source_id: str
    target_id: str
    rel_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    threat_score: float = 0.0
    severity: str = 'medium'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'edge_id': self.edge_id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'rel_type': self.rel_type,
            'properties': self.properties,
            'threat_score': self.threat_score,
            'severity': self.severity,
        }


@dataclass
class ThreatCluster:
    """Represents a cluster of threats."""
    cluster_id: str
    nodes: List[str] = field(default_factory=list)
    edges: List[str] = field(default_factory=list)
    size: int = 0
    threat_score: float = 0.0
    severity: str = 'medium'
    threat_types: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'cluster_id': self.cluster_id,
            'nodes': self.nodes,
            'edges': self.edges,
            'size': self.size,
            'threat_score': self.threat_score,
            'severity': self.severity,
            'threat_types': self.threat_types,
        }


@dataclass
class ThreatPath:
    """Represents a path in the threat graph."""
    path_id: str
    nodes: List[str] = field(default_factory=list)
    edges: List[str] = field(default_factory=list)
    length: int = 0
    threat_score: float = 0.0
    severity: str = 'medium'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'path_id': self.path_id,
            'nodes': self.nodes,
            'edges': self.edges,
            'length': self.length,
            'threat_score': self.threat_score,
            'severity': self.severity,
        }


@dataclass
class ThreatGraphConfig:
    """Configuration for threat graph."""
    min_threat_score: float = 0.5
    min_severity: str = 'medium'
    max_depth: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'min_threat_score': self.min_threat_score,
            'min_severity': self.min_severity,
            'max_depth': self.max_depth,
        }


class ThreatGraph:
    """
    Threat graph for OpenLens.
    
    Provides:
    - Threat graph construction
    - Threat relationship analysis
    - Threat propagation analysis
    - Threat clustering
    - Threat visualization
    """
    
    def __init__(self, config: ThreatGraphConfig = None, 
                 graph_engine=None, ioc_manager=None, 
                 threat_analyzer=None):
        """
        Initialize the threat graph.
        
        Args:
            config: ThreatGraphConfig instance.
            graph_engine: GraphEngine instance.
            ioc_manager: IOCManager instance.
            threat_analyzer: ThreatAnalyzer instance.
        """
        self.config = config or ThreatGraphConfig()
        self.graph_engine = graph_engine
        self.ioc_manager = ioc_manager
        self.threat_analyzer = threat_analyzer
        self._threat_nodes: Dict[str, ThreatNode] = {}
        self._threat_edges: Dict[str, ThreatEdge] = {}
        self._threat_graph: Optional[nx.Graph] = None
        self._lock = threading.Lock()
    
    def build_threat_graph(self, force: bool = False) -> bool:
        """
        Build the threat graph from the main graph and IOCs.
        
        Args:
            force: Force rebuild.
            
        Returns:
            True if built.
        """
        if not self.graph_engine or not self.ioc_manager:
            return False
        
        with self._lock:
            if not force and self._threat_graph:
                return True
            
            try:
                # Clear existing graph
                self._threat_nodes = {}
                self._threat_edges = {}
                self._threat_graph = nx.Graph()
                
                # Get all nodes from the main graph
                query = "MATCH (n) RETURN n"
                result = self.graph_engine.execute_query(query)
                
                if not result:
                    return False
                
                # Process nodes
                for node in result.nodes:
                    # Check if node is a threat
                    is_threat = self._is_threat_node(node)
                    threat_score = self._calculate_node_threat_score(node)
                    severity = self._determine_severity(threat_score)
                    threat_types = self._get_node_threat_types(node)
                    
                    threat_node = ThreatNode(
                        node_id=node.node_id,
                        labels=node.labels,
                        properties=node.properties,
                        threat_score=threat_score,
                        severity=severity,
                        threat_types=threat_types,
                        is_ioc=is_threat,
                    )
                    
                    self._threat_nodes[node.node_id] = threat_node
                    self._threat_graph.add_node(
                        node.node_id,
                        threat_score=threat_score,
                        severity=severity,
                        threat_types=threat_types,
                        is_ioc=is_threat,
                        labels=node.labels,
                        **node.properties
                    )
                
                # Process edges
                query = "MATCH ()-[r]->() RETURN r"
                result = self.graph_engine.execute_query(query)
                
                if result:
                    for rel in result.relationships:
                        # Check if edge is a threat
                        is_threat = self._is_threat_edge(rel)
                        threat_score = self._calculate_edge_threat_score(rel)
                        severity = self._determine_severity(threat_score)
                        
                        threat_edge = ThreatEdge(
                            edge_id=rel.rel_id,
                            source_id=rel.source_id,
                            target_id=rel.target_id,
                            rel_type=rel.rel_type,
                            properties=rel.properties,
                            threat_score=threat_score,
                            severity=severity,
                        )
                        
                        self._threat_edges[rel.rel_id] = threat_edge
                        self._threat_graph.add_edge(
                            rel.source_id,
                            rel.target_id,
                            threat_score=threat_score,
                            severity=severity,
                            rel_type=rel.rel_type,
                            **rel.properties
                        )
                
                return True
            
            except Exception as e:
                print(f"Error building threat graph: {e}")
                return False
    
    @staticmethod
    def _node_indicator(node) -> str:
        """Best-effort indicator value carried by a graph node."""
        props = getattr(node, 'properties', {}) or {}
        return str(props.get('indicator') or props.get('value') or props.get('name') or '')

    def _is_threat_node(self, node) -> bool:
        """Check if a node is a threat."""
        # Check if node is an IOC. get_ioc is keyed by indicator value, so
        # look up via the node's indicator property - node ids never match.
        if self.ioc_manager:
            indicator = self._node_indicator(node)
            if indicator and self.ioc_manager.get_ioc(indicator):
                return True
        
        # Check for threat-related labels
        threat_labels = ['Malware', 'ThreatActor', 'Vulnerability', 'Attack', 'Exploit', 'Botnet', 'C2']
        for label in node.labels:
            if label in threat_labels:
                return True
        
        # Check for threat-related properties
        threat_properties = ['malicious', 'suspicious', 'threat', 'attack', 'exploit', 'vulnerability']
        for key, value in node.properties.items():
            if any(prop in str(value).lower() for prop in threat_properties):
                return True
        
        return False
    
    def _calculate_node_threat_score(self, node) -> float:
        """Calculate threat score for a node."""
        score = 0.0
        
        # Check if node is an IOC (indicator lookup, as in _is_threat_node)
        if self.ioc_manager:
            indicator = self._node_indicator(node)
            ioc = self.ioc_manager.get_ioc(indicator) if indicator else None
            if ioc:
                # Use IOC confidence and severity
                severity_scores = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'critical': 1.0}
                score = ioc.confidence * severity_scores.get(ioc.severity, 0.5)
                return score * 100
        
        # Check for threat-related labels
        threat_labels = {
            'Malware': 0.9,
            'ThreatActor': 0.9,
            'Vulnerability': 0.8,
            'Attack': 0.8,
            'Exploit': 0.8,
            'Botnet': 0.8,
            'C2': 0.8,
        }
        
        for label in node.labels:
            if label in threat_labels:
                score = max(score, threat_labels[label])
        
        # Check for threat-related properties
        threat_properties = {
            'malicious': 0.8,
            'suspicious': 0.6,
            'threat': 0.7,
            'attack': 0.8,
            'exploit': 0.8,
            'vulnerability': 0.7,
        }
        
        for key, value in node.properties.items():
            for prop, prop_score in threat_properties.items():
                if prop in str(value).lower():
                    score = max(score, prop_score)
        
        return score * 100
    
    def _get_node_threat_types(self, node) -> List[str]:
        """Get threat types for a node."""
        threat_types = set()
        
        # Check if node is an IOC (indicator lookup, as in _is_threat_node)
        if self.ioc_manager:
            indicator = self._node_indicator(node)
            ioc = self.ioc_manager.get_ioc(indicator) if indicator else None
            if ioc and ioc.threat_type:
                threat_types.add(ioc.threat_type)
        
        # Check for threat-related labels
        for label in node.labels:
            if label in ['Malware', 'ThreatActor', 'Vulnerability', 'Attack', 'Exploit', 'Botnet', 'C2']:
                threat_types.add(label)
        
        # Check for threat-related properties
        for key, value in node.properties.items():
            if 'malware' in str(value).lower():
                threat_types.add('Malware')
            if 'phishing' in str(value).lower():
                threat_types.add('Phishing')
            if 'botnet' in str(value).lower():
                threat_types.add('Botnet')
            if 'c2' in str(value).lower():
                threat_types.add('C2')
        
        return list(threat_types)
    
    def _is_threat_edge(self, edge) -> bool:
        """Check if an edge is a threat."""
        # Check for threat-related relationship types
        threat_rel_types = ['USES', 'EXPLOITS', 'COMMUNICATES_WITH', 'CONTROLS', 'INFECTS']
        if edge.rel_type in threat_rel_types:
            return True
        
        # Check for threat-related properties
        threat_properties = ['malicious', 'suspicious', 'threat', 'attack', 'exploit']
        for key, value in edge.properties.items():
            if any(prop in str(value).lower() for prop in threat_properties):
                return True
        
        return False
    
    def _calculate_edge_threat_score(self, edge) -> float:
        """Calculate threat score for an edge."""
        score = 0.0
        
        # Check for threat-related relationship types
        threat_rel_scores = {
            'USES': 0.8,
            'EXPLOITS': 0.9,
            'COMMUNICATES_WITH': 0.7,
            'CONTROLS': 0.8,
            'INFECTS': 0.9,
        }
        
        if edge.rel_type in threat_rel_scores:
            score = threat_rel_scores[edge.rel_type]
        
        # Check for threat-related properties
        threat_properties = {
            'malicious': 0.8,
            'suspicious': 0.6,
            'threat': 0.7,
            'attack': 0.8,
            'exploit': 0.8,
        }
        
        for key, value in edge.properties.items():
            for prop, prop_score in threat_properties.items():
                if prop in str(value).lower():
                    score = max(score, prop_score)
        
        # Add score from connected nodes
        if self.graph_engine:
            # Get source and target nodes
            query = f"MATCH (n) WHERE n.id = '{edge.source_id}' RETURN n"
            result = self.graph_engine.execute_query(query)
            if result and result.nodes:
                source_score = self._calculate_node_threat_score(result.nodes[0])
                score = max(score, source_score * 0.5)
            
            query = f"MATCH (n) WHERE n.id = '{edge.target_id}' RETURN n"
            result = self.graph_engine.execute_query(query)
            if result and result.nodes:
                target_score = self._calculate_node_threat_score(result.nodes[0])
                score = max(score, target_score * 0.5)
        
        return score * 100
    
    def _determine_severity(self, score: float) -> str:
        """Determine severity based on score."""
        if score >= 90:
            return 'critical'
        elif score >= 75:
            return 'high'
        elif score >= 50:
            return 'medium'
        else:
            return 'low'
    
    def get_threat_node(self, node_id: str) -> Optional[ThreatNode]:
        """
        Get a threat node.
        
        Args:
            node_id: Node ID.
            
        Returns:
            ThreatNode or None.
        """
        with self._lock:
            return self._threat_nodes.get(node_id)
    
    def get_threat_edge(self, edge_id: str) -> Optional[ThreatEdge]:
        """
        Get a threat edge.
        
        Args:
            edge_id: Edge ID.
            
        Returns:
            ThreatEdge or None.
        """
        with self._lock:
            return self._threat_edges.get(edge_id)
    
    def find_threat_clusters(self, min_score: float = None, 
                            min_severity: str = None) -> List[ThreatCluster]:
        """
        Find clusters of threats in the graph.
        
        Args:
            min_score: Minimum threat score.
            min_severity: Minimum severity.
            
        Returns:
            List of ThreatCluster objects.
        """
        self.build_threat_graph()
        
        if not self._threat_graph:
            return []
        
        min_score = min_score or self.config.min_threat_score * 100
        min_severity = min_severity or self.config.min_severity
        
        # Filter nodes by threat score and severity
        filtered_nodes = []
        for node_id, data in self._threat_graph.nodes(data=True):
            if data.get('threat_score', 0) >= min_score:
                severity = data.get('severity', 'low')
                severity_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
                if severity_order.get(severity, 0) >= severity_order.get(min_severity, 0):
                    filtered_nodes.append(node_id)
        
        # Create subgraph with filtered nodes
        subgraph = self._threat_graph.subgraph(filtered_nodes)
        
        # Find connected components (clusters)
        clusters = []
        for i, component in enumerate(nx.connected_components(subgraph)):
            if len(component) > 1:
                # Calculate cluster metrics
                cluster_score = sum(
                    self._threat_graph.nodes[node].get('threat_score', 0)
                    for node in component
                ) / len(component)
                
                # Determine cluster severity
                severities = [
                    self._threat_graph.nodes[node].get('severity', 'low')
                    for node in component
                ]
                severity_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
                max_severity = max(severities, key=lambda x: severity_order.get(x, 0))
                
                # Collect threat types
                threat_types = set()
                for node in component:
                    threat_types.update(self._threat_graph.nodes[node].get('threat_types', []))
                
                # Collect edges
                cluster_edges = []
                for u, v in subgraph.edges(component):
                    edge_id = f"{u}_{v}"
                    if edge_id in self._threat_edges:
                        cluster_edges.append(edge_id)
                
                cluster = ThreatCluster(
                    cluster_id=f"cluster_{i}",
                    nodes=list(component),
                    edges=cluster_edges,
                    size=len(component),
                    threat_score=cluster_score,
                    severity=max_severity,
                    threat_types=list(threat_types),
                )
                clusters.append(cluster)
        
        # Sort by threat score (descending)
        clusters.sort(key=lambda x: x.threat_score, reverse=True)
        
        return clusters
    
    def find_threat_paths(self, source_id: str = None, target_id: str = None,
                         max_length: int = None, top_k: int = 5) -> List[ThreatPath]:
        """
        Find paths between threat nodes.

        Args:
            source_id: Source node ID. None means "paths among the top_k
                highest-scoring threat nodes" - a useful default instead of
                the TypeError the no-arg call used to raise.
            target_id: Target node ID (None for all paths from source).
            max_length: Maximum path length.
            top_k: How many top-scoring nodes to pair up when source_id is None.

        Returns:
            List of ThreatPath objects.
        """
        self.build_threat_graph()

        if not self._threat_graph:
            return []

        if source_id is None:
            # Pair up the highest-scoring threat nodes.
            scored = sorted(
                self._threat_graph.nodes(data=True),
                key=lambda item: item[1].get('threat_score', 0),
                reverse=True,
            )[:max(2, top_k)]
            node_ids = [node_id for node_id, _ in scored]
            paths: List[ThreatPath] = []
            for i, src in enumerate(node_ids):
                for dst in node_ids[i + 1:]:
                    paths.extend(self.find_threat_paths(src, dst, max_length))
            return paths

        max_length = max_length or self.config.max_depth
        
        paths = []
        
        if target_id:
            # Find paths to specific target
            try:
                all_paths = list(nx.all_simple_paths(
                    self._threat_graph,
                    source=source_id,
                    target=target_id,
                    cutoff=max_length
                ))
                
                for path_nodes in all_paths:
                    path_id = hashlib.sha256('_'.join(path_nodes).encode()).hexdigest()
                    
                    # Calculate path threat score
                    path_score = sum(
                        self._threat_graph.nodes[node].get('threat_score', 0)
                        for node in path_nodes
                    ) / len(path_nodes)
                    
                    # Determine path severity
                    severities = [
                        self._threat_graph.nodes[node].get('severity', 'low')
                        for node in path_nodes
                    ]
                    severity_order = {'low': 0, 'medium': 1, 'high': 2, 'critical': 3}
                    max_severity = max(severities, key=lambda x: severity_order.get(x, 0))
                    
                    # Collect edges
                    path_edges = []
                    for i in range(len(path_nodes) - 1):
                        edge_id = f"{path_nodes[i]}_{path_nodes[i+1]}"
                        if edge_id in self._threat_edges:
                            path_edges.append(edge_id)
                    
                    path = ThreatPath(
                        path_id=path_id,
                        nodes=path_nodes,
                        edges=path_edges,
                        length=len(path_nodes) - 1,
                        threat_score=path_score,
                        severity=max_severity,
                    )
                    paths.append(path)
            
            except nx.NetworkXNoPath:
                pass
        else:
            # Find all paths from source
            for target in self._threat_graph.nodes():
                if target != source_id:
                    paths.extend(self.find_threat_paths(source_id, target, max_length))
        
        # Sort by threat score (descending)
        paths.sort(key=lambda x: x.threat_score, reverse=True)
        
        return paths
    
    def find_threat_propagation(self, node_id: str, max_depth: int = None) -> Dict[str, Any]:
        """
        Analyze threat propagation from a node.
        
        Args:
            node_id: Starting node ID.
            max_depth: Maximum depth to analyze.
            
        Returns:
            Propagation analysis results.
        """
        self.build_threat_graph()
        
        if not self._threat_graph or node_id not in self._threat_graph:
            return {}
        
        max_depth = max_depth or self.config.max_depth
        
        # Find all nodes reachable within max_depth
        reachable_nodes = set()
        visited = set()
        queue = [(node_id, 0)]
        
        while queue:
            current_node, depth = queue.pop(0)
            
            if current_node in visited or depth > max_depth:
                continue
            
            visited.add(current_node)
            reachable_nodes.add(current_node)
            
            # Add neighbors
            for neighbor in self._threat_graph.neighbors(current_node):
                if neighbor not in visited:
                    queue.append((neighbor, depth + 1))
        
        # Calculate propagation metrics
        total_reachable = len(reachable_nodes)
        
        # Calculate average threat score
        threat_scores = [
            self._threat_graph.nodes[node].get('threat_score', 0)
            for node in reachable_nodes
        ]
        avg_threat_score = sum(threat_scores) / len(threat_scores) if threat_scores else 0
        
        # Count by severity
        severities = [
            self._threat_graph.nodes[node].get('severity', 'low')
            for node in reachable_nodes
        ]
        severity_counts = defaultdict(int)
        for severity in severities:
            severity_counts[severity] += 1
        
        # Count by threat type
        threat_types = set()
        for node in reachable_nodes:
            threat_types.update(self._threat_graph.nodes[node].get('threat_types', []))
        
        return {
            'node_id': node_id,
            'total_reachable': total_reachable,
            'max_depth': max_depth,
            'avg_threat_score': avg_threat_score,
            'severity_counts': dict(severity_counts),
            'threat_types': list(threat_types),
            'reachable_nodes': list(reachable_nodes),
        }
    
    def get_threat_graph_data(self) -> Dict[str, Any]:
        """
        Get threat graph data for visualization.
        
        Returns:
            Dictionary with nodes and edges.
        """
        self.build_threat_graph()
        
        if not self._threat_graph:
            return {'nodes': [], 'edges': []}
        
        nodes = []
        for node_id, data in self._threat_graph.nodes(data=True):
            nodes.append({
                'id': node_id,
                'labels': data.get('labels', []),
                'threat_score': data.get('threat_score', 0),
                'severity': data.get('severity', 'low'),
                'threat_types': data.get('threat_types', []),
                'is_ioc': data.get('is_ioc', False),
                'properties': {k: v for k, v in data.items() if k not in ['labels', 'threat_score', 'severity', 'threat_types', 'is_ioc']},
            })
        
        edges = []
        for source, target, data in self._threat_graph.edges(data=True):
            edges.append({
                'id': f"{source}_{target}",
                'source': source,
                'target': target,
                'type': data.get('rel_type', ''),
                'threat_score': data.get('threat_score', 0),
                'severity': data.get('severity', 'low'),
                'properties': {k: v for k, v in data.items() if k not in ['rel_type', 'threat_score', 'severity']},
            })
        
        return {
            'nodes': nodes,
            'edges': edges,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get threat graph statistics.
        
        Returns:
            Dictionary with statistics.
        """
        self.build_threat_graph()
        
        if not self._threat_graph:
            return {}
        
        stats = {
            'total_nodes': len(self._threat_nodes),
            'total_edges': len(self._threat_edges),
            'by_severity': defaultdict(int),
            'by_threat_type': defaultdict(int),
            'by_indicator_type': defaultdict(int),
            'avg_threat_score': 0.0,
        }
        
        # Calculate node statistics
        threat_scores = []
        for node in self._threat_nodes.values():
            stats['by_severity'][node.severity] += 1
            for threat_type in node.threat_types:
                stats['by_threat_type'][threat_type] += 1
            threat_scores.append(node.threat_score)
        
        if threat_scores:
            stats['avg_threat_score'] = sum(threat_scores) / len(threat_scores)
        
        # Calculate edge statistics
        for edge in self._threat_edges.values():
            stats['by_severity'][edge.severity] += 1
        
        # Convert defaultdict to dict
        for key in stats:
            if isinstance(stats[key], defaultdict):
                stats[key] = dict(stats[key])
        
        return stats
    
    def export_to_json(self) -> str:
        """
        Export threat graph data to JSON.
        
        Returns:
            JSON string.
        """
        data = {
            'nodes': [n.to_dict() for n in self._threat_nodes.values()],
            'edges': [e.to_dict() for e in self._threat_edges.values()],
            'config': self.config.to_dict(),
        }
        
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: str) -> bool:
        """
        Import threat graph data from JSON.
        
        Args:
            json_data: JSON string.
            
        Returns:
            True if imported.
        """
        try:
            data = json.loads(json_data)
            
            # Import nodes
            self._threat_nodes = {}
            for node_data in data.get('nodes', []):
                node = ThreatNode(
                    node_id=node_data['node_id'],
                    labels=node_data.get('labels', []),
                    properties=node_data.get('properties', {}),
                    threat_score=node_data.get('threat_score', 0.0),
                    severity=node_data.get('severity', 'medium'),
                    threat_types=node_data.get('threat_types', []),
                    is_ioc=node_data.get('is_ioc', False),
                )
                self._threat_nodes[node.node_id] = node
            
            # Import edges
            self._threat_edges = {}
            for edge_data in data.get('edges', []):
                edge = ThreatEdge(
                    edge_id=edge_data['edge_id'],
                    source_id=edge_data['source_id'],
                    target_id=edge_data['target_id'],
                    rel_type=edge_data.get('rel_type', ''),
                    properties=edge_data.get('properties', {}),
                    threat_score=edge_data.get('threat_score', 0.0),
                    severity=edge_data.get('severity', 'medium'),
                )
                self._threat_edges[edge.edge_id] = edge
            
            # Import config
            config_data = data.get('config', {})
            self.config = ThreatGraphConfig(
                min_threat_score=config_data.get('min_threat_score', 0.5),
                min_severity=config_data.get('min_severity', 'medium'),
                max_depth=config_data.get('max_depth', 5),
            )
            
            # Rebuild graph
            self._threat_graph = None
            self.build_threat_graph()
            
            return True
        
        except Exception as e:
            print(f"Error importing threat graph data: {e}")
            return False


# Global threat graph instance
threat_graph = ThreatGraph()
