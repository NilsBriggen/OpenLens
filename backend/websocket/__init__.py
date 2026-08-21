"""
WebSocket Module for OpenLens

Provides real-time communication using WebSocket for:
- Live scraping updates
- Real-time notifications
- Collaborative features

Usage:
    from websocket.socket_server import SocketServer, socketio
    from websocket.event_handlers import register_event_handlers
"""

from .socket_server import SocketServer, get_socketio
from .event_handlers import register_event_handlers

__all__ = [
    'SocketServer',
    'get_socketio',
    'register_event_handlers',
]
