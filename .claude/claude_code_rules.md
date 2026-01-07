# Claude Code - BidDeed.AI Safety Rules

## 🎯 Core Principle
**"Execute Fast, Rollback Faster"** - Autonomous execution with instant rollback capability.

**BidDeed.AI Philosophy**: 100% autonomous deployment. NEVER ask permission except for the 5 STOP conditions below.

---

## 🚨 THE 5 STOP CONDITIONS (Ask Before Executing)

ONLY these 5 scenarios require user confirmation:

### 1. 💰 SPEND >$10
- New API subscriptions
- Paid service integrations
- Cloud resource scaling that costs money

### 2. 🗄️ PRODUCTION DATA DELETION
- `DELETE FROM` on tables: `properties`, `auctions`, `foreclosure_data`, `ml_predictions`
- `TRUNCATE` on any production table
- `DROP TABLE` or `DROP DATABASE`

### 3. 🔐 SECURITY CHANGES
- API key rotation
- Authentication logic modification
- Authorization rule changes
- Supabase RLS policy changes

### 4. 🏗️ BREAKING SCHEMA CHANGES
- Removing columns with existing data
- Changing column types that require data migration
- Dropping tables with >100 rows

### 5. 🚀 BILLING/PAYMENT SYSTEMS
- Stripe integration changes
- Payment processing logic
- Subscription management changes

**Everything else? Execute autonomously. Commit. Deploy. Report results.**

---

## ✅ ALWAYS EXECUTE AUTONOMOUSLY (No Permission Needed)

### Code Operations:
- Bug fixes and error resolution
- Code refactoring and optimization
- Adding new features (non-breaking)
- Dependency updates (minor/patch versions)
- Documentation updates
- Test creation and execution
- Performance improvements

### Git Operations:
- Creating backup commits
- Feature branches
- Commits with detailed messages
- Pushing to GitHub
- Creating tags for rollback

### Deployment Operations:
- GitHub Actions workflow updates
- Cloudflare Pages deployments
- Supabase function deployments
- Environment variable updates (non-secret)

### Database Operations (Safe):
- `INSERT` into any table
- `UPDATE` with WHERE clause (affecting <100 rows at once)
- `SELECT` queries (read-only)
- Creating new tables
- Adding new columns (non-breaking)
- Creating indexes

### BidDeed.AI Specific:
- Scraper updates (RealForeclose, BCPAO, AcclaimWeb, RealTDM)
- Smart Router configuration changes
- LangGraph workflow modifications
- ForecastEngine™ updates
- Report generation changes
- ML model retraining (non-production)

---

## 🔄 AUTO-BACKUP PROTOCOL

### Before ANY Destructive Operation:

```bash
# Step 1: Auto-backup (no questions asked)
git add .
git commit -m "[AUTO-BACKUP] Pre-change snapshot: $(date +%Y%m%d-%H%M%S)

About to: [OPERATION_DESCRIPTION]
Project: BidDeed.AI
Branch: $(git branch --show-current)
"

# Step 2: Create rollback tag
git tag "rollback-$(date +%Y%m%d-%H%M%S)"

# Step 3: Verify backup exists
git log -1 --oneline

# NOW execute the change
```

**Execution Time**: <5 seconds. No user interaction needed.

---

## 🗄️ SUPABASE SAFETY RULES

### Tables That Require Extra Caution:

#### PRODUCTION DATA (Backup before DELETE/TRUNCATE):
- `properties` - Foreclosure property data
- `foreclosure_auctions` - Auction records
- `ml_predictions` - XGBoost model outputs
- `lien_discoveries` - Lien priority analysis
- `max_bid_calculations` - Bidding decisions

#### OPERATIONAL DATA (Safe to modify):
- `activities` - Activity logs
- `daily_metrics` - Metrics tracking
- `insights` - AI insights
- `workflow_logs` - LangGraph execution logs
- `smart_router_stats` - Router performance data

### Safe Database Patterns:

