# OpenLens Documentation

## 📚 Table of Contents

1. [Overview](#-overview)
2. [Architecture](#-architecture)
3. [Installation](#-installation)
4. [Configuration](#-configuration)
5. [API Reference](#-api-reference)
6. [Frontend Components](#-frontend-components)
7. [Backend Services](#-backend-services)
8. [Authentication](#-authentication)
9. [WebSocket Integration](#-websocket-integration)
10. [Testing](#-testing)
11. [Deployment](#-deployment)
12. [Troubleshooting](#-troubleshooting)

---

## 📖 Overview

OpenLens is an **Enterprise-Grade OSINT (Open Source Intelligence) Platform** designed to compete with solutions like Palantir Gotham. It provides comprehensive tools for:

- **Graph Analytics**: Visualize and analyze relationships in your data
- **AI/ML Insights**: Detect anomalies, resolve entities, make predictions
- **Distributed Scraping**: Collect data from multiple sources
- **Enterprise Security**: Role-based access control, audit logging
- **Real-Time Threat Intelligence**: IOC management, threat feeds, alerts

### Key Features

| Feature | Description |
|---------|-------------|
| Graph Visualization | Interactive graph exploration with Cytoscape.js |
| AI Assistant | Natural language queries with context-aware responses |
| Real-time Updates | WebSocket integration for live data |
| Authentication | JWT-based with automatic token refresh |
| Code Splitting | Optimized bundle sizes with lazy loading |
| Export | CSV, JSON, STIX, PDF export capabilities |

---

## 🏗️ Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         OpenLens Platform                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │   Frontend      │    │    Backend       │    │   Database   │  │
│  │   (React/TS)    │◄──►│   (FastAPI)      │◄──►│   (PostgreSQL│  │
│  └─────────────────┘    └─────────────────┘    │    Neo4j)    │  │
│          ▲                  ▲  ▲  ▲  ▲              └─────────────┘  │
│          │                  │  │  │  │                                  │
│          │                  │  │  └── Scraping Workers (Celery)       │
│          │                  │  │      └── VK, Twitter, Instagram      │
│          │                  │  └── AI/ML Services                     │
│          │                  │      └── Anomaly Detection              │
│          │                  │      └── Entity Resolution              │
│          │                  │      └── Predictive Analytics           │
│          │                  └── Threat Intelligence                  │
│          │                          └── STIX/TAXII Feeds                 │
│          │                          └── IOC Enrichment                     │
│          └──────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Frontend Architecture

```
frontend/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── common/           # Common components (ProtectedRoute, LoadingSpinner, etc.)
│   │   ├── GraphVisualization.tsx
│   │   ├── ConnectedGraphVisualization.tsx
│   │   ├── AIChatAssistant.tsx
│   │   ├── NotificationCenter.tsx
│   │   └── ...
│   ├── contexts/             # React contexts
│   │   └── WebSocketContext.tsx
│   ├── hooks/                # Custom React hooks
│   │   └── useApi.ts          # API hooks with Axios
│   ├── layouts/              # Page layouts
│   │   └── MainLayout.tsx
│   ├── lib/                  # Library utilities
│   │   └── apiClient.ts      # Axios configuration
│   ├── pages/                # Page components
│   │   ├── Dashboard.tsx
│   │   ├── GraphExplorer.tsx
│   │   ├── AIAnalytics.tsx
│   │   ├── ScrapingHub.tsx
│   │   ├── SecurityCenter.tsx
│   │   ├── ThreatIntelligence.tsx
│   │   ├── Settings.tsx
│   │   ├── Login.tsx
│   │   └── Register.tsx
│   ├── providers/            # React Query providers
│   │   └── AppProvider.tsx
│   ├── utils/                # Utility functions
│   │   ├── exportUtils.ts     # Export functions (CSV, JSON, STIX, etc.)
│   │   └── uiUtils.ts        # UI utility functions
│   ├── App.tsx
│   ├── index.tsx
│   └── index.css
├── public/                   # Static assets
├── .env.development
├── .env.production
├── .env.staging
├── vite.config.ts
├── package.json
└── README.md
```

### Backend Architecture

```
backend/
├── api/                      # FastAPI REST API
│   ├── main.py               # FastAPI app entry point
│   ├── routers/              # API routers
│   │   ├── graph_router.py    # Graph analytics endpoints
│   │   ├── ai_router.py      # AI/ML endpoints
│   │   ├── scraping_router.py # Scraping endpoints
│   │   ├── security_router.py # Security endpoints
│   │   ├── threat_router.py  # Threat intelligence endpoints
│   │   ├── system_router.py  # System endpoints
│   │   └── websocket_router.py # WebSocket endpoints
│   └── __init__.py
├── app.py                    # Flask app (legacy)
├── auth/                     # Authentication module
│   ├── authentication.py     # JWT authentication
│   ├── models.py            # User models
│   └── __init__.py
├── graph/                    # Graph analytics module
│   ├── graph_engine.py       # Graph database operations
│   ├── network_analyzer.py   # Network analysis algorithms
│   ├── path_finder.py        # Path finding algorithms
│   ├── community_detector.py # Community detection
│   ├── graph_visualizer.py   # Graph visualization
│   └── temporal_analyzer.py  # Temporal analysis
├── ai/                       # AI/ML module
│   ├── anomaly_detector.py   # Anomaly detection
│   ├── entity_resolver.py    # Entity resolution
│   └── predictive_analyzer.py # Predictive analytics
├── scraping/                 # Scraping module
│   ├── scrapers/             # Platform scrapers
│   │   ├── vk_scraper.py
│   │   ├── twitter_scraper.py
│   │   └── instagram_scraper.py
│   └── ...
├── threat_intelligence/      # Threat intelligence module
│   ├── feeds.py              # Threat feed management
│   ├── ioc_manager.py        # IOC management
│   └── alert_system.py       # Alert system
├── database/                 # Database module
│   ├── postgres_db.py        # PostgreSQL operations
│   └── neo4j_db.py           # Neo4j operations
├── websocket/                # WebSocket module
│   ├── socket_server.py      # Socket.IO server
│   └── event_handlers.py     # Event handlers
├── tasks/                    # Celery tasks
│   ├── celery_app.py         # Celery configuration
│   └── scraping_tasks.py     # Scraping tasks
└── ...
```

---

## 🚀 Installation

### Prerequisites

#### Frontend
- Node.js >= 16.0.0
- npm >= 8.0.0

#### Backend
- Python >= 3.9
- pip >= 21.0
- PostgreSQL >= 13
- Neo4j >= 4.4
- Redis >= 6.0

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd OpenLens/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Copy environment file:
```bash
cp .env.development .env
```

4. Edit `.env` to configure API URLs:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

5. Start development server:
```bash
npm start
# or for faster development with Vite
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend Setup

1. Navigate to the backend directory:
```bash
cd OpenLens/backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
```

4. Initialize databases:
```bash
# PostgreSQL
createdb openlens

# Neo4j
# Access Neo4j browser at http://localhost:7474
# Default credentials: neo4j/neo4j
```

5. Start the FastAPI server:
```bash
cd api
uvicorn main:app --reload
```

The backend will be available at `http://localhost:8000`

6. (Optional) Start the Flask server (legacy):
```bash
python app.py
```

---

## ⚙️ Configuration

### Environment Variables

#### Frontend (.env)

```env
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000

# App Configuration
REACT_APP_ENV=development
REACT_APP_VERSION=7.0.0
REACT_APP_NAME=OpenLens

# Feature Flags
REACT_APP_ENABLE_ANALYTICS=true
REACT_APP_ENABLE_AI=true
REACT_APP_ENABLE_WEBSOCKET=true
REACT_APP_ENABLE_SCRAPING=true
REACT_APP_ENABLE_THREAT_INTEL=true

# Debug
REACT_APP_DEBUG=true
```

#### Backend (.env)

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# FastAPI
FASTAPI_HOST=0.0.0.0
FASTAPI_PORT=8000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=openlens
POSTGRES_PASSWORD=openlens
POSTGRES_DB=openlens

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
JWT_REFRESH_EXPIRE_DAYS=7

# WebSocket
SOCKETIO_ASYNC_MODE=eventlet
SOCKETIO_CORS_ORIGINS=*
```

---

## 🔌 API Reference

### Base URL
```
http://localhost:8000/api
```

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/security/token` | POST | Get JWT token |
| `/security/refresh` | POST | Refresh access token |
| `/security/logout` | POST | Logout and invalidate token |
| `/security/users` | GET | List all users |
| `/security/users` | POST | Create a new user |
| `/security/users/{id}` | GET | Get user details |
| `/security/users/{id}` | PUT | Update user |
| `/security/roles` | GET | List all roles |
| `/security/roles` | POST | Create a new role |
| `/security/permissions` | GET | List all permissions |
| `/security/permissions` | POST | Create a new permission |
| `/security/audit` | GET | Get audit logs |
| `/security/audit` | POST | Log an audit event |

### Graph Analytics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/graph/stats` | GET | Get graph statistics |
| `/graph/nodes` | GET | List all nodes |
| `/graph/nodes` | POST | Create a new node |
| `/graph/nodes/{id}` | GET | Get node by ID |
| `/graph/edges` | GET | List all edges |
| `/graph/edges` | POST | Create a new edge |
| `/graph/query` | POST | Execute Cypher query |
| `/graph/centrality` | POST | Calculate centrality metrics |
| `/graph/communities` | POST | Detect communities |
| `/graph/path` | POST | Find path between nodes |
| `/graph/visualization/matplotlib` | GET | Generate Matplotlib visualization |
| `/graph/visualization/pyvis` | GET | Generate PyVis HTML |
| `/graph/visualization/plotly` | GET | Generate Plotly 3D visualization |
| `/graph/temporal/patterns` | GET | Detect temporal patterns |
| `/graph/temporal/evolution` | GET | Analyze graph evolution |

### AI/ML

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ai/chat` | POST | Chat with AI Assistant |
| `/ai/anomalies/detect` | POST | Detect anomalies |
| `/ai/anomalies/scores` | GET | Get anomaly scores |
| `/ai/entities/resolve` | POST | Resolve entity matches |
| `/ai/entities/deduplicate` | POST | Deduplicate entities |
| `/ai/predict/link` | POST | Predict link between nodes |
| `/ai/predict/node` | POST | Predict node classification |
| `/ai/predict/graph-evolution` | GET | Predict graph evolution |
| `/ai/predict/threats` | GET | Predict potential threats |

### Scraping

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/scraping/jobs` | GET | List all scrape jobs |
| `/scraping/jobs` | POST | Create a new scrape job |
| `/scraping/scrape` | POST | Start a scrape |
| `/scraping/vk/user` | POST | Scrape VK user |
| `/scraping/vk/posts` | POST | Scrape VK posts |
| `/scraping/vk/search` | POST | Search VK users |
| `/scraping/twitter/tweets` | POST | Scrape Twitter tweets |
| `/scraping/twitter/user` | POST | Scrape Twitter user |
| `/scraping/twitter/trends` | POST | Get Twitter trends |
| `/scraping/instagram/user` | POST | Scrape Instagram user |
| `/scraping/instagram/posts` | POST | Scrape Instagram posts |
| `/scraping/instagram/hashtag` | POST | Scrape Instagram hashtag |

### Threat Intelligence

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/threat/feeds` | GET | List all threat feeds |
| `/threat/feeds` | POST | Add a new threat feed |
| `/threat/feeds/{id}` | GET | Get feed details |
| `/threat/iocs` | GET | List all IOCs |
| `/threat/iocs` | POST | Add a new IOC |
| `/threat/iocs/{id}` | GET | Get IOC details |
| `/threat/alerts` | GET | List all alerts |
| `/threat/alerts` | POST | Create a new alert |
| `/threat/rules` | GET | List all threat rules |
| `/threat/rules` | POST | Add a new threat rule |
| `/threat/enrichment` | POST | Enrich an IOC |
| `/threat/correlation` | POST | Correlate IOCs |
| `/threat/stix` | POST | Import/export STIX |

### System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/system/health` | GET | Full system health check |
| `/system/version` | GET | API version information |
| `/system/stats` | GET | System statistics |
| `/system/config` | GET | System configuration |
| `/system/logs` | GET | System logs |
| `/system/backup` | POST | Create backup |

### WebSocket

| Endpoint | Description |
|----------|-------------|
| `/ws` | Main WebSocket endpoint |
| `/ws/notifications` | Notifications WebSocket |
| `/ws/graph` | Graph updates WebSocket |
| `/ws/scraping` | Scraping updates WebSocket |
| `/ws/threat` | Threat updates WebSocket |

---

## 🎨 Frontend Components

### Core Components

#### AIChatAssistant
Natural language query interface with context-aware suggestions.

**Props:**
```typescript
interface AIChatAssistantProps {
  visible: boolean;
  onClose: () => void;
  context?: string; // Current page/context for AI to understand
}
```

**Features:**
- Natural language processing
- Context-aware responses
- Command parsing (anomaly detection, entity resolution, etc.)
- Conversation history
- Markdown support
- Code syntax highlighting

**Usage:**
```typescript
<AIChatAssistant
  visible={visible}
  onClose={() => setVisible(false)}
  context="graph"
/>
```

#### NotificationCenter
Real-time notification system with filtering and categorization.

**Props:**
```typescript
interface NotificationCenterProps {
  visible: boolean;
  onClose: () => void;
}
```

**Features:**
- Real-time notifications via WebSocket
- Filter by type, severity, status
- Mark as read/unread
- Notification history

#### GraphVisualization
Interactive graph visualization with Cytoscape.js.

**Props:**
```typescript
interface GraphVisualizationProps {
  data: GraphData;
  height?: number | string;
  layout?: string;
  onNodeClick?: (node: NodeData) => void;
  onEdgeClick?: (edge: EdgeData) => void;
  onReady?: (cy: any) => void;
  style?: React.CSSProperties;
}

interface GraphData {
  nodes: NodeData[];
  edges: EdgeData[];
}

interface NodeData {
  id: string;
  label: string;
  type?: string;
  properties?: Record<string, any>;
}

interface EdgeData {
  id: string;
  source: string;
  target: string;
  label?: string;
  type?: string;
  properties?: Record<string, any>;
}
```

**Features:**
- Multiple layout algorithms (CoSE, Circle, Grid, Dagre, etc.)
- Node/edge styling based on type
- Zoom and pan controls
- Fullscreen mode
- Node/edge selection

#### ConnectedGraphVisualization
Graph visualization connected to backend API.

**Props:**
```typescript
interface ConnectedGraphVisualizationProps {
  height?: number | string;
  layout?: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
  showControls?: boolean;
  showStats?: boolean;
  onNodeClick?: (node: NodeData) => void;
  onEdgeClick?: (edge: EdgeData) => void;
  style?: React.CSSProperties;
}
```

**Features:**
- Fetches data from `/api/graph/nodes` and `/api/graph/edges`
- Real-time updates via WebSocket
- Search and filtering
- Centrality and community analysis
- Path finding
- Export functionality

#### ProtectedRoute
Route protection with authentication check.

**Props:**
```typescript
interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string; // Default: /login
  requireAuth?: boolean; // Default: true
}
```

**Features:**
- Redirects to login if not authenticated
- Can be configured to require or not require auth
- Preserves redirect location

**Usage:**
```typescript
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>
```

### UI Components

#### LoadingSpinner
Multiple spinner variants with animations.

**Props:**
```typescript
interface LoadingSpinnerProps {
  size?: 'small' | 'default' | 'large';
  type?: 'spin' | 'dots' | 'wave' | 'ring' | 'grid' | 'bar';
  fullScreen?: boolean;
  tip?: string;
  color?: string;
}
```

#### ErrorBoundary
Error handling with fallback UI.

**Props:**
```typescript
interface ErrorBoundaryProps {
  fallback?: React.ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  children: React.ReactNode;
}
```

#### ToastNotification
Rich notification system with positioning.

**Props:**
```typescript
interface ToastNotificationProps {
  message: string;
  type?: 'success' | 'error' | 'warning' | 'info';
  duration?: number;
  position?: 'topLeft' | 'topRight' | 'bottomLeft' | 'bottomRight' | 'topCenter' | 'bottomCenter';
  icon?: React.ReactNode;
  onClose?: () => void;
}
```

#### ContextMenu
Right-click and button-triggered menus.

**Props:**
```typescript
interface ContextMenuProps {
  items: MenuItem[];
  children: React.ReactNode;
  onClick?: (key: string) => void;
  trigger?: 'click' | 'contextMenu' | 'hover';
}

interface MenuItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  disabled?: boolean;
  danger?: boolean;
  children?: MenuItem[];
}
```

#### StatusBadge
Multiple badge variants.

**Props:**
```typescript
interface StatusBadgeProps {
  status: string;
  type?: 'status' | 'count' | 'pill' | 'dot' | 'icon';
  size?: 'small' | 'default' | 'large';
  color?: string;
  text?: string;
}
```

#### ProgressBar
Various progress indicators.

**Props:**
```typescript
interface ProgressBarProps {
  percent: number;
  type?: 'line' | 'circle' | 'ring' | 'dashboard' | 'steps';
  size?: 'small' | 'default' | 'large';
  status?: 'normal' | 'active' | 'success' | 'exception';
  strokeColor?: string;
  trailColor?: string;
  showInfo?: boolean;
  format?: (percent: number) => string;
}
```

#### SkeletonLoader
Loading placeholders with shimmer effects.

**Props:**
```typescript
interface SkeletonLoaderProps {
  type?: 'text' | 'avatar' | 'paragraph' | 'title' | 'button' | 'input' | 'image' | 'card' | 'list' | 'table';
  active?: boolean;
  size?: 'small' | 'default' | 'large';
  shape?: 'circle' | 'square' | 'round' | 'default';
  rows?: number;
  width?: number | string;
  height?: number | string;
}
```

#### CopyToClipboard
Clipboard functionality with feedback.

**Props:**
```typescript
interface CopyToClipboardProps {
  text: string;
  children?: React.ReactNode;
  onCopy?: () => void;
  tooltip?: string;
  icon?: React.ReactNode;
}
```

#### TimeAgo
Relative time display with auto-update.

**Props:**
```typescript
interface TimeAgoProps {
  date: Date | string | number;
  interval?: number; // Update interval in seconds
  formatter?: (value: number, unit: string, suffix: string) => string;
  locale?: string;
}
```

#### EmptyState
Empty state placeholders.

**Props:**
```typescript
interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  image?: string;
  actions?: React.ReactNode;
}
```

#### AvatarGroup
Stacked/horizontal avatar displays.

**Props:**
```typescript
interface AvatarGroupProps {
  avatars: AvatarItem[];
  maxCount?: number;
  size?: 'small' | 'default' | 'large';
  shape?: 'circle' | 'square';
  stack?: boolean;
  tooltip?: boolean;
}

interface AvatarItem {
  src?: string;
  alt?: string;
  icon?: React.ReactNode;
  color?: string;
  style?: React.CSSProperties;
}
```

#### TagInput
Tag management with add/remove/edit.

**Props:**
```typescript
interface TagInputProps {
  value: string[];
  onChange: (value: string[]) => void;
  placeholder?: string;
  separator?: string | string[];
  allowDuplicates?: boolean;
  maxTags?: number;
  readOnly?: boolean;
  disabled?: boolean;
  size?: 'small' | 'default' | 'large';
}
```

#### ColorPicker
Multiple color picker variants.

**Props:**
```typescript
interface ColorPickerProps {
  value?: string;
  onChange?: (color: string) => void;
  type?: 'sketch' | 'chrome' | 'photos' | 'compact' | 'material' | 'twitter' | 'github' | 'block' | 'swatches';
  size?: 'small' | 'default' | 'large';
  presetColors?: string[];
  disabled?: boolean;
  showText?: boolean;
}
```

#### Rating
Star, emoji, and like/dislike ratings.

**Props:**
```typescript
interface RatingProps {
  value: number;
  onChange?: (value: number) => void;
  type?: 'star' | 'emoji' | 'like' | 'heart' | 'fire';
  count?: number;
  size?: 'small' | 'default' | 'large';
  color?: string;
  activeColor?: string;
  inactiveColor?: string;
  allowHalf?: boolean;
  disabled?: boolean;
  tooltip?: boolean;
}
```

#### ToggleSwitch
Customizable toggle components.

**Props:**
```typescript
interface ToggleSwitchProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  size?: 'small' | 'default' | 'large';
  disabled?: boolean;
  loading?: boolean;
  label?: string;
  checkedLabel?: string;
  uncheckedLabel?: string;
  checkedColor?: string;
  uncheckedColor?: string;
}
```

#### Badge
Enhanced badge components.

**Props:**
```typescript
interface BadgeProps {
  count?: number | string;
  max?: number;
  dot?: boolean;
  overflowCount?: number;
  color?: string;
  backgroundColor?: string;
  text?: string;
  size?: 'small' | 'default' | 'large';
  style?: React.CSSProperties;
  children?: React.ReactNode;
}
```

#### Card
Enhanced card components.

**Props:**
```typescript
interface CardProps {
  title?: string;
  extra?: React.ReactNode;
  children: React.ReactNode;
  type?: 'default' | 'stat' | 'profile' | 'feature' | 'bordered';
  size?: 'small' | 'default' | 'large';
  hoverable?: boolean;
  loading?: boolean;
  cover?: React.ReactNode;
  actions?: React.ReactNode[];
  style?: React.CSSProperties;
  bodyStyle?: React.CSSProperties;
  headStyle?: React.CSSProperties;
}
```

#### Dropdown
Enhanced dropdown components.

**Props:**
```typescript
interface DropdownProps {
  items: MenuItem[];
  children: React.ReactNode;
  trigger?: ('click' | 'hover' | 'contextMenu')[];
  placement?: 'topLeft' | 'topCenter' | 'topRight' | 'bottomLeft' | 'bottomCenter' | 'bottomRight' | 'top' | 'bottom';
  overlayStyle?: React.CSSProperties;
  onVisibleChange?: (visible: boolean) => void;
}
```

#### Tabs
Enhanced tabs components.

**Props:**
```typescript
interface TabsProps {
  items: TabItem[];
  activeKey?: string;
  onChange?: (key: string) => void;
  type?: 'line' | 'card' | 'editable-card' | 'segmented';
  size?: 'small' | 'default' | 'large';
  position?: 'top' | 'right' | 'bottom' | 'left';
  tabPosition?: 'top' | 'right' | 'bottom' | 'left';
  centered?: boolean;
  animated?: boolean;
  addIcon?: React.ReactNode;
  onEdit?: (targetKey: string, action: 'add' | 'remove') => void;
  hideAdd?: boolean;
}

interface TabItem {
  key: string;
  label: React.ReactNode;
  children?: React.ReactNode;
  icon?: React.ReactNode;
  disabled?: boolean;
  closable?: boolean;
}
```

#### Accordion
Collapsible sections.

**Props:**
```typescript
interface AccordionProps {
  items: AccordionItem[];
  activeKey?: string | string[];
  onChange?: (key: string | string[]) => void;
  type?: 'accordion' | 'collapse';
  ghost?: boolean;
  expandIcon?: React.ReactNode;
  expandIconPosition?: 'left' | 'right';
  defaultActiveKey?: string | string[];
  destroyInactivePanel?: boolean;
}

interface AccordionItem {
  key: string;
  title: React.ReactNode;
  children: React.ReactNode;
  icon?: React.ReactNode;
  disabled?: boolean;
}
```

#### Stepper
Multi-step process components.

**Props:**
```typescript
interface StepperProps {
  current: number;
  onChange?: (current: number) => void;
  items: StepItem[];
  type?: 'default' | 'navigation' | 'inline';
  size?: 'small' | 'default';
  direction?: 'horizontal' | 'vertical';
  initial?: number;
  status?: 'wait' | 'process' | 'finish' | 'error';
}

interface StepItem {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  disabled?: boolean;
  subTitle?: string;
}
```

#### Timeline
Chronological event display.

**Props:**
```typescript
interface TimelineProps {
  items: TimelineItem[];
  mode?: 'left' | 'alternate' | 'right' | 'both';
  pending?: boolean;
  pendingDot?: React.ReactNode;
  reverse?: boolean;
  type?: 'default' | 'alternate' | 'left' | 'right';
}

interface TimelineItem {
  key: string;
  label?: React.ReactNode;
  children: React.ReactNode;
  color?: string;
  dot?: React.ReactNode;
  position?: 'left' | 'right';
  pending?: boolean;
}
```

#### Calendar
Multiple calendar views.

**Props:**
```typescript
interface CalendarProps {
  value?: moment.Moment | Date;
  onChange?: (date: moment.Moment | Date) => void;
  type?: 'month' | 'week' | 'range' | 'event';
  mode?: 'month' | 'year' | 'decade';
  fullscreen?: boolean;
  headerRender?: (value: moment.Moment) => React.ReactNode;
  dateCellRender?: (date: moment.Moment) => React.ReactNode;
  monthCellRender?: (date: moment.Moment) => React.ReactNode;
}
```

#### Tree
Hierarchical data display.

**Props:**
```typescript
interface TreeProps {
  data: TreeNode[];
  onSelect?: (keys: React.Key[], info: { selected: boolean; selectedNodes: TreeNode[]; node: TreeNode; event: React.MouseEvent }) => void;
  onCheck?: (checkedKeys: React.Key[], info: { checked: boolean; checkedNodes: TreeNode[]; node: TreeNode; event: React.MouseEvent }) => void;
  checkable?: boolean;
  selectable?: boolean;
  multiple?: boolean;
  checkStrictly?: boolean;
  autoExpandParent?: boolean;
  expandedKeys?: React.Key[];
  selectedKeys?: React.Key[];
  checkedKeys?: React.Key[];
  defaultExpandAll?: boolean;
  defaultExpandParent?: boolean;
  defaultCheckedKeys?: React.Key[];
  defaultSelectedKeys?: React.Key[];
  loadData?: (treeNode: TreeNode) => Promise<void>;
  showLine?: boolean;
  showIcon?: boolean;
  icon?: React.ReactNode | ((props: { isLeaf: boolean; expanded: boolean }) => React.ReactNode);
  switcherIcon?: React.ReactNode | ((props: { isLeaf: boolean; expanded: boolean; loading: boolean }) => React.ReactNode);
  draggable?: boolean;
  blockNode?: boolean;
}

interface TreeNode {
  key: React.Key;
  title: React.ReactNode;
  children?: TreeNode[];
  disabled?: boolean;
  disableCheckbox?: boolean;
  selectable?: boolean;
  checkable?: boolean;
  isLeaf?: boolean;
  icon?: React.ReactNode;
}
```

#### Transfer
Dual-list transfer components.

**Props:**
```typescript
interface TransferProps {
  dataSource: TransferItem[];
  targetKeys?: React.Key[];
  onChange?: (targetKeys: React.Key[], direction: 'left' | 'right', moveKeys: React.Key[]) => void;
  onSelectChange?: (sourceSelectedKeys: React.Key[], targetSelectedKeys: React.Key[]) => void;
  onScroll?: (direction: 'left' | 'right', e: React.SyntheticEvent) => void;
  titles?: [string, string];
  operations?: string[];
  showSearch?: boolean;
  filterOption?: (inputValue: string, option: TransferItem) => boolean;
  locale?: {
    notFoundContent?: string;
    searchPlaceholder?: string;
    itemUnit?: string;
    itemsUnit?: string;
  };
  rowKey?: (record: TransferItem) => React.Key;
  render?: (item: TransferItem) => React.ReactNode;
  showSelectAll?: boolean;
  selectAllLabels?: [React.ReactNode, React.ReactNode];
  oneWay?: boolean;
  pagination?: boolean | object;
}

interface TransferItem {
  key: React.Key;
  title: string;
  description?: string;
  disabled?: boolean;
  [key: string]: any;
}
```

#### Carousel
Multiple carousel variants.

**Props:**
```typescript
interface CarouselProps {
  items: CarouselItem[];
  autoPlay?: boolean;
  autoPlaySpeed?: number;
  dots?: boolean;
  arrows?: boolean;
  fade?: boolean;
  vertical?: boolean;
  infinite?: boolean;
  slidesToShow?: number;
  slidesToScroll?: number;
  beforeChange?: (from: number, to: number) => void;
  afterChange?: (current: number) => void;
}

interface CarouselItem {
  key: string;
  title?: string;
  description?: string;
  image?: string;
  content?: React.ReactNode;
  href?: string;
}
```

---

## 🔧 Backend Services

### Graph Analytics Engine

The Graph Analytics Engine provides comprehensive graph analysis capabilities.

**Features:**
- Node and relationship management
- Cypher query execution
- Network analysis (centrality, communities, path finding)
- Graph visualization (Matplotlib, PyVis, Plotly)
- Temporal analysis

**Endpoints:**
- `POST /api/graph/nodes` - Create a node
- `GET /api/graph/nodes/{id}` - Get a node
- `GET /api/graph/nodes` - List all nodes
- `POST /api/graph/edges` - Create an edge
- `GET /api/graph/edges` - List all edges
- `POST /api/graph/query` - Execute a Cypher query
- `POST /api/graph/centrality` - Calculate centrality metrics
- `POST /api/graph/communities` - Detect communities
- `POST /api/graph/path` - Find path between nodes

**Algorithms:**
- **Centrality**: Degree, Betweenness, Closeness, Eigenvector, PageRank
- **Community Detection**: Louvain, Label Propagation, Girvan-Newman
- **Path Finding**: Shortest Path, All Paths, Dijkstra, A*

### AI/ML Services

The AI/ML module provides intelligent analysis capabilities.

**Features:**
- Anomaly detection
- Entity resolution
- Link prediction
- Node classification
- Graph evolution prediction
- Threat prediction
- Natural language chat

**Endpoints:**
- `POST /api/ai/chat` - Chat with AI Assistant
- `POST /api/ai/anomalies/detect` - Detect anomalies
- `GET /api/ai/anomalies/scores` - Get anomaly scores
- `POST /api/ai/entities/resolve` - Resolve entities
- `POST /api/ai/entities/deduplicate` - Deduplicate entities
- `POST /api/ai/predict/link` - Predict link
- `POST /api/ai/predict/node` - Predict node classification
- `GET /api/ai/predict/graph-evolution` - Predict graph evolution
- `GET /api/ai/predict/threats` - Predict threats

**Methods:**
- **Anomaly Detection**: Statistical, Z-Score, IQR, Isolation Forest, Local Outlier Factor, DBSCAN, Graph-based, Temporal
- **Entity Resolution**: Exact, Fuzzy, Record Linkage, Graph-based
- **Link Prediction**: Common Neighbors, Jaccard, Adamic-Adar, Preferential Attachment

### Scraping Service

The Scraping Service provides distributed web scraping capabilities.

**Features:**
- Platform-specific scrapers (VK, Twitter, Instagram)
- Generic web scraping
- Proxy rotation
- Rate limiting
- Caching
- JavaScript rendering
- Async task queue (Celery)

**Endpoints:**
- `GET /api/scraping/jobs` - List all jobs
- `POST /api/scraping/jobs` - Create a new job
- `POST /api/scraping/scrape` - Start a scrape
- `POST /api/scraping/vk/user` - Scrape VK user
- `POST /api/scraping/vk/posts` - Scrape VK posts
- `POST /api/scraping/vk/search` - Search VK users
- `POST /api/scraping/twitter/tweets` - Scrape Twitter tweets
- `POST /api/scraping/twitter/user` - Scrape Twitter user
- `POST /api/scraping/twitter/trends` - Get Twitter trends
- `POST /api/scraping/instagram/user` - Scrape Instagram user
- `POST /api/scraping/instagram/posts` - Scrape Instagram posts
- `POST /api/scraping/instagram/hashtag` - Scrape Instagram hashtag

**Scraper Configuration:**
```python
{
  "rate_limit_delay": 1.0,  # Seconds between requests
  "use_proxy": True,
  "use_cache": True,
  "render_js": False,
  "max_depth": 3,
  "timeout": 30
}
```

### Threat Intelligence

The Threat Intelligence module provides IOC management and analysis.

**Features:**
- Threat feed integration (STIX, MISP, OTX)
- IOC management (IP, Domain, URL, Hash, Email)
- IOC enrichment
- IOC correlation
- Alert generation
- STIX/TAXII support

**Endpoints:**
- `GET /api/threat/feeds` - List all feeds
- `POST /api/threat/feeds` - Add a new feed
- `GET /api/threat/iocs` - List all IOCs
- `POST /api/threat/iocs` - Add a new IOC
- `GET /api/threat/alerts` - List all alerts
- `POST /api/threat/alerts` - Create a new alert
- `GET /api/threat/rules` - List all rules
- `POST /api/threat/rules` - Add a new rule
- `POST /api/threat/enrichment` - Enrich an IOC
- `POST /api/threat/correlation` - Correlate IOCs
- `POST /api/threat/stix` - Import/export STIX

**IOC Types:**
- IP Address
- Domain
- URL
- Hash (MD5, SHA1, SHA256)
- Email

**Severity Levels:**
- Critical
- High
- Medium
- Low
- Info

### Security

The Security module provides authentication and authorization.

**Features:**
- JWT-based authentication
- Role-Based Access Control (RBAC)
- Audit logging
- Encryption services
- Password hashing

**Endpoints:**
- `POST /api/security/token` - Get JWT token
- `POST /api/security/refresh` - Refresh access token
- `POST /api/security/logout` - Logout
- `GET /api/security/users` - List all users
- `POST /api/security/users` - Create a new user
- `GET /api/security/users/{id}` - Get user details
- `PUT /api/security/users/{id}` - Update user
- `GET /api/security/roles` - List all roles
- `POST /api/security/roles` - Create a new role
- `GET /api/security/permissions` - List all permissions
- `POST /api/security/permissions` - Create a new permission
- `GET /api/security/audit` - Get audit logs
- `POST /api/security/audit` - Log an audit event
- `POST /api/security/encrypt` - Encrypt data
- `POST /api/security/decrypt` - Decrypt data

**RBAC:**
- **Roles**: Admin, Analyst, Viewer, Custom
- **Permissions**: Create, Read, Update, Delete, Manage
- **Resources**: User, Role, Permission, Graph, Scraping, Threat, AI, System

---

## 🔐 Authentication

OpenLens uses JWT (JSON Web Token) for authentication.

### Authentication Flow

1. **Login**: User submits credentials to `/api/security/token`
2. **Token Issuance**: Server returns access token and refresh token
3. **Token Storage**: Tokens are stored in HTTP-only cookies
4. **API Requests**: Access token is sent in Authorization header
5. **Token Refresh**: When access token expires, refresh token is used to get a new one
6. **Logout**: Tokens are invalidated and removed from cookies

### Token Structure

**Access Token:**
```json
{
  "sub": "user_id",
  "username": "username",
  "roles": ["admin", "analyst"],
  "exp": 1234567890,
  "iat": 1234567800
}
```

**Refresh Token:**
```json
{
  "sub": "user_id",
  "exp": 1234567890,
  "iat": 1234567800
}
```

### Token Configuration

```python
# JWT Settings
JWT_SECRET_KEY = "your-secret-key"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = 60  # Access token expires in 60 minutes
JWT_REFRESH_EXPIRE_DAYS = 7  # Refresh token expires in 7 days
```

### Automatic Token Refresh

The frontend automatically refreshes the access token when it receives a 401 Unauthorized response:

1. Interceptor catches 401 response
2. Checks if refresh token exists
3. Calls `/api/security/refresh` with refresh token
4. Updates access token in cookies
5. Retries the original request with new token

### Password Hashing

Passwords are hashed using bcrypt:
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash password
hashed_password = pwd_context.hash(password)

# Verify password
is_valid = pwd_context.verify(password, hashed_password)
```

---

## 📡 WebSocket Integration

OpenLens uses WebSocket for real-time communication between frontend and backend.

### WebSocket Endpoints

| Endpoint | Description | Authentication |
|----------|-------------|---------------|
| `/api/ws` | Main WebSocket | Optional |
| `/api/ws/notifications` | Notifications | Required |
| `/api/ws/graph` | Graph updates | Required |
| `/api/ws/scraping` | Scraping updates | Required |
| `/api/ws/threat` | Threat updates | Required |

### Connection

**Frontend:**
```typescript
import { useWebSocket } from '../hooks/useApi';

const { isConnected, messages, sendMessage, subscribe, unsubscribe } = useWebSocket(
  '/ws/graph',
  (data) => {
    // Handle incoming messages
    console.log('Received:', data);
  }
);
```

**Backend (FastAPI):**
```python
from fastapi import WebSocket

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    await websocket.accept()
    
    # Authenticate if token provided
    if token:
        payload = decode_token(token)
        if not payload:
            await websocket.close(code=1008)
            return
    
    # Handle messages
    while True:
        data = await websocket.receive_json()
        # Process message
        await websocket.send_json({"type": "response", "data": data})
```

### Message Types

**Graph Updates:**
```json
{
  "type": "graph_update",
  "action": "create" | "update" | "delete",
  "target": "node" | "edge",
  "data": { ... }
}
```

**Notifications:**
```json
{
  "type": "notification",
  "id": "notification_id",
  "title": "Notification Title",
  "message": "Notification message",
  "severity": "info" | "warning" | "error",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**Scraping Updates:**
```json
{
  "type": "job_update",
  "job_id": "job_id",
  "status": "queued" | "running" | "paused" | "completed" | "failed",
  "progress": 0-100,
  "message": "Update message"
}
```

**Threat Updates:**
```json
{
  "type": "threat_update",
  "action": "new_ioc" | "updated_ioc" | "new_alert",
  "data": { ... }
}
```

### Reconnection

The WebSocket client automatically reconnects with exponential backoff:

```typescript
// Configuration
const maxReconnectAttempts = 5;
const reconnectDelay = 3000; // 3 seconds

// Reconnect logic
if (reconnectAttempts < maxReconnectAttempts) {
  const delay = reconnectDelay * Math.pow(2, reconnectAttempts);
  setTimeout(() => {
    setReconnectAttempts(prev => prev + 1);
    connect();
  }, delay);
}
```

---

## 🧪 Testing

### Frontend Testing

**Unit Tests:**
```bash
npm test
```

**Test Files:**
- `src/lib/__tests__/apiClient.test.ts` - API client tests
- `src/hooks/__tests__/useApi.test.tsx` - Hook tests
- `src/components/common/__tests__/ProtectedRoute.test.tsx` - Component tests

**Test Coverage:**
- API client configuration
- Authentication functions
- API hooks (GET, POST, PUT, DELETE)
- Graph hooks
- AI hooks
- Security hooks
- Utility hooks (theme, localStorage, debounce, previous)
- ProtectedRoute component
- PublicRoute component

### Backend Testing

**Run tests:**
```bash
cd backend
pytest
```

**Test Files:**
- `tests/test_graph.py` - Graph engine tests
- `tests/test_ai.py` - AI module tests
- `tests/test_scraping.py` - Scraping tests
- `tests/test_security.py` - Security tests
- `tests/test_threat.py` - Threat intelligence tests
- `tests/test_api.py` - API endpoint tests

### Test Configuration

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
```

---

## 🚀 Deployment

### Development Deployment

1. **Start backend:**
```bash
cd backend/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

2. **Start frontend:**
```bash
cd frontend
npm run dev
```

3. **Access the app:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### Production Deployment

#### Docker Deployment

1. **Build Docker images:**
```bash
# Frontend
docker build -t openlens-frontend -f frontend/Dockerfile .

# Backend
docker build -t openlens-backend -f backend/Dockerfile .
```

2. **Run containers:**
```bash
docker-compose -f docker-compose.yml up -d
```

3. **Access the app:**
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

#### Manual Deployment

1. **Build frontend:**
```bash
cd frontend
npm run build
```

2. **Serve frontend:**
```bash
npx serve -s build -l 3000
```

3. **Run backend:**
```bash
cd backend/api
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

4. **Set up reverse proxy (Nginx):**
```nginx
server {
    listen 80;
    server_name openlens.example.com;

    location / {
        root /path/to/frontend/build;
        try_files $uri /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Kubernetes Deployment

1. **Create Kubernetes manifests:**
```yaml
# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: openlens-frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: openlens-frontend
  template:
    metadata:
      labels:
        app: openlens-frontend
    spec:
      containers:
      - name: frontend
        image: openlens-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: REACT_APP_API_URL
          value: "http://openlens-backend:8000"
        - name: REACT_APP_WS_URL
          value: "ws://openlens-backend:8000"
---
apiVersion: v1
kind: Service
metadata:
  name: openlens-frontend
spec:
  selector:
    app: openlens-frontend
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
```

2. **Apply manifests:**
```bash
kubectl apply -f frontend-deployment.yaml
kubectl apply -f backend-deployment.yaml
```

---

## 🐛 Troubleshooting

### Common Issues

**1. CORS Errors**

**Symptom:** `Access to XMLHttpRequest at 'http://localhost:8000/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution:**
- Ensure backend CORS middleware is configured:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
- Or specify allowed origins:
```python
allow_origins=["http://localhost:3000", "http://your-domain.com"]
```

**2. WebSocket Connection Failed**

**Symptom:** WebSocket connection fails with status code 1006

**Solution:**
- Check if backend WebSocket server is running
- Verify WebSocket URL in frontend:
```typescript
// Should match backend URL
const WS_BASE_URL = 'ws://localhost:8000';
```
- Check for authentication issues (token may be expired)

**3. 401 Unauthorized Errors**

**Symptom:** API requests return 401 Unauthorized

**Solution:**
- Check if access token is present in cookies
- Verify token is not expired
- Check if token is being sent in Authorization header:
```typescript
headers: {
  'Authorization': `Bearer ${token}`,
}
```
- Enable automatic token refresh in apiClient

**4. 404 Not Found Errors**

**Symptom:** API endpoints return 404

**Solution:**
- Verify backend is running
- Check endpoint URLs match between frontend and backend
- Ensure API version is correct (v1, v2, etc.)
- Check for typos in endpoint paths

**5. Build Failures**

**Symptom:** Frontend build fails with errors

**Solution:**
- Delete `node_modules` and reinstall:
```bash
rm -rf node_modules package-lock.json
npm install
```
- Check for dependency version conflicts
- Ensure Node.js version is compatible (>= 16.0.0)

**6. Memory Issues**

**Symptom:** Backend crashes with memory errors

**Solution:**
- Increase worker count:
```bash
uvicorn main:app --workers 4
```
- Use Gunicorn with Uvicorn workers:
```bash
gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 main:app
```
- Optimize memory usage in scrapers

### Debug Mode

**Frontend:**
```bash
# Enable debug logging
REACT_APP_DEBUG=true npm start
```

**Backend:**
```bash
# FastAPI debug mode
uvicorn main:app --reload --log-level debug
```

### Logging

**Frontend:**
- Check browser console for errors
- Check network tab for API request/response details

**Backend:**
- Check FastAPI logs:
```bash
# View logs
journalctl -u openlens-backend -f

# Or check log files
cat /var/log/openlens/backend.log
```

---

## 📞 Support

For issues, questions, or feature requests:

1. **Check the documentation** - This file and other docs in the `/docs` directory
2. **Search existing issues** - Check GitHub issues for similar problems
3. **Create a new issue** - Open a GitHub issue with details about your problem
4. **Join the community** - Join our Discord server for real-time support

### Issue Template

```markdown
## Description

[Describe the issue]

## Steps to Reproduce

1. [First step]
2. [Second step]
3. [Third step]

## Expected Behavior

[What you expected to happen]

## Actual Behavior

[What actually happened]

## Environment

- OpenLens Version: [e.g., 7.0.0]
- Node.js Version: [e.g., 18.16.0]
- npm Version: [e.g., 9.5.1]
- Python Version: [e.g., 3.11.4]
- Browser: [e.g., Chrome 115]
- OS: [e.g., Ubuntu 22.04]

## Additional Context

[Any other relevant information]
```

---

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Ant Design](https://ant.design/) - UI Component Library
- [React](https://reactjs.org/) - JavaScript Library
- [TypeScript](https://www.typescriptlang.org/) - Type System
- [FastAPI](https://fastapi.tiangolo.com/) - Backend Framework
- [Cytoscape.js](https://js.cytoscape.org/) - Graph Visualization
- [Vite](https://vitejs.dev/) - Build Tool
- [Uvicorn](https://www.uvicorn.org/) - ASGI Server
- [Celery](https://docs.celeryq.dev/) - Distributed Task Queue
- [Neo4j](https://neo4j.com/) - Graph Database
- [PostgreSQL](https://www.postgresql.org/) - Relational Database
- [Redis](https://redis.io/) - In-Memory Data Store
