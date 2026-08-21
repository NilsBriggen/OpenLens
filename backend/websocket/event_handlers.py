"""
Event Handlers for WebSocket

Provides event handlers for real-time features:
- Scraping progress updates
- Notification broadcasting
- Collaborative features
- User presence tracking
- Shared workspace functionality
"""

from typing import Dict, Any, List, Optional
from flask_socketio import emit, join_room, leave_room
from datetime import datetime
import json
import uuid

# Import socket server
from .socket_server import socket_server, get_socketio, ClientInfo, RoomInfo


def register_event_handlers(socketio):
    """
    Register all event handlers with SocketIO.
    
    Args:
        socketio: SocketIO instance.
    """
    
    # ==================== Connection Events ====================
    
    @socketio.on('connect')
    def handle_connect():
        """Handle new client connection."""
        client_id = request.sid
        
        # Get client info from query string or headers
        client_info = {
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', ''),
        }
        
        # Check for authentication token
        token = request.args.get('token') or request.headers.get('Authorization')
        if token:
            # In a real implementation, verify the JWT token
            # For now, just mark as authenticated
            client_info['is_authenticated'] = True
            
            # Extract user info from token (simplified)
            try:
                if token.startswith('Bearer '):
                    token = token[7:]
                # Decode token to get user info
                from auth.authentication import decode_token
                payload = decode_token(token)
                if payload:
                    client_info['user_id'] = int(payload.get('sub', 0))
                    client_info['username'] = payload.get('username', 'unknown')
                    client_info['is_authenticated'] = True
            except Exception:
                pass
        
        client = socket_server.add_client(client_id, client_info)
        
        print(f"Client connected: {client_id} (User: {client.username or 'anonymous'})")
        
        emit('connected', {
            'message': 'Connected to OpenLens WebSocket',
            'client_id': client_id,
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        # Send current server stats
        emit('server_stats', socket_server.get_stats())
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        client_id = request.sid
        
        if client_id in socket_server.clients:
            client = socket_server.clients[client_id]
            print(f"Client disconnected: {client_id} (User: {client.username or 'anonymous'})")
        else:
            print(f"Client disconnected: {client_id}")
        
        socket_server.remove_client(client_id)
        
        # Notify rooms that the client left
        # (This is handled automatically by the leave_room event)
    
    # ==================== Authentication Events ====================
    
    @socketio.on('authenticate')
    def handle_authenticate(data: Dict):
        """
        Handle client authentication.
        
        Args:
            data: Dictionary with 'token' key.
        """
        client_id = request.sid
        token = data.get('token')
        
        if not token:
            emit('error', {'message': 'Token is required'})
            return
        
        # Verify token
        from auth.authentication import verify_token
        payload = verify_token(token)
        
        if not payload:
            emit('error', {'message': 'Invalid or expired token'})
            return
        
        # Update client info
        socket_server.update_client(client_id,
            user_id=int(payload.get('sub', 0)),
            username=payload.get('username', 'unknown'),
            is_authenticated=True,
        )
        
        client = socket_server.clients.get(client_id)
        
        print(f"Client authenticated: {client_id} (User: {client.username})")
        
        emit('authenticated', {
            'message': 'Authentication successful',
            'user_id': client.user_id,
            'username': client.username,
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        # Notify user's other clients
        if client.user_id:
            socket_server.broadcast_to_user(client.user_id, 'user_connected', {
                'client_id': client_id,
                'message': 'New connection established',
            }, skip_clients=[client_id])
    
    @socketio.on('deauthenticate')
    def handle_deauthenticate():
        """Handle client deauthentication."""
        client_id = request.sid
        
        if client_id in socket_server.clients:
            socket_server.update_client(client_id,
                user_id=None,
                username=None,
                is_authenticated=False,
            )
            
            print(f"Client deauthenticated: {client_id}")
            emit('deauthenticated', {'message': 'Deauthentication successful'})
    
    # ==================== Room Events ====================
    
    @socketio.on('join_room')
    def handle_join_room(data: Dict):
        """
        Handle client joining a room.
        
        Args:
            data: Dictionary with 'room' key and optional 'is_private'.
        """
        client_id = request.sid
        room_name = data.get('room')
        is_private = data.get('is_private', False)
        
        if not room_name:
            emit('error', {'message': 'Room name is required'})
            return
        
        # Get client info
        client = socket_server.clients.get(client_id)
        creator_id = str(client.user_id) if client and client.user_id else None
        
        room = socket_server.join_room(client_id, room_name, is_private, creator_id)
        
        print(f"Client {client_id} joined room: {room_name}")
        
        emit('joined_room', {
            'room': room_name,
            'message': f'Joined room {room_name}',
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        # Notify room
        socket_server.broadcast_to_room(room_name, 'user_joined', {
            'client_id': client_id,
            'user_id': client.user_id if client else None,
            'username': client.username if client else 'anonymous',
            'room': room_name,
            'timestamp': datetime.utcnow().isoformat(),
        }, include_self=False)
        
        # Send room info
        emit('room_info', {
            'room': room_name,
            'clients': len(room.clients),
            'is_private': room.is_private,
            'created_at': room.created_at.isoformat(),
        })
    
    @socketio.on('leave_room')
    def handle_leave_room(data: Dict):
        """
        Handle client leaving a room.
        
        Args:
            data: Dictionary with 'room' key.
        """
        client_id = request.sid
        room_name = data.get('room')
        
        if not room_name:
            emit('error', {'message': 'Room name is required'})
            return
        
        socket_server.leave_room(client_id, room_name)
        
        client = socket_server.clients.get(client_id)
        print(f"Client {client_id} left room: {room_name}")
        
        emit('left_room', {
            'room': room_name,
            'message': f'Left room {room_name}',
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        # Notify room
        socket_server.broadcast_to_room(room_name, 'user_left', {
            'client_id': client_id,
            'user_id': client.user_id if client else None,
            'username': client.username if client else 'anonymous',
            'room': room_name,
            'timestamp': datetime.utcnow().isoformat(),
        }, include_self=False)
    
    @socketio.on('get_room_info')
    def handle_get_room_info(data: Dict):
        """
        Get information about a room.
        
        Args:
            data: Dictionary with 'room' key.
        """
        room_name = data.get('room')
        
        if not room_name:
            emit('error', {'message': 'Room name is required'})
            return
        
        room = socket_server.get_room(room_name)
        if not room:
            emit('error', {'message': 'Room not found'})
            return
        
        clients = socket_server.get_room_clients(room_name)
        
        emit('room_info', {
            'room': room.name,
            'clients': [{
                'client_id': c.client_id,
                'user_id': c.user_id,
                'username': c.username,
                'connected_at': c.connected_at.isoformat(),
            } for c in clients],
            'is_private': room.is_private,
            'created_at': room.created_at.isoformat(),
            'creator_id': room.creator_id,
            'client_count': len(clients),
        })
    
    # ==================== Message Events ====================
    
    @socketio.on('message')
    def handle_message(data: Dict):
        """
        Handle incoming message.
        
        Args:
            data: Message data with 'room' and 'message' keys.
        """
        client_id = request.sid
        room_name = data.get('room')
        message = data.get('message')
        message_type = data.get('type', 'text')  # 'text', 'image', 'file', etc.
        
        if not message:
            emit('error', {'message': 'Message is required'})
            return
        
        client = socket_server.clients.get(client_id)
        
        print(f"Message from {client_id} ({client.username or 'anonymous'}): {message[:50]}...")
        
        message_data = {
            'client_id': client_id,
            'user_id': client.user_id if client else None,
            'username': client.username if client else 'anonymous',
            'message': message,
            'type': message_type,
            'room': room_name,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        # Broadcast to room or to all
        if room_name:
            socket_server.broadcast_to_room(room_name, 'message', message_data, include_self=True)
        else:
            emit('message', message_data)
    
    # ==================== Collaboration Events ====================
    
    @socketio.on('create_collaboration')
    def handle_create_collaboration(data: Dict):
        """
        Create a new collaboration session.
        
        Args:
            data: Dictionary with 'participants' and optional 'name'.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        
        if not client or not client.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        participants = data.get('participants', [])
        name = data.get('name', 'Untitled Collaboration')
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create collaboration session
        session = socket_server.create_collaboration_session(
            session_id=session_id,
            creator_id=str(client.user_id),
            participants=[int(p) for p in participants] + [client.user_id],
            name=name,
            data=data.get('data', {}),
        )
        
        print(f"Collaboration created: {session_id} by {client.username}")
        
        emit('collaboration_created', {
            'session_id': session_id,
            'name': name,
            'room_name': session['room_name'],
            'creator_id': client.user_id,
            'creator_username': client.username,
            'participants': list(session['participants']),
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        # Invite participants
        for participant_id in session['participants']:
            if participant_id != client.user_id:
                socket_server.broadcast_to_user(participant_id, 'collaboration_invite', {
                    'session_id': session_id,
                    'name': name,
                    'room_name': session['room_name'],
                    'inviter_id': client.user_id,
                    'inviter_username': client.username,
                    'timestamp': datetime.utcnow().isoformat(),
                })
    
    @socketio.on('join_collaboration')
    def handle_join_collaboration(data: Dict):
        """
        Join an existing collaboration session.
        
        Args:
            data: Dictionary with 'session_id' key.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        
        if not client or not client.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        session_id = data.get('session_id')
        
        if not session_id:
            emit('error', {'message': 'Session ID is required'})
            return
        
        session = socket_server.get_collaboration_session(session_id)
        
        if not session:
            emit('error', {'message': 'Collaboration session not found'})
            return
        
        if client.user_id not in session['participants']:
            emit('error', {'message': 'You are not a participant in this collaboration'})
            return
        
        # Join the room
        room_name = session['room_name']
        socket_server.join_room(client_id, room_name, is_private=True)
        
        print(f"User {client.username} joined collaboration: {session_id}")
        
        emit('collaboration_joined', {
            'session_id': session_id,
            'room_name': room_name,
            'message': f'Joined collaboration {session_id}',
            'timestamp': datetime.utcnow().isoformat(),
        })
        
        # Notify other participants
        socket_server.broadcast_to_room(room_name, 'user_joined_collaboration', {
            'client_id': client_id,
            'user_id': client.user_id,
            'username': client.username,
            'session_id': session_id,
            'timestamp': datetime.utcnow().isoformat(),
        }, include_self=False)
    
    @socketio.on('collaboration_message')
    def handle_collaboration_message(data: Dict):
        """
        Handle a message in a collaboration session.
        
        Args:
            data: Dictionary with 'session_id' and 'message' keys.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        
        if not client or not client.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        session_id = data.get('session_id')
        message = data.get('message')
        message_type = data.get('type', 'text')
        
        if not session_id or not message:
            emit('error', {'message': 'Session ID and message are required'})
            return
        
        session = socket_server.get_collaboration_session(session_id)
        
        if not session:
            emit('error', {'message': 'Collaboration session not found'})
            return
        
        room_name = session['room_name']
        
        message_data = {
            'session_id': session_id,
            'client_id': client_id,
            'user_id': client.user_id,
            'username': client.username,
            'message': message,
            'type': message_type,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        # Broadcast to collaboration room
        socket_server.broadcast_to_room(room_name, 'collaboration_message', message_data, 
                                       include_self=True)
    
    @socketio.on('shared_editor_update')
    def handle_shared_editor_update(data: Dict):
        """
        Handle updates to a shared editor/document.
        
        Args:
            data: Dictionary with 'session_id', 'document_id', and 'content' keys.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        
        if not client or not client.is_authenticated:
            emit('error', {'message': 'Authentication required'})
            return
        
        session_id = data.get('session_id')
        document_id = data.get('document_id')
        content = data.get('content')
        operation = data.get('operation', 'update')  # 'update', 'insert', 'delete'
        
        if not session_id or not document_id:
            emit('error', {'message': 'Session ID and document ID are required'})
            return
        
        session = socket_server.get_collaboration_session(session_id)
        
        if not session:
            emit('error', {'message': 'Collaboration session not found'})
            return
        
        room_name = session['room_name']
        
        update_data = {
            'session_id': session_id,
            'document_id': document_id,
            'client_id': client_id,
            'user_id': client.user_id,
            'username': client.username,
            'content': content,
            'operation': operation,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        # Broadcast to collaboration room
        socket_server.broadcast_to_room(room_name, 'shared_editor_update', update_data, 
                                       include_self=False, skip_clients=[client_id])
        
        # Acknowledge to sender
        emit('shared_editor_ack', {
            'session_id': session_id,
            'document_id': document_id,
            'message': 'Update received',
        })
    
    @socketio.on('cursor_position')
    def handle_cursor_position(data: Dict):
        """
        Handle cursor position updates for collaborative editing.
        
        Args:
            data: Dictionary with 'session_id', 'document_id', 'position', and 'selection' keys.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        
        if not client or not client.is_authenticated:
            return  # Silently ignore unauthenticated cursor updates
        
        session_id = data.get('session_id')
        document_id = data.get('document_id')
        position = data.get('position')
        selection = data.get('selection')
        
        if not session_id or not document_id or not position:
            return
        
        session = socket_server.get_collaboration_session(session_id)
        
        if not session:
            return
        
        room_name = session['room_name']
        
        cursor_data = {
            'session_id': session_id,
            'document_id': document_id,
            'client_id': client_id,
            'user_id': client.user_id,
            'username': client.username,
            'position': position,
            'selection': selection,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        # Broadcast to collaboration room (exclude self to avoid echo)
        socket_server.broadcast_to_room(room_name, 'cursor_position', cursor_data, 
                                       include_self=False, skip_clients=[client_id])
    
    # ==================== Scraping Events ====================
    
    @socketio.on('start_scraping')
    def handle_start_scraping(data: Dict):
        """
        Handle start scraping event.
        
        Args:
            data: Dictionary with scraping parameters.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        job_id = data.get('job_id', str(uuid.uuid4()))
        target = data.get('target', 'unknown')
        platform = data.get('platform', 'unknown')
        
        print(f"Scraping started by {client_id} ({client.username or 'anonymous'}): {platform} - {target}")
        
        # Broadcast to room if specified
        room_name = data.get('room')
        if room_name:
            socket_server.broadcast_to_room(room_name, 'scraping_started', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'target': target,
                'platform': platform,
                'timestamp': datetime.utcnow().isoformat(),
            })
        else:
            emit('scraping_started', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'target': target,
                'platform': platform,
                'timestamp': datetime.utcnow().isoformat(),
            })
    
    @socketio.on('scraping_progress')
    def handle_scraping_progress(data: Dict):
        """
        Handle scraping progress update.
        
        Args:
            data: Dictionary with progress data.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        job_id = data.get('job_id')
        progress = data.get('progress', 0)
        current = data.get('current', 0)
        total = data.get('total', 0)
        items = data.get('items', [])
        
        print(f"Scraping progress from {client_id}: {progress}% ({current}/{total})")
        
        # Broadcast to room if specified
        room_name = data.get('room')
        if room_name:
            socket_server.broadcast_to_room(room_name, 'scraping_progress', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'progress': progress,
                'current': current,
                'total': total,
                'items': items,
                'timestamp': datetime.utcnow().isoformat(),
            })
        else:
            emit('scraping_progress', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'progress': progress,
                'current': current,
                'total': total,
                'items': items,
                'timestamp': datetime.utcnow().isoformat(),
            })
    
    @socketio.on('scraping_complete')
    def handle_scraping_complete(data: Dict):
        """
        Handle scraping completion.
        
        Args:
            data: Dictionary with completion data.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        job_id = data.get('job_id')
        results = data.get('results', {})
        count = data.get('count', 0)
        
        print(f"Scraping completed by {client_id}: {count} items")
        
        # Broadcast to room if specified
        room_name = data.get('room')
        if room_name:
            socket_server.broadcast_to_room(room_name, 'scraping_complete', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'results': results,
                'count': count,
                'timestamp': datetime.utcnow().isoformat(),
            })
        else:
            emit('scraping_complete', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'results': results,
                'count': count,
                'timestamp': datetime.utcnow().isoformat(),
            })
    
    @socketio.on('scraping_error')
    def handle_scraping_error(data: Dict):
        """
        Handle scraping error.
        
        Args:
            data: Dictionary with error data.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        job_id = data.get('job_id')
        error = data.get('error', 'Unknown error')
        
        print(f"Scraping error from {client_id}: {error}")
        
        # Broadcast to room if specified
        room_name = data.get('room')
        if room_name:
            socket_server.broadcast_to_room(room_name, 'scraping_error', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'error': error,
                'timestamp': datetime.utcnow().isoformat(),
            })
        else:
            emit('scraping_error', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'error': error,
                'timestamp': datetime.utcnow().isoformat(),
            })
    
    # ==================== Analysis Events ====================
    
    @socketio.on('start_analysis')
    def handle_start_analysis(data: Dict):
        """
        Handle start analysis event.
        
        Args:
            data: Dictionary with analysis parameters.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        job_id = data.get('job_id', str(uuid.uuid4()))
        analysis_type = data.get('type', 'unknown')
        
        print(f"Analysis started by {client_id}: {analysis_type}")
        
        # Broadcast to room if specified
        room_name = data.get('room')
        if room_name:
            socket_server.broadcast_to_room(room_name, 'analysis_started', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'type': analysis_type,
                'timestamp': datetime.utcnow().isoformat(),
            })
        else:
            emit('analysis_started', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'type': analysis_type,
                'timestamp': datetime.utcnow().isoformat(),
            })
    
    @socketio.on('analysis_progress')
    def handle_analysis_progress(data: Dict):
        """
        Handle analysis progress update.
        
        Args:
            data: Dictionary with progress data.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        job_id = data.get('job_id')
        progress = data.get('progress', 0)
        current = data.get('current', 0)
        total = data.get('total', 0)
        
        print(f"Analysis progress from {client_id}: {progress}% ({current}/{total})")
        
        # Broadcast to room if specified
        room_name = data.get('room')
        if room_name:
            socket_server.broadcast_to_room(room_name, 'analysis_progress', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'progress': progress,
                'current': current,
                'total': total,
                'timestamp': datetime.utcnow().isoformat(),
            })
        else:
            emit('analysis_progress', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'progress': progress,
                'current': current,
                'total': total,
                'timestamp': datetime.utcnow().isoformat(),
            })
    
    @socketio.on('analysis_complete')
    def handle_analysis_complete(data: Dict):
        """
        Handle analysis completion.
        
        Args:
            data: Dictionary with completion data.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        job_id = data.get('job_id')
        results = data.get('results', {})
        
        print(f"Analysis completed by {client_id}")
        
        # Broadcast to room if specified
        room_name = data.get('room')
        if room_name:
            socket_server.broadcast_to_room(room_name, 'analysis_complete', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'results': results,
                'timestamp': datetime.utcnow().isoformat(),
            })
        else:
            emit('analysis_complete', {
                'client_id': client_id,
                'user_id': client.user_id if client else None,
                'username': client.username if client else 'anonymous',
                'job_id': job_id,
                'results': results,
                'timestamp': datetime.utcnow().isoformat(),
            })
    
    # ==================== Notification Events ====================
    
    @socketio.on('send_notification')
    def handle_send_notification(data: Dict):
        """
        Handle sending a notification.
        
        Args:
            data: Dictionary with notification data.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        message = data.get('message', '')
        notification_type = data.get('type', 'info')
        target_user = data.get('target_user')
        target_room = data.get('target_room')
        
        notification = {
            'client_id': client_id,
            'user_id': client.user_id if client else None,
            'username': client.username if client else 'anonymous',
            'message': message,
            'type': notification_type,
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        print(f"Notification from {client_id}: {message[:50]}...")
        
        # Send to specific user
        if target_user:
            socket_server.broadcast_to_user(int(target_user), 'notification', notification)
        # Send to specific room
        elif target_room:
            socket_server.broadcast_to_room(target_room, 'notification', notification)
        # Broadcast to all
        else:
            socket_server.broadcast_to_all('notification', notification)
    
    # ==================== Presence Events ====================
    
    @socketio.on('get_online_users')
    def handle_get_online_users():
        """Get list of online users."""
        online_users = socket_server.get_online_users()
        emit('online_users', {
            'users': online_users,
            'count': len(online_users),
            'timestamp': datetime.utcnow().isoformat(),
        })
    
    @socketio.on('get_server_stats')
    def handle_get_server_stats():
        """Get server statistics."""
        stats = socket_server.get_stats()
        emit('server_stats', stats)
    
    # ==================== Utility Events ====================
    
    @socketio.on('ping')
    def handle_ping():
        """Handle ping request."""
        emit('pong', {
            'timestamp': datetime.utcnow().isoformat(),
        })
    
    @socketio.on('typing')
    def handle_typing(data: Dict):
        """
        Handle typing indicator.
        
        Args:
            data: Dictionary with 'room' key.
        """
        client_id = request.sid
        client = socket_server.clients.get(client_id)
        room_name = data.get('room')
        
        if not room_name:
            return
        
        if client:
            socket_server.broadcast_to_room(room_name, 'user_typing', {
                'client_id': client_id,
                'user_id': client.user_id,
                'username': client.username,
                'room': room_name,
                'timestamp': datetime.utcnow().isoformat(),
            }, include_self=False)


# Import request for the handlers
from flask import request
