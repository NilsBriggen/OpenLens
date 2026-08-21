"""
OpenLens Backend API

Flask-based API for OSINT data collection, processing, and analysis.
Endpoints:
- /extract/metadata: Extract EXIF metadata from images
- /extract/text: Extract geotags/hashtags from text
- /nlp/entities: Extract entities (people, orgs, locations) from text
- /nlp/analyze: Comprehensive text analysis
- /visualize/timeline: Generate timeline data from posts
- /visualize/heatmap: Generate heatmap data from locations
- /visualize/graph: Generate graph data from posts and users
- /scrape/vk/user: Scrape VK user profile
- /scrape/vk/posts: Scrape VK user posts
- /scrape/vk/search: Search VK users
- /scrape/twitter/tweets: Scrape Twitter tweets
- /scrape/twitter/user: Scrape Twitter user profile
- /scrape/twitter/trends: Scrape Twitter trends
- /scrape/instagram/user: Scrape Instagram user profile
- /scrape/instagram/posts: Scrape Instagram user posts
- /scrape/instagram/hashtag: Scrape Instagram posts by hashtag
- /tasks/scrape/vk/user: Async VK user scraping (Celery)
- /tasks/scrape/vk/posts: Async VK posts scraping (Celery)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime, timedelta
from processors.metadata_extractor import metadata_extractor
from processors.nlp_processor import nlp_processor
from processors.data_processor import data_processor
from processors.normalizer import normalizer
from database.postgres_db import db_manager, init_db
from database.neo4j_db import get_neo4j_db, init_neo4j
from auth.authentication import auth_required, get_current_user, create_access_token, create_refresh_token, verify_token, AuthConfig
from auth.models import User, RoleType
from export.exporter import exporter, export_to_csv, export_to_json, export_to_pdf
from nlp.sentiment_analyzer import sentiment_analyzer, analyze_sentiment, SentimentResult
from nlp.topic_modeler import topic_modeler, extract_topics, extract_keyphrases, TopicResult, KeyphraseResult
from websocket.socket_server import init_socketio, get_socketio
from websocket.event_handlers import register_event_handlers
from monitoring.logger import get_logger, setup_logging
from monitoring.middleware import init_logging_middleware
from monitoring.analytics import get_analytics
from monitoring.health import health_check, check_database, check_system
from scrapers.vk_scraper import VKScraper, VKUser, VKPost
from scrapers.twitter_scraper import TwitterScraper, Tweet, TwitterUser
from scrapers.instagram_scraper import InstagramScraper, InstagramPost, InstagramUser
from middleware.rate_limiter import init_rate_limiter, rate_limit

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Initialize rate limiter (100 requests per minute per IP)
init_rate_limiter(app, default_limit=100, default_window=60)

# Initialize databases
init_db(app)
init_neo4j(app)

# Initialize authentication
from auth.authentication import init_auth
init_auth(app)

# Initialize SocketIO
socketio = init_socketio(app)
register_event_handlers(socketio)

# Initialize monitoring
setup_logging()
init_logging_middleware(app)

# Apply rate limiting to all API endpoints
@app.after_request
def apply_rate_limiting(response):
    # Rate limiting is applied via decorator on specific endpoints
    return response

# Configure upload folder
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'uploads')
TASK_RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'data', 'task_results')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TASK_RESULTS_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Initialize scrapers
vk_scraper = VKScraper(rate_limit_delay=1.0)
twitter_scraper = TwitterScraper(rate_limit_delay=1.0)
instagram_scraper = InstagramScraper(rate_limit_delay=1.0)

# Initialize Celery (if available)
try:
    from tasks.celery_app import celery
    from tasks.scraping_tasks import scrape_vk_user_task, scrape_vk_posts_task, search_vk_users_task
    from tasks.processing_tasks import extract_metadata_task, extract_text_metadata_task
    CELERY_ENABLED = True
except ImportError:
    CELERY_ENABLED = False
    print("Celery not available. Running in synchronous mode.")


@app.route('/')
def index():
    """Home endpoint with API documentation."""
    endpoints = {
        "/extract/metadata": {
            "method": "POST",
            "description": "Extract EXIF metadata from an image",
            "example": "curl -F 'file=@image.jpg' http://localhost:5000/extract/metadata"
        },
        "/extract/text": {
            "method": "POST",
            "description": "Extract geotags/hashtags from text",
            "example": "curl -X POST -H 'Content-Type: application/json' -d '{\"text\":\"#Moscow @[55.75,37.61]\"}' http://localhost:5000/extract/text"
        },
        # NLP Endpoints
        "/nlp/entities": {
            "method": "POST",
            "description": "Extract entities (people, orgs, locations) from text",
            "example": "curl -X POST -H 'Content-Type: application/json' -d '{\"text\":\"Mistral AI is based in Paris\"}' http://localhost:5000/nlp/entities"
        },
        "/nlp/analyze": {
            "method": "POST",
            "description": "Comprehensive text analysis",
            "example": "curl -X POST -H 'Content-Type: application/json' -d '{\"text\":\"Mistral AI is based in Paris\"}' http://localhost:5000/nlp/analyze"
        },
        # Visualization Endpoints
        "/visualize/timeline": {
            "method": "POST",
            "description": "Generate timeline data from posts",
            "example": "curl -X POST -H 'Content-Type: application/json' -d '{\"posts\": [...]}' http://localhost:5000/visualize/timeline"
        },
        "/visualize/heatmap": {
            "method": "POST",
            "description": "Generate heatmap data from locations",
            "example": "curl -X POST -H 'Content-Type: application/json' -d '{\"posts\": [...]}' http://localhost:5000/visualize/heatmap"
        },
        "/visualize/graph": {
            "method": "POST",
            "description": "Generate graph data from posts and users",
            "example": "curl -X POST -H 'Content-Type: application/json' -d '{\"posts\": [...], \"users\": [...]}' http://localhost:5000/visualize/graph"
        },
        # VK Endpoints
        "/scrape/vk/user": {
            "method": "GET",
            "description": "Scrape a VK user profile (synchronous)",
            "example": "curl http://localhost:5000/scrape/vk/user?username=durov"
        },
        "/scrape/vk/posts": {
            "method": "GET",
            "description": "Scrape VK user posts (synchronous)",
            "example": "curl http://localhost:5000/scrape/vk/posts?username=durov&limit=5"
        },
        "/scrape/vk/search": {
            "method": "GET",
            "description": "Search VK users (synchronous)",
            "example": "curl http://localhost:5000/scrape/vk/search?query=John%20Doe&limit=5"
        },
        # Twitter Endpoints
        "/scrape/twitter/tweets": {
            "method": "GET",
            "description": "Scrape tweets by query (synchronous)",
            "example": "curl http://localhost:5000/scrape/twitter/tweets?query=OSINT&limit=5"
        },
        "/scrape/twitter/user": {
            "method": "GET",
            "description": "Scrape Twitter user profile (synchronous)",
            "example": "curl http://localhost:5000/scrape/twitter/user?username=twitter"
        },
        "/scrape/twitter/trends": {
            "method": "GET",
            "description": "Scrape Twitter trends (synchronous)",
            "example": "curl http://localhost:5000/scrape/twitter/trends?limit=5"
        },
        # Instagram Endpoints
        "/scrape/instagram/user": {
            "method": "GET",
            "description": "Scrape Instagram user profile (synchronous)",
            "example": "curl http://localhost:5000/scrape/instagram/user?username=instagram"
        },
        "/scrape/instagram/posts": {
            "method": "GET",
            "description": "Scrape Instagram user posts (synchronous)",
            "example": "curl http://localhost:5000/scrape/instagram/posts?username=instagram&limit=5"
        },
        "/scrape/instagram/hashtag": {
            "method": "GET",
            "description": "Scrape Instagram posts by hashtag (synchronous)",
            "example": "curl http://localhost:5000/scrape/instagram/hashtag?hashtag=osint&limit=5"
        },
    }
    
    # Add async endpoints if Celery is enabled
    if CELERY_ENABLED:
        endpoints.update({
            "/tasks/scrape/vk/user": {
                "method": "POST",
                "description": "Scrape a VK user profile (asynchronous, returns task ID)",
                "example": "curl -X POST -H 'Content-Type: application/json' -d '{\"username\":\"durov\"}' http://localhost:5000/tasks/scrape/vk/user"
            },
            "/tasks/scrape/vk/posts": {
                "method": "POST",
                "description": "Scrape VK user posts (asynchronous, returns task ID)",
                "example": "curl -X POST -H 'Content-Type: application/json' -d '{\"username\":\"durov\",\"limit\":5}' http://localhost:5000/tasks/scrape/vk/posts"
            },
            "/tasks/status/<task_id>": {
                "method": "GET",
                "description": "Check the status of an async task",
                "example": "curl http://localhost:5000/tasks/status/<task_id>"
            },
        })
    
    return jsonify({
        "name": "OpenLens API",
        "version": "0.2.0",
        "celery_enabled": CELERY_ENABLED,
        "nlp_enabled": nlp_processor is not None,
        "endpoints": endpoints
    })


@app.route('/extract/metadata', methods=['POST'])
@rate_limit(limit=10, window=60)  # 10 requests per minute for metadata extraction
def extract_metadata():
    """
    Extract EXIF metadata from an uploaded image.

    Request:
    - Multipart form with 'file' field containing the image.

    Response:
    - JSON with extracted metadata (GPS, timestamp, device info, etc.).
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        # Secure the filename and save temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Extract metadata
        metadata = metadata_extractor.extract_exif_from_image(filepath)

        # Clean up: remove the uploaded file
        os.remove(filepath)

        return jsonify({
            "success": True,
            "filename": filename,
            "metadata": metadata
        })
    except Exception as e:
        return jsonify({
            "error": f"Failed to process file: {str(e)}"
        }), 500


