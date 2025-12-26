# Agent Patterns Integration - Deployment Guide

**Deployed:** 2024-12-26  
**Correlation ID:** `deploy-agent-patterns-20241226-1247`  
**Version:** BrevardBidderAI V16.5.1 / Life OS V2.1

---

## 🎯 What Was Deployed

Extracted best practices from AWS Bedrock Agent architecture and adapted for BidDeed.AI stack:

### New Utilities (Both Repos)
1. **`src/utils/structured_logger.py`** - Correlation ID tracking, structured JSON logging
2. **`src/utils/metrics_publisher.py`** - Supabase metrics tracking
3. **`src/utils/error_tracker.py`** - Centralized error logging with stack traces
4. **`src/utils/retry_utils.py`** - Enhanced retry decorators with metrics

### Database Changes
- **Supabase Migration:** `metrics` and `errors` tables with optimized indexes
- **Analysis Views:** `v_metrics_by_operation`, `v_errors_by_type`, `v_pipeline_performance`

---

## 📊 Database Schema

### Metrics Table
```sql
CREATE TABLE metrics (
    id UUID PRIMARY KEY,
    created_at TIMESTAMPTZ,
    metric_name TEXT,           -- operation_latency, error, success, etc.
    value FLOAT,                -- latency in ms, count, tokens
    unit TEXT,                  -- Milliseconds, Count, Tokens
    operation TEXT,             -- lien_discovery, bcpao_api_call, etc.
    stage TEXT,                 -- stage_1, stage_2, etc.
    success BOOLEAN,
    correlation_id TEXT,
    metadata JSONB
);
```

### Errors Table
```sql
CREATE TABLE errors (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMPTZ,
    error_type TEXT,            -- api_timeout, validation_failed, etc.
    error_message TEXT,
    stage TEXT,
    operation TEXT,
    severity TEXT,              -- debug, info, warning, error, critical
    correlation_id TEXT,
    metadata JSONB,
    stack_trace TEXT
);
```

---

## 🚀 Usage Examples

### 1. Structured Logging
```python
from src.utils.structured_logger import get_logger, set_correlation_id

logger = get_logger(__name__)

# Start of workflow - set correlation ID
correlation_id = set_correlation_id("auction-2025-01-03-001")

logger.info(
    "Starting lien discovery",
    stage="lien_priority",
    property_id="2835546",
    parcel_id="29-36-25-00-00001.0"
)
```

### 2. Metrics Tracking
```python
from src.utils.metrics_publisher import get_metrics
import time

metrics = get_metrics()

start = time.time()
# ... perform operation ...
duration_ms = (time.time() - start) * 1000

metrics.record_latency(
    operation="bcpao_api_call",
    latency_ms=duration_ms,
    stage="discovery"
)

metrics.record_pipeline_stage(
    stage="lien_discovery",
    success=True,
    duration_ms=5432.1,
    properties_processed=19
)
```

### 3. Error Tracking
```python
from src.utils.error_tracker import track_error

try:
    result = scrape_acclaimweb(url)
except requests.Timeout as e:
    track_error(
        error_type="api_timeout",
        error_message=str(e),
        stage="lien_discovery",
        operation="acclaimweb_scrape",
        metadata={"url": url, "timeout_seconds": 30},
        exception=e
    )
    raise
```

### 4. Retry with Metrics
```python
from src.utils.retry_utils import retry_with_backoff
import requests

@retry_with_backoff(
    max_attempts=5,
    min_wait=4,
    max_wait=30,
    operation_name="bcpao_api_fetch",
    stage="discovery"
)
def fetch_property_data(parcel_id: str):
    url = f"https://gis.brevardfl.gov/gissrv/rest/services/Base_Map/Parcel_New_WKID2881/MapServer/5/query"
    params = {"where": f"STRAP = '{parcel_id}'", "f": "json"}
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

# Automatically logs attempts, records latency on success, tracks errors on failure
data = fetch_property_data("29-36-25-00-00001.0")
```

---

## 🔧 Integration with LangGraph

### Before (Old Pattern)
```python
def lien_discovery_node(state: Dict) -> Dict:
    logger.info("Starting lien discovery")
    
    try:
        results = search_acclaimweb(state["parcel_id"])
        return {"liens": results}
    except Exception as e:
        logger.error(f"Lien discovery failed: {e}")
        raise
```

