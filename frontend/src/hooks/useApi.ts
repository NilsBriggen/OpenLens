import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import React from 'react';
import Cookies from 'js-cookie';
import { message } from 'antd';
import {
  apiClient,
  handleLogin,
  handleLogout,
  getAccessToken,
  isAuthenticated,
  graphEndpoints,
  aiEndpoints,
  scrapingEndpoints,
  securityEndpoints,
  threatEndpoints,
  systemEndpoints,
  getWebSocketUrl,
} from '../lib/apiClient';

// ============================================================================
// Generic API Hooks
// ============================================================================

// Generic GET request with React Query
export const useApiGet = <T>(
  key: string | string[],
  url: string,
  options?: {
    params?: Record<string, any>;
    enabled?: boolean;
    staleTime?: number;
    cacheTime?: number;
    retry?: number | false;
  }
) => {
  return useQuery<T>({
    queryKey: Array.isArray(key) ? key : [key],
    queryFn: async () => {
      const response = await apiClient.get<T>(url, { params: options?.params });
      return response.data;
    },
    enabled: options?.enabled !== false,
    retry: options?.retry ?? 2,
    staleTime: options?.staleTime ?? 5 * 60 * 1000, // 5 minutes
    cacheTime: options?.cacheTime ?? 10 * 60 * 1000, // 10 minutes
  });
};

// Generic POST request
export const useApiPost = <T, V = any>(url: string, config?: { onSuccess?: (data: T) => void; onError?: (error: Error) => void }) => {
  return useMutation<T, Error, V>({
    mutationFn: async (data: V) => {
      const response = await apiClient.post<T>(url, data);
      return response.data;
    },
    onSuccess: config?.onSuccess,
    onError: (error) => {
      config?.onError?.(error);
      if (error.message && !error.message.includes('canceled')) {
        message.error(`Request failed: ${error.message}`);
      }
    },
  });
};

// Generic PUT request
export const useApiPut = <T, V = any>(url: string, config?: { onSuccess?: (data: T) => void; onError?: (error: Error) => void }) => {
  return useMutation<T, Error, V>({
    mutationFn: async (data: V) => {
      const response = await apiClient.put<T>(url, data);
      return response.data;
    },
    onSuccess: config?.onSuccess,
    onError: config?.onError,
  });
};

// Generic DELETE request
export const useApiDelete = <T = any>(url: string, config?: { onSuccess?: (data: T) => void; onError?: (error: Error) => void }) => {
  return useMutation<T, Error, string | number>({
    mutationFn: async (id: string | number) => {
      const response = await apiClient.delete<T>(`${url}/${id}`);
      return response.data;
    },
    onSuccess: config?.onSuccess,
    onError: config?.onError,
  });
};

// Generic PATCH request
export const useApiPatch = <T, V = any>(url: string, config?: { onSuccess?: (data: T) => void; onError?: (error: Error) => void }) => {
  return useMutation<T, Error, V>({
    mutationFn: async (data: V) => {
      const response = await apiClient.patch<T>(url, data);
      return response.data;
    },
    onSuccess: config?.onSuccess,
    onError: config?.onError,
  });
};

// ============================================================================
// Graph Analytics Hooks
// ============================================================================

export const useGraphStats = (options?: { enabled?: boolean; refetchInterval?: number }) => {
  return useApiGet<any>('graph-stats', graphEndpoints.stats, {
    enabled: options?.enabled,
    staleTime: 30 * 1000, // 30 seconds for real-time data
    retry: false,
  });
};

export const useGraphNodes = (params?: Record<string, any>, options?: { enabled?: boolean }) => {
  return useApiGet<any[]>('graph-nodes', graphEndpoints.nodes, {
    params,
    enabled: options?.enabled,
    staleTime: 60 * 1000, // 1 minute
  });
};

export const useGraphEdges = (params?: Record<string, any>, options?: { enabled?: boolean }) => {
  return useApiGet<any[]>('graph-edges', graphEndpoints.edges, {
    params,
    enabled: options?.enabled,
    staleTime: 60 * 1000,
  });
};

export const useGraphQuery = (query: string, params?: Record<string, any>) => {
  return useApiPost<any, { query: string; params?: Record<string, any> }>(graphEndpoints.query);
};

export const useGraphCentrality = () => {
  return useApiPost<any, { algorithm: string; limit?: number }>(graphEndpoints.centrality);
};

export const useGraphCommunities = () => {
  return useApiPost<any, { algorithm: string; resolution?: number }>(graphEndpoints.communities);
};

export const useGraphPath = () => {
  return useApiPost<any, { start_node: string; end_node: string; max_depth?: number; algorithm?: string }>(
    graphEndpoints.path
  );
};

