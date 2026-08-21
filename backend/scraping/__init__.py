"""
Distributed Scraping Module for OpenLens

Provides enterprise-grade distributed scraping capabilities:
- Celery-based task distribution
- Scrapy integration
- Proxy rotation
- User agent rotation
- Rate limiting
- Result caching
- Error handling
- Monitoring
"""

from .celery_app import celery_app, create_celery_app
from .scrapy_integration import ScrapyIntegration, scrapy_integration
from .proxy_manager import ProxyManager, proxy_manager
from .user_agent_manager import UserAgentManager, user_agent_manager
from .rate_limiter import RateLimiter, rate_limiter
from .result_cache import ResultCache, result_cache
from .scraper import WebScraper, scraper
from .distributed_scraper import DistributedScraper, distributed_scraper
from .scraping_tasks import *

__all__ = [
    'celery_app',
    'create_celery_app',
    'ScrapyIntegration',
    'scrapy_integration',
    'ProxyManager',
    'proxy_manager',
    'UserAgentManager',
    'user_agent_manager',
    'RateLimiter',
    'rate_limiter',
    'ResultCache',
    'result_cache',
    'WebScraper',
    'scraper',
    'DistributedScraper',
    'distributed_scraper',
]
