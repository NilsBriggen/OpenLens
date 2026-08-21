"""
Threat Feed Manager for OpenLens

Provides threat feed integration:
- Multiple threat feed sources
- Feed parsing and normalization
- Feed updates
- Feed caching
- Feed statistics
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
from urllib.parse import urlparse

from backend.paths import resolve_dir


@dataclass
class ThreatFeed:
    """Represents a threat feed."""
    feed_id: str
    name: str
    description: str = ''
    url: str = ''
    feed_type: str = 'ioc'  # ioc, reputation, vulnerability, malware, etc.
    format: str = 'csv'  # csv, json, txt, stix, misp
    update_interval: int = 3600  # seconds
    last_updated: datetime = None
    is_active: bool = True
    requires_auth: bool = False
    auth_username: str = ''
    auth_password: str = ''
    auth_token: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'feed_id': self.feed_id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'feed_type': self.feed_type,
            'format': self.format,
            'update_interval': self.update_interval,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'is_active': self.is_active,
            'requires_auth': self.requires_auth,
            'auth_username': self.auth_username,
            'auth_password': '*****' if self.auth_password else '',
            'auth_token': '*****' if self.auth_token else '',
        }


@dataclass
class ThreatFeedItem:
    """Represents an item from a threat feed."""
    item_id: str
    feed_id: str
    indicator: str
    indicator_type: str = ''  # ip, domain, url, hash, email, etc.
    threat_type: str = ''  # malware, phishing, botnet, c2, etc.
    confidence: float = 0.0
    severity: str = 'medium'  # low, medium, high, critical
    description: str = ''
    reference: str = ''
    first_seen: datetime = None
    last_seen: datetime = None
    tags: List[str] = field(default_factory=list)
    raw_data: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'item_id': self.item_id,
            'feed_id': self.feed_id,
            'indicator': self.indicator,
            'indicator_type': self.indicator_type,
            'threat_type': self.threat_type,
            'confidence': self.confidence,
            'severity': self.severity,
            'description': self.description,
            'reference': self.reference,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'tags': self.tags,
            'raw_data': self.raw_data,
        }


@dataclass
class ThreatFeedConfig:
    """Configuration for threat feed manager."""
    feed_dir: str = field(
        default_factory=lambda: resolve_dir('OPENLENS_FEED_DIR', '/var/data/openlens/feeds', 'feeds')
    )
    update_interval: int = 3600  # seconds
    max_items_per_feed: int = 100000
    max_age: int = 30  # days
    user_agent: str = 'OpenLens Threat Feed Manager/1.0'
    timeout: int = 30
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'feed_dir': self.feed_dir,
            'update_interval': self.update_interval,
            'max_items_per_feed': self.max_items_per_feed,
            'max_age': self.max_age,
            'user_agent': self.user_agent,
            'timeout': self.timeout,
        }


@dataclass
class ThreatFeedStats:
    """Statistics for threat feeds."""
    total_feeds: int = 0
    active_feeds: int = 0
    total_items: int = 0
    by_feed_type: Dict[str, int] = field(default_factory=dict)
    by_indicator_type: Dict[str, int] = field(default_factory=dict)
    by_threat_type: Dict[str, int] = field(default_factory=dict)
    by_severity: Dict[str, int] = field(default_factory=dict)
    last_updated: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_feeds': self.total_feeds,
            'active_feeds': self.active_feeds,
            'total_items': self.total_items,
            'by_feed_type': self.by_feed_type,
            'by_indicator_type': self.by_indicator_type,
            'by_threat_type': self.by_threat_type,
            'by_severity': self.by_severity,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
        }


class ThreatFeedManager:
    """
    Threat feed manager for OpenLens.
    
    Provides:
    - Multiple threat feed sources
    - Feed parsing and normalization
    - Feed updates
    - Feed caching
    - Feed statistics
    """
    
    def __init__(self, config: ThreatFeedConfig = None):
        """
        Initialize the threat feed manager.
        
        Args:
            config: ThreatFeedConfig instance.
        """
        self.config = config or ThreatFeedConfig()
        self._feeds: Dict[str, ThreatFeed] = {}
        self._items: Dict[str, ThreatFeedItem] = {}  # indicator -> item
        self._feed_items: Dict[str, List[str]] = defaultdict(list)  # feed_id -> [item_ids]
        self._lock = threading.Lock()
        self._update_thread = None
        self._running = False
        
        # Create feed directory if it doesn't exist
        if self.config.feed_dir and not os.path.exists(self.config.feed_dir):
            os.makedirs(self.config.feed_dir, exist_ok=True)
        
        # Initialize with default feeds
        self._initialize_default_feeds()
    
    def _initialize_default_feeds(self):
        """Initialize default threat feeds."""
        default_feeds = [
            ThreatFeed(
                feed_id='abuse_ch',
                name='Abuse.ch Feodo Tracker',
                description='Feodo (aka Emotet/Cobalt Strike) botnet C2 IPs',
                url='https://feodotracker.abuse.ch/downloads/IP_blocklist.txt',
                feed_type='ioc',
                format='txt',
                update_interval=3600,
            ),
            ThreatFeed(
                feed_id='abuse_ch_malwarebazaar',
                name='Abuse.ch MalwareBazaar',
                description='MalwareBazaar hash feed',
                url='https://bazaar.abuse.ch/export/txt/sha256/',
                feed_type='ioc',
                format='txt',
                update_interval=3600,
            ),
            ThreatFeed(
                feed_id='alienvault_otx',
                name='AlienVault OTX',
                description='AlienVault Open Threat Exchange pulse feeds',
                url='https://otx.alienvault.com/api/v1/indicators/export',
                feed_type='ioc',
                format='json',
                update_interval=3600,
                requires_auth=True,
                auth_token='YOUR_OTX_API_KEY',
            ),
            ThreatFeed(
                feed_id='fireeye',
                name='FireEye Threat Intelligence',
                description='FireEye threat intelligence feeds',
                url='https://api.threatintel.fireeye.com/',
                feed_type='ioc',
                format='json',
                update_interval=3600,
                requires_auth=True,
            ),
            ThreatFeed(
                feed_id='proofpoint',
                name='Proofpoint Threat Intelligence',
                description='Proofpoint threat intelligence feeds',
                url='https://tide.dnsfilter.com/api/v2/indicators',
                feed_type='ioc',
                format='json',
                update_interval=3600,
                requires_auth=True,
            ),
            ThreatFeed(
                feed_id='misp',
                name='MISP Threat Sharing',
                description='MISP threat sharing platform',
                url='https://www.misp-project.org/feeds/',
                feed_type='ioc',
                format='misp',
                update_interval=3600,
                requires_auth=True,
            ),
        ]
        
        for feed in default_feeds:
            self._feeds[feed.feed_id] = feed
    
    def create_feed(self, name: str, url: str, feed_type: str = 'ioc',
                    enabled: bool = True, description: str = '',
                    format: str = 'csv', update_interval: int = 3600,
                    **auth_kwargs) -> Optional[ThreatFeed]:
        """
        Construct and register a feed from scalars (add_feed takes an object).

        Returns:
            The created ThreatFeed, or None when a feed with the same id
            already exists.
        """
        feed_id = hashlib.sha256(f'{name}:{url}'.encode()).hexdigest()[:16]
        feed = ThreatFeed(
            feed_id=feed_id,
            name=name,
            description=description,
            url=url,
            feed_type=feed_type,
            format=format,
            update_interval=update_interval,
            is_active=enabled,
            requires_auth=bool(auth_kwargs.get('auth_username') or auth_kwargs.get('auth_token')),
            auth_username=auth_kwargs.get('auth_username', ''),
            auth_password=auth_kwargs.get('auth_password', ''),
            auth_token=auth_kwargs.get('auth_token', ''),
        )
        return feed if self.add_feed(feed) else None

    def add_feed(self, feed: ThreatFeed) -> bool:
        """
        Add a threat feed.
        
        Args:
            feed: ThreatFeed to add.
            
        Returns:
            True if added.
        """
        with self._lock:
            if feed.feed_id in self._feeds:
                return False
            
            self._feeds[feed.feed_id] = feed
            return True
    
    def remove_feed(self, feed_id: str) -> bool:
        """
        Remove a threat feed.
        
        Args:
            feed_id: Feed ID.
            
        Returns:
            True if removed.
        """
        with self._lock:
            if feed_id not in self._feeds:
                return False
            
            # Remove all items from this feed
            if feed_id in self._feed_items:
                for item_id in self._feed_items[feed_id]:
                    if item_id in self._items:
                        del self._items[item_id]
                del self._feed_items[feed_id]
            
            del self._feeds[feed_id]
            return True
    
    def get_feed(self, feed_id: str) -> Optional[ThreatFeed]:
        """
        Get a threat feed.
        
        Args:
            feed_id: Feed ID.
            
        Returns:
            ThreatFeed or None.
        """
        return self._feeds.get(feed_id)
    
    def list_feeds(self, feed_type: str = None) -> List[ThreatFeed]:
        """
        List all threat feeds.
        
        Args:
            feed_type: Filter by feed type (None for all).
            
        Returns:
            List of ThreatFeed objects.
        """
        with self._lock:
            if feed_type:
                return [f for f in self._feeds.values() if f.feed_type == feed_type]
            return list(self._feeds.values())
    
    def update_feed(self, feed_id: str) -> bool:
        """
        Update a threat feed (fetch latest data).
        
        Args:
            feed_id: Feed ID.
            
        Returns:
            True if updated.
        """
        feed = self.get_feed(feed_id)
        
        if not feed or not feed.is_active:
            return False
        
        try:
            # Fetch feed data
            data = self._fetch_feed(feed)
            
            if not data:
                return False
            
            # Parse feed data
            items = self._parse_feed(feed, data)
            
            # Store items
            with self._lock:
                # Remove old items from this feed
                if feed_id in self._feed_items:
                    for item_id in self._feed_items[feed_id]:
                        if item_id in self._items:
                            del self._items[item_id]
                    del self._feed_items[feed_id]
                
                # Add new items
                self._feed_items[feed_id] = []
                for item in items:
                    # Use indicator as item_id for deduplication
                    item_id = f"{feed_id}:{item.indicator}"
                    self._items[item_id] = item
                    self._feed_items[feed_id].append(item_id)
                
                # Update feed timestamp
                feed.last_updated = datetime.utcnow()
            
            return True
        
        except Exception as e:
            print(f"Error updating feed {feed_id}: {e}")
            return False
    
    def update_all_feeds(self) -> Dict[str, bool]:
        """
        Update all threat feeds.
        
        Returns:
            Dictionary with feed IDs and update status.
        """
        results = {}
        
        for feed_id in self._feeds:
            results[feed_id] = self.update_feed(feed_id)
        
        return results
    
    def _fetch_feed(self, feed: ThreatFeed) -> Optional[str]:
        """Fetch data from a feed."""
        try:
            headers = {'User-Agent': self.config.user_agent}
            
            if feed.requires_auth:
                if feed.auth_token:
                    headers['Authorization'] = f"Bearer {feed.auth_token}"
                elif feed.auth_username and feed.auth_password:
                    headers['Authorization'] = f"Basic {self._base64_encode(f'{feed.auth_username}:{feed.auth_password}')}"
            
            response = requests.get(
                feed.url,
                headers=headers,
                timeout=self.config.timeout,
            )
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"Failed to fetch feed {feed.feed_id}: HTTP {response.status_code}")
                return None
        
        except Exception as e:
            print(f"Error fetching feed {feed.feed_id}: {e}")
            return None
    
    def _base64_encode(self, data: str) -> str:
        """Base64 encode a string."""
        import base64
        return base64.b64encode(data.encode()).decode()
    
    def _parse_feed(self, feed: ThreatFeed, data: str) -> List[ThreatFeedItem]:
        """Parse feed data."""
        items = []
        
        try:
            if feed.format == 'txt':
                items = self._parse_txt_feed(feed, data)
            elif feed.format == 'csv':
                items = self._parse_csv_feed(feed, data)
            elif feed.format == 'json':
                items = self._parse_json_feed(feed, data)
            elif feed.format == 'stix':
                items = self._parse_stix_feed(feed, data)
            elif feed.format == 'misp':
                items = self._parse_misp_feed(feed, data)
            else:
                # Try to auto-detect format
                items = self._parse_auto_feed(feed, data)
        
        except Exception as e:
            print(f"Error parsing feed {feed.feed_id}: {e}")
        
        return items
    
    def _parse_txt_feed(self, feed: ThreatFeed, data: str) -> List[ThreatFeedItem]:
        """Parse a text feed."""
        items = []
        
        for line in data.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Determine indicator type
            indicator_type = self._detect_indicator_type(line)
            
            item = ThreatFeedItem(
                item_id=f"{feed.feed_id}:{hashlib.sha256(line.encode()).hexdigest()}",
                feed_id=feed.feed_id,
                indicator=line,
                indicator_type=indicator_type,
                threat_type=feed.feed_type,
                confidence=0.8,
                severity='medium',
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                raw_data={'source': feed.name},
            )
            items.append(item)
        
        return items
    
    def _parse_csv_feed(self, feed: ThreatFeed, data: str) -> List[ThreatFeedItem]:
        """Parse a CSV feed."""
        import csv
        from io import StringIO
        
        items = []
        
        reader = csv.reader(StringIO(data))
        for row in reader:
            if not row:
                continue
            
            # Assume first column is the indicator
            indicator = row[0].strip()
            if not indicator:
                continue
            
            # Try to extract more information from other columns
            indicator_type = self._detect_indicator_type(indicator)
            threat_type = row[1].strip() if len(row) > 1 else feed.feed_type
            confidence = float(row[2].strip()) if len(row) > 2 and row[2].strip().replace('.', '').isdigit() else 0.8
            severity = row[3].strip().lower() if len(row) > 3 else 'medium'
            description = row[4].strip() if len(row) > 4 else ''
            
            item = ThreatFeedItem(
                item_id=f"{feed.feed_id}:{hashlib.sha256(indicator.encode()).hexdigest()}",
                feed_id=feed.feed_id,
                indicator=indicator,
                indicator_type=indicator_type,
                threat_type=threat_type,
                confidence=confidence,
                severity=severity,
                description=description,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                raw_data={'source': feed.name, 'row': row},
            )
            items.append(item)
        
        return items
    
    def _parse_json_feed(self, feed: ThreatFeed, data: str) -> List[ThreatFeedItem]:
        """Parse a JSON feed."""
        items = []
        
        try:
            json_data = json.loads(data)
            
            if isinstance(json_data, list):
                # Array of items
                for item_data in json_data:
                    item = self._parse_json_item(feed, item_data)
                    if item:
                        items.append(item)
            elif isinstance(json_data, dict):
                # Single item or object with items
                if 'indicators' in json_data:
                    for item_data in json_data['indicators']:
                        item = self._parse_json_item(feed, item_data)
                        if item:
                            items.append(item)
                elif 'results' in json_data:
                    for item_data in json_data['results']:
                        item = self._parse_json_item(feed, item_data)
                        if item:
                            items.append(item)
                else:
                    # Try to parse as single item
                    item = self._parse_json_item(feed, json_data)
                    if item:
                        items.append(item)
        
        except Exception as e:
            print(f"Error parsing JSON feed: {e}")
        
        return items
    
    def _parse_json_item(self, feed: ThreatFeed, item_data: Dict) -> Optional[ThreatFeedItem]:
        """Parse a single JSON item."""
        try:
            # Extract indicator
            indicator = item_data.get('indicator', '') or \
                       item_data.get('value', '') or \
                       item_data.get('ip', '') or \
                       item_data.get('domain', '') or \
                       item_data.get('url', '') or \
                       item_data.get('hash', '')
            
            if not indicator:
                return None
            
            indicator_type = item_data.get('type', '') or self._detect_indicator_type(indicator)
            threat_type = item_data.get('threat_type', '') or \
                          item_data.get('classification', '') or \
                          feed.feed_type
            confidence = float(item_data.get('confidence', 0.8))
            severity = item_data.get('severity', 'medium').lower()
            description = item_data.get('description', '') or \
                          item_data.get('title', '') or \
                          item_data.get('name', '')
            reference = item_data.get('reference', '') or \
                        item_data.get('source', '') or \
                        feed.url
            
            # Extract timestamps
            first_seen = None
            last_seen = None
            
            if 'first_seen' in item_data:
                try:
                    first_seen = datetime.fromisoformat(item_data['first_seen'])
                except:
                    pass
            
            if 'last_seen' in item_data:
                try:
                    last_seen = datetime.fromisoformat(item_data['last_seen'])
                except:
                    pass
            
            # Extract tags
            tags = item_data.get('tags', []) or \
                  item_data.get('tag', []) or \
                  []
            
            if isinstance(tags, str):
                tags = [tags]
            
            item = ThreatFeedItem(
                item_id=f"{feed.feed_id}:{hashlib.sha256(indicator.encode()).hexdigest()}",
                feed_id=feed.feed_id,
                indicator=indicator,
                indicator_type=indicator_type,
                threat_type=threat_type,
                confidence=confidence,
                severity=severity,
                description=description,
                reference=reference,
                first_seen=first_seen or datetime.utcnow(),
                last_seen=last_seen or datetime.utcnow(),
                tags=tags,
                raw_data=item_data,
            )
            
            return item
        
        except Exception as e:
            print(f"Error parsing JSON item: {e}")
            return None
    
    def _parse_stix_feed(self, feed: ThreatFeed, data: str) -> List[ThreatFeedItem]:
        """Parse a STIX feed."""
        # STIX parsing would be implemented here
        # For now, fall back to auto-detection
        return self._parse_auto_feed(feed, data)
    
    def _parse_misp_feed(self, feed: ThreatFeed, data: str) -> List[ThreatFeedItem]:
        """Parse a MISP feed."""
        # MISP parsing would be implemented here
        # For now, fall back to auto-detection
        return self._parse_auto_feed(feed, data)
    
    def _parse_auto_feed(self, feed: ThreatFeed, data: str) -> List[ThreatFeedItem]:
        """Auto-detect and parse feed format."""
        # Try JSON first
        try:
            json.loads(data)
            return self._parse_json_feed(feed, data)
        except:
            pass
        
        # Try CSV
        try:
            import csv
            from io import StringIO
            reader = csv.reader(StringIO(data))
            if len(list(reader)) > 1:
                return self._parse_csv_feed(feed, data)
        except:
            pass
        
        # Default to text
        return self._parse_txt_feed(feed, data)
    
    def _detect_indicator_type(self, indicator: str) -> str:
        """Detect the type of an indicator."""
        # IP address
        if self._is_ip_address(indicator):
            return 'ip'
        
        # Domain
        if self._is_domain(indicator):
            return 'domain'
        
        # URL
        if self._is_url(indicator):
            return 'url'
        
        # Email
        if self._is_email(indicator):
            return 'email'
        
        # Hash
        if self._is_hash(indicator):
            return 'hash'
        
        return 'unknown'
    
    def _is_ip_address(self, indicator: str) -> bool:
        """Check if indicator is an IP address."""
        import re
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        return bool(re.match(ip_pattern, indicator))
    
    def _is_domain(self, indicator: str) -> bool:
        """Check if indicator is a domain."""
        import re
        domain_pattern = r'^[a-zA-Z0-9\-]+(\.[a-zA-Z0-9\-]+)*\.[a-zA-Z]{2,}$'
        return bool(re.match(domain_pattern, indicator))
    
    def _is_url(self, indicator: str) -> bool:
        """Check if indicator is a URL."""
        return indicator.startswith('http://') or indicator.startswith('https://')
    
    def _is_email(self, indicator: str) -> bool:
        """Check if indicator is an email address."""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, indicator))
    
    def _is_hash(self, indicator: str) -> bool:
        """Check if indicator is a hash."""
        # MD5: 32 hex characters
        if len(indicator) == 32 and all(c in '0123456789abcdef' for c in indicator.lower()):
            return True
        
        # SHA-1: 40 hex characters
        if len(indicator) == 40 and all(c in '0123456789abcdef' for c in indicator.lower()):
            return True
        
        # SHA-256: 64 hex characters
        if len(indicator) == 64 and all(c in '0123456789abcdef' for c in indicator.lower()):
            return True
        
        return False
    
    def get_item(self, indicator: str, indicator_type: str = None) -> Optional[ThreatFeedItem]:
        """
        Get a threat feed item by indicator.
        
        Args:
            indicator: Indicator to look up.
            indicator_type: Indicator type (None for any).
            
        Returns:
            ThreatFeedItem or None.
        """
        with self._lock:
            # Try exact match first
            for item_id, item in self._items.items():
                if item.indicator == indicator:
                    if not indicator_type or item.indicator_type == indicator_type:
                        return item
            
            # Try fuzzy match (for hashes with different cases)
            if indicator_type == 'hash':
                for item_id, item in self._items.items():
                    if item.indicator_type == 'hash' and item.indicator.lower() == indicator.lower():
                        return item
            
            return None
    
    def search_items(self, query: str, indicator_type: str = None, 
                     threat_type: str = None, severity: str = None,
                     limit: int = 100) -> List[ThreatFeedItem]:
        """
        Search threat feed items.
        
        Args:
            query: Search query.
            indicator_type: Filter by indicator type.
            threat_type: Filter by threat type.
            severity: Filter by severity.
            limit: Maximum number of results.
            
        Returns:
            List of ThreatFeedItem objects.
        """
        with self._lock:
            results = []
            
            for item in self._items.values():
                # Filter by indicator type
                if indicator_type and item.indicator_type != indicator_type:
                    continue
                
                # Filter by threat type
                if threat_type and item.threat_type != threat_type:
                    continue
                
                # Filter by severity
                if severity and item.severity != severity:
                    continue
                
                # Search query
                if query:
                    query_lower = query.lower()
                    if (query_lower not in item.indicator.lower() and
                        query_lower not in item.description.lower() and
                        query_lower not in item.threat_type.lower()):
                        continue
                
                results.append(item)
                
                if len(results) >= limit:
                    break
            
            return results
    
    def get_stats(self) -> ThreatFeedStats:
        """
        Get threat feed statistics.
        
        Returns:
            ThreatFeedStats.
        """
        with self._lock:
            stats = ThreatFeedStats()
            
            stats.total_feeds = len(self._feeds)
            stats.active_feeds = len([f for f in self._feeds.values() if f.is_active])
            stats.total_items = len(self._items)
            
            # Count by feed type
            for feed in self._feeds.values():
                stats.by_feed_type[feed.feed_type] = stats.by_feed_type.get(feed.feed_type, 0) + 1
            
            # Count by indicator type
            for item in self._items.values():
                stats.by_indicator_type[item.indicator_type] = stats.by_indicator_type.get(item.indicator_type, 0) + 1
                stats.by_threat_type[item.threat_type] = stats.by_threat_type.get(item.threat_type, 0) + 1
                stats.by_severity[item.severity] = stats.by_severity.get(item.severity, 0) + 1
            
            # Get last updated
            last_updated = None
            for feed in self._feeds.values():
                if feed.last_updated and (not last_updated or feed.last_updated > last_updated):
                    last_updated = feed.last_updated
            stats.last_updated = last_updated
            
            return stats
    
    def start_auto_update(self, interval: int = None):
        """
        Start automatic feed updates.
        
        Args:
            interval: Update interval in seconds (None for config default).
        """
        if self._running:
            return
        
        interval = interval or self.config.update_interval
        
        def update_loop():
            while self._running:
                self.update_all_feeds()
                time.sleep(interval)
        
        self._update_thread = threading.Thread(target=update_loop, daemon=True)
        self._running = True
        self._update_thread.start()
    
    def stop_auto_update(self):
        """Stop automatic feed updates."""
        self._running = False
        if self._update_thread:
            self._update_thread.join(timeout=5)
            self._update_thread = None
    
    def export_to_json(self) -> str:
        """
        Export threat feed data to JSON.
        
        Returns:
            JSON string.
        """
        data = {
            'feeds': [f.to_dict() for f in self._feeds.values()],
            'items': [i.to_dict() for i in self._items.values()],
            'config': self.config.to_dict(),
        }
        
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: str) -> bool:
        """
        Import threat feed data from JSON.
        
        Args:
            json_data: JSON string.
            
        Returns:
            True if imported.
        """
        try:
            data = json.loads(json_data)
            
            # Import feeds
            self._feeds = {}
            for feed_data in data.get('feeds', []):
                feed = ThreatFeed(
                    feed_id=feed_data['feed_id'],
                    name=feed_data['name'],
                    description=feed_data.get('description', ''),
                    url=feed_data.get('url', ''),
                    feed_type=feed_data.get('feed_type', 'ioc'),
                    format=feed_data.get('format', 'txt'),
                    update_interval=feed_data.get('update_interval', 3600),
                    last_updated=datetime.fromisoformat(feed_data['last_updated']) if feed_data.get('last_updated') else None,
                    is_active=feed_data.get('is_active', True),
                    requires_auth=feed_data.get('requires_auth', False),
                    auth_username=feed_data.get('auth_username', ''),
                    auth_password=feed_data.get('auth_password', ''),
                    auth_token=feed_data.get('auth_token', ''),
                )
                self._feeds[feed.feed_id] = feed
            
            # Import items
            self._items = {}
            self._feed_items = defaultdict(list)
            for item_data in data.get('items', []):
                item = ThreatFeedItem(
                    item_id=item_data['item_id'],
                    feed_id=item_data['feed_id'],
                    indicator=item_data['indicator'],
                    indicator_type=item_data.get('indicator_type', ''),
                    threat_type=item_data.get('threat_type', ''),
                    confidence=item_data.get('confidence', 0.0),
                    severity=item_data.get('severity', 'medium'),
                    description=item_data.get('description', ''),
                    reference=item_data.get('reference', ''),
                    first_seen=datetime.fromisoformat(item_data['first_seen']) if item_data.get('first_seen') else None,
                    last_seen=datetime.fromisoformat(item_data['last_seen']) if item_data.get('last_seen') else None,
                    tags=item_data.get('tags', []),
                    raw_data=item_data.get('raw_data', {}),
                )
                self._items[item.item_id] = item
                self._feed_items[item.feed_id].append(item.item_id)
            
            # Import config
            config_data = data.get('config', {})
            self.config = ThreatFeedConfig(
                feed_dir=config_data.get('feed_dir', resolve_dir('OPENLENS_FEED_DIR', '/var/data/openlens/feeds', 'feeds')),
                update_interval=config_data.get('update_interval', 3600),
                max_items_per_feed=config_data.get('max_items_per_feed', 100000),
                max_age=config_data.get('max_age', 30),
                user_agent=config_data.get('user_agent', 'OpenLens Threat Feed Manager/1.0'),
                timeout=config_data.get('timeout', 30),
            )
            
            return True
        
        except Exception as e:
            print(f"Error importing threat feed data: {e}")
            return False


# Global threat feed manager instance
threat_feed_manager = ThreatFeedManager()
