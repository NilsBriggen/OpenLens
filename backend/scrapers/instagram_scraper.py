"""
Instagram Scraper for OpenLens

Scrapes public Instagram profiles, posts, and stories using instaloader.

Dependencies:
- instaloader: For Instagram scraping
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import instaloader
from instaloader import Instaloader, Profile, Post, Story, Hashtag


@dataclass
class InstagramPost:
    """Represents an Instagram post with metadata."""
    id: str
    shortcode: str
    caption: Optional[str] = None
    timestamp: Optional[datetime] = None
    likes: int = 0
    comments: int = 0
    views: int = 0
    url: Optional[str] = None
    media_url: Optional[str] = None
    media_type: str = "image"  # "image", "video", "album"
    hashtags: List[str] = None
    mentions: List[str] = None
    location: Optional[str] = None
    geotag: Optional[Dict[str, float]] = None

    def __post_init__(self):
        if self.hashtags is None:
            self.hashtags = []
        if self.mentions is None:
            self.mentions = []


@dataclass
class InstagramUser:
    """Represents an Instagram user profile."""
    id: str
    username: str
    full_name: str
    bio: Optional[str] = None
    url: Optional[str] = None
    followers: int = 0
    following: int = 0
    posts: int = 0
    is_verified: bool = False
    is_private: bool = False
    profile_pic_url: Optional[str] = None
    website: Optional[str] = None
    business_category: Optional[str] = None


class InstagramScraper:
    """
    Scrapes public data from Instagram using instaloader.
    
    Note: Requires Instagram login for private profiles.
    Public profiles can be scraped without authentication.
    """

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        rate_limit_delay: float = 1.0,
    ):
        """
        Initialize the Instagram scraper.
        
        Args:
            username: Instagram username (for authentication).
            password: Instagram password (for authentication).
            rate_limit_delay: Delay between requests (in seconds).
        """
        self.username = username
        self.password = password
        self.rate_limit_delay = rate_limit_delay
        self.L = Instaloader()
        
        # Login if credentials are provided
        if self.username and self.password:
            try:
                self.L.login(self.username, self.password)
            except Exception as e:
                print(f"Failed to login to Instagram: {e}")

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract hashtags and mentions from text.
        
        Args:
            text: Input text.
            
        Returns:
            Dictionary with lists of hashtags and mentions.
        """
        return {
            "hashtags": re.findall(r'#(\w+)', text),
            "mentions": re.findall(r'@(\w+)', text),
        }

    def scrape_user_profile(self, username: str) -> Optional[InstagramUser]:
        """
        Scrape an Instagram user profile.
        
        Args:
            username: Instagram username.
            
        Returns:
            InstagramUser object or None if failed.
        """
        try:
            profile = Profile.from_username(self.L.context, username)
            
            return InstagramUser(
                id=str(profile.userid),
                username=profile.username,
                full_name=profile.full_name,
                bio=profile.biography,
                url=f"https://www.instagram.com/{profile.username}/",
                followers=profile.followers,
                following=profile.followees,
                posts=profile.mediacount,
                is_verified=profile.is_verified,
                is_private=profile.is_private,
                profile_pic_url=profile.profile_pic_url,
                website=profile.external_url,
                business_category=profile.business_category_name,
            )
        except Exception as e:
            print(f"Failed to scrape user profile: {e}")
            return None

    def scrape_user_posts(
        self,
        username: str,
        limit: int = 10,
    ) -> List[InstagramPost]:
        """
        Scrape posts from an Instagram user profile.
        
        Args:
            username: Instagram username.
            limit: Maximum number of posts to scrape.
            
        Returns:
            List of InstagramPost objects.
        """
        posts = []
        
        try:
            profile = Profile.from_username(self.L.context, username)
            
            for i, post in enumerate(profile.get_posts()):
                if i >= limit:
                    break
                
                # Extract entities from caption
                entities = self._extract_entities(post.caption)
                
                # Extract geotag
                geotag = None
                if post.location:
                    geotag = {
                        "latitude": post.location.lat,
                        "longitude": post.location.lng,
                    }
                
                # Determine media type
                media_type = "image"
                if post.is_video:
                    media_type = "video"
                elif post.typename == "GraphSidecar":
                    media_type = "album"
                
                posts.append(InstagramPost(
                    id=str(post.userid),
                    shortcode=post.shortcode,
                    caption=post.caption,
                    timestamp=post.date_utc,
                    likes=post.likes,
                    comments=post.comments,
                    views=post.video_view_count if post.is_video else 0,
                    url=f"https://www.instagram.com/p/{post.shortcode}/",
                    media_url=post.url,
                    media_type=media_type,
                    hashtags=entities["hashtags"],
                    mentions=entities["mentions"],
                    location=post.location.name if post.location else None,
                    geotag=geotag,
                ))
        except Exception as e:
            print(f"Failed to scrape user posts: {e}")
        
        return posts

    def scrape_hashtag_posts(
        self,
        hashtag: str,
        limit: int = 10,
    ) -> List[InstagramPost]:
        """
        Scrape posts by hashtag.
        
        Args:
            hashtag: Instagram hashtag (without #).
            limit: Maximum number of posts to scrape.
            
        Returns:
            List of InstagramPost objects.
        """
        posts = []
        
        try:
            hashtag_obj = Hashtag.from_name(self.L.context, hashtag)
            
            for i, post in enumerate(hashtag_obj.get_top_posts()):
                if i >= limit:
                    break
                
                # Extract entities from caption
                entities = self._extract_entities(post.caption)
                
                # Extract geotag
                geotag = None
                if post.location:
                    geotag = {
                        "latitude": post.location.lat,
                        "longitude": post.location.lng,
                    }
                
                # Determine media type
                media_type = "image"
                if post.is_video:
                    media_type = "video"
                elif post.typename == "GraphSidecar":
                    media_type = "album"
                
                posts.append(InstagramPost(
                    id=str(post.userid),
                    shortcode=post.shortcode,
                    caption=post.caption,
                    timestamp=post.date_utc,
                    likes=post.likes,
                    comments=post.comments,
                    views=post.video_view_count if post.is_video else 0,
                    url=f"https://www.instagram.com/p/{post.shortcode}/",
                    media_url=post.url,
                    media_type=media_type,
                    hashtags=entities["hashtags"],
                    mentions=entities["mentions"],
                    location=post.location.name if post.location else None,
                    geotag=geotag,
                ))
        except Exception as e:
            print(f"Failed to scrape hashtag posts: {e}")
        
        return posts

    def scrape_post(self, shortcode: str) -> Optional[InstagramPost]:
        """
        Scrape a single Instagram post by shortcode.
        
        Args:
            shortcode: Instagram post shortcode (e.g., "ABC123").
            
        Returns:
            InstagramPost object or None if failed.
        """
        try:
            post = Post.from_shortcode(self.L.context, shortcode)
            
            # Extract entities from caption
            entities = self._extract_entities(post.caption)
            
            # Extract geotag
            geotag = None
            if post.location:
                geotag = {
                    "latitude": post.location.lat,
                    "longitude": post.location.lng,
                }
            
            # Determine media type
            media_type = "image"
            if post.is_video:
                media_type = "video"
            elif post.typename == "GraphSidecar":
                media_type = "album"
            
            return InstagramPost(
                id=str(post.userid),
                shortcode=post.shortcode,
                caption=post.caption,
                timestamp=post.date_utc,
                likes=post.likes,
                comments=post.comments,
                views=post.video_view_count if post.is_video else 0,
                url=f"https://www.instagram.com/p/{post.shortcode}/",
                media_url=post.url,
                media_type=media_type,
                hashtags=entities["hashtags"],
                mentions=entities["mentions"],
                location=post.location.name if post.location else None,
                geotag=geotag,
            )
        except Exception as e:
            print(f"Failed to scrape post: {e}")
            return None

    def search_users(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for Instagram users by name or username.
        
        Args:
            query: Search query.
            limit: Maximum number of results.
            
        Returns:
            List of user dictionaries.
        """
        users = []
        
        try:
            # Instagram does not have a direct search API in instaloader,
            # so we use a workaround by searching for profiles
            for profile in self.L.get_profiles([query]):
                users.append({
                    "username": profile.username,
                    "full_name": profile.full_name,
                    "url": f"https://www.instagram.com/{profile.username}/",
                })
        except Exception as e:
            print(f"Failed to search users: {e}")
        
        return users[:limit]


# Singleton instance for easy use
instagram_scraper = InstagramScraper()