@app.route('/extract/text', methods=['POST'])
@rate_limit(limit=20, window=60)  # 20 requests per minute for text extraction
def extract_text_metadata():
    """
    Extract geotags, hashtags, and other metadata from text.

    Request:
    - JSON with 'text' field containing the input text.

    Response:
    - JSON with extracted metadata (hashtags, geotags, mentions, URLs).
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text']
    metadata = metadata_extractor.extract_text_metadata(text)

    return jsonify({
        "success": True,
        "text": text,
        "metadata": metadata
    })


# --- NLP Endpoints ---

@app.route('/nlp/entities', methods=['POST'])
@rate_limit(limit=15, window=60)  # 15 requests per minute for NLP entities
def extract_nlp_entities():
    """
    Extract entities (people, organizations, locations, dates) from text.

    Request:
    - JSON with 'text' field containing the input text.

    Response:
    - JSON with extracted entities.
    """
    if nlp_processor is None:
        return jsonify({"error": "NLP processor not available"}), 500

    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text']
    result = nlp_processor.extract_entities(text)

    return jsonify({
        "success": True,
        "text": text,
        "entities": [
            {"text": e.text, "label": e.label, "start": e.start, "end": e.end}
            for e in result.entities
        ],
        "people": result.people,
        "organizations": result.organizations,
        "locations": result.locations,
        "dates": result.dates,
        "keywords": result.keywords,
    })


@app.route('/nlp/analyze', methods=['POST'])
def analyze_text():
    """
    Perform comprehensive text analysis.

    Request:
    - JSON with 'text' field containing the input text.

    Response:
    - JSON with analysis results.
    """
    if nlp_processor is None:
        return jsonify({"error": "NLP processor not available"}), 500

    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text']
    analysis = nlp_processor.analyze_text(text)

    return jsonify({
        "success": True,
        "analysis": analysis
    })


# --- Visualization Endpoints ---

@app.route('/visualize/timeline', methods=['POST'])
def generate_timeline():
    """
    Generate timeline data from a list of posts.

    Request:
    - JSON with 'posts' field containing a list of post dictionaries.

    Response:
    - JSON with timeline events.
    """
    data = request.get_json()
    if not data or 'posts' not in data:
        return jsonify({"error": "No posts provided"}), 400

    try:
        posts = data['posts']
        events = data_processor.create_timeline_from_posts(posts)
        
        timeline_data = []
        for event in events:
            timeline_data.append({
                "id": event.id,
                "title": event.title,
                "start": event.start.isoformat() if event.start else None,
                "end": event.end.isoformat() if event.end else None,
                "description": event.description,
                "category": event.category,
                "icon": event.icon,
                "color": event.color,
            })
        
        return jsonify({
            "success": True,
            "events": timeline_data
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate timeline: {str(e)}"}), 500


@app.route('/visualize/heatmap', methods=['POST'])
def generate_heatmap():
    """
    Generate heatmap data from a list of posts or locations.

    Request:
    - JSON with 'posts' or 'locations' field.

    Response:
    - JSON with heatmap points.
    """
    data = request.get_json()
    if not data or ('posts' not in data and 'locations' not in data):
        return jsonify({"error": "No posts or locations provided"}), 400

    try:
        points = []
        if 'posts' in data:
            points = data_processor.create_heatmap_from_posts(data['posts'])
        elif 'locations' in data:
            points = data_processor.create_heatmap_from_locations(data['locations'])
        
        heatmap_data = []
        for point in points:
            heatmap_data.append({
                "latitude": point.latitude,
                "longitude": point.longitude,
                "intensity": point.intensity,
                "radius": point.radius,
                "color": point.color,
            })
        
        return jsonify({
            "success": True,
            "points": heatmap_data
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate heatmap: {str(e)}"}), 500


@app.route('/visualize/graph', methods=['POST'])
def generate_graph():
    """
    Generate graph data from posts and users.

    Request:
    - JSON with 'posts' and optional 'users' fields.

    Response:
    - JSON with graph nodes and links.
    """
    data = request.get_json()
    if not data or 'posts' not in data:
        return jsonify({"error": "No posts provided"}), 400

    try:
        posts = data['posts']
        users = data.get('users', [])
        
        nodes, links = data_processor.create_graph_from_posts_and_users(posts, users)
        
        graph_data = {
            "nodes": [
                {
                    "id": node.id,
                    "name": node.name,
                    "type": node.type,
                    "group": node.group,
                    "size": node.size,
                    "color": node.color,
                }
                for node in nodes
            ],
            "links": [
                {
                    "source": link.source,
                    "target": link.target,
                    "type": link.type,
                    "value": link.value,
                    "color": link.color,
                }
                for link in links
            ]
        }
        
        return jsonify({
            "success": True,
            "graph": graph_data
        })
    except Exception as e:
        return jsonify({"error": f"Failed to generate graph: {str(e)}"}), 500


# --- Data Normalization Endpoints ---

@app.route('/normalize/text', methods=['POST'])
def normalize_text():
    """
    Normalize text.

    Request:
    - JSON with 'text' field and optional normalization options.

    Response:
    - JSON with normalized text.
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text']
    lowercase = data.get('lowercase', True)
    remove_extra_spaces = data.get('remove_extra_spaces', True)
    remove_special_chars = data.get('remove_special_chars', False)
    remove_punctuation = data.get('remove_punctuation', False)

    normalized = normalizer.normalize_text(
        text,
        lowercase=lowercase,
        remove_extra_spaces=remove_extra_spaces,
        remove_special_chars=remove_special_chars,
        remove_punctuation=remove_punctuation,
    )

    return jsonify({
        "success": True,
        "original": text,
        "normalized": normalized
    })


