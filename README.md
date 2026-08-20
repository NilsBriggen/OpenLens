# OpenLens

> **A Custom, Open-Source Intelligence (OSINT) Gathering and Analysis Framework**

OpenLens is a modular tool for collecting, analyzing, and visualizing publicly available data (e.g., social media, geolocation, metadata) to uncover connections and patterns. Inspired by tools like Maltego, OpenLens aims to democratize OSINT capabilities for researchers, journalists, and analysts.

---

## \ud83d\ude80 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)
- PostgreSQL (optional, for structured data)
- Neo4j (optional, for graph relationships)
- Redis (optional, for rate limiting and caching)

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
4. Run the Flask API:
   ```bash
   python app.py
   ```
   The API will start at `http://localhost:5000`.

### Frontend Setup (Optional)
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the React app:
   ```bash
   npm start
   ```
   The app will open at `http://localhost:3000`.

---

## \ud83d\udcc2 Project Structure

OpenLens is organized into the following main components:

- **backend/**: Python backend with Flask, Celery, and various modules
  - `app.py`: Main Flask application entry point
  - `requirements.txt`: Python dependencies
  - `ai/`: AI/ML modules (anomaly detection, entity resolution, predictive analytics)
  - `graph/`: Graph analytics engine (graph_engine, network_analysis, path_finding, community_detection, graph_visualizer, temporal_analysis)
  - `scraping/`: Distributed scraping system (celery_app, proxy_manager, user_agent_manager, rate_limiter, result_cache, scraper, distributed_scraper, scraping_tasks)
  - `security/`: Enterprise security (rbac, audit, encryption, authentication, authorization, security_policies, compliance)
  - `threat_intelligence/`: Real-time threat intelligence pipeline (threat_feeds, ioc_manager, threat_analysis, alerting, threat_hunting, threat_intel_sharing, monitoring, threat_graph)
  - `nlp/`: NLP analysis (sentiment_analyzer, topic_modeler)
  - `processors/`: Data processing (data_processor, metadata_extractor, nlp_processor, normalizer)
  - `models/`: Database models (neo4j_models, postgres_models)
  - `database/`: Database integration (neo4j_db, postgres_db)
  - `auth/`: Authentication (authentication, models)
  - `api/`: API endpoints and documentation
  - `middleware/`: Middleware (rate_limiter)
  - `monitoring/`: Monitoring (health, analytics, logger, middleware)
  - `export/`: Data export (exporter)
  - `websocket/`: WebSocket server (socket_server, event_handlers)
  - `scrapers/`: Social media scrapers (vk_scraper, telegram_scraper, twitter_scraper, instagram_scraper)
  - `tasks/`: Celery tasks (celery_app, processing_tasks, scraping_tasks)
  - `tests/`: Unit tests

- **frontend/**: React frontend with TypeScript
  - `src/`: React components and application code
  - `public/`: Static files
  - `package.json`: Node.js dependencies

- **monitoring/**: Monitoring configuration
  - `prometheus.yml`: Prometheus configuration
  - `grafana/`: Grafana dashboards and datasources

- **docker-compose.yml**: Docker Compose configuration for local development
- **docker-compose.production.yml**: Production Docker Compose configuration
- **docker-compose.staging.yml**: Staging Docker Compose configuration
- **nginx.production.conf**: Production Nginx configuration

---

## \ud83d\udce6 Configuration

### Environment Variables

Create a `.env` file in the backend directory. See `.env.example` for the template.

### Database Setup

#### PostgreSQL
1. Install PostgreSQL
2. Create a database and user
3. Update `.env` with connection details

#### Neo4j
1. Install Neo4j
2. Start the server
3. Access at `http://localhost:7474`
4. Default credentials: `neo4j` / `neo4j`

---

## \ud83d\udcdc Deployment

### Using Docker Compose

```bash
docker-compose up -d --build
docker-compose logs -f
```

### Production Deployment

Use the production Docker Compose file:
```bash
docker-compose -f docker-compose.production.yml up -d --build
```

---

## \ud83d\udce7 API Documentation

The API will be available at `/docs/` once the backend is running.

### Authentication

- JWT-based authentication
- API key authentication
- Rate limiting

---

## \ud83d\udee0\ufe0f Core Features

### Phase 6 Implementation (Complete)

1. **Graph Analytics Engine** (6 modules)
   - Neo4j integration
   - Network analysis (centrality, community detection, path finding)
   - Graph visualization
   - Temporal analysis

2. **AI/ML-Powered Insights** (7 modules)
   - Anomaly detection (statistical, ML-based, graph-based)
   - Entity resolution (exact matching, fuzzy matching, record linkage)
   - Predictive analytics (link prediction, node classification, threat prediction)

3. **Distributed Scraping System** (9 modules)
   - Celery-based task distribution
   - Proxy rotation
   - User agent rotation
   - Rate limiting
   - Result caching
   - Web scraping
   - Distributed scraping

4. **Enterprise Security** (7 modules)
   - RBAC (Role-Based Access Control)
   - Audit logging
   - Encryption (symmetric, asymmetric, hashing)
   - Authentication (JWT, session management)
   - Authorization (permission checking, policy evaluation)
   - Security policies
   - Compliance (GDPR, HIPAA, SOC2, ISO27001)

5. **Real-Time Threat Intelligence Pipeline** (8 modules)
   - Threat feed integration
   - IOC (Indicator of Compromise) management
   - Threat analysis and scoring
   - Alerting
   - Threat hunting
   - Intelligence sharing (STIX/TAXII, MISP)
   - Monitoring
   - Threat graph

---

## \ud83d\udce7 Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## \ud83d\udcdc License

MIT License

---

## \ud83e\udd1d Contributing

Contributions are welcome! Please fork the repository and submit pull requests.

---

## \ud83d\udce7 Support

For questions or support, please open an issue in the GitHub repository.
