"""
Error Tracking for Supabase
Centralized error logging with categorization and analysis

Usage:
    from src.utils.error_tracker import track_error
    
    try:
        result = risky_operation()
    except Exception as e:
        track_error(
            error_type="api_timeout",
            error_message=str(e),
            stage="lien_discovery",
            metadata={"url": "https://acclaimweb.com"}
        )
        raise
"""

import os
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from supabase import create_client, Client
from src.utils.structured_logger import get_logger, get_correlation_id

logger = get_logger(__name__)

class ErrorTracker:
    """Track errors to Supabase for analysis and monitoring"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co"),
            os.getenv("SUPABASE_KEY", "")
        )
        self.enabled = bool(os.getenv("SUPABASE_KEY"))
        
        if not self.enabled:
            logger.warning("Error tracking disabled - SUPABASE_KEY not set")
    
    def track(
        self,
        error_type: str,
        error_message: str,
        stage: str = None,
        operation: str = None,
        severity: str = "error",
        metadata: Dict[str, Any] = None,
        exception: Exception = None
    ):
        """
        Track error to Supabase
        
        Args:
            error_type: Error category (e.g., "api_timeout", "validation_failed")
            error_message: Error description
            stage: Pipeline stage where error occurred
            operation: Specific operation (e.g., "bcpao_api_call")
            severity: Error severity (debug, info, warning, error, critical)
            metadata: Additional context
            exception: Original exception object (for stack trace)
        """
        if not self.enabled:
            return
        
        try:
            error_data = {
                "error_type": error_type,
                "error_message": error_message,
                "stage": stage,
                "operation": operation,
                "severity": severity,
                "correlation_id": get_correlation_id(),
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add stack trace if exception provided
            if exception:
                error_data["stack_trace"] = "".join(
                    traceback.format_exception(
                        type(exception),
                        exception,
                        exception.__traceback__
                    )
                )
            
            self.supabase.table("errors").insert(error_data).execute()
            
            logger.debug(
                "Error tracked",
                error_type=error_type,
                stage=stage,
                operation=operation
            )
            
        except Exception as e:
            logger.error(
                "Failed to track error",
                error=str(e),
                original_error=error_type
            )


# Global error tracker instance
_error_tracker: Optional[ErrorTracker] = None

def get_error_tracker() -> ErrorTracker:
    """Get or create global error tracker"""
    global _error_tracker
    if _error_tracker is None:
        _error_tracker = ErrorTracker()
    return _error_tracker


def track_error(
    error_type: str,
    error_message: str,
    stage: str = None,
    operation: str = None,
    severity: str = "error",
    metadata: Dict[str, Any] = None,
    exception: Exception = None
):
    """
    Convenience function to track error
    
    Args:
        error_type: Error category
        error_message: Error description
        stage: Pipeline stage
        operation: Specific operation
        severity: Error severity
        metadata: Additional context
        exception: Original exception
    """
    tracker = get_error_tracker()
    tracker.track(
        error_type=error_type,
        error_message=error_message,
        stage=stage,
        operation=operation,
        severity=severity,
        metadata=metadata,
        exception=exception
    )
