/**
 * apiClient
 *
 * Central axios instance, auth-token handling and endpoint catalogue for the
 * OpenLens API gateway (backend/api/main.py, FastAPI, default port 8000).
 *
 * Every endpoint below is mounted under the `/api/<module>` prefixes declared
 * in `backend/api/main.py`.
 */

import axios, {
  AxiosError,
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios';
import Cookies from 'js-cookie';

// ============================================================================
// Configuration
// ============================================================================

const env = import.meta.env;

/**
 * Base URL for REST calls. Left empty by default so requests stay relative and
 * are forwarded by the Vite dev-server proxy (see vite.config.ts), which avoids
 * cross-origin requests entirely in development.
 */
export const API_BASE_URL: string = env.REACT_APP_API_URL ?? '';

/** Base URL for WebSocket connections. */
export const WS_BASE_URL: string = env.REACT_APP_WS_URL ?? 'ws://localhost:8000';

export const ACCESS_TOKEN_COOKIE = 'access_token';
export const REFRESH_TOKEN_COOKIE = 'refresh_token';

/** Days before the access / refresh cookies expire. */
const ACCESS_TOKEN_TTL_DAYS = 1;
const REFRESH_TOKEN_TTL_DAYS = 7;

const COOKIE_OPTIONS = {
  secure: true,
  sameSite: 'strict',
} as const;

// ============================================================================
// Axios instance
// ============================================================================

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30_000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ============================================================================
// Token helpers
// ============================================================================

export interface AuthTokens {
  access_token: string;
  refresh_token?: string;
  token_type?: string;
  expires_in?: number;
  user?: Record<string, unknown>;
}

/** Returns the current access token, or undefined when signed out. */
export const getAccessToken = (): string | undefined => Cookies.get(ACCESS_TOKEN_COOKIE);

/** Returns the current refresh token, or undefined when signed out. */
export const getRefreshToken = (): string | undefined => Cookies.get(REFRESH_TOKEN_COOKIE);

/** True when an access token is present. */
export const isAuthenticated = (): boolean => !!getAccessToken();

/**
 * Persists the tokens returned by POST /api/security/token and primes the
 * default Authorization header so in-flight consumers pick it up immediately.
 */
export const handleLogin = (tokens: AuthTokens): void => {
  Cookies.set(ACCESS_TOKEN_COOKIE, tokens.access_token, {
    expires: ACCESS_TOKEN_TTL_DAYS,
    ...COOKIE_OPTIONS,
  });

  if (tokens.refresh_token) {
    Cookies.set(REFRESH_TOKEN_COOKIE, tokens.refresh_token, {
      expires: REFRESH_TOKEN_TTL_DAYS,
      ...COOKIE_OPTIONS,
    });
  }

  apiClient.defaults.headers.common['Authorization'] = `Bearer ${tokens.access_token}`;
};

/** Clears stored tokens and the default Authorization header. */
export const handleLogout = (): void => {
  Cookies.remove(ACCESS_TOKEN_COOKIE);
  Cookies.remove(REFRESH_TOKEN_COOKIE);
  delete apiClient.defaults.headers.common['Authorization'];
};

/**
 * Builds a WebSocket URL for `path`, appending the access token as a query
 * parameter because the browser WebSocket API cannot send custom headers.
 */
export const getWebSocketUrl = (path: string): string => {
  const base = WS_BASE_URL.replace(/\/$/, '');
  const suffix = path.startsWith('/') ? path : `/${path}`;
  const token = getAccessToken();

  return token ? `${base}${suffix}?token=${token}` : `${base}${suffix}`;
};

// Restore the Authorization header on a full page reload.
const existingToken = getAccessToken();
if (existingToken) {
  apiClient.defaults.headers.common['Authorization'] = `Bearer ${existingToken}`;
}

// ============================================================================
// Interceptors
// ============================================================================

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getAccessToken();
    if (token) {
      config.headers.set('Authorization', `Bearer ${token}`);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/** Marks a request that has already been retried after a token refresh. */
type RetriableConfig = AxiosRequestConfig & { _retriedAfterRefresh?: boolean };

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError) => {
    const original = error.config as RetriableConfig | undefined;
    const refreshToken = getRefreshToken();

    const canRefresh =
      error.response?.status === 401 &&
      !!original &&
      !original._retriedAfterRefresh &&
      !!refreshToken &&
      // Never try to refresh the refresh call itself.
      !original.url?.includes(securityEndpoints.refresh);

    if (!canRefresh) {
      return Promise.reject(error);
    }

    original._retriedAfterRefresh = true;

    try {
      // Bare axios call so this response interceptor cannot recurse.
      const { data } = await axios.post<AuthTokens>(
        `${API_BASE_URL}${securityEndpoints.refresh}`,
        { refresh_token: refreshToken },
        { headers: { 'Content-Type': 'application/json' } }
      );

      handleLogin(data);
      return apiClient(original as AxiosRequestConfig);
    } catch (refreshError) {
      handleLogout();
      return Promise.reject(refreshError);
    }
  }
);

