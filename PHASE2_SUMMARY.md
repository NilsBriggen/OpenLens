# OpenLens - Phase 2 Implementation Summary

## Overview
This document summarizes the implementation of **Phase 2** of the OpenLens OSINT framework, which includes:
- Advanced Visualizations (Timeline, Heatmap)
- Data Normalization Pipeline
- API Improvements (Pagination, Rate Limiting)
- Frontend Integration (NLP, Twitter, Instagram)

---

## 1. Advanced Visualizations

### Backend (`backend/processors/data_processor.py`)
Created a comprehensive data processor with support for:
- **Timeline Data**: `TimelineEvent` dataclass for temporal visualization
- **Heatmap Data**: `HeatmapPoint` dataclass for geospatial density visualization
- **Graph Data**: `GraphNode` and `GraphLink` dataclasses for network visualization
- **Data Aggregation**: Methods for aggregating data by date and location
- **Normalization**: Text, phone, email, URL normalization utilities

**Key Methods:**
- `create_timeline_from_posts()`: Convert posts to timeline events
- `create_heatmap_from_posts()`: Convert geotagged posts to heatmap points
- `create_heatmap_from_locations()`: Convert locations to heatmap points
- `create_graph_from_posts_and_users()`: Create network graph data
- `aggregate_by_date()`: Aggregate items by date
- `aggregate_by_location()`: Aggregate items by location

### Backend API (`backend/app.py`)
Added 3 new visualization endpoints:
- `POST /visualize/timeline`: Generate timeline data from posts
- `POST /visualize/heatmap`: Generate heatmap data from posts/locations
- `POST /visualize/graph`: Generate graph data from posts and users

### Frontend Components
Created 2 new React components:
1. **`TimelineVisualization.tsx`**: 
   - Displays events in a vertical timeline format
   - Supports sample data and API-generated data
   - Shows event details (title, date, description, category)

2. **`HeatmapVisualization.tsx`**:
   - Uses Leaflet with Heat plugin for geospatial visualization
   - Supports both heatmap and marker views
   - Displays location data with intensity values
   - Interactive map with zoom and pan

---

## 2. Data Normalization Pipeline

### Backend (`backend/processors/normalizer.py`)
Created a comprehensive data normalizer with support for:
- **Text Normalization**: Lowercase, remove extra spaces, special chars, punctuation
- **Phone Number Normalization**: Convert to international format (+CC)
- **Email Normalization**: Lowercase, remove spaces, validate format
- **URL Normalization**: Lowercase, remove trailing slash, add https:// prefix
- **Date/Time Normalization**: Convert to ISO format
- **Deduplication**: Remove duplicates from lists while preserving order
- **Validation**: Check email, URL, phone validity
- **Batch Normalization**: Normalize entire data structures

**Key Methods:**
- `normalize_text()`: Normalize text with various options
- `normalize_phone()`: Convert phone to international format
- `normalize_email()`: Clean and validate email addresses
- `normalize_url()`: Standardize URLs
- `normalize_date()`: Convert dates to ISO format
- `normalize_datetime()`: Convert datetimes to ISO format
- `deduplicate_list()`: Remove duplicates from lists
- `normalize_batch()`: Normalize entire data structures

### Backend API (`backend/app.py`)
Added 5 new normalization endpoints:
- `POST /normalize/text`: Normalize text
- `POST /normalize/phone`: Normalize phone numbers
- `POST /normalize/email`: Normalize email addresses
- `POST /normalize/url`: Normalize URLs
- `POST /normalize/batch`: Normalize batch data

---

## 3. API Improvements

### Rate Limiting (`backend/middleware/rate_limiter.py`)
Created a rate limiting middleware with:
- **In-memory Store**: Tracks requests per IP address
- **Configurable Limits**: Set requests per time window
- **Decorator**: Easy to apply to Flask endpoints
- **Cleanup**: Automatic cleanup of old entries

**Usage:**
```python
from middleware.rate_limiter import rate_limit

@app.route('/api/endpoint')
@rate_limit(limit=10, window=60)  # 10 requests per minute
def endpoint():
    return jsonify({"message": "Hello"})
```

