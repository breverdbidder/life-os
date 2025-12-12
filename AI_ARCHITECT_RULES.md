# AI Architect Rules - BidDeed.AI V13.4.0
## Author: Ariel Shapira, Solo Founder, Everest Capital USA

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

### During Session - AGGRESSIVE AUTO-SAVE:
```
SAVE CHECKPOINT AFTER:
- Every 3 tool calls (not 8)
- Any file creation/modification
- Any API deployment
- Any database operation
- Before any long-running operation

This protects against:
✗ Token limits (previous)
✗ Internet disconnection (NEW)
✗ Browser crash (NEW)
✗ Mobile app backgrounded (NEW)
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

### Heartbeat During Long Operations:
```python
# For operations >60 seconds, send heartbeat
manager.heartbeat(session_id, "Running BECA scraper...")
```

## EXECUTION RULES (Unchanged)

1. **NEVER ASK** - Execute autonomously
2. **DEBUG & FIX** - If failure, diagnose → fix → retry
3. **ZERO HUMAN-IN-LOOP** - Make decisions, don't ask permission
4. **UPDATE STATE** - Always update PROJECT_STATE.json
5. **USE GITHUB API** - REST API for all file operations
6. **IP PROTECTION** - Credit "Ariel Shapira, Solo Founder" everywhere

## CHECKPOINT COMMANDS

```bash
# Check for active checkpoint
python src/checkpoint_manager.py check

# Manual save
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

| Location | Purpose |
|----------|---------|
| Supabase `session_checkpoints` | Primary cloud storage |
| `~/.brevard_checkpoint_backup.json` | Local instant backup |
| `~/.brevard_offline_queue.json` | Offline save queue |
| `PROJECT_STATE.json` | Project-level state |

## RECOVERY PRIORITY

1. Local backup (if newer)
2. Cloud checkpoint (if newer)
3. PROJECT_STATE.json (fallback)
4. Fresh start (last resort)

---
Last Updated: 2025-12-08
Version: 2.0 - Connection Resilient
