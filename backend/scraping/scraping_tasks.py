"""
Scraping Tasks for OpenLens Celery

Provides Celery tasks for distributed scraping:
- URL scraping
- News scraping
- Social media scraping
- Dark web scraping
- Proxy management
- Cache cleanup
"""

import os
import time
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
from bs4 import BeautifulSoup

# Import Celery
from .celery_app import celery_app, OpenLensTask


@celery_app.task(bind=True, base=OpenLensTask)
def scrape_url(self, url: str, method: str = 'GET', 
               params: Dict = None, config: Dict = None) -> Dict[str, Any]:
    """
    Scrape a single URL.
    
    Args:
        url: URL to scrape.
        method: HTTP method.
        params: Request parameters.
        config: Scraper configuration.
        
    Returns:
        Dictionary with scraping results.
    """
    from .scraper import WebScraper, ScraperConfig
    from .proxy_manager import proxy_manager
    from .user_agent_manager import user_agent_manager
    
    try:
        # Create scraper with configuration
        scraper_config = ScraperConfig(
            user_agent=config.get('user_agent'),
            timeout=config.get('timeout', 30),
            max_retries=config.get('max_retries', 3),
            use_proxy=config.get('use_proxy', True),
            use_javascript=config.get('use_javascript', False),
        )
        
        scraper = WebScraper(
            config=scraper_config,
            proxy_manager=proxy_manager,
            user_agent_manager=user_agent_manager,
        )
        
        # Execute request
        if method.upper() == 'GET':
            response = scraper.get(url, params=params)
        elif method.upper() == 'POST':
            response = scraper.post(url, data=params)
        else:
            response = scraper.request(url, method, params=params)
        
        # Process response
        if response.is_success:
            return {
                'status': 'success',
                'url': url,
                'data': {
                    'content': response.content,
                    'soup': str(response.soup) if response.soup else '',
                    'status_code': response.status_code,
                    'headers': response.headers,
                    'request_time': response.request_time,
                },
                'metrics': {
                    'request_time': response.request_time,
                    'content_length': len(response.content),
                },
            }
        else:
            return {
                'status': 'failure',
                'url': url,
                'error': response.error or f"HTTP {response.status_code}",
            }
    
    except Exception as e:
        return {
            'status': 'failure',
            'url': url,
            'error': str(e),
        }


@celery_app.task(bind=True, base=OpenLensTask)
def scrape_news_sources(self) -> Dict[str, Any]:
    """
    Scrape news from various sources.
    
    Returns:
        Dictionary with news articles.
    """
    from .scraper import WebScraper
    from .proxy_manager import proxy_manager
    from .user_agent_manager import user_agent_manager
    
    news_sources = [
        'https://www.bbc.com/news',
        'https://www.cnn.com/',
        'https://www.reuters.com/',
        'https://www.nytimes.com/',
        'https://www.theguardian.com/',
    ]
    
    articles = []
    
    try:
        scraper = WebScraper(
            proxy_manager=proxy_manager,
            user_agent_manager=user_agent_manager,
        )
        
        for source in news_sources:
            try:
                response = scraper.get(source, timeout=30)
                
                if response.is_success and response.soup:
                    # Extract articles (simplified)
                    # In production, use site-specific selectors
                    for article in response.soup.find_all(['article', 'div'], class_=lambda x: x and 'article' in x.lower()):
                        title = article.find(['h1', 'h2', 'h3'])
                        link = article.find('a', href=True)
                        
                        if title and link:
                            articles.append({
                                'source': source,
                                'title': title.get_text(strip=True),
                                'url': link['href'],
                                'timestamp': datetime.utcnow().isoformat(),
                            })
            
            except Exception as e:
                print(f"Error scraping {source}: {e}")
                continue
        
        return {
            'status': 'success',
            'count': len(articles),
            'articles': articles,
        }
    
    except Exception as e:
        return {
            'status': 'failure',
            'error': str(e),
        }


