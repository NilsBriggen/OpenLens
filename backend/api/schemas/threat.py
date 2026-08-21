"""Threat-intelligence response models (wire shapes the frontend reads)."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, Field, model_validator

from backend.api.schemas.base import ApiModel


class IOCOut(ApiModel):
    """An Indicator of Compromise as the frontend reads it."""
    id: str = Field(validation_alias=AliasChoices('id', 'ioc_id'))
    value: str = Field(validation_alias=AliasChoices('value', 'indicator'))
    ioc_type: str = Field(validation_alias=AliasChoices('ioc_type', 'indicator_type'))
    threat_type: str = ''
    confidence: float = 0.0
    severity: str = 'medium'
    description: str = ''
    source: str = ''
    tags: List[str] = []
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    related_threats: List[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices('related_threats', 'related_iocs'))


class ThreatFeedOut(ApiModel):
    """A threat feed as the frontend reads it."""
    id: str = Field(validation_alias=AliasChoices('id', 'feed_id'))
    name: str
    feed_type: str = 'ioc'
    enabled: bool = Field(default=True,
                          validation_alias=AliasChoices('enabled', 'is_active'))
    status: str = 'idle'
    ioc_count: int = 0
    frequency: int = Field(default=3600,
                           validation_alias=AliasChoices('frequency', 'update_interval'))
    last_updated: Optional[datetime] = None
    description: str = ''
    url: str = ''

    @model_validator(mode='after')
    def _derive_status(self) -> 'ThreatFeedOut':
        if self.status == 'idle':
            self.status = 'active' if self.enabled else 'disabled'
        return self


class AlertOut(ApiModel):
    """A security alert as the frontend reads it."""
    id: str = Field(validation_alias=AliasChoices('id', 'alert_id'))
    title: str
    description: str = ''
    severity: str = 'medium'
    status: str = 'new'
    ioc_count: int = 0
    indicator: str = ''
    indicator_type: str = ''
    threat_types: List[str] = []
    confidence: float = 0.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    ioc_id: str = Field(default='', exclude=True)

    @model_validator(mode='after')
    def _derive_ioc_count(self) -> 'AlertOut':
        if not self.ioc_count and self.ioc_id:
            self.ioc_count = 1
        return self


class AlertRuleOut(ApiModel):
    """An alerting rule as the frontend reads it."""
    id: str = Field(validation_alias=AliasChoices('id', 'rule_id'))
    name: str
    description: str = ''
    enabled: bool = Field(default=True,
                          validation_alias=AliasChoices('enabled', 'is_enabled'))
    condition: Dict[str, Any] = {}


class ThreatScoreOut(ApiModel):
    """A calculated threat score."""
    ioc_id: str = ''
    indicator: str = ''
    indicator_type: str = ''
    score: float = 0.0
    severity: str = 'medium'
    factors: Dict[str, float] = {}


class ThreatAnalysisOut(ApiModel):
    """A full IOC analysis."""
    id: str = Field(validation_alias=AliasChoices('id', 'analysis_id'))
    ioc_id: str = ''
    indicator: str = ''
    indicator_type: str = ''
    threat_score: float = 0.0
    confidence: float = 0.0
    severity: str = 'medium'
    threat_types: List[str] = []
    related_iocs: List[str] = []
    findings: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    created_at: Optional[datetime] = None


class IOCCorrelationOut(ApiModel):
    """Correlations for one IOC."""
    ioc_id: str
    correlations: List[IOCOut] = []


class HuntOut(ApiModel):
    """A threat hunt with its results."""
    id: str = Field(validation_alias=AliasChoices('id', 'hunt_id'))
    name: str
    hunt_type: str = ''
    status: str = 'pending'
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: List[Dict[str, Any]] = []


class ThreatGraphOut(ApiModel):
    """The threat subgraph."""
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
