"""
Graph Engine for OpenLens

Enterprise-grade graph database engine with:
- Neo4j integration
- Cypher query builder
- Batch operations
- Transaction management
- Graph schema management
- Index optimization

This is the core of OpenLens's graph analytics capabilities,
designed to compete with Palantir Gotham's graph processing.
"""

import os
import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple, Union, Generator
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib
import uuid

# Try to import Neo4j driver.
# Note: BoltStatementResult existed only in the 1.x driver; importing it made
# this module report "driver not available" against every modern driver.
try:
    from neo4j import GraphDatabase, Record, Session
    from neo4j import graph as neo4j_graph
    from neo4j.exceptions import Neo4jError, ServiceUnavailable
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("Neo4j driver not available. Install with: pip install neo4j")

# Try to import networkx (used by to_networkx)
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False


@dataclass
class Node:
    """Represents a node in the graph."""
    node_id: str
    labels: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.node_id,
            'labels': self.labels,
            'properties': self.properties,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
    
    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a property value."""
        return self.properties.get(key, default)
    
    def has_label(self, label: str) -> bool:
        """Check if node has a specific label."""
        return label in self.labels


@dataclass
class Relationship:
    """Represents a relationship between nodes."""
    rel_id: str
    rel_type: str
    source_id: str
    target_id: str
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.rel_id,
            'type': self.rel_type,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'properties': self.properties,
            'created_at': self.created_at.isoformat(),
        }


@dataclass
class GraphResult:
    """Represents a graph query result."""
    nodes: List[Node] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    # Full row data for every record, so scalars, maps and aggregates survive.
    # Without this, `RETURN count(n)` and `CALL db.labels()` come back empty.
    records: List[Dict[str, Any]] = field(default_factory=list)
    query: str = ""
    execution_time: float = 0.0
    stats: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'nodes': [n.to_dict() for n in self.nodes],
            'relationships': [r.to_dict() for r in self.relationships],
            'records': self.records,
            'query': self.query,
            'execution_time': self.execution_time,
            'stats': self.stats,
        }


@dataclass
class GraphSchema:
    """Represents the graph schema."""
    node_labels: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    relationship_types: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    property_keys: Dict[str, str] = field(default_factory=dict)  # property_name -> type
    indexes: List[Dict[str, Any]] = field(default_factory=list)
    constraints: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'node_labels': self.node_labels,
            'relationship_types': self.relationship_types,
            'property_keys': self.property_keys,
            'indexes': self.indexes,
            'constraints': self.constraints,
        }


class CypherQueryBuilder:
    """
    Builds Cypher queries programmatically.
    """
    
    def __init__(self):
        """Initialize the query builder."""
        self.clauses = []
        self.params = {}
        self.param_counter = 0
    
    def match(self, pattern: str, where: Dict = None) -> 'CypherQueryBuilder':
        """Add a MATCH clause."""
        self.clauses.append(f"MATCH {pattern}")
        if where:
            self._add_where(where)
        return self
    
    def optional_match(self, pattern: str, where: Dict = None) -> 'CypherQueryBuilder':
        """Add an OPTIONAL MATCH clause."""
        self.clauses.append(f"OPTIONAL MATCH {pattern}")
        if where:
            self._add_where(where)
        return self
    
    def where(self, conditions: Dict) -> 'CypherQueryBuilder':
        """Add a WHERE clause."""
        self._add_where(conditions)
        return self
    
    def _add_where(self, conditions: Dict):
        """Add WHERE conditions."""
        if not conditions:
            return
        
        where_clauses = []
        for key, value in conditions.items():
            param_name = f"param_{self.param_counter}"
            self.param_counter += 1
            self.params[param_name] = value
            
            if isinstance(value, (list, tuple)):
                where_clauses.append(f"{key} IN ${param_name}")
            elif value is None:
                where_clauses.append(f"{key} IS NULL")
            elif isinstance(value, str) and '*' in value:
                # Handle wildcard searches
                param_name = f"param_{self.param_counter}"
                self.param_counter += 1
                self.params[param_name] = value.replace('*', '.*')
                where_clauses.append(f"{key} =~ ${param_name}")
            else:
                where_clauses.append(f"{key} = ${param_name}")
        
        if where_clauses:
            where_str = " AND ".join(where_clauses)
            if not any(c.startswith("WHERE") for c in self.clauses):
                self.clauses.append(f"WHERE {where_str}")
            else:
                # Find the last WHERE clause and append
                for i, clause in enumerate(self.clauses):
                    if clause.startswith("WHERE"):
                        self.clauses[i] = f"{clause} AND {where_str}"
                        break
    
    def create(self, pattern: str, properties: Dict = None) -> 'CypherQueryBuilder':
        """Add a CREATE clause."""
        if properties:
            param_name = f"props_{self.param_counter}"
            self.param_counter += 1
            self.params[param_name] = properties
            self.clauses.append(f"CREATE {pattern} SET {pattern} = ${param_name}")
        else:
            self.clauses.append(f"CREATE {pattern}")
        return self
    
    def merge(self, pattern: str, properties: Dict = None) -> 'CypherQueryBuilder':
        """Add a MERGE clause."""
        if properties:
            param_name = f"props_{self.param_counter}"
            self.param_counter += 1
            self.params[param_name] = properties
            self.clauses.append(f"MERGE {pattern} SET {pattern} = ${param_name}")
        else:
            self.clauses.append(f"MERGE {pattern}")
        return self
    
    def create_relationship(self, source: str, rel_type: str, target: str, 
                           properties: Dict = None) -> 'CypherQueryBuilder':
        """Create a relationship."""
        if properties:
            param_name = f"rel_props_{self.param_counter}"
            self.param_counter += 1
            self.params[param_name] = properties
            self.clauses.append(
                f"CREATE ({source})-[:{rel_type} {{{param_name}}}]->({target})"
            )
        else:
            self.clauses.append(
                f"CREATE ({source})-[:{rel_type}]->({target})"
            )
        return self
    
    def merge_relationship(self, source: str, rel_type: str, target: str,
                          properties: Dict = None) -> 'CypherQueryBuilder':
        """Merge a relationship."""
        if properties:
            param_name = f"rel_props_{self.param_counter}"
            self.param_counter += 1
            self.params[param_name] = properties
            self.clauses.append(
                f"MERGE ({source})-[:{rel_type} {{{param_name}}}]->({target})"
            )
        else:
            self.clauses.append(
                f"MERGE ({source})-[:{rel_type}]->({target})"
            )
        return self
    
    def delete(self, pattern: str) -> 'CypherQueryBuilder':
        """Add a DELETE clause."""
        self.clauses.append(f"DELETE {pattern}")
        return self
    
    def detach_delete(self, pattern: str) -> 'CypherQueryBuilder':
        """Add a DETACH DELETE clause."""
        self.clauses.append(f"DETACH DELETE {pattern}")
        return self
    
    def set_properties(self, pattern: str, properties: Dict) -> 'CypherQueryBuilder':
        """Add a SET clause for properties."""
        param_name = f"set_props_{self.param_counter}"
        self.param_counter += 1
        self.params[param_name] = properties
        self.clauses.append(f"SET {pattern} += ${param_name}")
        return self
    
    def return_(self, *fields: str) -> 'CypherQueryBuilder':
        """Add a RETURN clause."""
        if fields:
            self.clauses.append(f"RETURN {', '.join(fields)}")
        else:
            self.clauses.append("RETURN *")
        return self
    
    def limit(self, limit: int) -> 'CypherQueryBuilder':
        """Add a LIMIT clause."""
        self.clauses.append(f"LIMIT {limit}")
        return self
    
    def skip(self, skip: int) -> 'CypherQueryBuilder':
        """Add a SKIP clause."""
        self.clauses.append(f"SKIP {skip}")
        return self
    
    def order_by(self, *fields: str) -> 'CypherQueryBuilder':
        """Add an ORDER BY clause."""
        self.clauses.append(f"ORDER BY {', '.join(fields)}")
        return self
    
    def with_(self, *fields: str) -> 'CypherQueryBuilder':
        """Add a WITH clause."""
        self.clauses.append(f"WITH {', '.join(fields)}")
        return self
    
    def unwind(self, list_var: str, as_var: str = None) -> 'CypherQueryBuilder':
        """Add an UNWIND clause."""
        if as_var:
            self.clauses.append(f"UNWIND {list_var} AS {as_var}")
        else:
            self.clauses.append(f"UNWIND {list_var}")
        return self
    
    def call(self, procedure: str, args: Dict = None) -> 'CypherQueryBuilder':
        """Add a CALL clause for stored procedures."""
        if args:
            param_name = f"proc_args_{self.param_counter}"
            self.param_counter += 1
            self.params[param_name] = args
            self.clauses.append(f"CALL {procedure}(${param_name})")
        else:
            self.clauses.append(f"CALL {procedure}()")
        return self
    
    def union(self) -> 'CypherQueryBuilder':
        """Add a UNION clause."""
        self.clauses.append("UNION")
        return self
    
    def union_all(self) -> 'CypherQueryBuilder':
        """Add a UNION ALL clause."""
        self.clauses.append("UNION ALL")
        return self
    
    def build(self) -> Tuple[str, Dict]:
        """Build the final query and parameters."""
        query = "\n".join(self.clauses)
        return query, self.params
    
    def execute(self, session: "Session" = None) -> Optional[Any]:
        """Execute the query."""
        if not NEO4J_AVAILABLE:
            return None

        query, params = self.build()
        if session:
            return session.run(query, parameters=params)
        return None


class GraphEngine:
    """
    Enterprise-grade graph engine for OpenLens.
    
    Provides:
    - Neo4j database integration
    - Cypher query execution
    - Batch operations
    - Transaction management
    - Schema management
    - Performance optimization
    """
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """
        Initialize the graph engine.
        
        Args:
            uri: Neo4j server URI.
            user: Neo4j username.
            password: Neo4j password.
        """
        if uri is None or user is None or password is None:
            from backend.config import neo4j_settings
            settings = neo4j_settings()
            uri = uri or settings['uri']
            user = user or settings['user']
            password = password or settings['password']

        self.uri = uri
        self.user = user
        self.password = password

        self._driver = None
        self._last_connect_failure = 0.0
        self._connect_retry_interval = 30.0  # seconds between reconnect attempts
        self._nx_cache: Optional[Tuple[float, Any]] = None
        self._nx_cache_ttl = 300.0  # seconds
        self._session_pool = []
        self._lock = threading.Lock()
        self._query_cache: Dict[str, Tuple[str, Dict]] = {}
        self._stats = {
            'queries_executed': 0,
            'query_time_total': 0.0,
            'nodes_created': 0,
            'relationships_created': 0,
            'cache_hits': 0,
            'cache_misses': 0,
        }
        # Deliberately no connection attempt here: importing this module must
        # not open a socket. The driver connects lazily on first use.

    @property
    def driver(self):
        """The Neo4j driver, connecting lazily on first access."""
        self._ensure_driver()
        return self._driver

    @driver.setter
    def driver(self, value):
        self._driver = value

    def _ensure_driver(self) -> bool:
        """
        Idempotently construct and verify the Neo4j driver.

        Retries after a failure at most every _connect_retry_interval seconds,
        so a down database costs one short timeout per interval rather than one
        per call.
        """
        if self._driver is not None:
            return True
        if not NEO4J_AVAILABLE:
            return False
        if time.time() - self._last_connect_failure < self._connect_retry_interval:
            return False

        with self._lock:
            if self._driver is not None:
                return True
            try:
                # No encrypted=/trust= settings: encryption is selected by the
                # URI scheme (bolt+s://, neo4j+s://); forcing encrypted=True on
                # plain bolt:// fails the handshake against a default container.
                driver = GraphDatabase.driver(
                    self.uri,
                    auth=(self.user, self.password),
                    max_connection_lifetime=30 * 60,  # 30 minutes
                    max_connection_pool_size=50,
                    connection_timeout=5,
                )
                driver.verify_connectivity()
                self._driver = driver
                print(f"Connected to Neo4j at {self.uri}")
                return True
            except Exception as e:
                self._last_connect_failure = time.time()
                print(f"Failed to connect to Neo4j: {e}")
                return False

    def verify_connection(self) -> bool:
        """
        Verify the connection to Neo4j.

        Returns:
            True if connected, False otherwise.
        """
        if not self._ensure_driver():
            return False

        try:
            with self._driver.session() as session:
                session.run("RETURN 1").consume()
            return True
        except Exception:
            return False

    def is_connected(self) -> bool:
        """Public alias for verify_connection()."""
        return self.verify_connection()
    
    def get_session(self) -> Optional[Session]:
        """
        Get a database session.
        
        Returns:
            Neo4j Session or None if not connected.
        """
        if not self.driver:
            return None
        
        return self.driver.session()
    
    def execute_query(self, query: str, params: Dict = None, 
                      use_cache: bool = True) -> Optional[GraphResult]:
        """
        Execute a Cypher query.
        
        Args:
            query: Cypher query string.
            params: Query parameters.
            use_cache: Whether to use query caching.
            
        Returns:
            GraphResult or None if failed.
        """
        if not self.driver:
            return None
        
        params = params or {}
        start_time = time.time()
        
        # Check cache
        cache_key = self._generate_cache_key(query, params)
        if use_cache and cache_key in self._query_cache:
            cached_query, cached_params = self._query_cache[cache_key]
            self._stats['cache_hits'] += 1
        else:
            cached_query, cached_params = query, params
            self._stats['cache_misses'] += 1
        
        try:
            with self._driver.session() as session:
                # parameters= rather than **kwargs, so a param named 'query'
                # or 'parameters' cannot collide with the driver's signature.
                result = session.run(cached_query, parameters=cached_params)

                nodes = []
                relationships = []
                records: List[Dict[str, Any]] = []

                for record in result:
                    records.append(record.data())
                    for key, value in record.items():
                        if isinstance(value, neo4j_graph.Node):
                            node = self._parse_node(value)
                            if node and node not in nodes:
                                nodes.append(node)
                        elif isinstance(value, neo4j_graph.Relationship):
                            rel = self._parse_relationship(value)
                            if rel and rel not in relationships:
                                relationships.append(rel)

                # Get query stats. SummaryCounters is not a mapping in the 5.x
                # driver, so dict(summary.counters) raises; read the documented
                # attributes explicitly instead.
                summary = result.consume()
                counters = summary.counters
                stats = {
                    'counters': {
                        name: getattr(counters, name, 0)
                        for name in (
                            'nodes_created', 'nodes_deleted',
                            'relationships_created', 'relationships_deleted',
                            'properties_set', 'labels_added', 'labels_removed',
                            'indexes_added', 'indexes_removed',
                            'constraints_added', 'constraints_removed',
                        )
                    },
                    'query_type': summary.query_type,
                }

                execution_time = time.time() - start_time
                self._stats['queries_executed'] += 1
                self._stats['query_time_total'] += execution_time

                # Cache the query
                if use_cache and cache_key not in self._query_cache:
                    self._query_cache[cache_key] = (query, params)

                return GraphResult(
                    nodes=nodes,
                    relationships=relationships,
                    records=records,
                    query=query,
                    execution_time=execution_time,
                    stats=stats,
                )

        except Exception as e:
            print(f"Query execution error ({type(e).__name__}): {e}")
            return None
    
    def _generate_cache_key(self, query: str, params: Dict) -> str:
        """Generate a cache key for a query."""
        param_str = json.dumps(params, sort_keys=True) if params else ""
        return hashlib.sha256(f"{query}:{param_str}".encode()).hexdigest()
    
    @staticmethod
    def _entity_id(neo4j_entity) -> str:
        """
        Best identifier for a Neo4j entity: the business 'id' property that
        create_node/create_relationship set, falling back to the driver's
        element_id. Downstream code (entity merge, threat-graph classification)
        treats node_id as a business id, so the property must win when present.
        """
        props = dict(neo4j_entity)
        business_id = props.get('id')
        if business_id:
            return str(business_id)
        return str(getattr(neo4j_entity, 'element_id', '') or getattr(neo4j_entity, 'id', ''))

    def _parse_node(self, neo4j_node) -> Optional[Node]:
        """Parse a Neo4j Node object."""
        try:
            return Node(
                node_id=self._entity_id(neo4j_node),
                labels=list(neo4j_node.labels),
                properties=dict(neo4j_node),
            )
        except Exception:
            return None

    def _parse_relationship(self, neo4j_rel) -> Optional[Relationship]:
        """Parse a Neo4j Relationship object."""
        try:
            return Relationship(
                rel_id=self._entity_id(neo4j_rel),
                rel_type=neo4j_rel.type,
                source_id=self._entity_id(neo4j_rel.start_node),
                target_id=self._entity_id(neo4j_rel.end_node),
                properties=dict(neo4j_rel),
            )
        except Exception:
            return None
    
    def execute_transaction(self, queries: List[Tuple[str, Dict]]) -> bool:
        """
        Execute multiple queries in a transaction.
        
        Args:
            queries: List of (query, params) tuples.
            
        Returns:
            True if all queries succeeded, False otherwise.
        """
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                with session.begin_transaction() as tx:
                    for query, params in queries:
                        tx.run(query, parameters=params)
            return True
        except Exception as e:
            print(f"Transaction error: {e}")
            return False
    
    def execute_batch(self, query: str, params_list: List[Dict], 
                      batch_size: int = 1000) -> List[GraphResult]:
        """
        Execute a query in batches.
        
        Args:
            query: Cypher query with parameters.
            params_list: List of parameter dictionaries.
            batch_size: Number of queries per batch.
            
        Returns:
            List of GraphResult objects.
        """
        results = []
        
        for i in range(0, len(params_list), batch_size):
            batch = params_list[i:i + batch_size]
            
            if not self.driver:
                return results
            
            try:
                with self.driver.session() as session:
                    for params in batch:
                        result = session.run(query, parameters=params)
                        nodes = []
                        relationships = []
                        records: List[Dict[str, Any]] = []

                        for record in result:
                            records.append(record.data())
                            for key, value in record.items():
                                if isinstance(value, neo4j_graph.Node):
                                    node = self._parse_node(value)
                                    if node and node not in nodes:
                                        nodes.append(node)
                                elif isinstance(value, neo4j_graph.Relationship):
                                    rel = self._parse_relationship(value)
                                    if rel and rel not in relationships:
                                        relationships.append(rel)

                        result.consume()

                        results.append(GraphResult(
                            nodes=nodes,
                            relationships=relationships,
                            records=records,
                            query=query,
                        ))
            except Exception as e:
                print(f"Batch execution error: {e}")
                # Continue with next batch
                continue
        
        return results
    
    def create_node(self, labels: List[str], properties: Dict = None) -> Optional[Node]:
        """
        Create a node in the graph.
        
        Args:
            labels: List of labels for the node.
            properties: Node properties.
            
        Returns:
            Created Node or None if failed.
        """
        if not self.driver:
            return None
        
        properties = properties or {}
        node_id = str(uuid.uuid4())
        properties['id'] = node_id
        properties['created_at'] = datetime.utcnow().isoformat()
        properties['updated_at'] = datetime.utcnow().isoformat()
        
        label_str = ':'.join(labels)
        query = f"CREATE (n:{label_str} $props) RETURN n"
        params = {'props': properties}
        
        try:
            result = self.execute_query(query, params)
            if result and result.nodes:
                self._stats['nodes_created'] += 1
                return result.nodes[0]
        except Exception as e:
            print(f"Create node error: {e}")
        
        return None
    
    def create_relationship(self, source_id: str, target_id: str, 
                           rel_type: str, properties: Dict = None) -> Optional[Relationship]:
        """
        Create a relationship between two nodes.
        
        Args:
            source_id: Source node ID.
            target_id: Target node ID.
            rel_type: Relationship type.
            properties: Relationship properties.
            
        Returns:
            Created Relationship or None if failed.
        """
        if not self.driver:
            return None
        
        properties = properties or {}
        rel_id = str(uuid.uuid4())
        properties['id'] = rel_id
        properties['created_at'] = datetime.utcnow().isoformat()
        
        # RETURN a and b as well: with only r in the result the driver leaves
        # start/end nodes as property-less stubs, so the parsed relationship
        # would carry element ids instead of the business ids callers passed in.
        query = """
        MATCH (a), (b)
        WHERE a.id = $source_id AND b.id = $target_id
        CREATE (a)-[r:%s $props]->(b)
        RETURN a, r, b
        """ % rel_type
        
        params = {
            'source_id': source_id,
            'target_id': target_id,
            'props': properties,
        }
        
        try:
            result = self.execute_query(query, params)
            if result and result.relationships:
                self._stats['relationships_created'] += 1
                return result.relationships[0]
        except Exception as e:
            print(f"Create relationship error: {e}")
        
        return None
    
    def merge_node(self, labels: List[str], properties: Dict = None) -> Optional[Node]:
        """
        Merge a node (create if not exists, update if exists).
        
        Args:
            labels: List of labels for the node.
            properties: Node properties.
            
        Returns:
            Merged Node or None if failed.
        """
        if not self.driver:
            return None
        
        properties = properties or {}
        label_str = ':'.join(labels)
        
        # Build MERGE query with property matching
        prop_conditions = []
        for key, value in properties.items():
            if key not in ['id', 'created_at', 'updated_at']:
                prop_conditions.append(f"n.{key} = ${key}")
        
        if prop_conditions:
            merge_condition = " AND ".join(prop_conditions)
            query = f"MERGE (n:{label_str} {{ {merge_condition} }}) SET n += $props RETURN n"
        else:
            query = f"MERGE (n:{label_str}) SET n += $props RETURN n"
        
        properties['updated_at'] = datetime.utcnow().isoformat()
        if 'created_at' not in properties:
            properties['created_at'] = datetime.utcnow().isoformat()
        
        params = {'props': properties}
        
        try:
            result = self.execute_query(query, params)
            if result and result.nodes:
                return result.nodes[0]
        except Exception as e:
            print(f"Merge node error: {e}")
        
        return None
    
    def merge_relationship(self, source_id: str, target_id: str, 
                          rel_type: str, properties: Dict = None) -> Optional[Relationship]:
        """
        Merge a relationship (create if not exists).
        
        Args:
            source_id: Source node ID.
            target_id: Target node ID.
            rel_type: Relationship type.
            properties: Relationship properties.
            
        Returns:
            Merged Relationship or None if failed.
        """
        if not self.driver:
            return None
        
        properties = properties or {}
        
        query = """
        MATCH (a), (b)
        WHERE a.id = $source_id AND b.id = $target_id
        MERGE (a)-[r:%s]->(b)
        SET r += $props
        RETURN a, r, b
        """ % rel_type
        
        params = {
            'source_id': source_id,
            'target_id': target_id,
            'props': properties,
        }
        
        try:
            result = self.execute_query(query, params)
            if result and result.relationships:
                return result.relationships[0]
        except Exception as e:
            print(f"Merge relationship error: {e}")
        
        return None
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Get a node by ID.
        
        Args:
            node_id: Node ID.
            
        Returns:
            Node or None if not found.
        """
        if not self.driver:
            return None
        
        query = "MATCH (n) WHERE n.id = $node_id RETURN n"
        params = {'node_id': node_id}
        
        result = self.execute_query(query, params)
        if result and result.nodes:
            return result.nodes[0]
        
        return None
    
    def get_relationship(self, rel_id: str) -> Optional[Relationship]:
        """
        Get a relationship by ID.
        
        Args:
            rel_id: Relationship ID.
            
        Returns:
            Relationship or None if not found.
        """
        if not self.driver:
            return None
        
        query = "MATCH ()-[r]->() WHERE r.id = $rel_id RETURN r"
        params = {'rel_id': rel_id}
        
        result = self.execute_query(query, params)
        if result and result.relationships:
            return result.relationships[0]
        
        return None
    
    def delete_node(self, node_id: str) -> bool:
        """
        Delete a node by ID.
        
        Args:
            node_id: Node ID.
            
        Returns:
            True if deleted, False otherwise.
        """
        if not self.driver:
            return False
        
        query = "MATCH (n) WHERE n.id = $node_id DETACH DELETE n"
        params = {'node_id': node_id}
        
        try:
            result = self.execute_query(query, params)
            return result is not None
        except Exception as e:
            print(f"Delete node error: {e}")
            return False
    
    def delete_relationship(self, rel_id: str) -> bool:
        """
        Delete a relationship by ID.
        
        Args:
            rel_id: Relationship ID.
            
        Returns:
            True if deleted, False otherwise.
        """
        if not self.driver:
            return False
        
        query = "MATCH ()-[r]->() WHERE r.id = $rel_id DELETE r"
        params = {'rel_id': rel_id}
        
        try:
            result = self.execute_query(query, params)
            return result is not None
        except Exception as e:
            print(f"Delete relationship error: {e}")
            return False
    
    def get_schema(self) -> Optional[GraphSchema]:
        """
        Get the graph schema.
        
        Returns:
            GraphSchema or None if failed.
        """
        if not self.driver:
            return None
        
        try:
            schema = GraphSchema()

            # These procedures return scalar rows, which land in .records
            # (never in .nodes - the old code silently produced an empty schema).
            result = self.execute_query("CALL db.labels()")
            if result:
                for record in result.records:
                    label = record.get('label', '')
                    if label:
                        schema.node_labels[label] = {}

            result = self.execute_query("CALL db.relationshipTypes()")
            if result:
                for record in result.records:
                    rel_type = record.get('relationshipType', '')
                    if rel_type:
                        schema.relationship_types[rel_type] = {}

            result = self.execute_query("CALL db.propertyKeys()")
            if result:
                for record in result.records:
                    prop_key = record.get('propertyKey', '')
                    if prop_key:
                        schema.property_keys[prop_key] = 'string'  # Default type

            result = self.execute_query("SHOW INDEXES")
            if result:
                schema.indexes.extend(result.records)

            result = self.execute_query("SHOW CONSTRAINTS")
            if result:
                schema.constraints.extend(result.records)

            return schema
        
        except Exception as e:
            print(f"Get schema error: {e}")
            return None
    
    def create_index(self, label: str, property: str, index_type: str = 'BTREE') -> bool:
        """
        Create an index.
        
        Args:
            label: Node label.
            property: Property name.
            index_type: Index type (BTREE, FULLTEXT, etc.).
            
        Returns:
            True if created, False otherwise.
        """
        if not self.driver:
            return False
        
        query = f"CREATE INDEX FOR (n:{label}) ON (n.{property})"
        if index_type != 'BTREE':
            query = f"CREATE {index_type} INDEX FOR (n:{label}) ON (n.{property})"
        
        try:
            result = self.execute_query(query)
            return result is not None
        except Exception as e:
            print(f"Create index error: {e}")
            return False
    
    def create_constraint(self, label: str, property: str, 
                         constraint_type: str = 'UNIQUE') -> bool:
        """
        Create a constraint.
        
        Args:
            label: Node label.
            property: Property name.
            constraint_type: Constraint type (UNIQUE, NOT NULL, etc.).
            
        Returns:
            True if created, False otherwise.
        """
        if not self.driver:
            return False
        
        query = f"CREATE CONSTRAINT FOR (n:{label}) REQUIRE n.{property} IS {constraint_type}"
        
        try:
            result = self.execute_query(query)
            return result is not None
        except Exception as e:
            print(f"Create constraint error: {e}")
            return False
    
    def execute_records(self, query: str, params: Dict = None) -> List[Dict[str, Any]]:
        """Execute a query and return the raw record rows."""
        result = self.execute_query(query, params)
        return result.records if result else []

    def execute_scalar(self, query: str, params: Dict = None, default: Any = None) -> Any:
        """Execute a query and return the first column of the first row."""
        records = self.execute_records(query, params)
        if records:
            first = records[0]
            if first:
                return next(iter(first.values()))
        return default

    def node_count(self) -> int:
        """Total number of nodes in the graph."""
        return int(self.execute_scalar("MATCH (n) RETURN count(n) AS c", default=0) or 0)

    def relationship_count(self) -> int:
        """Total number of relationships in the graph."""
        return int(self.execute_scalar("MATCH ()-[r]->() RETURN count(r) AS c", default=0) or 0)

    def to_networkx(self, force_refresh: bool = False, directed: bool = False):
        """
        Materialise the graph as a networkx Graph/DiGraph, cached for
        _nx_cache_ttl seconds.

        Returns None when networkx or the database is unavailable - callers
        must treat None as "cannot compute", never as "empty graph".
        """
        if not NETWORKX_AVAILABLE:
            return None
        if not self._ensure_driver():
            return None

        now = time.time()
        if not force_refresh and self._nx_cache is not None:
            cached_at, cached_graph = self._nx_cache
            if now - cached_at < self._nx_cache_ttl and cached_graph.is_directed() == directed:
                return cached_graph

        graph = nx.DiGraph() if directed else nx.Graph()

        node_result = self.execute_query("MATCH (n) RETURN n", use_cache=False)
        if node_result is None:
            return None
        for node in node_result.nodes:
            graph.add_node(node.node_id, labels=node.labels, **node.properties)

        rel_result = self.execute_query("MATCH (a)-[r]->(b) RETURN a, r, b", use_cache=False)
        if rel_result is None:
            return None
        for rel in rel_result.relationships:
            graph.add_edge(rel.source_id, rel.target_id, type=rel.rel_type, **rel.properties)

        self._nx_cache = (now, graph)
        return graph

    def _get_networkx_graph(self, force_refresh: bool = False):
        """
        Transitional alias for to_networkx().

        Several AI modules already call this name on the engine; keep it until
        those call sites migrate to the public name.
        """
        return self.to_networkx(force_refresh=force_refresh)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get engine statistics.

        Returns:
            Dictionary with statistics.
        """
        stats = self._stats.copy()

        if stats['queries_executed'] > 0:
            stats['avg_query_time'] = stats['query_time_total'] / stats['queries_executed']
        else:
            stats['avg_query_time'] = 0.0

        stats['cache_size'] = len(self._query_cache)
        stats['connected'] = self.is_connected()
        if stats['connected']:
            stats['node_count'] = self.node_count()
            stats['edge_count'] = self.relationship_count()
        else:
            stats['node_count'] = 0
            stats['edge_count'] = 0

        return stats

    def close(self):
        """Close the driver and all sessions."""
        if self._driver:
            self._driver.close()
            self._driver = None

        self._session_pool.clear()
        self._query_cache.clear()
        self._nx_cache = None


# Global graph engine instance
graph_engine = GraphEngine()
