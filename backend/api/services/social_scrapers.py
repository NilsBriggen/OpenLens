"""
Lazy accessors for the legacy social scrapers.

backend/scrapers/twitter_scraper.py does a bare `import tweepy` and
instagram_scraper.py a bare `import instaloader`; importing either at router
module level would break gateway startup for every endpoint. These accessors
import on first use and raise FeatureUnavailable (-> 503) when the library is
absent. VK needs only requests + bs4 and always works.
"""

from functools import lru_cache

from backend.api.errors import FeatureUnavailable


@lru_cache(maxsize=1)
def get_vk_scraper():
    """The VK scraper (requests + bs4, no optional deps)."""
    try:
        from backend.scrapers.vk_scraper import VKScraper
    except ImportError as exc:
        raise FeatureUnavailable(feature='scraping.vk',
                                 requires=['requests', 'beautifulsoup4']) from exc
    return VKScraper()


@lru_cache(maxsize=1)
def get_twitter_scraper():
    """The Twitter scraper; 503 when tweepy is not installed."""
    try:
        from backend.scrapers.twitter_scraper import TwitterScraper
    except ImportError as exc:
        raise FeatureUnavailable(feature='scraping.twitter',
                                 requires=['tweepy']) from exc
    return TwitterScraper(rate_limit_delay=1.0)


@lru_cache(maxsize=1)
def get_instagram_scraper():
    """The Instagram scraper; 503 when instaloader is not installed."""
    try:
        from backend.scrapers.instagram_scraper import InstagramScraper
    except ImportError as exc:
        raise FeatureUnavailable(feature='scraping.instagram',
                                 requires=['instaloader']) from exc
    return InstagramScraper()
