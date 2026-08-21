"""
Data Processor for OpenLens

Provides utilities for processing and transforming data for visualizations:
- Timeline data (for D3.js timeline charts)
- Heatmap data (for Leaflet heat layers)
- Graph data (for network visualizations)
- Normalization (cleaning, deduplication, validation)

Dependencies:
- pandas: For data manipulation
- numpy: For numerical operations
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict
import json


@dataclass
class TimelineEvent:
    """Represents an event for timeline visualization."""
    id: str
    title: str
    start: datetime
    end: Optional[datetime] = None
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


@dataclass
class HeatmapPoint:
    """Represents a point for heatmap visualization."""
    latitude: float
    longitude: float
    intensity: float = 1.0
    radius: int = 25
    color: Optional[str] = None


@dataclass
class GraphNode:
    """Represents a node for graph visualization."""
    id: str
    name: str
    type: str  # e.g., "user", "post", "location", "hashtag"
    group: int = 0
    size: int = 10
    color: Optional[str] = None


@dataclass
class GraphLink:
    """Represents a link between nodes for graph visualization."""
    source: str
    target: str
    type: str  # e.g., "POSTED_BY", "MENTIONS", "TAGGED_WITH"
    value: int = 1
    color: Optional[str] = None


class DataProcessor:
    """
    Processes raw data into formats suitable for visualization.
    """

    def __init__(self):
        """Initialize the data processor."""
        pass

    # --- Timeline Processing ---

    def create_timeline_from_posts(
        self,
        posts: List[Dict[str, Any]],
        title_field: str = "content",
        date_field: str = "timestamp",
    ) -> List[TimelineEvent]:
        """
        Convert a list of posts into timeline events.
        
        Args:
            posts: List of post dictionaries.
            title_field: Field name for the event title.
            date_field: Field name for the event date.
            
        Returns:
            List of TimelineEvent objects.
        """
        events = []
        for i, post in enumerate(posts):
            try:
                # Parse timestamp
                timestamp = post.get(date_field)
                if isinstance(timestamp, str):
                    start = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                else:
                    start = timestamp
                
                # Extract title (truncate if too long)
                title = str(post.get(title_field, f"Event {i}"))[:50]
                
                events.append(TimelineEvent(
                    id=str(i),
                    title=title,
                    start=start,
                    description=str(post.get("content", ""))[:200] if post.get("content") else None,
                    category=post.get("category"),
                ))
            except Exception as e:
                print(f"Failed to process post {i}: {e}")
                continue
        
        return events

    def create_timeline_from_tweets(
        self,
        tweets: List[Dict[str, Any]],
    ) -> List[TimelineEvent]:
        """
        Convert a list of tweets into timeline events.
        
        Args:
            tweets: List of tweet dictionaries.
            
        Returns:
            List of TimelineEvent objects.
        """
        events = []
        for i, tweet in enumerate(tweets):
            try:
                timestamp = tweet.get("timestamp")
                if isinstance(timestamp, str):
                    start = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                else:
                    start = timestamp
                
                title = f"@{tweet.get('username', 'unknown')}: {tweet.get('content', '')[:30]}..."
                
                events.append(TimelineEvent(
                    id=tweet.get("id", str(i)),
                    title=title,
                    start=start,
                    description=tweet.get("content"),
                    category="Tweet",
                    icon="🐦",
                ))
            except Exception as e:
                print(f"Failed to process tweet {i}: {e}")
                continue
        
        return events

    # --- Heatmap Processing ---

    def create_heatmap_from_posts(
        self,
        posts: List[Dict[str, Any]],
        latitude_field: str = "latitude",
        longitude_field: str = "longitude",
        intensity_field: Optional[str] = None,
    ) -> List[HeatmapPoint]:
        """
        Convert a list of posts with geotags into heatmap points.
        
        Args:
            posts: List of post dictionaries.
            latitude_field: Field name for latitude.
            longitude_field: Field name for longitude.
            intensity_field: Optional field name for intensity (default: 1.0).
            
        Returns:
            List of HeatmapPoint objects.
        """
        points = []
        for i, post in enumerate(posts):
            try:
                # Extract geotag
                geotag = post.get("geotag")
                if geotag:
                    latitude = geotag.get(latitude_field)
                    longitude = geotag.get(longitude_field)
                    if latitude is not None and longitude is not None:
                        intensity = post.get(intensity_field, 1.0) if intensity_field else 1.0
                        points.append(HeatmapPoint(
                            latitude=float(latitude),
                            longitude=float(longitude),
                            intensity=float(intensity),
                        ))
                
                # Also check for direct latitude/longitude fields
                elif latitude_field in post and longitude_field in post:
                    latitude = post.get(latitude_field)
                    longitude = post.get(longitude_field)
                    if latitude is not None and longitude is not None:
                        intensity = post.get(intensity_field, 1.0) if intensity_field else 1.0
                        points.append(HeatmapPoint(
                            latitude=float(latitude),
                            longitude=float(longitude),
                            intensity=float(intensity),
                        ))
            except Exception as e:
                print(f"Failed to process post {i}: {e}")
                continue
        
        return points

    def create_heatmap_from_locations(
        self,
        locations: List[Dict[str, Any]],
        weight_field: Optional[str] = None,
    ) -> List[HeatmapPoint]:
        """
        Convert a list of locations into heatmap points.
        
        Args:
            locations: List of location dictionaries.
            weight_field: Optional field name for weight (default: 1.0).
            
        Returns:
            List of HeatmapPoint objects.
        """
        points = []
        for i, loc in enumerate(locations):
            try:
                latitude = loc.get("latitude")
                longitude = loc.get("longitude")
                if latitude is not None and longitude is not None:
                    weight = loc.get(weight_field, 1.0) if weight_field else 1.0
                    points.append(HeatmapPoint(
                        latitude=float(latitude),
                        longitude=float(longitude),
                        intensity=float(weight),
                    ))
            except Exception as e:
                print(f"Failed to process location {i}: {e}")
                continue
        
        return points

    # --- Graph Processing ---

    def create_graph_from_posts_and_users(
        self,
        posts: List[Dict[str, Any]],
        users: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[List[GraphNode], List[GraphLink]]:
        """
        Create a graph from posts and users (for network visualization).
        
        Args:
            posts: List of post dictionaries.
            users: Optional list of user dictionaries.
            
        Returns:
            Tuple of (nodes, links).
        """
        nodes = []
        links = []
        
        # Track unique nodes
        node_ids = set()
        
        # Add user nodes
        user_map = {}
        if users:
            for user in users:
                user_id = user.get("id", user.get("username", ""))
                if user_id not in node_ids:
                    node_ids.add(user_id)
                    nodes.append(GraphNode(
                        id=user_id,
                        name=user.get("username", user.get("name", "Unknown")),
                        type="user",
                        group=1,
                        size=20,
                        color="#4CAF50",
                    ))
                    user_map[user_id] = len(nodes) - 1
        
        # Add post nodes and links
        for post in posts:
            post_id = post.get("id", str(hash(post.get("content", ""))))
            if post_id not in node_ids:
                node_ids.add(post_id)
                nodes.append(GraphNode(
                    id=post_id,
                    name=post.get("content", "Post")[:30] + "...",
                    type="post",
                    group=2,
                    size=15,
                    color="#2196F3",
                ))
            
            # Link post to author
            author_id = post.get("user_id", post.get("username", ""))
            if author_id:
                links.append(GraphLink(
                    source=author_id,
                    target=post_id,
                    type="POSTED_BY",
                    value=1,
                    color="#999",
                ))
            
            # Link post to hashtags
            hashtags = post.get("hashtags", [])
            for hashtag in hashtags:
                hashtag_id = f"hashtag_{hashtag}"
                if hashtag_id not in node_ids:
                    node_ids.add(hashtag_id)
                    nodes.append(GraphNode(
                        id=hashtag_id,
                        name=f"#{hashtag}",
                        type="hashtag",
                        group=3,
                        size=10,
                        color="#FF9800",
                    ))
                links.append(GraphLink(
                    source=post_id,
                    target=hashtag_id,
                    type="TAGGED_WITH",
                    value=1,
                    color="#999",
                ))
            
            # Link post to mentions
            mentions = post.get("mentions", [])
            for mention in mentions:
                mention_id = f"user_{mention}"
                if mention_id not in node_ids:
                    node_ids.add(mention_id)
                    nodes.append(GraphNode(
                        id=mention_id,
                        name=mention,
                        type="user",
                        group=1,
                        size=15,
                        color="#4CAF50",
                    ))
                links.append(GraphLink(
                    source=post_id,
                    target=mention_id,
                    type="MENTIONS",
                    value=1,
                    color="#999",
                ))
        
        return nodes, links

    # --- Data Normalization ---

    def normalize_text(self, text: str) -> str:
        """
        Normalize text (lowercase, remove extra spaces, etc.).
        
        Args:
            text: Input text.
            
        Returns:
            Normalized text.
        """
        if not text:
            return ""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Convert to lowercase
        text = text.lower()
        # Remove special characters (optional)
        # text = re.sub(r'[^\w\s]', '', text)
        return text

    def normalize_phone(self, phone: str) -> Optional[str]:
        """
        Normalize phone number (remove non-digits, add country code if missing).
        
        Args:
            phone: Input phone number.
            
        Returns:
            Normalized phone number or None if invalid.
        """
        if not phone:
            return None
        # Remove all non-digit characters
        digits = re.sub(r'[^\d]', '', phone)
        if not digits:
            return None
        # Add country code if missing (assume +1 for US/Canada, +7 for Russia, etc.)
        if len(digits) == 10:
            # Assume US number
            digits = f"+1{digits}"
        elif len(digits) == 11 and digits.startswith("8"):
            # Convert Russian 8 to +7
            digits = f"+7{digits[1:]}"
        elif len(digits) < 10:
            return None
        return digits

    def normalize_email(self, email: str) -> Optional[str]:
        """
        Normalize email address (lowercase, remove spaces).
        
        Args:
            email: Input email address.
            
        Returns:
            Normalized email or None if invalid.
        """
        if not email:
            return None
        # Remove spaces and convert to lowercase
        email = email.replace(" ", "").lower()
        # Basic validation
        if "@" not in email or "." not in email:
            return None
        return email

    def normalize_url(self, url: str) -> Optional[str]:
        """
        Normalize URL (remove trailing slash, lowercase, etc.).
        
        Args:
            url: Input URL.
            
        Returns:
            Normalized URL or None if invalid.
        """
        if not url:
            return None
        # Remove trailing slash
        url = url.rstrip("/")
        # Convert to lowercase
        url = url.lower()
        # Ensure it starts with http:// or https://
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        return url

    def deduplicate_list(self, items: List[Any]) -> List[Any]:
        """
        Remove duplicates from a list while preserving order.
        
        Args:
            items: Input list.
            
        Returns:
            Deduplicated list.
        """
        seen = set()
        deduplicated = []
        for item in items:
            # Use JSON serialization for hashable comparison
            key = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else item
            if key not in seen:
                seen.add(key)
                deduplicated.append(item)
        return deduplicated

    def validate_entity(self, entity: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate that an entity has all required fields.
        
        Args:
            entity: Entity dictionary.
            required_fields: List of required field names.
            
        Returns:
            True if valid, False otherwise.
        """
        for field in required_fields:
            if field not in entity or not entity[field]:
                return False
        return True

    # --- Data Aggregation ---

    def aggregate_by_date(
        self,
        items: List[Dict[str, Any]],
        date_field: str = "timestamp",
        group_field: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Aggregate items by date (e.g., count posts per day).
        
        Args:
            items: List of item dictionaries.
            date_field: Field name for the date.
            group_field: Optional field name to group by (e.g., "category").
            
        Returns:
            Dictionary with aggregated data.
        """
        aggregated = defaultdict(lambda: defaultdict(int))
        
        for item in items:
            try:
                # Extract date
                date_value = item.get(date_field)
                if isinstance(date_value, str):
                    date = datetime.fromisoformat(date_value.replace("Z", "+00:00")).date()
                else:
                    date = date_value.date() if hasattr(date_value, 'date') else date_value
                
                date_str = str(date)
                
                if group_field:
                    group = item.get(group_field, "default")
                    aggregated[date_str][group] += 1
                else:
                    aggregated[date_str]["count"] += 1
            except Exception as e:
                print(f"Failed to aggregate item: {e}")
                continue
        
        return dict(aggregated)

    def aggregate_by_location(
        self,
        items: List[Dict[str, Any]],
        latitude_field: str = "latitude",
        longitude_field: str = "longitude",
        precision: int = 4,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Aggregate items by location (rounded coordinates).
        
        Args:
            items: List of item dictionaries.
            latitude_field: Field name for latitude.
            longitude_field: Field name for longitude.
            precision: Number of decimal places for rounding.
            
        Returns:
            Dictionary with aggregated data by location.
        """
        aggregated = defaultdict(lambda: {"count": 0, "latitude": 0.0, "longitude": 0.0})
        
        for item in items:
            try:
                # Extract geotag
                geotag = item.get("geotag")
                if geotag:
                    latitude = geotag.get(latitude_field)
                    longitude = geotag.get(longitude_field)
                else:
                    latitude = item.get(latitude_field)
                    longitude = item.get(longitude_field)
                
                if latitude is not None and longitude is not None:
                    # Round coordinates to specified precision
                    lat_rounded = round(float(latitude), precision)
                    lon_rounded = round(float(longitude), precision)
                    location_key = f"{lat_rounded},{lon_rounded}"
                    
                    aggregated[location_key]["count"] += 1
                    aggregated[location_key]["latitude"] = lat_rounded
                    aggregated[location_key]["longitude"] = lon_rounded
            except Exception as e:
                print(f"Failed to aggregate location: {e}")
                continue
        
        return dict(aggregated)


# Singleton instance for easy use
data_processor = DataProcessor()
