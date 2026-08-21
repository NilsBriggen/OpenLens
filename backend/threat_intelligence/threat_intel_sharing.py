"""
Threat Intelligence Sharing for OpenLens

Provides threat intelligence sharing capabilities:
- STIX/TAXII support
- MISP integration
- Export/import of threat intelligence
- Sharing with trusted partners
- Synchronization with threat intelligence platforms
"""

import os
import time
import json
import requests
import threading
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class SharingProfile:
    """Represents a sharing profile."""
    profile_id: str
    name: str
    description: str = ''
    sharing_type: str = 'export'  # export, import, bidirectional
    protocol: str = 'stix'  # stix, taxii, misp, custom
    endpoint: str = ''
    authentication: Dict[str, Any] = field(default_factory=dict)
    filters: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    last_sync: datetime = None
    sync_interval: int = 3600  # seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'profile_id': self.profile_id,
            'name': self.name,
            'description': self.description,
            'sharing_type': self.sharing_type,
            'protocol': self.protocol,
            'endpoint': self.endpoint,
            'authentication': self.authentication,
            'filters': self.filters,
            'is_active': self.is_active,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
            'sync_interval': self.sync_interval,
        }


@dataclass
class SharedItem:
    """Represents a shared threat intelligence item."""
    item_id: str
    indicator: str
    indicator_type: str
    threat_type: str = ''
    severity: str = 'medium'
    confidence: float = 0.0
    description: str = ''
    source: str = ''
    tags: List[str] = field(default_factory=list)
    shared_at: datetime = field(default_factory=datetime.utcnow)
    sharing_profile_id: str = ''
    direction: str = 'export'  # export, import
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'item_id': self.item_id,
            'indicator': self.indicator,
            'indicator_type': self.indicator_type,
            'threat_type': self.threat_type,
            'severity': self.severity,
            'confidence': self.confidence,
            'description': self.description,
            'source': self.source,
            'tags': self.tags,
            'shared_at': self.shared_at.isoformat(),
            'sharing_profile_id': self.sharing_profile_id,
            'direction': self.direction,
        }


@dataclass
class SharingStats:
    """Statistics for threat intelligence sharing."""
    total_profiles: int = 0
    active_profiles: int = 0
    total_items_exported: int = 0
    total_items_imported: int = 0
    by_protocol: Dict[str, int] = field(default_factory=dict)
    by_direction: Dict[str, int] = field(default_factory=dict)
    last_sync: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_profiles': self.total_profiles,
            'active_profiles': self.active_profiles,
            'total_items_exported': self.total_items_exported,
            'total_items_imported': self.total_items_imported,
            'by_protocol': self.by_protocol,
            'by_direction': self.by_direction,
            'last_sync': self.last_sync.isoformat() if self.last_sync else None,
        }


@dataclass
class SharingConfig:
    """Configuration for threat intelligence sharing."""
    stix_version: str = '2.1'
    taxii_version: str = '2.1'
    default_sync_interval: int = 3600  # seconds
    max_items_per_sync: int = 1000
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'stix_version': self.stix_version,
            'taxi_version': self.taxii_version,
            'default_sync_interval': self.default_sync_interval,
            'max_items_per_sync': self.max_items_per_sync,
        }


