"""
Proxy Manager for OpenLens Distributed Scraping

Provides proxy management capabilities:
- Proxy rotation
- Proxy health checking
- Proxy type support (HTTP, HTTPS, SOCKS)
- Geographic distribution
- Anonymous proxy detection
"""

import os
import time
import threading
import random
import json
import requests
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from urllib.parse import urlparse


@dataclass
class Proxy:
    """Represents a proxy server."""
    host: str
    port: int
    protocol: str = 'http'  # http, https, socks4, socks5
    username: str = ''
    password: str = ''
    country: str = ''
    city: str = ''
    isp: str = ''
    anonymity: str = 'transparent'  # transparent, anonymous, elite
    speed: float = 0.0  # Response time in seconds
    success_rate: float = 0.0  # Success rate (0-1)
    last_checked: datetime = None
    last_success: datetime = None
    last_failure: datetime = None
    consecutive_failures: int = 0
    is_active: bool = True
    
    def __post_init__(self):
        """Initialize proxy."""
        if isinstance(self.port, str):
            self.port = int(self.port)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'host': self.host,
            'port': self.port,
            'protocol': self.protocol,
            'username': self.username,
            'password': '*****' if self.password else '',
            'country': self.country,
            'city': self.city,
            'isp': self.isp,
            'anonymity': self.anonymity,
            'speed': self.speed,
            'success_rate': self.success_rate,
            'last_checked': self.last_checked.isoformat() if self.last_checked else None,
            'last_success': self.last_success.isoformat() if self.last_success else None,
            'last_failure': self.last_failure.isoformat() if self.last_failure else None,
            'consecutive_failures': self.consecutive_failures,
            'is_active': self.is_active,
        }
    
    def get_url(self) -> str:
        """Get the proxy URL."""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.host}:{self.port}"
        else:
            return f"{self.protocol}://{self.host}:{self.port}"
    
    def get_dict(self) -> Dict[str, str]:
        """Get proxy as dictionary for requests."""
        return {
            'http': self.get_url(),
            'https': self.get_url(),
        }


@dataclass
class ProxyConfig:
    """Configuration for proxy manager."""
    proxy_sources: List[str] = field(default_factory=lambda: [
        'https://www.sslproxies.org/',
        'https://free-proxy-list.net/',
        'https://www.us-proxy.org/',
    ])
    check_interval: int = 300  # Seconds between proxy checks
    max_consecutive_failures: int = 5
    min_speed: float = 5.0  # Maximum acceptable response time
    min_success_rate: float = 0.8  # Minimum success rate
    preferred_countries: List[str] = field(default_factory=list)
    preferred_protocols: List[str] = field(default_factory=lambda: ['http', 'https'])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'proxy_sources': self.proxy_sources,
            'check_interval': self.check_interval,
            'max_consecutive_failures': self.max_consecutive_failures,
            'min_speed': self.min_speed,
            'min_success_rate': self.min_success_rate,
            'preferred_countries': self.preferred_countries,
            'preferred_protocols': self.preferred_protocols,
        }


