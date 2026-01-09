# Capacity Enforcement System

Automated enforcement of Claude Sonnet 4.5's capacity commitment: **Never claim token/space limitations until 800K+ tokens used (80% of 1M capacity)**.

## The 80% Rule

**Context Window**: 1,000,000 tokens (1M)  
**Threshold**: 800,000 tokens (80%)  
**Violation**: Claiming "space constraints", "limited capacity", or "running out of tokens" when usage <80%

## System Components

### 1. `capacity_enforcement.py`
Python script that:
- Checks if Claude violated the 80% rule
- Calculates violation severity (SEVERE/HIGH/MEDIUM/LOW)
- Logs compliance data to Supabase
- Queries violation history

### 2. `supabase_schema.sql`
Database schema:
- `capacity_compliance` table: Stores all compliance checks
- `capacity_violations_summary` view: Aggregated violation statistics
- Indexes for fast queries on violations

### 3. `.github/workflows/capacity_enforcement.yml`
GitHub Actions workflow:
- Scheduled checks every 6 hours
- Manual trigger with token usage input
- Fails workflow if violation detected
- Logs all checks to Supabase

## Usage

### Manual Trigger (GitHub Actions)
```bash
# Navigate to Actions → Capacity Enforcement → Run workflow
# Input:
#   - tokens_used: 125000
#   - claimed_limitation: true
# 
# Result: Workflow fails if violation detected
```

### Python Script
```python
from capacity_enforcement import CapacityEnforcement

enforcer = CapacityEnforcement()

# Check compliance
result = enforcer.check_compliance(
    tokens_used=125_000,
    claimed_limitation=True  # Did Claude claim limitations?
)

print(result)
# {
#   "tokens_used": 125000,
#   "usage_percent": 12.5,
#   "is_violation": true,
#   "violation_severity": "SEVERE"
# }

# Log to Supabase
enforcer.log_to_supabase(result)

# Get violation summary
summary = enforcer.get_violation_summary()
print(f"Total violations: {summary['total_violations']}")
```

## Violation Severity Levels

| Severity | Usage Range | Example |
|----------|-------------|---------|
| SEVERE | <20% | Used 125K (12.5%) but claimed limitations |
| HIGH | 20-40% | Used 300K (30%) but claimed limitations |
| MEDIUM | 40-60% | Used 500K (50%) but claimed limitations |
| LOW | 60-80% | Used 700K (70%) but claimed limitations |

## Supabase Setup

Run the schema:
```sql
-- In Supabase SQL Editor
-- Run supabase_schema.sql
```

Set the secret in GitHub:
```bash
# GitHub repo → Settings → Secrets → Actions
# Name: SUPABASE_KEY
# Value: [Your Supabase service role key]
```

## Commitment

**Date Committed**: January 9, 2026  
**Violation Count**: 0 (reset)  
**Base64 Reference**: `/tmp/capacity_commitment.b64`

Claude will **NEVER** claim token/space limitations until 800K+ tokens used (80% of 1M capacity).

## Files

- `capacity_enforcement.py` - Main enforcement script
- `supabase_schema.sql` - Database schema
- `.github/workflows/capacity_enforcement.yml` - GitHub Actions workflow
- `capacity_commitment.b64` - Base64 encoded commitment
- `README_CAPACITY.md` - This file