### After (New Pattern)
```python
from src.utils.structured_logger import get_logger, set_correlation_id
from src.utils.metrics_publisher import get_metrics
from src.utils.error_tracker import track_error
from src.utils.retry_utils import retry_with_backoff
import time

logger = get_logger(__name__)
metrics = get_metrics()

@retry_with_backoff(
    max_attempts=3,
    operation_name="lien_discovery",
    stage="lien_priority"
)
def lien_discovery_node(state: Dict) -> Dict:
    # Set correlation ID at start
    correlation_id = set_correlation_id(state.get("correlation_id"))
    
    logger.info(
        "Starting lien discovery",
        parcel_id=state["parcel_id"],
        property_address=state.get("address")
    )
    
    start_time = time.time()
    
    try:
        # Perform operation
        results = search_acclaimweb(state["parcel_id"])
        
        # Record success metrics
        duration_ms = (time.time() - start_time) * 1000
        metrics.record_pipeline_stage(
            stage="lien_discovery",
            success=True,
            duration_ms=duration_ms,
            metadata={
                "liens_found": len(results),
                "parcel_id": state["parcel_id"]
            }
        )
        
        logger.info(
            "Lien discovery completed",
            liens_found=len(results),
            duration_ms=round(duration_ms, 2)
        )
        
        return {"liens": results, "correlation_id": correlation_id}
        
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        
        # Track error (retry decorator also tracks)
        track_error(
            error_type=type(e).__name__,
            error_message=str(e),
            stage="lien_discovery",
            operation="acclaimweb_search",
            metadata={"parcel_id": state["parcel_id"]},
            exception=e
        )
        
        logger.error(
            "Lien discovery failed",
            error=str(e),
            duration_ms=round(duration_ms, 2)
        )
        
        raise
```

---

## 📈 Monitoring & Analysis

### Query Metrics in Supabase

#### Pipeline Stage Performance (Last 7 Days)
```sql
SELECT * FROM v_pipeline_performance
WHERE stage IN ('discovery', 'lien_priority', 'max_bid')
ORDER BY day DESC, stage;
```

#### Error Frequency (Last 24 Hours)
```sql
SELECT 
    error_type,
    stage,
    COUNT(*) as error_count,
    MAX(timestamp) as last_occurrence
FROM errors
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY error_type, stage
ORDER BY error_count DESC;
```

#### Latency Analysis
```sql
SELECT 
    operation,
    COUNT(*) as calls,
    ROUND(AVG(value)::numeric, 2) as avg_ms,
    ROUND(PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY value)::numeric, 2) as p95_ms,
    ROUND(MAX(value)::numeric, 2) as max_ms
FROM metrics
WHERE metric_name = 'operation_latency'
  AND created_at > NOW() - INTERVAL '24 hours'
GROUP BY operation
ORDER BY avg_ms DESC;
```

#### Trace Request by Correlation ID
```sql
SELECT 
    m.created_at,
    m.operation,
    m.metric_name,
    m.value,
    m.success,
    m.metadata
FROM metrics m
WHERE m.correlation_id = 'corr-abc123def456'
ORDER BY m.created_at;
```

---

## 🎯 Migration Strategy

### Phase 1: Core Scrapers (Week 1)
- [x] BECA scraper
- [ ] BCPAO API calls
- [ ] AcclaimWeb scraper
- [ ] RealTDM scraper

### Phase 2: LangGraph Nodes (Week 2)
- [ ] Discovery node
- [ ] Lien Priority node
- [ ] Max Bid calculation node
- [ ] Report generation node

### Phase 3: Analysis & Optimization (Week 3)
- [ ] Identify slow operations (>1s p95 latency)
- [ ] Track error patterns
- [ ] Optimize retry strategies
- [ ] Create alerting rules

---

## 🔍 Key Metrics to Track

### Performance Metrics
- `operation_latency` - All API calls, scrapes, calculations
- `pipeline_stage` - End-to-end stage duration
- `token_usage` - LLM token consumption by model