export const useGraphVisualization = (type: 'matplotlib' | 'pyvis' | 'plotly') => {
  const endpoint = graphEndpoints.visualization[type];
  return useApiGet<any>(`graph-viz-${type}`, endpoint);
};

export const useTemporalPatterns = () => {
  return useApiGet<any>('temporal-patterns', graphEndpoints.temporal.patterns);
};

export const useGraphEvolution = () => {
  return useApiGet<any>('graph-evolution', graphEndpoints.temporal.evolution);
};

// ============================================================================
// AI/ML Hooks
// ============================================================================

export const useAnomalyDetection = () => {
  return useApiPost<any, { data: any[]; method?: string; threshold?: number }>(aiEndpoints.anomalies.detect);
};

export const useAnomalyScores = () => {
  return useApiGet<any>('anomaly-scores', aiEndpoints.anomalies.scores);
};

export const useEntityResolution = () => {
  return useApiPost<any, { entities: any[]; method?: string; threshold?: number }>(aiEndpoints.entities.resolve);
};

export const useEntityDeduplication = () => {
  return useApiPost<any>(aiEndpoints.entities.deduplicate);
};

export const useLinkPrediction = () => {
  return useApiPost<any, { node1: string; node2: string; method?: string }>(aiEndpoints.predict.link);
};

export const useNodeClassification = () => {
  return useApiPost<any, { node_id: string; features: Record<string, number>; method?: string }>(
    aiEndpoints.predict.node
  );
};

export const useGraphEvolutionPrediction = () => {
  return useApiGet<any>('graph-evolution-prediction', aiEndpoints.predict.graphEvolution);
};

export const useThreatPrediction = () => {
  return useApiGet<any>('threat-prediction', aiEndpoints.predict.threats);
};

// ============================================================================
// Scraping Hooks
// ============================================================================

export const useScrapeJobs = (params?: Record<string, any>) => {
  return useApiGet<any[]>('scrape-jobs', scrapingEndpoints.jobs, { params });
};

export const useCreateScrapeJob = () => {
  return useApiPost<any, any>(scrapingEndpoints.scrape);
};

export const useScrapeVkUser = () => {
  return useApiPost<any, { user_id: string; username?: string }>(scrapingEndpoints.vk.user);
};

export const useScrapeVkPosts = () => {
  return useApiPost<any, { user_id: string; limit?: number }>(scrapingEndpoints.vk.posts);
};

export const useScrapeVkSearch = () => {
  return useApiPost<any, { query: string; limit?: number }>(scrapingEndpoints.vk.search);
};

export const useScrapeTwitterTweets = () => {
  return useApiPost<any, { query: string; limit?: number }>(scrapingEndpoints.twitter.tweets);
};

export const useScrapeTwitterUser = () => {
  return useApiPost<any, { username: string }>(scrapingEndpoints.twitter.user);
};

export const useScrapeTwitterTrends = () => {
  return useApiGet<any>('twitter-trends', scrapingEndpoints.twitter.trends);
};

export const useScrapeInstagramUser = () => {
  return useApiPost<any, { username: string }>(scrapingEndpoints.instagram.user);
};

export const useScrapeInstagramPosts = () => {
  return useApiPost<any, { username: string; limit?: number }>(scrapingEndpoints.instagram.posts);
};

export const useScrapeInstagramHashtag = () => {
  return useApiPost<any, { hashtag: string; limit?: number }>(scrapingEndpoints.instagram.hashtag);
};

// ============================================================================
// Security & Authentication Hooks
// ============================================================================

export const useUsers = (params?: Record<string, any>) => {
  return useApiGet<any[]>('users', securityEndpoints.users, { params });
};

export const useUser = (userId: string) => {
  return useApiGet<any>(`user-${userId}`, `${securityEndpoints.users}/${userId}`);
};

export const useCreateUser = () => {
  return useApiPost<any, { username: string; password: string; email?: string; full_name?: string }>(
    securityEndpoints.users
  );
};

export const useUpdateUser = (userId: string) => {
  return useApiPut<any, { email?: string; full_name?: string; password?: string }>(
    `${securityEndpoints.users}/${userId}`
  );
};

