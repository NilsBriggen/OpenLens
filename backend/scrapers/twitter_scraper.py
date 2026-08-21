"""
Twitter Scraper for OpenLens

Scrapes public tweets, user profiles, and trends using the Twitter API (tweepy).
Falls back to web scraping for public data if API keys are not available.

Dependencies:
- tweepy: For Twitter API access
- requests: For web scraping fallback
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import tweepy
import requests
from bs4 import BeautifulSoup


@dataclass
class Tweet:
    """Represents a tweet with metadata."""
    id: str
    content: str
    username: str
    user_id: str
    display_name: str
    timestamp: datetime
    likes: int
    retweets: int
    replies: int
    quotes: int
    views: Optional[int] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    urls: List[str] = None
    media: List[Dict[str, Any]] = None
    geotag: Optional[Dict[str, float]] = None

    def __post_init__(self):
        if self.hashtags is None:
            self.hashtags = []
        if self.mentions is None:
            self.mentions = []
        if self.urls is None:
            self.urls = []
        if self.media is None:
            self.media = []


@dataclass
class TwitterUser:
    """Represents a Twitter user profile."""
    id: str
    username: str
    display_name: str
    bio: Optional[str] = None
    location: Optional[str] = None
    url: Optional[str] = None
    join_date: Optional[datetime] = None
    followers: int = 0
    following: int = 0
    tweets: int = 0
    likes: int = 0
    verified: bool = False
    profile_image: Optional[str] = None
    banner_image: Optional[str] = None


class TwitterScraper:
    """
    Scrapes public data from Twitter using the Twitter API (tweepy).
    
    Note: Requires Twitter API keys for full functionality.
    Falls back to web scraping for public profiles if no API keys are provided.
    """

    TWITTER_API_URL = "https://api.twitter.com/2"
    TWITTER_WEB_URL = "https://twitter.com"

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None,
        bearer_token: Optional[str] = None,
        rate_limit_delay: float = 1.0,
    ):
        """
        Initialize the Twitter scraper.
        
        Args:
            api_key: Twitter API key.
            api_secret: Twitter API secret.
            access_token: Twitter access token.
            access_token_secret: Twitter access token secret.
            bearer_token: Twitter bearer token (for API v2).
            rate_limit_delay: Delay between requests (in seconds).
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.bearer_token = bearer_token
        self.rate_limit_delay = rate_limit_delay
        self.client = None
        
        # Initialize Twitter API client if credentials are provided
        if self.bearer_token:
            self.client = tweepy.Client(bearer_token=self.bearer_token)
        elif all([api_key, api_secret, access_token, access_token_secret]):
            self.client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
            )

    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract hashtags, mentions, and URLs from text.
        
        Args:
            text: Input text.
            
        Returns:
            Dictionary with lists of hashtags, mentions, and URLs.
        """
        return {
            "hashtags": re.findall(r'#(\w+)', text),
            "mentions": re.findall(r'@(\w+)', text),
            "urls": re.findall(r'https?://[^\s]+', text),
        }

    def scrape_tweets(
        self,
        query: str,
        limit: int = 10,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
    ) -> List[Tweet]:
        """
        Scrape tweets matching a query.
        
        Args:
            query: Search query (e.g., "OSINT", "from:username").
            limit: Maximum number of tweets to scrape.
            since: Start date (inclusive).
            until: End date (inclusive).
            
        Returns:
            List of Tweet objects.
        """
        tweets = []
        
        if self.client:
            # Use Twitter API v2
            try:
                # Build query parameters
                query_params = {
                    "query": query,
                    "max_results": min(limit, 100),  # API limit
                    "tweet.fields": ["created_at", "public_metrics", "geo"],
                    "user.fields": ["username", "name", "verified"],
                    "expansions": ["author_id"],
                }
                
                if since:
                    query_params["start_time"] = since.isoformat()
                if until:
                    query_params["end_time"] = until.isoformat()

                # Fetch tweets
                response = self.client.search_recent_tweets(**query_params)
                
                if response.data:
                    for tweet_data in response.data:
                        user_data = response.includes.get("users", {}).get(tweet_data.author_id)
                        
                        # Extract entities from text
                        entities = self._extract_entities(tweet_data.text)
                        
                        # Extract geotag
                        geotag = None
                        if tweet_data.geo:
                            geotag = {
                                "latitude": tweet_data.geo.coordinates[0],
                                "longitude": tweet_data.geo.coordinates[1],
                            }
                        
                        tweets.append(Tweet(
                            id=str(tweet_data.id),
                            content=tweet_data.text,
                            username=user_data.username if user_data else "",
                            user_id=str(tweet_data.author_id),
                            display_name=user_data.name if user_data else "",
                            timestamp=tweet_data.created_at,
                            likes=tweet_data.public_metrics.get("like_count", 0),
                            retweets=tweet_data.public_metrics.get("retweet_count", 0),
                            replies=tweet_data.public_metrics.get("reply_count", 0),
                            quotes=tweet_data.public_metrics.get("quote_count", 0),
                            hashtags=entities["hashtags"],
                            mentions=entities["mentions"],
                            urls=entities["urls"],
                            geotag=geotag,
                        ))
            except Exception as e:
                print(f"Twitter API error: {e}")
        
        # Fallback: Web scraping (limited functionality)
        if not tweets:
            try:
                tweets = self._scrape_tweets_web(query, limit)
            except Exception as e:
                print(f"Web scraping error: {e}")
        
        return tweets[:limit]

    def _scrape_tweets_web(self, query: str, limit: int = 10) -> List[Tweet]:
        """
        Fallback: Scrape tweets from Twitter web (public data only).
        
        Note: This is a simplified version and may not work reliably due to
        Twitter's anti-scraping measures.
        
        Args:
            query: Search query.
            limit: Maximum number of tweets to scrape.
            
        Returns:
            List of Tweet objects.
        """
        tweets = []
        
        # Try to scrape from Twitter search page
        try:
            url = f"{self.TWITTER_WEB_URL}/search?q={query.replace(' ', '%20')}&src=typed_query"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract tweet elements (Twitter's HTML structure changes frequently)
            tweet_elements = soup.find_all("article", {"data-testid": "tweet"})
            
            for tweet_element in tweet_elements[:limit]:
                try:
                    # Extract username
                    username_element = tweet_element.find("a", {"role": "link"})
                    username = username_element.get("href", "").split("/")[-1] if username_element else ""
                    
                    # Extract display name
                    display_name = username_element.get_text() if username_element else ""
                    
                    # Extract content
                    content_element = tweet_element.find("div", {"lang": True})
                    content = content_element.get_text() if content_element else ""
                    
                    # Extract timestamp
                    timestamp_element = tweet_element.find("time")
                    timestamp_str = timestamp_element.get("datetime", "") if timestamp_element else ""
                    timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")) if timestamp_str else datetime.utcnow()
                    
                    # Extract metrics
                    likes = 0
                    retweets = 0
                    replies = 0
                    
                    # Extract entities
                    entities = self._extract_entities(content)
                    
                    tweets.append(Tweet(
                        id=str(hash(content + username + timestamp_str)),
                        content=content,
                        username=username,
                        user_id="",
                        display_name=display_name,
                        timestamp=timestamp,
                        likes=likes,
                        retweets=retweets,
                        replies=replies,
                        hashtags=entities["hashtags"],
                        mentions=entities["mentions"],
                        urls=entities["urls"],
                    ))
                except Exception:
                    continue
        except Exception as e:
            print(f"Web scraping failed: {e}")
        
        return tweets

    def scrape_user_profile(self, username: str) -> Optional[TwitterUser]:
        """
        Scrape a Twitter user profile.
        
        Args:
            username: Twitter username (without @).
            
        Returns:
            TwitterUser object or None if failed.
        """
        if self.client:
            # Use Twitter API v2
            try:
                response = self.client.get_user(
                    username=username,
                    user_fields=["description", "location", "url", "created_at", 
                                "public_metrics", "verified", "profile_image_url", 
                                "profile_banner_url"],
                )
                
                user_data = response.data
                
                return TwitterUser(
                    id=str(user_data.id),
                    username=user_data.username,
                    display_name=user_data.name,
                    bio=user_data.description,
                    location=user_data.location,
                    url=user_data.url,
                    join_date=user_data.created_at,
                    followers=user_data.public_metrics.get("followers_count", 0),
                    following=user_data.public_metrics.get("following_count", 0),
                    tweets=user_data.public_metrics.get("tweet_count", 0),
                    likes=user_data.public_metrics.get("like_count", 0),
                    verified=user_data.verified,
                    profile_image=user_data.profile_image_url,
                    banner_image=user_data.profile_banner_url,
                )
            except Exception as e:
                print(f"Twitter API error: {e}")
        
        # Fallback: Web scraping
        try:
            return self._scrape_user_profile_web(username)
        except Exception as e:
            print(f"Web scraping error: {e}")
        
        return None

    def _scrape_user_profile_web(self, username: str) -> Optional[TwitterUser]:
        """
        Fallback: Scrape Twitter user profile from web.
        
        Args:
            username: Twitter username.
            
        Returns:
            TwitterUser object or None if failed.
        """
        try:
            url = f"{self.TWITTER_WEB_URL}/{username}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract profile data (Twitter's HTML structure changes frequently)
            display_name_element = soup.find("span", {"class": re.compile(r"ProfileHeaderCard-name")})
            display_name = display_name_element.get_text() if display_name_element else ""
            
            bio_element = soup.find("p", {"class": re.compile(r"ProfileHeaderCard-bio")})
            bio = bio_element.get_text() if bio_element else None
            
            location_element = soup.find("span", {"class": re.compile(r"ProfileHeaderCard-location")})
            location = location_element.get_text() if location_element else None
            
            url_element = soup.find("a", {"class": re.compile(r"ProfileHeaderCard-url")})
            url = url_element.get("href", "") if url_element else None
            
            join_date_element = soup.find("span", {"class": re.compile(r"ProfileHeaderCard-joinDate")})
            join_date_str = join_date_element.get_text() if join_date_element else None
            join_date = datetime.strptime(join_date_str, "%B %Y") if join_date_str else None
            
            followers_element = soup.find("a", {"href": f"/{username}/followers"})
            followers_text = followers_element.get_text() if followers_element else "0"
            followers = self._extract_number(followers_text)
            
            following_element = soup.find("a", {"href": f"/{username}/following"})
            following_text = following_element.get_text() if following_element else "0"
            following = self._extract_number(following_text)
            
            verified_element = soup.find("svg", {"aria-label": "Verified account"})
            verified = verified_element is not None
            
            profile_image_element = soup.find("img", {"class": re.compile(r"ProfileAvatar")})
            profile_image = profile_image_element.get("src", "") if profile_image_element else None
            
            return TwitterUser(
                id=username,
                username=username,
                display_name=display_name,
                bio=bio,
                location=location,
                url=url,
                join_date=join_date,
                followers=followers,
                following=following,
                verified=verified,
                profile_image=profile_image,
            )
        except Exception as e:
            print(f"Web scraping failed: {e}")
            return None

    def _extract_number(self, text: str) -> int:
        """
        Extract a number from a string (e.g., "1.2K" -> 1200).
        
        Args:
            text: Input string.
            
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

    def scrape_trends(self, location: int = 23424977, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Scrape Twitter trends for a location.
        
        Args:
            location: WOIED (Where On Earth ID) for the location (default: worldwide).
            limit: Maximum number of trends to return.
            
        Returns:
            List of trend dictionaries.
        """
        trends = []
        
        if self.client:
            # Use Twitter API v2
            try:
                response = self.client.get_place_trends(id=location)
                if response.data:
                    for trend_data in response.data[0].trend_results:
                        trends.append({
                            "name": trend_data.name,
                            "tweet_volume": trend_data.tweet_volume,
                        })
            except Exception as e:
                print(f"Twitter API error: {e}")
        
        # Fallback: Web scraping (not implemented for trends)
        
        return trends[:limit]


# Singleton instance for easy use
twitter_scraper = TwitterScraper()
