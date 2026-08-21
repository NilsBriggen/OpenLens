"""
Scraping Router

API endpoints for the Distributed Scraping System plus the social scrapers
(VK works out of the box; Twitter/Instagram 503 until their libraries are
installed). Request bodies stay snake_case; responses are camelCase.
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
from pydantic import BaseModel

from backend.api.deps import require_permission
from backend.api.schemas import (
    CacheStatsOut, Payload, ProxyListOut, ProxyOut, RateLimitStatusOut,
    ScrapeJobOut, StatusOut, UserAgentListOut,
)
from backend.api.services.social_scrapers import (
    get_instagram_scraper, get_twitter_scraper, get_vk_scraper,
)
from backend.scraping import (
    distributed_scraper, proxy_manager, rate_limiter, result_cache,
    user_agent_manager,
)

router = APIRouter()

_EXECUTE = require_permission('scraper', 'execute')
_CONFIGURE = require_permission('scraper', 'configure')
_READ = require_permission('scraper', 'read')


# Pydantic Models (request side - unchanged wire format)
class ScrapeRequest(BaseModel):
    urls: List[str]
    name: Optional[str] = None
    depth: Optional[int] = 1
    use_proxy: Optional[bool] = True
    use_cache: Optional[bool] = True
    render_js: Optional[bool] = False


class RateLimitRequest(BaseModel):
    domain: str
    limit: int
    window: int = 60


class VkUserRequest(BaseModel):
    user_id: Optional[str] = None
    username: Optional[str] = None


class VkPostsRequest(BaseModel):
    user_id: str
    limit: Optional[int] = 10


class VkSearchRequest(BaseModel):
    query: str
    limit: Optional[int] = 10


class TwitterTweetsRequest(BaseModel):
    query: str
    limit: Optional[int] = 20


class TwitterUserRequest(BaseModel):
    username: str


class InstagramUserRequest(BaseModel):
    username: str


class InstagramPostsRequest(BaseModel):
    username: str
    limit: Optional[int] = 10


class InstagramHashtagRequest(BaseModel):
    hashtag: str
    limit: Optional[int] = 10


# Scraping job endpoints
@router.get("/jobs", response_model=List[ScrapeJobOut], dependencies=[_READ])
async def list_jobs(search: str = Query(default=None),
                    status: str = Query(default=None)):
    """List scraping jobs"""
    jobs = [distributed_scraper.get_job(job['job_id'])
            for job in distributed_scraper.get_all_jobs()]
    jobs = [job for job in jobs if job]
    if status:
        jobs = [job for job in jobs if job.status == status]
    if search:
        needle = search.lower()
        jobs = [job for job in jobs if needle in job.name.lower()]
    return jobs


@router.post("/scrape", response_model=ScrapeJobOut, dependencies=[_EXECUTE])
async def scrape_urls(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """Create and start a scraping job"""
    if not request.urls:
        raise HTTPException(status_code=400, detail='urls must not be empty')
    job_id = distributed_scraper.create_scrape_job(
        request.urls,
        name=request.name or '',
        depth=request.depth or 1,
        use_proxy=bool(request.use_proxy),
        use_cache=bool(request.use_cache),
        render_js=bool(request.render_js),
    )
    background_tasks.add_task(distributed_scraper.execute_scrape_job, job_id)
    return distributed_scraper.get_job(job_id)


@router.get("/scrape/{job_id}", response_model=ScrapeJobOut, dependencies=[_READ])
async def get_job_status(job_id: str):
    """One job's status"""
    job = distributed_scraper.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail='Job not found')
    return job


@router.get("/scrape/{job_id}/results", response_model=Payload,
            dependencies=[_READ])
async def get_job_results(job_id: str):
    """One job's results"""
    if not distributed_scraper.get_job(job_id):
        raise HTTPException(status_code=404, detail='Job not found')
    return Payload(data=distributed_scraper.get_job_results(job_id))


# Proxy endpoints
@router.get("/proxies", response_model=ProxyListOut, dependencies=[_READ])
async def list_proxies(active_only: bool = Query(default=False)):
    """List known proxies"""
    proxies = proxy_manager.list_proxies(active_only=active_only)
    return ProxyListOut(proxies=proxies, count=len(proxies))


@router.get("/proxies/next", response_model=ProxyOut, dependencies=[_READ])
async def next_proxy(country: str = Query(default=None),
                     protocol: str = Query(default=None)):
    """The next proxy in rotation. Query params - a GET takes no body."""
    proxy = proxy_manager.get_proxy(country=country, protocol=protocol)
    if not proxy:
        raise HTTPException(status_code=404, detail='No proxy available')
    return proxy


@router.post("/proxies/check", response_model=ProxyListOut,
             dependencies=[_CONFIGURE])
async def check_proxies():
    """Health-check every proxy; returns the active list"""
    active = proxy_manager.check_all_proxies(force=True)
    return ProxyListOut(proxies=active, count=len(active))


# User-agent endpoints
@router.get("/user-agents/next", response_model=Payload, dependencies=[_READ])
async def next_user_agent(browser: str = Query(default=None),
                          device_type: str = Query(default=None)):
    """The next user agent in rotation"""
    user_agent = user_agent_manager.get_user_agent(browser=browser,
                                                   device_type=device_type)
    if not user_agent:
        raise HTTPException(status_code=404, detail='No user agent available')
    return Payload(data={'user_agent': user_agent})


@router.get("/user-agents/list", response_model=UserAgentListOut,
            dependencies=[_READ])
