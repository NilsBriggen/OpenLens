"""
apiClient Tests

Unit tests for the API client configuration.
"""

import { apiClient, handleLogin, handleLogout, getAccessToken, isAuthenticated } from '../apiClient';
import Cookies from 'js-cookie';

// Mock js-cookie
jest.mock('js-cookie');

// Mock axios
jest.mock('axios');

describe('apiClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('handleLogin', () => {
    it('should set access and refresh tokens in cookies', () => {
      const tokens = {
        access_token: 'test-access-token',
        refresh_token: 'test-refresh-token',
        expires_in: 3600,
      };

      handleLogin(tokens);

      expect(Cookies.set).toHaveBeenCalledWith('access_token', 'test-access-token', {
        expires: 1,
        secure: true,
        sameSite: 'strict',
      });

      expect(Cookies.set).toHaveBeenCalledWith('refresh_token', 'test-refresh-token', {
        expires: 7,
        secure: true,
        sameSite: 'strict',
      });
    });

    it('should set Authorization header on apiClient', () => {
      const tokens = {
        access_token: 'test-access-token',
        refresh_token: 'test-refresh-token',
      };

      handleLogin(tokens);

      expect(apiClient.defaults.headers.common['Authorization']).toBe('Bearer test-access-token');
    });
  });

  describe('handleLogout', () => {
    it('should remove access and refresh tokens from cookies', () => {
      handleLogout();

      expect(Cookies.remove).toHaveBeenCalledWith('access_token');
      expect(Cookies.remove).toHaveBeenCalledWith('refresh_token');
    });

    it('should remove Authorization header from apiClient', () => {
      apiClient.defaults.headers.common['Authorization'] = 'Bearer test-token';
      handleLogout();

      expect(apiClient.defaults.headers.common['Authorization']).toBeUndefined();
    });
  });

  describe('getAccessToken', () => {
    it('should return the access token from cookies', () => {
      (Cookies.get as jest.Mock).mockReturnValue('test-access-token');

      const token = getAccessToken();

      expect(token).toBe('test-access-token');
      expect(Cookies.get).toHaveBeenCalledWith('access_token');
    });

    it('should return undefined if no token exists', () => {
      (Cookies.get as jest.Mock).mockReturnValue(undefined);

      const token = getAccessToken();

      expect(token).toBeUndefined();
    });
  });

  describe('isAuthenticated', () => {
    it('should return true if access token exists', () => {
      (Cookies.get as jest.Mock).mockReturnValue('test-access-token');

      const authenticated = isAuthenticated();

      expect(authenticated).toBe(true);
    });

    it('should return false if no access token exists', () => {
      (Cookies.get as jest.Mock).mockReturnValue(undefined);

      const authenticated = isAuthenticated();

      expect(authenticated).toBe(false);
    });
  });
});

describe('API Endpoints', () => {
  it('should export graph endpoints', () => {
    const { graphEndpoints } = require('../apiClient');

    expect(graphEndpoints.stats).toBe('/api/graph/stats');
    expect(graphEndpoints.nodes).toBe('/api/graph/nodes');
    expect(graphEndpoints.edges).toBe('/api/graph/edges');
    expect(graphEndpoints.query).toBe('/api/graph/query');
  });

  it('should export AI endpoints', () => {
    const { aiEndpoints } = require('../apiClient');

    expect(aiEndpoints.anomalies.detect).toBe('/api/ai/anomalies/detect');
    expect(aiEndpoints.entities.resolve).toBe('/api/ai/entities/resolve');
    expect(aiEndpoints.predict.link).toBe('/api/ai/predict/link');
  });

  it('should export scraping endpoints', () => {
    const { scrapingEndpoints } = require('../apiClient');

    expect(scrapingEndpoints.jobs).toBe('/api/scraping/jobs');
    expect(scrapingEndpoints.vk.user).toBe('/api/scraping/vk/user');
    expect(scrapingEndpoints.twitter.tweets).toBe('/api/scraping/twitter/tweets');
  });

  it('should export security endpoints', () => {
    const { securityEndpoints } = require('../apiClient');

    expect(securityEndpoints.token).toBe('/api/security/token');
    expect(securityEndpoints.refresh).toBe('/api/security/refresh');
    expect(securityEndpoints.users).toBe('/api/security/users');
  });

  it('should export threat endpoints', () => {
    const { threatEndpoints } = require('../apiClient');

    expect(threatEndpoints.feeds).toBe('/api/threat/feeds');
    expect(threatEndpoints.iocs).toBe('/api/threat/iocs');
    expect(threatEndpoints.alerts).toBe('/api/threat/alerts');
  });

  it('should export system endpoints', () => {
    const { systemEndpoints } = require('../apiClient');

    expect(systemEndpoints.health).toBe('/api/system/health');
    expect(systemEndpoints.stats).toBe('/api/system/stats');
  });
});

describe('getWebSocketUrl', () => {
  it('should return WebSocket URL with token', () => {
    (Cookies.get as jest.Mock).mockReturnValue('test-token');

    const url = require('../apiClient').getWebSocketUrl('/ws');

    expect(url).toBe('ws://localhost:8000/ws?token=test-token');
  });

  it('should return WebSocket URL without token if not authenticated', () => {
    (Cookies.get as jest.Mock).mockReturnValue(undefined);

    const url = require('../apiClient').getWebSocketUrl('/ws');

    expect(url).toBe('ws://localhost:8000/ws');
  });
});