@celery_app.task(bind=True, base=OpenLensTask)
def scrape_social_media(self) -> Dict[str, Any]:
    """
    Scrape social media (simulated - actual implementation would use APIs).
    
    Returns:
        Dictionary with social media posts.
    """
    # Note: In production, this would use official APIs with proper authentication
    # This is a simplified simulation
    
    posts = []
    
    try:
        # Simulate scraping Twitter
        twitter_urls = [
            'https://twitter.com/search?q=cybersecurity',
            'https://twitter.com/search?q=threatintel',
        ]
        
        from .scraper import WebScraper
        from .proxy_manager import proxy_manager
        from .user_agent_manager import user_agent_manager
        
        scraper = WebScraper(
            proxy_manager=proxy_manager,
            user_agent_manager=user_agent_manager,
        )
        
        for url in twitter_urls:
            try:
                response = scraper.get(url, timeout=30)
                
                if response.is_success:
                    # In production, parse the page for tweets
                    # This is a simplified example
                    posts.append({
                        'platform': 'twitter',
                        'url': url,
                        'count': 10,  # Simulated
                        'timestamp': datetime.utcnow().isoformat(),
                    })
            
            except Exception as e:
                print(f"Error scraping {url}: {e}")
                continue
        
        return {
            'status': 'success',
            'count': len(posts),
            'posts': posts,
        }
    
    except Exception as e:
        return {
            'status': 'failure',
            'error': str(e),
        }


@celery_app.task(bind=True, base=OpenLensTask)
def scrape_darkweb_sources(self) -> Dict[str, Any]:
    """
    Scrape dark web sources (simulated - requires special access).
    
    Returns:
        Dictionary with dark web data.
    """
    # Note: This is a simulation. Actual dark web scraping requires:
    # - Tor network access
    # - Special configuration
    # - Legal considerations
    
    try:
        # Simulate scraping some dark web directories
        # In production, this would use Tor and specific .onion addresses
        
        return {
            'status': 'success',
            'message': 'Dark web scraping simulation',
            'data': {
                'sites_visited': 0,
                'data_collected': 0,
            },
        }
    
    except Exception as e:
        return {
            'status': 'failure',
            'error': str(e),
        }


@celery_app.task(bind=True, base=OpenLensTask)
def update_proxy_list(self) -> Dict[str, Any]:
    """
    Update the proxy list from all sources.
    
    Returns:
        Dictionary with update results.
    """
    from .proxy_manager import proxy_manager
    
    try:
        count = proxy_manager.update_proxy_list()
        stats = proxy_manager.get_stats()
        
        return {
            'status': 'success',
            'proxies_loaded': count,
            'stats': stats,
        }
    
    except Exception as e:
        return {
            'status': 'failure',
            'error': str(e),
        }


@celery_app.task(bind=True, base=OpenLensTask)
def cleanup_result_cache(self) -> Dict[str, Any]:
    """
    Clean up the result cache.
    
    Returns:
        Dictionary with cleanup results.
    """
    from .result_cache import result_cache
    
    try:
        result_cache.cleanup()
        stats = result_cache.get_stats()
        
        return {
            'status': 'success',
            'stats': stats.to_dict(),
        }
    
    except Exception as e:
        return {
            'status': 'failure',
            'error': str(e),
        }