```sql
-- ✅ SAFE: Read operations (always allowed)
SELECT * FROM properties WHERE county = 'Brevard';

-- ✅ SAFE: Targeted updates with WHERE clause
UPDATE properties 
SET status = 'ANALYZED' 
WHERE property_id = '123' AND status = 'PENDING';

-- ✅ SAFE: Inserts (additive)
INSERT INTO foreclosure_auctions (property_id, auction_date, max_bid)
VALUES ('456', '2026-02-04', 150000);

-- ⚠️ CAUTION: Update without WHERE (ask if >100 rows affected)
UPDATE properties SET status = 'ARCHIVED';  -- Ask first!

-- 🛑 FORBIDDEN: Delete without WHERE
DELETE FROM properties;  -- STOP! Requires confirmation

-- ✅ SAFE: Delete with specific WHERE
DELETE FROM properties 
WHERE property_id = '789' AND status = 'DUPLICATE';
```

### Supabase RLS (Row Level Security):

```sql
-- ⚠️ CAUTION: RLS policy changes require confirmation
-- These affect data access security

-- Always test RLS changes in staging first:
-- 1. Apply to staging
-- 2. Run test queries
-- 3. Verify expected behavior
-- 4. Then apply to production
```

---

## 🚀 GITHUB ACTIONS DEPLOYMENT

### Auto-Deploy Workflow:

```yaml
# .github/workflows/auto-deploy.yml
# This workflow runs on every push to main

name: Auto-Deploy BidDeed.AI
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Tests
        run: npm test
      
      - name: Deploy to Cloudflare Pages
        run: |
          npx wrangler pages deploy dist \
            --project-name=brevard-bidder-landing \
            --commit-message="${GITHUB_SHA}"
      
      - name: Update Supabase Functions
        run: npx supabase functions deploy
```

**Autonomous Execution**: Commits to `main` auto-deploy. No human approval needed.

### Workflow Failures:

If GitHub Actions workflow fails:

```bash
# 1. Diagnose (check logs)
gh run view [run-id] --log-failed

# 2. Fix the issue
[make code changes]

# 3. Auto-commit and redeploy
git add .
git commit -m "[FIX] Resolved deployment failure: [description]"
git push origin main

# GitHub Actions will auto-retry deployment
```

**No human intervention required unless 3 consecutive failures.**

---

## 🧠 LANGRAPH ORCHESTRATION SAFETY

### Workflow State Management:

```python
# ✅ SAFE: State updates via LangGraph
from langgraph.graph import StateGraph

# Checkpointing is automatic in BidDeed.AI
# State persists to Supabase after each node
# No manual intervention needed

async def analyze_property(state: PropertyState):
    """Example: Autonomous property analysis"""
    
    # 1. Scrape data (autonomous)
    property_data = await scrape_bcpao(state.property_id)
    
    # 2. Analyze liens (autonomous)
    lien_analysis = await discover_liens(property_data)
    
    # 3. Calculate max bid (autonomous)
    max_bid = calculate_max_bid(property_data, lien_analysis)
    
    # 4. Update state (autonomous)
    return {
        **state,
        "analyzed": True,
        "max_bid": max_bid,
        "recommendation": "BID" if max_bid > 0 else "SKIP"
    }
```

### Circuit Breakers:

```python
# Auto-implemented in BidDeed.AI
MAX_RETRIES = 3
BACKOFF_SECONDS = [1, 5, 15]

# If external API fails 3 times:
# 1. Log failure to Supabase insights
# 2. Mark property as "BLOCKED"
# 3. Continue to next property
# 4. Human reviews "BLOCKED" items later
```

---

## 🎯 SMART ROUTER V7.4 SAFETY

### Tier Routing Rules:

```python
# ✅ SAFE: Auto-routing based on complexity
# No human approval needed for tier selection

ROUTING_RULES = {
    "FREE": {  # 90% of operations
        "models": ["gemini-2.5-flash", "gemini-2.5-pro"],
        "max_tokens": 8000,
        "use_for": ["simple analysis", "data extraction", "classification"]
    },
    "ULTRA_CHEAP": {  # 5% of operations
        "models": ["deepseek-v3.2"],
        "cost": "$0.28/1M tokens",
        "use_for": ["lien reasoning", "complex analysis"]
    },
    "PREMIUM": {  # 5% of operations
        "models": ["claude-sonnet-4.5", "claude-opus-4.5"],
        "use_for": ["legal interpretation", "complex decisions"]
    }
}

# Router automatically selects optimal tier
# Tracks costs in Supabase daily_metrics
# No intervention needed unless monthly spend >$100
```

### Cost Monitoring:

