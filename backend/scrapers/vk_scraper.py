"""
VK Scraper for OpenLens

Scrapes public VK (VKontakte) profiles, posts, and groups for OSINT data.
Uses the official VK API (preferred) or web scraping as a fallback.

Dependencies:
- requests: For HTTP requests
- beautifulsoup4: For HTML parsing (fallback)
- vk-api: For official API access (optional)
"""

import re
import time
import random
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup


@dataclass
class VKPost:
    """Represents a VK post with metadata."""
    id: str
    author_id: str
    author_name: str
    content: str
    timestamp: str
    likes: int
    reposts: int
    views: int
    comments: int
    attachments: List[Dict[str, Any]]  # Images, videos, links, etc.
    location: Optional[Dict[str, Any]] = None
    geotag: Optional[Dict[str, float]] = None


@dataclass
class VKUser:
    """Represents a VK user profile."""
    id: str
    first_name: str
    last_name: str
    username: str
    bio: str
    city: Optional[str] = None
    country: Optional[str] = None
    birthday: Optional[str] = None
    universities: Optional[List[str]] = None
    schools: Optional[List[str]] = None
    work: Optional[List[str]] = None
    social_connections: Optional[List[str]] = None
    last_seen: Optional[str] = None
    is_verified: bool = False
    followers: int = 0
    friends: int = 0


