"""
Telegram Scraper for OpenLens

Scrapes public Telegram channels, groups, and user profiles for OSINT data.
Uses the Telethon library (Python client for Telegram's API).

Dependencies:
- telethon: For Telegram API access
- asyncio: For async operations
"""

import asyncio
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from telethon.sync import TelegramClient
from telethon.tl.types import (
    PeerChannel,
    PeerChat,
    PeerUser,
    Message,
    User,
    Channel,
    Chat,
    MessageMediaPhoto,
    MessageMediaDocument,
    MessageEntityUrl,
    MessageEntityMention,
    MessageEntityHashtag,
)


@dataclass
class TelegramPost:
    """Represents a Telegram post/message with metadata."""
    id: int
    channel_id: Optional[int] = None
    channel_name: Optional[str] = None
    author_id: Optional[int] = None
    author_name: Optional[str] = None
    content: str = ""
    timestamp: Optional[str] = None
    views: int = 0
    forwards: int = 0
    replies: int = 0
    attachments: List[Dict[str, Any]] = None
    hashtags: List[str] = None
    mentions: List[str] = None
    urls: List[str] = None
    geotag: Optional[Dict[str, float]] = None

    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []
        if self.hashtags is None:
            self.hashtags = []
        if self.mentions is None:
            self.mentions = []
        if self.urls is None:
            self.urls = []


@dataclass
class TelegramUser:
    """Represents a Telegram user profile."""
    id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    is_verified: bool = False
    is_bot: bool = False
    last_seen: Optional[str] = None
    profile_photo: Optional[str] = None


@dataclass
class TelegramChannel:
    """Represents a Telegram channel or group."""
    id: int
    title: str
    username: Optional[str] = None
    description: Optional[str] = None
    members: int = 0
    is_verified: bool = False
    is_private: bool = False


