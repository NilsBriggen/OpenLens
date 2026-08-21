"""
Web Scraper for OpenLens

Provides web scraping capabilities:
- HTTP requests with retries
- HTML parsing
- JavaScript rendering (optional)
- Form handling
- Session management
- Cookie handling
"""

import os
import time
import json
import random
import requests
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# Try to import selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available. Install with: pip install selenium")

# Try to import playwright
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not available. Install with: pip install playwright")


@dataclass
class ScraperConfig:
    """Configuration for web scraper."""
    user_agent: str = ''
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0
    follow_redirects: bool = True
    use_proxy: bool = False
    use_javascript: bool = False
    javascript_engine: str = 'selenium'  # selenium, playwright
    headless: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'user_agent': self.user_agent,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'follow_redirects': self.follow_redirects,
            'use_proxy': self.use_proxy,
            'use_javascript': self.use_javascript,
            'javascript_engine': self.javascript_engine,
            'headless': self.headless,
        }


@dataclass
class ScraperResponse:
    """Response from web scraper."""
    url: str
    status_code: int = 200
    content: str = ''
    headers: Dict[str, str] = field(default_factory=dict)
    cookies: Dict[str, str] = field(default_factory=dict)
    soup: Any = None  # BeautifulSoup object
    request_time: float = 0.0
    is_success: bool = False
    error: str = ''
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'url': self.url,
            'status_code': self.status_code,
            'content': self.content,
            'headers': self.headers,
            'cookies': self.cookies,
            'request_time': self.request_time,
            'is_success': self.is_success,
            'error': self.error,
        }


@dataclass
class FormField:
    """Represents a form field."""
    name: str
    type: str = 'text'
    value: str = ''
    options: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'type': self.type,
            'value': self.value,
            'options': self.options,
        }


@dataclass
class Form:
    """Represents a web form."""
    action: str
    method: str = 'GET'
    fields: List[FormField] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'action': self.action,
            'method': self.method,
            'fields': [f.to_dict() for f in self.fields],
        }


