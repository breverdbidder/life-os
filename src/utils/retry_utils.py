"""
Retry Utilities with Exponential Backoff
Wraps tenacity with logging and metrics

Usage:
    from src.utils.retry_utils import retry_with_backoff
    
    @retry_with_backoff(operation_name="bcpao_api_call")
    def fetch_property_data(parcel_id):
        response = requests.get(f"https://api.bcpao.us/{parcel_id}")
        response.raise_for_status()
        return response.json()
"""

from functools import wraps
from typing import Callable, Any
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)
import logging
from src.utils.structured_logger import get_logger
from src.utils.metrics_publisher import get_metrics
from src.utils.error_tracker import track_error
import time

logger = get_logger(__name__)
metrics = get_metrics()

def retry_with_backoff(
    max_attempts: int = 3,
    min_wait: int = 4,
    max_wait: int = 10,
    operation_name: str = None,
    stage: str = None,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying operations with exponential backoff
    
    Args:
        max_attempts: Maximum retry attempts
        min_wait: Minimum wait time in seconds
        max_wait: Maximum wait time in seconds
        operation_name: Name for logging/metrics
        stage: Pipeline stage
        exceptions: Tuple of exceptions to retry on
    
    Example:
        @retry_with_backoff(
            max_attempts=5,
            operation_name="acclaimweb_scrape",
            stage="lien_discovery"
        )
        def scrape_acclaimweb(url):
            return requests.get(url).json()
    """
    
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type(exceptions),
            before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING)
        )
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Record success metrics
                duration_ms = (time.time() - start_time) * 1000
                metrics.record_latency(
                    operation=op_name,
                    latency_ms=duration_ms,
                    stage=stage
                )
                metrics.record_success(
                    operation=op_name,
                    stage=stage
                )
                
                logger.debug(
                    "Operation succeeded",
                    operation=op_name,
                    duration_ms=round(duration_ms, 2)
                )
                
                return result
                
            except Exception as e:
                # Record error
                duration_ms = (time.time() - start_time) * 1000
                
                track_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stage=stage,
                    operation=op_name,
                    exception=e
                )
                
                metrics.record_error(
                    error_type=type(e).__name__,
                    error_source=op_name,
                    stage=stage
                )
                
                logger.error(
                    "Operation failed after retries",
                    operation=op_name,
                    error=str(e),
                    duration_ms=round(duration_ms, 2)
                )
                
                raise
        
        return wrapper
    return decorator


def retry_async_with_backoff(
    max_attempts: int = 3,
    min_wait: int = 4,
    max_wait: int = 10,
    operation_name: str = None,
    stage: str = None,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying async operations with exponential backoff
    
    Args:
        max_attempts: Maximum retry attempts
        min_wait: Minimum wait time in seconds
        max_wait: Maximum wait time in seconds
        operation_name: Name for logging/metrics
        stage: Pipeline stage
        exceptions: Tuple of exceptions to retry on
    
    Example:
        @retry_async_with_backoff(
            max_attempts=5,
            operation_name="async_api_call"
        )
        async def fetch_data(url):
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                return response.json()
    """
    
    def decorator(func: Callable) -> Callable:
        op_name = operation_name or func.__name__
        
        @retry(
            stop=stop_after_attempt(max_attempts),
            wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
            retry=retry_if_exception_type(exceptions),
            before_sleep=before_sleep_log(logging.getLogger(__name__), logging.WARNING)
        )
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record success metrics
                duration_ms = (time.time() - start_time) * 1000
                metrics.record_latency(
                    operation=op_name,
                    latency_ms=duration_ms,
                    stage=stage
                )
                metrics.record_success(
                    operation=op_name,
                    stage=stage
                )
                
                logger.debug(
                    "Async operation succeeded",
                    operation=op_name,
                    duration_ms=round(duration_ms, 2)
                )
                
                return result
                
            except Exception as e:
                # Record error
                duration_ms = (time.time() - start_time) * 1000
                
                track_error(
                    error_type=type(e).__name__,
                    error_message=str(e),
                    stage=stage,
                    operation=op_name,
                    exception=e
                )
                
                metrics.record_error(
                    error_type=type(e).__name__,
                    error_source=op_name,
                    stage=stage
                )
                
                logger.error(
                    "Async operation failed after retries",
                    operation=op_name,
                    error=str(e),
                    duration_ms=round(duration_ms, 2)
                )
                
                raise
        
        return wrapper
    return decorator
