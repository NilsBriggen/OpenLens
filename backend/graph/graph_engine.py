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

# Try to import Neo4j driver
try:
    from neo4j import GraphDatabase, BoltStatementResult, Record, Session, Transaction
    from neo4j.exceptions import Neo4jError, ServiceUnavailable
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("Neo4j driver not available. Install with: pip install neo4j")


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
    query: str = ""
    execution_time: float = 0.0
    stats: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'nodes': [n.to_dict() for n in self.nodes],
            'relationships': [r.to_dict() for r in self.relationships],
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
    
    def execute(self, session: Session = None) -> Optional[BoltStatementResult]:
        """Execute the query."""
        if not NEO4J_AVAILABLE:
            return None
        
        query, params = self.build()
        if session:
            return session.run(query, **params)
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
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USERNAME', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD', 'password')
        
        self.driver = None
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
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the Neo4j driver."""
        if not NEO4J_AVAILABLE:
            return
        
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password),
                max_connection_lifetime=30 * 60,  # 30 minutes
                max_connection_pool_size=50,
                connection_timeout=30,
                encrypted=True,
                trust=TRUST_ALL_CERTIFICATES if os.getenv('NEO4J_TRUST_ALL', 'false').lower() == 'true' else TRUST_SYSTEM_CA_SIGNED_CERTIFICATES,
            )
            
            # Verify connection
            self.verify_connection()
            
            print(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            self.driver = None
    
    def verify_connection(self) -> bool:
        """
        Verify the connection to Neo4j.
        
        Returns:
            True if connected, False otherwise.
        """
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                session.run("RETURN 1").consume()
            return True
        except Exception:
            return False
    
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
            with self.driver.session() as session:
                result = session.run(cached_query, **cached_params)
                
                nodes = []
                relationships = []
                stats = {}
                
                for record in result:
                    for key, value in record.items():
                        if hasattr(value, '__class__') and value.__class__.__name__ == 'Node':
                            node = self._parse_node(value)
                            if node and node not in nodes:
                                nodes.append(node)
                        elif hasattr(value, '__class__') and value.__class__.__name__ == 'Relationship':
                            rel = self._parse_relationship(value)
                            if rel and rel not in relationships:
                                relationships.append(rel)
                
                # Get query stats
                summary = result.consume()
                stats = {
                    'counters': dict(summary.counters),
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
                    query=query,
                    execution_time=execution_time,
                    stats=stats,
                )
        
        except Exception as e:
            print(f"Query execution error: {e}")
            return None
    
    def _generate_cache_key(self, query: str, params: Dict) -> str:
        """Generate a cache key for a query."""
        param_str = json.dumps(params, sort_keys=True) if params else ""
        return hashlib.sha256(f"{query}:{param_str}".encode()).hexdigest()
    
    def _parse_node(self, neo4j_node) -> Optional[Node]:
        """Parse a Neo4j Node object."""
        try:
            return Node(
                node_id=str(neo4j_node.id),
                labels=list(neo4j_node.labels),
                properties=dict(neo4j_node),
            )
        except Exception:
            return None
    
    def _parse_relationship(self, neo4j_rel) -> Optional[Relationship]:
        """Parse a Neo4j Relationship object."""
        try:
            return Relationship(
                rel_id=str(neo4j_rel.id),
                rel_type=neo4j_rel.type,
                source_id=str(neo4j_rel.start_node.id),
                target_id=str(neo4j_rel.end_node.id),
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
                        tx.run(query, **params)
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
                        result = session.run(query, **params)
                        nodes = []
                        relationships = []
                        
                        for record in result:
                            for key, value in record.items():
                                if hasattr(value, '__class__') and value.__class__.__name__ == 'Node':
                                    node = self._parse_node(value)
                                    if node and node not in nodes:
                                        nodes.append(node)
                                elif hasattr(value, '__class__') and value.__class__.__name__ == 'Relationship':
                                    rel = self._parse_relationship(value)
                                    if rel and rel not in relationships:
                                        relationships.append(rel)
                        
                        summary = result.consume()
                        
                        results.append(GraphResult(
                            nodes=nodes,
                            relationships=relationships,
                            query=query,
                            stats={'counters': dict(summary.counters)},
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
        
        query = """
        MATCH (a), (b)
        WHERE a.id = $source_id AND b.id = $target_id
        CREATE (a)-[r:%s $props]->(b)
        RETURN r
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
        RETURN r
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
            
            # Get node labels
            query = "CALL db.labels()"
            result = self.execute_query(query)
            if result:
                for record in result.nodes:
                    label = record.get_property('label', '')
                    if label:
                        schema.node_labels[label] = {}
            
            # Get relationship types
            query = "CALL db.relationshipTypes()"
            result = self.execute_query(query)
            if result:
                for record in result.nodes:
                    rel_type = record.get_property('relationshipType', '')
                    if rel_type:
                        schema.relationship_types[rel_type] = {}
            
            # Get property keys
            query = "CALL db.propertyKeys()"
            result = self.execute_query(query)
            if result:
                for record in result.nodes:
                    prop_key = record.get_property('propertyKey', '')
                    if prop_key:
                        schema.property_keys[prop_key] = 'string'  # Default type
            
            # Get indexes
            query = "SHOW INDEXES"
            result = self.execute_query(query)
            if result:
                for record in result.nodes:
                    schema.indexes.append(dict(record.properties))
            
            # Get constraints
            query = "SHOW CONSTRAINTS"
            result = self.execute_query(query)
            if result:
                for record in result.nodes:
                    schema.constraints.append(dict(record.properties))
            
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
        stats['connected'] = self.driver is not None
        
        return stats
    
    def close(self):
        """Close the driver and all sessions."""
        if self.driver:
            self.driver.close()
            self.driver = None
        
        self._session_pool.clear()
        self._query_cache.clear()


# Global graph engine instance
graph_engine = GraphEngine()


# Neo4j trust constants (for SSL)
TRUST_ALL_CERTIFICATES = "TRUST_ALL_CERTIFICATES"
TRUST_SYSTEM_CA_SIGNED_CERTIFICATES = "TRUST_SYSTEM_CA_SIGNED_CERTIFICATES"
