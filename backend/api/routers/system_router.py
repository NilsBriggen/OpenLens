"""
System Router - Health, metrics, and system endpoints
"""

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from typing import Dict, Any
import psutil
import platform
from datetime import datetime

router = APIRouter()
security = HTTPBearer()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Full system health check"""
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
            "cpu_usage": psutil.cpu_percent(interval=1),
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


@router.get("/stats")
async def system_stats() -> Dict[str, Any]:
    """System statistics"""
    return {
        "modules": {
            "graph": 6,
            "ai": 7,
            "scraping": 9,
            "security": 7,
            "threat_intelligence": 8
        },
        "total_modules": 37,
        "features": {
            "graph_analytics": True,
            "anomaly_detection": True,
            "distributed_scraping": True,
            "rbac": True,
            "threat_intel": True
        }
    }
