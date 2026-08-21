"""
Unit Tests for Authentication Module

Tests for:
- JWT token creation and verification
- API key generation and rotation
- Password reset functionality
- Rate limiting
"""

import unittest
import os
import sys
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.authentication import (
    AuthManager, AuthConfig, auth_manager,
    create_access_token, create_refresh_token, verify_token,
    generate_api_key, hash_api_key, verify_api_key, rotate_api_key,
    generate_password_reset_token, blacklist_token
)
from auth.models import User, APIKey, RoleType
from middleware.rate_limiter import RateLimiter, rate_limit, user_rate_limit, api_key_rate_limit


class TestJWTAuthentication(unittest.TestCase):
    """Test JWT token functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.auth = AuthManager()
        self.user_id = 1
        self.username = "testuser"
        self.role = "user"
    
    def test_create_access_token(self):
        """Test creating an access token."""
        token = self.auth.create_access_token(self.user_id, self.username, self.role)
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)
    
    def test_create_refresh_token(self):
        """Test creating a refresh token."""
        token = self.auth.create_refresh_token(self.user_id)
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)
    
    def test_verify_valid_token(self):
        """Test verifying a valid token."""
        token = self.auth.create_access_token(self.user_id, self.username, self.role)
        payload = self.auth.verify_token(token)
        
        self.assertIsNotNone(payload)
        self.assertEqual(payload['sub'], str(self.user_id))
        self.assertEqual(payload['username'], self.username)
        self.assertEqual(payload['role'], self.role)
        self.assertEqual(payload['type'], 'access')
    
    def test_verify_invalid_token(self):
        """Test verifying an invalid token."""
        payload = self.auth.verify_token("invalid.token.here")
        self.assertIsNone(payload)
    
    def test_verify_expired_token(self):
        """Test verifying an expired token."""
        # Create a token with very short expiration
        with patch.object(AuthConfig, 'ACCESS_TOKEN_EXPIRE_MINUTES', 0):
            token = self.auth.create_access_token(self.user_id, self.username, self.role)
        
        # Wait a bit to ensure expiration
        import time
        time.sleep(1)
        
        payload = self.auth.verify_token(token)
        self.assertIsNone(payload)
    
    def test_token_blacklist(self):
        """Test token blacklisting."""
        token = self.auth.create_access_token(self.user_id, self.username, self.role)
        
        # Verify token is valid
        payload = self.auth.verify_token(token)
        self.assertIsNotNone(payload)
        
        # Blacklist the token
        self.auth.blacklist_token(token)
        
        # Verify token is now invalid
        payload = self.auth.verify_token(token)
        self.assertIsNone(payload)
    
    def test_decode_token_without_verification(self):
        """Test decoding a token without verification."""
        token = self.auth.create_access_token(self.user_id, self.username, self.role)
        payload = self.auth.decode_token(token)
        
        self.assertIsNotNone(payload)
        self.assertEqual(payload['sub'], str(self.user_id))


class TestAPIKeyFunctionality(unittest.TestCase):
    """Test API key functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.auth = AuthManager()
        self.user_id = 1
    
    def test_generate_api_key(self):
        """Test generating an API key."""
        key, key_hash, key_prefix = self.auth.generate_api_key(self.user_id, "Test Key")
        
        self.assertIsInstance(key, str)
        self.assertEqual(len(key), AuthConfig.API_KEY_LENGTH)
        self.assertIsInstance(key_hash, str)
        self.assertEqual(len(key_prefix), 10)
    
    def test_hash_api_key(self):
        """Test hashing an API key."""
        api_key = "test_api_key_1234567890"
        hashed = self.auth.hash_api_key(api_key)
        
        self.assertIsInstance(hashed, str)
        self.assertEqual(len(hashed), 64)  # SHA-256 produces 64 hex chars
    
    def test_verify_api_key(self):
        """Test verifying an API key."""
        api_key = "test_api_key_1234567890"
        hashed = self.auth.hash_api_key(api_key)
        
        # Should verify correctly
        self.assertTrue(self.auth.verify_api_key(api_key, hashed))
        
        # Should fail with wrong key
        self.assertFalse(self.auth.verify_api_key("wrong_key", hashed))
    
    def test_rotate_api_key(self):
        """Test rotating an API key."""
        old_key, old_hash, old_prefix = self.auth.generate_api_key(self.user_id, "Old Key")
        
        new_key, new_hash, new_prefix = self.auth.rotate_api_key(
            old_key, self.user_id, "New Key"
        )
        
        # New key should be different from old key
        self.assertNotEqual(new_key, old_key)
        self.assertNotEqual(new_hash, old_hash)
        
        # New key should still be valid
        self.assertEqual(len(new_key), AuthConfig.API_KEY_LENGTH)


