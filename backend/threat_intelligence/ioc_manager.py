"""
Indicator of Compromise (IOC) Manager for OpenLens

Provides IOC management capabilities:
- IOC storage and retrieval
- IOC classification
- IOC correlation
- IOC enrichment
- IOC expiration
- IOC bulk operations
"""

import os
import time
import json
import hashlib
import threading
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict


@dataclass
class IOC:
    """Represents an Indicator of Compromise."""
    ioc_id: str
    indicator: str
    indicator_type: str  # ip, domain, url, hash, email, etc.
    threat_type: str = ''  # malware, phishing, botnet, c2, etc.
    confidence: float = 0.0
    severity: str = 'medium'  # low, medium, high, critical
    description: str = ''
    reference: str = ''
    source: str = ''
    first_seen: datetime = None
    last_seen: datetime = None
    expires_at: datetime = None
    tags: List[str] = field(default_factory=list)
    related_iocs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'ioc_id': self.ioc_id,
            'indicator': self.indicator,
            'indicator_type': self.indicator_type,
            'threat_type': self.threat_type,
            'confidence': self.confidence,
            'severity': self.severity,
            'description': self.description,
            'reference': self.reference,
            'source': self.source,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'tags': self.tags,
            'related_iocs': self.related_iocs,
            'metadata': self.metadata,
        }
    
    def is_expired(self) -> bool:
        """Check if the IOC has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at


@dataclass
class IOCSearchQuery:
    """Query for searching IOCs."""
    indicator: str = ''
    indicator_type: str = ''
    threat_type: str = ''
    severity: str = ''
    source: str = ''
    tags: List[str] = field(default_factory=list)
    min_confidence: float = 0.0
    is_active: bool = True
    limit: int = 100
    offset: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'indicator': self.indicator,
            'indicator_type': self.indicator_type,
            'threat_type': self.threat_type,
            'severity': self.severity,
            'source': self.source,
            'tags': self.tags,
            'min_confidence': self.min_confidence,
            'is_active': self.is_active,
            'limit': self.limit,
            'offset': self.offset,
        }


@dataclass
class IOCStats:
    """Statistics for IOCs."""
    total_iocs: int = 0
    active_iocs: int = 0
    expired_iocs: int = 0
    by_indicator_type: Dict[str, int] = field(default_factory=dict)
    by_threat_type: Dict[str, int] = field(default_factory=dict)
    by_severity: Dict[str, int] = field(default_factory=dict)
    by_source: Dict[str, int] = field(default_factory=dict)
    by_tag: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_iocs': self.total_iocs,
            'active_iocs': self.active_iocs,
            'expired_iocs': self.expired_iocs,
            'by_indicator_type': self.by_indicator_type,
            'by_threat_type': self.by_threat_type,
            'by_severity': self.by_severity,
            'by_source': self.by_source,
            'by_tag': self.by_tag,
        }


@dataclass
class IOCConfig:
    """Configuration for IOC manager."""
    default_expiration: int = 30  # days
    max_expiration: int = 365  # days
    cleanup_interval: int = 3600  # seconds
    correlation_threshold: float = 0.7  # Similarity threshold for correlation
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'default_expiration': self.default_expiration,
            'max_expiration': self.max_expiration,
            'cleanup_interval': self.cleanup_interval,
            'correlation_threshold': self.correlation_threshold,
        }


class IOCManager:
    """
    IOC manager for OpenLens.
    
    Provides:
    - IOC storage and retrieval
    - IOC classification
    - IOC correlation
    - IOC enrichment
    - IOC expiration
    - IOC bulk operations
    """
    
    def __init__(self, config: IOCConfig = None, threat_feed_manager=None):
        """
        Initialize the IOC manager.
        
        Args:
            config: IOCConfig instance.
            threat_feed_manager: ThreatFeedManager instance.
        """
        self.config = config or IOCConfig()
        self.threat_feed_manager = threat_feed_manager
        self._iocs: Dict[str, IOC] = {}  # ioc_id -> IOC
        self._indicator_index: Dict[str, str] = {}  # indicator -> ioc_id
        self._lock = threading.Lock()
        self._cleanup_thread = None
        self._running = False
    
    VALID_SEVERITIES = ('low', 'medium', 'high', 'critical')

    def add_ioc(self, indicator: str, indicator_type: str, *,
                threat_type: str = '', confidence: float = 0.8,
                severity: str = 'medium', description: str = '',
                reference: str = '', source: str = '',
                tags: List[str] = None, expires_in: int = None) -> IOC:
        """
        Add a new IOC.

        Everything after indicator_type is keyword-only: a caller once passed
        confidence/severity positionally into the threat_type/confidence slots,
        which stored corrupt IOCs without any error. The `*` turns that mistake
        into a loud TypeError, and the validation below catches the same class
        of shift arriving through dicts (e.g. bulk_add_iocs).

        Args:
            indicator: Indicator value.
            indicator_type: Type of indicator.
            threat_type: Type of threat.
            confidence: Confidence score (0-1).
            severity: Severity level.
            description: Description.
            reference: Reference URL.
            source: Source of the IOC.
            tags: List of tags.
            expires_in: Expiration time in days (None for default).

        Returns:
            IOC object.

        Raises:
            ValueError: If confidence is not a number in [0, 1] or severity is
                not one of low/medium/high/critical.
        """
        if not isinstance(confidence, (int, float)) or isinstance(confidence, bool) \
                or not 0.0 <= float(confidence) <= 1.0:
            raise ValueError(f"confidence must be a number in [0, 1], got {confidence!r}")
        if severity not in self.VALID_SEVERITIES:
            raise ValueError(
                f"severity must be one of {self.VALID_SEVERITIES}, got {severity!r}")
        confidence = float(confidence)

        ioc_id = hashlib.sha256(f"{indicator}:{indicator_type}:{source}".encode()).hexdigest()
        
        now = datetime.utcnow()
        expires_in = expires_in or self.config.default_expiration
        expires_at = now + timedelta(days=expires_in)
        
        ioc = IOC(
            ioc_id=ioc_id,
            indicator=indicator,
            indicator_type=indicator_type,
            threat_type=threat_type,
            confidence=confidence,
            severity=severity,
            description=description,
            reference=reference,
            source=source,
            first_seen=now,
            last_seen=now,
            expires_at=expires_at,
            tags=tags or [],
        )
        
        with self._lock:
            self._iocs[ioc_id] = ioc
            self._indicator_index[indicator.lower()] = ioc_id
        
        return ioc
    
    def add_iocs_from_feed(self, feed_id: str) -> int:
        """
        Add IOCs from a threat feed.
        
        Args:
            feed_id: Feed ID.
            
        Returns:
            Number of IOCs added.
        """
        if not self.threat_feed_manager:
            return 0
        
        # Get feed items
        items = []
        if feed_id in self.threat_feed_manager._feed_items:
            for item_id in self.threat_feed_manager._feed_items[feed_id]:
                if item_id in self.threat_feed_manager._items:
                    items.append(self.threat_feed_manager._items[item_id])
        
        count = 0
        for item in items:
            # Check if IOC already exists
            if not self.get_ioc(item.indicator):
                self.add_ioc(
                    indicator=item.indicator,
                    indicator_type=item.indicator_type,
                    threat_type=item.threat_type,
                    confidence=item.confidence,
                    severity=item.severity,
                    description=item.description,
                    reference=item.reference,
                    source=f"feed:{item.feed_id}",
                    tags=item.tags,
                    expires_in=self.config.default_expiration,
                )
                count += 1
        
        return count
    
    def add_iocs_from_all_feeds(self) -> int:
        """
        Add IOCs from all threat feeds.
        
        Returns:
            Number of IOCs added.
        """
        if not self.threat_feed_manager:
            return 0
        
        count = 0
        for feed in self.threat_feed_manager.list_feeds():
            count += self.add_iocs_from_feed(feed.feed_id)
        
        return count
    
    def get_ioc(self, indicator: str) -> Optional[IOC]:
        """
        Get an IOC by indicator.
        
        Args:
            indicator: Indicator to look up.
            
        Returns:
            IOC or None.
        """
        with self._lock:
            ioc_id = self._indicator_index.get(indicator.lower())
            if ioc_id:
                return self._iocs.get(ioc_id)
            return None
    
    def get_ioc_by_id(self, ioc_id: str) -> Optional[IOC]:
        """
        Get an IOC by ID.
        
        Args:
            ioc_id: IOC ID.
            
        Returns:
            IOC or None.
        """
        with self._lock:
            return self._iocs.get(ioc_id)
    
    def search_iocs(self, query: IOCSearchQuery = None) -> List[IOC]:
        """
        Search IOCs.
        
        Args:
            query: IOCSearchQuery.
            
        Returns:
            List of IOC objects.
        """
        query = query or IOCSearchQuery()
        
        with self._lock:
            results = []
            
            for ioc in self._iocs.values():
                # Filter by indicator
                if query.indicator and query.indicator.lower() not in ioc.indicator.lower():
                    continue
                
                # Filter by indicator type
                if query.indicator_type and ioc.indicator_type != query.indicator_type:
                    continue
                
                # Filter by threat type
                if query.threat_type and ioc.threat_type != query.threat_type:
                    continue
                
                # Filter by severity
                if query.severity and ioc.severity != query.severity:
                    continue
                
                # Filter by source
                if query.source and ioc.source != query.source:
                    continue
                
                # Filter by tags
                if query.tags:
                    if not any(tag in ioc.tags for tag in query.tags):
                        continue
                
                # Filter by confidence
                if ioc.confidence < query.min_confidence:
                    continue
                
                # Filter by active status
                if query.is_active and ioc.is_expired():
                    continue
                
                results.append(ioc)
            
            # Apply limit and offset
            return results[query.offset:query.offset + query.limit]
    
    def update_ioc(self, ioc_id: str, **kwargs) -> bool:
        """
        Update an IOC.
        
        Args:
            ioc_id: IOC ID.
            **kwargs: Fields to update.
            
        Returns:
            True if updated.
        """
        with self._lock:
            if ioc_id not in self._iocs:
                return False
            
            ioc = self._iocs[ioc_id]
            
            for key, value in kwargs.items():
                if hasattr(ioc, key):
                    setattr(ioc, key, value)
            
            # Update last_seen if any field is updated
            if kwargs:
                ioc.last_seen = datetime.utcnow()
            
            return True
    
    def delete_ioc(self, ioc_id: str) -> bool:
        """
        Delete an IOC.
        
        Args:
            ioc_id: IOC ID.
            
        Returns:
            True if deleted.
        """
        with self._lock:
            if ioc_id not in self._iocs:
                return False
            
            ioc = self._iocs[ioc_id]
            
            # Remove from indicator index
            if ioc.indicator.lower() in self._indicator_index:
                del self._indicator_index[ioc.indicator.lower()]
            
            # Remove from related IOCs
            for related_ioc_id in ioc.related_iocs:
                related_ioc = self._iocs.get(related_ioc_id)
                if related_ioc and ioc_id in related_ioc.related_iocs:
                    related_ioc.related_iocs.remove(ioc_id)
            
            del self._iocs[ioc_id]
            return True
    
    def delete_expired_iocs(self) -> int:
        """
        Delete all expired IOCs.
        
        Returns:
            Number of IOCs deleted.
        """
        with self._lock:
            expired_ioc_ids = [ioc_id for ioc_id, ioc in self._iocs.items() if ioc.is_expired()]
            
            for ioc_id in expired_ioc_ids:
                self.delete_ioc(ioc_id)
            
            return len(expired_ioc_ids)
    
    def list_iocs(self, ioc_type: str = None, severity: str = None,
                  limit: int = 100, offset: int = 0) -> List[IOC]:
        """
        List IOCs, optionally filtered. Thin wrapper over search_iocs.

        Args:
            ioc_type: Filter by indicator type.
            severity: Filter by severity.
            limit: Maximum number of results.
            offset: Result offset for pagination.

        Returns:
            List of IOC objects.
        """
        return self.search_iocs(IOCSearchQuery(
            indicator_type=ioc_type,
            severity=severity,
            limit=limit,
            offset=offset,
        ))

    def find_correlations(self, ioc_id: str, threshold: float = None) -> List[Dict[str, Any]]:
        """
        Correlated IOCs for an IOC, serialised. Thin wrapper over correlate_iocs.

        Args:
            ioc_id: IOC ID.
            threshold: Similarity threshold (None for config default).

        Returns:
            List of IOC dictionaries.
        """
        return [ioc.to_dict() for ioc in self.correlate_iocs(ioc_id, threshold)]

    def correlate_iocs(self, ioc_id: str, threshold: float = None) -> List[IOC]:
        """
        Find IOCs correlated with a given IOC.
        
        Args:
            ioc_id: IOC ID.
            threshold: Similarity threshold (None for config default).
            
        Returns:
            List of correlated IOC objects.
        """
        threshold = threshold or self.config.correlation_threshold
        
        ioc = self.get_ioc_by_id(ioc_id)
        if not ioc:
            return []
        
        # Find IOCs with the same indicator type
        same_type_iocs = [
            other_ioc for other_ioc in self._iocs.values()
            if other_ioc.ioc_id != ioc_id and other_ioc.indicator_type == ioc.indicator_type
        ]
        
        # Find IOCs with the same threat type
        same_threat_iocs = [
            other_ioc for other_ioc in self._iocs.values()
            if other_ioc.ioc_id != ioc_id and other_ioc.threat_type == ioc.threat_type
        ]
        
        # Find IOCs with the same source
        same_source_iocs = [
            other_ioc for other_ioc in self._iocs.values()
            if other_ioc.ioc_id != ioc_id and other_ioc.source == ioc.source
        ]
        
        # Combine and deduplicate by id (IOC is a mutable dataclass and so is
        # not hashable - set() on the objects raises TypeError).
        _seen: Dict[str, Any] = {}
        for candidate in same_type_iocs + same_threat_iocs + same_source_iocs:
            _seen.setdefault(candidate.ioc_id, candidate)
        correlated_iocs = list(_seen.values())
        
        # Calculate similarity scores and filter by threshold
        results = []
        for other_ioc in correlated_iocs:
            similarity = self._calculate_similarity(ioc, other_ioc)
            if similarity >= threshold:
                results.append(other_ioc)
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: self._calculate_similarity(ioc, x), reverse=True)
        
        return results
    
    def _calculate_similarity(self, ioc1: IOC, ioc2: IOC) -> float:
        """Calculate similarity between two IOCs."""
        score = 0.0
        
        # Same indicator type
        if ioc1.indicator_type == ioc2.indicator_type:
            score += 0.3
        
        # Same threat type
        if ioc1.threat_type == ioc2.threat_type:
            score += 0.2
        
        # Same source
        if ioc1.source == ioc2.source:
            score += 0.1
        
        # Common tags
        common_tags = set(ioc1.tags) & set(ioc2.tags)
        if common_tags:
            score += 0.1 * (len(common_tags) / max(len(ioc1.tags), len(ioc2.tags), 1))
        
        # Similar confidence
        confidence_diff = abs(ioc1.confidence - ioc2.confidence)
        score += 0.1 * (1 - confidence_diff)
        
        # Similar severity
        severity_scores = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        severity1 = severity_scores.get(ioc1.severity, 0)
        severity2 = severity_scores.get(ioc2.severity, 0)
        severity_diff = abs(severity1 - severity2) / 4
        score += 0.2 * (1 - severity_diff)
        
        return min(score, 1.0)
    
    def relate_iocs(self, ioc_id1: str, ioc_id2: str) -> bool:
        """
        Relate two IOCs.
        
        Args:
            ioc_id1: First IOC ID.
            ioc_id2: Second IOC ID.
            
        Returns:
            True if related.
        """
        with self._lock:
            if ioc_id1 not in self._iocs or ioc_id2 not in self._iocs:
                return False
            
            ioc1 = self._iocs[ioc_id1]
            ioc2 = self._iocs[ioc_id2]
            
            if ioc_id2 not in ioc1.related_iocs:
                ioc1.related_iocs.append(ioc_id2)
            
            if ioc_id1 not in ioc2.related_iocs:
                ioc2.related_iocs.append(ioc_id1)
            
            return True
    
    def unrelate_iocs(self, ioc_id1: str, ioc_id2: str) -> bool:
        """
        Unrelate two IOCs.
        
        Args:
            ioc_id1: First IOC ID.
            ioc_id2: Second IOC ID.
            
        Returns:
            True if unrelated.
        """
        with self._lock:
            if ioc_id1 not in self._iocs or ioc_id2 not in self._iocs:
                return False
            
            ioc1 = self._iocs[ioc_id1]
            ioc2 = self._iocs[ioc_id2]
            
            if ioc_id2 in ioc1.related_iocs:
                ioc1.related_iocs.remove(ioc_id2)
            
            if ioc_id1 in ioc2.related_iocs:
                ioc2.related_iocs.remove(ioc_id1)
            
            return True
    
    def get_related_iocs(self, ioc_id: str) -> List[IOC]:
        """
        Get all IOCs related to a given IOC.
        
        Args:
            ioc_id: IOC ID.
            
        Returns:
            List of related IOC objects.
        """
        ioc = self.get_ioc_by_id(ioc_id)
        if not ioc:
            return []
        
        with self._lock:
            return [self._iocs[related_id] for related_id in ioc.related_iocs 
                    if related_id in self._iocs]
    
    def enrich_ioc(self, ioc_id: str) -> bool:
        """
        Enrich an IOC with additional information.
        
        Args:
            ioc_id: IOC ID.
            
        Returns:
            True if enriched.
        """
        ioc = self.get_ioc_by_id(ioc_id)
        if not ioc:
            return False
        
        # In a real implementation, this would query external services
        # For now, just update the last_seen timestamp
        ioc.last_seen = datetime.utcnow()
        
        # Add some metadata
        ioc.metadata['enriched'] = True
        ioc.metadata['enriched_at'] = datetime.utcnow().isoformat()
        
        return True
    
    def bulk_add_iocs(self, iocs: List[Dict[str, Any]]) -> int:
        """
        Add multiple IOCs in bulk.
        
        Args:
            iocs: List of IOC dictionaries.
            
        Returns:
            Number of IOCs added.
        """
        count = 0
        
        for ioc_data in iocs:
            # Check if IOC already exists
            if not self.get_ioc(ioc_data.get('indicator', '')):
                ioc = self.add_ioc(
                    indicator=ioc_data.get('indicator', ''),
                    indicator_type=ioc_data.get('indicator_type', ''),
                    threat_type=ioc_data.get('threat_type', ''),
                    confidence=ioc_data.get('confidence', 0.8),
                    severity=ioc_data.get('severity', 'medium'),
                    description=ioc_data.get('description', ''),
                    reference=ioc_data.get('reference', ''),
                    source=ioc_data.get('source', ''),
                    tags=ioc_data.get('tags', []),
                    expires_in=ioc_data.get('expires_in'),
                )
                count += 1
        
        return count
    
    def bulk_delete_iocs(self, query: IOCSearchQuery = None) -> int:
        """
        Delete multiple IOCs in bulk.
        
        Args:
            query: IOCSearchQuery to select IOCs to delete.
            
        Returns:
            Number of IOCs deleted.
        """
        iocs = self.search_iocs(query)
        count = 0
        
        for ioc in iocs:
            if self.delete_ioc(ioc.ioc_id):
                count += 1
        
        return count
    
    def get_stats(self) -> IOCStats:
        """
        Get IOC statistics.
        
        Returns:
            IOCStats.
        """
        with self._lock:
            stats = IOCStats()
            
            stats.total_iocs = len(self._iocs)
            
            for ioc in self._iocs.values():
                if ioc.is_expired():
                    stats.expired_iocs += 1
                else:
                    stats.active_iocs += 1
                
                stats.by_indicator_type[ioc.indicator_type] = stats.by_indicator_type.get(ioc.indicator_type, 0) + 1
                stats.by_threat_type[ioc.threat_type] = stats.by_threat_type.get(ioc.threat_type, 0) + 1
                stats.by_severity[ioc.severity] = stats.by_severity.get(ioc.severity, 0) + 1
                stats.by_source[ioc.source] = stats.by_source.get(ioc.source, 0) + 1
                
                for tag in ioc.tags:
                    stats.by_tag[tag] = stats.by_tag.get(tag, 0) + 1
            
            return stats
    
    def start_cleanup_thread(self, interval: int = None):
        """
        Start a background thread for cleanup.
        
        Args:
            interval: Cleanup interval in seconds (None for config default).
        """
        if self._running:
            return
        
        interval = interval or self.config.cleanup_interval
        
        def cleanup_loop():
            while self._running:
                self.delete_expired_iocs()
                time.sleep(interval)
        
        self._cleanup_thread = threading.Thread(target=cleanup_loop, daemon=True)
        self._running = True
        self._cleanup_thread.start()
    
    def stop_cleanup_thread(self):
        """Stop the cleanup thread."""
        self._running = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5)
            self._cleanup_thread = None
    
    def export_to_json(self) -> str:
        """
        Export IOC data to JSON.
        
        Returns:
            JSON string.
        """
        data = {
            'iocs': [i.to_dict() for i in self._iocs.values()],
            'config': self.config.to_dict(),
        }
        
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: str) -> bool:
        """
        Import IOC data from JSON.
        
        Args:
            json_data: JSON string.
            
        Returns:
            True if imported.
        """
        try:
            data = json.loads(json_data)
            
            # Import IOCs
            self._iocs = {}
            self._indicator_index = {}
            for ioc_data in data.get('iocs', []):
                ioc = IOC(
                    ioc_id=ioc_data['ioc_id'],
                    indicator=ioc_data['indicator'],
                    indicator_type=ioc_data['indicator_type'],
                    threat_type=ioc_data.get('threat_type', ''),
                    confidence=ioc_data.get('confidence', 0.0),
                    severity=ioc_data.get('severity', 'medium'),
                    description=ioc_data.get('description', ''),
                    reference=ioc_data.get('reference', ''),
                    source=ioc_data.get('source', ''),
                    first_seen=datetime.fromisoformat(ioc_data['first_seen']) if ioc_data.get('first_seen') else None,
                    last_seen=datetime.fromisoformat(ioc_data['last_seen']) if ioc_data.get('last_seen') else None,
                    expires_at=datetime.fromisoformat(ioc_data['expires_at']) if ioc_data.get('expires_at') else None,
                    tags=ioc_data.get('tags', []),
                    related_iocs=ioc_data.get('related_iocs', []),
                    metadata=ioc_data.get('metadata', {}),
                )
                self._iocs[ioc.ioc_id] = ioc
                self._indicator_index[ioc.indicator.lower()] = ioc.ioc_id
            
            # Import config
            config_data = data.get('config', {})
            self.config = IOCConfig(
                default_expiration=config_data.get('default_expiration', 30),
                max_expiration=config_data.get('max_expiration', 365),
                cleanup_interval=config_data.get('cleanup_interval', 3600),
                correlation_threshold=config_data.get('correlation_threshold', 0.7),
            )
            
            return True
        
        except Exception as e:
            print(f"Error importing IOC data: {e}")
            return False


# Global IOC manager instance
ioc_manager = IOCManager()
