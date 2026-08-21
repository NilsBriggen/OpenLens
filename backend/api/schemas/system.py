"""System response models."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.api.schemas.base import ApiModel


class HealthOut(ApiModel):
    """Liveness/health summary."""
    status: str
    timestamp: Optional[datetime] = None
    system: Dict[str, Any] = {}
    resources: Dict[str, Any] = {}


class VersionOut(ApiModel):
    """Version info."""
    version: str
    name: str = 'OpenLens API'


class SystemStatsOut(ApiModel):
    """Module inventory and feature flags."""
    modules: Dict[str, Any] = {}
    total_modules: int = 0
    features: Dict[str, Any] = {}


class SystemConfigOut(ApiModel):
    """Curated, secret-free configuration snapshot."""
    version: str
    auth_required: bool = True
    capabilities: Dict[str, bool] = {}
    cors_origins: List[str] = []
    features: Dict[str, bool] = {}


class LogEntryOut(ApiModel):
    """One in-memory log record."""
    level: str
    logger: str = ''
    message: str
    timestamp: Optional[datetime] = None