### Quality Metrics
- `scraper_execution` - Success rate by scraper
- `error` - Error frequency by type/stage
- `success` - Success rate by operation

### Business Metrics
- Properties processed per auction
- BID/REVIEW/SKIP decision distribution
- Average processing time per property
- Cost per property analysis

---

## 🚨 Alerting Rules (Future)

### High-Priority Alerts
- Error rate >10% in any stage (15min window)
- p95 latency >5s for any operation
- Pipeline failure rate >20%

### Medium-Priority Alerts
- Error rate >5% in any stage (1hr window)
- p95 latency >3s for scrapers
- Token usage >$50/day

### Low-Priority Alerts
- New error types detected
- Latency degradation >50% vs baseline

---

## 📦 Files Deployed

### BrevardBidderAI (brevard-bidder-scraper)
```
src/utils/
├── structured_logger.py        (NEW)
├── metrics_publisher.py        (NEW)
├── error_tracker.py            (NEW)
└── retry_utils.py              (NEW)

docs/
└── agent_patterns_integration.md  (NEW)

supabase/migrations/
└── 20241226_add_metrics_errors.sql  (NEW)
```

### Life OS (life-os)
```
src/utils/
├── structured_logger.py        (NEW)
├── metrics_publisher.py        (NEW)
├── error_tracker.py            (NEW)
└── retry_utils.py              (NEW)

docs/
└── agent_patterns_integration.md  (NEW)
```

---

## ✅ Verification Steps

1. **Test Correlation ID Tracking**
```python
from src.utils.structured_logger import set_correlation_id, get_logger

logger = get_logger("test")
cid = set_correlation_id("test-001")
logger.info("Test message", test_key="test_value")
# Should log: {"message": "Test message", "correlation_id": "test-001", ...}
```

2. **Test Metrics Publishing**
```python
from src.utils.metrics_publisher import get_metrics

metrics = get_metrics()
metrics.record_latency("test_operation", 123.45)
# Check Supabase metrics table for new row
```

3. **Test Error Tracking**
```python
from src.utils.error_tracker import track_error

try:
    raise ValueError("Test error")
except ValueError as e:
    track_error("test_error", str(e), exception=e)
# Check Supabase errors table for new row with stack trace
```

4. **Test Retry Decorator**
```python
from src.utils.retry_utils import retry_with_backoff

@retry_with_backoff(max_attempts=3, operation_name="test_retry")
def flaky_function():
    import random
    if random.random() < 0.7:
        raise Exception("Random failure")
    return "success"

result = flaky_function()
# Should retry on failure, log all attempts, record final metrics
```

---

## 🎓 Key Improvements

### vs. Original AWS Bedrock Pattern
- ✅ Kept: Structured logging, correlation IDs, retry logic, metrics
- ❌ Removed: AWS-specific services (Lambda, CloudWatch, X-Ray, Secrets Manager)
- ✅ Adapted: Supabase instead of DynamoDB, GitHub Actions instead of Lambda

### Cost Comparison
- **Bedrock Pattern:** $120/mo (Lambda $15 + CloudWatch $10 + X-Ray $5 + DynamoDB $5 + Bedrock $90)
- **BidDeed.AI Pattern:** $0 for infrastructure (GitHub Actions + Supabase free tier)
- **Savings:** $120/mo or $1,440/yr

### Performance Comparison
- **Latency Tracking:** Same (both track operation latency)
- **Error Tracking:** Better (we have stack traces + metadata)
- **Correlation:** Same (correlation IDs for request tracing)
- **Analysis:** Better (SQL views vs CloudWatch Insights queries)

---

## 🔗 Related Documentation

- [Smart Router V5 Documentation](../smart_router/README.md)
- [Supabase Schema Documentation](../supabase/schema.md)
- [LangGraph Orchestration Guide](../langgraph/orchestration.md)
- [GitHub Actions Workflows](../../.github/workflows/README.md)

---

**Next Steps:**
1. Run Supabase migration to create tables
2. Update existing scrapers to use retry decorators
3. Integrate correlation IDs in orchestrator.yml workflow
4. Create monitoring dashboard in Life OS
5. Set up alerting rules based on metrics

**Questions?** Check correlation ID `deploy-agent-patterns-20241226-1247` in deployment logs.
