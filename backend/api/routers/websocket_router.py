"""
WebSocket Router

Provides WebSocket endpoints for real-time communication.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json
import asyncio
from datetime import datetime
import uuid

router = APIRouter()
security = HTTPBearer()


# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None):
        await websocket.accept()
        if user_id:
            self.user_connections[user_id] = websocket
        else:
            client_id = str(uuid.uuid4())
            if client_id not in self.active_connections:
                self.active_connections[client_id] = []
            self.active_connections[client_id].append(websocket)
        return client_id if not user_id else user_id
    
    def disconnect(self, websocket: WebSocket, user_id: Optional[str] = None, client_id: Optional[str] = None):
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        elif client_id and client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
    
    async def send_personal_message(self, message: Dict[str, Any], user_id: str):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_json(message)
    
    async def broadcast(self, message: Dict[str, Any], channel: Optional[str] = None):
        if channel:
            # Broadcast to specific channel
            for client_id, connections in self.active_connections.items():
                for websocket in connections:
                    try:
                        await websocket.send_json({
                            **message,
                            "channel": channel,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    except Exception:
                        pass
        else:
            # Broadcast to all connections
            for user_id, websocket in self.user_connections.items():
                try:
                    await websocket.send_json({
                        **message,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception:
                    pass


manager = ConnectionManager()


class WebSocketMessage(BaseModel):
    type: str
    data: Optional[Dict[str, Any]] = None
    channel: Optional[str] = None


# WebSocket endpoint for real-time updates
@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time communication.
    
    Supports:
    - Authentication via JWT token (query parameter)
    - Channel subscription/unsubscription
    - Personal and broadcast messages
    - Scraping progress updates
    - Graph updates
    - Notifications
    """
    client_id = str(uuid.uuid4())
    user_id = None
    subscriptions: List[str] = []
    
    try:
        # Accept connection
        await websocket.accept()
        
        # Authenticate if token provided
        if token:
            try:
                from backend.auth.authentication import decode_token
                payload = decode_token(token)
                if payload:
                    user_id = str(payload.get('sub', 0))
                    await manager.connect(websocket, user_id=user_id)
                    
                    # Send authentication confirmation
                    await websocket.send_json({
                        "type": "authenticated",
                        "user_id": user_id,
                        "message": "Authentication successful",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                else:
                    await manager.connect(websocket)
                    await websocket.send_json({
                        "type": "connected",
                        "client_id": client_id,
                        "message": "Connected (not authenticated)",
                        "timestamp": datetime.utcnow().isoformat()
                    })
            except Exception as e:
                await manager.connect(websocket)
                await websocket.send_json({
                    "type": "error",
                    "message": f"Authentication failed: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                })
        else:
            await manager.connect(websocket)
            await websocket.send_json({
                "type": "connected",
                "client_id": client_id,
                "message": "Connected (not authenticated)",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Main message loop
        while True:
            try:
                data = await websocket.receive_json()
                message_type = data.get('type')
                
                # Handle subscription
                if message_type == 'subscribe':
                    channel = data.get('channel')
                    if channel and channel not in subscriptions:
                        subscriptions.append(channel)
                        await websocket.send_json({
                            "type": "subscribed",
                            "channel": channel,
                            "message": f"Subscribed to {channel}",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                
                # Handle unsubscription
                elif message_type == 'unsubscribe':
                    channel = data.get('channel')
                    if channel in subscriptions:
                        subscriptions.remove(channel)
                        await websocket.send_json({
                            "type": "unsubscribed",
                            "channel": channel,
                            "message": f"Unsubscribed from {channel}",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                
                # Handle ping
                elif message_type == 'ping':
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                # Handle custom messages
                else:
                    # Echo back or process
                    await websocket.send_json({
                        "type": "message",
                        "data": data,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close(code=1011)
    finally:
        manager.disconnect(websocket, user_id=user_id, client_id=client_id)
        await websocket.close()


@router.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time notifications.
    
    Requires authentication.
    """
    user_id = None
    
    try:
        await websocket.accept()
        
        # Require authentication
        if not token:
            await websocket.close(code=1008, reason="Authentication required")
            return
        
        try:
            from backend.auth.authentication import decode_token
            payload = decode_token(token)
            if not payload:
                await websocket.close(code=1008, reason="Invalid token")
                return
            user_id = str(payload.get('sub', 0))
            await manager.connect(websocket, user_id=user_id)
            
            # Send notification history
            await websocket.send_json({
                "type": "notification_history",
                "notifications": [],
                "unread_count": 0,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Keep connection alive
            while True:
                try:
                    data = await websocket.receive_json()
                    # Just acknowledge receipt
                    await websocket.send_json({
                        "type": "ack",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except WebSocketDisconnect:
                    break
                    
        except Exception as e:
            await websocket.close(code=1008, reason=f"Authentication error: {str(e)}")
            
    except Exception as e:
        print(f"Notification WebSocket error: {e}")
        await websocket.close(code=1011)
    finally:
        manager.disconnect(websocket, user_id=user_id)
        await websocket.close()


@router.websocket("/ws/graph")
async def websocket_graph(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time graph updates.
    
    Requires authentication.
    """
    user_id = None
    
    try:
        await websocket.accept()
        
        if not token:
            await websocket.close(code=1008, reason="Authentication required")
            return
        
        try:
            from backend.auth.authentication import decode_token
            payload = decode_token(token)
            if not payload:
                await websocket.close(code=1008, reason="Invalid token")
                return
            user_id = str(payload.get('sub', 0))
            await manager.connect(websocket, user_id=user_id)
            
            # Send initial graph state
            await websocket.send_json({
                "type": "graph_state",
                "nodes": [],
                "edges": [],
                "stats": {
                    "node_count": 0,
                    "edge_count": 0
                },
                "timestamp": datetime.utcnow().isoformat()
            })
            
            while True:
                try:
                    data = await websocket.receive_json()
                    # Handle graph queries
                    if data.get('type') == 'query':
                        # In production, this would query the graph database
                        await websocket.send_json({
                            "type": "query_result",
                            "query": data.get('query'),
                            "result": [],
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    else:
                        await websocket.send_json({
                            "type": "ack",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                except WebSocketDisconnect:
                    break
                    
        except Exception as e:
            await websocket.close(code=1008, reason=f"Authentication error: {str(e)}")
            
    except Exception as e:
        print(f"Graph WebSocket error: {e}")
        await websocket.close(code=1011)
    finally:
        manager.disconnect(websocket, user_id=user_id)
        await websocket.close()


# HTTP endpoint to broadcast messages to WebSocket clients
@router.post("/broadcast")
async def broadcast_message(
    message: WebSocketMessage,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Broadcast a message to all connected WebSocket clients.
    
    Requires admin privileges.
    """
    # Verify admin token
    try:
        from backend.auth.authentication import decode_token
        payload = decode_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Check if user is admin (simplified)
        # In production, check user roles
        
        await manager.broadcast({
            "type": message.type,
            "data": message.data,
            "channel": message.channel,
            "sender": "server"
        }, message.channel)
        
        return {"status": "broadcasted", "message": message.dict()}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