```python
# Auto-tracked in Supabase
# Alert triggers:
# - Daily spend >$10 → Log warning
# - Weekly spend >$50 → Email Ariel
# - Monthly spend >$100 → Pause PREMIUM tier (use ULTRA_CHEAP)

# Check current spend:
SELECT 
    DATE(created_at) as date,
    SUM(cost_usd) as daily_cost
FROM smart_router_stats
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at);
```

---

## 🏗️ FORECLOSURE DATA INTEGRITY

### Critical Data Validations:

```python
# ✅ ALWAYS validate before INSERT/UPDATE
def validate_foreclosure_data(data: dict) -> bool:
    """Autonomous validation - no human needed"""
    
    required_fields = [
        "property_id",      # Must exist
        "plaintiff",        # Must be non-empty
        "judgment_amount",  # Must be >0
        "auction_date",     # Must be future date
    ]
    
    for field in required_fields:
        if field not in data or not data[field]:
            log_error(f"Missing required field: {field}")
            return False
    
    # Validate judgment amount
    if data["judgment_amount"] <= 0:
        log_error("Invalid judgment amount")
        return False
    
    # Validate auction date
    if data["auction_date"] < datetime.now():
        log_warning("Auction date in past - might be historical data")
    
    return True

# Auto-reject invalid data without asking
# Log rejections to Supabase insights table
```

### Duplicate Detection:

```python
# ✅ ALWAYS check for duplicates before INSERT
async def insert_property(data: dict):
    """Autonomous duplicate handling"""
    
    # Check for existing property
    existing = await supabase.table("properties").select("*").eq(
        "property_id", data["property_id"]
    ).execute()
    
    if existing.data:
        # Update existing instead of insert
        await supabase.table("properties").update(data).eq(
            "property_id", data["property_id"]
        ).execute()
        log_info(f"Updated existing property: {data['property_id']}")
    else:
        # Insert new property
        await supabase.table("properties").insert(data).execute()
        log_info(f"Inserted new property: {data['property_id']}")
```

---

## 📝 AUTO-COMMIT MESSAGE FORMAT

### Standard Format (Auto-Generated):

```bash
[TYPE] Brief summary (50 chars max)

## Changes
- File1.py: Added function X for lien discovery
- File2.py: Updated Smart Router tier selection
- schema.sql: Added column for ML confidence score

## Why
[Auto-detected reason: bug fix, feature, refactor]

## Impact
- User-facing: [None/Visible changes]
- Developer-facing: [What devs need to know]
- Performance: [Improvement/Neutral/Degradation]

## Testing
- [x] Unit tests passed (automated)
- [x] Integration tests passed (automated)
- [x] Deployed to staging (automated)
- [ ] Manual QA required (rare)

## Rollback
git reset --hard rollback-[TIMESTAMP]

## Metrics
- Files changed: 3
- Lines added: 127
- Lines removed: 45
- Complexity: Medium
- Risk: Low

Deployed: [TIMESTAMP]
SHA: [COMMIT_SHA]
```

### Commit Types:

- `[AUTO-BACKUP]` - Pre-change safety snapshot
- `[FIX]` - Bug fix (auto-deployed)
- `[FEAT]` - New feature (auto-deployed)
- `[REFACTOR]` - Code cleanup (auto-deployed)
- `[DB]` - Database changes (review deploy logs)
- `[DEPLOY]` - Deployment configuration
- `[ROUTER]` - Smart Router updates
- `[SCRAPER]` - Scraper modifications
- `[WORKFLOW]` - LangGraph workflow changes
- `[SECURITY]` - Security-related (requires review)

---

## 🔄 ROLLBACK PROCEDURES

### Instant Rollback (1-Click):

```bash
# Find recent rollback points
git tag -l "rollback-*" | tail -5

# Rollback to specific point
git reset --hard rollback-20260107-143000

# Verify rollback
git log -1 --oneline

# Force push to trigger redeployment
git push origin main --force

# GitHub Actions will auto-redeploy previous version
```

**Execution Time**: <30 seconds total (including redeployment)

### Database Rollback:

```bash
# Supabase schema rollback
cp prisma/schema.backup.prisma prisma/schema.prisma
npx prisma db push

# Data rollback (from nightly backup)
# Automated: BidDeed.AI backs up to Supabase Storage nightly
# Restore: Download backup and run SQL import
```

