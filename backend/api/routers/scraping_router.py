"""
Scraping Router

API endpoints for Distributed Scraping System (9 modules)
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from backend.scraping import distributed_scraper, proxy_manager, user_agent_manager, rate_limiter, result_cache

router = APIRouter()


# Pydantic Models
class ScrapeRequest(BaseModel):
    urls: List[str]
    depth: Optional[int] = 1
    use_proxy: Optional[bool] = True
    use_cache: Optional[bool] = True
    render_js: Optional[bool] = False


class ProxyRequest(BaseModel):
    country: Optional[str] = None
    anonymous: Optional[bool] = True


class RateLimitRequest(BaseModel):
    domain: str
    limit: int
    window: int = 60


# Scraping Endpoints
@router.post("/scrape")
async def scrape_urls(request: ScrapeRequest, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """Scrape multiple URLs"""
    job_id = distributed_scraper.create_scrape_job(
        request.urls, 
        depth=request.depth,
        use_proxy=request.use_proxy,
        use_cache=request.use_cache,
        render_js=request.render_js
    )
    background_tasks.add_task(distributed_scraper.execute_scrape_job, job_id)
    return {"job_id": job_id, "status": "queued", "urls": request.urls}


@router.get("/scrape/{job_id}")
async def get_scrape_status(job_id: str) -> Dict[str, Any]:
    """Get scrape job status"""
    status = distributed_scraper.get_job_status(job_id)
    if status:
        return status
    raise HTTPException(status_code=404, detail="Job not found")


@router.get("/scrape/{job_id}/results")
async def get_scrape_results(job_id: str) -> Dict[str, Any]:
    """Get scrape job results"""
    results = distributed_scraper.get_job_results(job_id)
    if results:
        return {"job_id": job_id, "results": results}
    raise HTTPException(status_code=404, detail="Job not found or no results")


# Proxy Management
@router.get("/proxies")
async def list_proxies() -> Dict[str, Any]:
    """List available proxies"""
    proxies = proxy_manager.list_proxies()
    return {"proxies": proxies, "count": len(proxies)}


@router.get("/proxies/next")
async def get_next_proxy(request: ProxyRequest) -> Dict[str, Any]:
    """Get next proxy for rotation"""
    proxy = proxy_manager.get_proxy(country=request.country, anonymous=request.anonymous)
    if proxy:
        return proxy.to_dict()
    raise HTTPException(status_code=404, detail="No proxies available")


@router.post("/proxies/check")
async def check_proxies() -> Dict[str, Any]:
    """Check proxy health"""
    result = proxy_manager.check_all_proxies()
    return {"checked": len(result), "healthy": sum(1 for p in result if p.healthy)}


# User Agent Management
@router.get("/user-agents/next")
async def get_next_user_agent() -> Dict[str, Any]:
    """Get next user agent for rotation"""
    ua = user_agent_manager.get_user_agent()
    return {"user_agent": ua}


@router.get("/user-agents/list")
async def list_user_agents() -> Dict[str, Any]:
    """List all user agents"""
    uas = user_agent_manager.list_user_agents()
    return {"user_agents": uas, "count": len(uas)}


# Rate Limiting
@router.post("/rate-limit/set")
async def set_rate_limit(request: RateLimitRequest) -> Dict[str, Any]:
    """Set rate limit for a domain"""
    rate_limiter.set_limit(request.domain, request.limit, request.window)
    return {"domain": request.domain, "limit": request.limit, "window": request.window}


@router.get("/rate-limit/check/{domain}")
async def check_rate_limit(domain: str) -> Dict[str, Any]:
    """Check rate limit status for a domain"""
    status = rate_limiter.check_limit(domain)
    return {"domain": domain, "remaining": status.remaining, "reset_in": status.reset_in}


# Cache
@router.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    stats = result_cache.get_stats()
    return stats


@router.post("/cache/clear")
async def clear_cache() -> Dict[str, Any]:
    """Clear the cache"""
    result_cache.clear()
    return {"status": "cleared"}