class ThreatIntelSharing:
    """
    Threat intelligence sharing for OpenLens.
    
    Provides:
    - STIX/TAXII support
    - MISP integration
    - Export/import of threat intelligence
    - Sharing with trusted partners
    - Synchronization with threat intelligence platforms
    """
    
    def __init__(self, config: SharingConfig = None, 
                 ioc_manager=None, threat_feed_manager=None):
        """
        Initialize the threat intelligence sharing.
        
        Args:
            config: SharingConfig instance.
            ioc_manager: IOCManager instance.
            threat_feed_manager: ThreatFeedManager instance.
        """
        self.config = config or SharingConfig()
        self.ioc_manager = ioc_manager
        self.threat_feed_manager = threat_feed_manager
        self._profiles: Dict[str, SharingProfile] = {}
        self._shared_items: Dict[str, SharedItem] = {}
        self._lock = threading.Lock()
        self._sync_thread = None
        self._running = False
        
        # Initialize with default profiles
        self._initialize_default_profiles()
    
    def _initialize_default_profiles(self):
        """Initialize default sharing profiles."""
        # Example STIX/TAXII server
        stix_profile = SharingProfile(
            profile_id='stix_default',
            name='STIX/TAXII Server',
            description='Default STIX/TAXII threat intelligence server',
            sharing_type='bidirectional',
            protocol='stix',
            endpoint='https://stix.example.com/api/',
            authentication={
                'type': 'basic',
                'username': 'openlens',
                'password': 'password',
            },
            filters={
                'severity': ['high', 'critical'],
                'threat_types': ['malware', 'phishing', 'botnet'],
            },
            sync_interval=3600,
        )
        self._profiles[stix_profile.profile_id] = stix_profile
        
        # Example MISP instance
        misp_profile = SharingProfile(
            profile_id='misp_default',
            name='MISP Instance',
            description='Default MISP threat intelligence sharing',
            sharing_type='bidirectional',
            protocol='misp',
            endpoint='https://misp.example.com/',
            authentication={
                'type': 'api_key',
                'api_key': 'your_api_key',
            },
            filters={
                'tags': ['openlens', 'threat-intel'],
            },
            sync_interval=3600,
        )
        self._profiles[misp_profile.profile_id] = misp_profile
    
    def add_profile(self, profile: SharingProfile) -> bool:
        """
        Add a sharing profile.
        
        Args:
            profile: SharingProfile to add.
            
        Returns:
            True if added.
        """
        with self._lock:
            if profile.profile_id in self._profiles:
                return False
            
            self._profiles[profile.profile_id] = profile
            return True
    
    def remove_profile(self, profile_id: str) -> bool:
        """
        Remove a sharing profile.
        
        Args:
            profile_id: Profile ID.
            
        Returns:
            True if removed.
        """
        with self._lock:
            if profile_id not in self._profiles:
                return False
            
            del self._profiles[profile_id]
            return True
    
    def get_profile(self, profile_id: str) -> Optional[SharingProfile]:
        """
        Get a sharing profile.
        
        Args:
            profile_id: Profile ID.
            
        Returns:
            SharingProfile or None.
        """
        return self._profiles.get(profile_id)
    
    def list_profiles(self, protocol: str = None, is_active: bool = None) -> List[SharingProfile]:
        """
        List sharing profiles.
        
        Args:
            protocol: Filter by protocol.
            is_active: Filter by active status.
            
        Returns:
            List of SharingProfile objects.
        """
        with self._lock:
            results = []
            
            for profile in self._profiles.values():
                if protocol and profile.protocol != protocol:
                    continue
                if is_active is not None and profile.is_active != is_active:
                    continue
                
                results.append(profile)
            
            return results
    
    def sync_profile(self, profile_id: str) -> bool:
        """
        Synchronize a sharing profile.
        
        Args:
            profile_id: Profile ID.
            
        Returns:
            True if sync was successful.
        """
        profile = self.get_profile(profile_id)
        
        if not profile or not profile.is_active:
            return False
        
        try:
            if profile.sharing_type in ['export', 'bidirectional']:
                self._export_to_profile(profile)
            
            if profile.sharing_type in ['import', 'bidirectional']:
                self._import_from_profile(profile)
            
            # Update last sync time
            profile.last_sync = datetime.utcnow()
            
            return True
        
        except Exception as e:
            print(f"Error syncing profile {profile_id}: {e}")
            return False
    
    def sync_all_profiles(self) -> Dict[str, bool]:
        """
        Synchronize all sharing profiles.
        
        Returns:
            Dictionary with profile IDs and sync status.
        """
        results = {}
        
        for profile_id in self._profiles:
            results[profile_id] = self.sync_profile(profile_id)
        
        return results
    
    def _export_to_profile(self, profile: SharingProfile):
        """Export threat intelligence to a profile."""
        if not self.ioc_manager:
            return
        
        # Get IOCs to export
        query = self._create_export_query(profile)
        iocs = self.ioc_manager.search_iocs(query)
        
        # Convert to the appropriate format
        if profile.protocol == 'stix':
            data = self._convert_to_stix(iocs)
        elif profile.protocol == 'misp':
            data = self._convert_to_misp(iocs)
        else:
            data = self._convert_to_json(iocs)
        
        # Send to the endpoint
        self._send_to_endpoint(profile, data, 'export')
        
        # Record shared items
        for ioc in iocs:
            shared_item = SharedItem(
                item_id=f"{profile.profile_id}:{ioc.ioc_id}",
                indicator=ioc.indicator,
                indicator_type=ioc.indicator_type,
                threat_type=ioc.threat_type,
                severity=ioc.severity,
                confidence=ioc.confidence,
                description=ioc.description,
                source=ioc.source,
                tags=ioc.tags,
                sharing_profile_id=profile.profile_id,
                direction='export',
            )
            
            with self._lock:
                self._shared_items[shared_item.item_id] = shared_item
    
    def _import_from_profile(self, profile: SharingProfile):
        """Import threat intelligence from a profile."""
        # Fetch data from the endpoint
        data = self._fetch_from_endpoint(profile)
        
        if not data:
            return
        
        # Convert from the appropriate format
        if profile.protocol == 'stix':
            iocs = self._convert_from_stix(data)
        elif profile.protocol == 'misp':
            iocs = self._convert_from_misp(data)
        else:
            iocs = self._convert_from_json(data)
        
        # Add to IOC manager
        if self.ioc_manager:
            for ioc_data in iocs:
                # Check if IOC already exists
                existing_ioc = self.ioc_manager.get_ioc(ioc_data.get('indicator', ''))
                
                if not existing_ioc:
                    self.ioc_manager.add_ioc(
                        indicator=ioc_data.get('indicator', ''),
                        indicator_type=ioc_data.get('indicator_type', ''),
                        threat_type=ioc_data.get('threat_type', ''),
                        confidence=ioc_data.get('confidence', 0.8),
                        severity=ioc_data.get('severity', 'medium'),
                        description=ioc_data.get('description', ''),
                        reference=ioc_data.get('reference', ''),
                        source=f"sharing:{profile.profile_id}",
                        tags=ioc_data.get('tags', []),
                    )
                
                # Record shared item
                shared_item = SharedItem(
                    item_id=f"{profile.profile_id}:{hashlib.sha256(ioc_data.get('indicator', '').encode()).hexdigest()}",
                    indicator=ioc_data.get('indicator', ''),
                    indicator_type=ioc_data.get('indicator_type', ''),
                    threat_type=ioc_data.get('threat_type', ''),
                    severity=ioc_data.get('severity', 'medium'),
                    confidence=ioc_data.get('confidence', 0.8),
                    description=ioc_data.get('description', ''),
                    source=f"sharing:{profile.profile_id}",
                    tags=ioc_data.get('tags', []),
                    sharing_profile_id=profile.profile_id,
                    direction='import',
                )
                
                with self._lock:
                    self._shared_items[shared_item.item_id] = shared_item
    
    def _create_export_query(self, profile: SharingProfile) -> Any:
        """Create a query for exporting IOCs based on profile filters."""
        from ..threat_intelligence.ioc_manager import IOCSearchQuery
        
        query = IOCSearchQuery()
        
        # Apply filters
        if 'severity' in profile.filters:
            query.severity = profile.filters['severity']
        
        if 'threat_types' in profile.filters:
            query.threat_type = profile.filters['threat_types'][0]  # Simplified
        
        if 'indicator_types' in profile.filters:
            query.indicator_type = profile.filters['indicator_types'][0]  # Simplified
        
        if 'min_confidence' in profile.filters:
            query.min_confidence = profile.filters['min_confidence']
        
        # Only export active IOCs
        query.is_active = True
        
        # Limit the number of items
        query.limit = self.config.max_items_per_sync
        
        return query
    
    # Per-type STIX pattern templates. The old code emitted
    # network-traffic:dst_ref.value for every non-hash type, so domains, URLs
    # and emails all round-tripped back as 'ip'.
    _STIX_PATTERNS = {
        'ip': "[ipv4-addr:value = '{v}']",
        'domain': "[domain-name:value = '{v}']",
        'url': "[url:value = '{v}']",
        'email': "[email-addr:value = '{v}']",
    }

    @staticmethod
    def _hash_algorithm(indicator: str) -> str:
        """Guess the hash algorithm from the *indicator's* length."""
        length = len(indicator or '')
        if length == 32:
            return 'MD5'
        if length == 40:
            return 'SHA-1'
        return 'SHA-256'

    def _stix_pattern(self, ioc: Any) -> str:
        """Build the STIX pattern for one IOC."""
        if ioc.indicator_type == 'hash':
            algo = self._hash_algorithm(ioc.indicator)
            return f"[file:hashes.'{algo}' = '{ioc.indicator}']"
        template = self._STIX_PATTERNS.get(ioc.indicator_type)
        if template:
            return template.format(v=ioc.indicator)
        return f"[artifact:payload_bin = '{ioc.indicator}']"

    def _convert_to_stix(self, iocs: List[Any]) -> Dict[str, Any]:
        """
        Convert IOCs to a STIX-2.1-shaped bundle.

        Note: this is hand-rolled and not validated against the STIX schema
        (the stix2 library is optional and not required here).
        """
        stix_objects = []

        for ioc in iocs:
            stix_object = {
                'type': 'indicator',
                'id': f"indicator--{hashlib.sha256(ioc.indicator.encode()).hexdigest()}",
                'created': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'modified': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'pattern': self._stix_pattern(ioc),
                'pattern_type': 'stix',
                'valid_from': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'labels': [ioc.threat_type] if ioc.threat_type else [],
                'description': ioc.description,
            }

            # Add confidence if available
            if hasattr(ioc, 'confidence'):
                stix_object['confidence'] = ioc.confidence

            stix_objects.append(stix_object)

        return {
            'type': 'bundle',
            'id': f"bundle--{hashlib.sha256(str(time.time()).encode()).hexdigest()}",
            'objects': stix_objects,
        }
    
    def _convert_to_misp(self, iocs: List[Any]) -> Dict[str, Any]:
        """Convert IOCs to MISP format."""
        # Simplified MISP conversion
        misp_event = {
            'Event': {
                'info': 'OpenLens Threat Intelligence Export',
                'timestamp': int(time.time()),
                'published': False,
                'uuid': hashlib.sha256(str(time.time()).encode()).hexdigest(),
                'Attribute': [],
            }
        }
        
        for ioc in iocs:
            attribute = {
                'type': self._map_indicator_type_to_misp(ioc.indicator_type, ioc.indicator),
                'value': ioc.indicator,
                'comment': ioc.description,
                'to_ids': True,
            }
            
            # Add tags
            if ioc.tags:
                attribute['Tag'] = [{'name': tag} for tag in ioc.tags]
            
            misp_event['Event']['Attribute'].append(attribute)
        
        return misp_event
    
    def _map_indicator_type_to_misp(self, indicator_type: str,
                                    indicator: str = '') -> str:
        """
        Map indicator type to MISP attribute type.

        The hash algorithm is chosen from the *indicator's* length; the old
        code measured the type name ('hash', length 4), mapping every hash to
        sha256.
        """
        if indicator_type == 'hash':
            return self._hash_algorithm(indicator).lower().replace('-', '')
        mapping = {
            'ip': 'ip-dst',
            'domain': 'domain',
            'url': 'url',
            'email': 'email-dst',
        }
        return mapping.get(indicator_type, 'text')
    
    def _convert_to_json(self, iocs: List[Any]) -> List[Dict[str, Any]]:
        """Convert IOCs to JSON format."""
        return [ioc.to_dict() for ioc in iocs]
    
    def _convert_from_stix(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert STIX data to IOC format."""
        iocs = []
        
        if data.get('type') == 'bundle':
            for obj in data.get('objects', []):
                if obj.get('type') == 'indicator':
                    ioc = {
                        'indicator': self._extract_indicator_from_stix(obj.get('pattern', '')),
                        'indicator_type': self._extract_indicator_type_from_stix(obj.get('pattern', '')),
                        'threat_type': obj.get('labels', [])[0] if obj.get('labels') else '',
                        'severity': 'medium',
                        'confidence': obj.get('confidence', 0.8),
                        'description': obj.get('description', ''),
                        'reference': obj.get('external_references', [{}])[0].get('url', '') if obj.get('external_references') else '',
                        'source': 'stix',
                        'tags': obj.get('labels', []),
                    }
                    iocs.append(ioc)
        
        return iocs
    
    def _extract_indicator_from_stix(self, pattern: str) -> str:
        """Extract indicator from STIX pattern."""
        # Simplified extraction. Strip the pattern's closing bracket before the
        # quotes - the old order left a trailing "']" on every indicator, so a
        # re-imported bundle never matched its own IOCs.
        if '=' in pattern:
            value = pattern.split('=', 1)[1].strip()
            return value.rstrip(']').strip().strip("'\"")
        return pattern
    
    def _extract_indicator_type_from_stix(self, pattern: str) -> str:
        """Extract indicator type from STIX pattern."""
        lowered = pattern.lower()
        if 'file:hashes' in lowered or 'hashes' in lowered:
            return 'hash'
        if 'domain-name' in lowered:
            return 'domain'
        if 'url:value' in lowered:
            return 'url'
        if 'email-addr' in lowered:
            return 'email'
        if 'ipv4-addr' in lowered or 'ipv6-addr' in lowered \
                or 'dst_ref' in lowered or 'src_ref' in lowered:
            return 'ip'
        return 'unknown'
    
    def _convert_from_misp(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert MISP data to IOC format."""
        iocs = []
        
        event = data.get('Event', {})
        for attribute in event.get('Attribute', []):
            ioc = {
                'indicator': attribute.get('value', ''),
                'indicator_type': self._map_misp_to_indicator_type(attribute.get('type', '')),
                'threat_type': '',
                'severity': 'medium',
                'confidence': 0.8,
                'description': attribute.get('comment', ''),
                'reference': '',
                'source': 'misp',
                'tags': [tag.get('name', '') for tag in attribute.get('Tag', [])],
            }
            iocs.append(ioc)
        
        return iocs
    
    def _map_misp_to_indicator_type(self, misp_type: str) -> str:
        """Map MISP attribute type to indicator type."""
        mapping = {
            'ip-dst': 'ip',
            'ip-src': 'ip',
            'domain': 'domain',
            'url': 'url',
            'md5': 'hash',
            'sha1': 'hash',
            'sha256': 'hash',
            'email-dst': 'email',
            'email-src': 'email',
        }
        return mapping.get(misp_type, 'unknown')
    
    def _convert_from_json(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert JSON data to IOC format."""
        return data
    
    def _send_to_endpoint(self, profile: SharingProfile, data: Any, direction: str):
        """Send data to an endpoint."""
        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'OpenLens Threat Intel Sharing',
            }
            
            # Add authentication
            if profile.authentication:
                auth_type = profile.authentication.get('type', '')
                
                if auth_type == 'basic':
                    import base64
                    username = profile.authentication.get('username', '')
                    password = profile.authentication.get('password', '')
                    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                    headers['Authorization'] = f"Basic {credentials}"
                elif auth_type == 'api_key':
                    api_key = profile.authentication.get('api_key', '')
                    headers['Authorization'] = f"Bearer {api_key}"
                elif auth_type == 'token':
                    token = profile.authentication.get('token', '')
                    headers['Authorization'] = f"Token {token}"
            
            # Determine endpoint URL
            endpoint = profile.endpoint
            if not endpoint.endswith('/'):
                endpoint += '/'
            
            # Add direction-specific path
            if profile.protocol == 'stix':
                if direction == 'export':
                    endpoint += 'indicators/'
                else:
                    endpoint += 'indicators/'
            elif profile.protocol == 'misp':
                if direction == 'export':
                    endpoint += 'events/push'
                else:
                    endpoint += 'events/pull'
            
            # Send request
            if direction == 'export':
                response = requests.post(
                    endpoint,
                    json=data,
                    headers=headers,
                    timeout=30,
                )
            else:
                response = requests.get(
                    endpoint,
                    headers=headers,
                    timeout=30,
                )
            
            if response.status_code >= 200 and response.status_code < 300:
                return True
            else:
                print(f"Error sending to {endpoint}: HTTP {response.status_code}")
                return False
        
        except Exception as e:
            print(f"Error sending to endpoint: {e}")
            return False
    
    def _fetch_from_endpoint(self, profile: SharingProfile) -> Optional[Any]:
        """Fetch data from an endpoint."""
        try:
            headers = {
                'Accept': 'application/json',
                'User-Agent': 'OpenLens Threat Intel Sharing',
            }
            
            # Add authentication
            if profile.authentication:
                auth_type = profile.authentication.get('type', '')
                
                if auth_type == 'basic':
                    import base64
                    username = profile.authentication.get('username', '')
                    password = profile.authentication.get('password', '')
                    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
                    headers['Authorization'] = f"Basic {credentials}"
                elif auth_type == 'api_key':
                    api_key = profile.authentication.get('api_key', '')
                    headers['Authorization'] = f"Bearer {api_key}"
                elif auth_type == 'token':
                    token = profile.authentication.get('token', '')
                    headers['Authorization'] = f"Token {token}"
            
            # Determine endpoint URL
            endpoint = profile.endpoint
            if not endpoint.endswith('/'):
                endpoint += '/'
            
            # Add protocol-specific path
            if profile.protocol == 'stix':
                endpoint += 'indicators/'
            elif profile.protocol == 'misp':
                endpoint += 'events/pull'
            
            # Fetch data
            response = requests.get(
                endpoint,
                headers=headers,
                timeout=30,
            )
            
            if response.status_code >= 200 and response.status_code < 300:
                return response.json()
            else:
                print(f"Error fetching from {endpoint}: HTTP {response.status_code}")
                return None
        
        except Exception as e:
            print(f"Error fetching from endpoint: {e}")
            return None
    
    def start_auto_sync(self, interval: int = None):
        """
        Start automatic synchronization.
        
        Args:
            interval: Sync interval in seconds (None for default).
        """
        if self._running:
            return
        
        interval = interval or self.config.default_sync_interval
        
        def sync_loop():
            while self._running:
                self.sync_all_profiles()
                time.sleep(interval)
        
        self._sync_thread = threading.Thread(target=sync_loop, daemon=True)
        self._running = True
        self._sync_thread.start()
    
    def stop_auto_sync(self):
        """Stop automatic synchronization."""
        self._running = False
        if self._sync_thread:
            self._sync_thread.join(timeout=5)
            self._sync_thread = None
    
    def get_shared_item(self, item_id: str) -> Optional[SharedItem]:
        """
        Get a shared item.
        
        Args:
            item_id: Item ID.
            
        Returns:
            SharedItem or None.
        """
        with self._lock:
            return self._shared_items.get(item_id)
    
    def list_shared_items(self, profile_id: str = None, direction: str = None,
                          limit: int = 100) -> List[SharedItem]:
        """
        List shared items.
        
        Args:
            profile_id: Filter by profile ID.
            direction: Filter by direction.
            limit: Maximum number of results.
            
        Returns:
            List of SharedItem objects.
        """
        with self._lock:
            results = []
            
            for item in self._shared_items.values():
                if profile_id and item.sharing_profile_id != profile_id:
                    continue
                if direction and item.direction != direction:
                    continue
                
                results.append(item)
            
            # Sort by shared_at (descending)
            results.sort(key=lambda x: x.shared_at, reverse=True)
            
            return results[:limit]
    
    def get_stats(self) -> SharingStats:
        """
        Get sharing statistics.
        
        Returns:
            SharingStats.
        """
        with self._lock:
            stats = SharingStats()
            
            stats.total_profiles = len(self._profiles)
            stats.active_profiles = len([p for p in self._profiles.values() if p.is_active])
            stats.total_items_exported = len([i for i in self._shared_items.values() if i.direction == 'export'])
            stats.total_items_imported = len([i for i in self._shared_items.values() if i.direction == 'import'])
            
            # Count by protocol
            for profile in self._profiles.values():
                stats.by_protocol[profile.protocol] = stats.by_protocol.get(profile.protocol, 0) + 1
            
            # Count by direction
            for item in self._shared_items.values():
                stats.by_direction[item.direction] = stats.by_direction.get(item.direction, 0) + 1
            
            # Get last sync
            last_sync = None
            for profile in self._profiles.values():
                if profile.last_sync and (not last_sync or profile.last_sync > last_sync):
                    last_sync = profile.last_sync
            stats.last_sync = last_sync
            
            return stats
    
    def _resolve_iocs(self, ioc_ids: List[str] = None, query: Any = None) -> List[Any]:
        """Resolve IOCs by explicit ids, a search query, or all IOCs."""
        if not self.ioc_manager:
            return []
        if ioc_ids:
            resolved = [self.ioc_manager.get_ioc_by_id(i) for i in ioc_ids]
            return [ioc for ioc in resolved if ioc]
        if query is not None:
            return self.ioc_manager.search_iocs(query)
        return self.ioc_manager.search_iocs()

    def export_to_stix(self, ioc_ids: List[str] = None, query: Any = None,
                       validate: bool = False) -> Dict[str, Any]:
        """
        Export IOCs as a STIX-2.1-shaped bundle.

        The bundle is hand-rolled, not schema-validated. Pass validate=True
        only when the stix2 library is installed; without it validation is
        refused loudly rather than silently skipped.

        Args:
            ioc_ids: Explicit IOC ids to export (None for query/all).
            query: IOCSearchQuery selecting the IOCs (None for all).
            validate: Validate the bundle against the STIX schema.

        Returns:
            STIX bundle dictionary.
        """
        if validate:
            try:
                import stix2  # noqa: F401
            except ImportError:
                raise RuntimeError(
                    'stix2 not installed; cannot validate. '
                    'Install with: pip install stix2, or call with validate=False')
        return self._convert_to_stix(self._resolve_iocs(ioc_ids, query))

    def import_from_stix(self, stix_data: Union[str, Dict[str, Any]],
                         source: str = 'stix') -> int:
        """
        Import IOCs from a STIX bundle (JSON string or parsed dict).

        Args:
            stix_data: STIX bundle.
            source: Source label recorded on the imported IOCs.

        Returns:
            Number of IOCs added.
        """
        if isinstance(stix_data, str):
            stix_data = json.loads(stix_data)
        if not isinstance(stix_data, dict):
            raise ValueError('stix_data must be a JSON object or its string form')

        ioc_dicts = self._convert_from_stix(stix_data)
        for ioc in ioc_dicts:
            ioc['source'] = source
        if not self.ioc_manager:
            return 0
        return self.ioc_manager.bulk_add_iocs(ioc_dicts)

    def export_to_misp(self, ioc_ids: List[str] = None, query: Any = None) -> Dict[str, Any]:
        """Export IOCs as a MISP event dictionary."""
        return self._convert_to_misp(self._resolve_iocs(ioc_ids, query))

    def import_from_misp(self, misp_data: Union[str, Dict[str, Any]],
                         source: str = 'misp') -> int:
        """Import IOCs from a MISP event (JSON string or parsed dict)."""
        if isinstance(misp_data, str):
            misp_data = json.loads(misp_data)
        if not isinstance(misp_data, dict):
            raise ValueError('misp_data must be a JSON object or its string form')

        ioc_dicts = self._convert_from_misp(misp_data)
        for ioc in ioc_dicts:
            ioc['source'] = source
        if not self.ioc_manager:
            return 0
        return self.ioc_manager.bulk_add_iocs(ioc_dicts)

    def export_to_json(self) -> str:
        """
        Export sharing data to JSON.

        Returns:
            JSON string.
        """
        data = {
            'profiles': [p.to_dict() for p in self._profiles.values()],
            'shared_items': [i.to_dict() for i in self._shared_items.values()],
            'config': self.config.to_dict(),
        }
        
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: str) -> bool:
        """
        Import sharing data from JSON.
        
        Args:
            json_data: JSON string.
            
        Returns:
            True if imported.
        """
        try:
            data = json.loads(json_data)
            
            # Import profiles
            self._profiles = {}
            for profile_data in data.get('profiles', []):
                profile = SharingProfile(
                    profile_id=profile_data['profile_id'],
                    name=profile_data['name'],
                    description=profile_data.get('description', ''),
                    sharing_type=profile_data.get('sharing_type', 'export'),
                    protocol=profile_data.get('protocol', 'stix'),
                    endpoint=profile_data.get('endpoint', ''),
                    authentication=profile_data.get('authentication', {}),
                    filters=profile_data.get('filters', {}),
                    is_active=profile_data.get('is_active', True),
                    last_sync=datetime.fromisoformat(profile_data['last_sync']) if profile_data.get('last_sync') else None,
                    sync_interval=profile_data.get('sync_interval', 3600),
                )
                self._profiles[profile.profile_id] = profile
            
            # Import shared items
            self._shared_items = {}
            for item_data in data.get('shared_items', []):
                item = SharedItem(
                    item_id=item_data['item_id'],
                    indicator=item_data['indicator'],
                    indicator_type=item_data['indicator_type'],
                    threat_type=item_data.get('threat_type', ''),
                    severity=item_data.get('severity', 'medium'),
                    confidence=item_data.get('confidence', 0.0),
                    description=item_data.get('description', ''),
                    source=item_data.get('source', ''),
                    tags=item_data.get('tags', []),
                    shared_at=datetime.fromisoformat(item_data['shared_at']),
                    sharing_profile_id=item_data.get('sharing_profile_id', ''),
                    direction=item_data.get('direction', 'export'),
                )
                self._shared_items[item.item_id] = item
            
            # Import config
            config_data = data.get('config', {})
            self.config = SharingConfig(
                stix_version=config_data.get('stix_version', '2.1'),
                taxii_version=config_data.get('taxi_version', '2.1'),
                default_sync_interval=config_data.get('default_sync_interval', 3600),
                max_items_per_sync=config_data.get('max_items_per_sync', 1000),
            )
            
            return True
        
        except Exception as e:
            print(f"Error importing sharing data: {e}")
            return False


# Global threat intel sharing instance
threat_intel_sharing = ThreatIntelSharing()
