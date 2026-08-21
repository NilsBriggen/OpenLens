"""
Query Optimizer for OpenLens

Provides query optimization for:
- Database queries (SQLAlchemy, raw SQL)
- API requests
- Scraping operations
- NLP processing
"""

from typing import Dict, List, Any, Optional, Callable, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from functools import wraps
import time
import re


@dataclass
class QueryPlan:
    """Represents an optimized query plan."""
    original_query: str
    optimized_query: str
    execution_time: float = 0.0
    estimated_cost: float = 0.0
    indexes_used: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'original_query': self.original_query,
            'optimized_query': self.optimized_query,
            'execution_time': self.execution_time,
            'estimated_cost': self.estimated_cost,
            'indexes_used': self.indexes_used,
            'warnings': self.warnings,
        }


class QueryOptimizer:
    """
    Optimizes database queries and other operations.
    """
    
    def __init__(self):
        """Initialize the query optimizer."""
        self.query_cache: Dict[str, QueryPlan] = {}
        self.index_hints: Dict[str, List[str]] = {}
        self.slow_queries: Dict[str, List[float]] = {}
    
    def optimize_sql_query(self, query: str, table_info: Dict = None) -> QueryPlan:
        """
        Optimize a SQL query.
        
        Args:
            query: SQL query to optimize.
            table_info: Optional dictionary with table information.
            
        Returns:
            QueryPlan with optimized query.
        """
        original_query = query
        optimized_query = query
        warnings = []
        
        # Convert to lowercase for case-insensitive matching
        query_lower = query.lower()
        
        # 1. Add missing WHERE clauses for full table scans
        if 'select' in query_lower and 'where' not in query_lower and 'limit' not in query_lower:
            warnings.append("Query has no WHERE clause and no LIMIT - consider adding filters")
        
        # 2. Check for SELECT *
        if re.search(r'select\s+\*', query_lower):
            warnings.append("Query uses SELECT * - consider specifying columns")
        
        # 3. Check for ORDER BY without LIMIT
        if 'order by' in query_lower and 'limit' not in query_lower:
            warnings.append("Query has ORDER BY but no LIMIT - consider adding LIMIT")
        
        # 4. Check for N+1 query patterns
        if self._detect_n_plus_1(query_lower):
            warnings.append("Potential N+1 query pattern detected")
        
        # 5. Add indexes if table info is provided
        if table_info:
            optimized_query = self._add_index_hints(query, table_info)
        
        # 6. Reorder JOINs for better performance
        optimized_query = self._reorder_joins(optimized_query)
        
        return QueryPlan(
            original_query=original_query,
            optimized_query=optimized_query,
            warnings=warnings,
        )
    
    def _detect_n_plus_1(self, query: str) -> bool:
        """Detect N+1 query patterns."""
        # Simple heuristic: multiple similar SELECT statements
        select_count = query.count('select')
        return select_count > 1
    
    def _add_index_hints(self, query: str, table_info: Dict) -> str:
        """Add index hints to the query."""
        # This is a simplified version - in a real implementation,
        # you would analyze the query and add appropriate index hints
        return query
    
    def _reorder_joins(self, query: str) -> str:
        """Reorder JOINs for better performance."""
        # This is a simplified version - in a real implementation,
        # you would analyze the join order and reorder based on table sizes
        return query
    
    def optimize_sqlalchemy_query(self, query, session, table_info: Dict = None) -> Tuple[Any, QueryPlan]:
        """
        Optimize a SQLAlchemy query.
        
        Args:
            query: SQLAlchemy query object.
            session: SQLAlchemy session.
            table_info: Optional dictionary with table information.
            
        Returns:
            Tuple of (optimized query, QueryPlan).
        """
        # Get the SQL string
        sql_str = str(query.statement.compile(dialect=session.bind.dialect))
        
        # Optimize the SQL
        plan = self.optimize_sql_query(sql_str, table_info)
        
        # For now, just return the original query
        # In a real implementation, you would modify the query based on the plan
        return query, plan
    
    def analyze_query_performance(self, query: str, execution_time: float) -> QueryPlan:
        """
        Analyze query performance.
        
        Args:
            query: SQL query.
            execution_time: Execution time in seconds.
            
        Returns:
            QueryPlan with performance analysis.
        """
        # Track slow queries
        if execution_time > 1.0:  # More than 1 second
            if query not in self.slow_queries:
                self.slow_queries[query] = []
            self.slow_queries[query].append(execution_time)
            
            # Keep only the last 100 executions
            if len(self.slow_queries[query]) > 100:
                self.slow_queries[query] = self.slow_queries[query][-100:]
        
        # Generate warnings based on execution time
        warnings = []
        if execution_time > 5.0:
            warnings.append(f"Query took {execution_time:.2f}s - consider optimizing")
        elif execution_time > 1.0:
            warnings.append(f"Query took {execution_time:.2f}s - monitor performance")
        
        return QueryPlan(
            original_query=query,
            optimized_query=query,
            execution_time=execution_time,
            warnings=warnings,
        )
    
    def get_slow_queries(self, threshold: float = 1.0, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the slowest queries.
        
        Args:
            threshold: Minimum execution time threshold.
            limit: Maximum number of queries to return.
            
        Returns:
            List of slow query information.
        """
        slow_queries = []
        
        for query, times in self.slow_queries.items():
            avg_time = sum(times) / len(times)
            if avg_time >= threshold:
                slow_queries.append({
                    'query': query[:100] + '...' if len(query) > 100 else query,
                    'count': len(times),
                    'avg_time': avg_time,
                    'max_time': max(times),
                    'min_time': min(times),
                })
        
        # Sort by average time (descending)
        slow_queries.sort(key=lambda x: x['avg_time'], reverse=True)
        
        return slow_queries[:limit]
    
    def suggest_indexes(self, query: str, table_info: Dict) -> List[Dict[str, Any]]:
        """
        Suggest indexes for a query.
        
        Args:
            query: SQL query.
            table_info: Dictionary with table information.
            
        Returns:
            List of index suggestions.
        """
        suggestions = []
        query_lower = query.lower()
        
        # 1. Check for WHERE clauses
        where_match = re.search(r'where\s+(.+?)(?:\s+(order|group|limit|having)|$)', query_lower, re.IGNORECASE)
        if where_match:
            where_clause = where_match.group(1)
            
            # Extract column names from WHERE clause
            columns = re.findall(r'(\w+)\s*(?:=|<>|!=|>|<|>=|<=|like|in)', where_clause)
            
            for column in columns:
                # Check if column is in a table with many rows
                for table_name, table_data in table_info.items():
                    if column in table_data.get('columns', {}):
                        if table_data.get('row_count', 0) > 10000:
                            suggestions.append({
                                'table': table_name,
                                'column': column,
                                'type': 'index',
                                'reason': f"Column used in WHERE clause on table with {table_data.get('row_count', 0)} rows",
                            })
        
        # 2. Check for JOIN conditions
        join_matches = re.findall(r'join\s+(\w+)\s+on\s+(.+?)(?:\s+(join|where|order|group)|$)', query_lower, re.IGNORECASE)
        for join_match in join_matches:
            table_name = join_match[0]
            on_clause = join_match[1]
            
            # Extract columns from ON clause
            columns = re.findall(r'(\w+)\s*=', on_clause)
            
            for column in columns:
                if column in table_info.get(table_name, {}).get('columns', {}):
                    suggestions.append({
                        'table': table_name,
                        'column': column,
                        'type': 'index',
                        'reason': 'Column used in JOIN condition',
                    })
        
        # 3. Check for ORDER BY columns
        order_match = re.search(r'order\s+by\s+(.+?)(?:\s+(limit|having)|$)', query_lower, re.IGNORECASE)
        if order_match:
            order_clause = order_match.group(1)
            columns = re.findall(r'(\w+)', order_clause)
            
            for column in columns:
                for table_name, table_data in table_info.items():
                    if column in table_data.get('columns', {}):
                        if table_data.get('row_count', 0) > 10000:
                            suggestions.append({
                                'table': table_name,
                                'column': column,
                                'type': 'index',
                                'reason': f"Column used in ORDER BY on table with {table_data.get('row_count', 0)} rows",
                            })
        
        return suggestions
    
    def batch_optimize(self, queries: List[str], table_info: Dict = None) -> List[QueryPlan]:
        """
        Optimize multiple queries.
        
        Args:
            queries: List of SQL queries.
            table_info: Optional dictionary with table information.
            
        Returns:
            List of QueryPlan objects.
        """
        return [self.optimize_sql_query(query, table_info) for query in queries]
    
    def get_optimization_report(self) -> Dict[str, Any]:
        """
        Get a report on query optimizations.
        
        Returns:
            Dictionary with optimization report.
        """
        return {
            'cached_queries': len(self.query_cache),
            'slow_queries': len(self.slow_queries),
            'index_hints': len(self.index_hints),
            'slowest_queries': self.get_slow_queries(),
        }


class QueryProfiler:
    """
    Profiles query execution.
    """
    
    def __init__(self):
        """Initialize the query profiler."""
        self.query_times: Dict[str, List[float]] = {}
        self.current_query: str = ""
        self.start_time: float = 0
    
    def start(self, query: str):
        """
        Start profiling a query.
        
        Args:
            query: Query to profile.
        """
        self.current_query = query
        self.start_time = time.time()
    
    def stop(self) -> float:
        """
        Stop profiling and record the time.
        
        Returns:
            Execution time in seconds.
        """
        execution_time = time.time() - self.start_time
        
        if self.current_query:
            if self.current_query not in self.query_times:
                self.query_times[self.current_query] = []
            self.query_times[self.current_query].append(execution_time)
        
        self.current_query = ""
        self.start_time = 0
        
        return execution_time
    
    def profile(self, query: str):
        """
        Context manager for profiling a query.
        
        Args:
            query: Query to profile.
            
        Returns:
            Context manager.
        """
        return QueryProfileContext(self, query)
    
    def get_stats(self, query: str = None) -> Dict[str, Any]:
        """
        Get statistics for a query or all queries.
        
        Args:
            query: Optional specific query.
            
        Returns:
            Dictionary with statistics.
        """
        if query:
            times = self.query_times.get(query, [])
            if not times:
                return {'error': 'Query not found'}
            
            return {
                'query': query,
                'count': len(times),
                'avg_time': sum(times) / len(times),
                'min_time': min(times),
                'max_time': max(times),
                'total_time': sum(times),
            }
        else:
            return {
                query: {
                    'count': len(times),
                    'avg_time': sum(times) / len(times) if times else 0,
                    'min_time': min(times) if times else 0,
                    'max_time': max(times) if times else 0,
                    'total_time': sum(times),
                }
                for query, times in self.query_times.items()
            }


class QueryProfileContext:
    """Context manager for query profiling."""
    
    def __init__(self, profiler: QueryProfiler, query: str):
        """
        Initialize the context manager.
        
        Args:
            profiler: QueryProfiler instance.
            query: Query to profile.
        """
        self.profiler = profiler
        self.query = query
    
    def __enter__(self):
        """Enter the context."""
        self.profiler.start(self.query)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        self.profiler.stop()


# Global query optimizer instance
query_optimizer = QueryOptimizer()


# Decorator for profiling function execution
def profile_query(func):
    """
    Decorator to profile function execution time.
    
    Args:
        func: Function to profile.
        
    Returns:
        Decorator function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        # Get function name for caching
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Record execution time
        if func_name not in query_optimizer.slow_queries:
            query_optimizer.slow_queries[func_name] = []
        query_optimizer.slow_queries[func_name].append(execution_time)
        
        # Keep only the last 100 executions
        if len(query_optimizer.slow_queries[func_name]) > 100:
            query_optimizer.slow_queries[func_name] = query_optimizer.slow_queries[func_name][-100:]
        
        return result
    
    return wrapper
