"""Scraping response models (wire shapes the frontend reads)."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import AliasChoices, Field, model_validator

from backend.api.schemas.base import ApiModel


class ScrapeJobOut(ApiModel):
    """A scraping job as the frontend reads it."""
    id: str = Field(validation_alias=AliasChoices('id', 'job_id'))
    name: str = ''
    status: str = 'pending'
    progress: float = 0.0
    success_count: int = 0
    failed_count: int = 0
    created_at: Optional[datetime] = None
    # Source fields used to derive the counts; not serialised.
    results: List[Any] = Field(default_factory=list, exclude=True)
    errors: List[Any] = Field(default_factory=list, exclude=True)

    @model_validator(mode='after')
    def _derive_counts(self) -> 'ScrapeJobOut':
        if not self.success_count:
            self.success_count = len(self.results)
        if not self.failed_count:
            self.failed_count = len(self.errors)
        return self


class ProxyOut(ApiModel):
    """A proxy server as the frontend reads it."""
    id: str = ''
    host: str
    port: int
    protocol: str = 'http'
    location: str = Field(default='', validation_alias=AliasChoices('location', 'country'))
    status: str = ''
    speed: float = 0.0
    success_rate: float = 0.0
    is_active: bool = Field(default=False, exclude=True)

    @model_validator(mode='after')
    def _derive_fields(self) -> 'ProxyOut':
        if not self.id:
            self.id = f'{self.host}:{self.port}'
        if not self.status:
            self.status = 'active' if self.is_active else 'inactive'
        return self


class ProxyListOut(ApiModel):
    """A proxy listing."""
    proxies: List[ProxyOut] = []
    count: int = 0


class RateLimitStatusOut(ApiModel):
    """Rate-limit status for a domain."""
    allowed: bool
    remaining: int
    reset_time: float
    reset_in: float = 0.0


class CacheStatsOut(ApiModel):
    """Result-cache statistics."""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    expirations: int = 0
    size: int = 0
    memory_usage: int = 0
    hit_rate: float = 0.0

    @model_validator(mode='after')
    def _derive_hit_rate(self) -> 'CacheStatsOut':
        total = self.hits + self.misses
        if not self.hit_rate and total:
            self.hit_rate = self.hits / total
        return self


class UserAgentListOut(ApiModel):
    """User-agent strings."""
    user_agents: List[str] = []
    count: int = 0
