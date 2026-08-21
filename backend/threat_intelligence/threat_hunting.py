"""
Threat Hunter for OpenLens

Provides proactive threat hunting capabilities:
- Hypothesis-driven hunting
- Anomaly-based hunting
- IOC-based hunting
- Behavioral hunting
- Pattern matching
- Hunt result analysis
"""

import os
import time
import json
import hashlib
import threading
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class Hunt:
    """Represents a threat hunt."""
    hunt_id: str
    name: str
    description: str = ''
    hunt_type: str = ''  # hypothesis, anomaly, ioc, behavioral, pattern
    status: str = 'pending'  # pending, running, completed, failed, cancelled
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: datetime = None
    completed_at: datetime = None
    created_by: str = ''
    parameters: Dict[str, Any] = field(default_factory=dict)
    results: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'hunt_id': self.hunt_id,
            'name': self.name,
            'description': self.description,
            'hunt_type': self.hunt_type,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_by': self.created_by,
            'parameters': self.parameters,
            'results': self.results,
        }


@dataclass
class HuntResult:
    """Represents a result from a threat hunt."""
    result_id: str
    hunt_id: str
    entity_id: str
    entity_type: str = ''  # node, edge, ioc, user, etc.
    match_type: str = ''  # exact, fuzzy, pattern, anomaly
    score: float = 0.0
    details: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'result_id': self.result_id,
            'hunt_id': self.hunt_id,
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'match_type': self.match_type,
            'score': self.score,
            'details': self.details,
            'created_at': self.created_at.isoformat(),
        }


@dataclass
class HuntPattern:
    """Represents a hunting pattern."""
    pattern_id: str
    name: str
    description: str = ''
    pattern_type: str = ''  # regex, cypher, graph, behavioral
    pattern: str = ''
    severity: str = 'medium'
    is_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'pattern_id': self.pattern_id,
            'name': self.name,
            'description': self.description,
            'pattern_type': self.pattern_type,
            'pattern': self.pattern,
            'severity': self.severity,
            'is_enabled': self.is_enabled,
            'created_at': self.created_at.isoformat(),
        }


@dataclass
class HuntConfig:
    """Configuration for threat hunter."""
    max_concurrent_hunts: int = 5
    timeout: int = 3600  # seconds
    result_limit: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'max_concurrent_hunts': self.max_concurrent_hunts,
            'timeout': self.timeout,
            'result_limit': self.result_limit,
        }


