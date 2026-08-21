"""
Database Module for OpenLens

Provides PostgreSQL and Neo4j database integration.

Usage:
    from database.postgres_db import get_db, get_session, db_manager
    from database.neo4j_db import get_neo4j_db
"""

from .postgres_db import get_db, get_session, db_manager, Database, DatabaseManager
from .neo4j_db import get_neo4j_db, Neo4jDatabase

__all__ = [
    'get_db',
    'get_session',
    'db_manager',
    'Database',
    'DatabaseManager',
    'get_neo4j_db',
    'Neo4jDatabase',
]
