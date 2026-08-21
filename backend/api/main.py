"""
OpenLens API Gateway - FastAPI Application

Main entry point for the OpenLens REST API.
Provides endpoints for all 32 backend modules:
- Graph Analytics
- AI/ML Insights
- Distributed Scraping
- Enterprise Security
- Real-Time Threat Intelligence
- WebSocket Real-Time Communication
"""

from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import logging
from typing import Optional

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

# Create FastAPI app
app = FastAPI(
    title="OpenLens API",
    description="Enterprise-Grade OSINT Platform API - Compete with Palantir Gotham",
    version="7.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# Include all routers
app.include_router(system_router.router, prefix="/api/system", tags=["System"])
app.include_router(graph_router.router, prefix="/api/graph", tags=["Graph Analytics"])
app.include_router(ai_router.router, prefix="/api/ai", tags=["AI/ML"])
app.include_router(scraping_router.router, prefix="/api/scraping", tags=["Scraping"])
app.include_router(security_router.router, prefix="/api/security", tags=["Security"])
app.include_router(threat_router.router, prefix="/api/threat", tags=["Threat Intelligence"])
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
