"""
Scrapy Integration for OpenLens

Provides Scrapy-based crawling support:
- Spider spec registry (dependency-free)
- Scrapy settings assembly from the fleet's proxy/UA managers
- Spider source-code generation for standalone Scrapy projects
- Spider execution (requires the scrapy package)

Only run_spider needs Scrapy itself; everything else is pure Python. When
Scrapy is not installed, run_spider raises ScrapyNotAvailableError rather
than emulating a crawl - a fake crawl result would be indistinguishable from
a real one. For crawling without Scrapy, use distributed_scraper/WebScraper.
"""

import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

# Try to import scrapy
try:
    import scrapy
    from scrapy.crawler import CrawlerProcess
    SCRAPY_AVAILABLE = True
except ImportError:
    SCRAPY_AVAILABLE = False
    print("Scrapy not available. Install with: pip install scrapy")


class ScrapyNotAvailableError(RuntimeError):
    """Raised when a Scrapy-requiring operation runs without Scrapy installed."""


@dataclass
class ScrapySpiderSpec:
    """Declarative description of a spider."""
    name: str
    start_urls: List[str] = field(default_factory=list)
    allowed_domains: List[str] = field(default_factory=list)
    item_selectors: Dict[str, str] = field(default_factory=dict)  # field -> css selector
    follow_links: bool = False
    max_depth: int = 1
    download_delay: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'start_urls': self.start_urls,
            'allowed_domains': self.allowed_domains,
            'item_selectors': self.item_selectors,
            'follow_links': self.follow_links,
            'max_depth': self.max_depth,
            'download_delay': self.download_delay,
        }


@dataclass
class ScrapyRunResult:
    """Result of a spider run."""
    spec_name: str
    items: List[Dict[str, Any]] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    execution_time: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'spec_name': self.spec_name,
            'items': self.items,
            'stats': self.stats,
            'errors': self.errors,
            'execution_time': self.execution_time,
        }


class ScrapyIntegration:
    """
    Scrapy integration for OpenLens.

    Registers spider specs, builds settings that plug into the fleet's proxy
    and user-agent rotation, and (when Scrapy is installed) runs spiders.
    """

    def __init__(self, proxy_manager=None, user_agent_manager=None,
                 settings: Dict[str, Any] = None):
        """
        Initialize the integration.

        Args:
            proxy_manager: ProxyManager instance.
            user_agent_manager: UserAgentManager instance.
            settings: Extra Scrapy settings overrides.
        """
        self.proxy_manager = proxy_manager
        self.user_agent_manager = user_agent_manager
        self.settings_overrides = settings or {}
        self._specs: Dict[str, ScrapySpiderSpec] = {}

    def is_available(self) -> bool:
        """True when the scrapy package is importable."""
        return SCRAPY_AVAILABLE

    def build_settings(self) -> Dict[str, Any]:
        """
        Scrapy settings dict, honest about what the fleet provides.
        Pure function - testable without Scrapy installed.
        """
        settings: Dict[str, Any] = {
            'ROBOTSTXT_OBEY': True,
            'DOWNLOAD_DELAY': 1.0,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
            'COOKIES_ENABLED': False,
            'TELNETCONSOLE_ENABLED': False,
            'LOG_LEVEL': 'WARNING',
        }

        if self.user_agent_manager:
            user_agent = self.user_agent_manager.get_user_agent()
            if user_agent:
                settings['USER_AGENT'] = user_agent

        if self.proxy_manager:
            proxy = self.proxy_manager.get_proxy()
            if proxy:
                settings['PROXY'] = f'{proxy.protocol}://{proxy.host}:{proxy.port}'

        settings.update(self.settings_overrides)
        return settings

    def register_spider(self, spec: ScrapySpiderSpec) -> bool:
        """Register (or replace) a spider spec."""
        if not spec.name or not spec.start_urls:
            return False
        self._specs[spec.name] = spec
        return True

    def get_spider(self, name: str) -> Optional[ScrapySpiderSpec]:
        """A registered spec by name."""
        return self._specs.get(name)

    def list_spiders(self) -> List[ScrapySpiderSpec]:
        """All registered specs."""
        return list(self._specs.values())

    def export_spider_module(self, name: str) -> str:
        """
        Generate standalone Scrapy spider source for a registered spec.
        Pure string templating - works without Scrapy installed.
        """
        spec = self._specs.get(name)
        if not spec:
            raise KeyError(f'no spider spec named {name!r}')

        selector_lines = '\n'.join(
            f"            {field_name!r}: response.css({selector!r}).get(),"
            for field_name, selector in spec.item_selectors.items()
        ) or "            'url': response.url,"

        follow_block = ''
        if spec.follow_links:
            follow_block = (
                "\n        for href in response.css('a::attr(href)').getall():\n"
                "            yield response.follow(href, self.parse)\n"
            )

        return f'''import scrapy


class {spec.name.title().replace('-', '').replace('_', '')}Spider(scrapy.Spider):
    name = {spec.name!r}
    start_urls = {spec.start_urls!r}
    allowed_domains = {spec.allowed_domains!r}
    custom_settings = {{
        'DOWNLOAD_DELAY': {spec.download_delay},
        'DEPTH_LIMIT': {spec.max_depth},
    }}

    def parse(self, response):
        yield {{
{selector_lines}
        }}{follow_block}
'''

    def run_spider(self, name: str, timeout: int = 300) -> ScrapyRunResult:
        """
        Run a registered spider.

        Raises:
            ScrapyNotAvailableError: When the scrapy package is not installed.
            KeyError: For an unregistered spider name.
        """
        if not SCRAPY_AVAILABLE:
            raise ScrapyNotAvailableError(
                'Scrapy is not installed; install with `pip install scrapy`, '
                'or use distributed_scraper/WebScraper for crawling without it.')

        spec = self._specs.get(name)
        if not spec:
            raise KeyError(f'no spider spec named {name!r}')

        started = time.time()
        collected: List[Dict[str, Any]] = []
        errors: List[str] = []

        selectors = dict(spec.item_selectors)
        follow = spec.follow_links

        class _SpecSpider(scrapy.Spider):
            name = spec.name
            start_urls = list(spec.start_urls)
            allowed_domains = list(spec.allowed_domains)
            custom_settings = {
                'DOWNLOAD_DELAY': spec.download_delay,
                'DEPTH_LIMIT': spec.max_depth,
                'CLOSESPIDER_TIMEOUT': timeout,
            }

            def parse(self, response):
                item = ({field_name: response.css(sel).get()
                         for field_name, sel in selectors.items()}
                        if selectors else {'url': response.url})
                collected.append(item)
                yield item
                if follow:
                    for href in response.css('a::attr(href)').getall():
                        yield response.follow(href, self.parse)

        try:
            process = CrawlerProcess(self.build_settings(), install_root_handler=False)
            process.crawl(_SpecSpider)
            process.start(stop_after_crawl=True)
        except Exception as e:
            errors.append(str(e))

        return ScrapyRunResult(
            spec_name=name,
            items=collected,
            stats={'item_count': len(collected)},
            errors=errors,
            execution_time=time.time() - started,
        )


# Global scrapy integration instance
scrapy_integration = ScrapyIntegration()
