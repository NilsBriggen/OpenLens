"""
API Analytics for OpenLens

Tracks and analyzes API usage patterns.
"""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import json

from .logger import get_logger


class APIAnalytics:
    """
    Tracks and analyzes API usage.
    """
    
    def __init__(self):
        """Initialize API analytics."""
        self.logger = get_logger('analytics')
        self.requests = []
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0,
            'success_count': 0,
            'error_count': 0,
            'last_request': None,
        })
        self.user_stats = defaultdict(lambda: {
            'count': 0,
            'last_request': None,
        })
        self.start_time = datetime.utcnow()
    
    def track_request(self, request_data: Dict):
        """
        Track an API request.
        
        Args:
            request_data: Dictionary with request data.
        """
        try:
            # Store request
            self.requests.append(request_data)
            
            # Update endpoint stats
            endpoint = request_data.get('endpoint', 'unknown')
            method = request_data.get('method', 'GET')
            status_code = request_data.get('status_code', 200)
            duration_ms = request_data.get('duration_ms', 0)
            
            endpoint_key = f"{method}:{endpoint}"
            
            self.endpoint_stats[endpoint_key]['count'] += 1
            self.endpoint_stats[endpoint_key]['total_duration'] += duration_ms
            self.endpoint_stats[endpoint_key]['last_request'] = datetime.utcnow().isoformat()
            
            if 200 <= status_code < 400:
                self.endpoint_stats[endpoint_key]['success_count'] += 1
            else:
                self.endpoint_stats[endpoint_key]['error_count'] += 1
            
            # Update user stats
            user_id = request_data.get('user_id')
            if user_id:
                self.user_stats[user_id]['count'] += 1
                self.user_stats[user_id]['last_request'] = datetime.utcnow().isoformat()
            
            # Log analytics
            self.logger.info(f"Tracked request: {endpoint_key}", extra={
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'duration_ms': duration_ms,
            })
        except Exception as e:
            self.logger.error(f"Failed to track request: {e}")
    
    def get_stats(self, time_range: str = 'all') -> Dict[str, Any]:
        """
        Get API usage statistics.
        
        Args:
            time_range: Time range ('all', 'hour', 'day', 'week', 'month').
            
        Returns:
            Dictionary with statistics.
        """
        # Filter requests by time range
        filtered_requests = self._filter_by_time_range(self.requests, time_range)
        
        # Calculate stats
        total_requests = len(filtered_requests)
        
        # Count by endpoint
        endpoint_counts = defaultdict(int)
        for req in filtered_requests:
            endpoint_key = f"{req.get('method', 'GET')}:{req.get('endpoint', 'unknown')}"
            endpoint_counts[endpoint_key] += 1
        
        # Count by status code
        status_counts = defaultdict(int)
        for req in filtered_requests:
            status_code = req.get('status_code', 200)
            status_counts[status_code] += 1
        
        # Calculate average duration
        total_duration = sum(req.get('duration_ms', 0) for req in filtered_requests)
        avg_duration = total_duration / total_requests if total_requests > 0 else 0
        
        # Get top endpoints
        top_endpoints = sorted(
            endpoint_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        # Get top users
        top_users = sorted(
            self.user_stats.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        return {
            'time_range': time_range,
            'total_requests': total_requests,
            'total_duration_ms': total_duration,
            'average_duration_ms': avg_duration,
            'top_endpoints': [{'endpoint': ep[0], 'count': ep[1]} for ep in top_endpoints],
            'status_counts': dict(status_counts),
            'top_users': [{'user_id': user[0], 'count': user[1]['count']} for user in top_users],
            'start_time': self.start_time.isoformat(),
            'current_time': datetime.utcnow().isoformat(),
        }
    
    def get_endpoint_stats(self, endpoint: str = None, method: str = None) -> Dict[str, Any]:
        """
        Get statistics for a specific endpoint.
        
        Args:
            endpoint: Endpoint path.
            method: HTTP method.
            
        Returns:
            Dictionary with endpoint statistics.
        """
        if endpoint and method:
            endpoint_key = f"{method}:{endpoint}"
            return dict(self.endpoint_stats.get(endpoint_key, {}))
        elif endpoint:
            # Return stats for all methods on this endpoint
            result = {}
            for key, stats in self.endpoint_stats.items():
                if key.endswith(f":{endpoint}"):
                    result[key] = dict(stats)
            return result
        else:
            # Return all endpoint stats
            return {k: dict(v) for k, v in self.endpoint_stats.items()}
    
    def get_user_stats(self, user_id: str = None) -> Dict[str, Any]:
        """
        Get statistics for a specific user.
        
        Args:
            user_id: User ID.
            
        Returns:
            Dictionary with user statistics.
        """
        if user_id:
            return dict(self.user_stats.get(user_id, {}))
        else:
            return {k: dict(v) for k, v in self.user_stats.items()}
    
    def _filter_by_time_range(self, requests: List[Dict], time_range: str) -> List[Dict]:
        """Filter requests by time range."""
        if time_range == 'all':
            return requests
        
        now = datetime.utcnow()
        
        if time_range == 'hour':
            cutoff = now - timedelta(hours=1)
        elif time_range == 'day':
            cutoff = now - timedelta(days=1)
        elif time_range == 'week':
            cutoff = now - timedelta(weeks=1)
        elif time_range == 'month':
            cutoff = now - timedelta(days=30)
        else:
            return requests
        
        return [
            req for req in requests
            if datetime.fromisoformat(req.get('timestamp', now.isoformat())) >= cutoff
        ]
    
    def reset(self):
        """Reset all statistics."""
        self.requests = []
        self.endpoint_stats = defaultdict(lambda: {
            'count': 0,
            'total_duration': 0,
            'success_count': 0,
            'error_count': 0,
            'last_request': None,
        })
        self.user_stats = defaultdict(lambda: {
            'count': 0,
            'last_request': None,
        })
        self.start_time = datetime.utcnow()


# Global analytics instance
analytics = APIAnalytics()


def get_analytics() -> APIAnalytics:
    """Get the global analytics instance."""
    return analytics
