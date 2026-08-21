"""
Entity Resolution Module for OpenLens

Provides entity resolution capabilities:
- Record linkage
- Deduplication
- Identity matching
- Fuzzy matching
- Graph-based entity resolution
"""

import time
import json
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from collections import defaultdict
import re

# Try to import numpy
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("NumPy not available. Install with: pip install numpy")

# Try to import pandas
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Pandas not available. Install with: pip install pandas")

# Try to import recordlinkage
try:
    import recordlinkage
    RECORDLINKAGE_AVAILABLE = True
except ImportError:
    RECORDLINKAGE_AVAILABLE = False
    print("recordlinkage not available. Install with: pip install recordlinkage")

# Try to import fuzzywuzzy
try:
    from fuzzywuzzy import fuzz, token_set_ratio, token_sort_ratio
    FUZZYWUZZY_AVAILABLE = True
except ImportError:
    FUZZYWUZZY_AVAILABLE = False
    print("fuzzywuzzy not available. Install with: pip install fuzzywuzzy python-Levenshtein")

# Try to import rapidfuzz (faster alternative to fuzzywuzzy)
try:
    from rapidfuzz import fuzz as rapidfuzz_fuzz
    from rapidfuzz import process
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    print("rapidfuzz not available. Install with: pip install rapidfuzz")


@dataclass
class Entity:
    """Represents an entity for resolution."""
    entity_id: str
    type: str  # Person, Organization, etc.
    attributes: Dict[str, Any] = field(default_factory=dict)
    source: str = ''
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'entity_id': self.entity_id,
            'type': self.type,
            'attributes': self.attributes,
            'source': self.source,
            'confidence': self.confidence,
        }


@dataclass
class EntityMatch:
    """Represents a match between entities."""
    entity_id_1: str
    entity_id_2: str
    similarity_score: float
    matching_attributes: List[str] = field(default_factory=list)
    non_matching_attributes: List[str] = field(default_factory=list)
    method: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'entity_id_1': self.entity_id_1,
            'entity_id_2': self.entity_id_2,
            'similarity_score': self.similarity_score,
            'matching_attributes': self.matching_attributes,
            'non_matching_attributes': self.non_matching_attributes,
            'method': self.method,
        }


@dataclass
class EntityCluster:
    """Represents a cluster of matched entities."""
    cluster_id: str
    entities: List[str] = field(default_factory=list)
    representative: str = ''
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'cluster_id': self.cluster_id,
            'entities': self.entities,
            'representative': self.representative,
            'confidence': self.confidence,
        }


@dataclass
class EntityResolutionResult:
    """Result of entity resolution."""
    method: str
    matches: List[EntityMatch] = field(default_factory=list)
    clusters: List[EntityCluster] = field(default_factory=list)
    total_entities: int = 0
    matched_entities: int = 0
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'method': self.method,
            'matches': [m.to_dict() for m in self.matches],
            'clusters': [c.to_dict() for c in self.clusters],
            'total_entities': self.total_entities,
            'matched_entities': self.matched_entities,
            'execution_time': self.execution_time,
        }


@dataclass
class EntityResolutionConfig:
    """Configuration for entity resolution."""
    methods: List[str] = field(default_factory=lambda: ['exact', 'fuzzy', 'graph'])
    similarity_threshold: float = 0.85
    fuzzy_threshold: float = 80.0
    block_keys: List[str] = field(default_factory=list)
    comparison_keys: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'methods': self.methods,
            'similarity_threshold': self.similarity_threshold,
            'fuzzy_threshold': self.fuzzy_threshold,
            'block_keys': self.block_keys,
            'comparison_keys': self.comparison_keys,
        }


