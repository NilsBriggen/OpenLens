"""
AI/ML Router

API endpoints for AI/ML modules (7 modules)
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from backend.ai import anomaly_detector, entity_resolver, predictive_analyzer

router = APIRouter()


# Pydantic Models
class AnomalyDetectionRequest(BaseModel):
    data: List[Dict[str, Any]]
    method: str = "statistical"  # statistical, isolation_forest, lof, dbscan, graph, temporal
    threshold: Optional[float] = 3.0


class EntityResolutionRequest(BaseModel):
    entities: List[Dict[str, Any]]
    method: str = "exact"  # exact, fuzzy, record_linkage, graph
    threshold: Optional[float] = 0.85


class LinkPredictionRequest(BaseModel):
    node1: str
    node2: str
    method: str = "common_neighbors"  # common_neighbors, jaccard, adamic_adar, preferential_attachment


class NodeClassificationRequest(BaseModel):
    node_id: str
    features: Dict[str, float]
    method: str = "logistic_regression"


# Anomaly Detection
@router.post("/anomalies/detect")
async def detect_anomalies(request: AnomalyDetectionRequest) -> Dict[str, Any]:
    """Detect anomalies in data"""
    if request.method == "statistical":
        result = anomaly_detector.detect_statistical_anomalies(request.data, request.threshold)
    elif request.method == "zscore":
        result = anomaly_detector.detect_zscore_anomalies(request.data, request.threshold)
    elif request.method == "iqr":
        result = anomaly_detector.detect_iqr_anomalies(request.data)
    elif request.method == "isolation_forest":
        result = anomaly_detector.detect_isolation_forest(request.data)
    elif request.method == "lof":
        result = anomaly_detector.detect_local_outlier_factor(request.data)
    elif request.method == "dbscan":
        result = anomaly_detector.detect_dbscan_anomalies(request.data)
    elif request.method == "graph":
        result = anomaly_detector.detect_graph_anomalies()
    elif request.method == "temporal":
        result = anomaly_detector.detect_temporal_anomalies()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown method: {request.method}")
    return {"method": request.method, "anomalies": result}


@router.get("/anomalies/scores")
async def get_anomaly_scores() -> Dict[str, Any]:
    """Get anomaly scores for all nodes"""
    result = anomaly_detector.calculate_anomaly_scores()
    return {"scores": result}


# Entity Resolution
@router.post("/entities/resolve")
async def resolve_entities(request: EntityResolutionRequest) -> Dict[str, Any]:
    """Resolve entity matches"""
    if request.method == "exact":
        result = entity_resolver.resolve_exact(request.entities)
    elif request.method == "fuzzy":
        result = entity_resolver.resolve_fuzzy(request.entities, request.threshold)
    elif request.method == "record_linkage":
        result = entity_resolver.resolve_record_linkage(request.entities)
    elif request.method == "graph":
        result = entity_resolver.resolve_graph_based(request.entities)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown method: {request.method}")
    return {"method": request.method, "matches": result}


@router.post("/entities/deduplicate")
async def deduplicate_entities() -> Dict[str, Any]:
    """Deduplicate entities in the graph"""
    result = entity_resolver.deduplicate_entities()
    return {"deduplicated": result}


# Predictive Analytics
@router.post("/predict/link")
async def predict_link(request: LinkPredictionRequest) -> Dict[str, Any]:
    """Predict if a link exists between two nodes"""
    if request.method == "common_neighbors":
        score = predictive_analyzer.predict_link_common_neighbors(request.node1, request.node2)
    elif request.method == "jaccard":
        score = predictive_analyzer.predict_link_jaccard(request.node1, request.node2)
    elif request.method == "adamic_adar":
        score = predictive_analyzer.predict_link_adamic_adar(request.node1, request.node2)
    elif request.method == "preferential_attachment":
        score = predictive_analyzer.predict_link_preferential_attachment(request.node1, request.node2)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown method: {request.method}")
    return {"node1": request.node1, "node2": request.node2, "method": request.method, "score": score}


@router.post("/predict/node")
async def predict_node_classification(request: NodeClassificationRequest) -> Dict[str, Any]:
    """Predict node classification"""
    result = predictive_analyzer.predict_node_classification(
        request.node_id, request.features, request.method
    )
    return {"node_id": request.node_id, "classification": result}


@router.get("/predict/graph-evolution")
async def predict_graph_evolution() -> Dict[str, Any]:
    """Predict graph evolution"""
    result = predictive_analyzer.predict_graph_evolution()
    return {"evolution": result}


@router.get("/predict/threats")
async def predict_threats() -> Dict[str, Any]:
    """Predict potential threats"""
    result = predictive_analyzer.predict_threats()
    return {"threats": result}
