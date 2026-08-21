/**
 * Frontend-facing API domain models.
 *
 * These match the backend's camelCase response models (Pydantic ApiModel).
 * Hand-written for now; once the OpenAPI schema carries full response shapes
 * these can be generated (see the plan's codegen note).
 */

export interface IOC {
  id: string;
  value: string;
  iocType: string;
  threatType: string;
  confidence: number;
  severity: string;
  description: string;
  source: string;
  tags: string[];
  firstSeen: string | null;
  lastSeen: string | null;
  expiresAt: string | null;
  relatedThreats: string[];
}

export interface ThreatFeed {
  id: string;
  name: string;
  feedType: string;
  enabled: boolean;
  status: string;
  iocCount: number;
  frequency: number;
  lastUpdated: string | null;
  description: string;
  url: string;
}

export interface Alert {
  id: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  iocCount: number;
  indicator: string;
  indicatorType: string;
  threatTypes: string[];
  confidence: number;
  createdAt: string | null;
  updatedAt: string | null;
}

export interface AlertRule {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  condition: Record<string, unknown>;
}

export interface GraphNode {
  id: string;
  label: string;
  type: string;
  labels: string[];
  properties: Record<string, unknown>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  properties: Record<string, unknown>;
}

export interface GraphStats {
  connected: boolean;
  nodeCount: number;
  edgeCount: number;
  queriesExecuted: number;
  avgQueryTime: number;
  cacheSize: number;
}

export interface User {
  id: string;
  username: string;
  email: string;
  roles: string[];
  isActive: boolean;
  lastLogin: string | null;
  createdAt: string | null;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
}

export interface Permission {
  id: string;
  name: string;
  description: string;
  resource: string;
  action: string;
}

export interface AuditEvent {
  id: string;
  eventType: string;
  severity: string;
  userId: string;
  username: string;
  resource: string;
  action: string;
  details: Record<string, unknown>;
  timestamp: string | null;
}

export interface ScrapeJob {
  id: string;
  name: string;
  status: string;
  progress: number;
  successCount: number;
  failedCount: number;
  createdAt: string | null;
  // Optional details the backend does not yet expose; the job drawer shows
  // them only when present.
  jobType?: string;
  depth?: number;
  urls?: string[];
  useProxy?: boolean;
  useCache?: boolean;
  renderJs?: boolean;
  duration?: number;
}

export interface Proxy {
  id: string;
  host: string;
  port: number;
  protocol: string;
  location: string;
  status: string;
  speed: number;
  successRate: number;
}

export interface SystemStats {
  modules: Record<string, number>;
  totalModules: number;
  features: Record<string, boolean>;
}

export interface SystemConfig {
  version: string;
  authRequired: boolean;
  capabilities: Record<string, boolean>;
  corsOrigins: string[];
  features: Record<string, boolean>;
}

/** FastAPI's error envelope, surfaced through axios. */
export interface ApiErrorBody {
  error?: string;
  message?: string;
  detail?: unknown;
  requires?: string[];
}
