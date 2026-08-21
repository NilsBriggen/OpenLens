import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import Cookies from 'js-cookie';
import { getWebSocketUrl, wsEndpoints } from '../lib/apiClient';

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

const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_BASE_DELAY = 3000; // ms
const MAX_BUFFERED_MESSAGES = 100;

/**
 * The live socket is held in refs rather than state on purpose.
 *
 * Keeping it in state made every connect() call change the identity of the
 * `connect`/`reconnect` callbacks, which in turn re-ran the effects that call
 * them - an unbounded connect loop that re-rendered continuously and prevented
 * the app from painting at all. Refs keep the connection lifecycle out of the
 * render cycle; only the values the UI actually shows live in state.
 */
export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
  children,
  url,
}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [subscriptions, setSubscriptions] = useState<string[]>([]);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const attemptsRef = useRef(0);
  const subscriptionsRef = useRef<string[]>([]);
  // Cleared on unmount so a pending close handler cannot resurrect the socket.
  const activeRef = useRef(true);

  const getSocketUrl = useCallback((): string => {
    if (url) {
      const token = Cookies.get('access_token');
      return token ? `${url}?token=${token}` : url;
    }
    return getWebSocketUrl(wsEndpoints.root);
  }, [url]);

  const connect = useCallback(() => {
    if (!activeRef.current) return;

    // Don't stack connections if one is already open or opening.
    const existing = socketRef.current;
    if (existing && (existing.readyState === WebSocket.OPEN || existing.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const socket = new WebSocket(getSocketUrl());
    socketRef.current = socket;

    socket.onopen = () => {
      if (!activeRef.current) return;
      attemptsRef.current = 0;
      setReconnectAttempts(0);
      setIsConnected(true);

      subscriptionsRef.current.forEach((channel) => {
        socket.send(JSON.stringify({ type: 'subscribe', channel }));
      });
    };

    socket.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        setMessages((prev) => [...prev.slice(-(MAX_BUFFERED_MESSAGES - 1)), message]);
      } catch (error) {
        console.error('WebSocket message parsing error:', error);
      }
    };

    socket.onclose = () => {
      if (socketRef.current === socket) {
        socketRef.current = null;
      }
      if (!activeRef.current) return;

      setIsConnected(false);

      if (attemptsRef.current >= MAX_RECONNECT_ATTEMPTS) return;

      const delay = RECONNECT_BASE_DELAY * Math.pow(2, attemptsRef.current);
      attemptsRef.current += 1;
      setReconnectAttempts(attemptsRef.current);

      reconnectTimerRef.current = setTimeout(connect, delay);
    };

    socket.onerror = () => {
      // `onclose` always follows, and handles the retry. Logging the raw Event
      // here just floods the console during a normal backend restart.
    };
  }, [getSocketUrl]);

  const reconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    attemptsRef.current = 0;
    setReconnectAttempts(0);

    const socket = socketRef.current;
    socketRef.current = null;
    socket?.close();

    connect();
  }, [connect]);

  const sendMessage = useCallback((message: any) => {
    const socket = socketRef.current;
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected. Message not sent:', message);
    }
  }, []);

  const subscribe = useCallback((channel: string) => {
    if (subscriptionsRef.current.includes(channel)) return;

    subscriptionsRef.current = [...subscriptionsRef.current, channel];
    setSubscriptions(subscriptionsRef.current);

    const socket = socketRef.current;
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: 'subscribe', channel }));
    }
  }, []);

  const unsubscribe = useCallback((channel: string) => {
    subscriptionsRef.current = subscriptionsRef.current.filter((c) => c !== channel);
    setSubscriptions(subscriptionsRef.current);

    const socket = socketRef.current;
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: 'unsubscribe', channel }));
    }
  }, []);

  // Open the connection once, while authenticated.
  useEffect(() => {
    activeRef.current = true;

    if (Cookies.get('access_token')) {
      connect();
    }

    return () => {
      activeRef.current = false;

      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }

      const socket = socketRef.current;
      socketRef.current = null;
      socket?.close();
    };
  }, [connect]);

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
