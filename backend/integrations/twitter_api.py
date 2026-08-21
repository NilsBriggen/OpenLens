"""
Twitter API Integration for OpenLens

Provides:
- Tweet retrieval
- User profile retrieval
- Search functionality
- Timeline retrieval
- Streaming (limited)

Dependencies:
- tweepy: Twitter API client
- requests: For HTTP requests
"""

import os
import json
from typing import Dict, List, Any, Optional, Generator
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import time

# Try to import tweepy
try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    print("Tweepy not available. Install with: pip install tweepy")


@dataclass
class Tweet:
    """Represents a tweet."""
    id: str
    text: str
    created_at: datetime
    user: Dict[str, Any]
    retweet_count: int = 0
    favorite_count: int = 0
    reply_count: int = 0
    quote_count: int = 0
    impressions: int = 0
    lang: str = ""
    source: str = ""
    entities: Dict[str, Any] = field(default_factory=dict)
    extended_tweet: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'text': self.text,
            'created_at': self.created_at.isoformat(),
            'user': self.user,
            'retweet_count': self.retweet_count,
            'favorite_count': self.favorite_count,
            'reply_count': self.reply_count,
            'quote_count': self.quote_count,
            'impressions': self.impressions,
            'lang': self.lang,
            'source': self.source,
            'entities': self.entities,
        }


@dataclass
class TwitterUser:
    """Represents a Twitter user."""
    id: str
    screen_name: str
    name: str
    description: str = ""
    followers_count: int = 0
    friends_count: int = 0
    statuses_count: int = 0
    favourites_count: int = 0
    listed_count: int = 0
    created_at: datetime = None
    location: str = ""
    url: str = ""
    profile_image_url: str = ""
    profile_banner_url: str = ""
    verified: bool = False
    protected: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'screen_name': self.screen_name,
            'name': self.name,
            'description': self.description,
            'followers_count': self.followers_count,
            'friends_count': self.friends_count,
            'statuses_count': self.statuses_count,
            'favourites_count': self.favourites_count,
            'listed_count': self.listed_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'location': self.location,
            'url': self.url,
            'profile_image_url': self.profile_image_url,
            'profile_banner_url': self.profile_banner_url,
            'verified': self.verified,
            'protected': self.protected,
        }


@dataclass
class TwitterSearchResult:
    """Represents a Twitter search result."""
    query: str
    tweets: List[Tweet]
    max_id: str = ""
    since_id: str = ""
    next_page: str = ""
    count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'query': self.query,
            'tweets': [t.to_dict() for t in self.tweets],
            'max_id': self.max_id,
            'since_id': self.since_id,
            'next_page': self.next_page,
            'count': self.count,
        }


