"""
User Agent Manager for OpenLens Distributed Scraping

Provides user agent management capabilities:
- User agent rotation
- Browser fingerprinting
- Device emulation
- User agent parsing
- Custom user agent generation
"""

import os
import time
import random
import json
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict


@dataclass
class UserAgent:
    """Represents a user agent string."""
    string: str
    browser: str = ''
    browser_version: str = ''
    os: str = ''
    os_version: str = ''
    device: str = ''
    device_type: str = 'desktop'  # desktop, mobile, tablet
    is_bot: bool = False
    usage_count: int = 0
    last_used: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'string': self.string,
            'browser': self.browser,
            'browser_version': self.browser_version,
            'os': self.os,
            'os_version': self.os_version,
            'device': self.device,
            'device_type': self.device_type,
            'is_bot': self.is_bot,
            'usage_count': self.usage_count,
            'last_used': self.last_used.isoformat() if self.last_used else None,
        }


@dataclass
class UserAgentConfig:
    """Configuration for user agent manager."""
    rotation_strategy: str = 'random'  # random, round_robin, least_used
    max_usage_per_agent: int = 100
    refresh_interval: int = 3600  # Seconds between refreshes
    preferred_browsers: List[str] = field(default_factory=lambda: ['chrome', 'firefox', 'safari', 'edge'])
    preferred_devices: List[str] = field(default_factory=lambda: ['desktop', 'mobile'])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'rotation_strategy': self.rotation_strategy,
            'max_usage_per_agent': self.max_usage_per_agent,
            'refresh_interval': self.refresh_interval,
            'preferred_browsers': self.preferred_browsers,
            'preferred_devices': self.preferred_devices,
        }


