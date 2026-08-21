"""
In-memory ring-buffer log handler backing GET /api/system/logs.

Kept separate from the audit log on purpose: audit records user actions for
compliance; this buffer holds recent process diagnostics.
"""

import logging
import threading
from collections import deque
from datetime import datetime
from typing import Any, Dict, List, Optional


class RingBufferHandler(logging.Handler):
    """Keeps the most recent log records in memory."""

    def __init__(self, capacity: int = 1000):
        super().__init__()
        self.capacity = capacity
        self._records: deque = deque(maxlen=capacity)
        self._buffer_lock = threading.Lock()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            entry = {
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'timestamp': datetime.utcfromtimestamp(record.created).isoformat(),
            }
        except Exception:
            return
        with self._buffer_lock:
            self._records.append(entry)

    def tail(self, level: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Most recent records, newest last, optionally filtered by level."""
        with self._buffer_lock:
            records = list(self._records)
        if level:
            wanted = level.upper()
            threshold = logging.getLevelName(wanted)
            if isinstance(threshold, int):
                records = [r for r in records
                           if logging.getLevelName(r['level']) >= threshold]
            else:
                records = [r for r in records if r['level'] == wanted]
        return records[-max(0, limit):]


ring_buffer = RingBufferHandler()


def install_ring_buffer(level: int = logging.INFO) -> RingBufferHandler:
    """Attach the ring buffer to the root logger (idempotent)."""
    root = logging.getLogger()
    if ring_buffer not in root.handlers:
        ring_buffer.setLevel(level)
        root.addHandler(ring_buffer)
        if root.level > level or root.level == logging.NOTSET:
            root.setLevel(level)
    return ring_buffer
