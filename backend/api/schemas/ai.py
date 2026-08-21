"""AI/ML response models (wire shapes the frontend reads)."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, Field

from backend.api.schemas.base import ApiModel


class AnomalyOut(ApiModel):
    """One detected anomaly."""
    id: str = Field(validation_alias=AliasChoices('id', 'anomaly_id'))
    entity_id: str
    entity_type: str = 'node'
    score: float = 0.0
    method: str = ''
    severity: str = 'medium'
    explanation: str = ''
    features: Dict[str, Any] = {}


class AnomalyDetectionOut(ApiModel):
    """An anomaly-detection run."""
    method: str
    anomalies: List[AnomalyOut] = []
    total_entities: int = 0
    anomalous_entities: int = 0
    execution_time: float = 0.0


class EntityMatchOut(ApiModel):
    """One entity match."""
    entity_id_1: str
    entity_id_2: str
    similarity_score: float = 0.0
    matching_attributes: List[str] = []
    method: str = ''


class EntityClusterOut(ApiModel):
    """One cluster of matched entities."""
    cluster_id: str
    entities: List[str] = []
    representative: str = ''
    confidence: float = 0.0


class EntityResolutionOut(ApiModel):
    """An entity-resolution run."""
    method: str
    matches: List[EntityMatchOut] = []
    clusters: List[EntityClusterOut] = []
    total_entities: int = 0
    matched_entities: int = 0
    execution_time: float = 0.0


class PredictionOut(ApiModel):
    """One prediction."""
    id: str = Field(validation_alias=AliasChoices('id', 'prediction_id'))
    entity_id: str = ''
    prediction_type: str = ''
    predicted_value: Any = None
    probability: float = 0.0
    method: str = ''


class PredictionResultOut(ApiModel):
    """A prediction run."""
    method: str = ''
    predictions: List[PredictionOut] = []
    total_predictions: int = 0
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    execution_time: float = 0.0


class LinkScoreOut(ApiModel):
    """Per-pair link score."""
    node_1: str
    node_2: str
    method: str
    score: float = 0.0


class ChatResponseOut(ApiModel):
    """AI assistant chat reply."""
    response: str
    context: Optional[str] = None
    timestamp: Optional[datetime] = None
