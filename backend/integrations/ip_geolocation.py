"""
IP Geolocation Service for OpenLens

Provides IP address geolocation:
- Offline MaxMind GeoIP2 lookups (preferred, when geoip2 + a database exist)
- ipinfo.io lookups (with IPINFO_TOKEN)
- ip-api.com fallback (free, 45 req/min)
- Private/reserved address short-circuit (stdlib, no network)
- ASN lookup

Never guesses: an unreachable provider yields None, not a centroid.
"""

import os
import time
import ipaddress
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

import requests

# Try to import geoip2 (offline MaxMind path)
try:
    import geoip2.database
    GEOIP2_AVAILABLE = True
except ImportError:
    GEOIP2_AVAILABLE = False
    print("geoip2 not available. Install with: pip install geoip2")


@dataclass
class IPLocation:
    """Represents a geolocated IP address."""
    ip: str
    latitude: float = 0.0
    longitude: float = 0.0
    city: str = ''
    region: str = ''
    country: str = ''
    country_code: str = ''
    postal_code: str = ''
    timezone: str = ''
    asn: str = ''
    isp: str = ''
    organization: str = ''
    is_private: bool = False
    provider: str = ''

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'ip': self.ip,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'city': self.city,
            'region': self.region,
            'country': self.country,
            'country_code': self.country_code,
            'postal_code': self.postal_code,
            'timezone': self.timezone,
            'asn': self.asn,
            'isp': self.isp,
            'organization': self.organization,
            'is_private': self.is_private,
            'provider': self.provider,
        }


class IPGeolocationService:
    """
    IP geolocation for OpenLens.

    Provider order: MaxMind database (offline) -> ipinfo.io (token) ->
    ip-api.com (free tier). Private/loopback/reserved addresses are handled
    locally without any network call.
    """

    def __init__(self, provider: str = None, api_key: str = None,
                 database_path: str = None):
        """
        Initialize the service.

        Args:
            provider: Force a provider ('maxmind', 'ipinfo', 'ip-api').
            api_key: ipinfo.io token (IPINFO_TOKEN env fallback).
            database_path: MaxMind .mmdb path (GEOIP_DATABASE_PATH fallback).
        """
        self.provider = provider
        self.api_key = api_key or os.getenv('IPINFO_TOKEN', '')
        self.database_path = database_path or os.getenv('GEOIP_DATABASE_PATH', '')
        self._reader = None
        self._rate_limit_delay = 1.5  # ip-api free tier: 45 req/min
        self._last_request_time = 0.0

        if GEOIP2_AVAILABLE and self.database_path and os.path.exists(self.database_path):
            try:
                self._reader = geoip2.database.Reader(self.database_path)
            except Exception as e:
                print(f"GeoIP database open error: {e}")

    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def is_available(self) -> bool:
        """True when at least one provider path is usable."""
        return bool(self._reader or self.api_key) or True  # ip-api needs no key

    @staticmethod
    def is_private(ip: str) -> bool:
        """True for private/loopback/reserved addresses. Never touches the network."""
        try:
            parsed = ipaddress.ip_address(ip)
        except ValueError:
            return False
        return (parsed.is_private or parsed.is_loopback or parsed.is_reserved
                or parsed.is_link_local or parsed.is_multicast)

    def locate(self, ip: str) -> Optional[IPLocation]:
        """
        Geolocate an IP address.

        Returns:
            IPLocation, an is_private-flagged stub for non-routable addresses,
            or None when every provider fails.
        """
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            return None

        if self.is_private(ip):
            return IPLocation(ip=ip, is_private=True, provider='local')

        if self._reader and self.provider in (None, 'maxmind'):
            located = self._locate_maxmind(ip)
            if located:
                return located
        if self.api_key and self.provider in (None, 'ipinfo'):
            located = self._locate_ipinfo(ip)
            if located:
                return located
        if self.provider in (None, 'ip-api'):
            return self._locate_ip_api(ip)
        return None

    def _locate_maxmind(self, ip: str) -> Optional[IPLocation]:
        """Offline MaxMind lookup."""
        try:
            record = self._reader.city(ip)
            return IPLocation(
                ip=ip,
                latitude=float(record.location.latitude or 0),
                longitude=float(record.location.longitude or 0),
                city=record.city.name or '',
                region=(record.subdivisions.most_specific.name or ''
                        if record.subdivisions else ''),
                country=record.country.name or '',
                country_code=record.country.iso_code or '',
                postal_code=record.postal.code or '',
                timezone=record.location.time_zone or '',
                provider='maxmind',
            )
        except Exception:
            return None

    def _locate_ipinfo(self, ip: str) -> Optional[IPLocation]:
        """ipinfo.io lookup."""
        try:
            response = requests.get(
                f'https://ipinfo.io/{ip}/json',
                params={'token': self.api_key}, timeout=10)
            response.raise_for_status()
            data = response.json()
            lat, lon = 0.0, 0.0
            if data.get('loc'):
                parts = data['loc'].split(',')
                lat, lon = float(parts[0]), float(parts[1])
            return IPLocation(
                ip=ip, latitude=lat, longitude=lon,
                city=data.get('city', ''), region=data.get('region', ''),
                country_code=data.get('country', ''),
                postal_code=data.get('postal', ''),
                timezone=data.get('timezone', ''),
                organization=data.get('org', ''),
                provider='ipinfo',
            )
        except Exception as e:
            print(f"ipinfo lookup error: {e}")
            return None

    def _locate_ip_api(self, ip: str) -> Optional[IPLocation]:
        """ip-api.com lookup (free tier, rate-limited)."""
        self._check_rate_limit()
        try:
            response = requests.get(
                f'http://ip-api.com/json/{ip}',
                params={'fields': 'status,message,lat,lon,city,regionName,'
                                  'country,countryCode,zip,timezone,as,isp,org'},
                timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('status') != 'success':
                return None
            return IPLocation(
                ip=ip,
                latitude=float(data.get('lat', 0) or 0),
                longitude=float(data.get('lon', 0) or 0),
                city=data.get('city', ''), region=data.get('regionName', ''),
                country=data.get('country', ''),
                country_code=data.get('countryCode', ''),
                postal_code=data.get('zip', ''),
                timezone=data.get('timezone', ''),
                asn=data.get('as', ''), isp=data.get('isp', ''),
                organization=data.get('org', ''),
                provider='ip-api',
            )
        except Exception as e:
            print(f"ip-api lookup error: {e}")
            return None

    def locate_batch(self, ips: List[str]) -> List[Optional[IPLocation]]:
        """Geolocate a list of IPs (rate limits apply per lookup)."""
        return [self.locate(ip) for ip in ips]

    def get_asn(self, ip: str) -> Optional[Dict[str, Any]]:
        """ASN/ISP information for an IP."""
        located = self.locate(ip)
        if not located or located.is_private:
            return None
        return {'ip': ip, 'asn': located.asn, 'isp': located.isp,
                'organization': located.organization}


# Global IP geolocation service instance
ip_geolocation_service = IPGeolocationService()
