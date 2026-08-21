"""
Threat Analyzer for OpenLens

Provides threat analysis capabilities:
- IOC analysis
- Threat scoring
- Threat correlation
- Anomaly detection
- Threat context enrichment
- Threat timeline analysis
"""

import time
import json
import hashlib
import threading
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

from .ioc_manager import IOC


@dataclass
class ThreatAnalysis:
    """Represents a threat analysis."""
    analysis_id: str
    ioc_id: str
    indicator: str
    indicator_type: str
    threat_score: float = 0.0
    confidence: float = 0.0
    severity: str = 'medium'
    threat_types: List[str] = field(default_factory=list)
    related_iocs: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    findings: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'analysis_id': self.analysis_id,
            'ioc_id': self.ioc_id,
            'indicator': self.indicator,
            'indicator_type': self.indicator_type,
            'threat_score': self.threat_score,
            'confidence': self.confidence,
            'severity': self.severity,
            'threat_types': self.threat_types,
            'related_iocs': self.related_iocs,
            'context': self.context,
            'findings': self.findings,
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat(),
        }


@dataclass
class ThreatScore:
    """Represents a threat score."""
    indicator: str
    indicator_type: str
    score: float = 0.0
    severity: str = 'medium'
    factors: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'indicator': self.indicator,
            'indicator_type': self.indicator_type,
            'score': self.score,
            'severity': self.severity,
            'factors': self.factors,
        }


@dataclass
class ThreatCorrelation:
    """Represents a threat correlation."""
    correlation_id: str
    ioc_ids: List[str] = field(default_factory=list)
    correlation_score: float = 0.0
    correlation_type: str = ''  # temporal, contextual, behavioral
    description: str = ''
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'correlation_id': self.correlation_id,
            'ioc_ids': self.ioc_ids,
            'correlation_score': self.correlation_score,
            'correlation_type': self.correlation_type,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
        }


@dataclass
class ThreatAnalysisConfig:
    """Configuration for threat analyzer."""
    min_score: float = 0.0
    max_score: float = 100.0
    severity_thresholds: Dict[str, float] = field(default_factory=lambda: {
        'low': 25.0,
        'medium': 50.0,
        'high': 75.0,
        'critical': 90.0,
    })
    correlation_threshold: float = 0.7
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'min_score': self.min_score,
            'max_score': self.max_score,
            'severity_thresholds': self.severity_thresholds,
            'correlation_threshold': self.correlation_threshold,
        }


