"""
Neo4j Models for OpenLens

Defines graph models for Neo4j to store relationships between entities
(e.g., users, posts, locations). Uses the official Neo4j Python driver.

Dependencies:
- neo4j: For Neo4j database access
"""

from typing import Dict, List, Optional, Any
from neo4j import GraphDatabase


class Neo4jManager:
    """
    Manages connections and queries for Neo4j.
    
    Stores entities (users, posts, locations) and their relationships
    (e.g., POSTED_BY, MENTIONS, LOCATED_AT).
    """

    def __init__(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password",
    ):
        """
        Initialize the Neo4j manager.
        
        Args:
            uri: Neo4j server URI (e.g., "bolt://localhost:7687").
            user: Neo4j username.
            password: Neo4j password.
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None

    def connect(self):
        """Connect to the Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Verify connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            print(f"Connected to Neo4j at {self.uri}")
            return True
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
            return False

    def close(self):
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            print("Closed Neo4j connection")

    def _run_query(self, query: str, parameters: Dict = None) -> List[Dict]:
        """
        Run a Cypher query and return the results.
        
        Args:
            query: Cypher query string.
            parameters: Dictionary of query parameters.
            
        Returns:
            List of result dictionaries.
        """
        if not self.driver:
            self.connect()
        
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]

    def create_constraints(self):
        """Create unique constraints for nodes."""
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (l:Location) REQUIRE l.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (h:Hashtag) REQUIRE h.tag IS UNIQUE",
        ]
        for query in queries:
            self._run_query(query)
        print("Created Neo4j constraints")

    def clear_database(self):
        """Clear all nodes and relationships from the database."""
        self._run_query("MATCH (n) DETACH DELETE n")
        print("Cleared Neo4j database")

    # --- User Operations ---

    def add_user(
        self,
        user_id: str,
        platform: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        **properties,
    ) -> bool:
        """
        Add or update a user node.
        
        Args:
            user_id: Unique user ID.
            platform: Platform name (e.g., "vk", "telegram").
            username: User's username.
            first_name: User's first name.
            last_name: User's last name.
            **properties: Additional properties.
            
        Returns:
            True if successful.
        """
        query = """
        MERGE (u:User {id: $user_id})
        SET u.platform = $platform,
            u.username = $username,
            u.first_name = $first_name,
            u.last_name = $last_name,
            u.full_name = $first_name + ' ' + $last_name,
            u.created_at = datetime()
        """
        parameters = {
            "user_id": user_id,
            "platform": platform,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
        }
        # Add additional properties
        for key, value in properties.items():
            query += f", u.{key} = ${key}"
            parameters[key] = value
        
        self._run_query(query, parameters)
        return True

    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Get a user node by ID.
        
        Args:
            user_id: User ID.
            
        Returns:
            User properties or None if not found.
        """
        query = "MATCH (u:User {id: $user_id}) RETURN u"
        results = self._run_query(query, {"user_id": user_id})
        return results[0].get("u") if results else None

    # --- Post Operations ---

    def add_post(
        self,
        post_id: str,
        platform: str,
        content: str,
        timestamp: str,
        author_id: Optional[str] = None,
        **properties,
    ) -> bool:
        """
        Add or update a post node.
        
        Args:
            post_id: Unique post ID.
            platform: Platform name (e.g., "vk", "telegram").
            content: Post content.
            timestamp: Post timestamp.
            author_id: ID of the author (user).
            **properties: Additional properties.
            
        Returns:
            True if successful.
        """
        query = """
        MERGE (p:Post {id: $post_id})
        SET p.platform = $platform,
            p.content = $content,
            p.timestamp = $timestamp,
            p.created_at = datetime()
        """
        parameters = {
            "post_id": post_id,
            "platform": platform,
            "content": content,
            "timestamp": timestamp,
        }
        # Add additional properties
        for key, value in properties.items():
            query += f", p.{key} = ${key}"
            parameters[key] = value
        
        self._run_query(query, parameters)
        
        # Create POSTED_BY relationship if author_id is provided
        if author_id:
            self._run_query(
                """
                MATCH (u:User {id: $author_id}), (p:Post {id: $post_id})
                MERGE (u)-[r:POSTED_BY]->(p)
                SET r.created_at = datetime()
                """,
                {"author_id": author_id, "post_id": post_id},
            )
        
        return True

    def get_post(self, post_id: str) -> Optional[Dict]:
        """
        Get a post node by ID.
        
        Args:
            post_id: Post ID.
            
        Returns:
            Post properties or None if not found.
        """
        query = "MATCH (p:Post {id: $post_id}) RETURN p"
        results = self._run_query(query, {"post_id": post_id})
        return results[0].get("p") if results else None

    # --- Location Operations ---

    def add_location(
        self,
        location_id: str,
        latitude: float,
        longitude: float,
        address: Optional[str] = None,
        **properties,
    ) -> bool:
        """
        Add or update a location node.
        
        Args:
            location_id: Unique location ID.
            latitude: GPS latitude.
            longitude: GPS longitude.
            address: Human-readable address.
            **properties: Additional properties.
            
        Returns:
            True if successful.
        """
        query = """
        MERGE (l:Location {id: $location_id})
        SET l.latitude = $latitude,
            l.longitude = $longitude,
            l.address = $address,
            l.created_at = datetime()
        """
        parameters = {
            "location_id": location_id,
            "latitude": latitude,
            "longitude": longitude,
            "address": address,
        }
        # Add additional properties
        for key, value in properties.items():
            query += f", l.{key} = ${key}"
            parameters[key] = value
        
        self._run_query(query, parameters)
        return True

    def link_post_to_location(self, post_id: str, location_id: str) -> bool:
        """
        Link a post to a location (LOCATED_AT relationship).
        
        Args:
            post_id: Post ID.
            location_id: Location ID.
            
        Returns:
            True if successful.
        """
        query = """
        MATCH (p:Post {id: $post_id}), (l:Location {id: $location_id})
        MERGE (p)-[r:LOCATED_AT]->(l)
        SET r.created_at = datetime()
        """
        self._run_query(query, {"post_id": post_id, "location_id": location_id})
        return True

    # --- Hashtag Operations ---

    def add_hashtag(self, tag: str) -> bool:
        """
        Add or update a hashtag node.
        
        Args:
            tag: Hashtag text (without #).
            
        Returns:
            True if successful.
        """
        query = """
        MERGE (h:Hashtag {tag: $tag})
        SET h.created_at = datetime()
        """
        self._run_query(query, {"tag": tag})
        return True

    def link_post_to_hashtag(self, post_id: str, tag: str) -> bool:
        """
        Link a post to a hashtag (TAGGED_WITH relationship).
        
        Args:
            post_id: Post ID.
            tag: Hashtag text.
            
        Returns:
            True if successful.
        """
        query = """
        MATCH (p:Post {id: $post_id}), (h:Hashtag {tag: $tag})
        MERGE (p)-[r:TAGGED_WITH]->(h)
        SET r.created_at = datetime()
        """
        self._run_query(query, {"post_id": post_id, "tag": tag})
        return True

    # --- Mention Operations ---

    def link_post_to_mention(self, post_id: str, mentioned_user_id: str) -> bool:
        """
        Link a post to a mentioned user (MENTIONS relationship).
        
        Args:
            post_id: Post ID.
            mentioned_user_id: Mentioned user ID.
            
        Returns:
            True if successful.
        """
        query = """
        MATCH (p:Post {id: $post_id}), (u:User {id: $mentioned_user_id})
        MERGE (p)-[r:MENTIONS]->(u)
        SET r.created_at = datetime()
        """
        self._run_query(query, {"post_id": post_id, "mentioned_user_id": mentioned_user_id})
        return True

    # --- Follower/Friend Operations ---

    def add_follow_relationship(self, follower_id: str, followee_id: str) -> bool:
        """
        Add a FOLLOWS relationship between two users.
        
        Args:
            follower_id: ID of the user who follows.
            followee_id: ID of the user being followed.
            
        Returns:
            True if successful.
        """
        query = """
        MATCH (u1:User {id: $follower_id}), (u2:User {id: $followee_id})
        MERGE (u1)-[r:FOLLOWS]->(u2)
        SET r.created_at = datetime()
        """
        self._run_query(query, {"follower_id": follower_id, "followee_id": followee_id})
        return True

    def add_friend_relationship(self, user1_id: str, user2_id: str) -> bool:
        """
        Add a FRIENDS_WITH relationship between two users.
        
        Args:
            user1_id: ID of the first user.
            user2_id: ID of the second user.
            
        Returns:
            True if successful.
        """
        query = """
        MATCH (u1:User {id: $user1_id}), (u2:User {id: $user2_id})
        MERGE (u1)-[r:FRIENDS_WITH]->(u2)
        SET r.created_at = datetime()
        """
        self._run_query(query, {"user1_id": user1_id, "user2_id": user2_id})
        return True

    # --- Query Operations ---

    def get_user_posts(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        Get all posts by a user.
        
        Args:
            user_id: User ID.
            limit: Maximum number of posts to return.
            
        Returns:
            List of post dictionaries.
        """
        query = """
        MATCH (u:User {id: $user_id})-[:POSTED_BY]->(p:Post)
        RETURN p
        ORDER BY p.timestamp DESC
        LIMIT $limit
        """
        results = self._run_query(query, {"user_id": user_id, "limit": limit})
        return [result.get("p") for result in results]

    def get_posts_by_hashtag(self, tag: str, limit: int = 10) -> List[Dict]:
        """
        Get all posts with a specific hashtag.
        
        Args:
            tag: Hashtag text.
            limit: Maximum number of posts to return.
            
        Returns:
            List of post dictionaries.
        """
        query = """
        MATCH (p:Post)-[:TAGGED_WITH]->(h:Hashtag {tag: $tag})
        RETURN p
        ORDER BY p.timestamp DESC
        LIMIT $limit
        """
        results = self._run_query(query, {"tag": tag, "limit": limit})
        return [result.get("p") for result in results]

    def get_posts_by_location(self, latitude: float, longitude: float, radius_km: float = 1.0) -> List[Dict]:
        """
        Get all posts near a specific location (using Neo4j's spatial functions).
        
        Note: Requires Neo4j Spatial plugin or manual distance calculation.
        
        Args:
            latitude: Center latitude.
            longitude: Center longitude.
            radius_km: Search radius in kilometers.
            
        Returns:
            List of post dictionaries.
        """
        # Simplified: Return all posts linked to locations (filtering in Python)
        query = """
        MATCH (p:Post)-[:LOCATED_AT]->(l:Location)
        RETURN p, l
        """
        results = self._run_query(query)
        filtered_results = []
        for result in results:
            post = result.get("p")
            location = result.get("l")
            if post and location:
                # Calculate distance (simplified Haversine formula)
                lat1, lon1 = location.get("latitude"), location.get("longitude")
                lat2, lon2 = latitude, longitude
                distance = self._haversine(lat1, lon1, lat2, lon2)
                if distance <= radius_km:
                    filtered_results.append(post)
        return filtered_results

    @staticmethod
    def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the distance between two points on Earth (Haversine formula).
        
        Args:
            lat1, lon1: Latitude and longitude of point 1.
            lat2, lon2: Latitude and longitude of point 2.
            
        Returns:
            Distance in kilometers.
        """
        from math import radians, sin, cos, sqrt, atan2
        
        R = 6371.0  # Earth radius in km
        
        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c


# Example usage
if __name__ == "__main__":
    neo4j = Neo4jManager(uri="bolt://localhost:7687", user="neo4j", password="password")
    if neo4j.connect():
        neo4j.create_constraints()
        neo4j.clear_database()
        
        # Add a user
        neo4j.add_user(
            user_id="vk_1",
            platform="vk",
            username="test_user",
            first_name="Test",
            last_name="User",
        )
        
        # Add a post
        neo4j.add_post(
            post_id="post_1",
            platform="vk",
            content="This is a test post #OSINT",
            timestamp="2023-10-15 12:34:56",
            author_id="vk_1",
        )
        
        # Add a hashtag
        neo4j.add_hashtag("OSINT")
        neo4j.link_post_to_hashtag("post_1", "OSINT")
        
        # Add a location
        neo4j.add_location(
            location_id="loc_1",
            latitude=37.7749,
            longitude=-122.4194,
            address="San Francisco, CA",
        )
        neo4j.link_post_to_location("post_1", "loc_1")
        
        # Query posts by user
        posts = neo4j.get_user_posts("vk_1")
        print(f"Posts by user vk_1: {posts}")
        
        neo4j.close()