@app.route('/normalize/phone', methods=['POST'])
def normalize_phone():
    """
    Normalize phone number.

    Request:
    - JSON with 'phone' field.

    Response:
    - JSON with normalized phone number.
    """
    data = request.get_json()
    if not data or 'phone' not in data:
        return jsonify({"error": "No phone provided"}), 400

    phone = data['phone']
    normalized = normalizer.normalize_phone(phone)

    return jsonify({
        "success": True,
        "original": phone,
        "normalized": normalized,
        "valid": normalizer.is_valid_phone(phone)
    })


@app.route('/normalize/email', methods=['POST'])
def normalize_email():
    """
    Normalize email address.

    Request:
    - JSON with 'email' field.

    Response:
    - JSON with normalized email address.
    """
    data = request.get_json()
    if not data or 'email' not in data:
        return jsonify({"error": "No email provided"}), 400

    email = data['email']
    normalized = normalizer.normalize_email(email)

    return jsonify({
        "success": True,
        "original": email,
        "normalized": normalized,
        "valid": normalizer.is_valid_email(email)
    })


@app.route('/normalize/url', methods=['POST'])
def normalize_url():
    """
    Normalize URL.

    Request:
    - JSON with 'url' field.

    Response:
    - JSON with normalized URL.
    """
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "No URL provided"}), 400

    url = data['url']
    normalized = normalizer.normalize_url(url)

    return jsonify({
        "success": True,
        "original": url,
        "normalized": normalized,
        "valid": normalizer.is_valid_url(url)
    })


@app.route('/normalize/batch', methods=['POST'])
def normalize_batch():
    """
    Normalize a batch of data.

    Request:
    - JSON with 'data' field containing a list of items.

    Response:
    - JSON with normalized data.
    """
    data = request.get_json()
    if not data or 'data' not in data:
        return jsonify({"error": "No data provided"}), 400

    try:
        normalized = normalizer.normalize_batch(data['data'])
        return jsonify({
            "success": True,
            "original_count": len(data['data']),
            "normalized_count": len(normalized),
            "data": normalized
        })
    except Exception as e:
        return jsonify({"error": f"Failed to normalize batch: {str(e)}"}), 500


# --- Advanced NLP Endpoints ---