export const useLogin = () => {
  const queryClient = useQueryClient();
  
  return useMutation<any, Error, { username: string; password: string }>({
    mutationFn: async (credentials: { username: string; password: string }) => {
      const response = await apiClient.post(securityEndpoints.token, {
        username: credentials.username,
        password: credentials.password,
        grant_type: 'password',
      });
      
      // Store tokens
      handleLogin(response.data);
      
      return response.data;
    },
    onSuccess: (data) => {
      queryClient.clear();
      message.success(`Welcome back, ${data.user?.username || 'user'}!`);
    },
    onError: (error) => {
      message.error('Login failed. Please check your credentials.');
    },
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();
  
  return useMutation<void, Error>({
    mutationFn: async () => {
      try {
        await apiClient.post(securityEndpoints.logout);
      } catch (error) {
        // Ignore errors on logout
        console.warn('Logout API call failed:', error);
      } finally {
        handleLogout();
      }
    },
    onSuccess: () => {
      queryClient.clear();
      message.success('Logged out successfully');
      window.location.href = '/login';
    },
  });
};

export const useRefreshToken = () => {
  return useMutation<any, Error, string>({
    mutationFn: async (refreshToken: string) => {
      const response = await apiClient.post(securityEndpoints.refresh, { refresh_token: refreshToken });
      handleLogin(response.data);
      return response.data;
    },
  });
};

export const useCurrentUser = () => {
  return useQuery<any>({
    queryKey: ['current-user'],
    queryFn: async () => {
      const response = await apiClient.get(securityEndpoints.users + '/me');
      return response.data;
    },
    enabled: isAuthenticated(),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useRoles = () => {
  return useApiGet<any[]>('roles', securityEndpoints.roles);
};

export const useCreateRole = () => {
  return useApiPost<any, { name: string; description?: string }>(securityEndpoints.roles);
};

export const usePermissions = () => {
  return useApiGet<any[]>('permissions', securityEndpoints.permissions);
};

export const useCreatePermission = () => {
  return useApiPost<any, { name: string; description?: string }>(securityEndpoints.permissions);
};

export const useAuditLogs = (limit?: number) => {
  return useApiGet<any[]>('audit-logs', securityEndpoints.audit, {
    params: { limit },
  });
};

export const useLogAuditEvent = () => {
  return useApiPost<any, { event_type: string; resource: string; action: string; details?: any }>(
    securityEndpoints.audit
  );
};

// ============================================================================
// Threat Intelligence Hooks
// ============================================================================

export const useThreatFeeds = (params?: Record<string, any>) => {
  return useApiGet<any[]>('threat-feeds', threatEndpoints.feeds, { params });
};

export const useIOCs = (params?: Record<string, any>) => {
  return useApiGet<any[]>('iocs', threatEndpoints.iocs, { params });
};

export const useAlerts = (params?: Record<string, any>) => {
  return useApiGet<any[]>('alerts', threatEndpoints.alerts, { params });
};

export const useThreatRules = () => {
  return useApiGet<any[]>('threat-rules', threatEndpoints.rules);
};

export const useThreatEnrichment = () => {
  return useApiPost<any, { ioc: string; ioc_type: string }>(threatEndpoints.enrichment);
};

export const useThreatCorrelation = () => {
  return useApiPost<any, { iocs: string[] }>(threatEndpoints.correlation);
};

export const useStixImport = () => {
  return useApiPost<any, { bundle: any }>(threatEndpoints.stix);
};

// ============================================================================
// System Hooks
// ============================================================================

export const useSystemHealth = () => {
  return useApiGet<any>('system-health', systemEndpoints.health, {
    staleTime: 30 * 1000, // 30 seconds
    retry: 3,
  });
};

export const useSystemStats = () => {
  return useApiGet<any>('system-stats', systemEndpoints.stats, {
    staleTime: 60 * 1000, // 1 minute
  });
};

export const useSystemConfig = () => {
  return useApiGet<any>('system-config', systemEndpoints.config);
};

export const useSystemLogs = (params?: { level?: string; limit?: number }) => {
  return useApiGet<any[]>('system-logs', systemEndpoints.logs, { params });
};

// ============================================================================
// WebSocket Hook for Real-Time Updates
// ============================================================================

export const useWebSocket = (
  path: string,
  onMessage: (data: any) => void,
  onOpen?: () => void,
  onClose?: () => void,
  onError?: (error: Event) => void
) => {
  const [socket, setSocket] = React.useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = React.useState(false);
  const [error, setError] = React.useState<Event | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = React.useState(0);
  const maxReconnectAttempts = 5;
  const reconnectDelay = 3000; // 3 seconds

  const connect = () => {
    const wsUrl = getWebSocketUrl(path);
    const newSocket = new WebSocket(wsUrl);
    
    newSocket.onopen = () => {
      setIsConnected(true);
      setReconnectAttempts(0);
      onOpen?.();
    };

    newSocket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (err) {
        console.error('WebSocket message parsing error:', err);
      }
    };

    newSocket.onclose = () => {
      setIsConnected(false);
      onClose?.();
      
      // Auto-reconnect if not too many attempts
      if (reconnectAttempts < maxReconnectAttempts) {
        setTimeout(() => {
          setReconnectAttempts((prev) => prev + 1);
          connect();
        }, reconnectDelay);
      }
    };

    newSocket.onerror = (err) => {
      setError(err);
      onError?.(err);
    };

    setSocket(newSocket);
    
    return () => {
      newSocket.close();
    };
  };

  React.useEffect(() => {
    if (isAuthenticated()) {
      connect();
    }
    
    return () => {
      if (socket) {
        socket.close();
      }
    };
  }, [path, onMessage, onOpen, onClose, onError]);

  const sendMessage = (message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected. Message not sent:', message);
    }
  };

  const reconnect = () => {
    if (socket) {
      socket.close();
    }
    setReconnectAttempts(0);
    connect();
  };

  return { socket, isConnected, error, sendMessage, reconnect, reconnectAttempts };
};

// ============================================================================
// Theme Hook
// ============================================================================

export const useTheme = () => {
  const [theme, setTheme] = React.useState<'light' | 'dark'>('light');
  const [primaryColor, setPrimaryColor] = React.useState<string>('#1890ff');

  React.useEffect(() => {
    const savedTheme = localStorage.getItem('theme') as 'light' | 'dark' | null;
    const savedColor = localStorage.getItem('primary-color');
    
    if (savedTheme) setTheme(savedTheme);
    if (savedColor) setPrimaryColor(savedColor);
  }, []);

  React.useEffect(() => {
    localStorage.setItem('theme', theme);
    document.body.setAttribute('data-theme', theme);
  }, [theme]);

  React.useEffect(() => {
    localStorage.setItem('primary-color', primaryColor);
  }, [primaryColor]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'));
  };

  const setColor = (color: string) => {
    setPrimaryColor(color);
  };

  return { theme, primaryColor, toggleTheme, setColor, setTheme };
};

// ============================================================================
// Local Storage Hook
// ============================================================================

export const useLocalStorage = <T>(key: string, initialValue: T) => {
  const [storedValue, setStoredValue] = React.useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      window.localStorage.setItem(key, JSON.stringify(valueToStore));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  };

  const removeValue = () => {
    try {
      window.localStorage.removeItem(key);
      setStoredValue(initialValue);
    } catch (error) {
      console.error('Error removing from localStorage:', error);
    }
  };

  return { value: storedValue, setValue, removeValue };
};

// ============================================================================
// Debounce Hook
// ============================================================================

export const useDebounce = <T>(value: T, delay: number): T => {
  const [debouncedValue, setDebouncedValue] = React.useState<T>(value);

  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// ============================================================================
// Previous Value Hook
// ============================================================================

export const usePrevious = <T>(value: T): T | undefined => {
  const ref = React.useRef<T>();

  React.useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
};

// ============================================================================
// Export Authentication Utilities
// ============================================================================

export { handleLogin, handleLogout, getAccessToken, isAuthenticated, getWebSocketUrl };

export default {
  // Generic hooks
  useApiGet,
  useApiPost,
  useApiPut,
  useApiDelete,
  useApiPatch,
  
  // Graph hooks
  useGraphStats,
  useGraphNodes,
  useGraphEdges,
  useGraphQuery,
  useGraphCentrality,
  useGraphCommunities,
  useGraphPath,
  useGraphVisualization,
  useTemporalPatterns,
  useGraphEvolution,
  
  // AI hooks
  useAnomalyDetection,
  useAnomalyScores,
  useEntityResolution,
  useEntityDeduplication,
  useLinkPrediction,
  useNodeClassification,
  useGraphEvolutionPrediction,
  useThreatPrediction,
  
  // Scraping hooks
  useScrapeJobs,
  useCreateScrapeJob,
  useScrapeVkUser,
  useScrapeVkPosts,
  useScrapeVkSearch,
  useScrapeTwitterTweets,
  useScrapeTwitterUser,
  useScrapeTwitterTrends,
  useScrapeInstagramUser,
  useScrapeInstagramPosts,
  useScrapeInstagramHashtag,
  
  // Security hooks
  useUsers,
  useUser,
  useCreateUser,
  useUpdateUser,
  useLogin,
  useLogout,
  useRefreshToken,
  useCurrentUser,
  useRoles,
  useCreateRole,
  usePermissions,
  useCreatePermission,
  useAuditLogs,
  useLogAuditEvent,
  
  // Threat hooks
  useThreatFeeds,
  useIOCs,
  useAlerts,
  useThreatRules,
  useThreatEnrichment,
  useThreatCorrelation,
  useStixImport,
  
  // System hooks
  useSystemHealth,
  useSystemStats,
  useSystemConfig,
  useSystemLogs,
  
  // Utility hooks
  useWebSocket,
  useTheme,
  useLocalStorage,
  useDebounce,
  usePrevious,
  
  // Auth utilities
  handleLogin,
  handleLogout,
  getAccessToken,
  isAuthenticated,
  getWebSocketUrl,
};
