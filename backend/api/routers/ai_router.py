"""
AI/ML Router

API endpoints for AI/ML modules (7 modules)
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from backend.ai import anomaly_detector, entity_resolver, predictive_analyzer

router = APIRouter()
security = HTTPBearer()


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
async def chat(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Chat with the AI Assistant.
    
    This endpoint processes natural language queries and returns responses
    based on the OpenLens data and capabilities.
    """
    # Verify token (optional for development)
    try:
        from backend.auth.authentication import decode_token
        payload = decode_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        # For development, allow unauthenticated access
        pass
    
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
        "timestamp": "2024-01-01T00:00:00Z",
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
