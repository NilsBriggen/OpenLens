"""
AI/ML Router

API endpoints for AI/ML modules (7 modules)
"""

from datetime import datetime
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.ai import anomaly_detector, entity_resolver, predictive_analyzer
from backend.api.capabilities import requires
from backend.api.deps import require_permission
from backend.api.schemas import (
    AnomalyDetectionOut, ChatResponseOut, EntityResolutionOut, LinkScoreOut,
    Payload, PredictionResultOut,
)

router = APIRouter()

_ANALYZE = require_permission('ai', 'analyze')


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


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    conversation_id: Optional[str] = None
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7


class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str
    timestamp: Optional[str] = None


# Chat Endpoint for AI Assistant
@router.post("/chat")
async def chat(request: ChatRequest) -> Dict[str, Any]:
    """
    Chat with the AI Assistant.

    Authentication is enforced by the router-level dependency in main.py.
    """
    # Process the message based on context and content
    message = request.message.lower()
    
    # Graph-related queries
    if any(keyword in message for keyword in ['graph', 'node', 'edge', 'connection', 'path']):
        response = process_graph_query(message, request.context)
    
    # Threat-related queries
    elif any(keyword in message for keyword in ['threat', 'ioc', 'malware', 'attack', 'security']):
        response = process_threat_query(message, request.context)
    
    # Scraping-related queries
    elif any(keyword in message for keyword in ['scrape', 'scraping', 'crawl', 'extract']):
        response = process_scraping_query(message, request.context)
    
    # AI-related queries
    elif any(keyword in message for keyword in ['anomaly', 'anomalies', 'entity', 'resolve', 'predict']):
        response = process_ai_query(message, request.context)
    
    # System-related queries
    elif any(keyword in message for keyword in ['system', 'health', 'status', 'user', 'users']):
        response = process_system_query(message, request.context)
    
    # General queries
    else:
        response = process_general_query(message, request.context)
    
    return {
        "role": "assistant",
        "content": response,
        "model": "OpenLens-AI-v7",
        "conversation_id": request.conversation_id or "default",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "tokens_used": len(response.split()),
    }


def process_graph_query(message: str, context: Optional[str]) -> str:
    """Process graph-related queries."""
    if 'shortest path' in message or 'find path' in message:
        return "To find the shortest path between nodes, use the Graph Explorer page and select two nodes, then click 'Find Path'. You can also use Cypher queries like: `MATCH path = shortestPath((a {id: 'node1'})-(b {id: 'node2'})) RETURN path`"
    
    elif 'community' in message or 'cluster' in message:
        return "To detect communities, use the 'Detect Communities' button in the Graph Explorer's Analysis tab. This uses the Louvain algorithm to identify clusters of related nodes."
    
    elif 'centrality' in message:
        return "Centrality metrics help identify the most important nodes. Available algorithms: Degree, Betweenness, Closeness, PageRank, Eigenvector. Use the Centrality Analysis tool in Graph Explorer."
    
    elif 'node' in message and ('add' in message or 'create' in message):
        return "To add a node, use the Graph Explorer's edit tools or the API endpoint POST /api/graph/nodes with the node data."
    
    elif 'connection' in message or 'relationship' in message:
        return "To find connections, use the Graph Explorer's visualization. Click on a node to see its connections, or use the path finding tools."
    
    else:
        return f"I can help with graph analysis. Your query: '{message}'. Try asking about specific nodes, paths, communities, or centrality metrics."


def process_threat_query(message: str, context: Optional[str]) -> str:
    """Process threat-related queries."""
    if 'latest ioc' in message or 'recent ioc' in message:
        return "To view the latest IOCs (Indicators of Compromise), go to the Threat Intelligence page. You can filter by type (IP, Domain, Hash, URL) and severity."
    
    elif 'threat feed' in message:
        return "Threat feeds provide real-time threat intelligence. OpenLens supports STIX/TAXII feeds. Configure feeds in the Threat Intelligence > Feeds section."
    
    elif 'analyze' in message:
        return "To analyze a threat, provide the IOC (IP, domain, hash, etc.) and I can enrich it with threat intelligence data from our feeds."
    
    elif 'alert' in message:
        return "Alerts are generated when IOCs are matched in your data. View alerts in Threat Intelligence > Alerts. Configure alert rules in the Settings."
    
    else:
        return f"I can help with threat intelligence. Your query: '{message}'. Try asking about IOCs, threat feeds, or analysis."


