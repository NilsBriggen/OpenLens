"""
Metrics Collector for OpenLens

Collects and tracks various metrics:
- API request metrics
- Scraping job metrics
- User activity metrics
- System performance metrics
- Custom metrics
"""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import time
import threading
import json


@dataclass
class MetricData:
    """Represents metric data."""
    name: str
    value: Any
    timestamp: datetime = field(default_factory=datetime.utcnow)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Counter:
    """A counter metric."""
    name: str
    value: int = 0
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    def increment(self, amount: int = 1):
        """Increment the counter."""
        self.value += amount
    
    def decrement(self, amount: int = 1):
        """Decrement the counter."""
        self.value -= amount
    
    def reset(self):
        """Reset the counter."""
        self.value = 0


@dataclass
class Gauge:
    """A gauge metric."""
    name: str
    value: float = 0.0
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    def set(self, value: float):
        """Set the gauge value."""
        self.value = value
    
    def increment(self, amount: float = 1.0):
        """Increment the gauge."""
        self.value += amount
    
    def decrement(self, amount: float = 1.0):
        """Decrement the gauge."""
        self.value -= amount


@dataclass
class Histogram:
    """A histogram metric."""
    name: str
    buckets: List[float]
    counts: List[int] = field(default_factory=list)
    total_count: int = 0
    total_sum: float = 0.0
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize counts array."""
        if not self.counts:
            self.counts = [0] * len(self.buckets)
    
    def record(self, value: float):
        """Record a value in the histogram."""
        self.total_count += 1
        self.total_sum += value
        
        for i, upper_bound in enumerate(self.buckets):
            if value <= upper_bound:
                self.counts[i] += 1
                break
    
    def get_percentiles(self) -> Dict[str, float]:
        """Get percentile values."""
        if self.total_count == 0:
            return {}
        
        sorted_values = []
        # In a real implementation, we'd store all values or use a more efficient approach
        # For now, return approximate percentiles based on buckets
        
        cumulative_count = 0
        percentiles = {}
        
        for i, (upper_bound, count) in enumerate(zip(self.buckets, self.counts)):
            cumulative_count += count
            percentile = (cumulative_count / self.total_count) * 100
            
            if percentile >= 50 and 'p50' not in percentiles:
                percentiles['p50'] = upper_bound
            if percentile >= 90 and 'p90' not in percentiles:
                percentiles['p90'] = upper_bound
            if percentile >= 99 and 'p99' not in percentiles:
                percentiles['p99'] = upper_bound
        
        return percentiles


@dataclass
class Timer:
    """A timer metric for tracking durations."""
    name: str
    durations: deque = field(default_factory=lambda: deque(maxlen=10000))
    total_count: int = 0
    total_time: float = 0.0
    description: str = ""
    tags: Dict[str, str] = field(default_factory=dict)
    
    def record(self, duration: float):
        """Record a duration."""
        self.durations.append(duration)
        self.total_count += 1
        self.total_time += duration
    
    def get_avg(self) -> float:
        """Get average duration."""
        if self.total_count == 0:
            return 0.0
        return self.total_time / self.total_count
    
    def get_percentile(self, percentile: float) -> float:
        """Get a specific percentile."""
        if not self.durations:
            return 0.0
        
        sorted_durations = sorted(self.durations)
        index = int((percentile / 100) * len(sorted_durations))
        return sorted_durations[min(index, len(sorted_durations) - 1)]


class MetricsCollector:
    """
    Collects and manages various metrics.
    """
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.counters: Dict[str, Counter] = {}
        self.gauges: Dict[str, Gauge] = {}
        self.histograms: Dict[str, Histogram] = {}
        self.timers: Dict[str, Timer] = {}
        self.time_series: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.metadata: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        self._start_time = datetime.utcnow()
        
        # Initialize default metrics
        self._initialize_default_metrics()
    
    def _initialize_default_metrics(self):
        """Initialize default metrics."""
        # API metrics
        self.create_counter('api.requests.total', 'Total API requests')
        self.create_counter('api.requests.success', 'Successful API requests')
        self.create_counter('api.requests.error', 'Error API requests')
        self.create_timer('api.request.duration', 'API request duration')
        
        # Scraping metrics
        self.create_counter('scraping.jobs.total', 'Total scraping jobs')
        self.create_counter('scraping.jobs.success', 'Successful scraping jobs')
        self.create_counter('scraping.jobs.failed', 'Failed scraping jobs')
        self.create_counter('scraping.items.total', 'Total items scraped')
        self.create_timer('scraping.job.duration', 'Scraping job duration')
        
        # User metrics
        self.create_counter('users.total', 'Total registered users')
        self.create_counter('users.active', 'Active users')
        self.create_counter('users.logins', 'User logins')
        
        # System metrics
        self.create_gauge('system.cpu.usage', 'CPU usage percentage')
        self.create_gauge('system.memory.usage', 'Memory usage percentage')
        self.create_gauge('system.disk.usage', 'Disk usage percentage')
        
        # Database metrics
        self.create_timer('database.query.duration', 'Database query duration')
        self.create_counter('database.queries.total', 'Total database queries')
    
    def create_counter(self, name: str, description: str = "", tags: Dict = None) -> Counter:
        """
        Create a new counter metric.
        
        Args:
            name: Metric name.
            description: Metric description.
            tags: Optional tags.
            
        Returns:
            Counter object.
        """
        with self._lock:
            if name in self.counters:
                return self.counters[name]
            
            counter = Counter(name=name, description=description, tags=tags or {})
            self.counters[name] = counter
            self.metadata[name] = {
                'type': 'counter',
                'description': description,
                'tags': tags or {},
                'created_at': datetime.utcnow().isoformat(),
            }
            return counter
    
    def get_counter(self, name: str) -> Optional[Counter]:
        """
        Get a counter metric.
        
        Args:
            name: Metric name.
            
        Returns:
            Counter object or None if not found.
        """
        return self.counters.get(name)
    
    def increment_counter(self, name: str, amount: int = 1, tags: Dict = None):
        """
        Increment a counter metric.
        
        Args:
            name: Metric name.
            amount: Amount to increment.
            tags: Optional tags for this increment.
        """
        counter = self.get_counter(name)
        if counter:
            counter.increment(amount)
            
            # Record time series data
            self._record_time_series(name, counter.value, tags)
    
    def create_gauge(self, name: str, description: str = "", tags: Dict = None) -> Gauge:
        """
        Create a new gauge metric.
        
        Args:
            name: Metric name.
            description: Metric description.
            tags: Optional tags.
            
        Returns:
            Gauge object.
        """
        with self._lock:
            if name in self.gauges:
                return self.gauges[name]
            
            gauge = Gauge(name=name, description=description, tags=tags or {})
            self.gauges[name] = gauge
            self.metadata[name] = {
                'type': 'gauge',
                'description': description,
                'tags': tags or {},
                'created_at': datetime.utcnow().isoformat(),
            }
            return gauge
    
    def get_gauge(self, name: str) -> Optional[Gauge]:
        """
        Get a gauge metric.
        
        Args:
            name: Metric name.
            
        Returns:
            Gauge object or None if not found.
        """
        return self.gauges.get(name)
    
    def set_gauge(self, name: str, value: float, tags: Dict = None):
        """
        Set a gauge metric value.
        
        Args:
            name: Metric name.
            value: Value to set.
            tags: Optional tags for this value.
        """
        gauge = self.get_gauge(name)
        if gauge:
            gauge.set(value)
            self._record_time_series(name, value, tags)
    
    def create_histogram(self, name: str, buckets: List[float], 
                        description: str = "", tags: Dict = None) -> Histogram:
        """
        Create a new histogram metric.
        
        Args:
            name: Metric name.
            buckets: List of bucket upper bounds.
            description: Metric description.
            tags: Optional tags.
            
        Returns:
            Histogram object.
        """
        with self._lock:
            if name in self.histograms:
                return self.histograms[name]
            
            histogram = Histogram(name=name, buckets=buckets, 
                                description=description, tags=tags or {})
            self.histograms[name] = histogram
            self.metadata[name] = {
                'type': 'histogram',
                'buckets': buckets,
                'description': description,
                'tags': tags or {},
                'created_at': datetime.utcnow().isoformat(),
            }
            return histogram
    
    def get_histogram(self, name: str) -> Optional[Histogram]:
        """
        Get a histogram metric.
        
        Args:
            name: Metric name.
            
        Returns:
            Histogram object or None if not found.
        """
        return self.histograms.get(name)
    
    def record_histogram(self, name: str, value: float, tags: Dict = None):
        """
        Record a value in a histogram.
        
        Args:
            name: Metric name.
            value: Value to record.
            tags: Optional tags for this value.
        """
        histogram = self.get_histogram(name)
        if histogram:
            histogram.record(value)
            self._record_time_series(name, value, tags)
    
    def create_timer(self, name: str, description: str = "", tags: Dict = None) -> Timer:
        """
        Create a new timer metric.
        
        Args:
            name: Metric name.
            description: Metric description.
            tags: Optional tags.
            
        Returns:
            Timer object.
        """
        with self._lock:
            if name in self.timers:
                return self.timers[name]
            
            timer = Timer(name=name, description=description, tags=tags or {})
            self.timers[name] = timer
            self.metadata[name] = {
                'type': 'timer',
                'description': description,
                'tags': tags or {},
                'created_at': datetime.utcnow().isoformat(),
            }
            return timer
    
    def get_timer(self, name: str) -> Optional[Timer]:
        """
        Get a timer metric.
        
        Args:
            name: Metric name.
            
        Returns:
            Timer object or None if not found.
        """
        return self.timers.get(name)
    
    def record_timer(self, name: str, duration: float, tags: Dict = None):
        """
        Record a duration in a timer.
        
        Args:
            name: Metric name.
            duration: Duration in seconds.
            tags: Optional tags for this duration.
        """
        timer = self.get_timer(name)
        if timer:
            timer.record(duration)
            self._record_time_series(name, duration, tags)
    
    def _record_time_series(self, name: str, value: Any, tags: Dict = None):
        """
        Record a time series data point.
        
        Args:
            name: Metric name.
            value: Value to record.
            tags: Optional tags.
        """
        data_point = {
            'timestamp': datetime.utcnow().isoformat(),
            'value': value,
            'tags': tags or {},
        }
        self.time_series[name].append(data_point)
    
    def get_time_series(self, name: str, start_time: datetime = None, 
                        end_time: datetime = None) -> List[Dict]:
        """
        Get time series data for a metric.
        
        Args:
            name: Metric name.
            start_time: Optional start time.
            end_time: Optional end time.
            
        Returns:
            List of time series data points.
        """
        if name not in self.time_series:
            return []
        
        data = list(self.time_series[name])
        
        if start_time or end_time:
            filtered_data = []
            for point in data:
                ts = datetime.fromisoformat(point['timestamp'])
                if start_time and ts < start_time:
                    continue
                if end_time and ts > end_time:
                    continue
                filtered_data.append(point)
            data = filtered_data
        
        return data
    
    def get_metrics(self, metric_type: str = None) -> Dict[str, Any]:
        """
        Get all metrics of a specific type.
        
        Args:
            metric_type: Optional metric type filter ('counter', 'gauge', 'histogram', 'timer').
            
        Returns:
            Dictionary with metric data.
        """
        result = {}
        
        with self._lock:
            if metric_type is None or metric_type == 'counter':
                result['counters'] = {
                    name: {
                        'value': counter.value,
                        'description': counter.description,
                        'tags': counter.tags,
                    }
                    for name, counter in self.counters.items()
                }
            
            if metric_type is None or metric_type == 'gauge':
                result['gauges'] = {
                    name: {
                        'value': gauge.value,
                        'description': gauge.description,
                        'tags': gauge.tags,
                    }
                    for name, gauge in self.gauges.items()
                }
            
            if metric_type is None or metric_type == 'histogram':
                result['histograms'] = {
                    name: {
                        'counts': histogram.counts,
                        'buckets': histogram.buckets,
                        'total_count': histogram.total_count,
                        'total_sum': histogram.total_sum,
                        'percentiles': histogram.get_percentiles(),
                        'description': histogram.description,
                        'tags': histogram.tags,
                    }
                    for name, histogram in self.histograms.items()
                }
            
            if metric_type is None or metric_type == 'timer':
                result['timers'] = {
                    name: {
                        'count': timer.total_count,
                        'total_time': timer.total_time,
                        'avg': timer.get_avg(),
                        'p50': timer.get_percentile(50),
                        'p90': timer.get_percentile(90),
                        'p99': timer.get_percentile(99),
                        'description': timer.description,
                        'tags': timer.tags,
                    }
                    for name, timer in self.timers.items()
                }
        
        return result
    
    def get_metric(self, name: str) -> Dict[str, Any]:
        """
        Get a specific metric by name.
        
        Args:
            name: Metric name.
            
        Returns:
            Dictionary with metric data.
        """
        with self._lock:
            if name in self.counters:
                counter = self.counters[name]
                return {
                    'type': 'counter',
                    'name': name,
                    'value': counter.value,
                    'description': counter.description,
                    'tags': counter.tags,
                }
            elif name in self.gauges:
                gauge = self.gauges[name]
                return {
                    'type': 'gauge',
                    'name': name,
                    'value': gauge.value,
                    'description': gauge.description,
                    'tags': gauge.tags,
                }
            elif name in self.histograms:
                histogram = self.histograms[name]
                return {
                    'type': 'histogram',
                    'name': name,
                    'counts': histogram.counts,
                    'buckets': histogram.buckets,
                    'total_count': histogram.total_count,
                    'total_sum': histogram.total_sum,
                    'percentiles': histogram.get_percentiles(),
                    'description': histogram.description,
                    'tags': histogram.tags,
                }
            elif name in self.timers:
                timer = self.timers[name]
                return {
                    'type': 'timer',
                    'name': name,
                    'count': timer.total_count,
                    'total_time': timer.total_time,
                    'avg': timer.get_avg(),
                    'p50': timer.get_percentile(50),
                    'p90': timer.get_percentile(90),
                    'p99': timer.get_percentile(99),
                    'description': timer.description,
                    'tags': timer.tags,
                }
        
        return {'error': f'Metric {name} not found'}
    
    def reset_metric(self, name: str) -> bool:
        """
        Reset a metric.
        
        Args:
            name: Metric name.
            
        Returns:
            True if reset, False if not found.
        """
        with self._lock:
            if name in self.counters:
                self.counters[name].reset()
                return True
            elif name in self.gauges:
                self.gauges[name].set(0.0)
                return True
            elif name in self.histograms:
                # Reset histogram by creating a new one
                histogram = self.histograms[name]
                histogram.counts = [0] * len(histogram.buckets)
                histogram.total_count = 0
                histogram.total_sum = 0.0
                return True
            elif name in self.timers:
                self.timers[name].durations.clear()
                self.timers[name].total_count = 0
                self.timers[name].total_time = 0.0
                return True
        
        return False
    
    def reset_all(self):
        """Reset all metrics."""
        with self._lock:
            for counter in self.counters.values():
                counter.reset()
            for gauge in self.gauges.values():
                gauge.set(0.0)
            for histogram in self.histograms.values():
                histogram.counts = [0] * len(histogram.buckets)
                histogram.total_count = 0
                histogram.total_sum = 0.0
            for timer in self.timers.values():
                timer.durations.clear()
                timer.total_count = 0
                timer.total_time = 0.0
            
            self.time_series.clear()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all metrics.
        
        Returns:
            Dictionary with summary data.
        """
        with self._lock:
            return {
                'uptime': (datetime.utcnow() - self._start_time).total_seconds(),
                'counters': {name: counter.value for name, counter in self.counters.items()},
                'gauges': {name: gauge.value for name, gauge in self.gauges.items()},
                'histograms': {
                    name: {
                        'total_count': h.total_count,
                        'total_sum': h.total_sum,
                    }
                    for name, h in self.histograms.items()
                },
                'timers': {
                    name: {
                        'count': t.total_count,
                        'avg': t.get_avg(),
                    }
                    for name, t in self.timers.items()
                },
            }
    
    def start_monitoring(self, interval: float = 60.0):
        """
        Start monitoring system metrics.
        
        Args:
            interval: Monitoring interval in seconds.
        """
        def monitor():
            """Monitor system metrics."""
            while True:
                try:
                    # Update system metrics
                    import psutil
                    
                    # CPU usage
                    cpu_percent = psutil.cpu_percent(interval=1)
                    self.set_gauge('system.cpu.usage', cpu_percent)
                    
                    # Memory usage
                    memory = psutil.virtual_memory()
                    self.set_gauge('system.memory.usage', memory.percent)
                    
                    # Disk usage
                    disk = psutil.disk_usage('/')
                    self.set_gauge('system.disk.usage', disk.percent)
                    
                except ImportError:
                    # psutil not available
                    pass
                except Exception as e:
                    print(f"Error monitoring system: {e}")
                
                time.sleep(interval)
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
        
        return monitor_thread


# Global metrics collector instance
metrics_collector = MetricsCollector()
