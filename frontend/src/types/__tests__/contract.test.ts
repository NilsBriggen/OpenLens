/**
 * Live contract tests: assert the running backend's wire shapes match the
 * frontend's domain models field-for-field.
 *
 * These hit a real backend (default http://localhost:8000) and are skipped
 * unless CONTRACT=1 - run them with `npm run test:contract`. Hand-written MSW
 * fixtures cannot catch drift; only the live wire can.
 */
import { describe, it, expect, beforeAll } from 'vitest';

const BASE = process.env.CONTRACT_BASE_URL || 'http://localhost:8000';
const ENABLED = process.env.CONTRACT === '1';

const d = describe.skipIf(!ENABLED);

let token = '';

const get = async (path: string) => {
  const response = await fetch(`${BASE}${path}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  return { status: response.status, body: await response.json() };
};

/** Every listed key must exist on the object; no extras beyond `alsoAllowed`. */
const expectShape = (obj: Record<string, unknown>, required: string[],
                     alsoAllowed: string[] = []) => {
  for (const key of required) {
    expect(obj, `missing key ${key}`).toHaveProperty(key);
  }
  const allowed = new Set([...required, ...alsoAllowed]);
  for (const key of Object.keys(obj)) {
    expect(allowed.has(key), `unexpected key ${key} - contract drift`).toBe(true);
  }
};

d('API contract (live backend)', () => {
  beforeAll(async () => {
    const response = await fetch(`${BASE}/api/security/token`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: 'username=admin&password=admin123&grant_type=password',
    });
    expect(response.status).toBe(200);
    token = (await response.json()).access_token;
  });

  it('GET /api/threat/iocs matches the IOC model', async () => {
    const { status, body } = await get('/api/threat/iocs?limit=5');
    expect(status).toBe(200);
    expect(Array.isArray(body)).toBe(true);
    if (body.length) {
      expectShape(body[0], [
        'id', 'value', 'iocType', 'threatType', 'confidence', 'severity',
        'description', 'source', 'tags', 'firstSeen', 'lastSeen',
        'expiresAt', 'relatedThreats',
      ]);
    }
  });

  it('GET /api/threat/feeds matches the ThreatFeed model', async () => {
    const { status, body } = await get('/api/threat/feeds');
    expect(status).toBe(200);
    if (body.length) {
      expectShape(body[0], [
        'id', 'name', 'feedType', 'enabled', 'status', 'iocCount',
        'frequency', 'lastUpdated', 'description', 'url',
      ]);
    }
  });

  it('GET /api/threat/alerts matches the Alert model', async () => {
    const { status, body } = await get('/api/threat/alerts');
    expect(status).toBe(200);
    if (body.length) {
      expectShape(body[0], [
        'id', 'title', 'description', 'severity', 'status', 'iocCount',
        'indicator', 'indicatorType', 'threatTypes', 'confidence',
        'createdAt', 'updatedAt',
      ]);
    }
  });

  it('GET /api/graph/stats matches the GraphStats model', async () => {
    const { status, body } = await get('/api/graph/stats');
    expect(status).toBe(200);
    expectShape(body, ['connected', 'nodeCount', 'edgeCount',
                       'queriesExecuted', 'avgQueryTime', 'cacheSize']);
  });

  it('GET /api/graph/nodes matches the GraphNode model', async () => {
    const { status, body } = await get('/api/graph/nodes?limit=3');
    expect(status).toBe(200);
    if (body.length) {
      expectShape(body[0], ['id', 'label', 'type', 'labels', 'properties']);
    }
  });

  it('GET /api/security/users matches the User model and never leaks hashes', async () => {
    const { status, body } = await get('/api/security/users');
    expect(status).toBe(200);
    expect(body.length).toBeGreaterThan(0);
    expectShape(body[0], ['id', 'username', 'email', 'roles', 'isActive',
                          'lastLogin', 'createdAt']);
    expect(JSON.stringify(body)).not.toContain('password');
  });

  it('every frontend endpoint resolves (never 404/405)', async () => {
    const paths = [
      '/api/graph/nodes', '/api/graph/edges', '/api/graph/stats',
      '/api/scraping/jobs', '/api/scraping/proxies', '/api/scraping/user-agents/list',
      '/api/security/users', '/api/security/roles', '/api/security/permissions',
      '/api/security/audit', '/api/threat/feeds', '/api/threat/iocs',
      '/api/threat/alerts', '/api/threat/rules', '/api/threat/monitoring/health',
      '/api/threat/monitoring/stats', '/api/system/health', '/api/system/stats',
      '/api/system/config', '/api/system/logs',
    ];
    for (const path of paths) {
      const { status } = await get(path);
      expect([200, 503], `${path} -> ${status}`).toContain(status);
    }
  });

  it('unavailable features return the ApiError shape, not empty results', async () => {
    const response = await fetch(`${BASE}/api/scraping/twitter/trends`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (response.status === 503) {
      const body = await response.json();
      expectShape(body, ['error', 'message', 'feature', 'requires', 'detail']);
      expect(body.error).toBe('feature_unavailable');
    }
  });
});