def process_scraping_query(message: str, context: Optional[str]) -> str:
    """Process scraping-related queries."""
    if 'create job' in message or 'new scrape' in message:
        return "To create a new scrape job: 1) Go to Scraping Hub, 2) Click 'New Job', 3) Enter URLs (one per line), 4) Configure options (depth, proxies, etc.), 5) Click 'Create'."
    
    elif 'proxy' in message:
        return "Proxy rotation helps avoid rate limiting. Configure proxies in Scraping Hub > Settings. OpenLens supports HTTP, HTTPS, and SOCKS proxies."
    
    elif 'rate limit' in message:
        return "Rate limiting prevents detection. Configure rate limits per domain in Scraping Hub > Settings. Recommended: 1-5 seconds between requests."
    
    elif 'export' in message:
        return "Export scraped data in multiple formats: CSV, JSON, or directly to the graph. Use the Export button in Scraping Hub > Jobs."
    
    else:
        return f"I can help with scraping. Your query: '{message}'. Try asking about creating jobs, proxies, or rate limits."


def process_ai_query(message: str, context: Optional[str]) -> str:
    """Process AI/ML-related queries."""
    if 'anomaly' in message:
        return "Anomaly detection identifies unusual patterns. Use POST /api/ai/anomalies/detect with your data. Available methods: statistical, zscore, iqr, isolation_forest, lof, dbscan, graph, temporal."
    
    elif 'entity' in message or 'resolve' in message:
        return "Entity resolution matches similar entities. Use POST /api/ai/entities/resolve with your entity list. Available methods: exact, fuzzy, record_linkage, graph."
    
    elif 'predict' in message:
        return "Predictive analytics includes: Link prediction (between nodes), Node classification, Graph evolution, Threat prediction. Use the /api/ai/predict/* endpoints."
    
    else:
        return f"I can help with AI/ML. Your query: '{message}'. Try asking about anomaly detection, entity resolution, or predictions."


def process_system_query(message: str, context: Optional[str]) -> str:
    """Process system-related queries."""
    if 'health' in message:
        return "System health: Check /api/system/health for detailed metrics including CPU, memory, disk usage, and database status."
    
    elif 'user' in message or 'users' in message:
        return "User management: View users at /api/security/users. Create users with POST /api/security/users. Manage roles and permissions in Security Center."
    
    elif 'audit' in message:
        return "Audit logs: View at /api/security/audit. Logs track all user actions for security and compliance."
    
    else:
        return f"I can help with system management. Your query: '{message}'. Try asking about health, users, or audit logs."


def process_general_query(message: str, context: Optional[str]) -> str:
    """Process general queries."""
    greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon']
    if any(greeting in message for greeting in greetings):
        return "Hello! I'm OpenLens AI Assistant. I can help you with graph analysis, threat intelligence, AI analytics, scraping, and system management. What would you like to do?"
    
    elif 'help' in message or 'what can you do' in message:
        return """I can help you with:

**📊 Graph Analysis**
- Find connections and paths between nodes
- Detect communities and clusters
- Calculate centrality metrics
- Query graph data with Cypher

**🛡️ Threat Intelligence**
- View latest IOCs (IPs, domains, hashes)
- Analyze threats and enrich IOCs
- Manage threat feeds
- Create and manage alerts

**🤖 AI/ML Analytics**
- Detect anomalies in data
- Resolve entity matches
- Predict links and classifications
- Analyze graph evolution

**🕸️ Scraping**
- Create and manage scrape jobs
- Configure proxies and rate limits
- Export scraped data
- Monitor job progress

**🔒 Security**
- Manage users and roles
- View audit logs
- Configure RBAC permissions
- Handle encryption

**⚙️ System**
- Check system health
- View statistics and metrics
- Configure settings
- Manage backups

Ask me anything!"""
    
    elif 'tutorial' in message:
        return """**OpenLens Tutorial**

1. **Dashboard**: Overview of all modules and recent activity
2. **Graph Explorer**: Visualize and analyze your graph data
3. **AI Analytics**: Run AI/ML analysis on your data
4. **Scraping Hub**: Create and manage web scraping jobs
5. **Security Center**: Manage users, roles, and security
6. **Threat Intelligence**: View and manage threat data

Click on any module to get started, or use the AI Assistant (me!) to ask questions."""
    
    else:
        return f"I understand you're asking about: **{message}**\n\nLet me help you with that. Based on your query, you might want to check the Graph Explorer, Threat Intelligence, or AI Analytics modules. Can you provide more details?"


# Anomaly Detection
_SKLEARN_METHODS = {'isolation_forest', 'lof', 'dbscan'}
_ANOMALY_METHODS = ('statistical', 'zscore', 'iqr', 'isolation_forest',
                    'lof', 'dbscan', 'graph', 'temporal')


@router.post("/anomalies/detect", response_model=AnomalyDetectionOut,
             dependencies=[_ANALYZE, requires('numpy')])
