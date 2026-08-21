"""
Logger for OpenLens

Provides structured logging with:
- File logging
- Console logging
- JSON formatting
- Log rotation

Dependencies:
- logging: Python built-in logging
- python-json-logger: For JSON formatting (optional)
"""

import os
import sys
import logging
import logging.handlers
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import json

# Try to import json logger
try:
    from pythonjsonlogger import jsonlogger
    JSON_LOGGER_AVAILABLE = True
except ImportError:
    JSON_LOGGER_AVAILABLE = False


class LoggingConfig:
    """Logging configuration."""
    
    # Log levels
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    # Default configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT = os.getenv('LOG_FORMAT', 'json')  # 'json', 'text', 'simple'
    LOG_DIR = os.getenv('LOG_DIR', './logs')
    LOG_FILE = os.getenv('LOG_FILE', 'openlens.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    LOG_CONSOLE = os.getenv('LOG_CONSOLE', 'true').lower() == 'true'
    
    @classmethod
    def get_log_level(cls) -> int:
        """Get log level from string."""
        level = getattr(cls, cls.LOG_LEVEL, cls.INFO)
        return level if isinstance(level, int) else cls.INFO


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured logs."""
    
    def __init__(self, fmt: str = None, datefmt: str = None, style: str = '%'):
        super().__init__(fmt, datefmt, style)
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record."""
        # Add additional fields
        record.asctime = datetime.utcnow().isoformat()
        
        # Ensure all fields are strings
        for attr in dir(record):
            if not attr.startswith('_') and not callable(getattr(record, attr)):
                value = getattr(record, attr)
                if not isinstance(value, (str, int, float, bool, type(None))):
                    try:
                        setattr(record, attr, str(value))
                    except:
                        setattr(record, attr, '<unserializable>')
        
        # Use parent format
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for logs."""
    
    def __init__(self):
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'level_num': record.levelno,
            'message': record.getMessage(),
            'logger': record.name,
            'thread': record.threadName,
            'process': record.processName,
        }
        
        # Add exception info
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add stack info
        if record.stack_info:
            log_data['stack_info'] = self.formatStack(record.stack_info)
        
        # Add extra fields
        extra_fields = {}
        for key, value in record.__dict__.items():
            if key not in (
                'name', 'msg', 'args', 'created', 'filename', 'funcName',
                'levelname', 'levelno', 'lineno', 'module', 'msecs',
                'pathname', 'process', 'processName', 'relativeCreated',
                'stack_info', 'exc_info', 'exc_text', 'thread', 'threadName',
                'message', 'asctime', 'timestamp'
            ):
                try:
                    if not callable(value):
                        extra_fields[key] = value
                except:
                    pass
        
        if extra_fields:
            log_data['extra'] = extra_fields
        
        return json.dumps(log_data, default=str)


# Global logger instance
_logger = None


def setup_logging(config: LoggingConfig = None) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        config: Logging configuration (defaults to LoggingConfig).
        
    Returns:
        Configured logger.
    """
    global _logger
    
    if config is None:
        config = LoggingConfig()
    
    # Create logger
    logger = logging.getLogger('openlens')
    logger.setLevel(config.get_log_level())
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
    
    # Create log directory
    log_dir = Path(config.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create formatter
    if config.LOG_FORMAT == 'json' and JSON_LOGGER_AVAILABLE:
        formatter = JSONFormatter()
    elif config.LOG_FORMAT == 'json':
        # Fall back to simple JSON
        formatter = JSONFormatter()
    elif config.LOG_FORMAT == 'simple':
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    else:
        # Default text format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(threadName)s - %(message)s'
        )
    
    # File handler (rotating)
    log_file = log_dir / config.LOG_FILE
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding='utf-8',
    )
    file_handler.setLevel(config.get_log_level())
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    if config.LOG_CONSOLE:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(config.get_log_level())
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Set global logger
    _logger = logger
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (defaults to 'openlens').
        
    Returns:
        Logger instance.
    """
    global _logger
    
    if _logger is None:
        _logger = setup_logging()
    
    if name:
        return _logger.getChild(name)
    return _logger


# Initialize logger on import
_logger = setup_logging()
