# OpenLens Frontend

Enterprise-Grade OSINT Platform Dashboard

## 🚀 Quick Start

### Prerequisites
- Node.js >= 16.0.0
- npm >= 8.0.0
- Backend API running (see [OpenLens Backend](../backend/README.md))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/NilsBriggen/OpenLens.git
cd OpenLens/frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
Copy the appropriate environment file:
```bash
# For development
cp .env.development .env

# For production
cp .env.production .env
```

Edit the `.env` file to match your backend configuration:
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
```

4. **Start the development server**
```bash
npm start
```

The app will be available at `http://localhost:3000`

### Using Vite (Recommended for Development)

For faster development with hot module replacement:

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── common/         # Common components (buttons, cards, etc.)
│   │   ├── GraphVisualization.tsx
│   │   ├── ConnectedGraphVisualization.tsx
│   │   ├── AIChatAssistant.tsx
│   │   ├── NotificationCenter.tsx
│   │   └── ...
│   ├── contexts/           # React contexts
│   │   └── WebSocketContext.tsx
│   ├── hooks/              # Custom React hooks
│   │   └── useApi.ts       # API hooks with Axios
│   ├── layouts/            # Page layouts
│   │   └── MainLayout.tsx
│   ├── lib/                # Library utilities
│   │   └── apiClient.ts    # Axios configuration
│   ├── pages/              # Page components
│   │   ├── Dashboard.tsx
│   │   ├── GraphExplorer.tsx
│   │   ├── AIAnalytics.tsx
│   │   ├── ScrapingHub.tsx
│   │   ├── SecurityCenter.tsx
│   │   ├── ThreatIntelligence.tsx
│   │   └── ...
│   ├── providers/          # React Query providers
│   │   └── AppProvider.tsx
│   ├── utils/              # Utility functions
│   │   ├── exportUtils.ts
│   │   └── uiUtils.ts
│   ├── App.tsx
│   ├── index.tsx
│   └── index.css
├── .env.development
├── .env.production
├── .env.staging
├── vite.config.ts
├── package.json
└── README.md
```

## 🔌 API Configuration

The frontend connects to the FastAPI backend at `http://localhost:8000` by default.

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API base URL | `http://localhost:8000` |
| `REACT_APP_WS_URL` | WebSocket URL | `ws://localhost:8000` |
| `REACT_APP_ENV` | Environment mode | `development` |

### API Endpoints

The frontend uses the following backend endpoints:

- **Authentication**: `/api/security/token`, `/api/security/refresh`, `/api/security/logout`
- **Graph Analytics**: `/api/graph/stats`, `/api/graph/nodes`, `/api/graph/edges`, `/api/graph/query`
- **AI/ML**: `/api/ai/chat`, `/api/ai/anomalies/detect`, `/api/ai/entities/resolve`, `/api/ai/predict/*`
- **Scraping**: `/api/scraping/jobs`, `/api/scraping/scrape`, `/api/scraping/vk/*`, `/api/scraping/twitter/*`, `/api/scraping/instagram/*`
- **Threat Intelligence**: `/api/threat/feeds`, `/api/threat/iocs`, `/api/threat/alerts`, `/api/threat/rules`
- **System**: `/api/system/health`, `/api/system/stats`
- **WebSocket**: `/api/ws`, `/api/ws/notifications`, `/api/ws/graph`

## 🎯 Features

### Core Features
- **Graph Visualization**: Interactive graph exploration with Cytoscape.js
- **AI Assistant**: Natural language queries with context-aware responses
- **Real-time Updates**: WebSocket integration for live data
- **Authentication**: JWT-based authentication with automatic token refresh
- **Responsive Design**: Mobile-friendly UI with Ant Design

### Advanced Features
- **Graph Analytics**: Centrality, community detection, path finding
- **Anomaly Detection**: Statistical and ML-based anomaly detection
- **Entity Resolution**: Fuzzy matching and deduplication
- **Threat Intelligence**: IOC management, enrichment, correlation
- **Distributed Scraping**: Platform-specific scrapers with proxy support
- **Export**: CSV, JSON, STIX, PDF export capabilities

## 🛠️ Build & Deployment

### Development Build
```bash
npm run build
```

### Production Build with Vite
```bash
npm run build:vite
```

### Bundle Analysis
To analyze the bundle size:
```bash
npm run build:analyze
```

This will generate a `bundle-analysis.html` file in the `dist` directory.

### Deployment

1. **Build for production**
```bash
npm run build
```

2. **Serve the build**
```bash
npx serve -s build
```

Or deploy to a web server (Nginx, Apache, etc.)

## 🧪 Testing

Run unit tests:
```bash
npm test
```

## ⚙️ Configuration

### Theme Customization
Edit `src/index.tsx` to customize the Ant Design theme:
```typescript
<ConfigProvider
  theme={{
    token: {
      colorPrimary: '#1890ff',
      borderRadius: 8,
    },
  }}
>
```

### API Client Configuration
Edit `src/lib/apiClient.ts` to customize Axios settings:
- Base URL
- Timeout
- Headers
- Interceptors

### WebSocket Configuration
Edit `src/contexts/WebSocketContext.tsx` to customize WebSocket settings:
- URL
- Reconnection logic
- Message handling

## 📡 WebSocket Integration

The frontend uses WebSocket for real-time updates:
- Graph updates
- Notification delivery
- Scraping progress
- Threat intelligence alerts

WebSocket endpoints:
- `/api/ws` - Main WebSocket endpoint
- `/api/ws/notifications` - Notifications only
- `/api/ws/graph` - Graph updates only

## 🔒 Authentication Flow

1. User logs in via `/api/security/token`
2. JWT tokens are stored in HTTP-only cookies
3. Access token is used for API requests
4. Refresh token is used to get new access tokens
5. Automatic token refresh on 401 responses

## 📊 Performance Optimization

### Code Splitting
The app uses React.lazy() for lazy loading pages:
```typescript
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
```

### Bundle Analysis
Use `npm run build:analyze` to generate a bundle analysis report.

### Manual Chunks
Vite is configured to split large dependencies into separate chunks:
- Vendor libraries (React, Ant Design, etc.)
- Charting libraries (D3, Recharts, etc.)
- Heavy components (Monaco Editor, Three.js, etc.)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and lint
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](../LICENSE)

## 🙏 Acknowledgments

- [Ant Design](https://ant.design/) - UI Component Library
- [React](https://reactjs.org/) - JavaScript Library
- [TypeScript](https://www.typescriptlang.org/) - Type System
- [FastAPI](https://fastapi.tiangolo.com/) - Backend Framework
- [Cytoscape.js](https://js.cytoscape.org/) - Graph Visualization
- [Vite](https://vitejs.dev/) - Build Tool