class TelegramScraper:
    """
    Scrapes public data from Telegram using the Telethon library.
    
    Note: Requires a Telegram API ID and hash (from https://my.telegram.org).
    """

    def __init__(
        self,
        api_id: int,
        api_hash: str,
        phone: Optional[str] = None,
        session_name: str = "openlens_session",
    ):
        """
        Initialize the Telegram scraper.
        
        Args:
            api_id: Telegram API ID (from https://my.telegram.org).
            api_hash: Telegram API hash (from https://my.telegram.org).
            phone: Optional phone number for authenticated access.
            session_name: Name for the Telethon session file.
        """
        self.api_id = api_id
        self.api_hash = api_hash
        self.phone = phone
        self.session_name = session_name
        self.client = None

    def start(self) -> bool:
        """
        Start the Telegram client.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            if self.phone:
                self.client = TelegramClient(
                    self.session_name,
                    self.api_id,
                    self.api_hash,
                )
                self.client.connect()
                if not self.client.is_user_authorized():
                    self.client.send_code_request(self.phone)
                    self.client.sign_in(self.phone, input("Enter the code: "))
            else:
                # Anonymous client (limited access)
                self.client = TelegramClient(
                    self.session_name,
                    self.api_id,
                    self.api_hash,
                )
                self.client.connect()
            return True
        except Exception as e:
            print(f"Failed to start Telegram client: {e}")
            return False

    def stop(self):
        """Stop the Telegram client."""
        if self.client:
            self.client.disconnect()

    async def _extract_message_metadata(self, message: Message) -> TelegramPost:
        """
        Extract metadata from a Telegram message.
        
        Args:
            message: Telethon Message object.
            
        Returns:
            TelegramPost object.
        """
        post = TelegramPost(
            id=message.id,
            timestamp=message.date.strftime("%Y-%m-%d %H:%M:%S") if message.date else None,
        )

        # Extract channel info
        if message.peer_id:
            if isinstance(message.peer_id, PeerChannel):
                channel = await self.client.get_entity(PeerChannel(message.peer_id.channel_id))
                post.channel_id = channel.id
                post.channel_name = channel.title
            elif isinstance(message.peer_id, PeerChat):
                chat = await self.client.get_entity(PeerChat(message.peer_id.chat_id))
                post.channel_name = chat.title

        # Extract author info
        if message.from_id:
            if isinstance(message.from_id, PeerUser):
                user = await self.client.get_entity(PeerUser(message.from_id.user_id))
                post.author_id = user.id
                post.author_name = f"{user.first_name} {user.last_name or ''}".strip()

        # Extract content
        if message.message:
            post.content = message.message

        # Extract hashtags, mentions, and URLs from entities
        if message.entities:
            for entity in message.entities:
                if isinstance(entity, MessageEntityHashtag):
                    hashtag = message.message[entity.offset:entity.offset + entity.length]
                    post.hashtags.append(hashtag)
                elif isinstance(entity, MessageEntityMention):
                    mention = message.message[entity.offset:entity.offset + entity.length]
                    post.mentions.append(mention)
                elif isinstance(entity, MessageEntityUrl):
                    url = message.message[entity.offset:entity.offset + entity.length]
                    post.urls.append(url)

        # Extract attachments (photos, documents, etc.)
        if message.media:
            if isinstance(message.media, MessageMediaPhoto):
                photo = message.media.photo
                post.attachments.append({
                    "type": "photo",
                    "id": photo.id,
                    "url": f"https://t.me/c/{post.channel_id}/{message.id}" if post.channel_id else None,
                })
            elif isinstance(message.media, MessageMediaDocument):
                doc = message.media.document
                post.attachments.append({
                    "type": "document",
                    "id": doc.id,
                    "filename": doc.file_name,
                    "mime_type": doc.mime_type,
                })

        # Extract engagement metrics
        if message.views:
            post.views = message.views
        if message.forwards:
            post.forwards = message.forwards
        if message.replies:
            post.replies = message.replies.replies

        return post

    async def scrape_channel_posts(
        self,
        channel_username: str,
        limit: int = 10,
    ) -> List[TelegramPost]:
        """
        Scrape recent posts from a public Telegram channel.
        
        Args:
            channel_username: Telegram channel username (e.g., "durov").
            limit: Maximum number of posts to scrape.
            
        Returns:
            List of TelegramPost objects.
        """
        posts = []
        try:
            channel = await self.client.get_entity(channel_username)
            async for message in self.client.iter_messages(channel, limit=limit):
                post = await self._extract_message_metadata(message)
                posts.append(post)
        except Exception as e:
            print(f"Failed to scrape channel {channel_username}: {e}")
        return posts

    async def scrape_user_profile(self, username: str) -> Optional[TelegramUser]:
        """
        Scrape a public Telegram user profile.
        
        Args:
            username: Telegram username (e.g., "durov").
            
        Returns:
            TelegramUser object or None if failed.
        """
        try:
            user = await self.client.get_entity(username)
            if isinstance(user, User):
                return TelegramUser(
                    id=user.id,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    username=user.username,
                    bio=user.about,
                    phone=user.phone,
                    is_verified=user.verified,
                    is_bot=user.bot,
                    last_seen=str(user.status) if user.status else None,
                )
        except Exception as e:
            print(f"Failed to scrape user {username}: {e}")
        return None

    async def search_channels(self, query: str, limit: int = 10) -> List[TelegramChannel]:
        """
        Search for Telegram channels by name or keyword.
        
        Args:
            query: Search query (e.g., "news").
            limit: Maximum number of results.
            
        Returns:
            List of TelegramChannel objects.
        """
        channels = []
        try:
            result = await self.client(
                "contacts.SearchRequest",
                q=query,
                limit=limit,
                hash=0,
            )
            for chat in result.chats:
                if isinstance(chat, Channel):
                    channels.append(TelegramChannel(
                        id=chat.id,
                        title=chat.title,
                        username=chat.username,
                        description=chat.about,
                        members=chat.participants_count if chat.participants_count else 0,
                        is_verified=chat.verified,
                        is_private=chat.broadcast is False,
                    ))
        except Exception as e:
            print(f"Failed to search channels: {e}")
        return channels

    async def get_channel_info(self, channel_username: str) -> Optional[TelegramChannel]:
        """
        Get information about a Telegram channel.
        
        Args:
            channel_username: Telegram channel username (e.g., "durov").
            
        Returns:
            TelegramChannel object or None if failed.
        """
        try:
            channel = await self.client.get_entity(channel_username)
            if isinstance(channel, Channel):
                return TelegramChannel(
                    id=channel.id,
                    title=channel.title,
                    username=channel.username,
                    description=channel.about,
                    members=channel.participants_count if channel.participants_count else 0,
                    is_verified=channel.verified,
                    is_private=channel.broadcast is False,
                )
        except Exception as e:
            print(f"Failed to get channel info: {e}")
        return None


# Example usage (requires API credentials)
# scraper = TelegramScraper(api_id=12345, api_hash="your_api_hash")
# scraper.start()
# posts = asyncio.run(scraper.scrape_channel_posts("durov", limit=5))
# scraper.stop()
