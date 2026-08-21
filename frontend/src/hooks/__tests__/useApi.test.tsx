"""
useApi Hooks Tests

Unit tests for custom API hooks.
"""

import React from 'react';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import axios from 'axios';
import Cookies from 'js-cookie';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock cookies
jest.mock('js-cookie');

// Import hooks after mocking
import {
  useApiGet,
  useApiPost,
  useApiPut,
  useApiDelete,
  useGraphStats,
  useGraphNodes,
  useGraphEdges,
  useAnomalyDetection,
  useEntityResolution,
  useUsers,
  useLogin,
  useLogout,
  useSystemHealth,
  useTheme,
  useLocalStorage,
  useDebounce,
  usePrevious,
} from '../useApi';

// Create a wrapper component for testing hooks
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useApiGet', () => {
  it('should fetch data successfully', async () => {
    const mockData = { id: 1, name: 'Test' };
    mockedAxios.get.mockResolvedValue({ data: mockData });

    const wrapper = createWrapper();
    const { result } = renderHook(() => useApiGet<any>('test-key', '/api/test'), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
      expect(result.current.data).toEqual(mockData);
    });
  });

  it('should handle errors', async () => {
    mockedAxios.get.mockRejectedValue(new Error('Network error'));

    const wrapper = createWrapper();
    const { result } = renderHook(() => useApiGet<any>('test-key', '/api/test'), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
  });

  it('should pass params to request', async () => {
    const mockData = { id: 1 };
    mockedAxios.get.mockResolvedValue({ data: mockData });

    const wrapper = createWrapper();
    renderHook(() => useApiGet<any>('test-key', '/api/test', { params: { page: 1 } }), { wrapper });

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/test', { params: { page: 1 } });
    });
  });
});

describe('useApiPost', () => {
  it('should post data successfully', async () => {
    const mockData = { id: 1 };
    mockedAxios.post.mockResolvedValue({ data: mockData });

    const wrapper = createWrapper();
    const { result } = renderHook(() => useApiPost<any, { name: string }>('/api/test'), { wrapper });

    result.current.mutate({ name: 'Test' });

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/test', { name: 'Test' });
    });
  });
});

describe('useGraphStats', () => {
  it('should fetch graph stats', async () => {
    const mockStats = { node_count: 100, edge_count: 200 };
    mockedAxios.get.mockResolvedValue({ data: mockStats });

    const wrapper = createWrapper();
    const { result } = renderHook(() => useGraphStats(), { wrapper });

    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
      expect(result.current.data).toEqual(mockStats);
    });
  });
});

describe('useGraphNodes', () => {
  it('should fetch graph nodes with params', async () => {
    const mockNodes = [{ id: '1', label: 'Node 1' }];
    mockedAxios.get.mockResolvedValue({ data: mockNodes });

    const wrapper = createWrapper();
    const { result } = renderHook(() => useGraphNodes({ search: 'test' }), { wrapper });

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/graph/nodes', { params: { search: 'test' } });
      expect(result.current.data).toEqual(mockNodes);
    });
  });
});

describe('useGraphEdges', () => {
  it('should fetch graph edges', async () => {
    const mockEdges = [{ id: '1', source: '1', target: '2' }];
    mockedAxios.get.mockResolvedValue({ data: mockEdges });

    const wrapper = createWrapper();
    const { result } = renderHook(() => useGraphEdges(), { wrapper });

    await waitFor(() => {
      expect(result.current.data).toEqual(mockEdges);
    });
  });
});

describe('useAnomalyDetection', () => {
  it('should detect anomalies', async () => {
    const mockResult = { anomalies: [1, 2, 3] };
    mockedAxios.post.mockResolvedValue({ data: mockResult });

    const wrapper = createWrapper();
    const { result } = renderHook(() => useAnomalyDetection(), { wrapper });

    result.current.mutate({ data: [1, 2, 3, 100], method: 'statistical', threshold: 3 });

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/ai/anomalies/detect', {
        data: [1, 2, 3, 100],
        method: 'statistical',
        threshold: 3,
      });
    });
  });
});