@celery_app.task(bind=True, base=OpenLensTask)
def scrape_website(self, url: str, depth: int = 1, 
                 max_pages: int = 50) -> Dict[str, Any]:
    """
    Scrape an entire website recursively.
    
    Args:
        url: Starting URL.
        depth: Maximum depth to crawl.
        max_pages: Maximum number of pages to scrape.
        
    Returns:
        Dictionary with scraping results.
    """
    from .scraper import WebScraper
    from .proxy_manager import proxy_manager
    from .user_agent_manager import user_agent_manager
    from urllib.parse import urljoin, urlparse
    
    try:
        scraper = WebScraper(
            proxy_manager=proxy_manager,
            user_agent_manager=user_agent_manager,
        )
        
        visited = set()
        to_visit = [(url, 0)]
        results = []
        
        while to_visit and len(results) < max_pages:
            current_url, current_depth = to_visit.pop(0)
            
            if current_url in visited or current_depth > depth:
                continue
            
            visited.add(current_url)
            
            try:
                response = scraper.get(current_url, timeout=30)
                
                if response.is_success:
                    # Extract links
                    links = []
                    if response.soup:
                        for link in response.soup.find_all('a', href=True):
                            href = link['href']
                            absolute_url = urljoin(current_url, href)
                            
                            # Only follow links from the same domain
                            if self._same_domain(url, absolute_url):
                                links.append(absolute_url)
                    
                    results.append({
                        'url': current_url,
                        'status': 'success',
                        'content_length': len(response.content),
                        'links': links,
                    })
                    
                    # Add new links to visit
                    for link in links:
                        if link not in visited:
                            to_visit.append((link, current_depth + 1))
            
            except Exception as e:
                results.append({
                    'url': current_url,
                    'status': 'failure',
                    'error': str(e),
                })
        
        return {
            'status': 'success',
            'start_url': url,
            'pages_scraped': len(results),
            'pages_visited': len(visited),
            'results': results,
        }
    
    except Exception as e:
        return {
            'status': 'failure',
            'error': str(e),
        }
    
    def _same_domain(self, base_url: str, url: str) -> bool:
        """Check if two URLs have the same domain."""
        base_parsed = urlparse(base_url)
        url_parsed = urlparse(url)
        
        return base_parsed.netloc == url_parsed.netloc


