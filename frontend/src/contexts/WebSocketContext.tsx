import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import Cookies from 'js-cookie';
import { getWebSocketUrl } from '../lib/apiClient';

interface WebSocketMessage {
  type: string;
  data: any;
  timestamp: string;
  channel?: string;
}

interface WebSocketContextType {
  isConnected: boolean;
  messages: WebSocketMessage[];
  sendMessage: (message: any) => void;
  subscribe: (channel: string) => void;
  unsubscribe: (channel: string) => void;
  subscriptions: string[];
  reconnect: () => void;
  reconnectAttempts: number;
}

const WebSocketContext = createContext<WebSocketContextType>({
  isConnected: false,
  messages: [],
  sendMessage: () => {},
  subscribe: () => {},
  unsubscribe: () => {},
  subscriptions: [],
  reconnect: () => {},
  reconnectAttempts: 0,
});

interface WebSocketProviderProps {
  children: React.ReactNode;
  url?: string;
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
  children,
  url,
}) => {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [subscriptions, setSubscriptions] = useState<string[]>([]);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000; // 3 seconds

  const getSocketUrl = useCallback((): string => {
    if (url) {
      const token = Cookies.get('access_token');
      return `${url}?token=${token}`;
    }
    return getWebSocketUrl('/ws');
  }, [url]);

  const connect = useCallback(() => {
    const wsUrl = getSocketUrl();
    
    const newSocket = new WebSocket(wsUrl);
    setSocket(newSocket);

    newSocket.onopen = () => {
      setIsConnected(true);
      setReconnectAttempts(0);
      
      // Resubscribe to all channels
      subscriptions.forEach(channel => {
        newSocket.send(JSON.stringify({ type: 'subscribe', channel }));
      });
    };

    newSocket.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        setMessages(prev => [...prev.slice(-99), message]); // Keep last 100 messages
      } catch (error) {
        console.error('WebSocket message parsing error:', error);
      }
    };

    newSocket.onclose = () => {
      setIsConnected(false);
      
      // Attempt to reconnect with exponential backoff
      if (reconnectAttempts < maxReconnectAttempts) {
        const delay = reconnectDelay * Math.pow(2, reconnectAttempts);
        setTimeout(() => {
          setReconnectAttempts(prev => prev + 1);
          connect();
        }, delay);
      }
    };

    newSocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return newSocket;
  }, [getSocketUrl, subscriptions, reconnectAttempts]);

  const sendMessage = useCallback((message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected. Message not sent:', message);
      // Queue message for when connection is established
      setTimeout(() => {
        if (socket && isConnected) {
          socket.send(JSON.stringify(message));
        }
      }, 1000);
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

  const reconnect = useCallback(() => {
    if (socket) {
      socket.close();
    }
    setReconnectAttempts(0);
    connect();
  }, [socket, connect]);

  // Initialize connection when authenticated
  useEffect(() => {
    const token = Cookies.get('access_token');
    if (token) {
      connect();
    }
    
    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, [connect]);

  // Reconnect when token changes
  useEffect(() => {
    const token = Cookies.get('access_token');
    if (token && !isConnected) {
      reconnect();
    }
  }, [isConnected, reconnect]);

  const value: WebSocketContextType = {
    isConnected,
    messages,
    sendMessage,
    subscribe,
    unsubscribe,
    subscriptions,
    reconnect,
    reconnectAttempts,
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
