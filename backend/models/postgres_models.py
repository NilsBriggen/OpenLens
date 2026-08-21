"""
PostgreSQL Models for OpenLens

Defines SQLAlchemy models for structured data storage in PostgreSQL.
Includes tables for users, posts, metadata, and relationships.

Dependencies:
- SQLAlchemy: For ORM
- psycopg2-binary: For PostgreSQL support
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    Index,
)
from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker,
)
from sqlalchemy.dialects.postgresql import ARRAY

# SQLAlchemy base class
Base = declarative_base()


class User(Base):
    """
    Represents a user from a social media platform (VK, Telegram, etc.).
    """
    __tablename__ = "users"

    id = Column(String(64), primary_key=True, index=True)
    platform = Column(String(32), nullable=False, index=True)  # e.g., "vk", "telegram"
    username = Column(String(64), index=True)
    first_name = Column(String(128))
    last_name = Column(String(128))
    full_name = Column(String(256))
    bio = Column(Text)
    city = Column(String(128))
    country = Column(String(128))
    birthday = Column(String(32))
    is_verified = Column(Boolean, default=False)
    is_bot = Column(Boolean, default=False)
    profile_url = Column(String(256))
    profile_photo = Column(String(256))
    last_seen = Column(String(128))
    followers_count = Column(Integer, default=0)
    friends_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    metadata = relationship("UserMetadata", back_populates="user", cascade="all, delete-orphan")
    mentions = relationship("Mention", foreign_keys="[Mention.mentioned_user_id]", back_populates="mentioned_user")
    
    __table_args__ = (
        Index('idx_user_platform_username', 'platform', 'username', unique=True),
    )

    def __repr__(self):
        return f"<User(id={self.id}, platform={self.platform}, username={self.username})>"


class Post(Base):
    """
    Represents a post from a social media platform.
    """
    __tablename__ = "posts"

    id = Column(String(64), primary_key=True, index=True)
    platform = Column(String(32), nullable=False, index=True)  # e.g., "vk", "telegram"
    post_url = Column(String(256))
    content = Column(Text)
    timestamp = Column(DateTime, index=True)
    likes = Column(Integer, default=0)
    reposts = Column(Integer, default=0)
    views = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    
    # Foreign keys
    author_id = Column(String(64), ForeignKey("users.id"), index=True)
    channel_id = Column(String(64), index=True)  # For group/channel posts
    
    # Relationships
    author = relationship("User", back_populates="posts")
    metadata = relationship("PostMetadata", back_populates="post", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="post", cascade="all, delete-orphan")
    mentions = relationship("Mention", back_populates="post")
    geotags = relationship("Geotag", back_populates="post")
    hashtags = relationship("Hashtag", back_populates="post")
    
    __table_args__ = (
        Index('idx_post_platform_id', 'platform', 'id', unique=True),
    )

    def __repr__(self):
        return f"<Post(id={self.id}, platform={self.platform}, timestamp={self.timestamp})>"


class UserMetadata(Base):
    """
    Additional metadata for users (e.g., education, work history).
    """
    __tablename__ = "user_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    key = Column(String(64), nullable=False)
    value = Column(JSON)
    
    # Relationships
    user = relationship("User", back_populates="metadata")

    __table_args__ = (
        Index('idx_user_metadata_key', 'user_id', 'key', unique=True),
    )


class PostMetadata(Base):
    """
    Additional metadata for posts (e.g., EXIF data from images).
    """
    __tablename__ = "post_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(64), ForeignKey("posts.id"), nullable=False, index=True)
    key = Column(String(64), nullable=False)
    value = Column(JSON)
    
    # Relationships
    post = relationship("Post", back_populates="metadata")

    __table_args__ = (
        Index('idx_post_metadata_key', 'post_id', 'key', unique=True),
    )


class Attachment(Base):
    """
    Represents an attachment (image, video, document, link) in a post.
    """
    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(64), ForeignKey("posts.id"), nullable=False, index=True)
    attachment_type = Column(String(32), nullable=False)  # e.g., "image", "video", "link"
    url = Column(String(512))
    thumbnail_url = Column(String(512))
    filename = Column(String(256))
    mime_type = Column(String(128))
    size = Column(Integer)  # File size in bytes
    width = Column(Integer)  # For images/videos
    height = Column(Integer)  # For images/videos
    duration = Column(Float)  # For videos/audio (in seconds)
    
    # Relationships
    post = relationship("Post", back_populates="attachments")


class Geotag(Base):
    """
    Represents a geotag (GPS coordinates) associated with a post or user.
    """
    __tablename__ = "geotags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(64), ForeignKey("posts.id"), index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float)
    accuracy = Column(Float)  # Accuracy in meters
    address = Column(String(256))  # Reverse-geocoded address
    
    # Relationships
    post = relationship("Post", back_populates="geotags")


class Hashtag(Base):
    """
    Represents a hashtag used in a post.
    """
    __tablename__ = "hashtags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(64), ForeignKey("posts.id"), index=True)
    tag = Column(String(64), nullable=False, index=True)
    
    # Relationships
    post = relationship("Post", back_populates="hashtags")

    __table_args__ = (
        Index('idx_hashtag_tag', 'tag'),
    )


class Mention(Base):
    """
    Represents a mention of a user in a post.
    """
    __tablename__ = "mentions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(String(64), ForeignKey("posts.id"), nullable=False, index=True)
    mentioned_user_id = Column(String(64), ForeignKey("users.id"), index=True)
    mention_text = Column(String(128))  # The text of the mention (e.g., "@username")
    
    # Relationships
    post = relationship("Post", back_populates="mentions")
    mentioned_user = relationship("User", foreign_keys=[mentioned_user_id], back_populates="mentions")


class Relationship(Base):
    """
    Represents a relationship between two users (e.g., friends, followers).
    """
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user1_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    user2_id = Column(String(64), ForeignKey("users.id"), nullable=False, index=True)
    relationship_type = Column(String(32), nullable=False)  # e.g., "friends", "follows", "mentions"
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_relationship_type', 'relationship_type'),
        Index('idx_relationship_users', 'user1_id', 'user2_id', unique=True),
    )


class DatabaseManager:
    """
    Manages database connections and sessions for PostgreSQL.
    """

    def __init__(self, db_url: str = "sqlite:///openlens.db"):
        """
        Initialize the database manager.
        
        Args:
            db_url: Database URL (e.g., "postgresql://user:password@localhost/openlens").
        """
        self.db_url = db_url
        self.engine = create_engine(db_url, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(self.engine)
        print(f"Created tables in database: {self.db_url}")

    def drop_tables(self):
        """Drop all tables in the database."""
        Base.metadata.drop_all(self.engine)
        print(f"Dropped tables in database: {self.db_url}")

    def get_session(self):
        """Get a new database session."""
        return self.Session()


# Example usage
if __name__ == "__main__":
    # Use SQLite for testing
    db_manager = DatabaseManager("sqlite:///openlens.db")
    db_manager.create_tables()
    
    # Create a session
    session = db_manager.get_session()
    
    # Add a test user
    user = User(
        id="test_user_1",
        platform="vk",
        username="test_user",
        first_name="Test",
        last_name="User",
        full_name="Test User",
    )
    session.add(user)
    session.commit()
    
    # Add a test post
    post = Post(
        id="test_post_1",
        platform="vk",
        content="This is a test post #OSINT",
        timestamp=datetime.utcnow(),
        author_id="test_user_1",
    )
    session.add(post)
    session.commit()
    
    print("Added test data to database.")
    session.close()
