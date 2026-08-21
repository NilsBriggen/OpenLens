"""
Graph Analytics Router

API endpoints for the Graph Analytics Engine. Request bodies stay snake_case
(as the frontend sends them); responses are camelCase via the schemas.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.api.capabilities import requires
from backend.api.deps import require_permission
from backend.api.errors import FeatureUnavailable
from backend.api.schemas import (
    CentralityOut, CentralityResponse, EdgeOut, GraphResultOut, GraphStatsOut,
    NodeOut, PathOut, PathResponse, Payload,
)
from backend.graph import (
    community_detector, graph_engine, graph_visualizer, network_analyzer,
    path_finder, temporal_analyzer,
)

router = APIRouter()


# Pydantic Models (request side - unchanged wire format)
class NodeCreate(BaseModel):
    labels: List[str]
    properties: Dict[str, Any]


class RelationshipCreate(BaseModel):
    # Node ids are strings (graph_engine business ids), not ints.
    start_node_id: str
    end_node_id: str
    relationship_type: str
    properties: Dict[str, Any] = {}


class QueryRequest(BaseModel):
    query: str
    params: Dict[str, Any] = {}


class PathRequest(BaseModel):
    start_node: str
    end_node: str
    max_depth: Optional[int] = 10
    algorithm: str = "shortest"  # shortest, all, dijkstra, astar


class CentralityRequest(BaseModel):
    algorithm: str = "degree"  # degree, betweenness, closeness, eigenvector, pagerank
    limit: Optional[int] = 100


class CommunityRequest(BaseModel):
    algorithm: str = "louvain"  # louvain, label_propagation, girvan_newman
    resolution: Optional[float] = 1.0


_CENTRALITY_ATTRS = {
    'degree': 'degree',
    'betweenness': 'betweenness',
    'closeness': 'closeness',
    'eigenvector': 'eigenvector',
    'pagerank': 'page_rank',
}


# Endpoints
@router.post("/nodes", response_model=NodeOut,
             dependencies=[require_permission('graph', 'write'),
                           requires('graph-db')])
async def create_node(node: NodeCreate):
    """Create a new node in the graph"""
    result = graph_engine.create_node(node.labels, node.properties)
    if result:
        return result
    raise HTTPException(status_code=400, detail="Failed to create node")


@router.get("/nodes", response_model=List[NodeOut],
            dependencies=[require_permission('graph', 'read'),
                          requires('graph-db')])
async def list_nodes(search: str = Query(default=''),
                     types: str = Query(default=''),
                     limit: int = Query(default=100, le=1000)):
    """List nodes, filtered by free-text search and/or label types."""
    clauses = []
    params: Dict[str, Any] = {'limit': limit}
    if search:
        clauses.append(
            "ANY(prop IN keys(n) WHERE toLower(toString(n[prop])) "
            "CONTAINS toLower($search))")
        params['search'] = search
    if types:
        clauses.append("ANY(label IN labels(n) WHERE label IN $types)")
        params['types'] = [t.strip() for t in types.split(',') if t.strip()]

    where = f"WHERE {' AND '.join(clauses)} " if clauses else ''
    result = graph_engine.execute_query(
        f"MATCH (n) {where}RETURN n LIMIT $limit", params, use_cache=False)
    if result is None:
        raise FeatureUnavailable(feature='graph.nodes', requires=['graph-db'])
    return result.nodes


@router.get("/nodes/{node_id}", response_model=NodeOut,
            dependencies=[require_permission('graph', 'read'),
                          requires('graph-db')])
async def get_node(node_id: str):
    """Get a node by ID"""
    result = graph_engine.get_node(node_id)
    if result:
        return result
    raise HTTPException(status_code=404, detail="Node not found")


@router.get("/edges", response_model=List[EdgeOut],
            dependencies=[require_permission('graph', 'read'),
                          requires('graph-db')])
async def list_edges(types: str = Query(default=''),
                     limit: int = Query(default=200, le=2000)):
    """List relationships, optionally filtered by type."""
    params: Dict[str, Any] = {'limit': limit}
    where = ''
    if types:
        where = "WHERE type(r) IN $types "
        params['types'] = [t.strip() for t in types.split(',') if t.strip()]

    result = graph_engine.execute_query(
        f"MATCH (a)-[r]->(b) {where}RETURN a, r, b LIMIT $limit",
        params, use_cache=False)
    if result is None:
        raise FeatureUnavailable(feature='graph.edges', requires=['graph-db'])
    return result.relationships


@router.post("/relationships", response_model=EdgeOut,
             dependencies=[require_permission('graph', 'write'),
                           requires('graph-db')])
async def create_relationship(rel: RelationshipCreate):
    """Create a new relationship"""
    result = graph_engine.create_relationship(
        rel.start_node_id, rel.end_node_id, rel.relationship_type, rel.properties
    )
    if result:
        return result
    raise HTTPException(status_code=400, detail="Failed to create relationship")


@router.post("/query", response_model=GraphResultOut,
             dependencies=[require_permission('graph', 'read'),
                           requires('graph-db')])
async def execute_query(query: QueryRequest):
    """Execute a Cypher query"""
    # params passed positionally as a dict - never splatted as kwargs.
    result = graph_engine.execute_query(query.query, query.params, use_cache=False)
    if result is None:
        raise FeatureUnavailable(feature='graph.query', requires=['graph-db'])
    return result


@router.get("/stats", response_model=GraphStatsOut,
            dependencies=[require_permission('graph', 'read')])
async def get_graph_stats():
    """Engine statistics. get_stats() returns a plain dict - no .to_dict()."""
    return graph_engine.get_stats()


@router.post("/centrality", response_model=CentralityResponse,
             dependencies=[require_permission('graph', 'read'),
                           requires('networkx', 'graph-db')])
async def calculate_centrality(request: CentralityRequest):
    """Centrality analysis. One service call computes all five metrics."""
    attr = _CENTRALITY_ATTRS.get(request.algorithm)
    if attr is None:
        raise HTTPException(status_code=400, detail={
            'message': f'Unknown centrality algorithm: {request.algorithm}',
            'allowed': sorted(_CENTRALITY_ATTRS),
        })

    results = network_analyzer.calculate_centrality()
    if not results:
        raise FeatureUnavailable(feature='graph.centrality',
                                 requires=['graph-db'])

    ranked = sorted(results, key=lambda r: getattr(r, attr, 0.0), reverse=True)
    limit = request.limit or 100
    return CentralityResponse(algorithm=request.algorithm, results=ranked[:limit])


@router.post("/communities", response_model=Payload,
             dependencies=[require_permission('graph', 'read'),
                           requires('networkx', 'graph-db')])
async def detect_communities(request: CommunityRequest):
    """Community detection"""
    if request.algorithm == 'louvain':
        result = community_detector.detect_louvain(resolution=request.resolution or 1.0)
    elif request.algorithm == 'label_propagation':
        result = community_detector.detect_label_propagation()
    elif request.algorithm == 'girvan_newman':
        result = community_detector.detect_girvan_newman()
    else:
        raise HTTPException(status_code=400, detail={
            'message': f'Unknown community algorithm: {request.algorithm}',
            'allowed': ['louvain', 'label_propagation', 'girvan_newman'],
        })

    if result is None:
        raise FeatureUnavailable(feature='graph.communities',
                                 requires=['networkx', 'graph-db'])
    return Payload(data=result.to_dict() if hasattr(result, 'to_dict') else result,
                   meta={'algorithm': request.algorithm})


@router.post("/path", response_model=PathResponse,
             dependencies=[require_permission('graph', 'read'),
                           requires('networkx', 'graph-db')])
async def find_path(request: PathRequest):
    """Path finding between two nodes"""
    algorithm = request.algorithm
    if algorithm == 'shortest':
        raw = path_finder.find_shortest_path(request.start_node, request.end_node)
        raw_paths = [raw] if raw else []
    elif algorithm == 'all':
        raw_paths = path_finder.find_all_paths(
            request.start_node, request.end_node,
            max_length=request.max_depth or 10) or []
    elif algorithm == 'dijkstra':
        raw = path_finder.find_shortest_path_dijkstra(
            request.start_node, request.end_node, 'weight')
        raw_paths = [raw] if raw else []
    elif algorithm == 'astar':
        raw = path_finder.find_shortest_path_astar(
            request.start_node, request.end_node, 'weight', None)
        raw_paths = [raw] if raw else []
    else:
        raise HTTPException(status_code=400, detail={
            'message': f'Unknown path algorithm: {algorithm}',
            'allowed': ['shortest', 'all', 'dijkstra', 'astar'],
        })

    paths = [
        PathOut(
            nodes=[str(n) for n in getattr(p, 'nodes', [])],
            length=getattr(p, 'length', 0) or max(0, len(getattr(p, 'nodes', [])) - 1),
            cost=float(getattr(p, 'weight', 0.0) or 0.0),
        )
        for p in raw_paths if p is not None
    ]
    if not paths:
        raise HTTPException(status_code=404, detail='No path found')
    return PathResponse(algorithm=algorithm, paths=paths)


@router.get("/visualization/matplotlib", response_model=Payload,
            dependencies=[require_permission('graph', 'read'),
                          requires('matplotlib', 'graph-db')])
async def visualize_matplotlib():
    """Static matplotlib visualization"""
    result = graph_visualizer.visualize_matplotlib()
    if result is None:
        raise FeatureUnavailable(feature='graph.visualization.matplotlib',
                                 requires=['matplotlib'])
    return Payload(data=result.to_dict() if hasattr(result, 'to_dict') else result)


@router.get("/visualization/pyvis", response_model=Payload,
            dependencies=[require_permission('graph', 'read'),
                          requires('pyvis', 'graph-db')])
async def visualize_pyvis():
    """Interactive pyvis visualization"""
    result = graph_visualizer.visualize_pyvis()
    if result is None:
        raise FeatureUnavailable(feature='graph.visualization.pyvis',
                                 requires=['pyvis'])
    return Payload(data=result.to_dict() if hasattr(result, 'to_dict') else result)


@router.get("/visualization/plotly", response_model=Payload,
            dependencies=[require_permission('graph', 'read'),
                          requires('plotly', 'graph-db')])
async def visualize_plotly():
    """Interactive plotly visualization"""
    result = graph_visualizer.visualize_plotly()
    if result is None:
        raise FeatureUnavailable(feature='graph.visualization.plotly',
                                 requires=['plotly'])
    return Payload(data=result.to_dict() if hasattr(result, 'to_dict') else result)


@router.get("/temporal/patterns", response_model=Payload,
            dependencies=[require_permission('graph', 'read'),
                          requires('networkx', 'graph-db')])
async def temporal_patterns(min_frequency: int = 2, max_period: float = 30.0):
    """Temporal pattern mining"""
    patterns = temporal_analyzer.find_temporal_patterns(
        min_frequency=min_frequency, max_period=max_period)
    return Payload(
        data=[p.to_dict() if hasattr(p, 'to_dict') else p for p in (patterns or [])],
        meta={'min_frequency': min_frequency, 'max_period': max_period})


@router.get("/temporal/evolution", response_model=Payload,
            dependencies=[require_permission('graph', 'read'),
                          requires('networkx', 'graph-db')])
async def temporal_evolution(num_slices: int = 10):
    """Graph evolution over time"""
    evolution = temporal_analyzer.get_temporal_evolution(num_slices=num_slices)
    return Payload(data=evolution or [], meta={'num_slices': num_slices})
