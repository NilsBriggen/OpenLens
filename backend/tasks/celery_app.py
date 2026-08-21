"""
Celery Configuration for OpenLens

Sets up Celery for asynchronous task processing (scraping, metadata extraction, etc.).
Uses Redis as the message broker.

Dependencies:
- celery: For task queue
- redis: For message broker
"""

from celery import Celery
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Initialize Celery app
celery = Celery(
    "openlens_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["tasks.scraping_tasks", "tasks.processing_tasks"],
)

# Configure Celery
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Rate limits (to avoid overwhelming external APIs)
    task_annotations={
        "tasks.scraping_tasks.scrape_vk_user": {"rate_limit": "10/m"},
        "tasks.scraping_tasks.scrape_vk_posts": {"rate_limit": "5/m"},
        "tasks.scraping_tasks.search_vk_users": {"rate_limit": "10/m"},
    },
    # Retry settings
    task_default_retry_delay=60,
    task_max_retries=3,
)

# Optional: Configure for production
if os.getenv("FLASK_ENV", "development") == "production":
    celery.conf.update(
        worker_prefetch_multiplier=1,
        worker_max_tasks_per_child=100,
        worker_max_memory_per_child=300000,  # 300MB
    )


if __name__ == "__main__":
    # Start Celery worker (for testing)
    celery.worker_main(["worker", "--loglevel=info"])