### Scraper Rollback:

```bash
# If scraper breaks foreclosure data collection:
# 1. Rollback code (instant)
git reset --hard rollback-[TIMESTAMP]

# 2. Re-run last successful scraper version
python src/scrapers/realforeclose_scraper.py --date=2026-01-06

# 3. Verify data integrity
python src/validators/foreclosure_data_validator.py
```

---

## 🛡️ FAIL-SAFE DEFAULTS

### API Integrations:

```python
# ✅ ALWAYS use circuit breakers
from circuitbreaker import circuit

@circuit(failure_threshold=3, recovery_timeout=60)
async def fetch_bcpao_data(property_id: str):
    """Auto-retry with backoff, auto-fail after 3 attempts"""
    try:
        response = await httpx.get(f"{BCPAO_API}/{property_id}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        log_error(f"BCPAO fetch failed: {e}")
        raise  # Circuit breaker handles retry logic
```

### Smart Router Fallbacks:

```python
# ✅ ALWAYS have fallback model
async def route_to_llm(task: str, complexity: str):
    """Autonomous tier selection with fallback"""
    
    try:
        # Try FREE tier first (90% success rate)
        if complexity == "simple":
            return await call_gemini(task)
    except Exception:
        # Fallback to ULTRA_CHEAP
        try:
            return await call_deepseek(task)
        except Exception:
            # Final fallback to PREMIUM (guaranteed)
            return await call_claude(task)
```

### Data Validation:

```python
# ✅ ALWAYS validate before save
def save_property(data: dict):
    """Autonomous save with validation"""
    
    # Validation failures auto-reject without asking
    if not validate_foreclosure_data(data):
        log_error(f"Validation failed: {data['property_id']}")
        return False  # Don't save invalid data
    
    # Duplicate check auto-resolves
    existing = check_duplicate(data["property_id"])
    if existing:
        update_property(data)  # Update instead of insert
    else:
        insert_property(data)  # Insert new
    
    return True
```

---

## 🚨 ERROR HANDLING PROTOCOL

### Auto-Recovery Sequence:

```
Error Detected
    ↓
1. Log to Supabase insights table
    ↓
2. Retry with exponential backoff (3 attempts)
    ↓
3. If still failing:
   a. Mark item as "BLOCKED"
   b. Continue processing other items
   c. Log summary to daily_metrics
    ↓
4. If 3+ items blocked in same category:
   → Surface to Ariel with diagnosis
```

### Example Auto-Recovery:

```python
async def process_foreclosure_batch(properties: list):
    """Autonomous batch processing with error handling"""
    
    results = {
        "processed": 0,
        "blocked": 0,
        "errors": []
    }
    
    for prop in properties:
        try:
            # Attempt processing (3 retries built-in)
            await analyze_property(prop)
            results["processed"] += 1
            
        except Exception as e:
            # Log and continue (don't stop entire batch)
            results["blocked"] += 1
            results["errors"].append({
                "property_id": prop["property_id"],
                "error": str(e),
                "timestamp": datetime.now()
            })
            
            # Log to Supabase
            await supabase.table("insights").insert({
                "type": "PROCESSING_ERROR",
                "property_id": prop["property_id"],
                "error_message": str(e)
            }).execute()
    
    # Only escalate if >20% failure rate
    if results["blocked"] / len(properties) > 0.2:
        send_alert_to_ariel(results)
    
    return results
```

---

## 📊 MONITORING & ALERTS

### Auto-Monitored Metrics:

```python
# Tracked in Supabase daily_metrics table
# No human intervention needed unless thresholds exceeded

MONITORING_THRESHOLDS = {
    "api_cost_daily": 10.00,        # Alert if >$10/day
    "scraper_failure_rate": 0.10,   # Alert if >10% failures
    "processing_time_avg": 300,     # Alert if >5min avg
    "blocked_properties": 5,         # Alert if >5 blocked in one run
    "database_size_gb": 10,          # Alert if >10GB
}

# Auto-alerts trigger email to Ariel
# Includes: diagnosis, impact, recommended action
```

### Dashboard (Auto-Updated):

