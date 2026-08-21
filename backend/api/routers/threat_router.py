"""
Threat Intelligence Router

API endpoints for Real-Time Threat Intelligence Pipeline (8 modules)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from backend.threat_intelligence import threat_feed_manager, ioc_manager, threat_analyzer, alert_manager, threat_hunter, threat_intel_sharing, threat_monitor, threat_graph

router = APIRouter()


# Pydantic Models
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
    description: str
    severity: str = "medium"
    ioc_ids: Optional[List[str]] = None


class ThreatHuntRequest(BaseModel):
    query: str
    method: str = "hypothesis"  # hypothesis, anomaly, ioc, behavioral, pattern


# Threat Feeds
@router.get("/feeds")
async def list_feeds() -> List[Dict[str, Any]]:
    """List all threat feeds"""
    feeds = threat_feed_manager.list_feeds()
    return [feed.to_dict() for feed in feeds]


@router.post("/feeds")
async def add_feed(feed: ThreatFeedCreate) -> Dict[str, Any]:
    """Add a new threat feed"""
    new_feed = threat_feed_manager.add_feed(
        feed.name, feed.url, feed.feed_type, feed.enabled
    )
    return new_feed.to_dict()


@router.post("/feeds/{feed_id}/update")
async def update_feed(feed_id: str) -> Dict[str, Any]:
    """Update a threat feed"""
    result = threat_feed_manager.update_feed(feed_id)
    return {"status": result}


@router.post("/feeds/update-all")
async def update_all_feeds() -> Dict[str, Any]:
    """Update all threat feeds"""
    result = threat_feed_manager.update_all_feeds()
    return {"updated": result}


# IOC Management
@router.post("/iocs")
async def add_ioc(ioc: IOCCreate) -> Dict[str, Any]:
    """Add a new IOC"""
    new_ioc = ioc_manager.add_ioc(
        ioc.value, ioc.ioc_type, ioc.confidence, ioc.severity, ioc.description, ioc.tags
    )
    return new_ioc.to_dict()


@router.get("/iocs")
async def list_iocs(ioc_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """List IOCs"""
    iocs = ioc_manager.list_iocs(ioc_type=ioc_type, limit=limit)
    return [ioc.to_dict() for ioc in iocs]


@router.get("/iocs/{ioc_id}")
async def get_ioc(ioc_id: str) -> Dict[str, Any]:
    """Get IOC details"""
    ioc = ioc_manager.get_ioc(ioc_id)
    if not ioc:
        raise HTTPException(status_code=404, detail="IOC not found")
    return ioc.to_dict()


@router.post("/iocs/{ioc_id}/correlate")
async def correlate_ioc(ioc_id: str) -> Dict[str, Any]:
    """Find correlations for an IOC"""
    correlations = ioc_manager.find_correlations(ioc_id)
    return {"ioc_id": ioc_id, "correlations": correlations}


# Threat Analysis
@router.post("/analyze/{ioc_id}")
async def analyze_threat(ioc_id: str) -> Dict[str, Any]:
    """Analyze a threat"""
    analysis = threat_analyzer.analyze_ioc(ioc_id)
    return analysis.to_dict()


@router.get("/threats/scoring")
async def get_threat_scores() -> Dict[str, Any]:
    """Get threat scores for all IOCs"""
    scores = threat_analyzer.calculate_threat_scores()
    return {"scores": scores}


# Alerting
@router.post("/alerts")
async def create_alert(alert: AlertCreate) -> Dict[str, Any]:
    """Create a new alert"""
    new_alert = alert_manager.create_alert(
        alert.title, alert.description, alert.severity, alert.ioc_ids
    )
    return new_alert.to_dict()


@router.get("/alerts")
async def list_alerts(status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """List alerts"""
    alerts = alert_manager.list_alerts(status=status, limit=limit)
    return [alert.to_dict() for alert in alerts]


@router.post("/alerts/{alert_id}/escalate")
async def escalate_alert(alert_id: str) -> Dict[str, Any]:
    """Escalate an alert"""
    result = alert_manager.escalate_alert(alert_id)
    return {"status": result}


# Threat Hunting
@router.post("/hunt")
async def start_hunt(request: ThreatHuntRequest) -> Dict[str, Any]:
    """Start a threat hunt"""
    if request.method == "hypothesis":
        result = threat_hunter.hypothesis_driven_hunt(request.query)
    elif request.method == "anomaly":
        result = threat_hunter.anomaly_based_hunt()
    elif request.method == "ioc":
        result = threat_hunter.ioc_based_hunt()
    elif request.method == "behavioral":
        result = threat_hunter.behavioral_hunt()
    elif request.method == "pattern":
        result = threat_hunter.pattern_matching_hunt(request.query)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown method: {request.method}")
    return {"method": request.method, "results": result}


# Threat Intel Sharing
@router.post("/sharing/export/stix")
async def export_stix() -> Dict[str, Any]:
    """Export threat intelligence as STIX"""
    stix_data = threat_intel_sharing.export_to_stix()
    return {"stix": stix_data}


@router.post("/sharing/import/stix")
async def import_stix(stix_data: str) -> Dict[str, Any]:
    """Import STIX threat intelligence"""
    result = threat_intel_sharing.import_from_stix(stix_data)
    return {"imported": result}


# Monitoring
@router.get("/monitoring/health")
async def get_threat_monitoring_health() -> Dict[str, Any]:
    """Get threat monitoring health"""
    health = threat_monitor.get_health()
    return health


@router.get("/monitoring/stats")
async def get_threat_stats() -> Dict[str, Any]:
    """Get threat intelligence statistics"""
    stats = threat_monitor.get_stats()
    return stats


# Threat Graph
@router.get("/graph/threat")
async def get_threat_graph() -> Dict[str, Any]:
    """Get the threat graph"""
    graph_data = threat_graph.get_threat_graph()
    return graph_data


@router.get("/graph/threat/clusters")
async def get_threat_clusters() -> Dict[str, Any]:
    """Get threat clusters"""
    clusters = threat_graph.find_threat_clusters()
    return {"clusters": clusters}


@router.get("/graph/threat/paths")
async def get_threat_paths() -> Dict[str, Any]:
    """Get threat paths"""
    paths = threat_graph.find_threat_paths()
    return {"paths": paths}
