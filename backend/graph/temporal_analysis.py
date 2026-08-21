"""
Temporal Analysis Module for OpenLens

Provides temporal graph analysis capabilities:
- Temporal graph construction
- Time-based queries
- Temporal patterns
- Evolution analysis
- Time series analysis
"""

import time
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter

# Try to import networkx
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    print("NetworkX not available. Install with: pip install networkx")

# Try to import pandas
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Pandas not available. Install with: pip install pandas")

# Try to import numpy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("NumPy not available. Install with: pip install numpy")


@dataclass
class TemporalNode:
    """Represents a node with temporal information."""
    node_id: str
    labels: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamps: List[datetime] = field(default_factory=list)
    first_seen: datetime = None
    last_seen: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.node_id,
            'labels': self.labels,
            'properties': self.properties,
            'timestamps': [t.isoformat() for t in self.timestamps],
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
        }


@dataclass
class TemporalEdge:
    """Represents an edge with temporal information."""
    source_id: str
    target_id: str
    rel_type: str
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamps: List[datetime] = field(default_factory=list)
    first_seen: datetime = None
    last_seen: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'type': self.rel_type,
            'properties': self.properties,
            'timestamps': [t.isoformat() for t in self.timestamps],
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
        }


@dataclass
class TemporalGraph:
    """Represents a temporal graph."""
    nodes: List[TemporalNode] = field(default_factory=list)
    edges: List[TemporalEdge] = field(default_factory=list)
    time_range: Tuple[datetime, datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'nodes': [n.to_dict() for n in self.nodes],
            'edges': [e.to_dict() for e in self.edges],
            'time_range': [
                self.time_range[0].isoformat() if self.time_range and self.time_range[0] else None,
                self.time_range[1].isoformat() if self.time_range and self.time_range[1] else None,
            ],
        }


@dataclass
class TemporalPattern:
    """Represents a temporal pattern."""
    pattern_type: str
    nodes: List[str] = field(default_factory=list)
    edges: List[Tuple[str, str]] = field(default_factory=list)
    timestamps: List[datetime] = field(default_factory=list)
    frequency: int = 0
    period: float = 0.0  # in days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'pattern_type': self.pattern_type,
            'nodes': self.nodes,
            'edges': self.edges,
            'timestamps': [t.isoformat() for t in self.timestamps],
            'frequency': self.frequency,
            'period': self.period,
        }


@dataclass
class TemporalMetrics:
    """Temporal metrics for the graph."""
    time_range: Tuple[datetime, datetime] = None
    num_nodes: int = 0
    num_edges: int = 0
    node_growth_rate: float = 0.0
    edge_growth_rate: float = 0.0
    average_node_lifetime: float = 0.0  # in days
    average_edge_lifetime: float = 0.0  # in days
    activity_patterns: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'time_range': [
                self.time_range[0].isoformat() if self.time_range and self.time_range[0] else None,
                self.time_range[1].isoformat() if self.time_range and self.time_range[1] else None,
            ],
            'num_nodes': self.num_nodes,
            'num_edges': self.num_edges,
            'node_growth_rate': self.node_growth_rate,
            'edge_growth_rate': self.edge_growth_rate,
            'average_node_lifetime': self.average_node_lifetime,
            'average_edge_lifetime': self.average_edge_lifetime,
            'activity_patterns': self.activity_patterns,
        }


