import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import Cookies from 'js-cookie';

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
}

interface WebSocketContextType {
  isConnected: boolean;
  messages: WebSocketMessage[];
  sendMessage: (message: any) => void;
  subscribe: (channel: string) => void;
  unsubscribe: (channel: string) => void;
  subscriptions: string[];
}

const WebSocketContext = createContext<WebSocketContextType>({
  isConnected: false,
  messages: [],
  sendMessage: () => {},
  subscribe: () => {},
  unsubscribe: () => {},
  subscriptions: [],
});

interface WebSocketProviderProps {
  children: React.ReactNode;
  url?: string;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
  children,
  url = 'ws://localhost:8000/ws',
}) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [subscriptions, setSubscriptions] = useState<string[]>([]);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const maxReconnectAttempts = 5;

  const connect = useCallback(() => {
    const token = Cookies.get('access_token');
    const wsUrl = `${url}?token=${token}`;
    
    const newSocket = new WebSocket(wsUrl);
    setSocket(newSocket);

    newSocket.onopen = () => {
      setIsConnected(true);
      setReconnectAttempts(0);
      console.log('WebSocket connected');
      
      // Resubscribe to all channels
      subscriptions.forEach(channel => {
        newSocket.send(JSON.stringify({ type: 'subscribe', channel }));
      });
    };

    newSocket.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        setMessages(prev => [...prev, message]);
      } catch (error) {
        console.error('WebSocket message parsing error:', error);
      }
    };

    newSocket.onclose = () => {
      setIsConnected(false);
      console.log('WebSocket disconnected');
      
      // Attempt to reconnect
      if (reconnectAttempts < maxReconnectAttempts) {
        setTimeout(() => {
          setReconnectAttempts(prev => prev + 1);
          connect();
        }, 1000 * Math.pow(2, reconnectAttempts));
      }
    };

    newSocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return newSocket;
  }, [url, subscriptions, reconnectAttempts]);

  const sendMessage = useCallback((message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected. Message not sent:', message);
    }
  }, [socket, isConnected]);

  const subscribe = useCallback((channel: string) => {
    if (!subscriptions.includes(channel)) {
      setSubscriptions(prev => [...prev, channel]);
      if (socket && isConnected) {
        socket.send(JSON.stringify({ type: 'subscribe', channel }));
      }
    }
  }, [socket, isConnected, subscriptions]);

  const unsubscribe = useCallback((channel: string) => {
    setSubscriptions(prev => prev.filter(c => c !== channel));
    if (socket && isConnected) {
      socket.send(JSON.stringify({ type: 'unsubscribe', channel }));
    }
  }, [socket, isConnected]);

  // Initialize connection
  useEffect(() => {
    connect();
    
    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, [connect]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, [socket]);

  const value: WebSocketContextType = {
    isConnected,
    messages,
    sendMessage,
    subscribe,
    unsubscribe,
    subscriptions,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

export default WebSocketContext;
