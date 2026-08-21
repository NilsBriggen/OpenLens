"""
Threat Intelligence Facade for OpenLens AI

A read-only facade over the threat-intelligence pipeline (IOC manager,
threat analyzer, alert manager, graph engine) for AI-side consumers:
- Indicator assessment
- Graph-node assessment
- Bulk enrichment
- Summary reporting
- Free-text search over IOCs

This module intentionally imports nothing from backend.threat_intelligence at
module level: its collaborators are injected by backend/composition.py, which
keeps the ai <-> threat_intelligence packages cycle-free.

Naming note: the singleton `threat_intelligence` shadows the sibling package
name in `from backend.ai import *` contexts; import the class or access it as
backend.ai.threat_intelligence explicitly.
"""

from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ThreatSummary:
    """Aggregate snapshot of the threat landscape."""
    total_iocs: int = 0
    active_iocs: int = 0
    by_severity: Dict[str, int] = field(default_factory=dict)
    by_indicator_type: Dict[str, int] = field(default_factory=dict)
    total_alerts: int = 0
    open_alerts: int = 0
    generated_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'total_iocs': self.total_iocs,
            'active_iocs': self.active_iocs,
            'by_severity': self.by_severity,
            'by_indicator_type': self.by_indicator_type,
            'total_alerts': self.total_alerts,
            'open_alerts': self.open_alerts,
            'generated_at': self.generated_at.isoformat(),
        }


@dataclass
class ThreatAssessment:
    """Assessment of one entity or indicator."""
    entity_id: str
    entity_type: str = ''
    score: float = 0.0
    severity: str = 'low'
    threat_types: List[str] = field(default_factory=list)
    matched_iocs: List[str] = field(default_factory=list)
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    assessed_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'entity_id': self.entity_id,
            'entity_type': self.entity_type,
            'score': self.score,
            'severity': self.severity,
            'threat_types': self.threat_types,
            'matched_iocs': self.matched_iocs,
            'findings': self.findings,
            'recommendations': self.recommendations,
            'assessed_at': self.assessed_at.isoformat(),
        }


class ThreatIntelligence:
    """
    Read-only threat-intelligence facade.

    Every method degrades to None/empty when its collaborator is unwired,
    never raising on a missing backend.
    """

    _SEVERITY_SCORE = {'low': 25.0, 'medium': 50.0, 'high': 75.0, 'critical': 100.0}

    def __init__(self, ioc_manager=None, threat_analyzer=None,
                 alert_manager=None, graph_engine=None):
        """
        Initialize the facade.

        Args:
            ioc_manager: IOCManager instance.
            threat_analyzer: ThreatAnalyzer instance.
            alert_manager: AlertManager instance.
            graph_engine: GraphEngine instance.
        """
        self.ioc_manager = ioc_manager
        self.threat_analyzer = threat_analyzer
        self.alert_manager = alert_manager
        self.graph_engine = graph_engine

    def assess_indicator(self, indicator: str,
                         indicator_type: str = None) -> Optional[ThreatAssessment]:
        """
        Assess a raw indicator value against the IOC store.

        Returns:
            ThreatAssessment (score 0 when the indicator is unknown), or None
            when the IOC manager is unwired.
        """
        if not self.ioc_manager:
            return None

        ioc = self.ioc_manager.get_ioc(indicator)
        assessment = ThreatAssessment(entity_id=indicator,
                                      entity_type=indicator_type or '')

        if not ioc:
            assessment.findings.append('No matching IOC on record')
            assessment.recommendations.append('Monitor; no action required')
            return assessment

        assessment.entity_type = ioc.indicator_type
        assessment.matched_iocs.append(ioc.ioc_id)
        if ioc.threat_type:
            assessment.threat_types.append(ioc.threat_type)
        assessment.severity = ioc.severity
        base = self._SEVERITY_SCORE.get(ioc.severity, 25.0)
        assessment.score = round(base * float(ioc.confidence), 2)
        assessment.findings.append(
            f'Matches IOC {ioc.ioc_id[:12]} ({ioc.indicator_type}, '
            f'severity {ioc.severity}, confidence {ioc.confidence:.2f})')

        if self.threat_analyzer:
            score = self.threat_analyzer.calculate_threat_score(ioc)
            if score is not None:
                analyzer_score = getattr(score, 'score', None)
                if isinstance(analyzer_score, (int, float)):
                    assessment.score = round(float(analyzer_score), 2)

        if assessment.severity in ('high', 'critical'):
            assessment.recommendations.append('Block the indicator at the perimeter')
            assessment.recommendations.append('Hunt for historical contact with it')
        else:
            assessment.recommendations.append('Add to watchlists')

        return assessment

    def assess_node(self, node_id: str) -> Optional[ThreatAssessment]:
        """
        Assess a graph node by its indicator-bearing properties.

        Returns None when the graph store is unavailable or the node unknown.
        """
        if not self.graph_engine:
            return None

        result = self.graph_engine.execute_query(
            'MATCH (n) WHERE n.id = $id RETURN n', {'id': node_id})
        if not result or not result.nodes:
            return None

        node = result.nodes[0]
        indicator = (node.properties.get('indicator')
                     or node.properties.get('value')
                     or node.properties.get('name'))
        if indicator:
            assessment = self.assess_indicator(str(indicator))
            if assessment:
                assessment.entity_id = node_id
                assessment.entity_type = node.labels[0] if node.labels else 'node'
                return assessment

        return ThreatAssessment(
            entity_id=node_id,
            entity_type=node.labels[0] if node.labels else 'node',
            findings=['Node carries no indicator property'],
        )

    def enrich(self, indicators: List[str]) -> List[ThreatAssessment]:
        """Assess a batch of indicators; unknown ones score 0."""
        assessments = []
        for indicator in indicators:
            assessment = self.assess_indicator(indicator)
            if assessment:
                assessments.append(assessment)
        return assessments

    def get_summary(self) -> ThreatSummary:
        """Aggregate IOC and alert counts."""
        summary = ThreatSummary()

        if self.ioc_manager:
            stats = self.ioc_manager.get_stats()
            summary.total_iocs = getattr(stats, 'total_iocs', 0)
            summary.active_iocs = getattr(stats, 'active_iocs', 0)
            summary.by_severity = dict(getattr(stats, 'by_severity', {}) or {})
            summary.by_indicator_type = dict(getattr(stats, 'by_type', {}) or {})

        if self.alert_manager:
            stats = self.alert_manager.get_stats()
            summary.total_alerts = stats.get('total_alerts', 0)
            by_status = stats.get('by_status', {}) or {}
            summary.open_alerts = sum(
                count for status, count in by_status.items()
                if status in ('new', 'acknowledged', 'investigated'))

        return summary

    def search(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Substring search over stored IOCs."""
        if not self.ioc_manager or not query:
            return []
        needle = query.lower()
        matches = []
        for ioc in self.ioc_manager.search_iocs():
            haystack = ' '.join([
                ioc.indicator, ioc.indicator_type, ioc.threat_type,
                ioc.description, ' '.join(ioc.tags or []),
            ]).lower()
            if needle in haystack:
                matches.append(ioc.to_dict())
                if len(matches) >= limit:
                    break
        return matches


# Global threat intelligence facade instance
threat_intelligence = ThreatIntelligence()