async def list_user_agents(browser: str = Query(default=None),
                           device_type: str = Query(default=None)):
    """List user agents"""
    agents = user_agent_manager.list_user_agents(browser=browser,
                                                 device_type=device_type)
    return UserAgentListOut(user_agents=agents, count=len(agents))


# Rate-limit endpoints
@router.post("/rate-limit/set", response_model=StatusOut,
             dependencies=[_CONFIGURE])
async def set_rate_limit(request: RateLimitRequest):
    """Set a per-domain rate limit"""
    rate_limiter.set_rate_limit(request.domain, request.limit,
                                float(request.window))
    return StatusOut(status='set', detail=f'{request.domain}: '
                     f'{request.limit}/{request.window}s')


@router.get("/rate-limit/check/{domain}", response_model=RateLimitStatusOut,
            dependencies=[_READ])
async def check_rate_limit(domain: str):
    """Non-consuming rate-limit status for a domain"""
    status = rate_limiter.get_status(domain)
    return RateLimitStatusOut(allowed=status.allowed, remaining=status.remaining,
                              reset_time=status.reset_time, reset_in=status.reset_in)


# Cache endpoints
@router.get("/cache/stats", response_model=CacheStatsOut, dependencies=[_READ])
async def cache_stats():
    """Result-cache statistics. The stats object is a dataclass - the schema
    validates it directly instead of the old raw-dataclass-in-Dict response."""
    return result_cache.get_stats()


@router.post("/cache/clear", response_model=StatusOut, dependencies=[_CONFIGURE])
async def clear_cache():
    """Clear the result cache"""
    result_cache.clear()
    return StatusOut(status='cleared')


# Social scrapers (reusing backend/scrapers/*; lazy imports so a missing
# optional library 503s the endpoint instead of breaking gateway startup)
@router.post("/vk/user", response_model=Payload, dependencies=[_EXECUTE])
async def scrape_vk_user(request: VkUserRequest):
    """Scrape a VK user profile"""
    identifier = request.username or request.user_id
    if not identifier:
        raise HTTPException(status_code=400, detail='user_id or username required')
    user = get_vk_scraper().scrape_user_profile(identifier)
    if not user:
        raise HTTPException(status_code=404, detail='VK user not found')
    return Payload(data=user.to_dict() if hasattr(user, 'to_dict') else vars(user))


@router.post("/vk/posts", response_model=Payload, dependencies=[_EXECUTE])
async def scrape_vk_posts(request: VkPostsRequest):
    """Scrape a VK user's posts"""
    posts = get_vk_scraper().scrape_user_posts(request.user_id,
                                               limit=request.limit or 10)
    return Payload(data=[p.to_dict() if hasattr(p, 'to_dict') else vars(p)
                         for p in (posts or [])])


@router.post("/vk/search", response_model=Payload, dependencies=[_EXECUTE])
async def search_vk_users(request: VkSearchRequest):
    """Search VK users"""
    results = get_vk_scraper().search_users(request.query,
                                            limit=request.limit or 10)
    return Payload(data=results or [])


@router.post("/twitter/tweets", response_model=Payload, dependencies=[_EXECUTE])
async def scrape_twitter_tweets(request: TwitterTweetsRequest):
    """Scrape tweets matching a query"""
    tweets = get_twitter_scraper().scrape_tweets(request.query,
                                                 limit=request.limit or 20)
    return Payload(data=[t.to_dict() if hasattr(t, 'to_dict') else vars(t)
                         for t in (tweets or [])])


@router.post("/twitter/user", response_model=Payload, dependencies=[_EXECUTE])
async def scrape_twitter_user(request: TwitterUserRequest):
    """Scrape a Twitter user profile"""
    user = get_twitter_scraper().scrape_user_profile(request.username)
    if not user:
        raise HTTPException(status_code=404, detail='Twitter user not found')
    return Payload(data=user.to_dict() if hasattr(user, 'to_dict') else vars(user))


@router.get("/twitter/trends", response_model=Payload, dependencies=[_EXECUTE])
async def scrape_twitter_trends(limit: int = Query(default=10, le=50)):
    """Scrape Twitter trends"""
    trends = get_twitter_scraper().scrape_trends(limit=limit)
    return Payload(data=trends or [])


@router.post("/instagram/user", response_model=Payload, dependencies=[_EXECUTE])
async def scrape_instagram_user(request: InstagramUserRequest):
    """Scrape an Instagram user profile"""
    user = get_instagram_scraper().scrape_user_profile(request.username)
    if not user:
        raise HTTPException(status_code=404, detail='Instagram user not found')
    return Payload(data=user.to_dict() if hasattr(user, 'to_dict') else vars(user))


@router.post("/instagram/posts", response_model=Payload, dependencies=[_EXECUTE])
async def scrape_instagram_posts(request: InstagramPostsRequest):
    """Scrape an Instagram user's posts"""
    posts = get_instagram_scraper().scrape_user_posts(request.username,
                                                      limit=request.limit or 10)
    return Payload(data=[p.to_dict() if hasattr(p, 'to_dict') else vars(p)
                         for p in (posts or [])])


@router.post("/instagram/hashtag", response_model=Payload, dependencies=[_EXECUTE])
async def scrape_instagram_hashtag(request: InstagramHashtagRequest):
    """Scrape posts for a hashtag"""
    posts = get_instagram_scraper().scrape_hashtag_posts(request.hashtag,
                                                         limit=request.limit or 10)
    return Payload(data=[p.to_dict() if hasattr(p, 'to_dict') else vars(p)
                         for p in (posts or [])])
