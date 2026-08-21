"""
PostgreSQL Database Integration for OpenLens

Provides SQLAlchemy-based database connection and ORM models for:
- Users
- Posts
- Metadata
- Attachments
- Geotags
- Hashtags
- Mentions
- Relationships
- Scraping Jobs
- API Logs

Dependencies:
- SQLAlchemy: ORM
- psycopg2-binary: PostgreSQL adapter
- python-dotenv: Environment variables
"""

import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SQLAlchemy base
Base = declarative_base()

# Database connection
class Database:
    """
    Manages PostgreSQL database connections and sessions.
    """
    
    def __init__(self):
        """Initialize database connection."""
        self.engine = None
        self.Session = None
        self._initialize()
    
    def _initialize(self):
        """Initialize database engine and session factory."""
        db_url = os.getenv('POSTGRES_URL', 'postgresql://postgres:postgres@localhost:5432/openlens')
        
        try:
            self.engine = create_engine(
                db_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False  # Set to True for debugging
            )
            self.Session = scoped_session(sessionmaker(bind=self.engine))
            print(f"Connected to PostgreSQL at {db_url}")
        except Exception as e:
            print(f"Failed to connect to PostgreSQL: {e}")
            self.engine = None
            self.Session = None
    
    def get_session(self):
        """
        Get a database session.
        
        Returns:
            SQLAlchemy session object.
        """
        if self.Session is None:
            raise RuntimeError("Database not initialized")
        return self.Session()
    
    def close(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
        if self.Session:
            self.Session.remove()


# Initialize database
_db = Database()


def get_db():
    """
    Get the database instance.
    
    Returns:
        Database instance.
    """
    return _db


def get_session():
    """
    Get a database session.
    
    Returns:
        SQLAlchemy session.
    """
    return _db.get_session()


# --- Models ---

class User(Base):
    """
    User model for storing user accounts.
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    bio = Column(Text)
    profile_image = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    posts = relationship('Post', back_populates='author')
    scraping_jobs = relationship('ScrapingJob', back_populates='user')
    api_logs = relationship('APILog', back_populates='user')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Post(Base):
    """
    Post model for storing scraped posts.
    """
    __tablename__ = 'posts'
    
    id = Column(String(100), primary_key=True)
    platform = Column(String(20), nullable=False, index=True)  # 'vk', 'twitter', 'instagram', 'telegram'
    platform_id = Column(String(100), nullable=False)  # Platform-specific ID
    content = Column(Text)
    author_id = Column(Integer, ForeignKey('users.id'))
    author_name = Column(String(100))
    author_username = Column(String(100))
    timestamp = Column(DateTime, index=True)
    likes = Column(Integer, default=0)
    reposts = Column(Integer, default=0)
    views = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    url = Column(String(500))
    language = Column(String(10))
    sentiment_score = Column(Float)
    sentiment_label = Column(String(20))
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = relationship('User', back_populates='posts')
    metadata = relationship('Metadata', back_populates='post', uselist=False)
    geotags = relationship('Geotag', back_populates='post')
    hashtags = relationship('Hashtag', back_populates='post')
    mentions = relationship('Mention', back_populates='post')
    attachments = relationship('Attachment', back_populates='post')
    
    __table_args__ = (
        Index('idx_post_platform_timestamp', 'platform', 'timestamp'),
    )
    
    def __repr__(self):
        return f'<Post {self.platform}/{self.id}>'


class Metadata(Base):
    """
    Metadata model for storing EXIF and other metadata.
    """
    __tablename__ = 'metadata'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(String(100), ForeignKey('posts.id'), unique=True, nullable=False)
    
    # EXIF data
    camera_make = Column(String(100))
    camera_model = Column(String(100))
    focal_length = Column(String(50))
    aperture = Column(String(50))
    iso = Column(Integer)
    exposure_time = Column(String(50))
    
    # GPS data
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)
    gps_altitude = Column(Float)
    gps_timestamp = Column(DateTime)
    
    # Timestamp data
    created_at = Column(DateTime)
    modified_at = Column(DateTime)
    
    # Device info
    device_type = Column(String(50))
    software = Column(String(100))
    
    # File info
    file_size = Column(Integer)
    file_type = Column(String(50))
    file_hash = Column(String(100))
    
    # Relationships
    post = relationship('Post', back_populates='metadata')
    
    def __repr__(self):
        return f'<Metadata {self.post_id}>'


class Geotag(Base):
    """
    Geotag model for storing location data.
    """
    __tablename__ = 'geotags'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(String(100), ForeignKey('posts.id'), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float)
    accuracy = Column(Float)
    place_name = Column(String(255))
    city = Column(String(100))
    region = Column(String(100))
    country = Column(String(100))
    country_code = Column(String(10))
    address = Column(Text)
    
    # Relationships
    post = relationship('Post', back_populates='geotags')
    
    __table_args__ = (
        Index('idx_geotag_lat_lon', 'latitude', 'longitude'),
    )
    
    def __repr__(self):
        return f'<Geotag {self.latitude}, {self.longitude}>'


class Hashtag(Base):
    """
    Hashtag model for storing hashtags.
    """
    __tablename__ = 'hashtags'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(String(100), ForeignKey('posts.id'), nullable=False)
    tag = Column(String(100), nullable=False, index=True)
    normalized_tag = Column(String(100), nullable=False, index=True)
    count = Column(Integer, default=1)
    
    # Relationships
    post = relationship('Post', back_populates='hashtags')
    
    __table_args__ = (
        Index('idx_hashtag_tag', 'tag'),
        Index('idx_hashtag_normalized', 'normalized_tag'),
    )
    
    def __repr__(self):
        return f'<Hashtag #{self.tag}>'


class Mention(Base):
    """
    Mention model for storing user mentions.
    """
    __tablename__ = 'mentions'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(String(100), ForeignKey('posts.id'), nullable=False)
    username = Column(String(100), nullable=False, index=True)
    display_name = Column(String(100))
    platform = Column(String(20))  # 'vk', 'twitter', 'instagram', 'telegram'
    platform_id = Column(String(100))
    
    # Relationships
    post = relationship('Post', back_populates='mentions')
    
    __table_args__ = (
        Index('idx_mention_username', 'username'),
    )
    
    def __repr__(self):
        return f'<Mention @{self.username}>'


class Attachment(Base):
    """
    Attachment model for storing post attachments (images, videos, links).
    """
    __tablename__ = 'attachments'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(String(100), ForeignKey('posts.id'), nullable=False)
    attachment_type = Column(String(20), nullable=False)  # 'image', 'video', 'audio', 'link', 'document'
    url = Column(String(500), nullable=False)
    thumbnail_url = Column(String(500))
    title = Column(String(255))
    description = Column(Text)
    file_size = Column(Integer)
    file_type = Column(String(50))
    width = Column(Integer)
    height = Column(Integer)
    duration = Column(Integer)  # For videos/audio
    
    # Relationships
    post = relationship('Post', back_populates='attachments')
    
    def __repr__(self):
        return f'<Attachment {self.attachment_type}: {self.url}>'


class ScrapingJob(Base):
    """
    ScrapingJob model for tracking async scraping tasks.
    """
    __tablename__ = 'scraping_jobs'
    
    id = Column(String(100), primary_key=True)  # Celery task ID
    user_id = Column(Integer, ForeignKey('users.id'))
    platform = Column(String(20), nullable=False, index=True)
    target = Column(String(255), nullable=False)  # Username, hashtag, etc.
    job_type = Column(String(50), nullable=False)  # 'user_profile', 'posts', 'search', etc.
    status = Column(String(20), default='pending', index=True)  # 'pending', 'running', 'completed', 'failed'
    parameters = Column(JSON, default={})
    result_count = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='scraping_jobs')
    
    __table_args__ = (
        Index('idx_scraping_job_status', 'status'),
        Index('idx_scraping_job_user', 'user_id'),
    )
    
    def __repr__(self):
        return f'<ScrapingJob {self.id}: {self.status}>'


class APILog(Base):
    """
    APILog model for tracking API usage.
    """
    __tablename__ = 'api_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    endpoint = Column(String(255), nullable=False, index=True)
    method = Column(String(10), nullable=False, index=True)
    status_code = Column(Integer, nullable=False, index=True)
    request_data = Column(JSON)
    response_data = Column(JSON)
    ip_address = Column(String(50), index=True)
    user_agent = Column(String(500))
    duration_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship('User', back_populates='api_logs')
    
    __table_args__ = (
        Index('idx_api_log_created', 'created_at'),
        Index('idx_api_log_endpoint', 'endpoint'),
    )
    
    def __repr__(self):
        return f'<APILog {self.endpoint} {self.method} {self.status_code}>'


class Entity(Base):
    """
    Entity model for storing NLP-extracted entities.
    """
    __tablename__ = 'entities'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(String(100), ForeignKey('posts.id'))
    entity_type = Column(String(20), nullable=False, index=True)  # 'PERSON', 'ORG', 'GPE', 'DATE', etc.
    text = Column(String(255), nullable=False)
    normalized_text = Column(String(255), nullable=False)
    start_char = Column(Integer)
    end_char = Column(Integer)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    post = relationship('Post')
    
    __table_args__ = (
        Index('idx_entity_type', 'entity_type'),
        Index('idx_entity_text', 'text'),
    )
    
    def __repr__(self):
        return f'<Entity {self.entity_type}: {self.text}>'


class Relationship(Base):
    """
    Relationship model for storing relationships between entities.
    """
    __tablename__ = 'relationships'
    
    id = Column(Integer, primary_key=True)
    source_type = Column(String(20), nullable=False)  # 'user', 'post', 'hashtag', 'entity'
    source_id = Column(String(100), nullable=False)
    target_type = Column(String(20), nullable=False)
    target_id = Column(String(100), nullable=False)
    relationship_type = Column(String(50), nullable=False, index=True)  # 'POSTED_BY', 'MENTIONS', 'TAGGED_WITH', etc.
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_relationship_type', 'relationship_type'),
        Index('idx_relationship_source', 'source_type', 'source_id'),
        Index('idx_relationship_target', 'target_type', 'target_id'),
    )
    
    def __repr__(self):
        return f'<Relationship {self.source_type}/{self.source_id} -> {self.target_type}/{self.target_id}>'


# --- Database Operations ---

class DatabaseManager:
    """
    Provides high-level database operations for OpenLens.
    """
    
    def __init__(self):
        """Initialize database manager."""
        self.db = _db
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(self.db.engine)
        print("Created all database tables")
    
    def drop_tables(self):
        """Drop all database tables."""
        Base.metadata.drop_all(self.db.engine)
        print("Dropped all database tables")
    
    def save_post(self, post_data: Dict[str, Any], platform: str) -> Optional[Post]:
        """
        Save a post and its related data to the database.
        
        Args:
            post_data: Dictionary containing post data.
            platform: Platform name ('vk', 'twitter', 'instagram', 'telegram').
            
        Returns:
            Saved Post object or None if failed.
        """
        session = self.db.get_session()
        try:
            # Create post
            post = Post(
                id=post_data.get('id', str(uuid.uuid4())),
                platform=platform,
                platform_id=post_data.get('platform_id', post_data.get('id', '')),
                content=post_data.get('content', ''),
                author_name=post_data.get('author_name', ''),
                author_username=post_data.get('author_username', ''),
                timestamp=post_data.get('timestamp'),
                likes=post_data.get('likes', 0),
                reposts=post_data.get('reposts', 0),
                views=post_data.get('views', 0),
                comments=post_data.get('comments', 0),
                url=post_data.get('url', ''),
            )
            session.add(post)
            session.flush()
            
            # Save metadata if present
            if 'metadata' in post_data:
                metadata = Metadata(
                    post_id=post.id,
                    camera_make=post_data['metadata'].get('camera_make'),
                    camera_model=post_data['metadata'].get('camera_model'),
                    gps_latitude=post_data['metadata'].get('gps_latitude'),
                    gps_longitude=post_data['metadata'].get('gps_longitude'),
                    gps_timestamp=post_data['metadata'].get('gps_timestamp'),
                    created_at=post_data['metadata'].get('created_at'),
                )
                session.add(metadata)
            
            # Save geotags if present
            if 'geotag' in post_data:
                geotag = post_data['geotag']
                if isinstance(geotag, dict):
                    db_geotag = Geotag(
                        post_id=post.id,
                        latitude=geotag.get('latitude'),
                        longitude=geotag.get('longitude'),
                        place_name=geotag.get('place_name'),
                        city=geotag.get('city'),
                        country=geotag.get('country'),
                    )
                    session.add(db_geotag)
            
            # Save hashtags if present
            if 'hashtags' in post_data:
                for tag in post_data['hashtags']:
                    hashtag = Hashtag(
                        post_id=post.id,
                        tag=tag,
                        normalized_tag=tag.lower().strip('#'),
                    )
                    session.add(hashtag)
            
            # Save mentions if present
            if 'mentions' in post_data:
                for mention in post_data['mentions']:
                    db_mention = Mention(
                        post_id=post.id,
                        username=mention.get('username', mention),
                        display_name=mention.get('display_name', ''),
                        platform=platform,
                    )
                    session.add(db_mention)
            
            # Save attachments if present
            if 'attachments' in post_data:
                for attachment in post_data['attachments']:
                    db_attachment = Attachment(
                        post_id=post.id,
                        attachment_type=attachment.get('type', 'link'),
                        url=attachment.get('url', ''),
                        thumbnail_url=attachment.get('thumbnail_url'),
                        title=attachment.get('title'),
                    )
                    session.add(db_attachment)
            
            session.commit()
            return post
        except Exception as e:
            session.rollback()
            print(f"Failed to save post: {e}")
            return None
        finally:
            session.close()
    
    def get_posts(self, platform: str = None, limit: int = 10, offset: int = 0) -> List[Post]:
        """
        Get posts from the database.
        
        Args:
            platform: Optional platform filter.
            limit: Maximum number of posts to return.
            offset: Offset for pagination.
            
        Returns:
            List of Post objects.
        """
        session = self.db.get_session()
        try:
            query = session.query(Post)
            if platform:
                query = query.filter(Post.platform == platform)
            query = query.order_by(Post.timestamp.desc())
            query = query.limit(limit).offset(offset)
            return query.all()
        except Exception as e:
            print(f"Failed to get posts: {e}")
            return []
        finally:
            session.close()
    
    def search_posts(self, query: str, limit: int = 10) -> List[Post]:
        """
        Search posts by content.
        
        Args:
            query: Search query.
            limit: Maximum number of results.
            
        Returns:
            List of Post objects.
        """
        session = self.db.get_session()
        try:
            return session.query(Post).filter(
                Post.content.ilike(f'%{query}%')
            ).limit(limit).all()
        except Exception as e:
            print(f"Failed to search posts: {e}")
            return []
        finally:
            session.close()
    
    def get_post_by_id(self, post_id: str) -> Optional[Post]:
        """
        Get a post by ID.
        
        Args:
            post_id: Post ID.
            
        Returns:
            Post object or None if not found.
        """
        session = self.db.get_session()
        try:
            return session.query(Post).filter(Post.id == post_id).first()
        except Exception as e:
            print(f"Failed to get post: {e}")
            return None
        finally:
            session.close()
    
    def save_scraping_job(self, job_data: Dict[str, Any]) -> Optional[ScrapingJob]:
        """
        Save a scraping job to the database.
        
        Args:
            job_data: Dictionary containing job data.
            
        Returns:
            Saved ScrapingJob object or None if failed.
        """
        session = self.db.get_session()
        try:
            job = ScrapingJob(
                id=job_data.get('id'),
                user_id=job_data.get('user_id'),
                platform=job_data.get('platform'),
                target=job_data.get('target'),
                job_type=job_data.get('job_type'),
                status=job_data.get('status', 'pending'),
                parameters=job_data.get('parameters', {}),
                started_at=job_data.get('started_at'),
                completed_at=job_data.get('completed_at'),
            )
            session.add(job)
            session.commit()
            return job
        except Exception as e:
            session.rollback()
            print(f"Failed to save scraping job: {e}")
            return None
        finally:
            session.close()
    
    def update_scraping_job(self, job_id: str, status: str, result_count: int = 0, error_message: str = None) -> bool:
        """
        Update a scraping job status.
        
        Args:
            job_id: Job ID.
            status: New status.
            result_count: Number of results.
            error_message: Error message if failed.
            
        Returns:
            True if successful, False otherwise.
        """
        session = self.db.get_session()
        try:
            job = session.query(ScrapingJob).filter(ScrapingJob.id == job_id).first()
            if job:
                job.status = status
                job.result_count = result_count
                job.error_message = error_message
                job.completed_at = datetime.utcnow()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Failed to update scraping job: {e}")
            return False
        finally:
            session.close()
    
    def log_api_request(self, request_data: Dict[str, Any]) -> Optional[APILog]:
        """
        Log an API request.
        
        Args:
            request_data: Dictionary containing request data.
            
        Returns:
            Saved APILog object or None if failed.
        """
        session = self.db.get_session()
        try:
            log = APILog(
                user_id=request_data.get('user_id'),
                endpoint=request_data.get('endpoint'),
                method=request_data.get('method'),
                status_code=request_data.get('status_code'),
                request_data=request_data.get('request_data'),
                response_data=request_data.get('response_data'),
                ip_address=request_data.get('ip_address'),
                user_agent=request_data.get('user_agent'),
                duration_ms=request_data.get('duration_ms'),
            )
            session.add(log)
            session.commit()
            return log
        except Exception as e:
            session.rollback()
            print(f"Failed to log API request: {e}")
            return None
        finally:
            session.close()


# Initialize database manager
db_manager = DatabaseManager()


# For use with Flask
import flask

def init_db(app: flask.Flask):
    """
    Initialize database with Flask app.
    
    Args:
        app: Flask application.
    """
    # Create tables on first request
    @app.before_first_request
    def create_tables():
        Base.metadata.create_all(_db.engine)
    
    # Clean up on teardown
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        _db.Session.remove()