class EntityResolver:
    """
    Entity resolver for OpenLens.
    
    Provides entity resolution capabilities:
    - Exact matching
    - Fuzzy matching
    - Record linkage
    - Graph-based resolution
    - Clustering
    """
    
    def __init__(self, graph_engine=None, config: EntityResolutionConfig = None):
        """
        Initialize the entity resolver.
        
        Args:
            graph_engine: GraphEngine instance.
            config: EntityResolutionConfig.
        """
        self.graph_engine = graph_engine
        self.config = config or EntityResolutionConfig()
    
    def resolve_entities(self, entities: List[Entity], 
                        method: str = None) -> EntityResolutionResult:
        """
        Resolve entities (find matches and clusters).
        
        Args:
            entities: List of Entity objects.
            method: Specific method to use (None for all methods).
            
        Returns:
            EntityResolutionResult.
        """
        start_time = time.time()
        
        methods = [method] if method else self.config.methods
        all_matches = []
        total_entities = len(entities)
        
        for method in methods:
            if method == 'exact':
                matches = self._exact_match(entities)
            elif method == 'fuzzy':
                matches = self._fuzzy_match(entities)
            elif method == 'record_linkage':
                matches = self._record_linkage_match(entities)
            elif method == 'graph':
                matches = self._graph_match(entities)
            else:
                continue
            
            all_matches.extend(matches)
        
        # Create clusters from matches
        clusters = self._create_clusters(all_matches, entities)
        
        execution_time = time.time() - start_time
        
        return EntityResolutionResult(
            method=', '.join(methods),
            matches=all_matches,
            clusters=clusters,
            total_entities=total_entities,
            matched_entities=len(set([m.entity_id_1 for m in all_matches] + [m.entity_id_2 for m in all_matches])),
            execution_time=execution_time,
        )
    
    def _exact_match(self, entities: List[Entity]) -> List[EntityMatch]:
        """Perform exact matching."""
        if not entities:
            return []
        
        matches = []
        
        try:
            # Group entities by type
            entities_by_type = defaultdict(list)
            for entity in entities:
                entities_by_type[entity.type].append(entity)
            
            # Compare entities of the same type
            for entity_type, type_entities in entities_by_type.items():
                for i in range(len(type_entities)):
                    for j in range(i + 1, len(type_entities)):
                        entity1 = type_entities[i]
                        entity2 = type_entities[j]
                        
                        # Check for exact matches on key attributes
                        matching_attrs = []
                        non_matching_attrs = []
                        
                        for key in self.config.comparison_keys or entity1.attributes.keys():
                            if key in entity1.attributes and key in entity2.attributes:
                                if entity1.attributes[key] == entity2.attributes[key]:
                                    matching_attrs.append(key)
                                else:
                                    non_matching_attrs.append(key)
                        
                        # Calculate similarity score
                        if matching_attrs:
                            similarity = len(matching_attrs) / (len(matching_attrs) + len(non_matching_attrs))
                        else:
                            similarity = 0.0
                        
                        if similarity >= self.config.similarity_threshold:
                            matches.append(EntityMatch(
                                entity_id_1=entity1.entity_id,
                                entity_id_2=entity2.entity_id,
                                similarity_score=similarity,
                                matching_attributes=matching_attrs,
                                non_matching_attributes=non_matching_attrs,
                                method='exact',
                            ))
        
        except Exception as e:
            print(f"Exact matching error: {e}")
        
        return matches
    
    def _fuzzy_match(self, entities: List[Entity]) -> List[EntityMatch]:
        """Perform fuzzy matching."""
        if not entities:
            return []
        
        matches = []
        
        try:
            # Group entities by type
            entities_by_type = defaultdict(list)
            for entity in entities:
                entities_by_type[entity.type].append(entity)
            
            # Use rapidfuzz if available, otherwise fuzzywuzzy
            fuzz_func = None
            if RAPIDFUZZ_AVAILABLE:
                fuzz_func = rapidfuzz_fuzz.token_set_ratio
            elif FUZZYWUZZY_AVAILABLE:
                fuzz_func = token_set_ratio
            
            if not fuzz_func:
                return []
            
            # Compare entities of the same type
            for entity_type, type_entities in entities_by_type.items():
                for i in range(len(type_entities)):
                    for j in range(i + 1, len(type_entities)):
                        entity1 = type_entities[i]
                        entity2 = type_entities[j]
                        
                        # Compare name attributes
                        name1 = entity1.attributes.get('name', '')
                        name2 = entity2.attributes.get('name', '')
                        
                        if name1 and name2:
                            similarity = fuzz_func(name1, name2) / 100.0
                            
                            if similarity >= self.config.fuzzy_threshold / 100.0:
                                matches.append(EntityMatch(
                                    entity_id_1=entity1.entity_id,
                                    entity_id_2=entity2.entity_id,
                                    similarity_score=similarity,
                                    matching_attributes=['name'],
                                    non_matching_attributes=[],
                                    method='fuzzy',
                                ))
                        
                        # Compare other string attributes
                        for key in self.config.comparison_keys or ['name', 'email', 'phone', 'address']:
                            if key in entity1.attributes and key in entity2.attributes:
                                val1 = str(entity1.attributes[key])
                                val2 = str(entity2.attributes[key])
                                
                                if val1 and val2:
                                    similarity = fuzz_func(val1, val2) / 100.0
                                    
                                    if similarity >= self.config.fuzzy_threshold / 100.0:
                                        matches.append(EntityMatch(
                                            entity_id_1=entity1.entity_id,
                                            entity_id_2=entity2.entity_id,
                                            similarity_score=similarity,
                                            matching_attributes=[key],
                                            non_matching_attributes=[],
                                            method='fuzzy',
                                        ))
        
        except Exception as e:
            print(f"Fuzzy matching error: {e}")
        
        return matches
    
    def _record_linkage_match(self, entities: List[Entity]) -> List[EntityMatch]:
        """Perform record linkage matching."""
        if not RECORDLINKAGE_AVAILABLE or not PANDAS_AVAILABLE or not entities:
            return []
        
        matches = []
        
        try:
            # Convert entities to DataFrame
            data = []
            for entity in entities:
                row = {'id': entity.entity_id, 'type': entity.type}
                row.update(entity.attributes)
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Index by block keys
            if self.config.block_keys:
                indexer = recordlinkage.Index()
                indexer.block(self.config.block_keys[0])
                pairs = indexer.index(df)
            else:
                # If no block keys, compare all pairs
                pairs = list(recordlinkage.pairs.Pairs(df, df))
            
            # Compare records
            compare = recordlinkage.Compare()
            
            # Add comparison rules
            for key in self.config.comparison_keys or df.columns:
                if key not in ['id', 'type'] and df[key].dtype == 'object':
                    compare.string(key, key, method='levenshtein', threshold=self.config.fuzzy_threshold / 100.0)
                elif key not in ['id', 'type']:
                    compare.exact(key, key)
            
            # Compute similarity scores
            features = compare.compute(pairs, df)
            
            # Get matches
            matches_df = features[features.sum(axis=1) >= self.config.similarity_threshold]
            
            for _, row in matches_df.iterrows():
                entity_id_1 = row.name[0]
                entity_id_2 = row.name[1]
                similarity = row.mean()
                
                matches.append(EntityMatch(
                    entity_id_1=entity_id_1,
                    entity_id_2=entity_id_2,
                    similarity_score=similarity,
                    matching_attributes=[col for col in row.index if row[col] > 0.5],
                    non_matching_attributes=[col for col in row.index if row[col] <= 0.5],
                    method='record_linkage',
                ))
        
        except Exception as e:
            print(f"Record linkage error: {e}")
        
        return matches
    
    def _graph_match(self, entities: List[Entity]) -> List[EntityMatch]:
        """Perform graph-based matching."""
        if not self.graph_engine or not entities:
            return []
        
        matches = []
        
        try:
            # Create a mapping from entity ID to entity
            entity_map = {e.entity_id: e for e in entities}
            
            # Find entities that are connected in the graph
            for entity in entities:
                # Find nodes in the graph that match this entity
                query = "MATCH (n) WHERE n.id = $id RETURN n"
                result = self.graph_engine.execute_query(query, {'id': entity.entity_id})
                
                if not result or not result.nodes:
                    continue
                
                # Find connected nodes
                query = "MATCH (n)-[r]->(m) WHERE n.id = $id RETURN m"
                result = self.graph_engine.execute_query(query, {'id': entity.entity_id})
                
                if result:
                    for connected_node in result.nodes:
                        connected_id = connected_node.node_id
                        
                        if connected_id in entity_map:
                            # Calculate similarity based on graph proximity
                            # For now, use a simple score based on connection
                            similarity = 0.9  # High similarity for connected entities
                            
                            matches.append(EntityMatch(
                                entity_id_1=entity.entity_id,
                                entity_id_2=connected_id,
                                similarity_score=similarity,
                                matching_attributes=['graph_connection'],
                                non_matching_attributes=[],
                                method='graph',
                            ))
        
        except Exception as e:
            print(f"Graph matching error: {e}")
        
        return matches
    
    def _create_clusters(self, matches: List[EntityMatch], 
                         entities: List[Entity]) -> List[EntityCluster]:
        """Create clusters from matches."""
        if not matches:
            return []
        
        # Build connected components
        graph = defaultdict(set)
        entity_ids = set()
        
        for match in matches:
            graph[match.entity_id_1].add(match.entity_id_2)
            graph[match.entity_id_2].add(match.entity_id_1)
            entity_ids.add(match.entity_id_1)
            entity_ids.add(match.entity_id_2)
        
        # Find connected components
        visited = set()
        clusters = []
        cluster_id = 0
        
        for entity_id in entity_ids:
            if entity_id not in visited:
                # BFS to find all connected entities
                queue = [entity_id]
                cluster_entities = []
                
                while queue:
                    current = queue.pop(0)
                    if current not in visited:
                        visited.add(current)
                        cluster_entities.append(current)
                        queue.extend(graph[current])
                
                if len(cluster_entities) > 1:
                    # Find representative (entity with most connections)
                    representative = max(
                        cluster_entities,
                        key=lambda x: len(graph.get(x, set()))
                    )
                    
                    # Calculate confidence (average similarity score)
                    cluster_matches = [
                        m for m in matches
                        if m.entity_id_1 in cluster_entities and m.entity_id_2 in cluster_entities
                    ]
                    confidence = sum(m.similarity_score for m in cluster_matches) / len(cluster_matches) if cluster_matches else 0.0
                    
                    clusters.append(EntityCluster(
                        cluster_id=f"cluster_{cluster_id}",
                        entities=cluster_entities,
                        representative=representative,
                        confidence=confidence,
                    ))
                    
                    cluster_id += 1
        
        return clusters
    
    _RESERVED_ENTITY_KEYS = {'entity_id', 'id', 'type', 'source', 'confidence', 'attributes'}

    def _coerce_entities(self, entities: List[Union["Entity", Dict[str, Any]]]) -> List["Entity"]:
        """
        Accept raw dicts (as the API router sends) alongside Entity objects.

        A dict may carry explicit 'attributes'; otherwise every non-reserved
        key becomes an attribute.
        """
        import uuid as _uuid

        coerced: List[Entity] = []
        for index, item in enumerate(entities):
            if isinstance(item, Entity):
                coerced.append(item)
                continue
            if not isinstance(item, dict):
                continue
            attributes = item.get('attributes')
            if not isinstance(attributes, dict):
                attributes = {k: v for k, v in item.items()
                              if k not in self._RESERVED_ENTITY_KEYS}
            coerced.append(Entity(
                entity_id=str(item.get('entity_id') or item.get('id') or _uuid.uuid4()),
                type=str(item.get('type', '')),
                attributes=attributes,
                source=str(item.get('source', '')),
                confidence=float(item.get('confidence', 1.0)),
            ))
        return coerced

    def resolve_exact(self, entities: List[Union["Entity", Dict[str, Any]]]) -> EntityResolutionResult:
        """Public: exact matching over entities or raw dicts."""
        return self.resolve_entities(self._coerce_entities(entities), method='exact')

    def resolve_fuzzy(self, entities: List[Union["Entity", Dict[str, Any]]],
                      threshold: float = None) -> EntityResolutionResult:
        """
        Public: fuzzy matching. Raises when no fuzzy library is installed -
        an empty result here would be indistinguishable from "no duplicates".
        """
        if not (FUZZYWUZZY_AVAILABLE or RAPIDFUZZ_AVAILABLE):
            raise RuntimeError(
                'fuzzy matching requires rapidfuzz (or fuzzywuzzy); '
                'install with: pip install rapidfuzz')
        resolver = self
        if threshold is not None:
            # Never mutate the module singleton's config per request.
            from dataclasses import replace as _replace
            resolver = EntityResolver(
                graph_engine=self.graph_engine,
                config=_replace(self.config, fuzzy_threshold=float(threshold)),
            )
        return resolver.resolve_entities(self._coerce_entities(entities), method='fuzzy')

    def resolve_record_linkage(self, entities: List[Union["Entity", Dict[str, Any]]]) -> EntityResolutionResult:
        """Public: record-linkage matching (requires the recordlinkage library)."""
        if not (RECORDLINKAGE_AVAILABLE and PANDAS_AVAILABLE):
            raise RuntimeError(
                'record linkage requires the recordlinkage and pandas libraries; '
                'install with: pip install recordlinkage pandas')
        return self.resolve_entities(self._coerce_entities(entities), method='record_linkage')

    def resolve_graph_based(self, entities: List[Union["Entity", Dict[str, Any]]]) -> EntityResolutionResult:
        """Public: graph-based matching."""
        return self.resolve_entities(self._coerce_entities(entities), method='graph')

    def deduplicate_entities(self, entity_type: str = None,
                             apply: bool = False) -> Dict[str, Any]:
        """
        Find (and optionally merge) duplicate entities in the graph.

        Dry-run by default: merging issues DETACH DELETE against the graph, so
        destruction must be an explicit opt-in.

        Returns:
            {'clusters': [...], 'merged': int, 'applied': bool}
        """
        clusters = self.find_duplicate_entities(entity_type)
        merged = 0
        if apply:
            for cluster in clusters:
                if self.merge_duplicate_entities(cluster):
                    merged += 1
        return {
            'clusters': [c.to_dict() for c in clusters],
            'merged': merged,
            'applied': apply,
        }

    def resolve_from_graph(self, entity_type: str = None) -> EntityResolutionResult:
        """
        Resolve entities from the graph.
        
        Args:
            entity_type: Type of entities to resolve (None for all).
            
        Returns:
            EntityResolutionResult.
        """
        if not self.graph_engine:
            return EntityResolutionResult(method='graph')
        
        start_time = time.time()
        
        try:
            # Get all nodes from graph
            query = "MATCH (n) RETURN n"
            result = self.graph_engine.execute_query(query)
            
            if not result:
                return EntityResolutionResult(method='graph')
            
            entities = []
            for node in result.nodes:
                if not entity_type or entity_type in node.labels:
                    entities.append(Entity(
                        entity_id=node.node_id,
                        type=node.labels[0] if node.labels else 'Unknown',
                        attributes=node.properties,
                        source='graph',
                    ))
            
            # Resolve entities
            result = self.resolve_entities(entities)
            result.method = 'graph'
            result.execution_time = time.time() - start_time
            
            return result
        
        except Exception as e:
            print(f"Graph entity resolution error: {e}")
            return EntityResolutionResult(method='graph')
    
    def find_duplicate_entities(self, entity_type: str = None) -> List[EntityCluster]:
        """
        Find duplicate entities in the graph.
        
        Args:
            entity_type: Type of entities to check (None for all).
            
        Returns:
            List of EntityCluster objects.
        """
        result = self.resolve_from_graph(entity_type)
        return [c for c in result.clusters if len(c.entities) > 1]
    
    def merge_duplicate_entities(self, cluster: EntityCluster) -> bool:
        """
        Merge duplicate entities in a cluster.
        
        Args:
            cluster: EntityCluster to merge.
            
        Returns:
            True if merge was successful.
        """
        if not self.graph_engine or not cluster.entities:
            return False
        
        try:
            # Get the representative entity
            representative = cluster.representative
            
            # For each entity in the cluster (except representative), merge its
            # data. All queries parameterised - the old code interpolated ids
            # into Cypher, and its relationship-redirect query was not valid
            # Cypher at all (so relationships were silently dropped before the
            # DETACH DELETE).
            for entity_id in cluster.entities:
                if entity_id == representative:
                    continue

                result = self.graph_engine.execute_query(
                    "MATCH (n) WHERE n.id = $id RETURN n", {'id': entity_id})
                if not result or not result.nodes:
                    continue
                entity_node = result.nodes[0]

                result = self.graph_engine.execute_query(
                    "MATCH (n) WHERE n.id = $id RETURN n", {'id': representative})
                if not result or not result.nodes:
                    continue
                rep_node = result.nodes[0]

                # Merge properties (representative wins on conflict, but keeps
                # its own id).
                merged_properties = {**entity_node.properties, **rep_node.properties}
                merged_properties['id'] = representative

                self.graph_engine.execute_query(
                    "MATCH (n) WHERE n.id = $id SET n += $props",
                    {'id': representative, 'props': merged_properties})

                # Redirect relationships. Cypher cannot recreate a relationship
                # with a dynamic type, so redirected edges become MERGED_REL
                # carrying the original type as a property.
                self.graph_engine.execute_query(
                    """
                    MATCH (src)-[r]->(old {id: $entity_id})
                    MATCH (rep {id: $representative})
                    WHERE src.id <> $representative
                    CREATE (src)-[r2:MERGED_REL]->(rep)
                    SET r2 = properties(r), r2.original_type = type(r)
                    """,
                    {'entity_id': entity_id, 'representative': representative})
                self.graph_engine.execute_query(
                    """
                    MATCH (old {id: $entity_id})-[r]->(dst)
                    MATCH (rep {id: $representative})
                    WHERE dst.id <> $representative
                    CREATE (rep)-[r2:MERGED_REL]->(dst)
                    SET r2 = properties(r), r2.original_type = type(r)
                    """,
                    {'entity_id': entity_id, 'representative': representative})

                self.graph_engine.execute_query(
                    "MATCH (n) WHERE n.id = $id DETACH DELETE n", {'id': entity_id})

            return True
        
        except Exception as e:
            print(f"Entity merge error: {e}")
            return False


# Global entity resolver instance
entity_resolver = EntityResolver()