// ============================================================================
// Endpoints - mirror backend/api/routers/*
// ============================================================================

export const graphEndpoints = {
  stats: '/api/graph/stats',
  nodes: '/api/graph/nodes',
  edges: '/api/graph/edges',
  relationships: '/api/graph/relationships',
  query: '/api/graph/query',
  centrality: '/api/graph/centrality',
  communities: '/api/graph/communities',
  path: '/api/graph/path',
  visualization: {
    matplotlib: '/api/graph/visualization/matplotlib',
    pyvis: '/api/graph/visualization/pyvis',
    plotly: '/api/graph/visualization/plotly',
  },
  temporal: {
    patterns: '/api/graph/temporal/patterns',
    evolution: '/api/graph/temporal/evolution',
  },
} as const;

export const aiEndpoints = {
  chat: '/api/ai/chat',
  anomalies: {
    detect: '/api/ai/anomalies/detect',
    scores: '/api/ai/anomalies/scores',
  },
  entities: {
    resolve: '/api/ai/entities/resolve',
    deduplicate: '/api/ai/entities/deduplicate',
  },
  predict: {
    link: '/api/ai/predict/link',
    node: '/api/ai/predict/node',
    graphEvolution: '/api/ai/predict/graph-evolution',
    threats: '/api/ai/predict/threats',
  },
} as const;

export const scrapingEndpoints = {
  jobs: '/api/scraping/jobs',
  scrape: '/api/scraping/scrape',
  proxies: '/api/scraping/proxies',
  userAgents: '/api/scraping/user-agents/list',
  cacheStats: '/api/scraping/cache/stats',
  vk: {
    user: '/api/scraping/vk/user',
    posts: '/api/scraping/vk/posts',
    search: '/api/scraping/vk/search',
  },
  twitter: {
    tweets: '/api/scraping/twitter/tweets',
    user: '/api/scraping/twitter/user',
    trends: '/api/scraping/twitter/trends',
  },
  instagram: {
    user: '/api/scraping/instagram/user',
    posts: '/api/scraping/instagram/posts',
    hashtag: '/api/scraping/instagram/hashtag',
  },
} as const;

export const securityEndpoints = {
  token: '/api/security/token',
  refresh: '/api/security/refresh',
  logout: '/api/security/logout',
  users: '/api/security/users',
  roles: '/api/security/roles',
  permissions: '/api/security/permissions',
  audit: '/api/security/audit',
  encrypt: '/api/security/encrypt',
  decrypt: '/api/security/decrypt',
} as const;

export const threatEndpoints = {
  feeds: '/api/threat/feeds',
  iocs: '/api/threat/iocs',
  alerts: '/api/threat/alerts',
  rules: '/api/threat/rules',
  enrichment: '/api/threat/enrichment',
  correlation: '/api/threat/correlation',
  hunt: '/api/threat/hunt',
  scoring: '/api/threat/threats/scoring',
  stix: '/api/threat/sharing/import/stix',
  stixExport: '/api/threat/sharing/export/stix',
  monitoring: {
    health: '/api/threat/monitoring/health',
    stats: '/api/threat/monitoring/stats',
  },
} as const;

export const systemEndpoints = {
  health: '/api/system/health',
  version: '/api/system/version',
  stats: '/api/system/stats',
  config: '/api/system/config',
  logs: '/api/system/logs',
} as const;

export const wsEndpoints = {
  root: '/api/ws',
  notifications: '/api/ws/notifications',
  graph: '/api/ws/graph',
} as const;

export default apiClient;