class UserAgentManager:
    """
    User agent manager for distributed scraping.
    
    Provides:
    - User agent rotation
    - Browser fingerprinting
    - Device emulation
    - User agent parsing
    - Custom user agent generation
    """
    
    def __init__(self, config: UserAgentConfig = None):
        """
        Initialize the user agent manager.
        
        Args:
            config: UserAgentConfig instance.
        """
        self.config = config or UserAgentConfig()
        self._user_agents: List[UserAgent] = []
        self._current_index: int = 0
        self._last_refresh: datetime = None
        self._lock = False  # Simplified lock for thread safety
        
        # Load default user agents
        self._load_default_user_agents()
    
    def _load_default_user_agents(self):
        """Load default user agents."""
        default_agents = [
            # Chrome
            {
                'string': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'browser': 'chrome',
                'browser_version': '91.0.4472.124',
                'os': 'windows',
                'os_version': '10',
                'device': 'desktop',
                'device_type': 'desktop',
                'is_bot': False,
            },
            {
                'string': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'browser': 'chrome',
                'browser_version': '91.0.4472.124',
                'os': 'macos',
                'os_version': '10.15.7',
                'device': 'desktop',
                'device_type': 'desktop',
                'is_bot': False,
            },
            {
                'string': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'browser': 'chrome',
                'browser_version': '91.0.4472.124',
                'os': 'linux',
                'os_version': '',
                'device': 'desktop',
                'device_type': 'desktop',
                'is_bot': False,
            },
            # Firefox
            {
                'string': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
                'browser': 'firefox',
                'browser_version': '89.0',
                'os': 'windows',
                'os_version': '10',
                'device': 'desktop',
                'device_type': 'desktop',
                'is_bot': False,
            },
            {
                'string': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',
                'browser': 'firefox',
                'browser_version': '89.0',
                'os': 'macos',
                'os_version': '10.15',
                'device': 'desktop',
                'device_type': 'desktop',
                'is_bot': False,
            },
            # Safari
            {
                'string': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
                'browser': 'safari',
                'browser_version': '14.1.1',
                'os': 'macos',
                'os_version': '10.15.7',
                'device': 'desktop',
                'device_type': 'desktop',
                'is_bot': False,
            },
            # Edge
            {
                'string': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
                'browser': 'edge',
                'browser_version': '91.0.864.59',
                'os': 'windows',
                'os_version': '10',
                'device': 'desktop',
                'device_type': 'desktop',
                'is_bot': False,
            },
            # Mobile
            {
                'string': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                'browser': 'safari',
                'browser_version': '14.0',
                'os': 'ios',
                'os_version': '14.6',
                'device': 'iphone',
                'device_type': 'mobile',
                'is_bot': False,
            },
            {
                'string': 'Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
                'browser': 'chrome',
                'browser_version': '91.0.4472.120',
                'os': 'android',
                'os_version': '10',
                'device': 'samsung',
                'device_type': 'mobile',
                'is_bot': False,
            },
            # Tablet
            {
                'string': 'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
                'browser': 'safari',
                'browser_version': '14.0',
                'os': 'ios',
                'os_version': '14.6',
                'device': 'ipad',
                'device_type': 'tablet',
                'is_bot': False,
            },
        ]
        
        for agent_data in default_agents:
            self._user_agents.append(UserAgent(**agent_data))
    
    def list_user_agents(self, browser: str = None,
                         device_type: str = None) -> List[str]:
        """List user-agent strings, optionally filtered."""
        return [ua.string for ua in self.list_user_agent_objects(browser, device_type)]

    def list_user_agent_objects(self, browser: str = None,
                                device_type: str = None) -> List["UserAgent"]:
        """List UserAgent objects, optionally filtered."""
        agents = list(self._user_agents)
        if browser:
            agents = [ua for ua in agents if ua.browser == browser]
        if device_type:
            agents = [ua for ua in agents if ua.device_type == device_type]
        return agents

    def get_user_agent(self, browser: str = None, device_type: str = None) -> Optional[str]:
        """
        Get a user agent string.
        
        Args:
            browser: Preferred browser (None for any).
            device_type: Preferred device type (None for any).
            
        Returns:
            User agent string or None.
        """
        # Refresh if needed
        self._refresh_if_needed()
        
        if not self._user_agents:
            return None
        
        # Filter user agents
        candidates = self._user_agents
        
        if browser:
            candidates = [ua for ua in candidates if ua.browser.lower() == browser.lower()]
        
        if device_type:
            candidates = [ua for ua in candidates if ua.device_type.lower() == device_type.lower()]
        
        if not candidates:
            candidates = self._user_agents
        
        # Select based on rotation strategy
        if self.config.rotation_strategy == 'random':
            ua = random.choice(candidates)
        elif self.config.rotation_strategy == 'round_robin':
            ua = candidates[self._current_index % len(candidates)]
            self._current_index += 1
        elif self.config.rotation_strategy == 'least_used':
            ua = min(candidates, key=lambda x: x.usage_count)
        else:
            ua = random.choice(candidates)
        
        # Update usage
        ua.usage_count += 1
        ua.last_used = datetime.utcnow()
        
        # Check if we need to refresh
        if ua.usage_count >= self.config.max_usage_per_agent:
            self._refresh_user_agents()
        
        return ua.string
    
    def get_random_user_agent(self) -> Optional[str]:
        """
        Get a random user agent string.
        
        Returns:
            User agent string or None.
        """
        self._refresh_if_needed()
        
        if not self._user_agents:
            return None
        
        ua = random.choice(self._user_agents)
        ua.usage_count += 1
        ua.last_used = datetime.utcnow()
        
        return ua.string
    
    def get_user_agents_by_browser(self, browser: str) -> List[str]:
        """
        Get all user agents for a specific browser.
        
        Args:
            browser: Browser name.
            
        Returns:
            List of user agent strings.
        """
        self._refresh_if_needed()
        
        return [ua.string for ua in self._user_agents if ua.browser.lower() == browser.lower()]
    
    def get_user_agents_by_device_type(self, device_type: str) -> List[str]:
        """
        Get all user agents for a specific device type.
        
        Args:
            device_type: Device type (desktop, mobile, tablet).
            
        Returns:
            List of user agent strings.
        """
        self._refresh_if_needed()
        
        return [ua.string for ua in self._user_agents if ua.device_type.lower() == device_type.lower()]
    
    def _refresh_if_needed(self):
        """Refresh user agents if needed."""
        current_time = datetime.utcnow()
        
        if not self._last_refresh or (current_time - self._last_refresh).seconds > self.config.refresh_interval:
            self._refresh_user_agents()
    
    def _refresh_user_agents(self):
        """Refresh the user agent list."""
        # Reset usage counts
        for ua in self._user_agents:
            ua.usage_count = 0
        
        # Add some new random user agents
        new_agents = self._generate_random_user_agents(5)
        self._user_agents.extend(new_agents)
        
        self._last_refresh = datetime.utcnow()
    
    def _generate_random_user_agents(self, count: int = 5) -> List[UserAgent]:
        """
        Generate random user agents.
        
        Args:
            count: Number of user agents to generate.
            
        Returns:
            List of UserAgent objects.
        """
        browsers = [
            ('chrome', '91.0.4472.124'),
            ('chrome', '90.0.4430.212'),
            ('chrome', '89.0.4389.114'),
            ('firefox', '89.0'),
            ('firefox', '88.0'),
            ('safari', '14.1.1'),
            ('safari', '14.0.3'),
            ('edge', '91.0.864.59'),
            ('edge', '90.0.818.62'),
        ]
        
        os_list = [
            ('windows', '10'),
            ('windows', '8.1'),
            ('macos', '10.15.7'),
            ('macos', '11.4'),
            ('linux', ''),
        ]
        
        devices = [
            ('desktop', 'Windows PC'),
            ('desktop', 'MacBook Pro'),
            ('desktop', 'Linux Desktop'),
            ('mobile', 'iPhone'),
            ('mobile', 'Samsung Galaxy'),
            ('mobile', 'Google Pixel'),
            ('tablet', 'iPad'),
            ('tablet', 'Samsung Tab'),
        ]
        
        user_agents = []
        
        for _ in range(count):
            browser, browser_version = random.choice(browsers)
            os_name, os_version = random.choice(os_list)
            device_type, device = random.choice(devices)
            
            if browser == 'chrome':
                ua_string = f'Mozilla/5.0 ({os_name} {os_version}; {device_type}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36'
            elif browser == 'firefox':
                ua_string = f'Mozilla/5.0 ({os_name} {os_version}; {device_type}; rv:{browser_version}) Gecko/20100101 Firefox/{browser_version}'
            elif browser == 'safari':
                ua_string = f'Mozilla/5.0 ({os_name} {os_version}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{browser_version} Safari/605.1.15'
            elif browser == 'edge':
                ua_string = f'Mozilla/5.0 ({os_name} {os_version}; {device_type}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36 Edg/{browser_version}'
            else:
                ua_string = f'Mozilla/5.0 ({os_name} {os_version}; {device_type}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36'
            
            user_agents.append(UserAgent(
                string=ua_string,
                browser=browser,
                browser_version=browser_version,
                os=os_name,
                os_version=os_version,
                device=device,
                device_type=device_type,
                is_bot=False,
            ))
        
        return user_agents
    
    def parse_user_agent(self, user_agent_string: str) -> Optional[UserAgent]:
        """
        Parse a user agent string.
        
        Args:
            user_agent_string: User agent string to parse.
            
        Returns:
            UserAgent object or None.
        """
        try:
            # Try to use user_agents library if available
            try:
                from user_agents import parse
                ua = parse(user_agent_string)
                
                return UserAgent(
                    string=user_agent_string,
                    browser=ua.browser.family,
                    browser_version=ua.browser.version_string,
                    os=ua.os.family,
                    os_version=ua.os.version_string,
                    device=ua.device.family,
                    device_type=ua.device.category,
                    is_bot=ua.is_bot,
                )
            except ImportError:
                # Fall back to simple parsing
                pass
            
            # Simple parsing
            browser = 'unknown'
            browser_version = ''
            os_name = 'unknown'
            os_version = ''
            device = 'unknown'
            device_type = 'desktop'
            is_bot = False
            
            # Check for common patterns
            if 'chrome' in user_agent_string.lower():
                browser = 'chrome'
                version_match = re.search(r'Chrome/([\d.]+)', user_agent_string)
                if version_match:
                    browser_version = version_match.group(1)
            elif 'firefox' in user_agent_string.lower():
                browser = 'firefox'
                version_match = re.search(r'Firefox/([\d.]+)', user_agent_string)
                if version_match:
                    browser_version = version_match.group(1)
            elif 'safari' in user_agent_string.lower():
                browser = 'safari'
                version_match = re.search(r'Version/([\d.]+)', user_agent_string)
                if version_match:
                    browser_version = version_match.group(1)
            elif 'edge' in user_agent_string.lower():
                browser = 'edge'
                version_match = re.search(r'Edg/([\d.]+)', user_agent_string)
                if version_match:
                    browser_version = version_match.group(1)
            
            if 'windows' in user_agent_string.lower():
                os_name = 'windows'
                version_match = re.search(r'Windows NT ([\d.]+)', user_agent_string)
                if version_match:
                    os_version = version_match.group(1)
            elif 'mac' in user_agent_string.lower():
                os_name = 'macos'
                version_match = re.search(r'Mac OS X ([\d_]+)', user_agent_string)
                if version_match:
                    os_version = version_match.group(1).replace('_', '.')
            elif 'linux' in user_agent_string.lower():
                os_name = 'linux'
            elif 'android' in user_agent_string.lower():
                os_name = 'android'
                version_match = re.search(r'Android ([\d.]+)', user_agent_string)
                if version_match:
                    os_version = version_match.group(1)
            elif 'iphone' in user_agent_string.lower() or 'ipad' in user_agent_string.lower():
                os_name = 'ios'
                version_match = re.search(r'CPU (?:iPhone )?OS ([\d_]+)', user_agent_string)
                if version_match:
                    os_version = version_match.group(1).replace('_', '.')
            
            if 'mobile' in user_agent_string.lower():
                device_type = 'mobile'
            elif 'tablet' in user_agent_string.lower() or 'ipad' in user_agent_string.lower():
                device_type = 'tablet'
            
            if 'bot' in user_agent_string.lower() or 'crawl' in user_agent_string.lower():
                is_bot = True
            
            return UserAgent(
                string=user_agent_string,
                browser=browser,
                browser_version=browser_version,
                os=os_name,
                os_version=os_version,
                device=device,
                device_type=device_type,
                is_bot=is_bot,
            )
        
        except Exception as e:
            print(f"Error parsing user agent: {e}")
            return None
    
    def add_user_agent(self, user_agent: UserAgent) -> bool:
        """
        Add a user agent to the list.
        
        Args:
            user_agent: UserAgent to add.
            
        Returns:
            True if added.
        """
        # Check if user agent already exists
        for ua in self._user_agents:
            if ua.string == user_agent.string:
                return False
        
        self._user_agents.append(user_agent)
        return True
    
    def remove_user_agent(self, user_agent_string: str) -> bool:
        """
        Remove a user agent from the list.
        
        Args:
            user_agent_string: User agent string to remove.
            
        Returns:
            True if removed.
        """
        for i, ua in enumerate(self._user_agents):
            if ua.string == user_agent_string:
                self._user_agents.pop(i)
                return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get user agent manager statistics.
        
        Returns:
            Dictionary with statistics.
        """
        return {
            'total_user_agents': len(self._user_agents),
            'browsers': self._get_browser_stats(),
            'device_types': self._get_device_type_stats(),
            'last_refresh': self._last_refresh.isoformat() if self._last_refresh else None,
        }
    
    def _get_browser_stats(self) -> Dict[str, int]:
        """Get statistics by browser."""
        browsers = defaultdict(int)
        for ua in self._user_agents:
            browsers[ua.browser] += 1
        return dict(browsers)
    
    def _get_device_type_stats(self) -> Dict[str, int]:
        """Get statistics by device type."""
        device_types = defaultdict(int)
        for ua in self._user_agents:
            device_types[ua.device_type] += 1
        return dict(device_types)
    
    def save_to_file(self, filename: str) -> bool:
        """
        Save user agents to a file.
        
        Args:
            filename: File path.
            
        Returns:
            True if saved.
        """
        try:
            data = {
                'user_agents': [ua.to_dict() for ua in self._user_agents],
                'last_refresh': self._last_refresh.isoformat() if self._last_refresh else None,
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving user agents to file: {e}")
            return False
    
    def load_from_file(self, filename: str) -> bool:
        """
        Load user agents from a file.
        
        Args:
            filename: File path.
            
        Returns:
            True if loaded.
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            self._user_agents = []
            for ua_data in data.get('user_agents', []):
                ua = UserAgent(
                    string=ua_data['string'],
                    browser=ua_data.get('browser', ''),
                    browser_version=ua_data.get('browser_version', ''),
                    os=ua_data.get('os', ''),
                    os_version=ua_data.get('os_version', ''),
                    device=ua_data.get('device', ''),
                    device_type=ua_data.get('device_type', 'desktop'),
                    is_bot=ua_data.get('is_bot', False),
                    usage_count=ua_data.get('usage_count', 0),
                    last_used=datetime.fromisoformat(ua_data['last_used']) if ua_data.get('last_used') else None,
                )
                self._user_agents.append(ua)
            
            self._last_refresh = datetime.fromisoformat(data['last_refresh']) if data.get('last_refresh') else None
            
            return True
        except Exception as e:
            print(f"Error loading user agents from file: {e}")
            return False


# Global user agent manager instance
user_agent_manager = UserAgentManager()


# Import re for parsing
import re
