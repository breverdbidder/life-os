"""
Structured Logger with Correlation ID Tracking
Adapted from AWS Bedrock Agent patterns for BidDeed.AI stack

Usage:
    from src.utils.structured_logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Operation started", stage="lien_discovery", property_id="12345")
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Any, Dict, Optional
from contextvars import ContextVar
import os

# Context variable for correlation ID (thread-safe)
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default=None)

class StructuredLogger:
    """Enhanced logger with structured JSON output and correlation tracking"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.name = name
    
    def set_correlation_id(self, correlation_id: str = None) -> str:
        """Set correlation ID for request tracing"""
        cid = correlation_id or f"corr-{uuid.uuid4().hex[:12]}"
        correlation_id_var.set(cid)
        return cid
    
    def get_correlation_id(self) -> Optional[str]:
        """Get current correlation ID"""
        return correlation_id_var.get(None)
    
    def _log(self, level: str, message: str, **kwargs):
        """Internal logging with structured data"""
        log_data = {
            "message": message,
            "correlation_id": self.get_correlation_id(),
            "timestamp": datetime.utcnow().isoformat(),
            "logger": self.name,
            **kwargs
        }
        
        # Log structured JSON
        log_method = getattr(self.logger, level)
        log_method(json.dumps(log_data, default=str))
    
    def info(self, message: str, **kwargs):
        """Log info level message"""
        self._log("info", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error level message"""
        self._log("error", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning level message"""
        self._log("warning", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug level message"""
        self._log("debug", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical level message"""
        self._log("critical", message, **kwargs)


# Global logger cache
_loggers: Dict[str, StructuredLogger] = {}

def get_logger(name: str, level: str = "INFO") -> StructuredLogger:
    """
    Get or create a structured logger
    
    Args:
        name: Logger name (typically __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        StructuredLogger instance
    """
    if name not in _loggers:
        _loggers[name] = StructuredLogger(name, level)
    return _loggers[name]


def set_correlation_id(correlation_id: str = None) -> str:
    """
    Set global correlation ID for request tracing
    
    Args:
        correlation_id: Optional correlation ID (auto-generated if None)
    
    Returns:
        The correlation ID that was set
    """
    cid = correlation_id or f"corr-{uuid.uuid4().hex[:12]}"
    correlation_id_var.set(cid)
    return cid


def get_correlation_id() -> Optional[str]:
    """Get current correlation ID"""
    return correlation_id_var.get(None)