class TestPasswordReset(unittest.TestCase):
    """Test password reset functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.auth = AuthManager()
        self.user_id = 1
        self.email = "test@example.com"
    
    def test_generate_password_reset_token(self):
        """Test generating a password reset token."""
        token, token_hash, expires_at = self.auth.generate_password_reset_token(
            self.user_id, self.email
        )
        
        self.assertIsInstance(token, str)
        self.assertIsInstance(token_hash, str)
        self.assertIsInstance(expires_at, datetime)
        
        # Token should expire in the configured time
        expected_expiry = datetime.utcnow() + timedelta(
            hours=AuthConfig.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
        )
        self.assertAlmostEqual(
            (expires_at - datetime.utcnow()).total_seconds(),
            (expected_expiry - datetime.utcnow()).total_seconds(),
            delta=1
        )
    
    def test_verify_password_reset_token(self):
        """Test verifying a password reset token."""
        token, token_hash, expires_at = self.auth.generate_password_reset_token(
            self.user_id, self.email
        )
        
        # Should verify correctly
        self.assertTrue(
            self.auth.verify_password_reset_token(token, token_hash, expires_at)
        )
        
        # Should fail with wrong token
        self.assertFalse(
            self.auth.verify_password_reset_token("wrong_token", token_hash, expires_at)
        )
    
    def test_verify_expired_password_reset_token(self):
        """Test verifying an expired password reset token."""
        token, token_hash, expires_at = self.auth.generate_password_reset_token(
            self.user_id, self.email
        )
        
        # Set expiration to the past
        expires_at = datetime.utcnow() - timedelta(hours=1)
        
        # Should fail because token is expired
        self.assertFalse(
            self.auth.verify_password_reset_token(token, token_hash, expires_at)
        )


class TestRateLimiter(unittest.TestCase):
    """Test rate limiting functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.limiter = RateLimiter(
            default_limit=10,
            default_window=60,
            user_default_limit=100,
            user_default_window=3600
        )
        self.test_ip = "192.168.1.1"
        self.test_user_id = "user_1"
        self.test_api_key = "test_api_key_1234567890"
    
    def test_ip_rate_limiting(self):
        """Test IP-based rate limiting."""
        # First 10 requests should be allowed
        for _ in range(10):
            self.assertFalse(self.limiter.is_rate_limited(self.test_ip))
        
        # 11th request should be rate limited
        self.assertTrue(self.limiter.is_rate_limited(self.test_ip))
    
    def test_user_rate_limiting(self):
        """Test user-based rate limiting."""
        # First 100 requests should be allowed
        for _ in range(100):
            self.assertFalse(self.limiter.is_user_rate_limited(self.test_user_id))
        
        # 101st request should be rate limited
        self.assertTrue(self.limiter.is_user_rate_limited(self.test_user_id))
    
    def test_api_key_rate_limiting(self):
        """Test API key-based rate limiting."""
        # First 10 requests should be allowed
        for _ in range(10):
            self.assertFalse(self.limiter.is_api_key_rate_limited(self.test_api_key))
        
        # 11th request should be rate limited
        self.assertTrue(self.limiter.is_api_key_rate_limited(self.test_api_key))
    
    def test_endpoint_rate_limiting(self):
        """Test endpoint-based rate limiting."""
        endpoint = "/api/test"
        
        # First 100 requests should be allowed (default_limit * 10)
        for _ in range(100):
            self.assertFalse(self.limiter.is_endpoint_rate_limited(endpoint))
        
        # 101st request should be rate limited
        self.assertTrue(self.limiter.is_endpoint_rate_limited(endpoint))
    
    def test_reset_rate_limiting(self):
        """Test resetting rate limiting."""
        # Max out IP rate limiting
        for _ in range(10):
            self.limiter.is_rate_limited(self.test_ip)
        
        # Should be rate limited
        self.assertTrue(self.limiter.is_rate_limited(self.test_ip))
        
        # Reset
        self.limiter.reset(ip=self.test_ip)
        
        # Should no longer be rate limited
        self.assertFalse(self.limiter.is_rate_limited(self.test_ip))
    
    def test_get_remaining_requests(self):
        """Test getting remaining requests."""
        # Make 5 requests
        for _ in range(5):
            self.limiter.is_rate_limited(self.test_ip)
        
        # Should have 5 remaining
        remaining = self.limiter.get_remaining_requests(ip=self.test_ip)
        self.assertEqual(remaining, 5)