class TemporalAnalyzer:
    """
    Temporal analyzer for graph data.
    
    Provides temporal analysis capabilities for OSINT data.
    """
    
    def __init__(self, graph_engine=None):
        """
        Initialize the temporal analyzer.
        
        Args:
            graph_engine: GraphEngine instance.
        """
        self.graph_engine = graph_engine
        self._temporal_graph = None
        self._last_updated = 0
        self._cache_ttl = 300  # 5 minutes
    
    def _get_temporal_graph(self, force_refresh: bool = False) -> Optional[TemporalGraph]:
        """
        Get the temporal graph.
        
        Args:
            force_refresh: Force refresh from database.
            
        Returns:
            TemporalGraph or None.
        """
        if not self.graph_engine:
            return None
        
        current_time = time.time()
        if not force_refresh and self._temporal_graph and (current_time - self._last_updated) < self._cache_ttl:
            return self._temporal_graph
        
        try:
            # Fetch all nodes with timestamps
            query = "MATCH (n) RETURN n"
            result = self.graph_engine.execute_query(query)
            
            if not result:
                return None
            
            temporal_nodes = []
            all_timestamps = []
            
            for node in result.nodes:
                timestamps = []
                first_seen = None
                last_seen = None
                
                # Extract timestamps from properties
                for key, value in node.properties.items():
                    if isinstance(value, str) and self._is_timestamp(value):
                        try:
                            ts = datetime.fromisoformat(value)
                            timestamps.append(ts)
                            if first_seen is None or ts < first_seen:
                                first_seen = ts
                            if last_seen is None or ts > last_seen:
                                last_seen = ts
                        except:
                            pass
                    elif isinstance(value, (int, float)):
                        # Assume Unix timestamp
                        try:
                            ts = datetime.fromtimestamp(value)
                            timestamps.append(ts)
                            if first_seen is None or ts < first_seen:
                                first_seen = ts
                            if last_seen is None or ts > last_seen:
                                last_seen = ts
                        except:
                            pass
                
                if timestamps:
                    all_timestamps.extend(timestamps)
                
                temporal_nodes.append(TemporalNode(
                    node_id=node.node_id,
                    labels=node.labels,
                    properties=node.properties,
                    timestamps=timestamps,
                    first_seen=first_seen,
                    last_seen=last_seen,
                ))
            
            # Fetch all edges with timestamps
            query = "MATCH ()-[r]->() RETURN r"
            result = self.graph_engine.execute_query(query)
            
            temporal_edges = []
            
            if result:
                for rel in result.relationships:
                    timestamps = []
                    first_seen = None
                    last_seen = None
                    
                    # Extract timestamps from properties
                    for key, value in rel.properties.items():
                        if isinstance(value, str) and self._is_timestamp(value):
                            try:
                                ts = datetime.fromisoformat(value)
                                timestamps.append(ts)
                                if first_seen is None or ts < first_seen:
                                    first_seen = ts
                                if last_seen is None or ts > last_seen:
                                    last_seen = ts
                            except:
                                pass
                        elif isinstance(value, (int, float)):
                            # Assume Unix timestamp
                            try:
                                ts = datetime.fromtimestamp(value)
                                timestamps.append(ts)
                                if first_seen is None or ts < first_seen:
                                    first_seen = ts
                                if last_seen is None or ts > last_seen:
                                    last_seen = ts
                            except:
                                pass
                    
                    if timestamps:
                        all_timestamps.extend(timestamps)
                    
                    temporal_edges.append(TemporalEdge(
                        source_id=rel.source_id,
                        target_id=rel.target_id,
                        rel_type=rel.rel_type,
                        properties=rel.properties,
                        timestamps=timestamps,
                        first_seen=first_seen,
                        last_seen=last_seen,
                    ))
            
            # Determine time range
            time_range = None
            if all_timestamps:
                time_range = (min(all_timestamps), max(all_timestamps))
            
            self._temporal_graph = TemporalGraph(
                nodes=temporal_nodes,
                edges=temporal_edges,
                time_range=time_range,
            )
            
            self._last_updated = current_time
            return self._temporal_graph
        
        except Exception as e:
            print(f"Error building temporal graph: {e}")
            return None
    
    def _is_timestamp(self, value: str) -> bool:
        """Check if a string value is a timestamp."""
        timestamp_patterns = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d',
            '%d-%m-%Y',
            '%m/%d/%Y',
        ]
        
        for pattern in timestamp_patterns:
            try:
                datetime.strptime(value, pattern)
                return True
            except:
                continue
        
        return False
    
    def get_temporal_graph(self) -> Optional[TemporalGraph]:
        """
        Get the temporal graph.
        
        Returns:
            TemporalGraph or None.
        """
        return self._get_temporal_graph()
    
    def query_time_slice(self, start_time: datetime, end_time: datetime) -> Optional[TemporalGraph]:
        """
        Query a time slice of the graph.
        
        Args:
            start_time: Start of time slice.
            end_time: End of time slice.
            
        Returns:
            TemporalGraph for the time slice.
        """
        temporal_graph = self._get_temporal_graph()
        if not temporal_graph:
            return None
        
        nodes = []
        edges = []
        all_timestamps = []
        
        for node in temporal_graph.nodes:
            # Filter timestamps within the time slice
            filtered_timestamps = [
                t for t in node.timestamps
                if start_time <= t <= end_time
            ]
            
            if filtered_timestamps:
                first_seen = min(filtered_timestamps)
                last_seen = max(filtered_timestamps)
                all_timestamps.extend(filtered_timestamps)
                
                nodes.append(TemporalNode(
                    node_id=node.node_id,
                    labels=node.labels,
                    properties=node.properties,
                    timestamps=filtered_timestamps,
                    first_seen=first_seen,
                    last_seen=last_seen,
                ))
        
        for edge in temporal_graph.edges:
            # Filter timestamps within the time slice
            filtered_timestamps = [
                t for t in edge.timestamps
                if start_time <= t <= end_time
            ]
            
            if filtered_timestamps:
                first_seen = min(filtered_timestamps)
                last_seen = max(filtered_timestamps)
                all_timestamps.extend(filtered_timestamps)
                
                edges.append(TemporalEdge(
                    source_id=edge.source_id,
                    target_id=edge.target_id,
                    rel_type=edge.rel_type,
                    properties=edge.properties,
                    timestamps=filtered_timestamps,
                    first_seen=first_seen,
                    last_seen=last_seen,
                ))
        
        time_range = None
        if all_timestamps:
            time_range = (min(all_timestamps), max(all_timestamps))
        
        return TemporalGraph(
            nodes=nodes,
            edges=edges,
            time_range=time_range,
        )
    
    def find_temporal_patterns(self, min_frequency: int = 2, 
                               max_period: float = 30.0) -> List[TemporalPattern]:
        """
        Find temporal patterns in the graph.
        
        Args:
            min_frequency: Minimum frequency to consider as a pattern.
            max_period: Maximum period in days to consider.
            
        Returns:
            List of TemporalPattern objects.
        """
        temporal_graph = self._get_temporal_graph()
        if not temporal_graph:
            return []
        
        patterns = []
        
        # Find patterns in node activity
        node_activity = defaultdict(list)
        for node in temporal_graph.nodes:
            for ts in node.timestamps:
                node_activity[node.node_id].append(ts)
        
        # Find patterns in edge activity
        edge_activity = defaultdict(list)
        for edge in temporal_graph.edges:
            for ts in edge.timestamps:
                edge_key = (edge.source_id, edge.target_id, edge.rel_type)
                edge_activity[edge_key].append(ts)
        
        # Detect periodic patterns in node activity
        for node_id, timestamps in node_activity.items():
            if len(timestamps) >= min_frequency:
                # Sort timestamps
                timestamps.sort()
                
                # Calculate intervals
                intervals = []
                for i in range(1, len(timestamps)):
                    interval = (timestamps[i] - timestamps[i-1]).total_seconds() / 86400  # in days
                    intervals.append(interval)
                
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    
                    if avg_interval <= max_period:
                        patterns.append(TemporalPattern(
                            pattern_type='node_periodic_activity',
                            nodes=[node_id],
                            timestamps=timestamps,
                            frequency=len(timestamps),
                            period=avg_interval,
                        ))
        
        # Detect periodic patterns in edge activity
        for edge_key, timestamps in edge_activity.items():
            if len(timestamps) >= min_frequency:
                timestamps.sort()
                
                intervals = []
                for i in range(1, len(timestamps)):
                    interval = (timestamps[i] - timestamps[i-1]).total_seconds() / 86400
                    intervals.append(interval)
                
                if intervals:
                    avg_interval = sum(intervals) / len(intervals)
                    
                    if avg_interval <= max_period:
                        patterns.append(TemporalPattern(
                            pattern_type='edge_periodic_activity',
                            nodes=list(edge_key[:2]),
                            edges=[edge_key],
                            timestamps=timestamps,
                            frequency=len(timestamps),
                            period=avg_interval,
                        ))
        
        # Detect co-occurrence patterns
        co_occurrence = defaultdict(lambda: defaultdict(int))
        
        for node in temporal_graph.nodes:
            for ts in node.timestamps:
                # Find other nodes active at the same time
                for other_node in temporal_graph.nodes:
                    if other_node.node_id != node.node_id:
                        for other_ts in other_node.timestamps:
                            if abs((ts - other_ts).total_seconds()) < 3600:  # Within 1 hour
                                co_occurrence[node.node_id][other_node.node_id] += 1
        
        for node_id, neighbors in co_occurrence.items():
            for neighbor_id, count in neighbors.items():
                if count >= min_frequency:
                    patterns.append(TemporalPattern(
                        pattern_type='node_co_occurrence',
                        nodes=[node_id, neighbor_id],
                        timestamps=[],
                        frequency=count,
                        period=0.0,
                    ))
        
        return patterns
    
    def calculate_temporal_metrics(self) -> TemporalMetrics:
        """
        Calculate temporal metrics for the graph.
        
        Returns:
            TemporalMetrics object.
        """
        temporal_graph = self._get_temporal_graph()
        if not temporal_graph:
            return TemporalMetrics()
        
        metrics = TemporalMetrics()
        
        try:
            metrics.time_range = temporal_graph.time_range
            metrics.num_nodes = len(temporal_graph.nodes)
            metrics.num_edges = len(temporal_graph.edges)
            
            if metrics.num_nodes > 1:
                # Calculate node growth rate
                if temporal_graph.time_range:
                    time_span = (temporal_graph.time_range[1] - temporal_graph.time_range[0]).total_seconds() / 86400
                    if time_span > 0:
                        metrics.node_growth_rate = metrics.num_nodes / time_span
            
            if metrics.num_edges > 1:
                # Calculate edge growth rate
                if temporal_graph.time_range:
                    time_span = (temporal_graph.time_range[1] - temporal_graph.time_range[0]).total_seconds() / 86400
                    if time_span > 0:
                        metrics.edge_growth_rate = metrics.num_edges / time_span
            
            # Calculate average node lifetime
            node_lifetimes = []
            for node in temporal_graph.nodes:
                if node.first_seen and node.last_seen:
                    lifetime = (node.last_seen - node.first_seen).total_seconds() / 86400
                    node_lifetimes.append(lifetime)
            
            if node_lifetimes:
                metrics.average_node_lifetime = sum(node_lifetimes) / len(node_lifetimes)
            
            # Calculate average edge lifetime
            edge_lifetimes = []
            for edge in temporal_graph.edges:
                if edge.first_seen and edge.last_seen:
                    lifetime = (edge.last_seen - edge.first_seen).total_seconds() / 86400
                    edge_lifetimes.append(lifetime)
            
            if edge_lifetimes:
                metrics.average_edge_lifetime = sum(edge_lifetimes) / len(edge_lifetimes)
            
            # Calculate activity patterns (hour of day)
            activity_by_hour = Counter()
            for node in temporal_graph.nodes:
                for ts in node.timestamps:
                    activity_by_hour[ts.hour] += 1
            
            metrics.activity_patterns = dict(activity_by_hour)
        
        except Exception as e:
            print(f"Temporal metrics calculation error: {e}")
        
        return metrics
    
    def find_temporal_clusters(self, time_window: float = 1.0) -> List[List[str]]:
        """
        Find temporal clusters (nodes active within the same time window).
        
        Args:
            time_window: Time window in days.
            
        Returns:
            List of clusters (each cluster is a list of node IDs).
        """
        temporal_graph = self._get_temporal_graph()
        if not temporal_graph:
            return []
        
        clusters = []
        
        try:
            # Sort all timestamps
            all_events = []
            for node in temporal_graph.nodes:
                for ts in node.timestamps:
                    all_events.append((ts, node.node_id))
            
            all_events.sort()
            
            # Find clusters
            current_cluster = set()
            current_window_start = None
            
            for ts, node_id in all_events:
                if current_window_start is None:
                    current_window_start = ts
                    current_cluster.add(node_id)
                else:
                    if (ts - current_window_start).total_seconds() / 86400 <= time_window:
                        current_cluster.add(node_id)
                    else:
                        # Start new cluster
                        if len(current_cluster) > 1:
                            clusters.append(list(current_cluster))
                        current_cluster = {node_id}
                        current_window_start = ts
            
            # Add last cluster
            if len(current_cluster) > 1:
                clusters.append(list(current_cluster))
        
        except Exception as e:
            print(f"Temporal clustering error: {e}")
        
        return clusters
    
    def find_temporal_anomalies(self, threshold: float = 3.0) -> List[Dict[str, Any]]:
        """
        Find temporal anomalies (unusual activity patterns).
        
        Args:
            threshold: Threshold for anomaly detection (standard deviations).
            
        Returns:
            List of anomaly dictionaries.
        """
        temporal_graph = self._get_temporal_graph()
        if not temporal_graph:
            return []
        
        anomalies = []
        
        try:
            # Calculate average activity per node
            activity_counts = []
            for node in temporal_graph.nodes:
                activity_counts.append(len(node.timestamps))
            
            if not activity_counts:
                return []
            
            mean_activity = sum(activity_counts) / len(activity_counts)
            std_activity = (sum((x - mean_activity) ** 2 for x in activity_counts) / len(activity_counts)) ** 0.5
            
            # Find nodes with unusually high or low activity
            for i, node in enumerate(temporal_graph.nodes):
                activity = len(node.timestamps)
                z_score = (activity - mean_activity) / std_activity if std_activity > 0 else 0
                
                if abs(z_score) > threshold:
                    anomalies.append({
                        'node_id': node.node_id,
                        'type': 'activity_anomaly',
                        'activity': activity,
                        'z_score': z_score,
                        'expected': mean_activity,
                    })
            
            # Find nodes with unusual temporal patterns
            for node in temporal_graph.nodes:
                if len(node.timestamps) >= 3:
                    timestamps = sorted(node.timestamps)
                    intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() / 86400
                                for i in range(len(timestamps) - 1)]
                    
                    mean_interval = sum(intervals) / len(intervals)
                    std_interval = (sum((x - mean_interval) ** 2 for x in intervals) / len(intervals)) ** 0.5
                    
                    for i, interval in enumerate(intervals):
                        z_score = (interval - mean_interval) / std_interval if std_interval > 0 else 0
                        
                        if abs(z_score) > threshold:
                            anomalies.append({
                                'node_id': node.node_id,
                                'type': 'interval_anomaly',
                                'interval': interval,
                                'z_score': z_score,
                                'expected': mean_interval,
                                'timestamp_1': timestamps[i].isoformat(),
                                'timestamp_2': timestamps[i+1].isoformat(),
                            })
        
        except Exception as e:
            print(f"Temporal anomaly detection error: {e}")
        
        return anomalies
    
    def get_temporal_evolution(self, num_slices: int = 10) -> List[Dict[str, Any]]:
        """
        Get the temporal evolution of the graph.
        
        Args:
            num_slices: Number of time slices.
            
        Returns:
            List of evolution data for each time slice.
        """
        temporal_graph = self._get_temporal_graph()
        if not temporal_graph or not temporal_graph.time_range:
            return []
        
        start_time, end_time = temporal_graph.time_range
        total_duration = (end_time - start_time).total_seconds() / 86400
        slice_duration = total_duration / num_slices
        
        evolution = []
        
        for i in range(num_slices):
            slice_start = start_time + timedelta(days=i * slice_duration)
            slice_end = start_time + timedelta(days=(i + 1) * slice_duration)
            
            time_slice = self.query_time_slice(slice_start, slice_end)
            
            if time_slice:
                evolution.append({
                    'time_slice': i,
                    'start_time': slice_start.isoformat(),
                    'end_time': slice_end.isoformat(),
                    'num_nodes': len(time_slice.nodes),
                    'num_edges': len(time_slice.edges),
                    'new_nodes': len([n for n in time_slice.nodes if n.first_seen >= slice_start]),
                    'active_nodes': len(time_slice.nodes),
                })
        
        return evolution
    
    def predict_future_activity(self, lookahead: int = 7) -> Dict[str, Any]:
        """
        Predict future activity based on historical patterns.
        
        Args:
            lookahead: Number of days to predict ahead.
            
        Returns:
            Prediction dictionary.
        """
        temporal_graph = self._get_temporal_graph()
        if not temporal_graph or not temporal_graph.time_range:
            return {}
        
        try:
            # Calculate daily activity
            daily_activity = defaultdict(int)
            for node in temporal_graph.nodes:
                for ts in node.timestamps:
                    day = ts.date()
                    daily_activity[day] += 1
            
            if not daily_activity:
                return {}
            
            # Sort by date
            sorted_days = sorted(daily_activity.keys())
            activities = [daily_activity[day] for day in sorted_days]
            
            # Simple moving average prediction
            if len(activities) >= 7:
                window_size = min(7, len(activities))
                moving_avg = sum(activities[-window_size:]) / window_size
            else:
                moving_avg = sum(activities) / len(activities)
            
            # Predict future activity
            last_date = sorted_days[-1]
            predictions = []
            
            for i in range(lookahead):
                future_date = last_date + timedelta(days=i + 1)
                predictions.append({
                    'date': future_date.isoformat(),
                    'predicted_activity': int(moving_avg),
                })
            
            return {
                'predictions': predictions,
                'average_daily_activity': moving_avg,
                'last_date': last_date.isoformat(),
            }
        
        except Exception as e:
            print(f"Future activity prediction error: {e}")
            return {}


# Global temporal analyzer instance
temporal_analyzer = TemporalAnalyzer()
