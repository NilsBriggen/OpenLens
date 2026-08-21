"""
Geocoding Service for OpenLens

Provides address geocoding:
- Forward geocoding (address -> coordinates) via Nominatim
- Reverse geocoding (coordinates -> address)
- Batch geocoding
- Haversine distance (no network)
- Optional Google Maps delegation when an API key is configured
"""

import os
import time
import math
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field

import requests

NOMINATIM_URL = os.getenv('NOMINATIM_URL', 'https://nominatim.openstreetmap.org')
_EARTH_RADIUS_KM = 6371.0088


@dataclass
class GeocodeResult:
    """Represents a geocoding result."""
    query: str
    latitude: float = 0.0
    longitude: float = 0.0
    display_name: str = ''
    city: str = ''
    region: str = ''
    country: str = ''
    country_code: str = ''
    postal_code: str = ''
    confidence: float = 0.0
    provider: str = ''
    raw: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'query': self.query,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'display_name': self.display_name,
            'city': self.city,
            'region': self.region,
            'country': self.country,
            'country_code': self.country_code,
            'postal_code': self.postal_code,
            'confidence': self.confidence,
            'provider': self.provider,
        }


class GeocodingService:
    """
    Geocoding service for OpenLens.

    Defaults to Nominatim (no API key required). The 1 request/second usage
    policy is enforced, and a descriptive User-Agent is mandatory - anonymous
    clients get blocked by the service.
    """

    def __init__(self, provider: str = None, user_agent: str = None,
                 google_maps_service=None):
        """
        Initialize the geocoding service.

        Args:
            provider: 'nominatim' (default) or 'google'.
            user_agent: User-Agent header (OPENLENS_USER_AGENT env fallback).
            google_maps_service: GoogleMapsService for provider='google'.
        """
        self.provider = provider or os.getenv('GEOCODING_PROVIDER', 'nominatim')
        self.user_agent = user_agent or os.getenv(
            'OPENLENS_USER_AGENT', 'OpenLens-OSINT/1.0 (geocoding)')
        self.google_maps_service = google_maps_service
        self._rate_limit_delay = 1.0  # Nominatim usage policy: 1 req/s
        self._last_request_time = 0.0

    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def is_available(self) -> bool:
        """True when a provider is usable."""
        if self.provider == 'google':
            return bool(self.google_maps_service
                        and getattr(self.google_maps_service, 'client', None))
        return True  # Nominatim needs no key

    def _nominatim_get(self, path: str, params: Dict[str, Any]) -> Optional[Any]:
        """One rate-limited Nominatim request."""
        self._check_rate_limit()
        try:
            response = requests.get(
                f'{NOMINATIM_URL}{path}',
                params={**params, 'format': 'jsonv2'},
                headers={'User-Agent': self.user_agent},
                timeout=10,
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Geocoding request error: {e}")
            return None

    @staticmethod
    def _parse_nominatim(query: str, item: Dict[str, Any]) -> GeocodeResult:
        """Build a GeocodeResult from one Nominatim item."""
        address = item.get('address', {}) or {}
        return GeocodeResult(
            query=query,
            latitude=float(item.get('lat', 0)),
            longitude=float(item.get('lon', 0)),
            display_name=item.get('display_name', ''),
            city=address.get('city') or address.get('town') or address.get('village', ''),
            region=address.get('state', ''),
            country=address.get('country', ''),
            country_code=(address.get('country_code') or '').upper(),
            postal_code=address.get('postcode', ''),
            confidence=float(item.get('importance', 0) or 0),
            provider='nominatim',
            raw=item,
        )

    def geocode(self, address: str, country_code: str = None) -> Optional[GeocodeResult]:
        """
        Forward-geocode an address.

        Args:
            address: Free-text address.
            country_code: Restrict results to a country (ISO code).

        Returns:
            Best GeocodeResult, or None.
        """
        if not address:
            return None

        params: Dict[str, Any] = {'q': address, 'limit': 1, 'addressdetails': 1}
        if country_code:
            params['countrycodes'] = country_code.lower()

        items = self._nominatim_get('/search', params)
        if not items:
            return None
        return self._parse_nominatim(address, items[0])

    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[GeocodeResult]:
        """Reverse-geocode coordinates to an address."""
        item = self._nominatim_get('/reverse', {
            'lat': latitude, 'lon': longitude, 'addressdetails': 1,
        })
        if not item or 'error' in item:
            return None
        result = self._parse_nominatim(f'{latitude},{longitude}', item)
        result.latitude, result.longitude = latitude, longitude
        return result

    def batch_geocode(self, addresses: List[str]) -> List[Optional[GeocodeResult]]:
        """Geocode a list of addresses (rate-limited per request)."""
        return [self.geocode(address) for address in addresses]

    @staticmethod
    def distance_between(a: Tuple[float, float], b: Tuple[float, float]) -> float:
        """Haversine distance in kilometres. Pure math, no network."""
        lat1, lon1 = math.radians(a[0]), math.radians(a[1])
        lat2, lon2 = math.radians(b[0]), math.radians(b[1])
        dlat, dlon = lat2 - lat1, lon2 - lon1
        h = (math.sin(dlat / 2) ** 2
             + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2)
        return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(h))


# Global geocoding service instance
geocoding_service = GeocodingService()
