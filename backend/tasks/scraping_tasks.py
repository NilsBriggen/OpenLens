"""
Celery Tasks for Scraping

Asynchronous tasks for scraping social media platforms (VK, Telegram).
"""

from celery import shared_task
from scrapers.vk_scraper import VKScraper, VKUser, VKPost
from scrapers.telegram_scraper import TelegramScraper, TelegramPost, TelegramUser
import time


# Initialize scrapers (reused across tasks)
vk_scraper = VKScraper(rate_limit_delay=0.5)  # Faster for async tasks


@shared_task(bind=True, max_retries=3)
def scrape_vk_user_task(self, username: str):
    """
    Celery task to scrape a VK user profile.
    
    Args:
        username: VK username or user ID.
        
    Returns:
        Dictionary with user data or error message.
    """
    try:
        user = vk_scraper.scrape_user_profile(username)
        if user:
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "bio": user.bio,
                    "city": user.city,
                    "country": user.country,
                    "birthday": user.birthday,
                    "followers": user.friends,
                }
            }
        else:
            return {"success": False, "error": "User not found or scraping failed"}
    except Exception as e:
        self.retry(exc=e, countdown=60)
        return {"success": False, "error": str(e)}


@shared_task(bind=True, max_retries=3)
def scrape_vk_posts_task(self, username: str, limit: int = 10):
    """
    Celery task to scrape VK user posts.
    
    Args:
        username: VK username or user ID.
        limit: Maximum number of posts to scrape.
        
    Returns:
        Dictionary with list of posts or error message.
    """
    try:
        posts = vk_scraper.scrape_user_posts(username, limit=limit)
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "author_name": post.author_name,
                "content": post.content,
                "timestamp": post.timestamp,
                "likes": post.likes,
                "reposts": post.reposts,
                "views": post.views,
                "comments": post.comments,
                "attachments": post.attachments,
            })
        return {"success": True, "username": username, "posts": posts_data}
    except Exception as e:
        self.retry(exc=e, countdown=60)
        return {"success": False, "error": str(e)}


@shared_task(bind=True, max_retries=3)
def search_vk_users_task(self, query: str, limit: int = 10):
    """
    Celery task to search VK users.
    
    Args:
        query: Search query.
        limit: Maximum number of results.
        
    Returns:
        Dictionary with list of users or error message.
    """
    try:
        users = vk_scraper.search_users(query, limit=limit)
        return {"success": True, "query": query, "users": users}
    except Exception as e:
        self.retry(exc=e, countdown=60)
        return {"success": False, "error": str(e)}


@shared_task(bind=True, max_retries=3)
def scrape_telegram_channel_task(self, api_id: int, api_hash: str, channel_username: str, limit: int = 10):
    """
    Celery task to scrape a Telegram channel.
    
    Note: Requires Telegram API credentials (passed as args for security).
    
    Args:
        api_id: Telegram API ID.
        api_hash: Telegram API hash.
        channel_username: Telegram channel username.
        limit: Maximum number of posts to scrape.
        
    Returns:
        Dictionary with list of posts or error message.
    """
    try:
        scraper = TelegramScraper(api_id=api_id, api_hash=api_hash)
        if not scraper.start():
            return {"success": False, "error": "Failed to start Telegram client"}
        
        # Run async scraping
        import asyncio
        loop = asyncio.get_event_loop()
        posts = loop.run_until_complete(
            scraper.scrape_channel_posts(channel_username, limit=limit)
        )
        scraper.stop()
        
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "channel_name": post.channel_name,
                "author_name": post.author_name,
                "content": post.content,
                "timestamp": post.timestamp,
                "views": post.views,
                "forwards": post.forwards,
                "replies": post.replies,
                "hashtags": post.hashtags,
                "mentions": post.mentions,
                "urls": post.urls,
            })
        return {"success": True, "channel": channel_username, "posts": posts_data}
    except Exception as e:
        self.retry(exc=e, countdown=60)
        return {"success": False, "error": str(e)}