@app.route('/nlp/sentiment', methods=['POST'])
def analyze_sentiment_endpoint():
    """
    Analyze sentiment of a text.

    Request:
    - JSON with 'text' field and optional 'method' ('vader', 'textblob', 'nltk').

    Response:
    - JSON with sentiment analysis results.
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text']
    method = data.get('method', 'vader')

    try:
        result = analyze_sentiment(text, method)
        return jsonify({
            "success": True,
            "text": text,
            "sentiment": result.sentiment,
            "compound": result.compound,
            "positive": result.positive,
            "negative": result.negative,
            "neutral": result.neutral,
            "confidence": result.confidence,
        })
    except Exception as e:
        return jsonify({"error": f"Failed to analyze sentiment: {str(e)}"}), 500


@app.route('/nlp/sentiment/batch', methods=['POST'])
def analyze_sentiment_batch_endpoint():
    """
    Analyze sentiment for a batch of texts.

    Request:
    - JSON with 'texts' field (list of texts) and optional 'method'.

    Response:
    - JSON with sentiment analysis results for each text.
    """
    data = request.get_json()
    if not data or 'texts' not in data:
        return jsonify({"error": "No texts provided"}), 400

    texts = data['texts']
    method = data.get('method', 'vader')

    try:
        results = sentiment_analyzer.analyze_batch(texts)
        return jsonify({
            "success": True,
            "results": [
                {
                    "text": r.text,
                    "sentiment": r.sentiment,
                    "compound": r.compound,
                    "positive": r.positive,
                    "negative": r.negative,
                    "neutral": r.neutral,
                    "confidence": r.confidence,
                }
                for r in results
            ],
            "distribution": sentiment_analyzer.get_sentiment_distribution(texts),
            "average": sentiment_analyzer.get_average_sentiment(texts).to_dict(),
        })
    except Exception as e:
        return jsonify({"error": f"Failed to analyze sentiment batch: {str(e)}"}), 500


@app.route('/nlp/topics', methods=['POST'])
def extract_topics_endpoint():
    """
    Extract topics from documents.

    Request:
    - JSON with 'documents' field (list of texts) and optional 'method' ('lda', 'nmf', 'bertopic') and 'num_topics'.

    Response:
    - JSON with topic modeling results.
    """
    data = request.get_json()
    if not data or 'documents' not in data:
        return jsonify({"error": "No documents provided"}), 400

    documents = data['documents']
    method = data.get('method', 'lda')
    num_topics = data.get('num_topics', 5)

    try:
        results = extract_topics(documents, method, num_topics)
        return jsonify({
            "success": True,
            "method": method,
            "num_topics": num_topics,
            "results": [
                {
                    "text": r.text,
                    "dominant_topic": r.dominant_topic,
                    "dominant_topic_label": r.dominant_topic_label,
                    "topics": r.topics,
                    "topic_distribution": r.topic_distribution,
                }
                for r in results
            ],
        })
    except Exception as e:
        return jsonify({"error": f"Failed to extract topics: {str(e)}"}), 500


@app.route('/nlp/keyphrases', methods=['POST'])
def extract_keyphrases_endpoint():
    """
    Extract keyphrases from text.

    Request:
    - JSON with 'text' field and optional 'method' ('rake', 'yake') and 'num_keyphrases'.

    Response:
    - JSON with keyphrase extraction results.
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "No text provided"}), 400

    text = data['text']
    method = data.get('method', 'rake')
    num_keyphrases = data.get('num_keyphrases', 10)

    try:
        result = extract_keyphrases(text, method, num_keyphrases)
        return jsonify({
            "success": True,
            "text": text,
            "keyphrases": [
                {"phrase": kp[0], "score": kp[1]}
                for kp in result.keyphrases
            ],
            "top_keyphrases": result.top_keyphrases,
        })
    except Exception as e:
        return jsonify({"error": f"Failed to extract keyphrases: {str(e)}"}), 500


# --- Export Endpoints ---

@app.route('/export/posts/csv', methods=['GET'])
@auth_required()
def export_posts_csv():
    """
    Export posts to CSV format.

    Query Parameters:
    - platform: Filter by platform.
    - limit: Maximum number of posts (default: 100).

    Response:
    - CSV file download.
    """
    platform = request.args.get('platform')
    limit = int(request.args.get('limit', 100))
    
    try:
        posts = db_manager.get_posts(platform, limit)
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "platform": post.platform,
                "content": post.content,
                "author_name": post.author_name,
                "timestamp": post.timestamp.isoformat() if post.timestamp else None,
                "likes": post.likes,
                "reposts": post.reposts,
                "views": post.views,
                "comments": post.comments,
            })
        
        csv_content = exporter.export_posts_to_csv(posts_data)
        
        # Return as downloadable file
        from flask import make_response
        response = make_response(csv_content)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = 'attachment; filename=posts.csv'
        return response
    except Exception as e:
        return jsonify({"error": f"Failed to export posts: {str(e)}"}), 500


@app.route('/export/posts/json', methods=['GET'])
@auth_required()
def export_posts_json():
    """
    Export posts to JSON format.

    Query Parameters:
    - platform: Filter by platform.
    - limit: Maximum number of posts (default: 100).

    Response:
    - JSON file download.
    """
    platform = request.args.get('platform')
    limit = int(request.args.get('limit', 100))
    
    try:
        posts = db_manager.get_posts(platform, limit)
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "platform": post.platform,
                "content": post.content,
                "author_name": post.author_name,
                "timestamp": post.timestamp.isoformat() if post.timestamp else None,
                "likes": post.likes,
                "reposts": post.reposts,
                "views": post.views,
                "comments": post.comments,
            })
        
        json_content = exporter.export_posts_to_json(posts_data)
        
        # Return as downloadable file
        from flask import make_response
        response = make_response(json_content)
        response.headers['Content-Type'] = 'application/json'
        response.headers['Content-Disposition'] = 'attachment; filename=posts.json'
        return response
    except Exception as e:
        return jsonify({"error": f"Failed to export posts: {str(e)}"}), 500


@app.route('/export/posts/pdf', methods=['GET'])
@auth_required()
def export_posts_pdf():
    """
    Export posts to PDF format.

    Query Parameters:
    - platform: Filter by platform.
    - limit: Maximum number of posts (default: 100).

    Response:
    - PDF file download.
    """
    platform = request.args.get('platform')
    limit = int(request.args.get('limit', 100))
    
    try:
        posts = db_manager.get_posts(platform, limit)
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "platform": post.platform,
                "content": post.content,
                "author_name": post.author_name,
                "timestamp": post.timestamp.isoformat() if post.timestamp else None,
                "likes": post.likes,
                "reposts": post.reposts,
                "views": post.views,
                "comments": post.comments,
            })
        
        pdf_content = exporter.export_to_pdf(posts_data, title='OpenLens Posts Report')
        
        if isinstance(pdf_content, str):
            return jsonify({"error": pdf_content}), 500
        
        # Return as downloadable file
        from flask import make_response
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=posts.pdf'
        return response
    except Exception as e:
        return jsonify({"error": f"Failed to export posts: {str(e)}"}), 500


