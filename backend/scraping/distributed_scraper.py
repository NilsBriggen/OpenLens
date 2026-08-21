"""
Distributed Scraper for OpenLens

Provides distributed scraping capabilities:
- Task distribution
- Result aggregation
- Progress tracking
- Error handling
- Retry logic
"""

import os
import time
import json
import uuid
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Try to import celery
try:
    from celery import group, chord, chain
    from celery.result import AsyncResult
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False
    print("Celery not available. Install with: pip install celery")


@dataclass
class ScrapingTask:
    """Represents a scraping task."""
    task_id: str
    url: str
    method: str = 'GET'
    params: Dict[str, Any] = field(default_factory=dict)
    config: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0  # 0 = normal, 1 = high, -1 = low
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = 'pending'  # pending, running, completed, failed
    result: Any = None
    error: str = ''
    retries: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'task_id': self.task_id,
            'url': self.url,
            'method': self.method,
            'params': self.params,
            'config': self.config,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'status': self.status,
            'result': self.result,
            'error': self.error,
            'retries': self.retries,
        }


@dataclass
class ScrapingResult:
    """Represents the result of a scraping task."""
    task_id: str
    url: str
    status: str  # success, failure, partial
    data: Any = None
    error: str = ''
    metrics: Dict[str, Any] = field(default_factory=dict)
    completed_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'task_id': self.task_id,
            'url': self.url,
            'status': self.status,
            'data': self.data,
            'error': self.error,
            'metrics': self.metrics,
            'completed_at': self.completed_at.isoformat(),
        }


@dataclass
class ScrapingJob:
    """Represents a scraping job (collection of tasks)."""
    job_id: str
    name: str
    tasks: List[ScrapingTask] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    status: str = 'pending'  # pending, running, completed, failed, cancelled
    progress: float = 0.0
    results: List[ScrapingResult] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'job_id': self.job_id,
            'name': self.name,
            'tasks': [t.to_dict() for t in self.tasks],
            'created_at': self.created_at.isoformat(),
            'status': self.status,
            'progress': self.progress,
            'results': [r.to_dict() for r in self.results],
            'errors': self.errors,
        }


