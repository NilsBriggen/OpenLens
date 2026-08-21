/**
 * apiClient tests: endpoint catalogue, token handling, WebSocket URLs.
 */
import { describe, it, expect, beforeEach, vi } from 'vitest';
import Cookies from 'js-cookie';

import {
  apiClient,
  handleLogin,
  handleLogout,
  getAccessToken,
  isAuthenticated,
  getWebSocketUrl,
  graphEndpoints,
  aiEndpoints,
  scrapingEndpoints,
  securityEndpoints,
  threatEndpoints,
  systemEndpoints,
} from '../apiClient';

vi.mock('js-cookie', () => {
  const store: Record<string, string> = {};
  return {
    default: {
      get: vi.fn((name?: string) => (name ? store[name] : { ...store })),
      set: vi.fn((name: string, value: string) => { store[name] = value; }),
      remove: vi.fn((name: string) => { delete store[name]; }),
    },
  };
});

const cookies = Cookies as unknown as {
  get: ReturnType<typeof vi.fn>;
  set: ReturnType<typeof vi.fn>;
  remove: ReturnType<typeof vi.fn>;
};

describe('token handling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    handleLogout();
  });

  it('handleLogin stores both tokens and primes the Authorization header', () => {
    handleLogin({ access_token: 'token-a', refresh_token: 'token-r' });

    expect(cookies.set).toHaveBeenCalledWith(
      'access_token', 'token-a',
      expect.objectContaining({ secure: true, sameSite: 'strict' }));
    expect(cookies.set).toHaveBeenCalledWith(
      'refresh_token', 'token-r',
      expect.objectContaining({ secure: true, sameSite: 'strict' }));
    expect(apiClient.defaults.headers.common['Authorization']).toBe('Bearer token-a');
  });

  it('handleLogout clears tokens and the Authorization header', () => {
    handleLogin({ access_token: 'token-a', refresh_token: 'token-r' });
    handleLogout();

    expect(cookies.remove).toHaveBeenCalledWith('access_token');
    expect(cookies.remove).toHaveBeenCalledWith('refresh_token');
    expect(apiClient.defaults.headers.common['Authorization']).toBeUndefined();
  });

  it('getAccessToken and isAuthenticated reflect the stored cookie', () => {
    expect(getAccessToken()).toBeUndefined();
    expect(isAuthenticated()).toBe(false);

    handleLogin({ access_token: 'token-a' });
    expect(getAccessToken()).toBe('token-a');
    expect(isAuthenticated()).toBe(true);
  });
});

describe('endpoint catalogue', () => {
  it('exports graph endpoints', () => {
    expect(graphEndpoints.stats).toBe('/api/graph/stats');
    expect(graphEndpoints.nodes).toBe('/api/graph/nodes');
    expect(graphEndpoints.edges).toBe('/api/graph/edges');
    expect(graphEndpoints.query).toBe('/api/graph/query');
  });

  it('exports AI endpoints', () => {
    expect(aiEndpoints.anomalies.detect).toBe('/api/ai/anomalies/detect');
    expect(aiEndpoints.entities.resolve).toBe('/api/ai/entities/resolve');
    expect(aiEndpoints.predict.link).toBe('/api/ai/predict/link');
  });

  it('exports scraping endpoints', () => {
    expect(scrapingEndpoints.jobs).toBe('/api/scraping/jobs');
    expect(scrapingEndpoints.vk.user).toBe('/api/scraping/vk/user');
    expect(scrapingEndpoints.twitter.tweets).toBe('/api/scraping/twitter/tweets');
  });

  it('exports security endpoints', () => {
    expect(securityEndpoints.token).toBe('/api/security/token');
    expect(securityEndpoints.refresh).toBe('/api/security/refresh');
    expect(securityEndpoints.users).toBe('/api/security/users');
  });

  it('exports threat endpoints', () => {
    expect(threatEndpoints.feeds).toBe('/api/threat/feeds');
    expect(threatEndpoints.iocs).toBe('/api/threat/iocs');
    expect(threatEndpoints.alerts).toBe('/api/threat/alerts');
  });

  it('exports system endpoints', () => {
    expect(systemEndpoints.health).toBe('/api/system/health');
    expect(systemEndpoints.stats).toBe('/api/system/stats');
  });
});

describe('getWebSocketUrl', () => {
  beforeEach(() => handleLogout());

  it('appends the access token as a query parameter when present', () => {
    handleLogin({ access_token: 'ws-token' });
    expect(getWebSocketUrl('/ws')).toBe('ws://localhost:8000/ws?token=ws-token');
  });

  it('omits the token when signed out', () => {
    expect(getWebSocketUrl('/ws')).toBe('ws://localhost:8000/ws');
  });
});
