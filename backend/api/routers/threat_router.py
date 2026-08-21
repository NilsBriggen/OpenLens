"""
Threat Intelligence Router

API endpoints for the Real-Time Threat Intelligence Pipeline. Request bodies
stay snake_case (as the frontend sends them); responses are camelCase via
the schemas.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.api.capabilities import requires
from backend.api.deps import require_permission
from backend.api.errors import FeatureUnavailable
from backend.api.schemas import (
    AlertOut, AlertRuleOut, HuntOut, IOCCorrelationOut, IOCOut, Payload,
    StatusOut, ThreatAnalysisOut, ThreatFeedOut, ThreatGraphOut, ThreatScoreOut,
)
from backend.threat_intelligence import (
    alert_manager, ioc_manager, threat_analyzer, threat_feed_manager,
    threat_graph, threat_hunter, threat_intel_sharing, threat_monitor,
)
from backend.threat_intelligence.ioc_manager import IOCSearchQuery

router = APIRouter()

_READ = require_permission('threat', 'read')
_WRITE = require_permission('threat', 'write')


# Pydantic Models (request side - unchanged wire format)
class IOCCreate(BaseModel):
    value: str
    ioc_type: str  # ip, domain, url, hash, email
    confidence: Optional[float] = 0.8
    severity: Optional[str] = "high"
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class ThreatFeedCreate(BaseModel):
    name: str
    url: str
    feed_type: str  # stix, misp, csv, json, text
    enabled: Optional[bool] = True


class AlertCreate(BaseModel):
    title: str
    description: str = ''
    severity: str = "medium"
    ioc_ids: Optional[List[str]] = None


class ThreatHuntRequest(BaseModel):
    query: str
    method: str = "hypothesis"  # hypothesis, anomaly, ioc, behavioral, pattern


class EnrichmentRequest(BaseModel):
    ioc: str
    ioc_type: str


class CorrelationRequest(BaseModel):
    iocs: List[str]


class StixImportRequest(BaseModel):
    bundle: Dict[str, Any]


def _feed_ioc_count(feed_id: str) -> int:
    """IOCs attributable to a feed (0 when nothing is indexed for it)."""
    try:
        items = getattr(threat_feed_manager, '_feed_items', {}).get(feed_id, [])
        return len(items)
    except Exception:
        return 0


def _feed_out(feed) -> ThreatFeedOut:
    out = ThreatFeedOut.model_validate(feed)
    out.ioc_count = _feed_ioc_count(feed.feed_id)
    return out


# Threat Feeds
@router.get("/feeds", response_model=List[ThreatFeedOut], dependencies=[_READ])
async def list_feeds(feed_type: str = Query(default=None)):
    """List all threat feeds"""
    return [_feed_out(feed) for feed in threat_feed_manager.list_feeds(feed_type)]


@router.post("/feeds", response_model=ThreatFeedOut, dependencies=[_WRITE])
async def add_feed(feed: ThreatFeedCreate):
    """Add a new threat feed"""
    created = threat_feed_manager.create_feed(
        name=feed.name, url=feed.url, feed_type=feed.feed_type,
        enabled=bool(feed.enabled))
    if created is None:
        raise HTTPException(status_code=409, detail='Feed already exists')
    return _feed_out(created)


@router.post("/feeds/{feed_id}/update", response_model=StatusOut,
             dependencies=[_WRITE])
async def update_feed(feed_id: str):
    """Fetch and ingest one feed now"""
    if not threat_feed_manager.get_feed(feed_id):
        raise HTTPException(status_code=404, detail='Feed not found')
    ok = threat_feed_manager.update_feed(feed_id)
    return StatusOut(status='updated' if ok else 'failed')


@router.post("/feeds/update-all", response_model=Payload, dependencies=[_WRITE])
async def update_all_feeds():
    """Fetch and ingest every active feed"""
    return Payload(data=threat_feed_manager.update_all_feeds())


# IOCs
@router.post("/iocs", response_model=IOCOut, dependencies=[_WRITE])
async def create_ioc(ioc: IOCCreate):
    """Create an IOC. All keyword args - the old positional call shifted
    every argument by one and stored corrupt IOCs."""
    try:
        created = ioc_manager.add_ioc(
            ioc.value, ioc.ioc_type,
            confidence=float(ioc.confidence if ioc.confidence is not None else 0.8),
            severity=ioc.severity or 'high',
            description=ioc.description or '',
            tags=ioc.tags,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return created


@router.get("/iocs", response_model=List[IOCOut], dependencies=[_READ])
async def list_iocs(search: str = Query(default=None),
                    type: str = Query(default=None),
                    ioc_type: str = Query(default=None),
                    severity: str = Query(default=None),
                    limit: int = Query(default=100, le=1000)):
    """List/search IOCs"""
    return ioc_manager.search_iocs(IOCSearchQuery(
        indicator=search,
        indicator_type=type or ioc_type,
        severity=severity,
        limit=limit,
    ))


@router.get("/iocs/{ioc_id}", response_model=IOCOut, dependencies=[_READ])
async def get_ioc(ioc_id: str):
    """Get one IOC by id. get_ioc_by_id, not get_ioc - the latter is keyed
    by indicator value and made this endpoint 404 for every id."""
    ioc = ioc_manager.get_ioc_by_id(ioc_id)
    if not ioc:
        raise HTTPException(status_code=404, detail='IOC not found')
    return ioc


@router.post("/iocs/{ioc_id}/correlate", response_model=IOCCorrelationOut,
             dependencies=[_READ])
async def correlate_ioc(ioc_id: str, threshold: float = Query(default=None)):
    """Correlated IOCs for an IOC"""
    if not ioc_manager.get_ioc_by_id(ioc_id):
        raise HTTPException(status_code=404, detail='IOC not found')
    correlated = ioc_manager.correlate_iocs(ioc_id, threshold)
    return IOCCorrelationOut(ioc_id=ioc_id, correlations=correlated)


@router.post("/analyze/{ioc_id}", response_model=ThreatAnalysisOut,
             dependencies=[_READ])
async def analyze_ioc(ioc_id: str):
    """Full analysis of one IOC"""
    analysis = threat_analyzer.analyze_ioc(ioc_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail='IOC not found or analysis failed')
    return analysis


@router.get("/threats/scoring", response_model=List[ThreatScoreOut],
            dependencies=[_READ])
async def threat_scoring(limit: int = Query(default=100, le=1000)):
    """Batch threat scores"""
    scores = threat_analyzer.calculate_threat_scores(limit=limit)
    return [{'ioc_id': ioc_id, **score} for ioc_id, score in scores.items()]


# Rules
@router.get("/rules", response_model=List[AlertRuleOut], dependencies=[_READ])
async def list_rules():
    """List alerting rules"""
    return alert_manager.list_rules()


# Enrichment / correlation (frontend-facing composites)
@router.post("/enrichment", response_model=ThreatAnalysisOut,
             dependencies=[_WRITE])
async def enrich_indicator(request: EnrichmentRequest):
    """Look up (or register) an indicator and analyze it."""
    ioc = ioc_manager.get_ioc(request.ioc)
    if not ioc:
        try:
            ioc = ioc_manager.add_ioc(request.ioc, request.ioc_type,
                                      source='enrichment')
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
    ioc_manager.enrich_ioc(ioc.ioc_id)
    analysis = threat_analyzer.analyze_ioc(ioc.ioc_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail='Analysis failed')
    return analysis


@router.post("/correlation", response_model=Payload, dependencies=[_READ])
async def correlate_indicators(request: CorrelationRequest):
    """Correlate a set of indicators (by value or id)."""
    ioc_ids: List[str] = []
    missing: List[str] = []
    for value in request.iocs:
        ioc = ioc_manager.get_ioc(value) or ioc_manager.get_ioc_by_id(value)
        if ioc:
            ioc_ids.append(ioc.ioc_id)
        else:
            missing.append(value)
    if missing:
        raise HTTPException(status_code=404, detail={
            'message': 'Unknown indicators', 'missing': missing})

    correlations = threat_analyzer.correlate_threats(ioc_ids)
    return Payload(data=[c.to_dict() if hasattr(c, 'to_dict') else c
                         for c in (correlations or [])])


# Alerts
@router.post("/alerts", response_model=AlertOut, dependencies=[_WRITE])
async def create_alert(alert: AlertCreate):
    """Create an alert"""
    created = alert_manager.create_alert(
        title=alert.title,
        description=alert.description,
        severity=alert.severity,
        ioc_id=(alert.ioc_ids[0] if alert.ioc_ids else ''),
    )
    return created


@router.get("/alerts", response_model=List[AlertOut], dependencies=[_READ])
async def list_alerts(status: str = Query(default=None),
                      severity: str = Query(default=None),
                      limit: int = Query(default=100, le=1000)):
    """List alerts"""
    return alert_manager.list_alerts(status=status, severity=severity, limit=limit)


@router.post("/alerts/{alert_id}/escalate", response_model=AlertOut,
             dependencies=[_WRITE])
async def escalate_alert(alert_id: str):
    """Escalate an alert one severity step"""
    escalated = alert_manager.escalate_alert(alert_id)
    if escalated is None:
        raise HTTPException(status_code=404, detail='Alert not found')
    return escalated


# Hunting
@router.post("/hunt", response_model=HuntOut, dependencies=[_WRITE])
async def run_hunt(request: ThreatHuntRequest):
    """Run a one-shot threat hunt"""
    method = request.method
    if method == 'hypothesis':
        hunt = threat_hunter.hypothesis_driven_hunt(request.query)
    elif method == 'anomaly':
        hunt = threat_hunter.anomaly_based_hunt()
    elif method == 'ioc':
        hunt = threat_hunter.ioc_based_hunt()
    elif method == 'behavioral':
        hunt = threat_hunter.behavioral_hunt()
    elif method == 'pattern':
        hunt = threat_hunter.pattern_matching_hunt(pattern=request.query)
    else:
        raise HTTPException(status_code=400, detail={
            'message': f'Unknown hunt method: {method}',
            'allowed': ['hypothesis', 'anomaly', 'ioc', 'behavioral', 'pattern'],
        })
    return hunt


# Sharing
@router.post("/sharing/export/stix", response_model=Payload, dependencies=[_READ])
async def export_stix():
    """Export the IOC store as a STIX-shaped bundle"""
    return Payload(data=threat_intel_sharing.export_to_stix())


@router.post("/sharing/import/stix", response_model=Payload, dependencies=[_WRITE])
async def import_stix(request: StixImportRequest):
    """Import IOCs from a STIX bundle"""
    try:
        count = threat_intel_sharing.import_from_stix(request.bundle)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return Payload(data={'imported': count})


# Monitoring
@router.get("/monitoring/health", response_model=Payload, dependencies=[_READ])
async def monitoring_health():
    """Threat pipeline health"""
    return Payload(data=threat_monitor.get_health_status())


@router.get("/monitoring/stats", response_model=Payload, dependencies=[_READ])
async def monitoring_stats():
    """Threat pipeline statistics"""
    return Payload(data=threat_monitor.get_stats())


# Threat graph
@router.get("/graph/threat", response_model=ThreatGraphOut,
            dependencies=[_READ, requires('networkx', 'graph-db')])
async def get_threat_graph():
    """The threat subgraph"""
    return threat_graph.get_threat_graph_data()


@router.get("/graph/threat/clusters", response_model=Payload,
            dependencies=[_READ, requires('networkx', 'graph-db')])
async def get_threat_clusters(min_score: float = Query(default=None)):
    """Threat clusters"""
    clusters = threat_graph.find_threat_clusters(min_score=min_score)
    return Payload(data=[c.to_dict() if hasattr(c, 'to_dict') else c
                         for c in (clusters or [])])


@router.get("/graph/threat/paths", response_model=Payload,
            dependencies=[_READ, requires('networkx', 'graph-db')])
async def get_threat_paths(source_id: str = Query(default=None),
                           target_id: str = Query(default=None),
                           max_length: int = Query(default=None)):
    """Threat propagation paths (top-scoring nodes when no source given)"""
    paths = threat_graph.find_threat_paths(source_id=source_id,
                                           target_id=target_id,
                                           max_length=max_length)
    return Payload(data=[p.to_dict() if hasattr(p, 'to_dict') else p
                         for p in (paths or [])])