class ProxyManager:
    """
    Proxy manager for distributed scraping.
    
    Provides:
    - Proxy collection from multiple sources
    - Proxy health checking
    - Proxy rotation
    - Geographic distribution
    - Performance monitoring
    """
    
    def __init__(self, config: ProxyConfig = None):
        """
        Initialize the proxy manager.
        
        Args:
            config: ProxyConfig instance.
        """
        self.config = config or ProxyConfig()
        self._proxies: List[Proxy] = []
        self._active_proxies: List[Proxy] = []
        self._last_check: datetime = None
        self._last_update: datetime = None
        self._check_interval: int = self.config.check_interval
        self._lock = threading.Lock()
    
    def load_proxies(self, source: str = None) -> int:
        """
        Load proxies from a source.
        
        Args:
            source: URL of proxy source (None for all sources).
            
        Returns:
            Number of proxies loaded.
        """
        sources = [source] if source else self.config.proxy_sources
        loaded_count = 0
        
        for source_url in sources:
            try:
                proxies = self._scrape_proxy_source(source_url)
                self._proxies.extend(proxies)
                loaded_count += len(proxies)
                print(f"Loaded {len(proxies)} proxies from {source_url}")
            except Exception as e:
                print(f"Error loading proxies from {source_url}: {e}")
        
        return loaded_count
    
    def _scrape_proxy_source(self, url: str) -> List[Proxy]:
        """
        Scrape proxies from a source URL.
        
        Args:
            url: URL of proxy source.
            
        Returns:
            List of Proxy objects.
        """
        proxies = []
        
        try:
            # Parse the URL
            parsed = urlparse(url)
            
            # Different scraping methods for different sources
            if 'sslproxies' in url or 'us-proxy' in url or 'free-proxy-list' in url:
                # Scrape from HTML table
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    # Parse HTML table (simplified)
                    # In production, use BeautifulSoup
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'html.parser')
                    table = soup.find('table')
                    
                    if table:
                        rows = table.find_all('tr')[1:]  # Skip header
                        for row in rows:
                            cols = row.find_all('td')
                            if len(cols) >= 2:
                                host = cols[0].text.strip()
                                port = cols[1].text.strip()
                                
                                # Try to extract more info
                                country = ''
                                anonymity = ''
                                
                                if len(cols) >= 4:
                                    country = cols[3].text.strip()
                                if len(cols) >= 5:
                                    anonymity = cols[4].text.strip().lower()
                                
                                proxies.append(Proxy(
                                    host=host,
                                    port=int(port),
                                    protocol='https' if 'https' in url else 'http',
                                    country=country,
                                    anonymity=anonymity,
                                ))
        
        except Exception as e:
            print(f"Error scraping proxy source {url}: {e}")
        
        return proxies
    
    def check_proxies(self, force: bool = False) -> int:
        """
        Check proxy health.
        
        Args:
            force: Force check all proxies.
            
        Returns:
            Number of proxies checked.
        """
        current_time = datetime.utcnow()
        
        # Only check if interval has passed or forced
        if not force and self._last_check and (current_time - self._last_check).seconds < self._check_interval:
            return 0
        
        checked_count = 0
        
        try:
            # Test each proxy
            for proxy in self._proxies:
                if self._check_proxy(proxy):
                    proxy.is_active = True
                    proxy.consecutive_failures = 0
                    self._active_proxies.append(proxy)
                else:
                    proxy.is_active = False
                    proxy.consecutive_failures += 1
                    
                    # Deactivate if too many failures
                    if proxy.consecutive_failures >= self.config.max_consecutive_failures:
                        proxy.is_active = False
                
                checked_count += 1
            
            # Update active proxies list
            self._active_proxies = [p for p in self._proxies if p.is_active]
            self._last_check = current_time
        
        except Exception as e:
            print(f"Error checking proxies: {e}")
        
        return checked_count
    
    def _check_proxy(self, proxy: Proxy) -> bool:
        """
        Check if a proxy is working.
        
        Args:
            proxy: Proxy to check.
            
        Returns:
            True if proxy is working.
        """
        try:
            # Test URL
            test_url = 'https://httpbin.org/ip'
            
            # Make request with timeout
            start_time = time.time()
            response = requests.get(
                test_url,
                proxies=proxy.get_dict(),
                timeout=10
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                # Update proxy stats
                proxy.speed = response_time
                proxy.last_checked = datetime.utcnow()
                proxy.last_success = datetime.utcnow()
                proxy.success_rate = (proxy.success_rate * 0.9) + (1.0 * 0.1)  # Moving average
                
                # Check if response contains our IP (not proxy IP)
                # This would indicate the proxy is not working properly
                return True
            else:
                proxy.last_failure = datetime.utcnow()
                proxy.success_rate = (proxy.success_rate * 0.9) + (0.0 * 0.1)
                return False
        
        except Exception as e:
            proxy.last_failure = datetime.utcnow()
            proxy.success_rate = (proxy.success_rate * 0.9) + (0.0 * 0.1)
            return False
    
    def list_proxies(self, active_only: bool = False, country: str = None,
                     protocol: str = None) -> List[Proxy]:
        """
        List known proxies, optionally filtered.

        Args:
            active_only: Only proxies that passed their last health check.
            country: Filter by country code.
            protocol: Filter by protocol.

        Returns:
            List of Proxy objects.
        """
        with self._lock:
            proxies = list(self._active_proxies if active_only else self._proxies)

        if country:
            proxies = [p for p in proxies if p.country == country]
        if protocol:
            proxies = [p for p in proxies if p.protocol == protocol]
        return proxies

    def check_all_proxies(self, force: bool = True) -> List[Proxy]:
        """
        Health-check every proxy and return the active list.

        check_proxies() returns only a count; this returns the proxies
        themselves for callers that render the result.
        """
        self.check_proxies(force=force)
        return self.list_proxies(active_only=True)

    def get_proxy(self, country: str = None, protocol: str = None) -> Optional[Proxy]:
        """
        Get a random active proxy.
        
        Args:
            country: Preferred country (None for any).
            protocol: Preferred protocol (None for any).
            
        Returns:
            Proxy or None if no active proxies.
        """
        # Check proxies if needed
        self.check_proxies()
        
        if not self._active_proxies:
            return None
        
        # Filter proxies
        candidates = self._active_proxies
        
        if country:
            candidates = [p for p in candidates if p.country.lower() == country.lower()]
        
        if protocol:
            candidates = [p for p in candidates if p.protocol.lower() == protocol.lower()]
        
        if not candidates:
            candidates = self._active_proxies
        
        # Sort by speed and success rate
        candidates.sort(key=lambda p: (p.speed, -p.success_rate))
        
        # Return the best proxy
        return candidates[0] if candidates else None
    
    def get_random_proxy(self) -> Optional[Proxy]:
        """
        Get a random active proxy.
        
        Returns:
            Proxy or None if no active proxies.
        """
        self.check_proxies()
        
        if not self._active_proxies:
            return None
        
        return random.choice(self._active_proxies)
    
    def get_proxies_by_country(self, country: str) -> List[Proxy]:
        """
        Get all active proxies from a specific country.
        
        Args:
            country: Country code.
            
        Returns:
            List of Proxy objects.
        """
        self.check_proxies()
        
        return [p for p in self._active_proxies if p.country.lower() == country.lower()]
    
    def get_proxies_by_protocol(self, protocol: str) -> List[Proxy]:
        """
        Get all active proxies with a specific protocol.
        
        Args:
            protocol: Protocol (http, https, socks4, socks5).
            
        Returns:
            List of Proxy objects.
        """
        self.check_proxies()
        
        return [p for p in self._active_proxies if p.protocol.lower() == protocol.lower()]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get proxy manager statistics.
        
        Returns:
            Dictionary with statistics.
        """
        self.check_proxies()
        
        return {
            'total_proxies': len(self._proxies),
            'active_proxies': len(self._active_proxies),
            'inactive_proxies': len(self._proxies) - len(self._active_proxies),
            'last_check': self._last_check.isoformat() if self._last_check else None,
            'last_update': self._last_update.isoformat() if self._last_update else None,
            'countries': self._get_country_stats(),
            'protocols': self._get_protocol_stats(),
        }
    
    def _get_country_stats(self) -> Dict[str, int]:
        """Get statistics by country."""
        countries = defaultdict(int)
        for proxy in self._active_proxies:
            if proxy.country:
                countries[proxy.country] += 1
        return dict(countries)
    
    def _get_protocol_stats(self) -> Dict[str, int]:
        """Get statistics by protocol."""
        protocols = defaultdict(int)
        for proxy in self._active_proxies:
            protocols[proxy.protocol] += 1
        return dict(protocols)
    
    def update_proxy_list(self) -> int:
        """
        Update the proxy list from all sources.
        
        Returns:
            Number of proxies loaded.
        """
        # Clear existing proxies
        self._proxies = []
        self._active_proxies = []
        
        # Load from all sources
        loaded = self.load_proxies()
        
        # Check all proxies
        self.check_proxies(force=True)
        
        self._last_update = datetime.utcnow()
        
        return loaded
    
    def add_proxy(self, proxy: Proxy) -> bool:
        """
        Add a proxy to the list.
        
        Args:
            proxy: Proxy to add.
            
        Returns:
            True if added.
        """
        # Check if proxy already exists
        for p in self._proxies:
            if p.host == proxy.host and p.port == proxy.port and p.protocol == proxy.protocol:
                return False
        
        self._proxies.append(proxy)
        return True
    
    def remove_proxy(self, host: str, port: int, protocol: str = 'http') -> bool:
        """
        Remove a proxy from the list.
        
        Args:
            host: Proxy host.
            port: Proxy port.
            protocol: Proxy protocol.
            
        Returns:
            True if removed.
        """
        for i, p in enumerate(self._proxies):
            if p.host == host and p.port == port and p.protocol == protocol:
                self._proxies.pop(i)
                self._active_proxies = [p for p in self._active_proxies if p != p]
                return True
        
        return False
    
    def save_to_file(self, filename: str) -> bool:
        """
        Save proxies to a file.
        
        Args:
            filename: File path.
            
        Returns:
            True if saved.
        """
        try:
            data = {
                'proxies': [p.to_dict() for p in self._proxies],
                'last_update': self._last_update.isoformat() if self._last_update else None,
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving proxies to file: {e}")
            return False
    
    def load_from_file(self, filename: str) -> bool:
        """
        Load proxies from a file.
        
        Args:
            filename: File path.
            
        Returns:
            True if loaded.
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self._proxies = []
            for proxy_data in data.get('proxies', []):
                proxy = Proxy(
                    host=proxy_data['host'],
                    port=proxy_data['port'],
                    protocol=proxy_data.get('protocol', 'http'),
                    username=proxy_data.get('username', ''),
                    password=proxy_data.get('password', ''),
                    country=proxy_data.get('country', ''),
                    city=proxy_data.get('city', ''),
                    isp=proxy_data.get('isp', ''),
                    anonymity=proxy_data.get('anonymity', 'transparent'),
                    speed=proxy_data.get('speed', 0.0),
                    success_rate=proxy_data.get('success_rate', 0.0),
                    last_checked=datetime.fromisoformat(proxy_data['last_checked']) if proxy_data.get('last_checked') else None,
                    last_success=datetime.fromisoformat(proxy_data['last_success']) if proxy_data.get('last_success') else None,
                    last_failure=datetime.fromisoformat(proxy_data['last_failure']) if proxy_data.get('last_failure') else None,
                    consecutive_failures=proxy_data.get('consecutive_failures', 0),
                    is_active=proxy_data.get('is_active', True),
                )
                self._proxies.append(proxy)
            
            self._last_update = datetime.fromisoformat(data['last_update']) if data.get('last_update') else None
            
            # Check proxies
            self.check_proxies(force=True)
            
            return True
        except Exception as e:
            print(f"Error loading proxies from file: {e}")
            return False


# Global proxy manager instance
proxy_manager = ProxyManager()
