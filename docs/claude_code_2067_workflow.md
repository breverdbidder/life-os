# Claude Code 2.0.67 - Everest Capital Workflow Reference

## New Features → Workflow Changes

### 1. Auto-Compacting (No Action Required)
**Before:** Manual /compact needed during long sessions
**Now:** Automatic, instant compacting

**Impact on 7hr autonomous sessions:**
- No more context window interruptions
- Smoother long-running implementations
- Remove any /compact reminders from workflows

---

### 2. Token Tracking (/stats)
**Command:** `/stats`

**Use for:**
- Daily burn rate against $200/mo Max subscription
- Model breakdown (Opus vs Sonnet usage)
- Optimize Smart Router V5 FREE tier targeting (40-55% goal)

**Recommended:** Check /stats at end of each session, log to Supabase `daily_metrics` if significant.

---

### 3. Session Management
**Features:**
- Rename: Give sessions meaningful names
- Search: Find past sessions by keyword

**Naming Convention for Everest:**
```
[REPO]-[FEATURE]-[DATE]
Examples:
- biddeed-beca-v22-dec12
- lifeos-orchestrator-dec12
- spd-discovery-agent-dec12
```

---

### 4. Plan Mode (Shift+Tab)
**Trigger:** Shift+Tab before complex prompts

**When to use:**
- Multi-file implementations
- 12-stage Everest Ascent pipeline work
- Cross-repo changes

**Key benefit:** Plans persist across conversations. No manual PROJECT_STATE.json updates for session continuity during Claude Code work.

**Note:** GitHub Actions orchestrator (`orchestrator.yml`) still handles automated checkpoints - different purpose than Plan Mode.

---

### 5. Mid-Prompt Model Switching (Option+P)
**Shortcut:** Option+P (Mac) / Alt+P (Windows)

**Strategy:**
| Task Type | Model |
|-----------|-------|
| Architecture decisions | Opus 4.5 |
| Code execution | Sonnet 4.5 |
| Bulk operations | Gemini Flash (via Smart Router) |

---

### 6. Cloudflare MCP Connector
**Status:** Requires manual setup (see cloudflare_mcp_setup.md)

**Enables:**
- Direct Pages deployment monitoring
- Environment variable management
- Build log access from Claude Desktop

---

## Updated AI Architect Rules

### REMOVED:
- ❌ Manual /compact during sessions
- ❌ PROJECT_STATE.json updates for session continuity (Plan Mode handles this)

### RETAINED:
- ✅ PROJECT_STATE.json for persistent architectural decisions
- ✅ GitHub Actions orchestrator for automated checkpoints
- ✅ Supabase logging for metrics/insights
- ✅ Zero human-in-loop principle

### ADDED:
- ✅ Use /stats to track token burn
- ✅ Name sessions with [REPO]-[FEATURE]-[DATE] convention
- ✅ Trigger Plan Mode (Shift+Tab) for multi-step implementations
- ✅ Switch models mid-prompt for cost optimization