class DistributedScraper:
    """
    Distributed scraper for OpenLens.
    
    Provides:
    - Task distribution across workers
    - Result aggregation
    - Progress tracking
    - Error handling
    - Retry logic
    """
    
    def __init__(self, celery_app=None, num_workers: int = 10, 
                 proxy_manager=None, user_agent_manager=None, 
                 rate_limiter=None, result_cache=None):
        """
        Initialize the distributed scraper.
        
        Args:
            celery_app: Celery app instance.
            num_workers: Number of worker threads.
            proxy_manager: ProxyManager instance.
            user_agent_manager: UserAgentManager instance.
            rate_limiter: RateLimiter instance.
            result_cache: ResultCache instance.
        """
        self.celery_app = celery_app
        self.num_workers = num_workers
        self.proxy_manager = proxy_manager
        self.user_agent_manager = user_agent_manager
        self.rate_limiter = rate_limiter
        self.result_cache = result_cache
        
        self._jobs: Dict[str, ScrapingJob] = {}
        self._tasks: Dict[str, ScrapingTask] = {}
        self._executor = ThreadPoolExecutor(max_workers=num_workers)
        self._running = True
    
    def create_job(self, name: str, urls: List[str], 
                  method: str = 'GET', params: Dict = None, 
                  config: Dict = None) -> ScrapingJob:
        """
        Create a new scraping job.
        
        Args:
            name: Job name.
            urls: List of URLs to scrape.
            method: HTTP method.
            params: Request parameters.
            config: Scraper configuration.
            
        Returns:
            ScrapingJob.
        """
        job_id = str(uuid.uuid4())
        
        tasks = []
        for url in urls:
            task = ScrapingTask(
                task_id=str(uuid.uuid4()),
                url=url,
                method=method,
                params=params or {},
                config=config or {},
            )
            tasks.append(task)
            self._tasks[task.task_id] = task
        
        job = ScrapingJob(
            job_id=job_id,
            name=name,
            tasks=tasks,
        )
        
        self._jobs[job_id] = job
        
        return job
    
    def execute_job(self, job_id: str, use_celery: bool = False) -> ScrapingJob:
        """
        Execute a scraping job.
        
        Args:
            job_id: Job ID.
            use_celery: Whether to use Celery for distribution.
            
        Returns:
            ScrapingJob with updated status.
        """
        if job_id not in self._jobs:
            raise ValueError(f"Job {job_id} not found")
        
        job = self._jobs[job_id]
        job.status = 'running'
        job.progress = 0.0
        
        if use_celery and CELERY_AVAILABLE and self.celery_app:
            return self._execute_job_celery(job)
        else:
            return self._execute_job_local(job)
    
    def _execute_job_local(self, job: ScrapingJob) -> ScrapingJob:
        """Execute a job locally using thread pool."""
        futures = []
        
        for task in job.tasks:
            future = self._executor.submit(self._execute_task, task)
            futures.append(future)
        
        # Wait for all tasks to complete
        for future in as_completed(futures):
            result = future.result()
            job.results.append(result)
            
            # Update progress
            completed = len(job.results)
            total = len(job.tasks)
            job.progress = completed / total if total > 0 else 0.0
        
        # Check for errors
        job.errors = [r.error for r in job.results if r.error]
        
        # Update job status
        if all(r.status == 'success' for r in job.results):
            job.status = 'completed'
        elif any(r.status == 'failure' for r in job.results):
            job.status = 'partial' if any(r.status == 'success' for r in job.results) else 'failed'
        
        return job
    
    def _execute_job_celery(self, job: ScrapingJob) -> ScrapingJob:
        """Execute a job using Celery."""
        if not CELERY_AVAILABLE or not self.celery_app:
            return self._execute_job_local(job)
        
        # Submit tasks to Celery
        from .celery_app import celery_app
        
        tasks = []
        for task in job.tasks:
            async_result = celery_app.send_task(
                'scraping.tasks.scrape_url',
                args=[task.url, task.method, task.params, task.config],
                kwargs={},
                queue='scraping',
                priority=task.priority,
            )
            tasks.append((task.task_id, async_result))
        
        # Wait for results
        for task_id, async_result in tasks:
            try:
                result = async_result.get(timeout=300)  # 5 minute timeout
                
                scraping_result = ScrapingResult(
                    task_id=task_id,
                    url=result.get('url', ''),
                    status=result.get('status', 'success'),
                    data=result.get('data'),
                    error=result.get('error', ''),
                    metrics=result.get('metrics', {}),
                )
                
                job.results.append(scraping_result)
            
            except Exception as e:
                scraping_result = ScrapingResult(
                    task_id=task_id,
                    url='',
                    status='failure',
                    error=str(e),
                )
                job.results.append(scraping_result)
            
            # Update progress
            completed = len(job.results)
            total = len(job.tasks)
            job.progress = completed / total if total > 0 else 0.0
        
        # Check for errors
        job.errors = [r.error for r in job.results if r.error]
        
        # Update job status
        if all(r.status == 'success' for r in job.results):
            job.status = 'completed'
        elif any(r.status == 'failure' for r in job.results):
            job.status = 'partial' if any(r.status == 'success' for r in job.results) else 'failed'
        
        return job
    
    def _execute_task(self, task: ScrapingTask) -> ScrapingResult:
        """Execute a single scraping task."""
        from .scraper import WebScraper
        
        try:
            # Create scraper with configuration
            scraper_config = ScraperConfig(
                user_agent=task.config.get('user_agent'),
                timeout=task.config.get('timeout', 30),
                max_retries=task.config.get('max_retries', 3),
                use_proxy=task.config.get('use_proxy', True),
                use_javascript=task.config.get('use_javascript', False),
            )
            
            scraper = WebScraper(
                config=scraper_config,
                proxy_manager=self.proxy_manager,
                user_agent_manager=self.user_agent_manager,
            )
            
            # Execute request
            if task.method.upper() == 'GET':
                response = scraper.get(task.url, params=task.params)
            elif task.method.upper() == 'POST':
                response = scraper.post(task.url, data=task.params)
            else:
                response = scraper.request(task.url, task.method, params=task.params)
            
            # Check rate limit
            if self.rate_limiter:
                domain = self._extract_domain(task.url)
                self.rate_limiter.allow(domain)
            
            # Check cache
            if self.result_cache:
                cache_key = self.result_cache.generate_key(task.url, task.params, task.method)
                cached_result = self.result_cache.get(cache_key)
                
                if cached_result:
                    return ScrapingResult(
                        task_id=task.task_id,
                        url=task.url,
                        status='success',
                        data=cached_result,
                        metrics={'cached': True},
                    )
            
            # Process response
            if response.is_success:
                # Cache the result
                if self.result_cache:
                    cache_key = self.result_cache.generate_key(task.url, task.params, task.method)
                    self.result_cache.cache_response(
                        task.url,
                        {'content': response.content, 'soup': str(response.soup)},
                        task.params,
                        task.method,
                        ttl=3600  # 1 hour
                    )
                
                return ScrapingResult(
                    task_id=task.task_id,
                    url=task.url,
                    status='success',
                    data={
                        'content': response.content,
                        'soup': str(response.soup) if response.soup else '',
                        'status_code': response.status_code,
                        'headers': response.headers,
                        'request_time': response.request_time,
                    },
                    metrics={
                        'request_time': response.request_time,
                        'content_length': len(response.content),
                    },
                )
            else:
                return ScrapingResult(
                    task_id=task.task_id,
                    url=task.url,
                    status='failure',
                    error=response.error or f"HTTP {response.status_code}",
                )
        
        except Exception as e:
            return ScrapingResult(
                task_id=task.task_id,
                url=task.url,
                status='failure',
                error=str(e),
            )
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc
    
    def get_job(self, job_id: str) -> Optional[ScrapingJob]:
        """
        Get a scraping job.
        
        Args:
            job_id: Job ID.
            
        Returns:
            ScrapingJob or None.
        """
        return self._jobs.get(job_id)
    
    def get_task(self, task_id: str) -> Optional[ScrapingTask]:
        """
        Get a scraping task.
        
        Args:
            task_id: Task ID.
            
        Returns:
            ScrapingTask or None.
        """
        return self._tasks.get(task_id)
    
    def cancel_job(self, job_id: str) -> bool:
        """
        Cancel a scraping job.
        
        Args:
            job_id: Job ID.
            
        Returns:
            True if cancelled.
        """
        if job_id not in self._jobs:
            return False
        
        job = self._jobs[job_id]
        
        if job.status == 'running':
            # In a real implementation, we would cancel the Celery tasks
            # For now, just mark as cancelled
            job.status = 'cancelled'
            return True
        
        return False
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of a scraping job.
        
        Args:
            job_id: Job ID.
            
        Returns:
            Status dictionary.
        """
        job = self.get_job(job_id)
        
        if not job:
            return {'status': 'not_found'}
        
        return {
            'job_id': job.job_id,
            'name': job.name,
            'status': job.status,
            'progress': job.progress,
            'total_tasks': len(job.tasks),
            'completed_tasks': len(job.results),
            'errors': len(job.errors),
            'created_at': job.created_at.isoformat(),
        }
    
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """
        Get all scraping jobs.
        
        Returns:
            List of job status dictionaries.
        """
        return [self.get_job_status(job_id) for job_id in self._jobs]
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a scraping job.
        
        Args:
            job_id: Job ID.
            
        Returns:
            True if deleted.
        """
        if job_id not in self._jobs:
            return False
        
        job = self._jobs[job_id]
        
        # Remove tasks
        for task in job.tasks:
            if task.task_id in self._tasks:
                del self._tasks[task.task_id]
        
        # Remove job
        del self._jobs[job_id]
        
        return True
    
    def scrape_urls(self, urls: List[str], config: Dict = None) -> ScrapingJob:
        """
        Scrape multiple URLs.
        
        Args:
            urls: List of URLs to scrape.
            config: Scraper configuration.
            
        Returns:
            ScrapingJob.
        """
        job = self.create_job(
            name=f"Scrape {len(urls)} URLs",
            urls=urls,
            config=config,
        )
        
        return self.execute_job(job.job_id)
    
    def scrape_with_pagination(self, base_url: str, page_param: str = 'page',
                              max_pages: int = 10, config: Dict = None) -> ScrapingJob:
        """
        Scrape a paginated website.
        
        Args:
            base_url: Base URL.
            page_param: Page parameter name.
            max_pages: Maximum number of pages.
            config: Scraper configuration.
            
        Returns:
            ScrapingJob.
        """
        urls = []
        
        for page in range(1, max_pages + 1):
            if '?' in base_url:
                url = f"{base_url}&{page_param}={page}"
            else:
                url = f"{base_url}?{page_param}={page}"
            urls.append(url)
        
        return self.scrape_urls(urls, config)
    
    def scrape_sitemap(self, sitemap_url: str, config: Dict = None) -> ScrapingJob:
        """
        Scrape URLs from a sitemap.
        
        Args:
            sitemap_url: Sitemap URL.
            config: Scraper configuration.
            
        Returns:
            ScrapingJob.
        """
        from .scraper import WebScraper
        
        # First, scrape the sitemap
        scraper = WebScraper()
        response = scraper.get(sitemap_url)
        
        if not response.is_success or not response.soup:
            raise ValueError(f"Failed to fetch sitemap: {response.error}")
        
        # Extract URLs from sitemap
        urls = []
        for loc in response.soup.find_all('loc'):
            url = loc.get_text(strip=True)
            if url:
                urls.append(url)
        
        return self.scrape_urls(urls, config)
    
    def close(self):
        """Close the distributed scraper."""
        self._running = False
        self._executor.shutdown(wait=True)


# Global distributed scraper instance
distributed_scraper = DistributedScraper()


# Import ScraperConfig for type hints
from .scraper import ScraperConfig
