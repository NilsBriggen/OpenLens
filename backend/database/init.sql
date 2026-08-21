-- PostgreSQL Initialization Script for OpenLens
-- This script is run when the PostgreSQL container starts for the first time

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE openlens' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'openlens')\;

-- Connect to the openlens database
\c openlens

-- Create schema for authentication
CREATE SCHEMA IF NOT EXISTS auth;

-- Create schema for application data
CREATE SCHEMA IF NOT EXISTS app;

-- Set search path
SET search_path TO public, auth, app;

-- Create tables for authentication
CREATE TABLE IF NOT EXISTS auth_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role VARCHAR(20) DEFAULT 'user',
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100),
    permissions JSONB DEFAULT '[''read'']',
    is_active BOOLEAN DEFAULT TRUE,
    rate_limit INTEGER DEFAULT 100,
    last_used TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token VARCHAR(500) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_revoked BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE CASCADE
);

-- Create tables for application data
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    username VARCHAR(100) UNIQUE,
    bio TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    birthday VARCHAR(50),
    friends INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS posts (
    id VARCHAR(100) PRIMARY KEY,
    platform VARCHAR(20) NOT NULL,
    platform_id VARCHAR(100) NOT NULL,
    content TEXT,
    author_id INTEGER,
    author_name VARCHAR(100),
    author_username VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE,
    likes INTEGER DEFAULT 0,
    reposts INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    url VARCHAR(500),
    language VARCHAR(10),
    sentiment_score FLOAT,
    sentiment_label VARCHAR(20),
    is_processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS metadata (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(100) UNIQUE NOT NULL,
    camera_make VARCHAR(100),
    camera_model VARCHAR(100),
    focal_length VARCHAR(50),
    aperture VARCHAR(50),
    iso INTEGER,
    exposure_time VARCHAR(50),
    gps_latitude FLOAT,
    gps_longitude FLOAT,
    gps_altitude FLOAT,
    gps_timestamp TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE,
    modified_at TIMESTAMP WITH TIME ZONE,
    device_type VARCHAR(50),
    software VARCHAR(100),
    file_size INTEGER,
    file_type VARCHAR(50),
    file_hash VARCHAR(100),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS geotags (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(100) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    altitude FLOAT,
    accuracy FLOAT,
    place_name VARCHAR(255),
    city VARCHAR(100),
    region VARCHAR(100),
    country VARCHAR(100),
    country_code VARCHAR(10),
    address TEXT,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS hashtags (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(100) NOT NULL,
    tag VARCHAR(100) NOT NULL,
    normalized_tag VARCHAR(100) NOT NULL,
    count INTEGER DEFAULT 1,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS mentions (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(100) NOT NULL,
    username VARCHAR(100) NOT NULL,
    display_name VARCHAR(100),
    platform VARCHAR(20),
    platform_id VARCHAR(100),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attachments (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(100) NOT NULL,
    attachment_type VARCHAR(20) NOT NULL,
    url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    title VARCHAR(255),
    description TEXT,
    file_size INTEGER,
    file_type VARCHAR(50),
    width INTEGER,
    height INTEGER,
    duration INTEGER,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scraping_jobs (
    id VARCHAR(100) PRIMARY KEY,
    user_id INTEGER,
    platform VARCHAR(20) NOT NULL,
    target VARCHAR(255) NOT NULL,
    job_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    parameters JSONB DEFAULT '{}',
    result_count INTEGER DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS api_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    request_data JSONB,
    response_data JSONB,
    ip_address VARCHAR(50),
    user_agent VARCHAR(500),
    duration_ms INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES auth_users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS entities (
    id SERIAL PRIMARY KEY,
    post_id VARCHAR(100),
    entity_type VARCHAR(20) NOT NULL,
    text VARCHAR(255) NOT NULL,
    normalized_text VARCHAR(255) NOT NULL,
    start_char INTEGER,
    end_char INTEGER,
    confidence FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS relationships (
    id SERIAL PRIMARY KEY,
    source_type VARCHAR(20) NOT NULL,
    source_id VARCHAR(100) NOT NULL,
    target_type VARCHAR(20) NOT NULL,
    target_id VARCHAR(100) NOT NULL,
    relationship_type VARCHAR(50) NOT NULL,
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_auth_users_username ON auth_users(username);
CREATE INDEX IF NOT EXISTS idx_auth_users_email ON auth_users(email);
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(key);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_refresh_tokens_token ON refresh_tokens(token);

CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform);
CREATE INDEX IF NOT EXISTS idx_posts_timestamp ON posts(timestamp);
CREATE INDEX IF NOT EXISTS idx_posts_platform_timestamp ON posts(platform, timestamp);
CREATE INDEX IF NOT EXISTS idx_posts_author_id ON posts(author_id);

CREATE INDEX IF NOT EXISTS idx_metadata_post_id ON metadata(post_id);
CREATE INDEX IF NOT EXISTS idx_geotags_post_id ON geotags(post_id);
CREATE INDEX IF NOT EXISTS idx_geotags_lat_lon ON geotags(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_hashtags_tag ON hashtags(tag);
CREATE INDEX IF NOT EXISTS idx_hashtags_normalized ON hashtags(normalized_tag);
CREATE INDEX IF NOT EXISTS idx_mentions_username ON mentions(username);
CREATE INDEX IF NOT EXISTS idx_attachments_post_id ON attachments(post_id);

CREATE INDEX IF NOT EXISTS idx_scraping_jobs_status ON scraping_jobs(status);
CREATE INDEX IF NOT EXISTS idx_scraping_jobs_user_id ON scraping_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_api_logs_created ON api_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_api_logs_endpoint ON api_logs(endpoint);
CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);
CREATE INDEX IF NOT EXISTS idx_entities_text ON entities(text);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type);
CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_type, source_id);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_type, target_id);

-- Create a sample admin user (for development only)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM auth_users WHERE username = 'admin') THEN
        INSERT INTO auth_users (username, email, password_hash, full_name, role, is_verified)
        VALUES ('admin', 'admin@openlens.com', '\$2b\$12\$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGgaYlPO', 'Admin User', 'admin', TRUE);
        
        RAISE NOTICE 'Created admin user with username: admin, password: admin123';
    END IF;
END $$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE openlens TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;

-- Log completion
RAISE NOTICE 'PostgreSQL initialization completed for OpenLens';
