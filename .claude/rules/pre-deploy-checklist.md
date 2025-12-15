# Claude Code Pre-Deploy Checklist

> **Purpose**: Human oversight layer between AI output and deployment  
> **Based on**: Kitze Vibe Engineering Framework + BidDeed.AI Failure Patterns  
> **Rule**: NO deployment without passing ALL critical checks

---

## 🔴 CRITICAL CHECKS (Blocking)

### 1. File Modification Safety
- [ ] **READ BEFORE WRITE**: Viewed existing file content before modifying
- [ ] **NO FILE REPLACEMENT**: Added to existing code, not replaced entire file
- [ ] **BACKUP EXISTS**: Original file content preserved if making breaking changes

### 2. Data Integrity
- [ ] **NO ESTIMATED DATA**: All KPIs use verified BECA V22 data only
- [ ] **NO GUESSED JUDGMENTS**: Final Judgment/Opening Bid from courthouse records
- [ ] **SOURCE VERIFIED**: Data source documented (BCPAO, AcclaimWeb, RealTDM, Census)

### 3. Autonomous Execution
- [ ] **NO PERMISSION REQUESTS**: Executed without asking Ariel "should I do X?"
- [ ] **SELF-DEBUGGED**: Fixed errors autonomously before reporting
- [ ] **COMPLETE WORKFLOW**: Ran full workflow, not stopped mid-process

### 4. State Management
- [ ] **PROJECT_STATE.json UPDATED**: Recent decisions array updated
- [ ] **SUPABASE LOGGED**: Insights table entry created via insert_insight.yml
- [ ] **CHECKPOINT SAVED**: Session checkpoint if long-running task

---

## 🟡 QUALITY CHECKS (Should Fix)

### 5. Architecture Alignment
- [ ] **12-STAGE PIPELINE**: Changes fit within Everest Ascent stages
- [ ] **SMART ROUTER USED**: LLM calls go through Smart Router V5
- [ ] **CORRECT TIER**: Task routed to appropriate tier (FREE/ULTRA_CHEAP/BALANCED)

### 6. Code Standards
- [ ] **TYPE HINTS**: All Python function signatures typed
- [ ] **DOCSTRINGS**: Google format on public functions
- [ ] **HTTPX NOT REQUESTS**: Async HTTP client used
- [ ] **PDFPLUMBER NOT PYPDF2**: Correct PDF library

### 7. Error Handling
- [ ] **SPECIFIC EXCEPTIONS**: No bare `except: pass`
- [ ] **CONTEXT IN LOGS**: case_number, stage included in errors
- [ ] **GRACEFUL DEGRADATION**: External API failures handled

### 8. Security
- [ ] **NO HARDCODED KEYS**: Secrets in GitHub Secrets only
- [ ] **PARAMETERIZED QUERIES**: No SQL injection risk
- [ ] **INPUT VALIDATED**: External data sanitized

---

## 🔵 OPTIMIZATION CHECKS (Nice to Have)

### 9. Performance
- [ ] **ASYNC I/O**: Awaited operations where applicable
- [ ] **BATCH OPERATIONS**: Grouped database calls
- [ ] **NO N+1 QUERIES**: Efficient data fetching

### 10. Documentation
- [ ] **DECISION LOGGED**: Why this approach vs alternatives
- [ ] **CHANGELOG UPDATED**: If user-facing change
- [ ] **README CURRENT**: If new feature/workflow

---

## Quick Reference: Known Claude Failure Patterns

| Pattern | Symptom | Prevention |
|---------|---------|------------|
| **File Replacement** | Entire file overwritten | Always read first, use str_replace |
| **Estimated Data** | Made-up Final Judgments | Only use BECA V22 verified data |
| **Permission Seeking** | "Should I proceed?" | Execute autonomously, report results |
| **Incomplete Workflow** | Stopped at first error | Debug and retry until complete |
| **Missing State Update** | PROJECT_STATE.json stale | Update after every decision |
| **Wrong HTTP Client** | Used `requests` | Always use `httpx` |
| **Wrong PDF Library** | Used PyPDF2 | Always use `pdfplumber` |
| **Secrets in Code** | API key in source | GitHub Secrets only |

---

## Enforcement

### Pre-Push Hook (Recommended)
```bash
#!/bin/bash
# .git/hooks/pre-push
echo "🔍 Running Pre-Deploy Checklist..."
# Add automated checks here
```

### Manual Review
Before running `git push`:
1. Open this checklist
2. Check each CRITICAL item
3. Address any QUALITY items
4. Document any skipped OPTIMIZATION items

### Post-Deploy Verification
```bash
# Verify deployment succeeded
curl -s https://brevard-bidder-landing.pages.dev/api/health | jq
# Check Supabase for new records
# Review GitHub Actions workflow status
```

---

## Scoring

| Category | Weight | Your Score |
|----------|--------|------------|
| Critical (4 items) | 40% | ___/4 |
| Quality (4 items) | 40% | ___/4 |
| Optimization (2 items) | 20% | ___/2 |

**Minimum to Deploy**: 100% Critical + 75% Quality = 7/8 required items

---

*Last Updated: December 2025*  
*Owner: Ariel Shapira / Claude AI Architect*