```
BidDeed.AI Health Dashboard (Cloudflare Pages)
- Last scraper run: 2026-01-07 06:00 EST ✅
- Properties processed: 23/25 (2 blocked) ⚠️
- Smart Router: 88% FREE tier 🎯
- API costs today: $3.47 ✅
- Database size: 4.2GB ✅
- LangGraph workflows: 18 completed ✅

View details: https://brevard-bidder-landing.pages.dev/dashboard
```

---

## 🎯 EXECUTION PHILOSOPHY

### Zero-Human-Loop Principles:

1. **Default to Action**: Execute first, ask later (only for 5 STOP conditions)
2. **Auto-Backup Always**: Every destructive operation gets auto-backup (5 seconds)
3. **Fail Forward**: Errors don't stop execution, they log and continue
4. **Rollback is Easy**: 1-click rollback to any point in last 30 days
5. **Monitor Everything**: Auto-track all metrics, alert only on anomalies

### Human Intervention Triggers:

```python
# ONLY escalate to Ariel if:
def should_escalate(event: dict) -> bool:
    """Determines if human intervention needed"""
    
    # Spending threshold
    if event["type"] == "COST" and event["amount"] > 10:
        return True
    
    # Production data deletion
    if event["type"] == "DB_DELETE" and event["table"] in PRODUCTION_TABLES:
        return True
    
    # Security changes
    if event["type"] == "SECURITY":
        return True
    
    # Repeated failures (3+ in same category)
    if event["type"] == "ERROR" and event["consecutive_failures"] >= 3:
        return True
    
    # Everything else? Handle autonomously
    return False
```

---

## 🔐 SECURITY BEST PRACTICES

### Environment Variables:

```bash
# ✅ SAFE: Non-sensitive config
SUPABASE_URL=https://mocerqjnksmhcjzxrewo.supabase.co
ENVIRONMENT=production
SMART_ROUTER_DEFAULT_TIER=FREE

# 🔐 SENSITIVE: Never commit these
SUPABASE_ANON_KEY=[SECRET]
ANTHROPIC_API_KEY=[SECRET]
GITHUB_TOKEN=[SECRET]

# Stored in: GitHub Secrets, Cloudflare Pages env vars
# Never in code, never in git
```

### API Key Rotation:

```bash
# ⚠️ Requires confirmation (STOP condition #3)
# Process:
# 1. Generate new key in service dashboard
# 2. Update GitHub Secrets
# 3. Update Cloudflare Pages env vars
# 4. Test in staging
# 5. Deploy to production
# 6. Revoke old key after 24 hours
```

---

## 📚 QUICK REFERENCE

### Daily Workflow:

```bash
# Morning: Check system health (automated)
curl https://brevard-bidder-landing.pages.dev/api/health

# Development: Make changes, auto-deploy
git add .
git commit -m "[FEAT] Description"
git push origin main  # Auto-deploys

# Afternoon: Check metrics (automated)
# Dashboard updates every 30 minutes

# Evening: Review blocked items (if any)
# Only if >5 properties blocked
```

### Emergency Commands:

```bash
# Stop all automated workflows
gh workflow disable auto-deploy.yml

# Rollback to last known good state
git reset --hard rollback-[TIMESTAMP]
git push origin main --force

# Check recent errors
psql $DATABASE_URL -c "
  SELECT * FROM insights 
  WHERE type = 'ERROR' 
  ORDER BY created_at DESC 
  LIMIT 10;
"

# Re-enable workflows
gh workflow enable auto-deploy.yml
```

---

## ✅ FINAL CHECKLIST

Before deploying this document:

- [x] BidDeed.AI-specific rules added
- [x] Supabase safety protocols defined
- [x] GitHub Actions auto-deploy configured
- [x] Smart Router safety rules included
- [x] LangGraph orchestration safety covered
- [x] Foreclosure data integrity rules set
- [x] Zero-human-loop philosophy implemented
- [x] 5 STOP conditions clearly defined
- [x] Auto-backup protocol standardized
- [x] Rollback procedures simplified
- [x] Monitoring and alerts configured
- [x] Security best practices documented

---

**Version**: 3.0 - BidDeed.AI Edition
**Last Updated**: 2026-01-07
**Next Review**: 2026-02-07 (30 days)

**Deployment**: Copy to `.claude/claude_code_rules.md` in all BidDeed.AI repositories.

**Questions?** See PROJECT_STATE.json or CLAUDE.md in repo root.