class ThreatAnalyzer:
    """
    Threat analyzer for OpenLens.
    
    Provides:
    - IOC analysis
    - Threat scoring
    - Threat correlation
    - Anomaly detection
    - Threat context enrichment
    - Threat timeline analysis
    """
    
    def __init__(self, config: ThreatAnalysisConfig = None, 
                 ioc_manager=None, graph_engine=None):
        """
        Initialize the threat analyzer.
        
        Args:
            config: ThreatAnalysisConfig instance.
            ioc_manager: IOCManager instance.
            graph_engine: GraphEngine instance.
        """
        self.config = config or ThreatAnalysisConfig()
        self.ioc_manager = ioc_manager
        self.graph_engine = graph_engine
        self._analyses: Dict[str, ThreatAnalysis] = {}
        self._scores: Dict[str, ThreatScore] = {}
        self._correlations: Dict[str, ThreatCorrelation] = {}
        self._lock = threading.Lock()
    
    def analyze_ioc(self, ioc_id: str) -> Optional[ThreatAnalysis]:
        """
        Analyze an IOC.
        
        Args:
            ioc_id: IOC ID.
            
        Returns:
            ThreatAnalysis or None.
        """
        if not self.ioc_manager:
            return None
        
        ioc = self.ioc_manager.get_ioc_by_id(ioc_id)
        if not ioc:
            return None
        
        analysis_id = f"analysis_{ioc_id}_{int(time.time())}"
        
        # Calculate threat score
        threat_score = self.calculate_threat_score(ioc)
        
        # Determine severity
        severity = self._determine_severity(threat_score.score)
        
        # Find related IOCs
        related_iocs = self.ioc_manager.correlate_iocs(ioc_id)
        related_ioc_ids = [ioc.ioc_id for ioc in related_iocs]
        
        # Find threat types
        threat_types = self._identify_threat_types(ioc, related_iocs)
        
        # Generate findings
        findings = self._generate_findings(ioc, related_iocs, threat_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(ioc, threat_score, findings)
        
        # Get context
        context = self._get_context(ioc)
        
        analysis = ThreatAnalysis(
            analysis_id=analysis_id,
            ioc_id=ioc_id,
            indicator=ioc.indicator,
            indicator_type=ioc.indicator_type,
            threat_score=threat_score.score,
            confidence=threat_score.factors.get('confidence', ioc.confidence),
            severity=severity,
            threat_types=threat_types,
            related_iocs=related_ioc_ids,
            context=context,
            findings=findings,
            recommendations=recommendations,
        )
        
        with self._lock:
            self._analyses[analysis_id] = analysis
            self._scores[ioc_id] = threat_score
        
        return analysis
    
    def calculate_threat_score(self, ioc: IOC) -> ThreatScore:
        """
        Calculate a threat score for an IOC.
        
        Args:
            ioc: IOC object.
            
        Returns:
            ThreatScore.
        """
        factors = {}
        
        # Base score from confidence
        factors['confidence'] = ioc.confidence
        
        # Severity factor
        severity_scores = {'low': 0.25, 'medium': 0.5, 'high': 0.75, 'critical': 1.0}
        factors['severity'] = severity_scores.get(ioc.severity, 0.5)
        
        # Threat type factor
        threat_type_scores = {
            'malware': 0.9,
            'phishing': 0.8,
            'botnet': 0.8,
            'c2': 0.9,
            'exploit': 0.8,
            'ransomware': 1.0,
            'spyware': 0.7,
            'trojan': 0.8,
        }
        factors['threat_type'] = threat_type_scores.get(ioc.threat_type.lower(), 0.5)
        
        # Indicator type factor
        indicator_type_scores = {
            'ip': 0.8,
            'domain': 0.7,
            'url': 0.6,
            'hash': 0.9,
            'email': 0.5,
        }
        factors['indicator_type'] = indicator_type_scores.get(ioc.indicator_type.lower(), 0.5)
        
        # Source factor (trusted sources get higher scores)
        trusted_sources = ['feed:abuse_ch', 'feed:alienvault_otx', 'feed:fireeye']
        factors['source'] = 0.9 if ioc.source in trusted_sources else 0.7
        
        # Age factor (newer IOCs get higher scores)
        if ioc.last_seen:
            age_hours = (datetime.utcnow() - ioc.last_seen).total_seconds() / 3600
            factors['age'] = max(0, 1 - (age_hours / 168))  # 1 week = 168 hours
        else:
            factors['age'] = 0.5
        
        # Calculate weighted score
        weights = {
            'confidence': 0.2,
            'severity': 0.2,
            'threat_type': 0.2,
            'indicator_type': 0.1,
            'source': 0.1,
            'age': 0.2,
        }
        
        score = sum(factors.get(key, 0) * weights.get(key, 0) for key in factors)
        
        # Scale to 0-100
        score = score * 100
        
        # Determine severity based on score
        severity = self._determine_severity(score)
        
        return ThreatScore(
            indicator=ioc.indicator,
            indicator_type=ioc.indicator_type,
            score=score,
            severity=severity,
            factors=factors,
        )
    
    def _determine_severity(self, score: float) -> str:
        """Determine severity based on score."""
        for severity, threshold in sorted(self.config.severity_thresholds.items(), key=lambda x: x[1], reverse=True):
            if score >= threshold:
                return severity
        return 'low'
    
    def _identify_threat_types(self, ioc: IOC, related_iocs: List[IOC]) -> List[str]:
        """Identify threat types for an IOC."""
        threat_types = set()
        
        # Add the IOC's own threat type
        if ioc.threat_type:
            threat_types.add(ioc.threat_type)
        
        # Add threat types from related IOCs
        for related_ioc in related_iocs:
            if related_ioc.threat_type:
                threat_types.add(related_ioc.threat_type)
        
        # Add inferred threat types based on indicator type
        if ioc.indicator_type == 'ip':
            threat_types.add('c2')
        elif ioc.indicator_type == 'domain':
            threat_types.add('malware')
            threat_types.add('phishing')
        elif ioc.indicator_type == 'url':
            threat_types.add('phishing')
            threat_types.add('exploit')
        elif ioc.indicator_type == 'hash':
            threat_types.add('malware')
        
        return list(threat_types)
    
    def _generate_findings(self, ioc: IOC, related_iocs: List[IOC], 
                          threat_score: ThreatScore) -> List[Dict[str, Any]]:
        """Generate findings for an IOC."""
        findings = []
        
        # Check if IOC is in any threat feeds
        if self.ioc_manager and self.ioc_manager.threat_feed_manager:
            feed_item = self.ioc_manager.threat_feed_manager.get_item(ioc.indicator)
            if feed_item:
                findings.append({
                    'type': 'threat_feed_match',
                    'description': f"IOC found in threat feed: {feed_item.feed_id}",
                    'severity': 'medium',
                    'details': {
                        'feed_id': feed_item.feed_id,
                        'feed_name': feed_item.feed_id,  # Would be feed.name in real implementation
                        'threat_type': feed_item.threat_type,
                        'confidence': feed_item.confidence,
                    },
                })
        
        # Check for related IOCs
        if related_iocs:
            findings.append({
                'type': 'related_iocs',
                'description': f"Found {len(related_iocs)} related IOCs",
                'severity': 'low',
                'details': {
                    'count': len(related_iocs),
                    'related_ioc_ids': [ioc.ioc_id for ioc in related_iocs],
                },
            })
        
        # Check threat score
        if threat_score.score >= 75:
            findings.append({
                'type': 'high_threat_score',
                'description': f"High threat score: {threat_score.score:.1f}",
                'severity': 'high',
                'details': {
                    'score': threat_score.score,
                    'factors': threat_score.factors,
                },
            })
        
        # Check if IOC is expired
        if ioc.is_expired():
            findings.append({
                'type': 'expired_ioc',
                'description': 'IOC has expired',
                'severity': 'low',
                'details': {
                    'expires_at': ioc.expires_at.isoformat() if ioc.expires_at else None,
                },
            })
        
        return findings
    
    def _generate_recommendations(self, ioc: IOC, threat_score: ThreatScore, 
                                  findings: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations for an IOC."""
        recommendations = []
        
        # General recommendations based on indicator type
        if ioc.indicator_type == 'ip':
            recommendations.append(f"Block IP address {ioc.indicator} at the firewall")
            recommendations.append(f"Investigate network connections to {ioc.indicator}")
        elif ioc.indicator_type == 'domain':
            recommendations.append(f"Block domain {ioc.indicator} at the DNS level")
            recommendations.append(f"Investigate DNS queries for {ioc.indicator}")
        elif ioc.indicator_type == 'url':
            recommendations.append(f"Block URL {ioc.indicator} at the proxy level")
            recommendations.append(f"Investigate web requests to {ioc.indicator}")
        elif ioc.indicator_type == 'hash':
            recommendations.append(f"Scan for files with hash {ioc.indicator}")
            recommendations.append(f"Quarantine any files matching hash {ioc.indicator}")
        elif ioc.indicator_type == 'email':
            recommendations.append(f"Monitor for emails from {ioc.indicator}")
            recommendations.append(f"Investigate any communications with {ioc.indicator}")
        
        # Recommendations based on threat score
        if threat_score.score >= 90:
            recommendations.append("Immediately isolate affected systems")
            recommendations.append("Initiate incident response procedures")
        elif threat_score.score >= 75:
            recommendations.append("Increase monitoring for this indicator")
            recommendations.append("Review related security logs")
        
        # Recommendations based on findings
        for finding in findings:
            if finding['type'] == 'threat_feed_match':
                recommendations.append(f"Review threat intelligence for {finding['details']['feed_id']}")
            elif finding['type'] == 'related_iocs':
                recommendations.append(f"Investigate all {finding['details']['count']} related IOCs")
        
        return recommendations
    
    def _get_context(self, ioc: IOC) -> Dict[str, Any]:
        """Get context for an IOC."""
        context = {
            'indicator': ioc.indicator,
            'indicator_type': ioc.indicator_type,
            'threat_type': ioc.threat_type,
            'severity': ioc.severity,
            'confidence': ioc.confidence,
            'source': ioc.source,
            'first_seen': ioc.first_seen.isoformat() if ioc.first_seen else None,
            'last_seen': ioc.last_seen.isoformat() if ioc.last_seen else None,
        }
        
        # Add graph context if available
        if self.graph_engine:
            graph_context = self._get_graph_context(ioc)
            if graph_context:
                context['graph'] = graph_context
        
        return context
    
    def _get_graph_context(self, ioc: IOC) -> Dict[str, Any]:
        """Get graph context for an IOC."""
        try:
            # Search for the indicator in the graph
            query = f"MATCH (n) WHERE n.indicator = '{ioc.indicator}' RETURN n"
            result = self.graph_engine.execute_query(query)
            
            if result and result.nodes:
                return {
                    'nodes': [n.to_dict() for n in result.nodes],
                    'relationships': [r.to_dict() for r in result.relationships],
                }
            
            # Search for nodes with the indicator in properties
            query = f"MATCH (n) WHERE ANY(prop IN keys(n) WHERE toLower(toString(n[prop])) CONTAINS toLower('{ioc.indicator}')) RETURN n"
            result = self.graph_engine.execute_query(query)
            
            if result and result.nodes:
                return {
                    'nodes': [n.to_dict() for n in result.nodes],
                    'relationships': [r.to_dict() for r in result.relationships],
                }
        
        except Exception as e:
            print(f"Error getting graph context: {e}")
        
        return {}
    
    def correlate_threats(self, ioc_ids: List[str]) -> List[ThreatCorrelation]:
        """
        Correlate multiple IOCs.
        
        Args:
            ioc_ids: List of IOC IDs.
            
        Returns:
            List of ThreatCorrelation objects.
        """
        if not self.ioc_manager:
            return []
        
        correlations = []
        
        # Get all IOCs
        iocs = [self.ioc_manager.get_ioc_by_id(ioc_id) for ioc_id in ioc_ids]
        iocs = [ioc for ioc in iocs if ioc]
        
        if len(iocs) < 2:
            return []
        
        # Find all pairs of IOCs
        for i in range(len(iocs)):
            for j in range(i + 1, len(iocs)):
                ioc1 = iocs[i]
                ioc2 = iocs[j]
                
                # Calculate correlation score
                score = self._calculate_correlation_score(ioc1, ioc2)
                
                if score >= self.config.correlation_threshold:
                    # Determine correlation type
                    correlation_type = self._determine_correlation_type(ioc1, ioc2)
                    
                    correlation_id = hashlib.sha256(f"{ioc1.ioc_id}:{ioc2.ioc_id}".encode()).hexdigest()
                    
                    correlation = ThreatCorrelation(
                        correlation_id=correlation_id,
                        ioc_ids=[ioc1.ioc_id, ioc2.ioc_id],
                        correlation_score=score,
                        correlation_type=correlation_type,
                        description=f"Correlation between {ioc1.indicator} and {ioc2.indicator}",
                    )
                    
                    correlations.append(correlation)
        
        # Sort by score (descending)
        correlations.sort(key=lambda x: x.correlation_score, reverse=True)
        
        with self._lock:
            for correlation in correlations:
                self._correlations[correlation.correlation_id] = correlation
        
        return correlations
    
    def _calculate_correlation_score(self, ioc1: IOC, ioc2: IOC) -> float:
        """Calculate correlation score between two IOCs."""
        score = 0.0
        
        # Same indicator type
        if ioc1.indicator_type == ioc2.indicator_type:
            score += 0.2
        
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
        score += 0.1 * (1 - severity_diff)
        
        # Temporal proximity
        if ioc1.last_seen and ioc2.last_seen:
            time_diff = abs((ioc1.last_seen - ioc2.last_seen).total_seconds())
            # Normalize time difference (1 day = 86400 seconds)
            time_diff_normalized = min(time_diff / 86400, 1.0)
            score += 0.2 * (1 - time_diff_normalized)
        
        return min(score, 1.0)
    
    def _determine_correlation_type(self, ioc1: IOC, ioc2: IOC) -> str:
        """Determine the type of correlation."""
        if ioc1.indicator_type == ioc2.indicator_type:
            if ioc1.threat_type == ioc2.threat_type:
                return 'behavioral'
            else:
                return 'contextual'
        else:
            return 'temporal'
    
    def get_threat_timeline(self, ioc_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get a threat timeline for an IOC.
        
        Args:
            ioc_id: IOC ID.
            days: Number of days to look back.
            
        Returns:
            List of timeline events.
        """
        if not self.ioc_manager:
            return []
        
        ioc = self.ioc_manager.get_ioc_by_id(ioc_id)
        if not ioc:
            return []
        
        timeline = []
        
        # Add IOC creation event
        if ioc.first_seen:
            timeline.append({
                'timestamp': ioc.first_seen.isoformat(),
                'event_type': 'ioc_created',
                'description': f"IOC {ioc.indicator} first seen",
                'severity': ioc.severity,
            })
        
        # Add IOC update events (would need audit logs in real implementation)
        if ioc.last_seen and ioc.last_seen != ioc.first_seen:
            timeline.append({
                'timestamp': ioc.last_seen.isoformat(),
                'event_type': 'ioc_updated',
                'description': f"IOC {ioc.indicator} last seen",
                'severity': ioc.severity,
            })
        
        # Add related IOC events
        related_iocs = self.ioc_manager.get_related_iocs(ioc_id)
        for related_ioc in related_iocs:
            if related_ioc.first_seen:
                timeline.append({
                    'timestamp': related_ioc.first_seen.isoformat(),
                    'event_type': 'related_ioc_created',
                    'description': f"Related IOC {related_ioc.indicator} first seen",
                    'severity': related_ioc.severity,
                    'related_ioc_id': related_ioc.ioc_id,
                })
        
        # Sort by timestamp
        timeline.sort(key=lambda x: x['timestamp'])
        
        # Filter by time range
        cutoff = datetime.utcnow() - timedelta(days=days)
        filtered_timeline = [
            event for event in timeline
            if datetime.fromisoformat(event['timestamp']) >= cutoff
        ]
        
        return filtered_timeline
    
    def get_analysis(self, analysis_id: str) -> Optional[ThreatAnalysis]:
        """
        Get a threat analysis.
        
        Args:
            analysis_id: Analysis ID.
            
        Returns:
            ThreatAnalysis or None.
        """
        with self._lock:
            return self._analyses.get(analysis_id)
    
    def get_analyses(self, ioc_id: str = None, limit: int = 100) -> List[ThreatAnalysis]:
        """
        Get threat analyses.
        
        Args:
            ioc_id: Filter by IOC ID (None for all).
            limit: Maximum number of results.
            
        Returns:
            List of ThreatAnalysis objects.
        """
        with self._lock:
            if ioc_id:
                return [a for a in self._analyses.values() if a.ioc_id == ioc_id][:limit]
            return list(self._analyses.values())[:limit]
    
    def calculate_threat_scores(self, ioc_ids: List[str] = None,
                                limit: int = 100) -> Dict[str, Dict[str, Any]]:
        """
        Batch threat scores, keyed by ioc_id.

        Args:
            ioc_ids: Explicit IOC ids (None to score every stored IOC).
            limit: Cap on how many IOCs are scored, so this cannot become an
                unbounded O(n) endpoint.

        Returns:
            {ioc_id: ThreatScore.to_dict()} for each scored IOC.
        """
        if not self.ioc_manager:
            return {}

        if ioc_ids:
            iocs = [self.ioc_manager.get_ioc_by_id(i) for i in ioc_ids]
            iocs = [ioc for ioc in iocs if ioc]
        else:
            iocs = self.ioc_manager.search_iocs()

        scores: Dict[str, Dict[str, Any]] = {}
        for ioc in iocs[:max(0, limit)]:
            score = self.calculate_threat_score(ioc)
            if score:
                scores[ioc.ioc_id] = score.to_dict()
        return scores

    def get_threat_score(self, ioc_id: str) -> Optional[ThreatScore]:
        """
        Get a threat score.
        
        Args:
            ioc_id: IOC ID.
            
        Returns:
            ThreatScore or None.
        """
        with self._lock:
            return self._scores.get(ioc_id)
    
    def get_correlation(self, correlation_id: str) -> Optional[ThreatCorrelation]:
        """
        Get a threat correlation.
        
        Args:
            correlation_id: Correlation ID.
            
        Returns:
            ThreatCorrelation or None.
        """
        with self._lock:
            return self._correlations.get(correlation_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get threat analysis statistics.
        
        Returns:
            Dictionary with statistics.
        """
        with self._lock:
            stats = {
                'total_analyses': len(self._analyses),
                'total_scores': len(self._scores),
                'total_correlations': len(self._correlations),
                'by_severity': defaultdict(int),
                'by_indicator_type': defaultdict(int),
                'by_threat_type': defaultdict(int),
            }
            
            for analysis in self._analyses.values():
                stats['by_severity'][analysis.severity] += 1
                stats['by_indicator_type'][analysis.indicator_type] += 1
                for threat_type in analysis.threat_types:
                    stats['by_threat_type'][threat_type] += 1
            
            # Convert defaultdict to dict
            for key in stats:
                if isinstance(stats[key], defaultdict):
                    stats[key] = dict(stats[key])
            
            return stats
    
    def export_to_json(self) -> str:
        """
        Export threat analysis data to JSON.
        
        Returns:
            JSON string.
        """
        data = {
            'analyses': [a.to_dict() for a in self._analyses.values()],
            'scores': [s.to_dict() for s in self._scores.values()],
            'correlations': [c.to_dict() for c in self._correlations.values()],
            'config': self.config.to_dict(),
        }
        
        return json.dumps(data, indent=2)
    
    def import_from_json(self, json_data: str) -> bool:
        """
        Import threat analysis data from JSON.
        
        Args:
            json_data: JSON string.
            
        Returns:
            True if imported.
        """
        try:
            data = json.loads(json_data)
            
            # Import analyses
            self._analyses = {}
            for analysis_data in data.get('analyses', []):
                analysis = ThreatAnalysis(
                    analysis_id=analysis_data['analysis_id'],
                    ioc_id=analysis_data['ioc_id'],
                    indicator=analysis_data['indicator'],
                    indicator_type=analysis_data['indicator_type'],
                    threat_score=analysis_data['threat_score'],
                    confidence=analysis_data['confidence'],
                    severity=analysis_data['severity'],
                    threat_types=analysis_data.get('threat_types', []),
                    related_iocs=analysis_data.get('related_iocs', []),
                    context=analysis_data.get('context', {}),
                    findings=analysis_data.get('findings', []),
                    recommendations=analysis_data.get('recommendations', []),
                    created_at=datetime.fromisoformat(analysis_data['created_at']),
                )
                self._analyses[analysis.analysis_id] = analysis
            
            # Import scores
            self._scores = {}
            for score_data in data.get('scores', []):
                score = ThreatScore(
                    indicator=score_data['indicator'],
                    indicator_type=score_data['indicator_type'],
                    score=score_data['score'],
                    severity=score_data['severity'],
                    factors=score_data.get('factors', {}),
                )
                # Use indicator as key for now
                self._scores[score.indicator] = score
            
            # Import correlations
            self._correlations = {}
            for correlation_data in data.get('correlations', []):
                correlation = ThreatCorrelation(
                    correlation_id=correlation_data['correlation_id'],
                    ioc_ids=correlation_data.get('ioc_ids', []),
                    correlation_score=correlation_data['correlation_score'],
                    correlation_type=correlation_data.get('correlation_type', ''),
                    description=correlation_data.get('description', ''),
                    created_at=datetime.fromisoformat(correlation_data['created_at']),
                )
                self._correlations[correlation.correlation_id] = correlation
            
            # Import config
            config_data = data.get('config', {})
            self.config = ThreatAnalysisConfig(
                min_score=config_data.get('min_score', 0.0),
                max_score=config_data.get('max_score', 100.0),
                severity_thresholds=config_data.get('severity_thresholds', {
                    'low': 25.0,
                    'medium': 50.0,
                    'high': 75.0,
                    'critical': 90.0,
                }),
                correlation_threshold=config_data.get('correlation_threshold', 0.7),
            )
            
            return True
        
        except Exception as e:
            print(f"Error importing threat analysis data: {e}")
            return False


# Global threat analyzer instance
threat_analyzer = ThreatAnalyzer()
