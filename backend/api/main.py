"""
OpenLens API Gateway - FastAPI Application

Main entry point for the OpenLens REST API:
- Graph Analytics
- AI/ML Insights
- Distributed Scraping
- Enterprise Security
- Real-Time Threat Intelligence
- WebSocket Real-Time Communication
"""

import logging
import os

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Wire service collaborators before any router imports the singletons.
# Module-level (not a lifespan hook) so pytest and CLI tools get the same
# wiring without booting ASGI.
from backend.composition import configure_services
configure_services()

from backend.api.deps import auth_required, get_current_user
from backend.api.errors import install_error_handlers
from backend.api.log_buffer import install_ring_buffer

# Import all module routers
from .routers import (
    graph_router,
    ai_router,
    scraping_router,
    security_router,
    threat_router,
    system_router,
    websocket_router
)

logger = logging.getLogger(__name__)

install_ring_buffer()

# Create FastAPI app
app = FastAPI(
    title="OpenLens API",
    description="Enterprise-Grade OSINT Platform API",
    version="7.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

CORS_ORIGINS = [
    origin.strip() for origin in
    os.getenv('OPENLENS_CORS_ORIGINS', 'http://localhost:3000').split(',')
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

install_error_handlers(app)

if not auth_required():
    logger.warning("AUTH DISABLED (OPENLENS_REQUIRE_AUTH=0) - every endpoint "
                   "is open. Never run production this way.")

# Optional demo seeding: the IOC store is in-memory per process, so demo IOCs
# must be seeded inside the API process to be visible to it.
if os.getenv('OPENLENS_SEED_DEMO', '0') == '1':
    try:
        from backend.graph.seed import seed_demo_graph, seed_demo_iocs
        from backend.graph import graph_engine
        if graph_engine.is_connected():
            seed_demo_graph(graph_engine)
        seeded = seed_demo_iocs()
        logger.info("Demo seed: %d IOCs loaded", seeded)
    except Exception as exc:
        logger.warning("Demo seeding failed: %s", exc)

# Authentication for every module router; per-route authorization lives in
# the routers' own dependencies. /api/security stays unguarded here because
# it contains the login endpoint (its protected routes guard themselves).
_AUTH = [Depends(get_current_user)]

app.include_router(system_router.router, prefix="/api/system", tags=["System"])
app.include_router(graph_router.router, prefix="/api/graph",
                   dependencies=_AUTH, tags=["Graph Analytics"])
app.include_router(ai_router.router, prefix="/api/ai",
                   dependencies=_AUTH, tags=["AI/ML"])
app.include_router(scraping_router.router, prefix="/api/scraping",
                   dependencies=_AUTH, tags=["Scraping"])
app.include_router(security_router.router, prefix="/api/security", tags=["Security"])
app.include_router(threat_router.router, prefix="/api/threat",
                   dependencies=_AUTH, tags=["Threat Intelligence"])
app.include_router(websocket_router.router, prefix="/api", tags=["WebSocket"])


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "OpenLens API",
        "version": "7.0.0",
        "description": "Enterprise-Grade OSINT Platform",
        "docs": "/docs",
        "health": "/api/system/health",
        "websocket": "/api/ws"
    }


@app.get("/health")
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "version": "7.0.0"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )
