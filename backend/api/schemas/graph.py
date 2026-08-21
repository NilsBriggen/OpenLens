"""Graph response models (wire shapes the frontend reads)."""

from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, Field, model_validator

from backend.api.schemas.base import ApiModel


class NodeOut(ApiModel):
    """A graph node as the frontend draws it."""
    id: str = Field(validation_alias=AliasChoices('id', 'node_id'))
    label: str = ''
    type: str = ''
    labels: List[str] = []
    properties: Dict[str, Any] = {}

    @model_validator(mode='after')
    def _derive_display_fields(self) -> 'NodeOut':
        if not self.label:
            self.label = str(self.properties.get('name') or self.id)
        if not self.type and self.labels:
            self.type = self.labels[0]
        return self


class EdgeOut(ApiModel):
    """A graph edge as the frontend draws it."""
    id: str = Field(validation_alias=AliasChoices('id', 'rel_id'))
    source: str = Field(validation_alias=AliasChoices('source', 'source_id'))
    target: str = Field(validation_alias=AliasChoices('target', 'target_id'))
    type: str = Field(default='', validation_alias=AliasChoices('type', 'rel_type'))
    properties: Dict[str, Any] = {}


class GraphStatsOut(ApiModel):
    """Engine statistics; connected distinguishes '0 nodes' from 'no DB'."""
    connected: bool = False
    node_count: int = 0
    edge_count: int = 0
    queries_executed: int = 0
    avg_query_time: float = 0.0
    cache_size: int = 0


class GraphResultOut(ApiModel):
    """A raw query result."""
    nodes: List[NodeOut] = []
    relationships: List[EdgeOut] = []
    records: List[Dict[str, Any]] = []
    execution_time: float = 0.0


class CentralityOut(ApiModel):
    """Centrality metrics for one node."""
    node_id: str
    degree: float = 0.0
    betweenness: float = 0.0
    closeness: float = 0.0
    eigenvector: float = 0.0
    page_rank: float = 0.0


class CentralityResponse(ApiModel):
    """A centrality run."""
    algorithm: str
    results: List[CentralityOut] = []


class PathOut(ApiModel):
    """One path through the graph."""
    nodes: List[str] = []
    length: int = 0
    cost: float = 0.0


class PathResponse(ApiModel):
    """A path-finding run."""
    algorithm: str
    paths: List[PathOut] = []
