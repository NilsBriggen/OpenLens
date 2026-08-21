/**
 * useApi hook tests.
 *
 * The apiClient module is mocked directly (rather than axios), so assertions
 * target exactly what the hooks call.
 */
import React from 'react';
import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { renderHook, waitFor, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

vi.mock('../../lib/apiClient', async () => {
  const actual = await vi.importActual<typeof import('../../lib/apiClient')>('../../lib/apiClient');
  return {
    ...actual,
    apiClient: {
      defaults: { headers: { common: {} } },
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      patch: vi.fn(),
    },
  };
});

import { apiClient } from '../../lib/apiClient';
import {
  useApiGet, useApiPost, useIOCs, useThreatFeeds, useSystemHealth,
  useLogin, useTheme, useLocalStorage, useDebounce,
} from '../useApi';

const mockedGet = apiClient.get as ReturnType<typeof vi.fn>;
const mockedPost = apiClient.post as ReturnType<typeof vi.fn>;

const wrapper = ({ children }: { children: React.ReactNode }) => {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
};

beforeEach(() => {
  vi.clearAllMocks();
  window.localStorage.clear();
});

describe('useApiGet', () => {
  it('fetches data and reports success', async () => {
    mockedGet.mockResolvedValueOnce({ data: { ok: true } });

    const { result } = renderHook(() => useApiGet('test-key', '/api/test'), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data).toEqual({ ok: true });
    expect(mockedGet).toHaveBeenCalledWith('/api/test', { params: undefined });
  });

  it('passes params to the request', async () => {
    mockedGet.mockResolvedValueOnce({ data: [] });

    const { result } = renderHook(
      () => useApiGet('test-params', '/api/test', { params: { page: 1 } }),
      { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockedGet).toHaveBeenCalledWith('/api/test', { params: { page: 1 } });
  });

  it('reports errors', async () => {
    mockedGet.mockRejectedValueOnce(new Error('boom'));

    const { result } = renderHook(
      () => useApiGet('test-error', '/api/test', { retry: false }), { wrapper });

    await waitFor(() => expect(result.current.isError).toBe(true));
  });

  it('honours enabled: false', async () => {
    renderHook(() => useApiGet('gated', '/api/test', { enabled: false }), { wrapper });
    await new Promise((resolve) => setTimeout(resolve, 50));
    expect(mockedGet).not.toHaveBeenCalled();
  });
});

describe('useApiPost', () => {
  it('posts data', async () => {
    mockedPost.mockResolvedValueOnce({ data: { id: '1' } });

    const { result } = renderHook(() => useApiPost('/api/things'), { wrapper });
    await act(async () => {
      await result.current.mutateAsync({ name: 'x' });
    });

    expect(mockedPost).toHaveBeenCalledWith('/api/things', { name: 'x' });
  });
});

describe('domain hooks', () => {
  it('useIOCs fetches from the IOC endpoint with params and options', async () => {
    mockedGet.mockResolvedValueOnce({ data: [{ id: 'i1' }] });

    const { result } = renderHook(
      () => useIOCs({ severity: 'high' }, { staleTime: 1000 }), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockedGet).toHaveBeenCalledWith('/api/threat/iocs',
      { params: { severity: 'high' } });
    expect(result.current.data).toEqual([{ id: 'i1' }]);
  });

  it('useThreatFeeds fetches from the feeds endpoint', async () => {
    mockedGet.mockResolvedValueOnce({ data: [] });

    const { result } = renderHook(() => useThreatFeeds(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockedGet).toHaveBeenCalledWith('/api/threat/feeds', { params: undefined });
  });

  it('useSystemHealth fetches from the health endpoint', async () => {
    mockedGet.mockResolvedValueOnce({ data: { status: 'healthy' } });

    const { result } = renderHook(() => useSystemHealth(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(mockedGet).toHaveBeenCalledWith('/api/system/health', { params: undefined });
  });
});

describe('useLogin', () => {
  it('sends OAuth2 form-encoded credentials (not JSON)', async () => {
    mockedPost.mockResolvedValueOnce({
      data: { access_token: 'a', refresh_token: 'r', user: { username: 'admin' } },
    });

    const { result } = renderHook(() => useLogin(), { wrapper });
    await act(async () => {
      await result.current.mutateAsync({ username: 'admin', password: 'pw' });
    });

    const [url, body, config] = mockedPost.mock.calls[0];
    expect(url).toBe('/api/security/token');
    expect(body).toBeInstanceOf(URLSearchParams);
    expect(String(body)).toBe('username=admin&password=pw&grant_type=password');
    expect(config.headers['Content-Type']).toBe('application/x-www-form-urlencoded');
  });
});

describe('useTheme', () => {
  it('defaults to light and toggles to dark, persisting the choice', async () => {
    const { result } = renderHook(() => useTheme());

    expect(result.current.theme).toBe('light');
    expect(result.current.isDark).toBe(false);

    act(() => result.current.toggleTheme());

    expect(result.current.theme).toBe('dark');
    expect(result.current.isDark).toBe(true);
    expect(window.localStorage.getItem('theme')).toBe('dark');
  });
});

describe('useLocalStorage', () => {
  it('round-trips values through window.localStorage', () => {
    const { result } = renderHook(() => useLocalStorage('k', 'initial'));

    expect(result.current.value).toBe('initial');
    act(() => result.current.setValue('updated'));
    expect(result.current.value).toBe('updated');
    expect(JSON.parse(window.localStorage.getItem('k') as string)).toBe('updated');
  });
});

describe('useDebounce', () => {
  afterEach(() => vi.useRealTimers());

  it('delays value updates', () => {
    vi.useFakeTimers();
    const { result, rerender } = renderHook(({ value }) => useDebounce(value, 100),
      { initialProps: { value: 'initial' } });

    rerender({ value: 'updated' });
    expect(result.current).toBe('initial');

    act(() => {
      vi.advanceTimersByTime(150);
    });
    expect(result.current).toBe('updated');
  });
});
