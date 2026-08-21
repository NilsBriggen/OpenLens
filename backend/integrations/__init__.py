"""
Integrations Module for OpenLens

Provides integration with external services:
- Google Maps API
- Twitter API
- VK API
- Instagram API
- Telegram API
- Other third-party services
"""

from .google_maps import GoogleMapsService, google_maps_service
from .twitter_api import TwitterAPIService, twitter_api_service
from .vk_api import VKAPIService, vk_api_service
from .geocoding import GeocodingService, geocoding_service
from .ip_geolocation import IPGeolocationService, ip_geolocation_service

__all__ = [
    'GoogleMapsService',
    'google_maps_service',
    'TwitterAPIService',
    'twitter_api_service',
    'VKAPIService',
    'vk_api_service',
    'GeocodingService',
    'geocoding_service',
    'IPGeolocationService',
    'ip_geolocation_service',
]