describe('useEntityResolution', () => {
  it('should resolve entities', async () => {
    const mockResult = { matches: [{ id: 1, score: 0.95 }] };
    mockedAxios.post.mockResolvedValue({ data: mockResult });

    const wrapper = createWrapper();
    const { result } = renderHook(() => useEntityResolution(), { wrapper });

    result.current.mutate({ entities: [{ id: 1 }], method: 'exact', threshold: 0.85 });

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/ai/entities/resolve', {
        entities: [{ id: 1 }],
        method: 'exact',
        threshold: 0.85,
      });
    });
  });
});

describe('useUsers', () => {
  it('should fetch users', async () => {
    const mockUsers = [{ id: 1, username: 'admin' }];
    mockedAxios.get.mockResolvedValue({ data: mockUsers });

    const wrapper = createWrapper();
    const { result } = renderHook(() => useUsers(), { wrapper });

    await waitFor(() => {
      expect(result.current.data).toEqual(mockUsers);
    });
  });
});

describe('useLogin', () => {
  it('should login successfully', async () => {
    const mockResponse = { access_token: 'test-token', refresh_token: 'test-refresh' };
    mockedAxios.post.mockResolvedValue({ data: mockResponse });

    const wrapper = createWrapper();
    const { result } = renderHook(() => useLogin(), { wrapper });

    result.current.mutate({ username: 'admin', password: 'password' });

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/security/token', {
        username: 'admin',
        password: 'password',
        grant_type: 'password',
      });
    });
  });
});

describe('useSystemHealth', () => {
  it('should fetch system health', async () => {
    const mockHealth = { status: 'healthy', version: '7.0.0' };
    mockedAxios.get.mockResolvedValue({ data: mockHealth });

    const wrapper = createWrapper();
    const { result } = renderHook(() => useSystemHealth(), { wrapper });

    await waitFor(() => {
      expect(result.current.data).toEqual(mockHealth);
    });
  });
});

describe('useTheme', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should initialize with light theme', () => {
    const { result } = renderHook(() => useTheme());
    expect(result.current.theme).toBe('light');
  });

  it('should toggle theme', () => {
    const { result } = renderHook(() => useTheme());
    
    result.current.toggleTheme();
    expect(result.current.theme).toBe('dark');
    
    result.current.toggleTheme();
    expect(result.current.theme).toBe('light');
  });

  it('should persist theme in localStorage', () => {
    const { result } = renderHook(() => useTheme());
    
    result.current.setTheme('dark');
    expect(localStorage.getItem('theme')).toBe('dark');
  });
});

describe('useLocalStorage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should initialize with default value', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
    expect(result.current.value).toBe('default-value');
  });

  it('should read from localStorage if value exists', () => {
    localStorage.setItem('test-key', JSON.stringify('stored-value'));
    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
    expect(result.current.value).toBe('stored-value');
  });

  it('should update value and localStorage', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
    
    result.current.setValue('new-value');
    expect(result.current.value).toBe('new-value');
    expect(localStorage.getItem('test-key')).toBe(JSON.stringify('new-value'));
  });

  it('should remove value from localStorage', () => {
    localStorage.setItem('test-key', JSON.stringify('stored-value'));
    const { result } = renderHook(() => useLocalStorage('test-key', 'default-value'));
    
    result.current.removeValue();
    expect(result.current.value).toBe('default-value');
    expect(localStorage.getItem('test-key')).toBeNull();
  });
});

describe('useDebounce', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should debounce value changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: 'initial', delay: 100 } }
    );

    expect(result.current).toBe('initial');

    rerender({ value: 'updated', delay: 100 });
    expect(result.current).toBe('initial');

    jest.advanceTimersByTime(100);
    expect(result.current).toBe('updated');
  });
});

describe('usePrevious', () => {
  it('should return undefined on first render', () => {
    const { result } = renderHook(
      ({ value }) => usePrevious(value),
      { initialProps: { value: 'initial' } }
    );

    expect(result.current).toBeUndefined();
  });

  it('should return previous value on subsequent renders', () => {
    const { result, rerender } = renderHook(
      ({ value }) => usePrevious(value),
      { initialProps: { value: 'initial' } }
    );

    rerender({ value: 'updated' });
    expect(result.current).toBe('initial');

    rerender({ value: 'updated-again' });
    expect(result.current).toBe('updated');
  });
});
