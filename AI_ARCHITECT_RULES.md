# AI Architect Rules - BidDeed.AI V13.4.0
## Author: Ariel Shapira, Solo Founder, Everest Capital USA

## CLAUDE CODE 2.0.67+ CHANGES

### Plan Mode Replaces Manual State Management
Claude Code now has **native cross-conversation persistence** via Plan Mode (Shift+Tab).

**OLD WAY (deprecated):**
```
- Update PROJECT_STATE.json after every decision
- Manual /compact commands
- Aggressive checkpoint saves every 3 tool calls
```

**NEW WAY:**
```
- Use Plan Mode (Shift+Tab) for multi-step implementations
- Claude Code auto-compacts instantly (no manual intervention)
- SESSION_STATE.json for session-specific data only
- PROJECT_STATE.json for major milestones only
```

### When to Update PROJECT_STATE.json

| Scenario | Update PROJECT_STATE.json? |
|----------|---------------------------|
| Routine code changes | ❌ No - Plan Mode handles |
| Mid-implementation state | ❌ No - Plan Mode handles |
| Context after /compact | ❌ No - Auto-compact handles |
| **Major version release** | ✅ Yes |
| **New feature completed** | ✅ Yes |
| **Architecture decision** | ✅ Yes |
| **Breaking change** | ✅ Yes |

### Useful Commands (Native)
```
/stats          → Token usage tracking
Shift+Tab       → Plan Mode (implementation plans)
Option+P        → Switch models mid-prompt
Tab             → Accept prompt suggestions
```

## SESSION PROTOCOL - CONNECTION RESILIENT

### On EVERY New Chat:
```
1. CHECK for active checkpoint:
   - GET /api/checkpoint?action=check  (Vercel)
   - OR python src/checkpoint_manager.py check
   
2. If checkpoint found:
   - Resume IMMEDIATELY without asking
   - Load state from checkpoint
   - Continue where left off
   
3. If no checkpoint:
   - Start fresh session
   - Generate session_id: bba_YYYYMMDD_HHMMSS
```

### During Session - SMART AUTO-SAVE:
```
SAVE CHECKPOINT AFTER:
- Any file creation/modification
- Any API deployment
- Any database operation
- Before any long-running operation (>60s)
- Major milestone completion

SKIP CHECKPOINT FOR:
- Read-only operations
- Query/search operations
- Mid-implementation steps (Plan Mode handles)
```

### Connection Loss Recovery:
```
The checkpoint manager now:
1. ALWAYS saves locally first (~/.brevard_checkpoint_backup.json)
2. Queues cloud saves if offline (~/.brevard_offline_queue.json)
3. Auto-syncs queue when back online
4. Compares local vs cloud timestamps - uses newest

On reconnect after disconnect:
- Check for local backup
- Compare with cloud checkpoint
- Use whichever is newer
- Resume without losing work
```

## EXECUTION RULES

1. **NEVER ASK** - Execute autonomously
2. **DEBUG & FIX** - If failure, diagnose → fix → retry
3. **ZERO HUMAN-IN-LOOP** - Make decisions, don't ask permission
4. **MILESTONE STATE** - Update PROJECT_STATE.json only for major milestones
5. **USE GITHUB API** - REST API for all file operations
6. **IP PROTECTION** - Credit "Ariel Shapira, Solo Founder" everywhere

## MCP CONNECTORS (2.0.67+)

Claude Code now supports direct service integration:

| Connector | Use Case |
|-----------|----------|
| **Cloudflare** | Pages deployment status, redeploy, logs |
| Figma | Design asset access |
| Netlify | Alternative deployment management |

Setup: Claude Desktop → Settings → Connectors → Enable & Authenticate

## CHECKPOINT COMMANDS

```bash
# Check for active checkpoint
python src/checkpoint_manager.py check

# Manual save (major milestones only)
python src/checkpoint_manager.py save <session_id> "<task>" '{"state": "data"}'

# Complete session
python src/checkpoint_manager.py complete <session_id>

# Force sync offline queue
python src/checkpoint_manager.py sync

# Heartbeat (for long ops)
python src/checkpoint_manager.py heartbeat <session_id> "<current_task>"
```

## VERCEL API

```
GET  /api/checkpoint?action=check  → List active checkpoints
POST /api/checkpoint               → Save checkpoint
PATCH /api/checkpoint              → Complete checkpoint
```

## STATE LOCATIONS

| Location | Purpose | Update Frequency |
|----------|---------|------------------|
| Claude Plan Mode | Implementation context | Automatic |
| Supabase `session_checkpoints` | Primary cloud storage | On milestones |
| `~/.brevard_checkpoint_backup.json` | Local instant backup | On milestones |
| `PROJECT_STATE.json` | Project-level state | Major releases only |

## RECOVERY PRIORITY

1. Claude Plan Mode context (if same session)
2. Local backup (if newer)
3. Cloud checkpoint (if newer)
4. PROJECT_STATE.json (fallback)
5. Fresh start (last resort)

---
Last Updated: 2025-12-12
Version: 2.1 - Claude Code 2.0.67+ Optimized
