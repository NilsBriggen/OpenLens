"""
Graph Analytics Router

API endpoints for the Graph Analytics Engine (6 modules)
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from backend.graph import graph_engine, network_analyzer, path_finder, community_detector, graph_visualizer, temporal_analyzer

router = APIRouter()
security = HTTPBearer()


# Pydantic Models
class NodeCreate(BaseModel):
    labels: List[str]
    properties: Dict[str, Any]


class RelationshipCreate(BaseModel):
    start_node_id: int
    end_node_id: int
    relationship_type: str
    properties: Dict[str, Any] = {}


class QueryRequest(BaseModel):
    query: str
    params: Dict[str, Any] = {}


class PathRequest(BaseModel):
    start_node: str
    end_node: str
    max_depth: Optional[int] = 10
    algorithm: str = "shortest"


class CentralityRequest(BaseModel):
    algorithm: str = "degree"  # degree, betweenness, closeness, eigenvector, pagerank
    limit: Optional[int] = 100


class CommunityRequest(BaseModel):
    algorithm: str = "louvain"  # louvain, label_propagation, girvan_newman
    resolution: Optional[float] = 1.0


# Endpoints
@router.post("/nodes")
async def create_node(node: NodeCreate) -> Dict[str, Any]:
    """Create a new node in the graph"""
    result = graph_engine.create_node(node.labels, node.properties)
    if result:
        return result.to_dict()
    raise HTTPException(status_code=400, detail="Failed to create node")


@router.get("/nodes/{node_id}")
async def get_node(node_id: int) -> Dict[str, Any]:
    """Get a node by ID"""
    result = graph_engine.get_node(node_id)
    if result:
        return result.to_dict()
    raise HTTPException(status_code=404, detail="Node not found")


@router.post("/relationships")
async def create_relationship(rel: RelationshipCreate) -> Dict[str, Any]:
    """Create a new relationship"""
    result = graph_engine.create_relationship(
        rel.start_node_id, rel.end_node_id, rel.relationship_type, rel.properties
    )
    if result:
        return result.to_dict()
    raise HTTPException(status_code=400, detail="Failed to create relationship")


@router.post("/query")
async def execute_query(query: QueryRequest) -> Dict[str, Any]:
    """Execute a Cypher query"""
    result = graph_engine.execute_query(query.query, **query.params)
    return result.to_dict()


@router.get("/stats")
async def get_graph_stats() -> Dict[str, Any]:
    """Get graph statistics"""
    stats = graph_engine.get_stats()
    return stats.to_dict()


# Network Analysis
@router.post("/centrality")
async def calculate_centrality(request: CentralityRequest) -> Dict[str, Any]:
    """Calculate centrality metrics"""
    if request.algorithm == "degree":
        result = network_analyzer.calculate_degree_centrality()
    elif request.algorithm == "betweenness":
        result = network_analyzer.calculate_betweenness_centrality()
    elif request.algorithm == "closeness":
        result = network_analyzer.calculate_closeness_centrality()
    elif request.algorithm == "eigenvector":
        result = network_analyzer.calculate_eigenvector_centrality()
    elif request.algorithm == "pagerank":
        result = network_analyzer.calculate_page_rank()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown algorithm: {request.algorithm}")
    return {"algorithm": request.algorithm, "result": result}


@router.post("/communities")
async def detect_communities(request: CommunityRequest) -> Dict[str, Any]:
    """Detect communities in the graph"""
    if request.algorithm == "louvain":
        result = community_detector.detect_louvain()
    elif request.algorithm == "label_propagation":
        result = community_detector.detect_label_propagation()
    elif request.algorithm == "girvan_newman":
        result = community_detector.detect_girvan_newman()
    else:
        raise HTTPException(status_code=400, detail=f"Unknown algorithm: {request.algorithm}")
    return {"algorithm": request.algorithm, "communities": result}


# Path Finding
@router.post("/path")
async def find_path(request: PathRequest) -> Dict[str, Any]:
    """Find path between two nodes"""
    if request.algorithm == "shortest":
        result = path_finder.find_shortest_path(request.start_node, request.end_node)
    elif request.algorithm == "all":
        result = path_finder.find_all_paths(request.start_node, request.end_node, request.max_depth)
    elif request.algorithm == "dijkstra":
        result = path_finder.find_dijkstra_path(request.start_node, request.end_node)
    elif request.algorithm == "astar":
        result = path_finder.find_astar_path(request.start_node, request.end_node)
    else:
        raise HTTPException(status_code=400, detail=f"Unknown algorithm: {request.algorithm}")
    return {"algorithm": request.algorithm, "path": result}


# Visualization
@router.get("/visualization/matplotlib")
async def get_matplotlib_visualization() -> Dict[str, Any]:
    """Generate Matplotlib visualization"""
    result = graph_visualizer.visualize_matplotlib()
    return {"image": result}


@router.get("/visualization/pyvis")
async def get_pyvis_visualization() -> Dict[str, Any]:
    """Generate PyVis interactive HTML"""
    result = graph_visualizer.visualize_pyvis()
    return {"html": result}


@router.get("/visualization/plotly")
async def get_plotly_visualization() -> Dict[str, Any]:
    """Generate Plotly 3D visualization"""
    result = graph_visualizer.visualize_plotly()
    return {"figure": result}


# Temporal Analysis
@router.get("/temporal/patterns")
async def get_temporal_patterns() -> Dict[str, Any]:
    """Detect temporal patterns"""
    result = temporal_analyzer.detect_temporal_patterns()
    return {"patterns": result}


@router.get("/temporal/evolution")
async def get_graph_evolution() -> Dict[str, Any]:
    """Analyze graph evolution over time"""
    result = temporal_analyzer.analyze_evolution()
    return {"evolution": result}