class ThreatHunter:
    """
    Threat hunter for OpenLens.
    
    Provides:
    - Hypothesis-driven hunting
    - Anomaly-based hunting
    - IOC-based hunting
    - Behavioral hunting
    - Pattern matching
    - Hunt result analysis
    """
    
    def __init__(self, config: HuntConfig = None, 
                 graph_engine=None, ioc_manager=None, 
                 anomaly_detector=None):
        """
        Initialize the threat hunter.
        
        Args:
            config: HuntConfig instance.
            graph_engine: GraphEngine instance.
            ioc_manager: IOCManager instance.
            anomaly_detector: AnomalyDetector instance.
        """
        self.config = config or HuntConfig()
        self.graph_engine = graph_engine
        self.ioc_manager = ioc_manager
        self.anomaly_detector = anomaly_detector
        self._hunts: Dict[str, Hunt] = {}
        self._patterns: Dict[str, HuntPattern] = {}
        self._running_hunts: Set[str] = set()
        self._lock = threading.Lock()
        
        # Initialize with default patterns
        self._initialize_default_patterns()
    
    def _initialize_default_patterns(self):
        """Initialize default hunting patterns."""
        # Suspicious IP pattern
        ip_pattern = HuntPattern(
            pattern_id='suspicious_ip_pattern',
            name='Suspicious IP Addresses',
            description='Detect nodes with suspicious IP addresses',
            pattern_type='cypher',
            pattern='MATCH (n) WHERE n.indicator_type = "ip" AND n.threat_type IN ["malware", "botnet", "c2"] RETURN n',
            severity='high',
        )
        self._patterns[ip_pattern.pattern_id] = ip_pattern
        
        # Suspicious domain pattern
        domain_pattern = HuntPattern(
            pattern_id='suspicious_domain_pattern',
            name='Suspicious Domains',
            description='Detect nodes with suspicious domains',
            pattern_type='cypher',
            pattern='MATCH (n) WHERE n.indicator_type = "domain" AND n.threat_type IN ["malware", "phishing"] RETURN n',
            severity='high',
        )
        self._patterns[domain_pattern.pattern_id] = domain_pattern
        
        # High degree nodes pattern
        high_degree_pattern = HuntPattern(
            pattern_id='high_degree_pattern',
            name='High Degree Nodes',
            description='Detect nodes with unusually high degree',
            pattern_type='graph',
            pattern='degree > 100',
            severity='medium',
        )
        self._patterns[high_degree_pattern.pattern_id] = high_degree_pattern
        
        # Anomalous behavior pattern
        anomalous_pattern = HuntPattern(
            pattern_id='anomalous_behavior_pattern',
            name='Anomalous Behavior',
            description='Detect nodes with anomalous behavior',
            pattern_type='behavioral',
            pattern='anomaly_score > 0.9',
            severity='high',
        )
        self._patterns[anomalous_pattern.pattern_id] = anomalous_pattern
    
    def create_hunt(self, name: str, description: str = '', 
                   hunt_type: str = 'hypothesis', parameters: Dict = None,
                   created_by: str = '') -> Hunt:
        """
        Create a new threat hunt.
        
        Args:
            name: Hunt name.
            description: Hunt description.
            hunt_type: Hunt type.
            parameters: Hunt parameters.
            created_by: User who created the hunt.
            
        Returns:
            Hunt object.
        """
        hunt_id = f"hunt_{int(time.time() * 1000)}"
        
        hunt = Hunt(
            hunt_id=hunt_id,
            name=name,
            description=description,
            hunt_type=hunt_type,
            created_by=created_by,
            parameters=parameters or {},
        )
        
        with self._lock:
            self._hunts[hunt_id] = hunt
        
        return hunt
    
    def execute_hunt(self, hunt_id: str) -> Optional[Hunt]:
        """
        Execute a threat hunt.
        
        Args:
            hunt_id: Hunt ID.
            
        Returns:
            Hunt object with results.
        """
        with self._lock:
            if hunt_id not in self._hunts:
                return None
            
            hunt = self._hunts[hunt_id]
            
            # Check if hunt is already running
            if hunt.status == 'running':
                return hunt
            
            # Check if we can run more hunts
            if len(self._running_hunts) >= self.config.max_concurrent_hunts:
                hunt.status = 'pending'
                return hunt
            
            # Mark as running
            hunt.status = 'running'
            hunt.started_at = datetime.utcnow()
            self._running_hunts.add(hunt_id)
        
        try:
            # Execute the hunt based on type
            if hunt.hunt_type == 'hypothesis':
                self._execute_hypothesis_hunt(hunt)
            elif hunt.hunt_type == 'anomaly':
                self._execute_anomaly_hunt(hunt)
            elif hunt.hunt_type == 'ioc':
                self._execute_ioc_hunt(hunt)
            elif hunt.hunt_type == 'behavioral':
                self._execute_behavioral_hunt(hunt)
            elif hunt.hunt_type == 'pattern':
                self._execute_pattern_hunt(hunt)
            else:
                hunt.status = 'failed'
                hunt.results.append({
                    'error': f"Unknown hunt type: {hunt.hunt_type}",
                })
            
            # Mark as completed
            hunt.status = 'completed'
            hunt.completed_at = datetime.utcnow()
        
        except Exception as e:
            hunt.status = 'failed'
            hunt.results.append({
                'error': str(e),
            })
        
        finally:
            with self._lock:
                self._running_hunts.discard(hunt_id)
                # Run next pending hunt if any
                self._run_next_pending_hunt()
        
        return hunt
    
    def _run_next_pending_hunt(self):
        """Run the next pending hunt if capacity is available."""
        with self._lock:
            if len(self._running_hunts) < self.config.max_concurrent_hunts:
                for hunt in self._hunts.values():
                    if hunt.status == 'pending':
                        # Run this hunt in a new thread
                        threading.Thread(
                            target=self.execute_hunt,
                            args=(hunt.hunt_id,),
                            daemon=True
                        ).start()
                        break
    
    def _execute_hypothesis_hunt(self, hunt: Hunt):
        """Execute a hypothesis-driven hunt."""
        # Hypothesis hunts are custom queries
        # Execute the query from parameters
        query = hunt.parameters.get('query', '')
        
        if not query:
            hunt.results.append({'error': 'No query provided'})
            return
        
        if not self.graph_engine:
            hunt.results.append({'error': 'Graph engine not available'})
            return
        
        try:
            result = self.graph_engine.execute_query(query)
            
            if not result:
                hunt.results.append({'error': 'No results from query'})
                return
            
            # Process results
            for node in result.nodes:
                hunt.results.append({
                    'entity_id': node.node_id,
                    'entity_type': 'node',
                    'match_type': 'query',
                    'score': 1.0,
                    'details': node.to_dict(),
                })
            
            for rel in result.relationships:
                hunt.results.append({
                    'entity_id': rel.rel_id,
                    'entity_type': 'relationship',
                    'match_type': 'query',
                    'score': 1.0,
                    'details': rel.to_dict(),
                })
        
        except Exception as e:
            hunt.results.append({'error': str(e)})
    
    def _execute_anomaly_hunt(self, hunt: Hunt):
        """Execute an anomaly-based hunt."""
        if not self.anomaly_detector:
            hunt.results.append({'error': 'Anomaly detector not available'})
            return
        
        # Get all nodes from the graph
        if not self.graph_engine:
            hunt.results.append({'error': 'Graph engine not available'})
            return
        
        try:
            query = "MATCH (n) RETURN n"
            result = self.graph_engine.execute_query(query)
            
            if not result:
                hunt.results.append({'error': 'No nodes found'})
                return
            
            # Prepare data for anomaly detection
            data = []
            for node in result.nodes:
                data.append({
                    'id': node.node_id,
                    'entity_type': 'node',
                    'labels': node.labels,
                    **node.properties
                })
            
            # Detect anomalies
            anomaly_result = self.anomaly_detector.detect_anomalies(data, method='graph')
            
            # Process anomalies
            for anomaly in anomaly_result.anomalies:
                hunt.results.append({
                    'entity_id': anomaly.entity_id,
                    'entity_type': anomaly.entity_type,
                    'match_type': 'anomaly',
                    'score': anomaly.score,
                    'details': {
                        'anomaly_id': anomaly.anomaly_id,
                        'method': anomaly.method,
                        'explanation': anomaly.explanation,
                        'severity': anomaly.severity,
                    },
                })
        
        except Exception as e:
            hunt.results.append({'error': str(e)})
    
    def _execute_ioc_hunt(self, hunt: Hunt):
        """Execute an IOC-based hunt."""
        if not self.ioc_manager:
            hunt.results.append({'error': 'IOC manager not available'})
            return
        
        if not self.graph_engine:
            hunt.results.append({'error': 'Graph engine not available'})
            return
        
        try:
            # Get IOCs to hunt for
            ioc_ids = hunt.parameters.get('ioc_ids', [])
            ioc_query = hunt.parameters.get('ioc_query', {})
            
            # Get IOCs
            iocs = []
            if ioc_ids:
                for ioc_id in ioc_ids:
                    ioc = self.ioc_manager.get_ioc_by_id(ioc_id)
                    if ioc:
                        iocs.append(ioc)
            else:
                iocs = self.ioc_manager.search_iocs(IOCSearchQuery(**ioc_query))
            
            # Search for each IOC in the graph
            for ioc in iocs:
                # Search for exact match
                query = f"MATCH (n) WHERE n.indicator = '{ioc.indicator}' RETURN n"
                result = self.graph_engine.execute_query(query)
                
                if result and result.nodes:
                    for node in result.nodes:
                        hunt.results.append({
                            'entity_id': node.node_id,
                            'entity_type': 'node',
                            'match_type': 'exact',
                            'score': 1.0,
                            'details': {
                                'ioc_id': ioc.ioc_id,
                                'indicator': ioc.indicator,
                                'indicator_type': ioc.indicator_type,
                                'threat_type': ioc.threat_type,
                                'node': node.to_dict(),
                            },
                        })
                
                # Search for partial match
                query = f"MATCH (n) WHERE ANY(prop IN keys(n) WHERE toLower(toString(n[prop])) CONTAINS toLower('{ioc.indicator}')) RETURN n"
                result = self.graph_engine.execute_query(query)
                
                if result and result.nodes:
                    for node in result.nodes:
                        # Check if already found
                        already_found = any(
                            r['entity_id'] == node.node_id and r['match_type'] == 'exact'
                            for r in hunt.results
                        )
                        
                        if not already_found:
                            hunt.results.append({
                                'entity_id': node.node_id,
                                'entity_type': 'node',
                                'match_type': 'partial',
                                'score': 0.8,
                                'details': {
                                    'ioc_id': ioc.ioc_id,
                                    'indicator': ioc.indicator,
                                    'indicator_type': ioc.indicator_type,
                                    'threat_type': ioc.threat_type,
                                    'node': node.to_dict(),
                                },
                            })
        
        except Exception as e:
            hunt.results.append({'error': str(e)})
    
    def _execute_behavioral_hunt(self, hunt: Hunt):
        """Execute a behavioral hunt."""
        if not self.graph_engine:
            hunt.results.append({'error': 'Graph engine not available'})
            return
        
        try:
            # Get behavior patterns from parameters
            patterns = hunt.parameters.get('patterns', [])
            
            if not patterns:
                hunt.results.append({'error': 'No behavior patterns provided'})
                return
            
            # Execute each pattern
            for pattern in patterns:
                pattern_type = pattern.get('type', '')
                pattern_value = pattern.get('value', '')
                
                if pattern_type == 'degree':
                    # Find nodes with degree > value
                    query = f"MATCH (n) WHERE size((n)--()) > {pattern_value} RETURN n"
                    result = self.graph_engine.execute_query(query)
                    
                    if result and result.nodes:
                        for node in result.nodes:
                            hunt.results.append({
                                'entity_id': node.node_id,
                                'entity_type': 'node',
                                'match_type': 'behavioral',
                                'score': 0.9,
                                'details': {
                                    'pattern': pattern,
                                    'degree': len(node.properties.get('connections', [])),
                                    'node': node.to_dict(),
                                },
                            })
                
                elif pattern_type == 'centrality':
                    # Find nodes with high centrality
                    # This would require centrality calculation
                    pass
                
                elif pattern_type == 'temporal':
                    # Find nodes with specific temporal patterns
                    pass
        
        except Exception as e:
            hunt.results.append({'error': str(e)})
    
    def _execute_pattern_hunt(self, hunt: Hunt):
        """Execute a pattern-based hunt."""
        pattern_id = hunt.parameters.get('pattern_id', '')
        pattern = self.get_pattern(pattern_id)
        
        if not pattern:
            hunt.results.append({'error': f"Pattern {pattern_id} not found"})
            return
        
        if not pattern.is_enabled:
            hunt.results.append({'error': f"Pattern {pattern_id} is disabled"})
            return
        
        try:
            if pattern.pattern_type == 'cypher':
                # Execute Cypher query
                result = self.graph_engine.execute_query(pattern.pattern)
                
                if result:
                    for node in result.nodes:
                        hunt.results.append({
                            'entity_id': node.node_id,
                            'entity_type': 'node',
                            'match_type': 'pattern',
                            'score': 1.0,
                            'details': {
                                'pattern_id': pattern.pattern_id,
                                'pattern_name': pattern.name,
                                'node': node.to_dict(),
                            },
                        })
                    
                    for rel in result.relationships:
                        hunt.results.append({
                            'entity_id': rel.rel_id,
                            'entity_type': 'relationship',
                            'match_type': 'pattern',
                            'score': 1.0,
                            'details': {
                                'pattern_id': pattern.pattern_id,
                                'pattern_name': pattern.name,
                                'relationship': rel.to_dict(),
                            },
                        })
            
            elif pattern.pattern_type == 'regex':
                # Search for regex pattern in node properties
                if not self.graph_engine:
                    hunt.results.append({'error': 'Graph engine not available'})
                    return
                
                query = "MATCH (n) RETURN n"
                result = self.graph_engine.execute_query(query)
                
                if result and result.nodes:
                    import re
                    regex = re.compile(pattern.pattern)
                    
                    for node in result.nodes:
                        for key, value in node.properties.items():
                            if isinstance(value, str) and regex.search(value):
                                hunt.results.append({
                                    'entity_id': node.node_id,
                                    'entity_type': 'node',
                                    'match_type': 'regex',
                                    'score': 0.9,
                                    'details': {
                                        'pattern_id': pattern.pattern_id,
                                        'pattern_name': pattern.name,
                                        'matched_property': key,
                                        'matched_value': value,
                                        'node': node.to_dict(),
                                    },
                                })
                                break
        
        except Exception as e:
            hunt.results.append({'error': str(e)})
    
    def get_hunt(self, hunt_id: str) -> Optional[Hunt]:
        """
        Get a threat hunt.
        
        Args:
            hunt_id: Hunt ID.
            
        Returns:
            Hunt or None.
        """
        with self._lock:
            return self._hunts.get(hunt_id)
    
    def list_hunts(self, status: str = None, hunt_type: str = None,
                  created_by: str = None, limit: int = 100) -> List[Hunt]:
        """
        List threat hunts.
        
        Args:
            status: Filter by status.
            hunt_type: Filter by hunt type.
            created_by: Filter by creator.
            limit: Maximum number of results.
            
        Returns:
            List of Hunt objects.
        """
        with self._lock:
            results = []
            
            for hunt in self._hunts.values():
                if status and hunt.status != status:
                    continue
                if hunt_type and hunt.hunt_type != hunt_type:
                    continue
                if created_by and hunt.created_by != created_by:
                    continue
                
                results.append(hunt)
            
            # Sort by created_at (descending)
            results.sort(key=lambda x: x.created_at, reverse=True)
            
            return results[:limit]
    
    def cancel_hunt(self, hunt_id: str) -> bool:
        """
        Cancel a threat hunt.
        
        Args:
            hunt_id: Hunt ID.
            
        Returns:
            True if cancelled.
        """
        with self._lock:
            if hunt_id not in self._hunts:
                return False
            
            hunt = self._hunts[hunt_id]
            
            if hunt.status not in ['pending', 'running']:
                return False
            
            hunt.status = 'cancelled'
            hunt.completed_at = datetime.utcnow()
            self._running_hunts.discard(hunt_id)
            
            return True
    
    def delete_hunt(self, hunt_id: str) -> bool:
        """
        Delete a threat hunt.
        
        Args:
            hunt_id: Hunt ID.
            
        Returns:
            True if deleted.
        """
        with self._lock:
            if hunt_id not in self._hunts:
                return False
            
            hunt = self._hunts[hunt_id]
            
            if hunt.status in ['running', 'pending']:
                return False
            
            del self._hunts[hunt_id]
            return True
    
    def add_pattern(self, pattern: HuntPattern) -> bool:
        """
        Add a hunting pattern.
        
        Args:
            pattern: HuntPattern to add.
            
        Returns:
            True if added.
        """
        with self._lock:
            if pattern.pattern_id in self._patterns:
                return False
            
            self._patterns[pattern.pattern_id] = pattern
            return True
    
    def remove_pattern(self, pattern_id: str) -> bool:
        """
        Remove a hunting pattern.
        
        Args:
            pattern_id: Pattern ID.
            
        Returns:
            True if removed.
        """
        with self._lock:
            if pattern_id not in self._patterns:
                return False
            
            del self._patterns[pattern_id]
            return True
    
    def get_pattern(self, pattern_id: str) -> Optional[HuntPattern]:
        """
        Get a hunting pattern.
        
        Args:
            pattern_id: Pattern ID.
            
        Returns:
            HuntPattern or None.
        """
        return self._patterns.get(pattern_id)
    
    def list_patterns(self, pattern_type: str = None, is_enabled: bool = None) -> List[HuntPattern]:
        """
        List hunting patterns.
        
        Args:
            pattern_type: Filter by pattern type.
            is_enabled: Filter by enabled status.
            
        Returns:
            List of HuntPattern objects.
        """
        with self._lock:
            results = []
            
            for pattern in self._patterns.values():
                if pattern_type and pattern.pattern_type != pattern_type:
                    continue
                if is_enabled is not None and pattern.is_enabled != is_enabled:
                    continue
                
                results.append(pattern)
            
            return results
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get threat hunting statistics.
        
        Returns:
            Dictionary with statistics.
        """
        with self._lock:
            stats = {
                'total_hunts': len(self._hunts),
                'by_status': defaultdict(int),
                'by_type': defaultdict(int),
                'running_hunts': len(self._running_hunts),
                'total_patterns': len(self._patterns),
                'by_pattern_type': defaultdict(int),
            }
            
            for hunt in self._hunts.values():
                stats['by_status'][hunt.status] += 1
                stats['by_type'][hunt.hunt_type] += 1
            
            for pattern in self._patterns.values():
                stats['by_pattern_type'][pattern.pattern_type] += 1
            
            # Convert defaultdict to dict
            for key in stats:
                if isinstance(stats[key], defaultdict):
                    stats[key] = dict(stats[key])
            
            return stats
    
    def export_to_json(self) -> str:
        """
        Export threat hunting data to JSON.
        
        Returns:
            JSON string.
        """
        data = {
            'hunts': [h.to_dict() for h in self._hunts.values()],
            'patterns': [p.to_dict() for p in self._patterns.values()],
            'config': self.config.to_dict(),
        }
        
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: str) -> bool:
        """
        Import threat hunting data from JSON.
        
        Args:
            json_data: JSON string.
            
        Returns:
            True if imported.
        """
        try:
            data = json.loads(json_data)
            
            # Import hunts
            self._hunts = {}
            for hunt_data in data.get('hunts', []):
                hunt = Hunt(
                    hunt_id=hunt_data['hunt_id'],
                    name=hunt_data['name'],
                    description=hunt_data.get('description', ''),
                    hunt_type=hunt_data.get('hunt_type', ''),
                    status=hunt_data.get('status', 'pending'),
                    created_at=datetime.fromisoformat(hunt_data['created_at']),
                    started_at=datetime.fromisoformat(hunt_data['started_at']) if hunt_data.get('started_at') else None,
                    completed_at=datetime.fromisoformat(hunt_data['completed_at']) if hunt_data.get('completed_at') else None,
                    created_by=hunt_data.get('created_by', ''),
                    parameters=hunt_data.get('parameters', {}),
                    results=hunt_data.get('results', []),
                )
                self._hunts[hunt.hunt_id] = hunt
            
            # Import patterns
            self._patterns = {}
            for pattern_data in data.get('patterns', []):
                pattern = HuntPattern(
                    pattern_id=pattern_data['pattern_id'],
                    name=pattern_data['name'],
                    description=pattern_data.get('description', ''),
                    pattern_type=pattern_data.get('pattern_type', ''),
                    pattern=pattern_data.get('pattern', ''),
                    severity=pattern_data.get('severity', 'medium'),
                    is_enabled=pattern_data.get('is_enabled', True),
                    created_at=datetime.fromisoformat(pattern_data['created_at']),
                )
                self._patterns[pattern.pattern_id] = pattern
            
            # Import config
            config_data = data.get('config', {})
            self.config = HuntConfig(
                max_concurrent_hunts=config_data.get('max_concurrent_hunts', 5),
                timeout=config_data.get('timeout', 3600),
                result_limit=config_data.get('result_limit', 1000),
            )
            
            return True
        
        except Exception as e:
            print(f"Error importing threat hunting data: {e}")
            return False


# Global threat hunter instance
threat_hunter = ThreatHunter()
