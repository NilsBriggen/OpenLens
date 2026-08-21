"""
Google Maps API Integration for OpenLens

Provides:
- Geocoding (address to coordinates)
- Reverse geocoding (coordinates to address)
- Distance matrix
- Directions
- Places search
- Static maps

Dependencies:
- googlemaps: Google Maps API client
"""

import os
import json
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from functools import lru_cache
import time

# Try to import the Google Maps client
try:
    import googlemaps
    from googlemaps import Client, directions, distance_matrix, geocoding, places
    GOOGLE_MAPS_AVAILABLE = True
except ImportError:
    GOOGLE_MAPS_AVAILABLE = False
    print("Google Maps client not available. Install with: pip install googlemaps")


@dataclass
class Location:
    """Represents a geographic location."""
    latitude: float
    longitude: float
    address: str = ""
    city: str = ""
    region: str = ""
    country: str = ""
    country_code: str = ""
    postal_code: str = ""
    formatted_address: str = ""
    place_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'city': self.city,
            'region': self.region,
            'country': self.country,
            'country_code': self.country_code,
            'postal_code': self.postal_code,
            'formatted_address': self.formatted_address,
            'place_id': self.place_id,
        }


@dataclass
class DistanceResult:
    """Represents a distance calculation result."""
    origin: str
    destination: str
    distance: float  # in meters
    duration: float  # in seconds
    distance_text: str
    duration_text: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'origin': self.origin,
            'destination': self.destination,
            'distance': self.distance,
            'duration': self.duration,
            'distance_text': self.distance_text,
            'duration_text': self.duration_text,
        }


@dataclass
class DirectionsResult:
    """Represents route directions."""
    origin: str
    destination: str
    distance: float
    duration: float
    steps: List[Dict[str, Any]]
    polyline: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'origin': self.origin,
            'destination': self.destination,
            'distance': self.distance,
            'duration': self.duration,
            'steps': self.steps,
            'polyline': self.polyline,
        }


@dataclass
class Place:
    """Represents a place from Google Places API."""
    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    rating: float = 0.0
    types: List[str] = field(default_factory=list)
    opening_hours: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'place_id': self.place_id,
            'name': self.name,
            'address': self.address,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'rating': self.rating,
            'types': self.types,
            'opening_hours': self.opening_hours,
        }