**Applied to:**
- `/extract/metadata`: 10 requests/minute
- `/extract/text`: 20 requests/minute
- `/nlp/entities`: 15 requests/minute
- `/scrape/vk/user`: 5 requests/minute

### Pagination (`backend/app.py`)
Enhanced the `/scrape/vk/posts` endpoint with:
- **Page Parameter**: `?page=1` (default: 1)
- **Per Page Parameter**: `?per_page=10` (default: 10)
- **Date Filtering**: `?since=2023-01-01` and `?until=2023-12-31`
- **Pagination Info**: Returns total posts, total pages, has_next, has_prev

**Example Request:**
```
GET /scrape/vk/posts?username=durov&page=2&per_page=5&since=2023-01-01
```

**Example Response:**
```json
{
  "success": true,
  "username": "durov",
  "posts": [...],
  "pagination": {
    "page": 2,
    "per_page": 5,
    "total_posts": 50,
    "total_pages": 10,
    "has_next": true,
    "has_prev": true
  }
}
```

---

## 4. Frontend Integration

### New Components
Created 3 new React components for Phase 2 features:

1. **`NLPAnalyzer.tsx`**:
   - Text input for NLP analysis
   - Full analysis and entity extraction modes
   - Displays entities with color-coded labels
   - Shows categorized results (people, organizations, locations, dates, keywords)
   - Connects to `/nlp/entities` and `/nlp/analyze` endpoints

2. **`TwitterScraper.tsx`**:
   - Tab-based interface (Tweets, User Profile, Trends)
   - Search tweets by query
   - Get user profiles by username
   - Fetch trending topics
   - Displays tweets with metadata (likes, retweets, hashtags, geotags)
   - Connects to `/scrape/twitter/tweets`, `/scrape/twitter/user`, `/scrape/twitter/trends`

3. **`InstagramScraper.tsx`**:
   - Tab-based interface (User Profile, User Posts, Hashtag Posts)
   - Get user profiles by username
   - Fetch user posts with images
   - Search posts by hashtag
   - Displays posts with captions, media, and metadata
   - Connects to `/scrape/instagram/user`, `/scrape/instagram/posts`, `/scrape/instagram/hashtag`

### Updated Components
- **`App.tsx`**: Added navigation links for Timeline and Heatmap
- **`App.tsx`**: Added routes for all new components

### Navigation
Added 2 new navigation items:
- **Timeline**: `/timeline` - Timeline visualization
- **Heatmap**: `/heatmap` - Heatmap visualization

---

## 5. Dependencies

### Backend (`backend/requirements.txt`)
Updated with new dependencies:
- `pandas==2.1.4` - Data manipulation
- `numpy==1.26.2` - Numerical operations
- `python-dateutil==2.8.2` - Date parsing

### Frontend (`frontend/package.json`)
Updated with new dependencies:
- `leaflet.heat==0.2.0` - Heatmap layer for Leaflet
- `@types/leaflet==1.9.8` - TypeScript types for Leaflet
- `@types/d3==7.4.3` - TypeScript types for D3.js

---

## 6. File Changes Summary

### New Files
| File | Purpose | Status |
|------|---------|--------|
| `backend/processors/data_processor.py` | Data processing for visualizations | Complete |
| `backend/processors/normalizer.py` | Data normalization utilities | Complete |
| `backend/middleware/rate_limiter.py` | Rate limiting middleware | Complete |
| `frontend/src/components/NLPAnalyzer.tsx` | NLP analysis UI | Complete |
| `frontend/src/components/TwitterScraper.tsx` | Twitter scraping UI | Complete |
| `frontend/src/components/InstagramScraper.tsx` | Instagram scraping UI | Complete |
| `frontend/src/components/TimelineVisualization.tsx` | Timeline visualization UI | Complete |
| `frontend/src/components/HeatmapVisualization.tsx` | Heatmap visualization UI | Complete |

### Modified Files
| File | Changes | Status |
|------|---------|--------|
| `backend/app.py` | Added visualization endpoints, normalization endpoints, pagination, rate limiting | Complete |
| `backend/requirements.txt` | Added new dependencies | Complete |
| `frontend/package.json` | Added new dependencies | Complete |
| `frontend/src/App.tsx` | Added new routes and navigation | Complete |

---

## 7. API Endpoints Summary

