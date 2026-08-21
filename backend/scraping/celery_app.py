"""
Celery Application for OpenLens Distributed Scraping

Provides Celery-based task distribution for:
- Web scraping tasks
- Data collection
- Background processing
- Scheduled tasks
"""

import os
import json
from typing import Dict, List, Any, Optional
from celery import Celery, Task
from celery.schedules import crontab
from datetime import datetime, timedelta


# Configuration
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
CELERY_TIMEZONE = os.getenv('CELERY_TIMEZONE', 'UTC')
CELERY_ENABLE_UTC = os.getenv('CELERY_ENABLE_UTC', 'True').lower() == 'true'


class OpenLensCeleryApp(Celery):
    """
    Custom Celery application for OpenLens.
    
    Provides:
    - Task configuration
    - Error handling
    - Monitoring
    - Retry logic
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the Celery app."""
        super().__init__(*args, **kwargs)
        
        # Configure task defaults
        self.conf.update(
            task_serializer='json',
            accept_content=['json'],
            result_serializer='json',
            timezone=CELERY_TIMEZONE,
            enable_utc=CELERY_ENABLE_UTC,
            broker_url=CELERY_BROKER_URL,
            result_backend=CELERY_RESULT_BACKEND,
            
            # Task configuration
            task_default_queue='scraping',
            task_default_exchange='scraping',
            task_default_routing_key='scraping.task',
            
            # Retry configuration
            task_acks_late=True,
            task_reject_on_worker_lost=True,
            
            # Rate limits
            worker_max_tasks_per_child=100,
            worker_max_memory_per_child=300000,  # 300MB
            
            # Result configuration
            result_expires=3600,  # 1 hour
            result_cache_max=10000,
            
            # Beat schedule
            beat_schedule={
                'scrape-news-every-hour': {
                    'task': 'scraping.tasks.scrape_news_sources',
                    'schedule': crontab(minute=0, hour='*/1'),
                    'options': {'queue': 'periodic'},
                },
                'scrape-social-media-every-30min': {
                    'task': 'scraping.tasks.scrape_social_media',
                    'schedule': crontab(minute='*/30'),
                    'options': {'queue': 'periodic'},
                },
                'scrape-darkweb-every-6hours': {
                    'task': 'scraping.tasks.scrape_darkweb_sources',
                    'schedule': crontab(minute=0, hour='*/6'),
                    'options': {'queue': 'periodic'},
                },
                'update-proxies-every-day': {
                    'task': 'scraping.tasks.update_proxy_list',
                    'schedule': crontab(minute=0, hour=0),
                    'options': {'queue': 'periodic'},
                },
                'cleanup-cache-every-hour': {
                    'task': 'scraping.tasks.cleanup_result_cache',
                    'schedule': crontab(minute=0, hour='*/1'),
                    'options': {'queue': 'periodic'},
                },
            },
            
            # Queues
            task_queues=(
                {'name': 'scraping', 'routing_key': 'scraping.task'},
                {'name': 'periodic', 'routing_key': 'periodic.task'},
                {'name': 'high_priority', 'routing_key': 'high_priority.task'},
                {'name': 'low_priority', 'routing_key': 'low_priority.task'},
            ),
            
            # Worker configuration
            worker_concurrency=10,
            worker_prefetch_multiplier=4,
        )
        
        # Custom task classes
        self.task_cls = OpenLensTask
    
    def on_configure(self):
        """Called when the worker process is started."""
        print(f"OpenLens Celery worker configured at {datetime.utcnow()}")
    
    def on_worker_init(self):
        """Called when a worker process is initialized."""
        print(f"OpenLens Celery worker initialized at {datetime.utcnow()}")
    
    def on_task_prerun(self, task_id: str, task: Task, *args, **kwargs):
        """Called before a task is executed."""
        print(f"Task {task.name} ({task_id}) starting at {datetime.utcnow()}")
    
    def on_task_postrun(self, task_id: str, task: Task, retval, state, *args, **kwargs):
        """Called after a task is executed."""
        print(f"Task {task.name} ({task_id}) completed with state {state} at {datetime.utcnow()}")
    
    def on_task_failure(self, task_id: str, task: Task, exception, *args, **kwargs):
        """Called when a task fails."""
        print(f"Task {task.name} ({task_id}) failed: {exception}")
        # Log to monitoring system
        self._log_to_monitoring(task_id, task.name, 'failure', str(exception))
    
    def on_task_retry(self, task_id: str, task: Task, exception, *args, **kwargs):
        """Called when a task is retried."""
        print(f"Task {task.name} ({task_id}) retrying: {exception}")
    
    def _log_to_monitoring(self, task_id: str, task_name: str, status: str, message: str):
        """Log task status to monitoring system."""
        # In production, this would log to a monitoring system
        # For now, just print
        print(f"MONITOR: {task_name} ({task_id}) - {status}: {message}")


class OpenLensTask(Task):
    """
    Custom task class for OpenLens.
    
    Provides:
    - Automatic retry on failure
    - Error handling
    - Task timeout
    - Result caching
    """
    
    autoretry_for = (Exception,)
    max_retries = 3
    retry_backoff = True
    retry_backoff_max = 60  # 60 seconds max backoff
    retry_jitter = True
    
    default_retry_delay = 5  # 5 seconds
    rate_limit = '100/hour'  # Default rate limit
    
    def __call__(self, *args, **kwargs):
        """Execute the task with error handling."""
        try:
            # Call the original task
            return super().__call__(*args, **kwargs)
        except Exception as e:
            # Log the error
            print(f"Task {self.name} failed: {e}")
            raise self.retry(exc=e)
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called when the task fails."""
        print(f"Task {self.name} ({task_id}) failed: {exc}")
        super().on_failure(exc, task_id, args, kwargs, einfo)
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Called when the task is retried."""
        print(f"Task {self.name} ({task_id}) retrying: {exc}")
        super().on_retry(exc, task_id, args, kwargs, einfo)
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called when the task succeeds."""
        print(f"Task {self.name} ({task_id}) succeeded")
        super().on_success(retval, task_id, args, kwargs)


# Create the Celery app
celery_app = OpenLensCeleryApp('OpenLens')


def create_celery_app(name: str = 'OpenLens', **kwargs) -> OpenLensCeleryApp:
    """
    Create a new Celery app instance.
    
    Args:
        name: Name of the app.
        **kwargs: Additional configuration.
        
    Returns:
        OpenLensCeleryApp instance.
    """
    config = {
        'broker_url': kwargs.get('broker_url', CELERY_BROKER_URL),
        'result_backend': kwargs.get('result_backend', CELERY_RESULT_BACKEND),
    }
    
    app = OpenLensCeleryApp(name, **config)
    app.conf.update(kwargs)
    
    return app


# Configure the app
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone=CELERY_TIMEZONE,
    enable_utc=CELERY_ENABLE_UTC,
)


# Import tasks to register them
# This will be done in the tasks module