class WebScraper:
    """
    Web scraper for OpenLens.
    
    Provides:
    - HTTP requests with retries
    - HTML parsing
    - JavaScript rendering (optional)
    - Form handling
    - Session management
    - Cookie handling
    """
    
    def __init__(self, config: ScraperConfig = None, proxy_manager=None, user_agent_manager=None):
        """
        Initialize the web scraper.
        
        Args:
            config: ScraperConfig instance.
            proxy_manager: ProxyManager instance.
            user_agent_manager: UserAgentManager instance.
        """
        self.config = config or ScraperConfig()
        self.proxy_manager = proxy_manager
        self.user_agent_manager = user_agent_manager
        self._session = None
        self._cookies = {}
        self._headers = {}
        self._javascript_driver = None
        
        # Initialize session
        self._init_session()
    
    def _init_session(self):
        """Initialize the requests session."""
        self._session = requests.Session()
        
        # Set default headers
        self._headers = {
            'User-Agent': self.config.user_agent or self._get_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        self._session.headers.update(self._headers)
    
    def _get_user_agent(self) -> str:
        """Get a user agent."""
        if self.user_agent_manager:
            return self.user_agent_manager.get_random_user_agent()
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    def _get_proxy(self) -> Optional[Dict]:
        """Get a proxy."""
        if self.proxy_manager and self.config.use_proxy:
            proxy = self.proxy_manager.get_random_proxy()
            if proxy:
                return proxy.get_dict()
        return None
    
    def request(self, url: str, method: str = 'GET', params: Dict = None, 
                data: Dict = None, headers: Dict = None, 
                cookies: Dict = None, timeout: int = None) -> ScraperResponse:
        """
        Make an HTTP request.
        
        Args:
            url: URL to request.
            method: HTTP method.
            params: Query parameters.
            data: Request body.
            headers: Request headers.
            cookies: Request cookies.
            timeout: Request timeout.
            
        Returns:
            ScraperResponse.
        """
        start_time = time.time()
        timeout = timeout or self.config.timeout
        
        # Prepare request
        request_headers = {**self._headers, **(headers or {})}
        request_cookies = {**self._cookies, **(cookies or {})}
        
        # Get proxy
        proxy = self._get_proxy()
        
        # Make request with retries
        for attempt in range(self.config.max_retries + 1):
            try:
                response = self._session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    headers=request_headers,
                    cookies=request_cookies,
                    proxies=proxy,
                    timeout=timeout,
                    allow_redirects=self.config.follow_redirects,
                )
                
                # Update cookies
                if response.cookies:
                    self._cookies.update(response.cookies)
                
                # Parse content
                content = response.text
                soup = BeautifulSoup(content, 'html.parser')
                
                request_time = time.time() - start_time
                
                return ScraperResponse(
                    url=url,
                    status_code=response.status_code,
                    content=content,
                    headers=dict(response.headers),
                    cookies=dict(response.cookies),
                    soup=soup,
                    request_time=request_time,
                    is_success=response.status_code < 400,
                    error='' if response.status_code < 400 else f'HTTP {response.status_code}',
                )
            
            except requests.exceptions.RequestException as e:
                if attempt < self.config.max_retries:
                    # Wait before retrying
                    time.sleep(self.config.retry_delay * (attempt + 1))
                    
                    # Try a different proxy
                    if self.proxy_manager and self.config.use_proxy:
                        proxy = self._get_proxy()
                    
                    # Try a different user agent
                    self._headers['User-Agent'] = self._get_user_agent()
                    self._session.headers.update(self._headers)
                else:
                    request_time = time.time() - start_time
                    return ScraperResponse(
                        url=url,
                        status_code=0,
                        content='',
                        headers={},
                        cookies={},
                        soup=None,
                        request_time=request_time,
                        is_success=False,
                        error=str(e),
                    )
        
        request_time = time.time() - start_time
        return ScraperResponse(
            url=url,
            status_code=0,
            content='',
            headers={},
            cookies={},
            soup=None,
            request_time=request_time,
            is_success=False,
            error='Max retries exceeded',
        )
    
    def get(self, url: str, params: Dict = None, headers: Dict = None, 
            cookies: Dict = None, timeout: int = None) -> ScraperResponse:
        """
        Make a GET request.
        
        Args:
            url: URL to request.
            params: Query parameters.
            headers: Request headers.
            cookies: Request cookies.
            timeout: Request timeout.
            
        Returns:
            ScraperResponse.
        """
        return self.request(url, 'GET', params=params, headers=headers, 
                           cookies=cookies, timeout=timeout)
    
    def post(self, url: str, data: Dict = None, params: Dict = None, 
             headers: Dict = None, cookies: Dict = None, timeout: int = None) -> ScraperResponse:
        """
        Make a POST request.
        
        Args:
            url: URL to request.
            data: Request body.
            params: Query parameters.
            headers: Request headers.
            cookies: Request cookies.
            timeout: Request timeout.
            
        Returns:
            ScraperResponse.
        """
        return self.request(url, 'POST', params=params, data=data, 
                           headers=headers, cookies=cookies, timeout=timeout)
    
    def get_with_javascript(self, url: str, wait_for: str = None, 
                           wait_time: float = 2.0) -> ScraperResponse:
        """
        Get a page with JavaScript rendering.
        
        Args:
            url: URL to request.
            wait_for: Element to wait for (CSS selector).
            wait_time: Time to wait for page to load.
            
        Returns:
            ScraperResponse.
        """
        if not self.config.use_javascript:
            return self.get(url)
        
        start_time = time.time()
        
        try:
            if self.config.javascript_engine == 'playwright' and PLAYWRIGHT_AVAILABLE:
                return self._get_with_playwright(url, wait_for, wait_time)
            elif self.config.javascript_engine == 'selenium' and SELENIUM_AVAILABLE:
                return self._get_with_selenium(url, wait_for, wait_time)
            else:
                return self.get(url)
        
        except Exception as e:
            request_time = time.time() - start_time
            return ScraperResponse(
                url=url,
                status_code=0,
                content='',
                headers={},
                cookies={},
                soup=None,
                request_time=request_time,
                is_success=False,
                error=f"JavaScript rendering error: {e}",
            )
    
    def _get_with_playwright(self, url: str, wait_for: str = None, 
                           wait_time: float = 2.0) -> ScraperResponse:
        """Get a page using Playwright."""
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=self.config.headless)
            context = browser.new_context(
                user_agent=self._get_user_agent(),
                viewport={'width': 1280, 'height': 720}
            )
            page = context.new_page()
            
            # Navigate to URL
            page.goto(url, timeout=self.config.timeout * 1000)
            
            # Wait for element or time
            if wait_for:
                try:
                    page.wait_for_selector(wait_for, timeout=wait_time * 1000)
                except:
                    pass
            else:
                time.sleep(wait_time)
            
            # Get content
            content = page.content()
            headers = dict(page.evaluate("() => Object.fromEntries(new URL(window.location.href).searchParams.entries())"))
            cookies = {cookie['name']: cookie['value'] for cookie in context.cookies()}
            
            # Close browser
            browser.close()
            
            soup = BeautifulSoup(content, 'html.parser')
            request_time = time.time() - start_time
            
            return ScraperResponse(
                url=url,
                status_code=200,
                content=content,
                headers=headers,
                cookies=cookies,
                soup=soup,
                request_time=request_time,
                is_success=True,
                error='',
            )
    
    def _get_with_selenium(self, url: str, wait_for: str = None, 
                          wait_time: float = 2.0) -> ScraperResponse:
        """Get a page using Selenium."""
        # Initialize driver if not already done
        if not self._javascript_driver:
            self._init_selenium_driver()
        
        try:
            self._javascript_driver.get(url)
            
            # Wait for element or time
            if wait_for:
                try:
                    WebDriverWait(self._javascript_driver, wait_time).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                    )
                except:
                    pass
            else:
                time.sleep(wait_time)
            
            # Get content
            content = self._javascript_driver.page_source
            cookies = {cookie['name']: cookie['value'] for cookie in self._javascript_driver.get_cookies()}
            
            soup = BeautifulSoup(content, 'html.parser')
            request_time = time.time() - start_time
            
            return ScraperResponse(
                url=url,
                status_code=200,
                content=content,
                headers={},
                cookies=cookies,
                soup=soup,
                request_time=request_time,
                is_success=True,
                error='',
            )
        
        except Exception as e:
            request_time = time.time() - start_time
            return ScraperResponse(
                url=url,
                status_code=0,
                content='',
                headers={},
                cookies={},
                soup=None,
                request_time=request_time,
                is_success=False,
                error=str(e),
            )
    
    def _init_selenium_driver(self):
        """Initialize Selenium driver."""
        if self.config.javascript_engine != 'selenium':
            return
        
        try:
            if self.config.headless:
                chrome_options = Options()
                chrome_options.add_argument('--headless')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument(f'user-agent={self._get_user_agent()}')
                
                self._javascript_driver = webdriver.Chrome(options=chrome_options)
            else:
                self._javascript_driver = webdriver.Chrome()
        
        except Exception as e:
            print(f"Error initializing Selenium: {e}")
            self._javascript_driver = None
    
    def extract_links(self, url: str, selector: str = 'a') -> List[str]:
        """
        Extract all links from a page.
        
        Args:
            url: URL to scrape.
            selector: CSS selector for links.
            
        Returns:
            List of URLs.
        """
        response = self.get(url)
        
        if not response.is_success or not response.soup:
            return []
        
        links = []
        for link in response.soup.select(selector):
            href = link.get('href')
            if href:
                # Make absolute URL
                absolute_url = urljoin(url, href)
                links.append(absolute_url)
        
        return links
    
    def extract_text(self, url: str, selector: str) -> List[str]:
        """
        Extract text from elements matching a selector.
        
        Args:
            url: URL to scrape.
            selector: CSS selector.
            
        Returns:
            List of text strings.
        """
        response = self.get(url)
        
        if not response.is_success or not response.soup:
            return []
        
        texts = []
        for element in response.soup.select(selector):
            text = element.get_text(strip=True)
            if text:
                texts.append(text)
        
        return texts
    
    def extract_data(self, url: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Extract structured data from a page.
        
        Args:
            url: URL to scrape.
            selectors: Dictionary of field names to CSS selectors.
            
        Returns:
            Dictionary with extracted data.
        """
        response = self.get(url)
        
        if not response.is_success or not response.soup:
            return {}
        
        data = {}
        for field, selector in selectors.items():
            elements = response.soup.select(selector)
            
            if len(elements) == 1:
                data[field] = elements[0].get_text(strip=True)
            elif len(elements) > 1:
                data[field] = [el.get_text(strip=True) for el in elements]
            else:
                data[field] = None
        
        return data
    
    def get_forms(self, url: str) -> List[Form]:
        """
        Extract all forms from a page.
        
        Args:
            url: URL to scrape.
            
        Returns:
            List of Form objects.
        """
        response = self.get(url)
        
        if not response.is_success or not response.soup:
            return []
        
        forms = []
        for form_element in response.soup.find_all('form'):
            action = form_element.get('action', '')
            method = form_element.get('method', 'GET').upper()
            
            form_fields = []
            for field_element in form_element.find_all(['input', 'select', 'textarea']):
                field_name = field_element.get('name', '')
                field_type = field_element.get('type', 'text')
                field_value = field_element.get('value', '')
                
                # Get options for select elements
                options = []
                if field_element.name == 'select':
                    for option in field_element.find_all('option'):
                        options.append(option.get('value', ''))
                
                form_fields.append(FormField(
                    name=field_name,
                    type=field_type,
                    value=field_value,
                    options=options,
                ))
            
            forms.append(Form(
                action=action,
                method=method,
                fields=form_fields,
            ))
        
        return forms
    
    def submit_form(self, url: str, form_data: Dict[str, str], 
                    method: str = 'POST') -> ScraperResponse:
        """
        Submit a form.
        
        Args:
            url: URL to submit to.
            form_data: Form data as dictionary.
            method: HTTP method.
            
        Returns:
            ScraperResponse.
        """
        return self.request(url, method, data=form_data)
    
    def scrape_table(self, url: str, table_selector: str = 'table') -> List[Dict[str, str]]:
        """
        Scrape data from a table.
        
        Args:
            url: URL to scrape.
            table_selector: CSS selector for the table.
            
        Returns:
            List of dictionaries (rows).
        """
        response = self.get(url)
        
        if not response.is_success or not response.soup:
            return []
        
        table = response.soup.select_one(table_selector)
        if not table:
            return []
        
        # Extract headers
        headers = []
        header_row = table.select_one('thead tr') or table.select_one('tr')
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
        
        # Extract rows
        rows = []
        for row in table.select('tbody tr') if table.select('tbody') else table.select('tr')[1:]:
            cells = row.find_all(['td', 'th'])
            row_data = {}
            
            for i, cell in enumerate(cells):
                header = headers[i] if i < len(headers) else str(i)
                row_data[header] = cell.get_text(strip=True)
            
            rows.append(row_data)
        
        return rows
    
    def scrape_list(self, url: str, item_selector: str) -> List[Dict[str, str]]:
        """
        Scrape a list of items.
        
        Args:
            url: URL to scrape.
            item_selector: CSS selector for list items.
            
        Returns:
            List of dictionaries (items).
        """
        response = self.get(url)
        
        if not response.is_success or not response.soup:
            return []
        
        items = []
        for item in response.soup.select(item_selector):
            item_data = {}
            
            # Extract all text
            item_data['text'] = item.get_text(strip=True)
            
            # Extract links
            links = []
            for link in item.find_all('a', href=True):
                links.append({
                    'text': link.get_text(strip=True),
                    'url': urljoin(url, link['href']),
                })
            item_data['links'] = links
            
            # Extract images
            images = []
            for img in item.find_all('img', src=True):
                images.append({
                    'alt': img.get('alt', ''),
                    'src': urljoin(url, img['src']),
                })
            item_data['images'] = images
            
            items.append(item_data)
        
        return items
    
    def close(self):
        """Close the scraper and clean up resources."""
        if self._session:
            self._session.close()
            self._session = None
        
        if self._javascript_driver:
            try:
                self._javascript_driver.quit()
            except:
                pass
            self._javascript_driver = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global scraper instance
scraper = WebScraper()
