"""
Neo4j Database Integration for OpenLens

Provides graph database operations for:
- Users (nodes)
- Posts (nodes)
- Hashtags (nodes)
- Locations (nodes)
- Entities (nodes)
- Relationships (POSTED_BY, MENTIONS, TAGGED_WITH, LOCATED_AT, etc.)

Dependencies:
- neo4j: Neo4j Python driver
- python-dotenv: Environment variables
"""

import os
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Neo4jDatabase:
    """
    Manages Neo4j database connections and graph operations.
    """
    
    def __init__(self):
        """Initialize Neo4j database connection."""
        self.driver = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Neo4j driver."""
        uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        username = os.getenv('NEO4J_USERNAME', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD', 'password')
        
        try:
            from neo4j import GraphDatabase
            self.driver = GraphDatabase.driver(
                uri,
                auth=(username, password),
                max_connection_pool_size=50,
                connection_timeout=30,
                encrypted=True,
            )
            # Verify connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print(f"Connected to Neo4j at {uri}")
        except ImportError:
            print("Neo4j Python driver not installed. Install with: pip install neo4j")
            self.driver = None
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            self.driver = None
    
    def close(self):
        """Close Neo4j driver."""
        if self.driver:
            self.driver.close()
    
    def _execute_query(self, query: str, parameters: Dict = None, read_only: bool = True) -> List[Dict]:
        """
        Execute a Cypher query.
        
        Args:
            query: Cypher query string.
            parameters: Query parameters.
            read_only: Whether the query is read-only.
            
        Returns:
            List of result dictionaries.
        """
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
        except Exception as e:
            print(f"Failed to execute query: {e}")
            return []
    
    def create_constraints(self):
        """Create database constraints for performance."""
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (h:Hashtag) REQUIRE h.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (u:User) ON (u.username)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Post) ON (p.platform)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Post) ON (p.timestamp)",
            "CREATE INDEX IF NOT EXISTS FOR (h:Hashtag) ON (h.name)",
            "CREATE INDEX IF NOT EXISTS FOR (l:Location) ON (l.latitude, l.longitude)",
        ]
        
        for query in queries:
            self._execute_query(query)
        
        print("Created Neo4j constraints and indexes")
    
    # --- Node Operations ---
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create a user node.
        
        Args:
            user_data: Dictionary containing user data.
            
        Returns:
            Created user node or None if failed.
        """
        query = """
        MERGE (u:User {id: $id})
        SET u += $properties
        RETURN u
        """
        
        properties = {
            'username': user_data.get('username'),
            'display_name': user_data.get('display_name'),
            'bio': user_data.get('bio'),
            'profile_image': user_data.get('profile_image'),
            'platform': user_data.get('platform'),
            'platform_id': user_data.get('platform_id'),
            'followers': user_data.get('followers', 0),
            'following': user_data.get('following', 0),
            'posts_count': user_data.get('posts_count', 0),
            'is_verified': user_data.get('is_verified', False),
            'created_at': user_data.get('created_at', datetime.utcnow().isoformat()),
            'updated_at': datetime.utcnow().isoformat(),
        }
        
        result = self._execute_query(query, {
            'id': user_data.get('id'),
            'properties': properties
        })
        
        return result[0] if result else None
    
    def create_post(self, post_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create a post node.
        
        Args:
            post_data: Dictionary containing post data.
            
        Returns:
            Created post node or None if failed.
        """
        query = """
        MERGE (p:Post {id: $id})
        SET p += $properties
        RETURN p
        """
        
        properties = {
            'platform': post_data.get('platform'),
            'platform_id': post_data.get('platform_id'),
            'content': post_data.get('content', ''),
            'author_id': post_data.get('author_id'),
            'author_name': post_data.get('author_name'),
            'author_username': post_data.get('author_username'),
            'timestamp': post_data.get('timestamp'),
            'likes': post_data.get('likes', 0),
            'reposts': post_data.get('reposts', 0),
            'views': post_data.get('views', 0),
            'comments': post_data.get('comments', 0),
            'url': post_data.get('url'),
            'language': post_data.get('language'),
            'sentiment_score': post_data.get('sentiment_score'),
            'sentiment_label': post_data.get('sentiment_label'),
            'is_processed': post_data.get('is_processed', False),
            'created_at': post_data.get('created_at', datetime.utcnow().isoformat()),
        }
        
        result = self._execute_query(query, {
            'id': post_data.get('id'),
            'properties': properties
        })
        
        return result[0] if result else None
    
    def create_hashtag(self, hashtag_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create a hashtag node.
        
        Args:
            hashtag_data: Dictionary containing hashtag data.
            
        Returns:
            Created hashtag node or None if failed.
        """
        query = """
        MERGE (h:Hashtag {name: $name})
        SET h += $properties
        RETURN h
        """
        
        properties = {
            'normalized_name': hashtag_data.get('normalized_name', hashtag_data.get('name', '').lower()),
            'count': hashtag_data.get('count', 1),
            'first_seen': hashtag_data.get('first_seen', datetime.utcnow().isoformat()),
            'last_seen': datetime.utcnow().isoformat(),
        }
        
        result = self._execute_query(query, {
            'name': hashtag_data.get('name'),
            'properties': properties
        })
        
        return result[0] if result else None
    
    def create_location(self, location_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create a location node.
        
        Args:
            location_data: Dictionary containing location data.
            
        Returns:
            Created location node or None if failed.
        """
        query = """
        MERGE (l:Location {id: $id})
        SET l += $properties
        RETURN l
        """
        
        # Create a unique ID based on coordinates
        lat = location_data.get('latitude', 0)
        lon = location_data.get('longitude', 0)
        location_id = f"{lat:.6f},{lon:.6f}"
        
        properties = {
            'latitude': lat,
            'longitude': lon,
            'altitude': location_data.get('altitude'),
            'place_name': location_data.get('place_name'),
            'city': location_data.get('city'),
            'region': location_data.get('region'),
            'country': location_data.get('country'),
            'country_code': location_data.get('country_code'),
            'address': location_data.get('address'),
            'post_count': location_data.get('post_count', 1),
        }
        
        result = self._execute_query(query, {
            'id': location_id,
            'properties': properties
        })
        
        return result[0] if result else None
    
    def create_entity(self, entity_data: Dict[str, Any]) -> Optional[Dict]:
        """
        Create an entity node (for NLP-extracted entities).
        
        Args:
            entity_data: Dictionary containing entity data.
            
        Returns:
            Created entity node or None if failed.
        """
        query = """
        MERGE (e:Entity {id: $id})
        SET e += $properties
        RETURN e
        """
        
        entity_id = f"{entity_data.get('entity_type', 'UNKNOWN')}:{entity_data.get('text', '')}"
        
        properties = {
            'entity_type': entity_data.get('entity_type'),
            'text': entity_data.get('text'),
            'normalized_text': entity_data.get('normalized_text', entity_data.get('text', '').lower()),
            'start_char': entity_data.get('start_char'),
            'end_char': entity_data.get('end_char'),
            'confidence': entity_data.get('confidence'),
            'first_seen': entity_data.get('first_seen', datetime.utcnow().isoformat()),
            'last_seen': datetime.utcnow().isoformat(),
        }
        
        result = self._execute_query(query, {
            'id': entity_id,
            'properties': properties
        })
        
        return result[0] if result else None
    
    # --- Relationship Operations ---
    
    def create_posted_by_relationship(self, user_id: str, post_id: str) -> bool:
        """
        Create a POSTED_BY relationship between a user and a post.
        
        Args:
            user_id: User node ID.
            post_id: Post node ID.
            
        Returns:
            True if successful, False otherwise.
        """
        query = """
        MATCH (u:User {id: $user_id}), (p:Post {id: $post_id})
        MERGE (u)-[r:POSTED_BY]->(p)
        RETURN r
        """
        
        result = self._execute_query(query, {
            'user_id': user_id,
            'post_id': post_id
        })
        
        return len(result) > 0
    
    def create_mentions_relationship(self, post_id: str, user_id: str, username: str = None) -> bool:
        """
        Create a MENTIONS relationship between a post and a user.
        
        Args:
            post_id: Post node ID.
            user_id: User node ID.
            username: Username (for creating user if not exists).
            
        Returns:
            True if successful, False otherwise.
        """
        query = """
        MATCH (p:Post {id: $post_id}), (u:User {id: $user_id})
        MERGE (p)-[r:MENTIONS]->(u)
        RETURN r
        """
        
        result = self._execute_query(query, {
            'post_id': post_id,
            'user_id': user_id
        })
        
        return len(result) > 0
    
    def create_tagged_with_relationship(self, post_id: str, hashtag_name: str) -> bool:
        """
        Create a TAGGED_WITH relationship between a post and a hashtag.
        
        Args:
            post_id: Post node ID.
            hashtag_name: Hashtag name.
            
        Returns:
            True if successful, False otherwise.
        """
        query = """
        MATCH (p:Post {id: $post_id}), (h:Hashtag {name: $hashtag_name})
        MERGE (p)-[r:TAGGED_WITH]->(h)
        RETURN r
        """
        
        result = self._execute_query(query, {
            'post_id': post_id,
            'hashtag_name': hashtag_name
        })
        
        return len(result) > 0
    
    def create_located_at_relationship(self, post_id: str, location_id: str) -> bool:
        """
        Create a LOCATED_AT relationship between a post and a location.
        
        Args:
            post_id: Post node ID.
            location_id: Location node ID.
            
        Returns:
            True if successful, False otherwise.
        """
        query = """
        MATCH (p:Post {id: $post_id}), (l:Location {id: $location_id})
        MERGE (p)-[r:LOCATED_AT]->(l)
        RETURN r
        """
        
        result = self._execute_query(query, {
            'post_id': post_id,
            'location_id': location_id
        })
        
        return len(result) > 0
    
    def create_contains_entity_relationship(self, post_id: str, entity_id: str) -> bool:
        """
        Create a CONTAINS_ENTITY relationship between a post and an entity.
        
        Args:
            post_id: Post node ID.
            entity_id: Entity node ID.
            
        Returns:
            True if successful, False otherwise.
        """
        query = """
        MATCH (p:Post {id: $post_id}), (e:Entity {id: $entity_id})
        MERGE (p)-[r:CONTAINS_ENTITY]->(e)
        RETURN r
        """
        
        result = self._execute_query(query, {
            'post_id': post_id,
            'entity_id': entity_id
        })
        
        return len(result) > 0
    
    # --- Complex Operations ---
    
    def save_post_with_relationships(self, post_data: Dict[str, Any]) -> bool:
        """
        Save a post with all its relationships to Neo4j.
        
        Args:
            post_data: Dictionary containing post data and relationships.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Create post
            post = self.create_post(post_data)
            if not post:
                return False
            
            post_id = post_data.get('id')
            
            # Create author if exists
            if post_data.get('author_id'):
                user_data = {
                    'id': post_data.get('author_id'),
                    'username': post_data.get('author_username'),
                    'display_name': post_data.get('author_name'),
                    'platform': post_data.get('platform'),
                }
                self.create_user(user_data)
                self.create_posted_by_relationship(post_data.get('author_id'), post_id)
            
            # Create hashtags
            if post_data.get('hashtags'):
                for tag in post_data['hashtags']:
                    hashtag_data = {
                        'name': tag,
                        'normalized_name': tag.lower().strip('#'),
                    }
                    self.create_hashtag(hashtag_data)
                    self.create_tagged_with_relationship(post_id, tag)
            
            # Create mentions
            if post_data.get('mentions'):
                for mention in post_data['mentions']:
                    mention_data = {
                        'id': mention.get('id', mention.get('username')),
                        'username': mention.get('username'),
                        'display_name': mention.get('display_name'),
                        'platform': post_data.get('platform'),
                    }
                    self.create_user(mention_data)
                    self.create_mentions_relationship(post_id, mention.get('id', mention.get('username')))
            
            # Create location
            if post_data.get('geotag'):
                geotag = post_data['geotag']
                location_data = {
                    'latitude': geotag.get('latitude'),
                    'longitude': geotag.get('longitude'),
                    'place_name': geotag.get('place_name'),
                    'city': geotag.get('city'),
                    'country': geotag.get('country'),
                }
                location = self.create_location(location_data)
                if location:
                    location_id = f"{geotag.get('latitude', 0):.6f},{geotag.get('longitude', 0):.6f}"
                    self.create_located_at_relationship(post_id, location_id)
            
            # Create entities (NLP)
            if post_data.get('entities'):
                for entity in post_data['entities']:
                    entity_data = {
                        'entity_type': entity.get('label'),
                        'text': entity.get('text'),
                        'normalized_text': entity.get('text', '').lower(),
                        'start_char': entity.get('start'),
                        'end_char': entity.get('end'),
                    }
                    entity_node = self.create_entity(entity_data)
                    if entity_node:
                        entity_id = f"{entity.get('label', 'UNKNOWN')}:{entity.get('text', '')}"
                        self.create_contains_entity_relationship(post_id, entity_id)
            
            return True
        except Exception as e:
            print(f"Failed to save post with relationships: {e}")
            return False
    
    # --- Query Operations ---
    
    def get_user_posts(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get posts by a user.
        
        Args:
            user_id: User ID.
            limit: Maximum number of posts.
            
        Returns:
            List of post dictionaries.
        """
        query = """
        MATCH (u:User {id: $user_id})-[:POSTED_BY]->(p:Post)
        RETURN p
        ORDER BY p.timestamp DESC
        LIMIT $limit
        """
        
        results = self._execute_query(query, {
            'user_id': user_id,
            'limit': limit
        })
        
        return [dict(record['p']) for record in results]
    
    def get_posts_by_hashtag(self, hashtag: str, limit: int = 10) -> List[Dict]:
        """
        Get posts by hashtag.
        
        Args:
            hashtag: Hashtag name.
            limit: Maximum number of posts.
            
        Returns:
            List of post dictionaries.
        """
        query = """
        MATCH (h:Hashtag {name: $hashtag})<-[:TAGGED_WITH]-(p:Post)
        RETURN p
        ORDER BY p.timestamp DESC
        LIMIT $limit
        """
        
        results = self._execute_query(query, {
            'hashtag': hashtag,
            'limit': limit
        })
        
        return [dict(record['p']) for record in results]
    
    def get_posts_by_location(self, latitude: float, longitude: float, radius_km: float = 10, limit: int = 10) -> List[Dict]:
        """
        Get posts by location (within a radius).
        
        Args:
            latitude: Center latitude.
            longitude: Center longitude.
            radius_km: Search radius in kilometers.
            limit: Maximum number of posts.
            
        Returns:
            List of post dictionaries.
        """
        # Note: This requires the APOC library in Neo4j for spatial queries
        # For simplicity, we'll use a basic distance calculation
        query = """
        MATCH (l:Location), (p:Post)-[:LOCATED_AT]->(l)
        WHERE abs(l.latitude - $latitude) < 0.1 AND abs(l.longitude - $longitude) < 0.1
        RETURN p, l
        ORDER BY p.timestamp DESC
        LIMIT $limit
        """
        
        results = self._execute_query(query, {
            'latitude': latitude,
            'longitude': longitude,
            'limit': limit
        })
        
        return [dict(record['p']) for record in results]
    
    def get_connected_users(self, user_id: str, max_depth: int = 2, limit: int = 20) -> List[Dict]:
        """
        Get users connected to a given user (via mentions, etc.).
        
        Args:
            user_id: User ID.
            max_depth: Maximum depth of connections.
            limit: Maximum number of users.
            
        Returns:
            List of user dictionaries.
        """
        query = """
        MATCH path = (u:User {id: $user_id})-[:POSTED_BY|MENTIONS*1..$max_depth]->(other:User)
        RETURN other
        LIMIT $limit
        """
        
        results = self._execute_query(query, {
            'user_id': user_id,
            'max_depth': max_depth,
            'limit': limit
        })
        
        return [dict(record['other']) for record in results]
    
    def get_trending_hashtags(self, limit: int = 10) -> List[Dict]:
        """
        Get trending hashtags by post count.
        
        Args:
            limit: Maximum number of hashtags.
            
        Returns:
            List of hashtag dictionaries.
        """
        query = """
        MATCH (h:Hashtag)
        RETURN h
        ORDER BY h.post_count DESC
        LIMIT $limit
        """
        
        results = self._execute_query(query, {
            'limit': limit
        })
        
        return [dict(record['h']) for record in results]
    
    def get_popular_locations(self, limit: int = 10) -> List[Dict]:
        """
        Get popular locations by post count.
        
        Args:
            limit: Maximum number of locations.
            
        Returns:
            List of location dictionaries.
        """
        query = """
        MATCH (l:Location)
        RETURN l
        ORDER BY l.post_count DESC
        LIMIT $limit
        """
        
        results = self._execute_query(query, {
            'limit': limit
        })
        
        return [dict(record['l']) for record in results]
    
    def get_entities_by_type(self, entity_type: str, limit: int = 10) -> List[Dict]:
        """
        Get entities by type.
        
        Args:
            entity_type: Entity type (e.g., 'PERSON', 'ORG', 'GPE').
            limit: Maximum number of entities.
            
        Returns:
            List of entity dictionaries.
        """
        query = """
        MATCH (e:Entity {entity_type: $entity_type})
        RETURN e
        ORDER BY e.last_seen DESC
        LIMIT $limit
        """
        
        results = self._execute_query(query, {
            'entity_type': entity_type,
            'limit': limit
        })
        
        return [dict(record['e']) for record in results]
    
    def get_network_graph(self, center_id: str, max_depth: int = 2, limit: int = 50) -> Dict:
        """
        Get a network graph centered on a user or post.
        
        Args:
            center_id: Center node ID (user or post).
            max_depth: Maximum depth of connections.
            limit: Maximum number of nodes.
            
        Returns:
            Dictionary with nodes and relationships.
        """
        query = """
        MATCH path = (center)-[*..$max_depth]-(other)
        WHERE center.id = $center_id
        RETURN nodes(path) as nodes, relationships(path) as rels
        LIMIT $limit
        """
        
        results = self._execute_query(query, {
            'center_id': center_id,
            'max_depth': max_depth,
            'limit': limit
        })
        
        nodes = []
        relationships = []
        
        for record in results:
            for node in record['nodes']:
                node_dict = dict(node)
                if node_dict not in nodes:
                    nodes.append(node_dict)
            
            for rel in record['rels']:
                rel_dict = dict(rel)
                relationships.append(rel_dict)
        
        return {
            'nodes': nodes,
            'relationships': relationships
        }


# Initialize Neo4j database
_neo4j_db = Neo4jDatabase()


def get_neo4j_db():
    """
    Get the Neo4j database instance.
    
    Returns:
        Neo4jDatabase instance.
    """
    return _neo4j_db


# For use with Flask
import flask

def init_neo4j(app: flask.Flask):
    """
    Initialize Neo4j with Flask app.
    
    Args:
        app: Flask application.
    """
    # Create constraints on startup
    @app.before_first_request
    def create_constraints():
        _neo4j_db.create_constraints()
