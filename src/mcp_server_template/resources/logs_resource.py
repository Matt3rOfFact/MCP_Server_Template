"""Logs resource for accessing recent log entries."""

from typing import List, Dict, Any, Optional
from collections import deque
from datetime import datetime
from mcp.types import Resource
import json
import logging


class LogsResource:
    """Resource for log information."""
    
    def __init__(self, max_logs: int = 100):
        """
        Initialize the logs resource.
        
        Args:
            max_logs: Maximum number of log entries to keep
        """
        self.max_logs = max_logs
        self.log_buffer = deque(maxlen=max_logs)
        self._setup_handler()
    
    def _setup_handler(self):
        """Set up a custom log handler to capture logs."""
        handler = BufferHandler(self.log_buffer)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        
        # Add handler to root logger
        logging.getLogger().addHandler(handler)
    
    async def get_recent_logs(self, count: int = 50) -> Resource:
        """
        Get recent log entries.
        
        Args:
            count: Number of recent logs to return
            
        Returns:
            Resource containing recent log entries
        """
        # Get the most recent logs
        logs = list(self.log_buffer)[-count:]
        
        logs_data = {
            "total_captured": len(self.log_buffer),
            "returned_count": len(logs),
            "max_buffer_size": self.max_logs,
            "logs": logs
        }
        
        return Resource(
            uri="logs://recent",
            name="Recent Logs",
            description=f"Last {len(logs)} log entries",
            mimeType="application/json",
            text=json.dumps(logs_data, indent=2)
        )
    
    async def get_filtered_logs(
        self,
        level: Optional[str] = None,
        logger_name: Optional[str] = None,
        message_contains: Optional[str] = None
    ) -> Resource:
        """
        Get filtered log entries.
        
        Args:
            level: Filter by log level
            logger_name: Filter by logger name
            message_contains: Filter by message content
            
        Returns:
            Resource containing filtered log entries
        """
        logs = list(self.log_buffer)
        
        # Apply filters
        if level:
            logs = [log for log in logs if log.get("level") == level.upper()]
        
        if logger_name:
            logs = [log for log in logs if logger_name in log.get("logger", "")]
        
        if message_contains:
            logs = [log for log in logs if message_contains.lower() in log.get("message", "").lower()]
        
        logs_data = {
            "filters": {
                "level": level,
                "logger_name": logger_name,
                "message_contains": message_contains
            },
            "matched_count": len(logs),
            "logs": logs
        }
        
        return Resource(
            uri="logs://filtered",
            name="Filtered Logs",
            description="Filtered log entries",
            mimeType="application/json",
            text=json.dumps(logs_data, indent=2)
        )


class BufferHandler(logging.Handler):
    """Custom log handler that stores logs in a buffer."""
    
    def __init__(self, buffer: deque):
        """
        Initialize the buffer handler.
        
        Args:
            buffer: Deque to store log entries
        """
        super().__init__()
        self.buffer = buffer
    
    def emit(self, record: logging.LogRecord):
        """
        Emit a log record to the buffer.
        
        Args:
            record: Log record to emit
        """
        try:
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": self.format(record),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno
            }
            
            # Add exception info if present
            if record.exc_info:
                log_entry["exception"] = self.format(record)
            
            self.buffer.append(log_entry)
        except Exception:
            self.handleError(record)