@celery_app.task(bind=True, base=OpenLensTask)
def extract_entities(self, url: str, entity_types: List[str] = None) -> Dict[str, Any]:
    """
    Extract entities from a webpage.
    
    Args:
        url: URL to scrape.
        entity_types: List of entity types to extract (Person, Organization, etc.).
        
    Returns:
        Dictionary with extracted entities.
    """
    from .scraper import WebScraper
    from .proxy_manager import proxy_manager
    from .user_agent_manager import user_agent_manager
    
    entity_types = entity_types or ['Person', 'Organization', 'Location', 'Date']
    
    try:
        scraper = WebScraper(
            proxy_manager=proxy_manager,
            user_agent_manager=user_agent_manager,
        )
        
        response = scraper.get(url, timeout=30)
        
        if not response.is_success or not response.soup:
            return {
                'status': 'failure',
                'url': url,
                'error': 'Failed to fetch page',
            }
        
        # Extract entities based on type
        entities = {}
        
        for entity_type in entity_types:
            if entity_type == 'Person':
                entities['Person'] = self._extract_people(response.soup)
            elif entity_type == 'Organization':
                entities['Organization'] = self._extract_organizations(response.soup)
            elif entity_type == 'Location':
                entities['Location'] = self._extract_locations(response.soup)
            elif entity_type == 'Date':
                entities['Date'] = self._extract_dates(response.soup)
            elif entity_type == 'Email':
                entities['Email'] = self._extract_emails(response.soup)
            elif entity_type == 'Phone':
                entities['Phone'] = self._extract_phones(response.soup)
        
        return {
            'status': 'success',
            'url': url,
            'entities': entities,
        }
    
    except Exception as e:
        return {
            'status': 'failure',
            'url': url,
            'error': str(e),
        }
    
    def _extract_people(self, soup: BeautifulSoup) -> List[str]:
        """Extract person names from HTML."""
        # This is a simplified extraction
        # In production, use NLP libraries like spaCy
        people = set()
        
        # Look for common patterns
        for text in soup.stripped_strings:
            # Simple pattern matching (would be replaced with NLP in production)
            if len(text.split()) >= 2 and len(text.split()) <= 4:
                # Check if it looks like a name (capitalized words)
                words = text.split()
                if all(word[0].isupper() for word in words):
                    people.add(text)
        
        return list(people)
    
    def _extract_organizations(self, soup: BeautifulSoup) -> List[str]:
        """Extract organization names from HTML."""
        organizations = set()
        
        # Look for common organization patterns
        for text in soup.stripped_strings:
            # Simple pattern matching
            if len(text.split()) >= 2:
                # Check for common organization suffixes
                suffixes = ['Inc', 'LLC', 'Corp', 'Corporation', 'Ltd', 'Limited', 'GmbH', 'S.A.']
                if any(suffix in text for suffix in suffixes):
                    organizations.add(text)
        
        return list(organizations)
    
    def _extract_locations(self, soup: BeautifulSoup) -> List[str]:
        """Extract location names from HTML."""
        locations = set()
        
        # Look for common location patterns
        for text in soup.stripped_strings:
            # Simple pattern matching
            if len(text.split()) >= 2:
                # Check for common location patterns
                # This would be replaced with a proper geocoding service in production
                pass
        
        return list(locations)
    
    def _extract_dates(self, soup: BeautifulSoup) -> List[str]:
        """Extract dates from HTML."""
        import re
        dates = set()
        
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
            r'\w+ \d{2}, \d{4}',   # Month DD, YYYY
        ]
        
        for text in soup.stripped_strings:
            for pattern in date_patterns:
                matches = re.findall(pattern, text)
                dates.update(matches)
        
        return list(dates)
    
    def _extract_emails(self, soup: BeautifulSoup) -> List[str]:
        """Extract email addresses from HTML."""
        import re
        emails = set()
        
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        for text in soup.stripped_strings:
            matches = re.findall(email_pattern, text)
            emails.update(matches)
        
        return list(emails)
    
    def _extract_phones(self, soup: BeautifulSoup) -> List[str]:
        """Extract phone numbers from HTML."""
        import re
        phones = set()
        
        phone_patterns = [
            r'\+?\d{10,15}',  # International format
            r'\(\d{3}\) \d{3}-\d{4}',  # US format
            r'\d{3}-\d{3}-\d{4}',  # US format
        ]
        
        for text in soup.stripped_strings:
            for pattern in phone_patterns:
                matches = re.findall(pattern, text)
                phones.update(matches)
        
        return list(phones)


@celery_app.task(bind=True, base=OpenLensTask)
def monitor_website(self, url: str, check_interval: int = 300, 
                   timeout: int = 30) -> Dict[str, Any]:
    """
    Monitor a website for changes.
    
    Args:
        url: URL to monitor.
        check_interval: Seconds between checks.
        timeout: Request timeout.
        
    Returns:
        Dictionary with monitoring results.
    """
    from .scraper import WebScraper
    from .proxy_manager import proxy_manager
    from .user_agent_manager import user_agent_manager
    from .result_cache import result_cache
    
    try:
        scraper = WebScraper(
            proxy_manager=proxy_manager,
            user_agent_manager=user_agent_manager,
        )
        
        # Get current content
        response = scraper.get(url, timeout=timeout)
        
        if not response.is_success:
            return {
                'status': 'failure',
                'url': url,
                'error': 'Failed to fetch page',
            }
        
        # Get previous content from cache
        cache_key = result_cache.generate_key(url)
        previous_content = result_cache.get(cache_key)
        
        # Compare content
        current_content = response.content
        
        if previous_content:
            changed = previous_content != current_content
        else:
            changed = False
        
        # Cache current content
        result_cache.set(cache_key, current_content, ttl=check_interval * 2)
        
        return {
            'status': 'success',
            'url': url,
            'changed': changed,
            'content_length': len(current_content),
            'timestamp': datetime.utcnow().isoformat(),
        }
    
    except Exception as e:
        return {
            'status': 'failure',
            'url': url,
            'error': str(e),
        }