class GoogleMapsService:
    """
    Provides integration with Google Maps API.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize the Google Maps service.
        
        Args:
            api_key: Google Maps API key.
        """
        self.api_key = api_key or os.getenv('GOOGLE_MAPS_API_KEY')
        self.client = None
        self._rate_limit_delay = 0.1  # 100ms between requests to avoid rate limiting
        self._last_request_time = 0
        
        if self.api_key and GOOGLE_MAPS_AVAILABLE:
            self.client = Client(key=self.api_key)
    
    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    def geocode(self, address: str, region: str = None) -> Optional[Location]:
        """
        Convert an address to geographic coordinates.
        
        Args:
            address: Address to geocode.
            region: Optional region bias (country code).
            
        Returns:
            Location object or None if failed.
        """
        if not self.client:
            return None
        
        self._check_rate_limit()
        
        try:
            result = self.client.geocode(address, region=region)
            
            if not result:
                return None
            
            location = result[0]['geometry']['location']
            address_components = result[0].get('address_components', [])
            
            # Extract address components
            city = ""
            region = ""
            country = ""
            country_code = ""
            postal_code = ""
            
            for component in address_components:
                types = component.get('types', [])
                if 'locality' in types:
                    city = component.get('long_name', '')
                elif 'administrative_area_level_1' in types:
                    region = component.get('long_name', '')
                elif 'country' in types:
                    country = component.get('long_name', '')
                    country_code = component.get('short_name', '')
                elif 'postal_code' in types:
                    postal_code = component.get('long_name', '')
            
            return Location(
                latitude=location['lat'],
                longitude=location['lng'],
                address=address,
                city=city,
                region=region,
                country=country,
                country_code=country_code,
                postal_code=postal_code,
                formatted_address=result[0].get('formatted_address', ''),
                place_id=result[0].get('place_id', ''),
            )
        
        except Exception as e:
            print(f"Geocoding error: {e}")
            return None
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Location]:
        """
        Convert coordinates to an address.
        
        Args:
            latitude: Latitude.
            longitude: Longitude.
            
        Returns:
            Location object or None if failed.
        """
        if not self.client:
            return None
        
        self._check_rate_limit()
        
        try:
            result = self.client.reverse_geocode((latitude, longitude))
            
            if not result:
                return None
            
            location = result[0]['geometry']['location']
            address_components = result[0].get('address_components', [])
            
            # Extract address components
            address = result[0].get('formatted_address', '')
            city = ""
            region = ""
            country = ""
            country_code = ""
            postal_code = ""
            
            for component in address_components:
                types = component.get('types', [])
                if 'locality' in types:
                    city = component.get('long_name', '')
                elif 'administrative_area_level_1' in types:
                    region = component.get('long_name', '')
                elif 'country' in types:
                    country = component.get('long_name', '')
                    country_code = component.get('short_name', '')
                elif 'postal_code' in types:
                    postal_code = component.get('long_name', '')
            
            return Location(
                latitude=latitude,
                longitude=longitude,
                address=address,
                city=city,
                region=region,
                country=country,
                country_code=country_code,
                postal_code=postal_code,
                formatted_address=address,
                place_id=result[0].get('place_id', ''),
            )
        
        except Exception as e:
            print(f"Reverse geocoding error: {e}")
            return None
    
    def batch_geocode(self, addresses: List[str]) -> List[Optional[Location]]:
        """
        Geocode multiple addresses.
        
        Args:
            addresses: List of addresses to geocode.
            
        Returns:
            List of Location objects (or None for failed geocodes).
        """
        return [self.geocode(addr) for addr in addresses]
    
    def get_distance(self, origin: str, destination: str, 
                     mode: str = 'driving') -> Optional[DistanceResult]:
        """
        Get distance and duration between two points.
        
        Args:
            origin: Origin address or coordinates.
            destination: Destination address or coordinates.
            mode: Travel mode ('driving', 'walking', 'bicycling', 'transit').
            
        Returns:
            DistanceResult object or None if failed.
        """
        if not self.client:
            return None
        
        self._check_rate_limit()
        
        try:
            result = self.client.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode=mode,
            )
            
            if not result or 'rows' not in result:
                return None
            
            row = result['rows'][0]
            element = row['elements'][0]
            
            if element.get('status') != 'OK':
                return None
            
            return DistanceResult(
                origin=origin,
                destination=destination,
                distance=element['distance']['value'],
                duration=element['duration']['value'],
                distance_text=element['distance']['text'],
                duration_text=element['duration']['text'],
            )
        
        except Exception as e:
            print(f"Distance matrix error: {e}")
            return None
    
    def get_directions(self, origin: str, destination: str, 
                       mode: str = 'driving', alternatives: bool = False) -> Optional[DirectionsResult]:
        """
        Get route directions between two points.
        
        Args:
            origin: Origin address or coordinates.
            destination: Destination address or coordinates.
            mode: Travel mode ('driving', 'walking', 'bicycling', 'transit').
            alternatives: Whether to include alternative routes.
            
        Returns:
            DirectionsResult object or None if failed.
        """
        if not self.client:
            return None
        
        self._check_rate_limit()
        
        try:
            result = self.client.directions(
                origin=origin,
                destination=destination,
                mode=mode,
                alternatives=alternatives,
            )
            
            if not result or 'routes' not in result:
                return None
            
            route = result['routes'][0]
            legs = route['legs']
            
            # Calculate total distance and duration
            total_distance = sum(leg['distance']['value'] for leg in legs)
            total_duration = sum(leg['duration']['value'] for leg in legs)
            
            # Extract steps
            steps = []
            for leg in legs:
                for step in leg['steps']:
                    steps.append({
                        'distance': step['distance']['value'],
                        'duration': step['duration']['value'],
                        'instructions': step['html_instructions'],
                        'start_location': step['start_location'],
                        'end_location': step['end_location'],
                        'polyline': step['polyline']['points'],
                    })
            
            # Get overview polyline
            polyline = route.get('overview_polyline', {}).get('points', '')
            
            return DirectionsResult(
                origin=origin,
                destination=destination,
                distance=total_distance,
                duration=total_duration,
                steps=steps,
                polyline=polyline,
            )
        
        except Exception as e:
            print(f"Directions error: {e}")
            return None
    
    def search_places(self, query: str, location: Tuple[float, float] = None, 
                      radius: int = 5000, types: List[str] = None) -> List[Place]:
        """
        Search for places.
        
        Args:
            query: Search query.
            location: Optional center point (latitude, longitude).
            radius: Search radius in meters.
            types: Optional list of place types to filter by.
            
        Returns:
            List of Place objects.
        """
        if not self.client:
            return []
        
        self._check_rate_limit()
        
        try:
            kwargs = {
                'query': query,
            }
            
            if location:
                kwargs['location'] = location
                kwargs['radius'] = radius
            
            if types:
                kwargs['type'] = types[0]  # Google Places only accepts one type
            
            result = self.client.places(**kwargs)
            
            places = []
            for place_result in result.get('results', []):
                location = place_result['geometry']['location']
                
                place = Place(
                    place_id=place_result.get('place_id', ''),
                    name=place_result.get('name', ''),
                    address=place_result.get('vicinity', ''),
                    latitude=location['lat'],
                    longitude=location['lng'],
                    rating=place_result.get('rating', 0.0),
                    types=place_result.get('types', []),
                    opening_hours=place_result.get('opening_hours', {}),
                )
                places.append(place)
            
            return places
        
        except Exception as e:
            print(f"Places search error: {e}")
            return []
    
    def get_place_details(self, place_id: str) -> Optional[Place]:
        """
        Get details for a specific place.
        
        Args:
            place_id: Place ID.
            
        Returns:
            Place object or None if failed.
        """
        if not self.client:
            return None
        
        self._check_rate_limit()
        
        try:
            result = self.client.place(place_id=place_id)
            
            if not result or 'result' not in result:
                return None
            
            place_result = result['result']
            location = place_result['geometry']['location']
            
            return Place(
                place_id=place_result.get('place_id', ''),
                name=place_result.get('name', ''),
                address=place_result.get('vicinity', ''),
                latitude=location['lat'],
                longitude=location['lng'],
                rating=place_result.get('rating', 0.0),
                types=place_result.get('types', []),
                opening_hours=place_result.get('opening_hours', {}),
            )
        
        except Exception as e:
            print(f"Place details error: {e}")
            return None
    
    def get_static_map(self, center: Tuple[float, float], zoom: int = 12, 
                       size: Tuple[int, int] = (640, 640), 
                       markers: List[Dict] = None, path: List[Tuple[float, float]] = None) -> Optional[str]:
        """
        Get a static map image URL.
        
        Args:
            center: Center coordinates (latitude, longitude).
            zoom: Zoom level.
            size: Image size (width, height).
            markers: Optional list of marker dictionaries.
            path: Optional list of coordinates for a path.
            
        Returns:
            URL to the static map image or None if failed.
        """
        if not self.api_key:
            return None
        
        # Build the static map URL
        base_url = "https://maps.googleapis.com/maps/api/staticmap"
        
        params = {
            'center': f"{center[0]},{center[1]}",
            'zoom': zoom,
            'size': f"{size[0]}x{size[1]}",
            'key': self.api_key,
        }
        
        # Add markers
        if markers:
            marker_strings = []
            for marker in markers:
                lat = marker.get('lat', 0)
                lon = marker.get('lon', 0)
                color = marker.get('color', 'red')
                label = marker.get('label', '')
                size = marker.get('size', 'mid')
                
                marker_str = f"{lat},{lon}"
                if color:
                    marker_str += f"|color:0x{color[1:]}" if color.startswith('#') else f"|color:{color}"
                if label:
                    marker_str += f"|label:{label}"
                if size:
                    marker_str += f"|size:{size}"
                
                marker_strings.append(marker_str)
            
            if marker_strings:
                params['markers'] = '|'.join(marker_strings)
        
        # Add path
        if path and len(path) > 1:
            path_str = '|'.join([f"{lat},{lon}" for lat, lon in path])
            params['path'] = f"color:0x0000FF|weight:5|{path_str}"
        
        # Build URL
        import urllib.parse
        url = base_url + "?" + urllib.parse.urlencode(params)
        
        return url
    
    def get_elevation(self, locations: List[Tuple[float, float]]) -> List[Dict[str, Any]]:
        """
        Get elevation data for multiple locations.
        
        Args:
            locations: List of (latitude, longitude) tuples.
            
        Returns:
            List of elevation data dictionaries.
        """
        if not self.client:
            return []
        
        self._check_rate_limit()
        
        try:
            result = self.client.elevation(locations)
            
            elevations = []
            for location_result in result.get('results', []):
                elevations.append({
                    'location': location_result['location'],
                    'elevation': location_result['elevation'],
                    'resolution': location_result.get('resolution', 0),
                })
            
            return elevations
        
        except Exception as e:
            print(f"Elevation error: {e}")
            return []
    
    def get_timezone(self, location: Tuple[float, float], 
                     timestamp: datetime = None) -> Optional[Dict[str, Any]]:
        """
        Get timezone information for a location.
        
        Args:
            location: Coordinates (latitude, longitude).
            timestamp: Optional timestamp (defaults to now).
            
        Returns:
            Dictionary with timezone information or None if failed.
        """
        if not self.client:
            return None
        
        self._check_rate_limit()
        
        try:
            if timestamp is None:
                timestamp = datetime.utcnow()
            
            result = self.client.timezone(location, timestamp)
            
            if not result:
                return None
            
            return {
                'timezone_id': result.get('timeZoneId', ''),
                'timezone_name': result.get('timeZoneName', ''),
                'offset': result.get('rawOffset', 0),
                'dst_offset': result.get('dstOffset', 0),
            }
        
        except Exception as e:
            print(f"Timezone error: {e}")
            return None


# Global Google Maps service instance
google_maps_service = GoogleMapsService()