class TestUserModel(unittest.TestCase):
    """Test User model functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.user = User(
            username="testuser",
            email="test@example.com",
            role=RoleType.USER
        )
        self.user.set_password("testpassword123")
    
    def test_set_and_check_password(self):
        """Test setting and checking password."""
        self.assertTrue(self.user.check_password("testpassword123"))
        self.assertFalse(self.user.check_password("wrongpassword"))
    
    def test_has_role(self):
        """Test role checking."""
        self.assertTrue(self.user.has_role(RoleType.USER))
        self.assertFalse(self.user.has_role(RoleType.ADMIN))
    
    def test_is_admin(self):
        """Test admin checking."""
        self.assertFalse(self.user.is_admin())
        
        admin_user = User(
            username="admin",
            email="admin@example.com",
            role=RoleType.ADMIN
        )
        self.assertTrue(admin_user.is_admin())
    
    def test_password_reset_token(self):
        """Test password reset token generation and verification."""
        token = self.user.generate_password_reset_token()
        
        self.assertIsInstance(token, str)
        self.assertIsNotNone(self.user.password_reset_token)
        self.assertIsNotNone(self.user.password_reset_token_expires)
        
        # Verify token
        self.assertTrue(self.user.verify_password_reset_token(token))
        
        # Clear token
        self.user.clear_password_reset_token()
        self.assertIsNone(self.user.password_reset_token)
        self.assertIsNone(self.user.password_reset_token_expires)
    
    def test_to_dict(self):
        """Test converting user to dictionary."""
        user_dict = self.user.to_dict()
        
        self.assertEqual(user_dict['username'], "testuser")
        self.assertEqual(user_dict['email'], "test@example.com")
        self.assertEqual(user_dict['role'], "user")


class TestAPIKeyModel(unittest.TestCase):
    """Test APIKey model functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = APIKey(
            user_id=1,
            key_hash="test_hash",
            key_prefix="test",
            name="Test Key",
            permissions=["read", "write"],
            created_at=datetime.utcnow()
        )
    
    def test_is_expired(self):
        """Test expiration checking."""
        # No expiration set
        self.assertFalse(self.api_key.is_expired())
        
        # Set expiration to the past
        self.api_key.expires_at = datetime.utcnow() - timedelta(days=1)
        self.assertTrue(self.api_key.is_expired())
        
        # Set expiration to the future
        self.api_key.expires_at = datetime.utcnow() + timedelta(days=1)
        self.assertFalse(self.api_key.is_expired())
    
    def test_can_access(self):
        """Test permission checking."""
        self.assertTrue(self.api_key.can_access("read"))
        self.assertTrue(self.api_key.can_access("write"))
        self.assertFalse(self.api_key.can_access("admin"))
    
    def test_needs_rotation(self):
        """Test rotation checking."""
        # Key created now should not need rotation
        self.assertFalse(self.api_key.needs_rotation())
        
        # Key created 100 days ago should need rotation
        self.api_key.created_at = datetime.utcnow() - timedelta(days=100)
        self.assertTrue(self.api_key.needs_rotation())
    
    def test_to_dict(self):
        """Test converting API key to dictionary."""
        key_dict = self.api_key.to_dict()
        
        self.assertEqual(key_dict['user_id'], 1)
        self.assertEqual(key_dict['name'], "Test Key")
        self.assertEqual(key_dict['key_prefix'], "test")
        self.assertEqual(key_dict['permissions'], ["read", "write"])


if __name__ == '__main__':
    unittest.main()