@app.route('/export/report', methods=['POST'])
@auth_required()
def export_report():
    """
    Export a custom report.

    Request:
    - JSON with report data and format.

    Response:
    - File download in specified format.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    report_data = data.get('data', {})
    format = data.get('format', 'json')  # 'csv', 'json', 'pdf'
    title = data.get('title', 'OpenLens Report')
    
    try:
        if format == 'csv':
            # For CSV, we need to flatten the data
            csv_content = exporter.export_to_csv(report_data)
            from flask import make_response
            response = make_response(csv_content)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename="{title}.csv"'
            return response
        elif format == 'json':
            json_content = exporter.export_to_json(report_data)
            from flask import make_response
            response = make_response(json_content)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = f'attachment; filename="{title}.json"'
            return response
        elif format == 'pdf':
            pdf_content = exporter.export_to_pdf(report_data, title=title)
            if isinstance(pdf_content, str):
                return jsonify({"error": pdf_content}), 500
            from flask import make_response
            response = make_response(pdf_content)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="{title}.pdf"'
            return response
        else:
            return jsonify({"error": f"Unsupported format: {format}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to export report: {str(e)}"}), 500


# --- Authentication Endpoints ---

@app.route('/auth/register', methods=['POST'])
def register():
    """
    Register a new user.

    Request:
    - JSON with username, email, password, and optional full_name.

    Response:
    - JSON with user data and tokens.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name', '')
    
    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required"}), 400
    
    # Check if user already exists
    session = db_manager.db.get_session()
    try:
        from sqlalchemy import or_
        existing_user = session.query(User).filter(
            or_(
                User.username == username,
                User.email == email
            )
        ).first()
        
        if existing_user:
            return jsonify({"error": "Username or email already exists"}), 400
        
        # Create new user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=RoleType.USER,
        )
        user.set_password(password)
        session.add(user)
        session.commit()
        
        # Generate tokens
        access_token = create_access_token(user.id, user.username, user.role.value)
        refresh_token = create_refresh_token(user.id)
        
        return jsonify({
            "success": True,
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        })
    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Failed to register user: {str(e)}"}), 500
    finally:
        session.close()


@app.route('/auth/login', methods=['POST'])
def login():
    """
    Login a user.

    Request:
    - JSON with username/email and password.

    Response:
    - JSON with user data and tokens.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not password:
        return jsonify({"error": "Password is required"}), 400
    
    if not username and not email:
        return jsonify({"error": "Username or email is required"}), 400
    
    session = db_manager.db.get_session()
    try:
        from sqlalchemy import or_
        user = session.query(User).filter(
            or_(
                User.username == username if username else False,
                User.email == email if email else False
            )
        ).first()
        
        if not user:
            return jsonify({"error": "Invalid username/email or password"}), 401
        
        if not user.check_password(password):
            return jsonify({"error": "Invalid username/email or password"}), 401
        
        if not user.is_active:
            return jsonify({"error": "Account is disabled"}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        session.commit()
        
        # Generate tokens
        access_token = create_access_token(user.id, user.username, user.role.value)
        refresh_token = create_refresh_token(user.id)
        
        return jsonify({
            "success": True,
            "user": user.to_dict(),
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        })
    except Exception as e:
        session.rollback()
        return jsonify({"error": f"Failed to login: {str(e)}"}), 500
    finally:
        session.close()


@app.route('/auth/refresh', methods=['POST'])
def refresh():
    """
    Refresh access token using refresh token.

    Request:
    - JSON with refresh_token.

    Response:
    - JSON with new access token.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    refresh_token = data.get('refresh_token')
    if not refresh_token:
        return jsonify({"error": "Refresh token is required"}), 400
    
    # Verify refresh token
    payload = verify_token(refresh_token)
    if not payload or payload.get('type') != 'refresh':
        return jsonify({"error": "Invalid refresh token"}), 401
    
    user_id = payload.get('sub')
    
    # Get user from database
    session = db_manager.db.get_session()
    try:
        user = session.query(User).filter(User.id == int(user_id)).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Generate new tokens
        access_token = create_access_token(user.id, user.username, user.role.value)
        new_refresh_token = create_refresh_token(user.id)
        
        return jsonify({
            "success": True,
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "Bearer",
            "expires_in": AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        })
    except Exception as e:
        return jsonify({"error": f"Failed to refresh token: {str(e)}"}), 500
    finally:
        session.close()


@app.route('/auth/me', methods=['GET'])
@auth_required()
def get_current_user_profile():
    """
    Get current user profile.

    Response:
    - JSON with current user data.
    """
    user_payload = get_current_user()
    if not user_payload:
        return jsonify({"error": "Not authenticated"}), 401
    
    user_id = user_payload.get('sub')
    
    session = db_manager.db.get_session()
    try:
        user = session.query(User).filter(User.id == int(user_id)).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "success": True,
            "user": user.to_dict()
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get user profile: {str(e)}"}), 500
    finally:
        session.close()


@app.route('/auth/logout', methods=['POST'])
@auth_required()
def logout():
    """
    Logout current user (invalidate refresh token).

    Response:
    - JSON with success message.
    """
    user_payload = get_current_user()
    if not user_payload:
        return jsonify({"error": "Not authenticated"}), 401
    
    # In a real implementation, we would blacklist the refresh token
    # For now, just return success
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })


# --- Database Endpoints ---

