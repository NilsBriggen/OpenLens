import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import Cookies from 'js-cookie';

// Create API instance with auth
const createApi = () => {
  const token = Cookies.get('access_token');
  return axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      'Content-Type': 'application/json',
    },
  });
};

// Generic GET request
export const useApiGet = <T>(key: string | string[], url: string, options?: any) => {
  return useQuery<T>({
    queryKey: Array.isArray(key) ? key : [key],
    queryFn: async () => {
      const api = createApi();
      const response = await api.get<T>(url, options);
      return response.data;
    },
    retry: 2,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

// Generic POST request
export const useApiPost = <T, V>(url: string) => {
  return useMutation<T, Error, V>({
    mutationFn: async (data: V) => {
      const api = createApi();
      const response = await api.post<T>(url, data);
      return response.data;
    },
  });
};

// Generic PUT request
export const useApiPut = <T, V>(url: string) => {
  return useMutation<T, Error, V>({
    mutationFn: async (data: V) => {
      const api = createApi();
      const response = await api.put<T>(url, data);
      return response.data;
    },
  });
};

// Generic DELETE request
export const useApiDelete = <T>(url: string) => {
  return useMutation<T, Error, string | number>({
    mutationFn: async (id: string | number) => {
      const api = createApi();
      const response = await api.delete<T>(`${url}/${id}`);
      return response.data;
    },
  });
};

// Graph-specific hooks
export const useGraphStats = () => {
  return useApiGet<any>('graph-stats', '/api/graph/stats');
};

export const useGraphNodes = (params?: any) => {
  return useApiGet<any[]>('graph-nodes', '/api/graph/nodes', { params });
};

export const useGraphEdges = (params?: any) => {
  return useApiGet<any[]>('graph-edges', '/api/graph/edges', { params });
};

// AI-specific hooks
export const useAnomalyDetection = (method: string, data: any) => {
  return useApiPost<any>('/api/ai/anomalies/detect')({ method, data });
};

export const useEntityResolution = (method: string, entities: any[]) => {
  return useApiPost<any>('/api/ai/entities/resolve')({ method, entities });
};

// Scraping-specific hooks
export const useScrapeJobs = () => {
  return useApiGet<any[]>('scrape-jobs', '/api/scraping/jobs');
};

export const useCreateScrapeJob = () => {
  return useApiPost<any, any>('/api/scraping/scrape');
};

// Security-specific hooks
export const useUsers = () => {
  return useApiGet<any[]>('users', '/api/security/users');
};

export const useLogin = () => {
  return useMutation<any, Error, { username: string; password: string }>({
    mutationFn: async (credentials: { username: string; password: string }) => {
      const api = axios.create({
        baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
      });
      const response = await api.post('/api/security/token', {
        username: credentials.username,
        password: credentials.password,
        grant_type: 'password',
      });
      return response.data;
    },
  });
};

export const useLogout = () => {
  const queryClient = useQueryClient();
  return useMutation<void, Error>({
    mutationFn: async () => {
      Cookies.remove('access_token');
      Cookies.remove('refresh_token');
    },
    onSuccess: () => {
      queryClient.clear();
      window.location.href = '/login';
    },
  });
};

// Threat-specific hooks
export const useThreatFeeds = () => {
  return useApiGet<any[]>('threat-feeds', '/api/threat/feeds');
};

export const useIOCs = (params?: any) => {
  return useApiGet<any[]>('iocs', '/api/threat/iocs', { params });
};

export const useAlerts = (params?: any) => {
  return useApiGet<any[]>('alerts', '/api/threat/alerts', { params });
};

// System-specific hooks
export const useSystemHealth = () => {
  return useApiGet<any>('system-health', '/api/system/health');
};

export const useSystemStats = () => {
  return useApiGet<any>('system-stats', '/api/system/stats');
};

// WebSocket hook for real-time updates
export const useWebSocket = (url: string, onMessage: (data: any) => void, onOpen?: () => void, onClose?: () => void) => {
  const [socket, setSocket] = React.useState<WebSocket | null>(null);
  const [isConnected, setIsConnected] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);

  React.useEffect(() => {
    const token = Cookies.get('access_token');
    const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}${url}?token=${token}`;
    
    const newSocket = new WebSocket(wsUrl);
    setSocket(newSocket);

    newSocket.onopen = () => {
      setIsConnected(true);
      onOpen && onOpen();
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
      onClose && onClose();
    };

    newSocket.onerror = (err) => {
      setError(err as Error);
    };

    return () => {
      newSocket.close();
    };
  }, [url, onMessage, onOpen, onClose]);

  const sendMessage = (message: any) => {
    if (socket && isConnected) {
      socket.send(JSON.stringify(message));
    }
  };

  return { socket, isConnected, error, sendMessage };
};

// Custom hook for theme management
export const useTheme = () => {
  const [theme, setTheme] = React.useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    return saved === 'dark' || (saved === null && prefersDark) ? 'dark' : 'light';
  });

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.body.setAttribute('data-theme', newTheme);
  };

  React.useEffect(() => {
    document.body.setAttribute('data-theme', theme);
  }, [theme]);

  return { theme, toggleTheme, isDark: theme === 'dark' };
};

// Custom hook for local storage
export const useLocalStorage = <T>(key: string, initialValue: T): [T, (value: T) => void] => {
  const [storedValue, setStoredValue] = React.useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return initialValue;
    }
  });

  const setValue = (value: T) => {
    try {
      setStoredValue(value);
      window.localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  };

  return [storedValue, setValue];
};

// Custom hook for debouncing
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

// Custom hook for previous value
export const usePrevious = <T>(value: T): T | undefined => {
  const ref = React.useRef<T>();

  React.useEffect(() => {
    ref.current = value;
  }, [value]);

  return ref.current;
};

// Export all hooks
export default {
  useApiGet,
  useApiPost,
  useApiPut,
  useApiDelete,
  useGraphStats,
  useGraphNodes,
  useGraphEdges,
  useAnomalyDetection,
  useEntityResolution,
  useScrapeJobs,
  useCreateScrapeJob,
  useUsers,
  useLogin,
  useLogout,
  useThreatFeeds,
  useIOCs,
  useAlerts,
  useSystemHealth,
  useSystemStats,
  useWebSocket,
  useTheme,
  useLocalStorage,
  useDebounce,
  usePrevious,
};
