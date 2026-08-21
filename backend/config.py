"""
Environment configuration for OpenLens backend services.

The FastAPI gateway does not go through the legacy Flask modules that call
load_dotenv(), so without this module it reads none of the repository's .env.
This is also the one place that reconciles the naming split between the root
.env (NEO4J_USER) and docker-compose.yml (NEO4J_USERNAME).
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple

_loaded = False


def load_environment(dotenv_path: Optional[str] = None) -> None:
    """
    Load the nearest .env into os.environ without overriding existing values.

    Walks upward from this file's directory so it works whether the process is
    started from the repo root, backend/, or a test runner's cwd.
    """
    global _loaded
    if _loaded and dotenv_path is None:
        return

    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    if dotenv_path:
        load_dotenv(dotenv_path, override=False)
    else:
        for parent in [Path(__file__).resolve().parent, *Path(__file__).resolve().parents]:
            candidate = parent / '.env'
            if candidate.is_file():
                load_dotenv(candidate, override=False)
                break

    _loaded = True


def neo4j_settings() -> Dict[str, str]:
    """
    Neo4j connection settings.

    Reads NEO4J_USERNAME first (what docker-compose.yml sets), then NEO4J_USER
    (what the root .env historically set), then the driver default.
    """
    load_environment()
    return {
        'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        'user': os.getenv('NEO4J_USERNAME') or os.getenv('NEO4J_USER') or 'neo4j',
        'password': os.getenv('NEO4J_PASSWORD', 'password'),
    }


def redis_url(db: int = 0) -> str:
    """Redis connection URL, from REDIS_URL or REDIS_HOST/PORT/PASSWORD parts."""
    load_environment()
    explicit = os.getenv('REDIS_URL')
    if explicit:
        return explicit

    host = os.getenv('REDIS_HOST', 'localhost')
    port = os.getenv('REDIS_PORT', '6379')
    password = os.getenv('REDIS_PASSWORD', '')
    auth = f':{password}@' if password else ''
    return f'redis://{auth}{host}:{port}/{db}'


def celery_urls() -> Tuple[str, str]:
    """(broker_url, result_backend) for Celery."""
    load_environment()
    broker = os.getenv('CELERY_BROKER_URL') or redis_url(0)
    backend = os.getenv('CELERY_RESULT_BACKEND') or redis_url(0)
    return broker, backend