@app.route('/db/posts', methods=['GET'])
def get_posts():
    """
    Get posts from PostgreSQL database.

    Query Parameters:
    - platform: Filter by platform (vk, twitter, instagram, telegram).
    - limit: Maximum number of posts (default: 10).
    - offset: Offset for pagination (default: 0).

    Response:
    - JSON with list of posts.
    """
    platform = request.args.get('platform')
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))

    try:
        posts = db_manager.get_posts(platform, limit, offset)
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "platform": post.platform,
                "content": post.content,
                "author_name": post.author_name,
                "timestamp": post.timestamp.isoformat() if post.timestamp else None,
                "likes": post.likes,
                "reposts": post.reposts,
                "views": post.views,
                "comments": post.comments,
            })
        return jsonify({
            "success": True,
            "posts": posts_data,
            "count": len(posts_data)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get posts: {str(e)}"}), 500


@app.route('/db/posts/<post_id>', methods=['GET'])
def get_post(post_id: str):
    """
    Get a specific post from PostgreSQL database.

    Args:
        post_id: Post ID.

    Response:
    - JSON with post data.
    """
    try:
        post = db_manager.get_post_by_id(post_id)
        if post:
            return jsonify({
                "success": True,
                "post": {
                    "id": post.id,
                    "platform": post.platform,
                    "content": post.content,
                    "author_name": post.author_name,
                    "timestamp": post.timestamp.isoformat() if post.timestamp else None,
                    "likes": post.likes,
                    "reposts": post.reposts,
                    "views": post.views,
                    "comments": post.comments,
                }
            })
        else:
            return jsonify({"error": "Post not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to get post: {str(e)}"}), 500


@app.route('/db/search', methods=['GET'])
def search_posts():
    """
    Search posts in PostgreSQL database.

    Query Parameters:
    - q: Search query.
    - limit: Maximum number of results (default: 10).

    Response:
    - JSON with list of matching posts.
    """
    query = request.args.get('q')
    limit = int(request.args.get('limit', 10))

    if not query:
        return jsonify({"error": "No search query provided"}), 400

    try:
        posts = db_manager.search_posts(query, limit)
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "platform": post.platform,
                "content": post.content,
                "author_name": post.author_name,
                "timestamp": post.timestamp.isoformat() if post.timestamp else None,
            })
        return jsonify({
            "success": True,
            "query": query,
            "posts": posts_data,
            "count": len(posts_data)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to search posts: {str(e)}"}), 500


@app.route('/db/save/post', methods=['POST'])
def save_post():
    """
    Save a post to PostgreSQL database.

    Request:
    - JSON with post data.

    Response:
    - JSON with saved post data.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    platform = data.get('platform', 'unknown')
    
    try:
        post = db_manager.save_post(data, platform)
        if post:
            return jsonify({
                "success": True,
                "post_id": post.id,
                "message": "Post saved successfully"
            })
        else:
            return jsonify({"error": "Failed to save post"}), 500
    except Exception as e:
        return jsonify({"error": f"Failed to save post: {str(e)}"}), 500


@app.route('/graph/network', methods=['GET'])
def get_network_graph():
    """
    Get a network graph from Neo4j.

    Query Parameters:
    - center_id: Center node ID (user or post).
    - max_depth: Maximum depth of connections (default: 2).
    - limit: Maximum number of nodes (default: 50).

    Response:
    - JSON with nodes and relationships.
    """
    center_id = request.args.get('center_id')
    max_depth = int(request.args.get('max_depth', 2))
    limit = int(request.args.get('limit', 50))

    if not center_id:
        return jsonify({"error": "No center_id provided"}), 400

    try:
        neo4j_db = get_neo4j_db()
        graph = neo4j_db.get_network_graph(center_id, max_depth, limit)
        return jsonify({
            "success": True,
            "graph": graph
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get network graph: {str(e)}"}), 500


@app.route('/graph/trending/hashtags', methods=['GET'])
def get_trending_hashtags():
    """
    Get trending hashtags from Neo4j.

    Query Parameters:
    - limit: Maximum number of hashtags (default: 10).

    Response:
    - JSON with list of trending hashtags.
    """
    limit = int(request.args.get('limit', 10))

    try:
        neo4j_db = get_neo4j_db()
        hashtags = neo4j_db.get_trending_hashtags(limit)
        return jsonify({
            "success": True,
            "hashtags": hashtags
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get trending hashtags: {str(e)}"}), 500


@app.route('/graph/popular/locations', methods=['GET'])
def get_popular_locations():
    """
    Get popular locations from Neo4j.

    Query Parameters:
    - limit: Maximum number of locations (default: 10).

    Response:
    - JSON with list of popular locations.
    """
    limit = int(request.args.get('limit', 10))

    try:
        neo4j_db = get_neo4j_db()
        locations = neo4j_db.get_popular_locations(limit)
        return jsonify({
            "success": True,
            "locations": locations
        })
    except Exception as e:
        return jsonify({"error": f"Failed to get popular locations: {str(e)}"}), 500


# --- Monitoring Endpoints ---

@app.route('/health', methods=['GET'])
def get_health():
    """
    Get system health status.

    Response:
    - JSON with health status of all components.
    """
    try:
        health = health_check()
        return jsonify(health)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500


@app.route('/health/database/<db_type>', methods=['GET'])
def check_database_health(db_type: str):
    """
    Check a specific database health.

    Args:
        db_type: Database type ('postgres', 'neo4j', 'redis').

    Response:
    - JSON with database health status.
    """
    try:
        result = check_database(db_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500


@app.route('/health/system', methods=['GET'])
def check_system_health():
    """
    Check system health.

    Response:
    - JSON with system health status.
    """
    try:
        result = check_system()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500


@app.route('/analytics', methods=['GET'])
def get_analytics():
    """
    Get API usage analytics.

    Query Parameters:
    - time_range: Time range ('all', 'hour', 'day', 'week', 'month').

    Response:
    - JSON with API usage statistics.
    """
    time_range = request.args.get('time_range', 'all')
    
    try:
        analytics = get_analytics()
        stats = analytics.get_stats(time_range)
        return jsonify(stats)
    except Exception as e:
        return jsonify({
            "error": str(e),
        }), 500


@app.route('/analytics/endpoints', methods=['GET'])
def get_endpoint_analytics():
    """
    Get endpoint-specific analytics.

    Query Parameters:
    - endpoint: Endpoint path (optional).
    - method: HTTP method (optional).

    Response:
    - JSON with endpoint statistics.
    """
    endpoint = request.args.get('endpoint')
    method = request.args.get('method')
    
    try:
        analytics = get_analytics()
        stats = analytics.get_endpoint_stats(endpoint, method)
        return jsonify(stats)
    except Exception as e:
        return jsonify({
            "error": str(e),
        }), 500


@app.route('/analytics/users', methods=['GET'])
def get_user_analytics():
    """
    Get user-specific analytics.

    Query Parameters:
    - user_id: User ID (optional).

    Response:
    - JSON with user statistics.
    """
    user_id = request.args.get('user_id')
    
    try:
        analytics = get_analytics()
        stats = analytics.get_user_stats(user_id)
        return jsonify(stats)
    except Exception as e:
        return jsonify({
            "error": str(e),
        }), 500


# --- VK Scraper Endpoints ---

@app.route('/scrape/vk/user', methods=['GET'])
@rate_limit(limit=5, window=60)  # 5 requests per minute for VK user scraping
def scrape_vk_user():
    """
    Scrape a VK user profile (synchronous).

    Query Parameters:
    - username: VK username or user ID (e.g., "durov").

    Response:
    - JSON with user profile data.
    """
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "No username provided"}), 400

    try:
        user = vk_scraper.scrape_user_profile(username)
        if user:
            return jsonify({
                "success": True,
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "username": user.username,
                    "bio": user.bio,
                    "city": user.city,
                    "country": user.country,
                    "birthday": user.birthday,
                    "followers": user.friends,
                }
            })
        else:
            return jsonify({"error": "User not found or scraping failed"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to scrape user: {str(e)}"}), 500


@app.route('/scrape/vk/posts', methods=['GET'])
def scrape_vk_posts():
    """
    Scrape recent posts from a VK user profile (synchronous).

    Query Parameters:
    - username: VK username or user ID.
    - limit: Maximum number of posts to scrape (default: 10).
    - page: Page number for pagination (default: 1).
    - per_page: Number of posts per page (default: 10).
    - since: Filter posts since this date (ISO format).
    - until: Filter posts until this date (ISO format).

    Response:
    - JSON with list of posts and pagination info.
    """
    username = request.args.get('username')
    limit = int(request.args.get('limit', 10))
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    since = request.args.get('since')
    until = request.args.get('until')

    if not username:
        return jsonify({"error": "No username provided"}), 400

    try:
        # Calculate offset for pagination
        offset = (page - 1) * per_page
        
        # Scrape posts with limit (for now, we'll scrape all and paginate in memory)
        all_posts = vk_scraper.scrape_user_posts(username, limit=limit * page)
        
        # Apply pagination
        paginated_posts = all_posts[offset:offset + per_page]
        
        # Apply date filters if provided
        if since or until:
            from datetime import datetime
            filtered_posts = []
            for post in paginated_posts:
                try:
                    post_date = datetime.fromisoformat(post.timestamp.replace('Z', '+00:00')) if isinstance(post.timestamp, str) else post.timestamp
                    if since:
                        since_date = datetime.fromisoformat(since.replace('Z', '+00:00'))
                        if post_date < since_date:
                            continue
                    if until:
                        until_date = datetime.fromisoformat(until.replace('Z', '+00:00'))
                        if post_date > until_date:
                            continue
                    filtered_posts.append(post)
                except:
                    filtered_posts.append(post)
            paginated_posts = filtered_posts
        
        posts_data = []
        for post in paginated_posts:
            posts_data.append({
                "id": post.id,
                "author_name": post.author_name,
                "content": post.content,
                "timestamp": post.timestamp,
                "likes": post.likes,
                "reposts": post.reposts,
                "views": post.views,
                "comments": post.comments,
                "attachments": post.attachments,
            })
        
        # Calculate pagination info
        total_posts = len(all_posts)
        total_pages = (total_posts + per_page - 1) // per_page
        
        return jsonify({
            "success": True,
            "username": username,
            "posts": posts_data,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total_posts": total_posts,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            }
        })
    except Exception as e:
        return jsonify({"error": f"Failed to scrape posts: {str(e)}"}), 500


@app.route('/scrape/vk/search', methods=['GET'])
def scrape_vk_search():
    """
    Search for VK users by name or keyword (synchronous).

    Query Parameters:
    - query: Search query (e.g., "John Doe").
    - limit: Maximum number of results (default: 10).

    Response:
    - JSON with list of users.
    """
    query = request.args.get('query')
    limit = int(request.args.get('limit', 10))

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        users = vk_scraper.search_users(query, limit=limit)
        return jsonify({
            "success": True,
            "query": query,
            "users": users
        })
    except Exception as e:
        return jsonify({"error": f"Failed to search users: {str(e)}"}), 500


# --- Twitter Scraper Endpoints ---

@app.route('/scrape/twitter/tweets', methods=['GET'])
def scrape_twitter_tweets():
    """
    Scrape tweets by query (synchronous).

    Query Parameters:
    - query: Search query (e.g., "OSINT", "from:username").
    - limit: Maximum number of tweets to scrape (default: 10).

    Response:
    - JSON with list of tweets.
    """
    query = request.args.get('query')
    limit = int(request.args.get('limit', 10))

    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        tweets = twitter_scraper.scrape_tweets(query, limit=limit)
        tweets_data = []
        for tweet in tweets:
            tweets_data.append({
                "id": tweet.id,
                "content": tweet.content,
                "username": tweet.username,
                "user_id": tweet.user_id,
                "display_name": tweet.display_name,
                "timestamp": tweet.timestamp.isoformat() if tweet.timestamp else None,
                "likes": tweet.likes,
                "retweets": tweet.retweets,
                "replies": tweet.replies,
                "quotes": tweet.quotes,
                "views": tweet.views,
                "hashtags": tweet.hashtags,
                "mentions": tweet.mentions,
                "urls": tweet.urls,
                "media": tweet.media,
                "geotag": tweet.geotag,
            })
        return jsonify({
            "success": True,
            "query": query,
            "tweets": tweets_data
        })
    except Exception as e:
        return jsonify({"error": f"Failed to scrape tweets: {str(e)}"}), 500


@app.route('/scrape/twitter/user', methods=['GET'])
def scrape_twitter_user():
    """
    Scrape Twitter user profile (synchronous).

    Query Parameters:
    - username: Twitter username (without @).

    Response:
    - JSON with user profile data.
    """
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "No username provided"}), 400

    try:
        user = twitter_scraper.scrape_user_profile(username)
        if user:
            return jsonify({
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "display_name": user.display_name,
                    "bio": user.bio,
                    "location": user.location,
                    "url": user.url,
                    "join_date": user.join_date.isoformat() if user.join_date else None,
                    "followers": user.followers,
                    "following": user.following,
                    "tweets": user.tweets,
                    "likes": user.likes,
                    "verified": user.verified,
                    "profile_image": user.profile_image,
                    "banner_image": user.banner_image,
                }
            })
        else:
            return jsonify({"error": "User not found or scraping failed"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to scrape user: {str(e)}"}), 500


@app.route('/scrape/twitter/trends', methods=['GET'])
def scrape_twitter_trends():
    """
    Scrape Twitter trends (synchronous).

    Query Parameters:
    - location: WOIED (Where On Earth ID) for the location (default: 23424977 for worldwide).
    - limit: Maximum number of trends to return (default: 10).

    Response:
    - JSON with list of trends.
    """
    location = int(request.args.get('location', 23424977))
    limit = int(request.args.get('limit', 10))

    try:
        trends = twitter_scraper.scrape_trends(location=location, limit=limit)
        return jsonify({
            "success": True,
            "location": location,
            "trends": trends
        })
    except Exception as e:
        return jsonify({"error": f"Failed to scrape trends: {str(e)}"}), 500


# --- Instagram Scraper Endpoints ---

@app.route('/scrape/instagram/user', methods=['GET'])
def scrape_instagram_user():
    """
    Scrape Instagram user profile (synchronous).

    Query Parameters:
    - username: Instagram username.

    Response:
    - JSON with user profile data.
    """
    username = request.args.get('username')
    if not username:
        return jsonify({"error": "No username provided"}), 400

    try:
        user = instagram_scraper.scrape_user_profile(username)
        if user:
            return jsonify({
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "bio": user.bio,
                    "url": user.url,
                    "followers": user.followers,
                    "following": user.following,
                    "posts": user.posts,
                    "is_verified": user.is_verified,
                    "is_private": user.is_private,
                    "profile_pic_url": user.profile_pic_url,
                    "website": user.website,
                    "business_category": user.business_category,
                }
            })
        else:
            return jsonify({"error": "User not found or scraping failed"}), 404
    except Exception as e:
        return jsonify({"error": f"Failed to scrape user: {str(e)}"}), 500


@app.route('/scrape/instagram/posts', methods=['GET'])
def scrape_instagram_posts():
    """
    Scrape Instagram user posts (synchronous).

    Query Parameters:
    - username: Instagram username.
    - limit: Maximum number of posts to scrape (default: 10).

    Response:
    - JSON with list of posts.
    """
    username = request.args.get('username')
    limit = int(request.args.get('limit', 10))

    if not username:
        return jsonify({"error": "No username provided"}), 400

    try:
        posts = instagram_scraper.scrape_user_posts(username, limit=limit)
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "shortcode": post.shortcode,
                "caption": post.caption,
                "timestamp": post.timestamp.isoformat() if post.timestamp else None,
                "likes": post.likes,
                "comments": post.comments,
                "views": post.views,
                "url": post.url,
                "media_url": post.media_url,
                "media_type": post.media_type,
                "hashtags": post.hashtags,
                "mentions": post.mentions,
                "location": post.location,
                "geotag": post.geotag,
            })
        return jsonify({
            "success": True,
            "username": username,
            "posts": posts_data
        })
    except Exception as e:
        return jsonify({"error": f"Failed to scrape posts: {str(e)}"}), 500


@app.route('/scrape/instagram/hashtag', methods=['GET'])
def scrape_instagram_hashtag():
    """
    Scrape Instagram posts by hashtag (synchronous).

    Query Parameters:
    - hashtag: Instagram hashtag (without #).
    - limit: Maximum number of posts to scrape (default: 10).

    Response:
    - JSON with list of posts.
    """
    hashtag = request.args.get('hashtag')
    limit = int(request.args.get('limit', 10))

    if not hashtag:
        return jsonify({"error": "No hashtag provided"}), 400

    try:
        posts = instagram_scraper.scrape_hashtag_posts(hashtag, limit=limit)
        posts_data = []
        for post in posts:
            posts_data.append({
                "id": post.id,
                "shortcode": post.shortcode,
                "caption": post.caption,
                "timestamp": post.timestamp.isoformat() if post.timestamp else None,
                "likes": post.likes,
                "comments": post.comments,
                "views": post.views,
                "url": post.url,
                "media_url": post.media_url,
                "media_type": post.media_type,
                "hashtags": post.hashtags,
                "mentions": post.mentions,
                "location": post.location,
                "geotag": post.geotag,
            })
        return jsonify({
            "success": True,
            "hashtag": hashtag,
            "posts": posts_data
        })
    except Exception as e:
        return jsonify({"error": f"Failed to scrape hashtag posts: {str(e)}"}), 500


# --- Async Task Endpoints (Celery) ---

@app.route('/tasks/scrape/vk/user', methods=['POST'])
def scrape_vk_user_async():
    """
    Scrape a VK user profile asynchronously (Celery task).

    Request:
    - JSON with 'username' field.

    Response:
    - JSON with task ID (for checking status later).
    """
    if not CELERY_ENABLED:
        return jsonify({"error": "Celery not enabled"}), 500

    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({"error": "No username provided"}), 400

    username = data['username']
    task = scrape_vk_user_task.delay(username)
    return jsonify({
        "success": True,
        "task_id": task.id,
        "status": "pending"
    })


@app.route('/tasks/scrape/vk/posts', methods=['POST'])
def scrape_vk_posts_async():
    """
    Scrape VK user posts asynchronously (Celery task).

    Request:
    - JSON with 'username' and optional 'limit' fields.

    Response:
    - JSON with task ID (for checking status later).
    """
    if not CELERY_ENABLED:
        return jsonify({"error": "Celery not enabled"}), 500

    data = request.get_json()
    if not data or 'username' not in data:
        return jsonify({"error": "No username provided"}), 400

    username = data['username']
    limit = data.get('limit', 10)
    task = scrape_vk_posts_task.delay(username, limit)
    return jsonify({
        "success": True,
        "task_id": task.id,
        "status": "pending"
    })


@app.route('/tasks/status/<task_id>', methods=['GET'])
def get_task_status(task_id: str):
    """
    Check the status of an async Celery task.

    Args:
        task_id: Celery task ID.

    Response:
    - JSON with task status and result (if completed).
    """
    if not CELERY_ENABLED:
        return jsonify({"error": "Celery not enabled"}), 500

    from celery.result import AsyncResult
    task_result = AsyncResult(task_id, app=celery)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
    }
    
    if task_result.status == "SUCCESS":
        response["result"] = task_result.result
    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)
    
    return jsonify(response)


if __name__ == '__main__':
    # Run with SocketIO
    from websocket.socket_server import get_socketio
    socketio = get_socketio()
    if socketio:
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', port=5000, debug=True)
