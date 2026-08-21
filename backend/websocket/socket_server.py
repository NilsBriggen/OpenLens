"""
WebSocket Server for OpenLens

Provides real-time communication using Flask-SocketIO.

Features:
- Room-based messaging
- User presence tracking
- Collaborative features
- Scraping progress updates
- Analysis progress updates
- Notification system

Dependencies:
- flask-socketio: WebSocket support for Flask
- python-socketio: Socket.IO server
- eventlet: Async server (optional)
- gevent: Async server (optional)
"""

import os
from typing import Dict, List, Any, Callable, Optional, Set
from flask import Flask, request
from flask_socketio import SocketIO, Namespace, emit, join_room, leave_room, rooms
from flask_socketio import disconnect
import json
from datetime import datetime
from dataclasses import dataclass, field
from typing import TypedDict

# Global SocketIO instance
_socketio = None


@dataclass
class ClientInfo:
    """Information about a connected client."""
    client_id: str
    username: Optional[str] = None
    user_id: Optional[int] = None
    ip_address: str = ""
    user_agent: str = ""
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    rooms: Set[str] = field(default_factory=set)
    is_authenticated: bool = False


@dataclass
class RoomInfo:
    """Information about a room."""
    name: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    creator_id: Optional[str] = None
    clients: Set[str] = field(default_factory=set)
    is_private: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class SocketServer:
    """
    Manages WebSocket connections and rooms with enhanced collaboration features.
    """
    
    def __init__(self, app: Flask = None):
        """
        Initialize SocketServer.
        
        Args:
            app: Optional Flask application.
        """
        self.app = app
        self.clients: Dict[str, ClientInfo] = {}  # client_id -> ClientInfo
        self.rooms: Dict[str, RoomInfo] = {}  # room_name -> RoomInfo
        self.user_to_client: Dict[int, Set[str]] = {}  # user_id -> Set[client_ids]
        self.collaboration_sessions: Dict[str, Dict] = {}  # session_id -> session_data
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """
        Initialize SocketServer with Flask app.
        
        Args:
            app: Flask application.
        """
        global _socketio
        
        self.app = app
        
        # Configure SocketIO
        async_mode = os.getenv('SOCKETIO_ASYNC_MODE', 'eventlet')
        cors_allowed_origins = os.getenv('SOCKETIO_CORS_ORIGINS', '*')
        max_http_buffer_size = int(os.getenv('SOCKETIO_MAX_HTTP_BUFFER_SIZE', '1e8'))
        
        _socketio = SocketIO(
            app,
            async_mode=async_mode,
            cors_allowed_origins=cors_allowed_origins,
            logger=True,
            engineio_logger=True,
            max_http_buffer_size=max_http_buffer_size,
            ping_timeout=20000,
            ping_interval=25000,
        )
        
        print(f"SocketIO initialized with async_mode={async_mode}")
    
    def get_socketio(self):
        """Get the SocketIO instance."""
        return _socketio
    
    def add_client(self, client_id: str, client_info: Dict = None, **kwargs):
        """
        Add a client to the tracking.
        
        Args:
            client_id: Unique client ID (usually request.sid).
            client_info: Optional client information.
            **kwargs: Additional client information.
        """
        info = client_info or {}
        
        client = ClientInfo(
            client_id=client_id,
            username=info.get('username') or kwargs.get('username'),
            user_id=info.get('user_id') or kwargs.get('user_id'),
            ip_address=info.get('ip') or kwargs.get('ip', request.remote_addr if request else ''),
            user_agent=info.get('user_agent') or kwargs.get('user_agent', ''),
            is_authenticated=info.get('is_authenticated', False) or kwargs.get('is_authenticated', False),
        )
        
        self.clients[client_id] = client
        
        # Track user to client mapping
        if client.user_id:
            if client.user_id not in self.user_to_client:
                self.user_to_client[client.user_id] = set()
            self.user_to_client[client.user_id].add(client_id)
        
        return client
    
    def remove_client(self, client_id: str):
        """
        Remove a client from tracking.
        
        Args:
            client_id: Client ID to remove.
        """
        if client_id in self.clients:
            client = self.clients[client_id]
            
            # Remove from user mapping
            if client.user_id and client.user_id in self.user_to_client:
                self.user_to_client[client.user_id].discard(client_id)
                if not self.user_to_client[client.user_id]:
                    del self.user_to_client[client.user_id]
            
            # Remove from all rooms
            for room_name in list(client.rooms):
                self.leave_room(client_id, room_name)
            
            del self.clients[client_id]
    
    def update_client(self, client_id: str, **kwargs):
        """
        Update client information.
        
        Args:
            client_id: Client ID to update.
            **kwargs: Fields to update.
        """
        if client_id in self.clients:
            client = self.clients[client_id]
            for key, value in kwargs.items():
                if hasattr(client, key):
                    setattr(client, key, value)
            
            # Update user mapping if user_id changed
            if 'user_id' in kwargs and kwargs['user_id'] != client.user_id:
                if client.user_id and client.user_id in self.user_to_client:
                    self.user_to_client[client.user_id].discard(client_id)
                    if not self.user_to_client[client.user_id]:
                        del self.user_to_client[client.user_id]
                
                client.user_id = kwargs['user_id']
                if client.user_id:
                    if client.user_id not in self.user_to_client:
                        self.user_to_client[client.user_id] = set()
                    self.user_to_client[client.user_id].add(client_id)
    
    def join_room(self, client_id: str, room_name: str, is_private: bool = False, 
                  creator_id: str = None, metadata: Dict = None):
        """
        Add a client to a room.
        
        Args:
            client_id: Client ID.
            room_name: Room name.
            is_private: Whether the room is private.
            creator_id: ID of the room creator.
            metadata: Additional room metadata.
        """
        if room_name not in self.rooms:
            self.rooms[room_name] = RoomInfo(
                name=room_name,
                creator_id=creator_id,
                is_private=is_private,
                metadata=metadata or {},
            )
        
        room = self.rooms[room_name]
        
        if client_id not in room.clients:
            room.clients.add(client_id)
            
            # Update client's rooms
            if client_id in self.clients:
                self.clients[client_id].rooms.add(room_name)
        
        # Join the Socket.IO room
        if _socketio:
            join_room(room_name)
        
        return room
    
    def leave_room(self, client_id: str, room_name: str):
        """
        Remove a client from a room.
        
        Args:
            client_id: Client ID.
            room_name: Room name.
        """
        if room_name in self.rooms and client_id in self.rooms[room_name].clients:
            self.rooms[room_name].clients.remove(client_id)
            
            # Update client's rooms
            if client_id in self.clients:
                self.clients[client_id].rooms.discard(room_name)
            
            # Remove room if empty
            if not self.rooms[room_name].clients:
                del self.rooms[room_name]
            
            # Leave the Socket.IO room
            if _socketio:
                leave_room(room_name)
    
    def get_room(self, room_name: str) -> Optional[RoomInfo]:
        """
        Get room information.
        
        Args:
            room_name: Room name.
            
        Returns:
            RoomInfo or None if not found.
        """
        return self.rooms.get(room_name)
    
    def get_room_clients(self, room_name: str) -> List[ClientInfo]:
        """
        Get all clients in a room.
        
        Args:
            room_name: Room name.
            
        Returns:
            List of ClientInfo objects.
        """
        room = self.rooms.get(room_name)
        if not room:
            return []
        
        return [self.clients[client_id] for client_id in room.clients if client_id in self.clients]
    
    def get_client_rooms(self, client_id: str) -> List[RoomInfo]:
        """
        Get all rooms a client is in.
        
        Args:
            client_id: Client ID.
            
        Returns:
            List of RoomInfo objects.
        """
        if client_id not in self.clients:
            return []
        
        return [self.rooms[room_name] for room_name in self.clients[client_id].rooms 
                if room_name in self.rooms]
    
    def get_user_clients(self, user_id: int) -> List[ClientInfo]:
        """
        Get all clients for a user.
        
        Args:
            user_id: User ID.
            
        Returns:
            List of ClientInfo objects.
        """
        if user_id not in self.user_to_client:
            return []
        
        return [self.clients[client_id] for client_id in self.user_to_client[user_id] 
                if client_id in self.clients]
    
    def broadcast_to_room(self, room_name: str, event: str, data: Any = None, 
                        include_self: bool = True, skip_clients: List[str] = None):
        """
        Broadcast a message to all clients in a room.
        
        Args:
            room_name: Room name.
            event: Event name.
            data: Data to send.
            include_self: Whether to include the sender.
            skip_clients: List of client IDs to skip.
        """
        if not _socketio:
            return
        
        skip_clients = skip_clients or []
        
        # Add timestamp if not present
        if isinstance(data, dict) and 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat()
        
        _socketio.emit(event, data, room=room_name, include_self=include_self, skip_sid=skip_clients)
    
    def send_to_client(self, client_id: str, event: str, data: Any = None):
        """
        Send a message to a specific client.
        
        Args:
            client_id: Client ID.
            event: Event name.
            data: Data to send.
        """
        if not _socketio:
            return
        
        # Add timestamp if not present
        if isinstance(data, dict) and 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat()
        
        _socketio.emit(event, data, to=client_id)
    
    def broadcast_to_user(self, user_id: int, event: str, data: Any = None):
        """
        Send a message to all clients of a specific user.
        
        Args:
            user_id: User ID.
            event: Event name.
            data: Data to send.
        """
        if not _socketio:
            return
        
        # Add timestamp if not present
        if isinstance(data, dict) and 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat()
        
        # Get all client IDs for this user
        client_ids = list(self.user_to_client.get(user_id, set()))
        
        for client_id in client_ids:
            _socketio.emit(event, data, to=client_id)
    
    def broadcast_to_all(self, event: str, data: Any = None, skip_clients: List[str] = None):
        """
        Broadcast a message to all connected clients.
        
        Args:
            event: Event name.
            data: Data to send.
            skip_clients: List of client IDs to skip.
        """
        if not _socketio:
            return
        
        skip_clients = skip_clients or []
        
        # Add timestamp if not present
        if isinstance(data, dict) and 'timestamp' not in data:
            data['timestamp'] = datetime.utcnow().isoformat()
        
        _socketio.emit(event, data, broadcast=True, skip_sid=skip_clients)
    
    def create_collaboration_session(self, session_id: str, creator_id: str, 
                                     participants: List[int], **kwargs) -> Dict:
        """
        Create a new collaboration session.
        
        Args:
            session_id: Unique session ID.
            creator_id: User ID of the creator.
            participants: List of user IDs to invite.
            **kwargs: Additional session data.
            
        Returns:
            Session data dictionary.
        """
        session = {
            'session_id': session_id,
            'creator_id': creator_id,
            'participants': set(participants),
            'created_at': datetime.utcnow().isoformat(),
            'status': 'active',
            'data': kwargs.get('data', {}),
            'room_name': f'collab_{session_id}',
        }
        
        self.collaboration_sessions[session_id] = session
        
        # Create a room for this session
        self.join_room(str(creator_id), session['room_name'], is_private=True, 
                       creator_id=str(creator_id))
        
        return session
    
    def get_collaboration_session(self, session_id: str) -> Optional[Dict]:
        """
        Get collaboration session data.
        
        Args:
            session_id: Session ID.
            
        Returns:
            Session data or None if not found.
        """
        return self.collaboration_sessions.get(session_id)
    
    def end_collaboration_session(self, session_id: str):
        """
        End a collaboration session.
        
        Args:
            session_id: Session ID.
        """
        if session_id in self.collaboration_sessions:
            session = self.collaboration_sessions[session_id]
            session['status'] = 'ended'
            session['ended_at'] = datetime.utcnow().isoformat()
            
            # Notify all participants
            room_name = session.get('room_name')
            if room_name:
                self.broadcast_to_room(room_name, 'collaboration_ended', {
                    'session_id': session_id,
                    'message': 'Collaboration session ended',
                })
    
    def get_online_users(self) -> List[Dict]:
        """
        Get list of online users with their client count.
        
        Returns:
            List of user info dictionaries.
        """
        online_users = []
        
        for user_id, client_ids in self.user_to_client.items():
            clients = [self.clients[cid] for cid in client_ids if cid in self.clients]
            if clients:
                # Get the most recent client info
                latest_client = max(clients, key=lambda c: c.last_activity)
                online_users.append({
                    'user_id': user_id,
                    'username': latest_client.username,
                    'client_count': len(clients),
                    'last_activity': latest_client.last_activity.isoformat(),
                })
        
        return online_users
    
    def get_stats(self) -> Dict:
        """
        Get WebSocket server statistics.
        
        Returns:
            Dictionary with server statistics.
        """
        return {
            'total_clients': len(self.clients),
            'total_rooms': len(self.rooms),
            'total_users': len(self.user_to_client),
            'active_collaborations': len([s for s in self.collaboration_sessions.values() 
                                         if s.get('status') == 'active']),
            'online_users': self.get_online_users(),
        }


# Global socket server instance
socket_server = SocketServer()


def get_socketio():
    """Get the global SocketIO instance."""
    return _socketio


def init_socketio(app: Flask):
    """
    Initialize SocketIO with Flask app.
    
    Args:
        app: Flask application.
    """
    socket_server.init_app(app)
    return socket_server
