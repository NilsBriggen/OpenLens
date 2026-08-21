"""
Unit Tests for Database Module

Tests for:
- Database connection and session management
- Model creation and relationships
- CRUD operations
- Query operations
"""

import unittest
import os
import sys
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import sqlite3

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.postgres_db import (
    Database, get_db, get_session, db_manager, Base,
    User, Post, Metadata, Geotag, Hashtag, Mention, Attachment,
    ScrapingJob, APILog, Entity, Relationship, DatabaseManager
)


class TestDatabaseConnection(unittest.TestCase):
    """Test database connection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use SQLite for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create a test database URL
        self.db_url = f'sqlite:///{self.temp_db.name}'
        
        # Patch the environment variable
        self.db_patcher = patch.dict('os.environ', {'POSTGRES_URL': self.db_url})
        self.db_patcher.start()
        
        # Create database instance
        self.db = Database()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.db_patcher.stop()
        
        if self.db.engine:
            self.db.close()
        
        # Remove temporary database file
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_database_initialization(self):
        """Test database initialization."""
        self.assertIsNotNone(self.db.engine)
        self.assertIsNotNone(self.db.Session)
    
    def test_get_session(self):
        """Test getting a database session."""
        session = self.db.get_session()
        self.assertIsNotNone(session)
        session.close()
    
    def test_create_tables(self):
        """Test creating database tables."""
        # Create all tables
        Base.metadata.create_all(self.db.engine)
        
        # Verify tables exist
        inspector = inspect(self.db.engine)
        tables = inspector.get_table_names()
        
        expected_tables = [
            'users', 'posts', 'metadata', 'geotags', 'hashtags',
            'mentions', 'attachments', 'scraping_jobs', 'api_logs',
            'entities', 'relationships'
        ]
        
        for table in expected_tables:
            self.assertIn(table, tables)
    
    def test_drop_tables(self):
        """Test dropping database tables."""
        # Create tables first
        Base.metadata.create_all(self.db.engine)
        
        # Verify tables exist
        inspector = inspect(self.db.engine)
        tables_before = inspector.get_table_names()
        self.assertGreater(len(tables_before), 0)
        
        # Drop tables
        Base.metadata.drop_all(self.db.engine)
        
        # Verify tables are gone
        tables_after = inspector.get_table_names()
        self.assertEqual(len(tables_after), 0)


class TestUserModel(unittest.TestCase):
    """Test User model functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use SQLite for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create a test database URL
        self.db_url = f'sqlite:///{self.temp_db.name}'
        
        # Patch the environment variable
        self.db_patcher = patch.dict('os.environ', {'POSTGRES_URL': self.db_url})
        self.db_patcher.start()
        
        # Create database instance
        self.db = Database()
        
        # Create tables
        Base.metadata.create_all(self.db.engine)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.db_patcher.stop()
        
        if self.db.engine:
            self.db.close()
        
        # Remove temporary database file
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_create_user(self):
        """Test creating a user."""
        session = self.db.get_session()
        try:
            user = User(
                username="testuser",
                email="test@example.com",
                password_hash="hashed_password",
                full_name="Test User",
                is_active=True,
                is_admin=False
            )
            session.add(user)
            session.commit()
            
            # Verify user was created
            retrieved_user = session.query(User).filter_by(username="testuser").first()
            self.assertIsNotNone(retrieved_user)
            self.assertEqual(retrieved_user.email, "test@example.com")
        finally:
            session.close()
    
    def test_user_relationships(self):
        """Test user relationships."""
        session = self.db.get_session()
        try:
            user = User(
                username="testuser",
                email="test@example.com",
                password_hash="hashed_password"
            )
            session.add(user)
            session.flush()
            
            # Create a post
            post = Post(
                id="post_1",
                platform="twitter",
                platform_id="tweet_1",
                content="Test post content",
                author_id=user.id,
                author_name="Test User",
                author_username="testuser",
                timestamp=datetime.utcnow()
            )
            session.add(post)
            session.commit()
            
            # Verify relationship
            retrieved_user = session.query(User).filter_by(username="testuser").first()
            self.assertEqual(len(retrieved_user.posts), 1)
            self.assertEqual(retrieved_user.posts[0].id, "post_1")
        finally:
            session.close()