class TwitterAPIService:
    """
    Provides integration with Twitter API.
    """
    
    def __init__(self, consumer_key: str = None, consumer_secret: str = None,
                 access_token: str = None, access_token_secret: str = None,
                 bearer_token: str = None):
        """
        Initialize the Twitter API service.
        
        Args:
            consumer_key: Twitter API consumer key.
            consumer_secret: Twitter API consumer secret.
            access_token: Twitter API access token.
            access_token_secret: Twitter API access token secret.
            bearer_token: Twitter API v2 bearer token.
        """
        self.consumer_key = consumer_key or os.getenv('TWITTER_CONSUMER_KEY')
        self.consumer_secret = consumer_secret or os.getenv('TWITTER_CONSUMER_SECRET')
        self.access_token = access_token or os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = access_token_secret or os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        self.bearer_token = bearer_token or os.getenv('TWITTER_BEARER_TOKEN')
        
        self.client_v1 = None
        self.client_v2 = None
        self._rate_limit_delay = 1.0  # 1 second between requests
        self._last_request_time = 0
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Twitter API clients."""
        if not TWEEPY_AVAILABLE:
            return
        
        # Initialize v1.1 client
        if self.consumer_key and self.consumer_secret and self.access_token and self.access_token_secret:
            try:
                auth = tweepy.OAuth1UserHandler(
                    self.consumer_key,
                    self.consumer_secret,
                    self.access_token,
                    self.access_token_secret,
                )
                self.client_v1 = tweepy.API(auth, wait_on_rate_limit=True)
            except Exception as e:
                print(f"Failed to initialize Twitter v1.1 client: {e}")
        
        # Initialize v2 client
        if self.bearer_token:
            try:
                self.client_v2 = tweepy.Client(bearer_token=self.bearer_token, wait_on_rate_limit=True)
            except Exception as e:
                print(f"Failed to initialize Twitter v2 client: {e}")
    
    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = time.time()
    
    def get_user(self, screen_name: str = None, user_id: str = None) -> Optional[TwitterUser]:
        """
        Get a Twitter user profile.
        
        Args:
            screen_name: Twitter screen name (username).
            user_id: Twitter user ID.
            
        Returns:
            TwitterUser object or None if failed.
        """
        if not self.client_v1 and not self.client_v2:
            return None
        
        self._check_rate_limit()
        
        try:
            # Try v1.1 API first
            if self.client_v1:
                if screen_name:
                    user = self.client_v1.get_user(screen_name=screen_name)
                elif user_id:
                    user = self.client_v1.get_user(user_id=user_id)
                else:
                    return None
                
                return TwitterUser(
                    id=str(user.id),
                    screen_name=user.screen_name,
                    name=user.name,
                    description=user.description or "",
                    followers_count=user.followers_count,
                    friends_count=user.friends_count,
                    statuses_count=user.statuses_count,
                    favourites_count=user.favourites_count,
                    listed_count=user.listed_count,
                    created_at=user.created_at,
                    location=user.location or "",
                    url=user.url or "",
                    profile_image_url=user.profile_image_url_https or "",
                    profile_banner_url=user.profile_banner_url or "",
                    verified=user.verified,
                    protected=user.protected,
                )
            
            # Try v2 API
            if self.client_v2:
                if screen_name:
                    user = self.client_v2.get_user(username=screen_name, user_fields=[
                        'created_at', 'description', 'location', 'url',
                        'profile_image_url', 'public_metrics', 'verified',
                    ])
                elif user_id:
                    user = self.client_v2.get_user(id=user_id, user_fields=[
                        'created_at', 'description', 'location', 'url',
                        'profile_image_url', 'public_metrics', 'verified',
                    ])
                else:
                    return None
                
                data = user.data
                public_metrics = data.public_metrics if hasattr(data, 'public_metrics') else {}
                
                return TwitterUser(
                    id=data.id,
                    screen_name=data.username,
                    name=data.name,
                    description=data.description or "",
                    followers_count=public_metrics.get('followers_count', 0),
                    friends_count=public_metrics.get('following_count', 0),
                    statuses_count=public_metrics.get('tweet_count', 0),
                    favourites_count=0,  # Not available in v2
                    listed_count=0,  # Not available in v2
                    created_at=data.created_at,
                    location=data.location or "",
                    url=data.url or "",
                    profile_image_url=data.profile_image_url or "",
                    profile_banner_url="",  # Not available in v2
                    verified=data.verified or False,
                    protected=False,  # Not available in v2
                )
        
        except Exception as e:
            print(f"Error getting Twitter user: {e}")
            return None
    
    def get_user_timeline(self, screen_name: str = None, user_id: str = None,
                         count: int = 20, since_id: str = None, 
                         max_id: str = None, include_rts: bool = True) -> List[Tweet]:
        """
        Get a user's timeline (tweets).
        
        Args:
            screen_name: Twitter screen name.
            user_id: Twitter user ID.
            count: Number of tweets to retrieve.
            since_id: Return tweets newer than this ID.
            max_id: Return tweets older than this ID.
            include_rts: Whether to include retweets.
            
        Returns:
            List of Tweet objects.
        """
        if not self.client_v1:
            return []
        
        self._check_rate_limit()
        
        try:
            kwargs = {
                'count': count,
                'include_rts': include_rts,
            }
            
            if screen_name:
                kwargs['screen_name'] = screen_name
            elif user_id:
                kwargs['user_id'] = user_id
            else:
                return []
            
            if since_id:
                kwargs['since_id'] = since_id
            if max_id:
                kwargs['max_id'] = max_id
            
            tweets = self.client_v1.user_timeline(**kwargs)
            
            return [
                Tweet(
                    id=str(tweet.id),
                    text=tweet.text,
                    created_at=tweet.created_at,
                    user={
                        'id': str(tweet.user.id),
                        'screen_name': tweet.user.screen_name,
                        'name': tweet.user.name,
                        'profile_image_url': tweet.user.profile_image_url_https,
                    },
                    retweet_count=tweet.retweet_count,
                    favorite_count=tweet.favorite_count,
                    reply_count=getattr(tweet, 'reply_count', 0),
                    quote_count=getattr(tweet, 'quote_count', 0),
                    impressions=getattr(tweet, 'impressions', 0),
                    lang=tweet.lang or "",
                    source=tweet.source or "",
                    entities=tweet.entities,
                )
                for tweet in tweets
            ]
        
        except Exception as e:
            print(f"Error getting user timeline: {e}")
            return []
    
    def get_home_timeline(self, count: int = 20, since_id: str = None, 
                         max_id: str = None) -> List[Tweet]:
        """
        Get the home timeline (tweets from users the authenticated user follows).
        
        Args:
            count: Number of tweets to retrieve.
            since_id: Return tweets newer than this ID.
            max_id: Return tweets older than this ID.
            
        Returns:
            List of Tweet objects.
        """
        if not self.client_v1:
            return []
        
        self._check_rate_limit()
        
        try:
            kwargs = {'count': count}
            
            if since_id:
                kwargs['since_id'] = since_id
            if max_id:
                kwargs['max_id'] = max_id
            
            tweets = self.client_v1.home_timeline(**kwargs)
            
            return [
                Tweet(
                    id=str(tweet.id),
                    text=tweet.text,
                    created_at=tweet.created_at,
                    user={
                        'id': str(tweet.user.id),
                        'screen_name': tweet.user.screen_name,
                        'name': tweet.user.name,
                        'profile_image_url': tweet.user.profile_image_url_https,
                    },
                    retweet_count=tweet.retweet_count,
                    favorite_count=tweet.favorite_count,
                    reply_count=getattr(tweet, 'reply_count', 0),
                    quote_count=getattr(tweet, 'quote_count', 0),
                    lang=tweet.lang or "",
                    source=tweet.source or "",
                    entities=tweet.entities,
                )
                for tweet in tweets
            ]
        
        except Exception as e:
            print(f"Error getting home timeline: {e}")
            return []
    
    def search_tweets(self, query: str, count: int = 20, lang: str = None,
                      since: datetime = None, until: datetime = None,
                      geocode: Tuple[float, float, str] = None) -> TwitterSearchResult:
        """
        Search for tweets.
        
        Args:
            query: Search query.
            count: Number of tweets to retrieve.
            lang: Language code.
            since: Start date.
            until: End date.
            geocode: Optional (latitude, longitude, radius) tuple.
            
        Returns:
            TwitterSearchResult object.
        """
        if not self.client_v1:
            return TwitterSearchResult(query=query, tweets=[])
        
        self._check_rate_limit()
        
        try:
            kwargs = {
                'q': query,
                'count': count,
            }
            
            if lang:
                kwargs['lang'] = lang
            if since:
                kwargs['since'] = since.strftime('%Y-%m-%d')
            if until:
                kwargs['until'] = until.strftime('%Y-%m-%d')
            if geocode:
                kwargs['geocode'] = f"{geocode[0]},{geocode[1]},{geocode[2]}"
            
            result = self.client_v1.search_tweets(**kwargs)
            
            tweets = [
                Tweet(
                    id=str(tweet.id),
                    text=tweet.text,
                    created_at=tweet.created_at,
                    user={
                        'id': str(tweet.user.id),
                        'screen_name': tweet.user.screen_name,
                        'name': tweet.user.name,
                        'profile_image_url': tweet.user.profile_image_url_https,
                    },
                    retweet_count=tweet.retweet_count,
                    favorite_count=tweet.favorite_count,
                    reply_count=getattr(tweet, 'reply_count', 0),
                    quote_count=getattr(tweet, 'quote_count', 0),
                    lang=tweet.lang or "",
                    source=tweet.source or "",
                    entities=tweet.entities,
                )
                for tweet in result
            ]
            
            # Get pagination info
            max_id = str(result[-1].id - 1) if result else ""
            
            return TwitterSearchResult(
                query=query,
                tweets=tweets,
                max_id=max_id,
                count=len(tweets),
            )
        
        except Exception as e:
            print(f"Error searching tweets: {e}")
            return TwitterSearchResult(query=query, tweets=[])
    
    def get_tweet(self, tweet_id: str) -> Optional[Tweet]:
        """
        Get a specific tweet by ID.
        
        Args:
            tweet_id: Tweet ID.
            
        Returns:
            Tweet object or None if failed.
        """
        if not self.client_v1:
            return None
        
        self._check_rate_limit()
        
        try:
            tweet = self.client_v1.get_status(tweet_id, tweet_mode='extended')
            
            return Tweet(
                id=str(tweet.id),
                text=tweet.full_text if hasattr(tweet, 'full_text') else tweet.text,
                created_at=tweet.created_at,
                user={
                    'id': str(tweet.user.id),
                    'screen_name': tweet.user.screen_name,
                    'name': tweet.user.name,
                    'profile_image_url': tweet.user.profile_image_url_https,
                },
                retweet_count=tweet.retweet_count,
                favorite_count=tweet.favorite_count,
                reply_count=getattr(tweet, 'reply_count', 0),
                quote_count=getattr(tweet, 'quote_count', 0),
                impressions=getattr(tweet, 'impressions', 0),
                lang=tweet.lang or "",
                source=tweet.source or "",
                entities=tweet.entities,
            )
        
        except Exception as e:
            print(f"Error getting tweet: {e}")
            return None
    
    def get_followers(self, screen_name: str = None, user_id: str = None,
                      count: int = 20, cursor: str = None) -> Tuple[List[TwitterUser], str]:
        """
        Get a user's followers.
        
        Args:
            screen_name: Twitter screen name.
            user_id: Twitter user ID.
            count: Number of followers to retrieve.
            cursor: Pagination cursor.
            
        Returns:
            Tuple of (list of TwitterUser objects, next cursor).
        """
        if not self.client_v1:
            return [], ""
        
        self._check_rate_limit()
        
        try:
            kwargs = {'count': count}
            
            if screen_name:
                kwargs['screen_name'] = screen_name
            elif user_id:
                kwargs['user_id'] = user_id
            else:
                return [], ""
            
            if cursor:
                kwargs['cursor'] = cursor
            
            result = self.client_v1.followers(**kwargs)
            
            users = [
                TwitterUser(
                    id=str(user.id),
                    screen_name=user.screen_name,
                    name=user.name,
                    description=user.description or "",
                    followers_count=user.followers_count,
                    friends_count=user.friends_count,
                    statuses_count=user.statuses_count,
                    profile_image_url=user.profile_image_url_https or "",
                    verified=user.verified,
                )
                for user in result
            ]
            
            next_cursor = result.next_cursor if hasattr(result, 'next_cursor') else ""
            
            return users, next_cursor
        
        except Exception as e:
            print(f"Error getting followers: {e}")
            return [], ""
    
    def get_friends(self, screen_name: str = None, user_id: str = None,
                    count: int = 20, cursor: str = None) -> Tuple[List[TwitterUser], str]:
        """
        Get a user's friends (who they follow).
        
        Args:
            screen_name: Twitter screen name.
            user_id: Twitter user ID.
            count: Number of friends to retrieve.
            cursor: Pagination cursor.
            
        Returns:
            Tuple of (list of TwitterUser objects, next cursor).
        """
        if not self.client_v1:
            return [], ""
        
        self._check_rate_limit()
        
        try:
            kwargs = {'count': count}
            
            if screen_name:
                kwargs['screen_name'] = screen_name
            elif user_id:
                kwargs['user_id'] = user_id
            else:
                return [], ""
            
            if cursor:
                kwargs['cursor'] = cursor
            
            result = self.client_v1.friends(**kwargs)
            
            users = [
                TwitterUser(
                    id=str(user.id),
                    screen_name=user.screen_name,
                    name=user.name,
                    description=user.description or "",
                    followers_count=user.followers_count,
                    friends_count=user.friends_count,
                    statuses_count=user.statuses_count,
                    profile_image_url=user.profile_image_url_https or "",
                    verified=user.verified,
                )
                for user in result
            ]
            
            next_cursor = result.next_cursor if hasattr(result, 'next_cursor') else ""
            
            return users, next_cursor
        
        except Exception as e:
            print(f"Error getting friends: {e}")
            return [], ""
    
    def get_trends(self, woeid: int = 1) -> List[Dict[str, Any]]:
        """
        Get trending topics for a location.
        
        Args:
            woeid: Where On Earth ID (default is worldwide).
            
        Returns:
            List of trend dictionaries.
        """
        if not self.client_v1:
            return []
        
        self._check_rate_limit()
        
        try:
            trends = self.client_v1.get_place_trends(id=woeid)
            
            return [
                {
                    'name': trend['name'],
                    'url': trend['url'],
                    'promoted_content': trend.get('promoted_content', None),
                    'query': trend.get('query', ''),
                    'tweet_volume': trend.get('tweet_volume', 0),
                }
                for trend in trends[0]['trends']
            ]
        
        except Exception as e:
            print(f"Error getting trends: {e}")
            return []
    
    def stream_tweets(self, query: str, callback: Callable, 
                      lang: str = None, locations: List[float] = None) -> bool:
        """
        Stream tweets in real-time.
        
        Args:
            query: Search query.
            callback: Function to call for each tweet.
            lang: Language code.
            locations: List of [longitude, latitude] pairs for geo filtering.
            
        Returns:
            True if streaming started, False otherwise.
        """
        if not self.client_v1:
            return False
        
        try:
            class StreamListener(tweepy.StreamListener):
                def on_status(self, status):
                    callback(status)
                
                def on_error(self, status_code):
                    if status_code == 420:
                        # Rate limit exceeded
                        return False
                    return True
            
            listener = StreamListener()
            stream = tweepy.Stream(
                self.consumer_key,
                self.consumer_secret,
                self.access_token,
                self.access_token_secret,
                listener,
            )
            
            if locations:
                stream.filter(locations=locations)
            else:
                stream.filter(track=[query], languages=[lang] if lang else None)
            
            return True
        
        except Exception as e:
            print(f"Error starting stream: {e}")
            return False


# Global Twitter API service instance
twitter_api_service = TwitterAPIService()
