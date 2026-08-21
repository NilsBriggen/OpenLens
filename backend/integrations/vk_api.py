"""
VK API Service for OpenLens

Provides VK (VKontakte) API access:
- User profiles (single and batch)
- Group information
- Friend lists
- Wall posts
- User search

Requires VK_API_TOKEN. Without a token every method returns None/[] after one
printed warning - the service never synthesises profiles.
"""

import os
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

import requests

VK_API_BASE = 'https://api.vk.com/method'


@dataclass
class VKUser:
    """Represents a VK user profile."""
    user_id: str
    first_name: str = ''
    last_name: str = ''
    screen_name: str = ''
    is_closed: bool = False
    city: str = ''
    country: str = ''
    photo_url: str = ''
    last_seen: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'screen_name': self.screen_name,
            'is_closed': self.is_closed,
            'city': self.city,
            'country': self.country,
            'photo_url': self.photo_url,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None,
        }


@dataclass
class VKGroup:
    """Represents a VK group."""
    group_id: str
    name: str = ''
    screen_name: str = ''
    members_count: int = 0
    description: str = ''
    is_closed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'group_id': self.group_id,
            'name': self.name,
            'screen_name': self.screen_name,
            'members_count': self.members_count,
            'description': self.description,
            'is_closed': self.is_closed,
        }


@dataclass
class VKPost:
    """Represents a VK wall post."""
    post_id: str
    owner_id: str = ''
    text: str = ''
    date: Optional[datetime] = None
    likes: int = 0
    reposts: int = 0
    comments: int = 0
    attachments: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'post_id': self.post_id,
            'owner_id': self.owner_id,
            'text': self.text,
            'date': self.date.isoformat() if self.date else None,
            'likes': self.likes,
            'reposts': self.reposts,
            'comments': self.comments,
            'attachments': self.attachments,
        }


class VKAPIService:
    """
    VK API client for OpenLens.

    Uses the plain HTTPS method API (no extra library required). Rate-limited
    to 3 requests/second per VK's API policy.
    """

    _USER_FIELDS = 'screen_name,city,country,photo_200,last_seen'

    def __init__(self, access_token: str = None, api_version: str = None):
        """
        Initialize the VK API service.

        Args:
            access_token: VK access token (VK_API_TOKEN env fallback).
            api_version: VK API version (VK_API_VERSION env, default 5.199).
        """
        token = access_token or os.getenv('VK_API_TOKEN', '')
        # The repo's .env ships a placeholder; treat it as unconfigured.
        if token in ('', 'your_vk_api_token'):
            token = ''
        self.access_token = token
        self.api_version = api_version or os.getenv('VK_API_VERSION', '5.199')
        self._rate_limit_delay = 1.0 / 3.0  # 3 req/s
        self._last_request_time = 0.0

        if not self.access_token:
            print("VK API token not configured. Set VK_API_TOKEN to enable VK lookups.")

    def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self._rate_limit_delay:
            time.sleep(self._rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    def is_available(self) -> bool:
        """True when a token is configured."""
        return bool(self.access_token)

    def _call(self, method: str, **params) -> Optional[Dict[str, Any]]:
        """One authenticated VK API call; None when unconfigured or failed."""
        if not self.access_token:
            return None

        self._check_rate_limit()
        try:
            response = requests.get(
                f'{VK_API_BASE}/{method}',
                params={**params, 'access_token': self.access_token,
                        'v': self.api_version},
                timeout=10,
            )
            response.raise_for_status()
            payload = response.json()
            if 'error' in payload:
                print(f"VK API error ({method}): "
                      f"{payload['error'].get('error_msg', payload['error'])}")
                return None
            return payload.get('response')
        except Exception as e:
            print(f"VK API request error ({method}): {e}")
            return None

    @classmethod
    def _parse_user(cls, data: Dict[str, Any]) -> VKUser:
        """Build a VKUser from an API user object."""
        last_seen = None
        seen = data.get('last_seen', {})
        if isinstance(seen, dict) and seen.get('time'):
            last_seen = datetime.utcfromtimestamp(seen['time'])
        return VKUser(
            user_id=str(data.get('id', '')),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            screen_name=data.get('screen_name', ''),
            is_closed=bool(data.get('is_closed', False)),
            city=(data.get('city') or {}).get('title', ''),
            country=(data.get('country') or {}).get('title', ''),
            photo_url=data.get('photo_200', ''),
            last_seen=last_seen,
        )

    def get_user(self, user_id: str = None, screen_name: str = None) -> Optional[VKUser]:
        """One user profile by numeric id or screen name."""
        identifier = user_id or screen_name
        if not identifier:
            return None
        users = self.get_users([str(identifier)])
        return users[0] if users else None

    def get_users(self, user_ids: List[str]) -> List[VKUser]:
        """Batch user profiles."""
        response = self._call('users.get', user_ids=','.join(map(str, user_ids)),
                              fields=self._USER_FIELDS)
        if not response:
            return []
        return [self._parse_user(u) for u in response]

    def get_group(self, group_id: str) -> Optional[VKGroup]:
        """Group information."""
        response = self._call('groups.getById', group_id=str(group_id),
                              fields='members_count,description')
        groups = (response or {}).get('groups') if isinstance(response, dict) else response
        if not groups:
            return None
        data = groups[0]
        return VKGroup(
            group_id=str(data.get('id', '')),
            name=data.get('name', ''),
            screen_name=data.get('screen_name', ''),
            members_count=int(data.get('members_count', 0) or 0),
            description=data.get('description', ''),
            is_closed=bool(data.get('is_closed', 0)),
        )

    def get_friends(self, user_id: str, count: int = 100) -> List[VKUser]:
        """A user's friends."""
        response = self._call('friends.get', user_id=str(user_id), count=count,
                              fields=self._USER_FIELDS)
        if not response:
            return []
        return [self._parse_user(u) for u in response.get('items', [])]

    def get_wall(self, owner_id: str, count: int = 20) -> List[VKPost]:
        """Wall posts for a user or group (negative id)."""
        response = self._call('wall.get', owner_id=str(owner_id), count=count)
        if not response:
            return []
        posts = []
        for item in response.get('items', []):
            posts.append(VKPost(
                post_id=str(item.get('id', '')),
                owner_id=str(item.get('owner_id', '')),
                text=item.get('text', ''),
                date=datetime.utcfromtimestamp(item['date']) if item.get('date') else None,
                likes=(item.get('likes') or {}).get('count', 0),
                reposts=(item.get('reposts') or {}).get('count', 0),
                comments=(item.get('comments') or {}).get('count', 0),
                attachments=item.get('attachments', []),
            ))
        return posts

    def search_users(self, query: str, count: int = 20) -> List[VKUser]:
        """Search users by free text."""
        response = self._call('users.search', q=query, count=count,
                              fields=self._USER_FIELDS)
        if not response:
            return []
        return [self._parse_user(u) for u in response.get('items', [])]


# Global VK API service instance
vk_api_service = VKAPIService()