class TestPostModel(unittest.TestCase):
    """Test Post model functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use SQLite for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create a test database URL
        self.db_url = f'sqlite:///{self.temp_db.name}'
        
        # Patch the environment variable
        self.db_patcher = patch.dict('os.environ', {'POSTGRES_URL': self.db_url})
        self.db_patcher.start()
        
        # Create database instance
        self.db = Database()
        
        # Create tables
        Base.metadata.create_all(self.db.engine)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.db_patcher.stop()
        
        if self.db.engine:
            self.db.close()
        
        # Remove temporary database file
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_create_post_with_metadata(self):
        """Test creating a post with metadata."""
        session = self.db.get_session()
        try:
            user = User(
                username="testuser",
                email="test@example.com",
                password_hash="hashed_password"
            )
            session.add(user)
            session.flush()
            
            post = Post(
                id="post_1",
                platform="twitter",
                platform_id="tweet_1",
                content="Test post content",
                author_id=user.id,
                author_name="Test User",
                author_username="testuser",
                timestamp=datetime.utcnow()
            )
            session.add(post)
            session.flush()
            
            metadata = Metadata(
                post_id=post.id,
                camera_make="Canon",
                camera_model="EOS 5D",
                gps_latitude=55.7558,
                gps_longitude=37.6173
            )
            session.add(metadata)
            session.commit()
            
            # Verify post and metadata
            retrieved_post = session.query(Post).filter_by(id="post_1").first()
            self.assertIsNotNone(retrieved_post)
            self.assertIsNotNone(retrieved_post.metadata)
            self.assertEqual(retrieved_post.metadata.camera_make, "Canon")
        finally:
            session.close()
    
    def test_create_post_with_hashtags(self):
        """Test creating a post with hashtags."""
        session = self.db.get_session()
        try:
            post = Post(
                id="post_2",
                platform="twitter",
                platform_id="tweet_2",
                content="Test post with #hashtag",
                author_name="Test User",
                author_username="testuser",
                timestamp=datetime.utcnow()
            )
            session.add(post)
            session.flush()
            
            hashtag = Hashtag(
                post_id=post.id,
                tag="#hashtag",
                normalized_tag="hashtag"
            )
            session.add(hashtag)
            session.commit()
            
            # Verify post and hashtag
            retrieved_post = session.query(Post).filter_by(id="post_2").first()
            self.assertIsNotNone(retrieved_post)
            self.assertEqual(len(retrieved_post.hashtags), 1)
            self.assertEqual(retrieved_post.hashtags[0].tag, "#hashtag")
        finally:
            session.close()


class TestDatabaseManager(unittest.TestCase):
    """Test DatabaseManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use SQLite for testing
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # Create a test database URL
        self.db_url = f'sqlite:///{self.temp_db.name}'
        
        # Patch the environment variable
        self.db_patcher = patch.dict('os.environ', {'POSTGRES_URL': self.db_url})
        self.db_patcher.start()
        
        # Create database instance
        self.db = Database()
        
        # Create tables
        Base.metadata.create_all(self.db.engine)
        
        # Create database manager
        self.manager = DatabaseManager()
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.db_patcher.stop()
        
        if self.db.engine:
            self.db.close()
        
        # Remove temporary database file
        try:
            os.unlink(self.temp_db.name)
        except:
            pass
    
    def test_save_post(self):
        """Test saving a post with related data."""
        post_data = {
            'id': 'test_post_1',
            'platform_id': 'tweet_1',
            'content': 'Test post content',
            'author_name': 'Test User',
            'author_username': 'testuser',
            'timestamp': datetime.utcnow(),
            'likes': 10,
            'reposts': 5,
            'metadata': {
                'camera_make': 'Canon',
                'camera_model': 'EOS 5D',
                'gps_latitude': 55.7558,
                'gps_longitude': 37.6173
            },
            'hashtags': ['#test', '#example'],
            'attachments': [
                {'type': 'image', 'url': 'http://example.com/image.jpg'}
            ]
        }
        
        post = self.manager.save_post(post_data, 'twitter')
        self.assertIsNotNone(post)
        self.assertEqual(post.id, 'test_post_1')
    
    def test_get_posts(self):
        """Test getting posts."""
        # Save a test post
        post_data = {
            'id': 'test_post_2',
            'platform_id': 'tweet_2',
            'content': 'Test post content',
            'author_name': 'Test User',
            'author_username': 'testuser',
            'timestamp': datetime.utcnow(),
            'likes': 10
        }
        self.manager.save_post(post_data, 'twitter')
        
        # Get posts
        posts = self.manager.get_posts(platform='twitter', limit=10)
        self.assertGreater(len(posts), 0)
    
    def test_search_posts(self):
        """Test searching posts."""
        # Save a test post
        post_data = {
            'id': 'test_post_3',
            'platform_id': 'tweet_3',
            'content': 'Test post with searchable content',
            'author_name': 'Test User',
            'author_username': 'testuser',
            'timestamp': datetime.utcnow()
        }
        self.manager.save_post(post_data, 'twitter')
        
        # Search posts
        results = self.manager.search_posts('searchable', limit=10)
        self.assertGreater(len(results), 0)
    
    def test_get_post_by_id(self):
        """Test getting a post by ID."""
        # Save a test post
        post_data = {
            'id': 'test_post_4',
            'platform_id': 'tweet_4',
            'content': 'Test post content',
            'author_name': 'Test User',
            'author_username': 'testuser',
            'timestamp': datetime.utcnow()
        }
        self.manager.save_post(post_data, 'twitter')
        
        # Get post by ID
        post = self.manager.get_post_by_id('test_post_4')
        self.assertIsNotNone(post)
        self.assertEqual(post.id, 'test_post_4')


# Import inspect for table inspection
from sqlalchemy import inspect


if __name__ == '__main__':
    unittest.main()
