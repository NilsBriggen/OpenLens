"""
System Router - Health, metrics, config, and log endpoints.

/health stays unauthenticated (it is the liveness probe); everything else
requires system:read.
"""

import platform
from datetime import datetime
from typing import Any, Dict

import psutil
from fastapi import APIRouter, Query

from backend.api.capabilities import capability_map
from backend.api.deps import auth_required, require_permission
from backend.api.log_buffer import ring_buffer
from backend.api.schemas import LogEntryOut, SystemConfigOut

router = APIRouter()

_READ = require_permission('system', 'read')


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Full system health check (unauthenticated liveness probe)"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "processor": platform.processor(),
            "machine": platform.machine()
        },
        "resources": {
            "cpu_cores": psutil.cpu_count(logical=False),
            "cpu_logical_cores": psutil.cpu_count(logical=True),
            "cpu_usage": psutil.cpu_percent(interval=0.2),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        }
    }


@router.get("/version")
async def version() -> Dict[str, str]:
    """API version information"""
    return {
        "api_version": "7.0.0",
        "openlens_version": "7.0.0",
        "phase": "7"
    }


@router.get("/stats", dependencies=[_READ])
async def system_stats() -> Dict[str, Any]:
    """Module inventory, derived from what is actually importable."""
    import backend.ai as ai_pkg
    import backend.graph as graph_pkg
    import backend.scraping as scraping_pkg
    import backend.security as security_pkg
    import backend.threat_intelligence as threat_pkg

    def module_count(pkg) -> int:
        # Count exported singletons (lower-case names in __all__).
        return len([name for name in getattr(pkg, '__all__', [])
                    if name and name[0].islower()])

    modules = {
        "graph": module_count(graph_pkg),
        "ai": module_count(ai_pkg),
        "scraping": module_count(scraping_pkg),
        "security": module_count(security_pkg),
        "threat_intelligence": module_count(threat_pkg),
    }
    capabilities = capability_map()
    return {
        "modules": modules,
        "total_modules": sum(modules.values()),
        "features": {
            "graph_analytics": capabilities.get('graph-db', False),
            "anomaly_detection": capabilities.get('numpy', False),
            "distributed_scraping": True,
            "rbac": True,
            "threat_intel": True,
        }
    }


@router.get("/config", response_model=SystemConfigOut, dependencies=[_READ])
async def system_config():
    """Curated, secret-free configuration snapshot. Whitelisted fields only -
    never an env dump."""
    import os
    capabilities = capability_map()
    return SystemConfigOut(
        version='7.0.0',
        auth_required=auth_required(),
        capabilities=capabilities,
        cors_origins=[o.strip() for o in
                      os.getenv('OPENLENS_CORS_ORIGINS',
                                'http://localhost:3000').split(',') if o.strip()],
        features={
            'graph': capabilities.get('graph-db', False),
            'ai': capabilities.get('numpy', False) and capabilities.get('sklearn', False),
            'scraping_social_vk': True,
            'scraping_social_twitter': capabilities.get('tweepy', False),
            'scraping_social_instagram': capabilities.get('instaloader', False),
        },
    )


@router.get("/logs", response_model=list[LogEntryOut], dependencies=[_READ])
async def system_logs(level: str = Query(default=None),
                      limit: int = Query(default=100, le=1000)):
    """Recent in-process log records (ring buffer, not the audit log)"""
    return ring_buffer.tail(level=level, limit=limit)
