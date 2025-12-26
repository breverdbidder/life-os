"""
Metrics Publisher for Supabase
Tracks operation latency, errors, and success rates

Usage:
    from src.utils.metrics_publisher import MetricsPublisher
    
    metrics = MetricsPublisher()
    metrics.record_latency("lien_discovery", 1234.5)
    metrics.record_error("beca_scraper", "timeout")
    metrics.record_success("stage_1_complete", metadata={"properties": 19})
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from supabase import create_client, Client
from src.utils.structured_logger import get_logger, get_correlation_id

logger = get_logger(__name__)

class MetricsPublisher:
    """Publish metrics to Supabase for monitoring and analysis"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co"),
            os.getenv("SUPABASE_KEY", "")
        )
        self.enabled = bool(os.getenv("SUPABASE_KEY"))
        
        if not self.enabled:
            logger.warning("Metrics disabled - SUPABASE_KEY not set")
    
    def _publish(
        self,
        metric_name: str,
        value: float,
        unit: str = "Count",
        operation: str = None,
        stage: str = None,
        success: bool = None,
        metadata: Dict[str, Any] = None
    ):
        """Internal method to publish metric to Supabase"""
        if not self.enabled:
            return
        
        try:
            metric_data = {
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "operation": operation,
                "stage": stage,
                "success": success,
                "correlation_id": get_correlation_id(),
                "metadata": metadata or {},
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.supabase.table("metrics").insert(metric_data).execute()
            
            logger.debug(
                "Metric published",
                metric_name=metric_name,
                value=value,
                operation=operation
            )
            
        except Exception as e:
            logger.error(
                "Failed to publish metric",
                error=str(e),
                metric_name=metric_name
            )
    
    def record_latency(
        self,
        operation: str,
        latency_ms: float,
        stage: str = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Record operation latency
        
        Args:
            operation: Operation name (e.g., "lien_discovery", "bcpao_api_call")
            latency_ms: Latency in milliseconds
            stage: Pipeline stage (e.g., "stage_3")
            metadata: Additional context
        """
        self._publish(
            metric_name="operation_latency",
            value=latency_ms,
            unit="Milliseconds",
            operation=operation,
            stage=stage,
            metadata=metadata
        )
    
    def record_error(
        self,
        error_type: str,
        error_source: str = None,
        stage: str = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Record error occurrence
        
        Args:
            error_type: Type of error (e.g., "timeout", "validation_failed")
            error_source: Source of error (e.g., "beca_scraper", "bcpao_api")
            stage: Pipeline stage where error occurred
            metadata: Error details
        """
        self._publish(
            metric_name="error",
            value=1,
            unit="Count",
            operation=error_source,
            stage=stage,
            success=False,
            metadata=metadata or {"error_type": error_type}
        )
    
    def record_success(
        self,
        operation: str,
        stage: str = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Record successful operation
        
        Args:
            operation: Operation name
            stage: Pipeline stage
            metadata: Success details
        """
        self._publish(
            metric_name="success",
            value=1,
            unit="Count",
            operation=operation,
            stage=stage,
            success=True,
            metadata=metadata
        )
    
    def record_pipeline_stage(
        self,
        stage: str,
        success: bool,
        duration_ms: float,
        properties_processed: int = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Record pipeline stage completion
        
        Args:
            stage: Stage name (e.g., "discovery", "lien_priority")
            success: Whether stage completed successfully
            duration_ms: Stage duration in milliseconds
            properties_processed: Number of properties processed
            metadata: Additional stage data
        """
        stage_metadata = metadata or {}
        if properties_processed is not None:
            stage_metadata["properties_processed"] = properties_processed
        
        self._publish(
            metric_name="pipeline_stage",
            value=duration_ms,
            unit="Milliseconds",
            operation=f"stage_{stage}",
            stage=stage,
            success=success,
            metadata=stage_metadata
        )
    
    def record_token_usage(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float = None,
        operation: str = None
    ):
        """
        Record LLM token usage
        
        Args:
            model: Model name (e.g., "claude-sonnet-4.5", "gemini-2.5-flash")
            input_tokens: Input token count
            output_tokens: Output token count
            cost_usd: Cost in USD (if applicable)
            operation: Operation that used tokens
        """
        self._publish(
            metric_name="token_usage",
            value=input_tokens + output_tokens,
            unit="Tokens",
            operation=operation,
            metadata={
                "model": model,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost_usd
            }
        )
    
    def record_scraper_result(
        self,
        scraper: str,
        success: bool,
        properties_found: int = None,
        duration_ms: float = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Record scraper execution result
        
        Args:
            scraper: Scraper name (e.g., "beca", "bcpao", "acclaimweb")
            success: Whether scraping succeeded
            properties_found: Number of properties/records found
            duration_ms: Scraping duration
            metadata: Additional scraper data
        """
        scraper_metadata = metadata or {}
        if properties_found is not None:
            scraper_metadata["properties_found"] = properties_found
        if duration_ms is not None:
            scraper_metadata["duration_ms"] = duration_ms
        
        self._publish(
            metric_name="scraper_execution",
            value=1,
            unit="Count",
            operation=f"scraper_{scraper}",
            success=success,
            metadata=scraper_metadata
        )


# Global metrics instance
_metrics: Optional[MetricsPublisher] = None

def get_metrics() -> MetricsPublisher:
    """Get or create global metrics publisher"""
    global _metrics
    if _metrics is None:
        _metrics = MetricsPublisher()
    return _metrics