### Phase 1 Endpoints (Existing)
- `/extract/metadata` - Extract EXIF metadata from images
- `/extract/text` - Extract metadata from text
- `/nlp/entities` - Extract entities from text
- `/nlp/analyze` - Comprehensive text analysis
- `/scrape/vk/user` - Scrape VK user profile
- `/scrape/vk/posts` - Scrape VK user posts
- `/scrape/vk/search` - Search VK users
- `/scrape/twitter/tweets` - Scrape Twitter tweets
- `/scrape/twitter/user` - Scrape Twitter user profile
- `/scrape/twitter/trends` - Scrape Twitter trends
- `/scrape/instagram/user` - Scrape Instagram user profile
- `/scrape/instagram/posts` - Scrape Instagram user posts
- `/scrape/instagram/hashtag` - Scrape Instagram posts by hashtag

### Phase 2 Endpoints (New)
- `/visualize/timeline` - Generate timeline data
- `/visualize/heatmap` - Generate heatmap data
- `/visualize/graph` - Generate graph data
- `/normalize/text` - Normalize text
- `/normalize/phone` - Normalize phone numbers
- `/normalize/email` - Normalize email addresses
- `/normalize/url` - Normalize URLs
- `/normalize/batch` - Normalize batch data

### Enhanced Endpoints
- `/scrape/vk/posts` - Now supports pagination and date filtering

---

## 8. Testing

### Backend Tests
- Existing tests in `backend/tests/test_metadata_extractor.py` continue to work
- New functionality can be tested via:
  - API endpoints (using curl or Postman)
  - Direct Python imports (e.g., `from processors.data_processor import data_processor`)

### Frontend Tests
- All new components can be accessed via the navigation menu
- Test with sample data or connect to the backend API
- Verify responsive design on different screen sizes

---

## 9. Known Limitations

1. **Twitter Scraper**: Web scraping fallback may be blocked by anti-bot measures. API access requires credentials.
2. **Instagram Scraper**: Blocked by Instagram's anti-bot measures. Requires authenticated session.
3. **Rate Limiting**: Uses in-memory store (not persistent across restarts). For production, use Redis.
4. **Pagination**: Currently implemented in-memory for VK posts. For large datasets, implement server-side pagination.
5. **Heatmap**: Requires `leaflet.heat` plugin to be properly loaded in the frontend.

---

## 10. Next Steps

### Phase 3 Tasks
1. **Database Integration**: Connect PostgreSQL and Neo4j to store scraped data
2. **Authentication**: Add user authentication and API key management
3. **Export/Import**: Add functionality to export data (CSV, JSON, PDF)
4. **Advanced NLP**: Add sentiment analysis, topic modeling
5. **Real-time Updates**: Implement WebSocket for real-time data updates
6. **Deployment**: Create production-ready Docker images and deployment scripts
7. **Monitoring**: Add logging and monitoring for API usage

### Immediate Tasks
1. Test all new endpoints with real data
2. Verify frontend components work with backend API
3. Fix any CORS issues between frontend and backend
4. Update documentation with new features

---

## 11. Usage Examples

### Timeline Visualization
```
POST /visualize/timeline
Content-Type: application/json

{
  "posts": [
    {"id": 1, "content": "Event 1", "timestamp": "2023-01-01T10:00:00Z"}
  ]
}
```

### Heatmap Visualization
```
POST /visualize/heatmap
Content-Type: application/json

{
  "posts": [
    {"id": 1, "geotag": {"latitude": 55.75, "longitude": 37.61}}
  ]
}
```

### Data Normalization
```
POST /normalize/text
Content-Type: application/json

{
  "text": "  Hello, World!  ",
  "lowercase": true,
  "remove_extra_spaces": true
}
```

### Paginated Scraping
```
GET /scrape/vk/posts?username=durov&page=2&per_page=5
```

---

## 12. Conclusion

Phase 2 of OpenLens has been successfully implemented with:
- Advanced visualizations (Timeline, Heatmap)
- Data normalization pipeline
- API improvements (Pagination, Rate Limiting)
- Frontend integration (NLP, Twitter, Instagram)

The framework now provides a comprehensive set of tools for OSINT data collection, processing, analysis, and visualization.