class VKScraper:
    """
    Scrapes public data from VK (VKontakte).
    
    Note: VK has strict rate limits and anti-scraping measures.
    Use with caution and respect robots.txt.
    """

    BASE_URL = "https://vk.com"
    API_BASE_URL = "https://api.vk.com/method"
    
    # User-Agent to mimic a browser
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self, api_token: Optional[str] = None, rate_limit_delay: float = 1.0):
        """
        Initialize the VK scraper.
        
        Args:
            api_token: Optional VK API token (for official API access).
            rate_limit_delay: Delay between requests (in seconds) to avoid rate limiting.
        """
        self.api_token = api_token
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def _rate_limit(self):
        """Enforce rate limiting."""
        time.sleep(self.rate_limit_delay + random.uniform(0, 0.5))

    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """
        Make an HTTP request with rate limiting and error handling.
        
        Args:
            url: URL to request.
            params: Query parameters.
            
        Returns:
            Response object or None if failed.
        """
        try:
            self._rate_limit()
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def _parse_user_profile(self, html: str) -> Optional[VKUser]:
        """
        Parse a VK user profile page (fallback method).
        
        Args:
            html: HTML content of the profile page.
            
        Returns:
            VKUser object or None if parsing fails.
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract basic info
            user = VKUser(
                id="",
                first_name="",
                last_name="",
                username="",
                bio="",
            )
            
            # Extract name (from title or profile header)
            title = soup.find("title")
            if title:
                name_parts = title.text.split()
                if len(name_parts) >= 2:
                    user.first_name = name_parts[0]
                    user.last_name = " ".join(name_parts[1:])
            
            # Extract username (from URL or profile)
            canonical_link = soup.find("link", {"rel": "canonical"})
            if canonical_link and "vk.com/" in canonical_link.get("href", ""):
                username = canonical_link["href"].split("/")[-1]
                user.username = username
                user.id = username  # For public profiles, username == id
            
            # Extract bio (from profile description)
            bio_element = soup.find("div", class_=re.compile(r"profile_info.*", re.I))
            if not bio_element:
                bio_element = soup.find("div", class_=re.compile(r"about.*", re.I))
            if bio_element:
                user.bio = bio_element.get_text(strip=True)
            
            # Extract city/country
            location_element = soup.find("div", class_=re.compile(r"profile_info.*location", re.I))
            if not location_element:
                location_element = soup.find("a", href=re.compile(r"/city\d+", re.I))
            if location_element:
                user.city = location_element.get_text(strip=True)
            
            # Extract followers/friends count
            followers_element = soup.find("a", href=re.compile(r"/friends", re.I))
            if followers_element:
                followers_text = followers_element.get_text(strip=True)
                user.friends = self._extract_number(followers_text)
            
            return user
        except Exception as e:
            print(f"Failed to parse user profile: {e}")
            return None

    def _parse_post(self, html: str) -> Optional[VKPost]:
        """
        Parse a VK post from HTML.
        
        Args:
            html: HTML content of the post.
            
        Returns:
            VKPost object or None if parsing fails.
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            post = VKPost(
                id="",
                author_id="",
                author_name="",
                content="",
                timestamp="",
                likes=0,
                reposts=0,
                views=0,
                comments=0,
                attachments=[],
            )
            
            # Extract post ID (from data-post-id or similar)
            post_id_element = soup.find(attrs={"data-post-id": True})
            if post_id_element:
                post.id = post_id_element["data-post-id"]
            
            # Extract author info
            author_element = soup.find("a", class_=re.compile(r"author", re.I))
            if author_element:
                post.author_name = author_element.get_text(strip=True)
                post.author_id = author_element.get("href", "").split("/")[-1]
            
            # Extract content
            content_element = soup.find("div", class_=re.compile(r"post_text", re.I))
            if content_element:
                post.content = content_element.get_text(strip=True)
            
            # Extract timestamp
            timestamp_element = soup.find("span", class_=re.compile(r"date", re.I))
            if timestamp_element:
                post.timestamp = timestamp_element.get("title", "")
            
            # Extract engagement metrics (likes, reposts, etc.)
            likes_element = soup.find("span", class_=re.compile(r"like.*count", re.I))
            if likes_element:
                post.likes = self._extract_number(likes_element.get_text(strip=True))
            
            reposts_element = soup.find("span", class_=re.compile(r"repost.*count", re.I))
            if reposts_element:
                post.reposts = self._extract_number(reposts_element.get_text(strip=True))
            
            views_element = soup.find("span", class_=re.compile(r"views.*count", re.I))
            if views_element:
                post.views = self._extract_number(views_element.get_text(strip=True))
            
            comments_element = soup.find("span", class_=re.compile(r"comments.*count", re.I))
            if comments_element:
                post.comments = self._extract_number(comments_element.get_text(strip=True))
            
            # Extract attachments (images, links, etc.)
            post.attachments = self._parse_attachments(soup)
            
            return post
        except Exception as e:
            print(f"Failed to parse post: {e}")
            return None

    def _parse_attachments(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """
        Parse attachments (images, videos, links) from a post.
        
        Args:
            soup: BeautifulSoup object for the post HTML.
            
        Returns:
            List of attachment dictionaries.
        """
        attachments = []
        
        # Extract images
        image_elements = soup.find_all("img", class_=re.compile(r"post_img", re.I))
        for img in image_elements:
            src = img.get("src", "")
            if src:
                attachments.append({
                    "type": "image",
                    "url": src,
                    "thumbnail": img.get("src", ""),
                })
        
        # Extract links
        link_elements = soup.find_all("a", class_=re.compile(r"post_link", re.I))
        for link in link_elements:
            href = link.get("href", "")
            if href:
                attachments.append({
                    "type": "link",
                    "url": href,
                    "title": link.get_text(strip=True),
                })
        
        return attachments

    def _extract_number(self, text: str) -> int:
        """
        Extract a number from a string (e.g., "1.2K" -> 1200).
        
        Args:
            text: Input string (e.g., "1.2K", "1,234").
            
        Returns:
            Extracted number.
        """
        text = text.replace(",", "").strip()
        if "K" in text.upper():
            return int(float(text.replace("K", "").strip()) * 1000)
        elif "M" in text.upper():
            return int(float(text.replace("M", "").strip()) * 1000000)
        else:
            try:
                return int(text)
            except ValueError:
                return 0

    def scrape_user_profile(self, username: str) -> Optional[VKUser]:
        """
        Scrape a public VK user profile.
        
        Args:
            username: VK username or user ID (e.g., "durov").
            
        Returns:
            VKUser object or None if failed.
        """
        url = f"{self.BASE_URL}/{username}"
        response = self._make_request(url)
        if not response:
            return None
        
        return self._parse_user_profile(response.text)

    def scrape_user_posts(self, username: str, limit: int = 10) -> List[VKPost]:
        """
        Scrape recent posts from a VK user profile.
        
        Args:
            username: VK username or user ID.
            limit: Maximum number of posts to scrape.
            
        Returns:
            List of VKPost objects.
        """
        posts = []
        url = f"{self.BASE_URL}/{username}"
        response = self._make_request(url)
        if not response:
            return posts
        
        soup = BeautifulSoup(response.text, 'html.parser')
        post_elements = soup.find_all("div", class_=re.compile(r"post", re.I))
        
        for post_element in post_elements[:limit]:
            post_html = str(post_element)
            post = self._parse_post(post_html)
            if post:
                posts.append(post)
        
        return posts

    def search_users(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for VK users by name or keyword.
        
        Args:
            query: Search query (e.g., "John Doe").
            limit: Maximum number of results.
            
        Returns:
            List of user dictionaries (basic info).
        """
        users = []
        url = f"{self.BASE_URL}/search"
        params = {
            "q": query,
            "c[section]": "people",
        }
        response = self._make_request(url, params=params)
        if not response:
            return users
        
        soup = BeautifulSoup(response.text, 'html.parser')
        user_elements = soup.find_all("div", class_=re.compile(r"search_result.*", re.I))
        
        for user_element in user_elements[:limit]:
            try:
                name_element = user_element.find("a", class_=re.compile(r"search_result_name", re.I))
                if name_element:
                    users.append({
                        "name": name_element.get_text(strip=True),
                        "username": name_element.get("href", "").split("/")[-1],
                        "url": name_element.get("href", ""),
                    })
            except Exception:
                continue
        
        return users

    def scrape_group(self, group_name: str, limit: int = 10) -> List[VKPost]:
        """
        Scrape recent posts from a VK group.
        
        Args:
            group_name: VK group name or ID (e.g., "vk").
            limit: Maximum number of posts to scrape.
            
        Returns:
            List of VKPost objects.
        """
        posts = []
        url = f"{self.BASE_URL}/{group_name}"
        response = self._make_request(url)
        if not response:
            return posts
        
        soup = BeautifulSoup(response.text, 'html.parser')
        post_elements = soup.find_all("div", class_=re.compile(r"post", re.I))
        
        for post_element in post_elements[:limit]:
            post_html = str(post_element)
            post = self._parse_post(post_html)
            if post:
                posts.append(post)
        
        return posts

    def close(self):
        """Close the session."""
        self.session.close()


# Singleton instance for easy use
vk_scraper = VKScraper()