async def detect_anomalies(request: AnomalyDetectionRequest):
    """Detect anomalies in data"""
    method = request.method
    if method in _SKLEARN_METHODS:
        from backend.api.capabilities import CAPABILITIES
        if not CAPABILITIES['sklearn']():
            from backend.api.errors import FeatureUnavailable
            raise FeatureUnavailable(feature=f'ai.anomalies.{method}',
                                     requires=['sklearn'])

    if method == "statistical":
        result = anomaly_detector.detect_statistical_anomalies(
            request.data, request.threshold or 3.0)
    elif method == "zscore":
        result = anomaly_detector.detect_zscore_anomalies(
            request.data, request.threshold or 3.0)
    elif method == "iqr":
        result = anomaly_detector.detect_iqr_anomalies(request.data)
    elif method == "isolation_forest":
        result = anomaly_detector.detect_isolation_forest(request.data)
    elif method == "lof":
        result = anomaly_detector.detect_local_outlier_factor(request.data)
    elif method == "dbscan":
        result = anomaly_detector.detect_dbscan_anomalies(request.data)
    elif method == "graph":
        result = anomaly_detector.detect_graph_anomalies()
    elif method == "temporal":
        result = anomaly_detector.detect_temporal_anomalies()
    else:
        raise HTTPException(status_code=400, detail={
            'message': f'Unknown method: {method}',
            'allowed': list(_ANOMALY_METHODS)})
    return result


@router.get("/anomalies/scores", response_model=Payload, dependencies=[_ANALYZE])
async def get_anomaly_scores():
    """Anomaly scores summary for stored graph/temporal anomalies"""
    return Payload(data=anomaly_detector.calculate_anomaly_scores())


# Entity Resolution
@router.post("/entities/resolve", response_model=EntityResolutionOut,
             dependencies=[_ANALYZE])
async def resolve_entities(request: EntityResolutionRequest):
    """Resolve entity matches"""
    try:
        if request.method == "exact":
            result = entity_resolver.resolve_exact(request.entities)
        elif request.method == "fuzzy":
            result = entity_resolver.resolve_fuzzy(request.entities,
                                                   request.threshold)
        elif request.method == "record_linkage":
            result = entity_resolver.resolve_record_linkage(request.entities)
        elif request.method == "graph":
            result = entity_resolver.resolve_graph_based(request.entities)
        else:
            raise HTTPException(status_code=400, detail={
                'message': f'Unknown method: {request.method}',
                'allowed': ['exact', 'fuzzy', 'record_linkage', 'graph']})
    except RuntimeError as exc:
        # Missing fuzzy/record-linkage library -> honest 503.
        from backend.api.errors import FeatureUnavailable
        raise FeatureUnavailable(feature=f'ai.entities.{request.method}',
                                 message=str(exc))
    return result


@router.post("/entities/deduplicate", response_model=Payload,
             dependencies=[_ANALYZE, requires('graph-db')])
async def deduplicate_entities(apply: bool = False):
    """Find duplicate entities (dry-run unless apply=true - merging deletes
    nodes from the graph)."""
    return Payload(data=entity_resolver.deduplicate_entities(apply=apply))


# Predictive Analytics
@router.post("/predict/link", response_model=LinkScoreOut,
             dependencies=[_ANALYZE, requires('networkx', 'graph-db')])
async def predict_link(request: LinkPredictionRequest):
    """Per-pair link score"""
    try:
        score = predictive_analyzer.score_link(request.node1, request.node2,
                                               request.method)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return LinkScoreOut(node_1=request.node1, node_2=request.node2,
                        method=request.method, score=score)


@router.post("/predict/node", response_model=Payload,
             dependencies=[_ANALYZE, requires('networkx', 'sklearn', 'graph-db')])
async def predict_node_classification(request: NodeClassificationRequest):
    """Predict one node's label"""
    prediction = predictive_analyzer.predict_node_classification(
        request.node_id, request.features, request.method)
    if prediction is None:
        raise HTTPException(
            status_code=404,
            detail='Node not found or model could not be trained')
    return Payload(data=prediction.to_dict()
                   if hasattr(prediction, 'to_dict') else prediction)


@router.get("/predict/graph-evolution", response_model=PredictionResultOut,
            dependencies=[_ANALYZE, requires('networkx', 'graph-db')])
async def predict_graph_evolution(steps: int = 5):
    """Predict graph evolution"""
    return predictive_analyzer.predict_graph_evolution(steps=steps)


@router.get("/predict/threats", response_model=PredictionResultOut,
            dependencies=[_ANALYZE, requires('networkx', 'sklearn', 'graph-db')])
async def predict_threats():
    """Predict potential threats"""
    return predictive_analyzer.predict_threats()
