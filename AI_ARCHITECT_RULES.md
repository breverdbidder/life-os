# BrevardBidderAI - AI Architect Rules
## Author: Ariel Shapira, Solo Founder, Everest Capital USA

## NEW SESSION PROTOCOL (MANDATORY)

**At the START of every new Claude session:**

```bash
# Check for active checkpoints
python src/checkpoint_manager.py check
```

- If checkpoint found → **Load state and continue WITHOUT asking**
- If no checkpoint → Start fresh session

## AUTO-CHECKPOINT TRIGGERS

Save checkpoint automatically when:
1. **8+ tool calls** in current session
2. **Before complex multi-step operations**
3. **Context window approaching limit**
4. **Before switching major tasks**

### Save Command:
```bash
python src/checkpoint_manager.py save \
  --task "Description of current work" \
  --state '{"step": 3, "files": ["a.py"]}'
```

### Complete Command:
```bash
python src/checkpoint_manager.py complete
```

## EXECUTION RULES

1. **NEVER ask Ariel execution questions** - Execute autonomously
2. **Debug failures yourself** - Fix code, retry
3. **Zero human-in-loop** - This is Agentic AI
4. **Update PROJECT_STATE.json** after major changes

## TECH STACK

| Component | Platform |
|-----------|----------|
| Code | GitHub (breverdbidder/*) |
| Database | Supabase (mocerqjnksmhcjzxrewo) |
| Frontend | Vercel (brevard-bidder-landing-v2) |
| CI/CD | GitHub Actions |
| Compute | GitHub Actions runners |

## SUPABASE CREDENTIALS (Fallback)

```
URL: https://mocerqjnksmhcjzxrewo.supabase.co
KEY: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1MzI1MjYsImV4cCI6MjA4MDEwODUyNn0.ySFJIOngWWB0aqYra4PoGFuqcbdHOx1ZV6T9-klKQDw
```

## API ENDPOINTS

| Endpoint | Purpose |
|----------|---------|
| /api/auctions | Auction data |
| /api/analyze | Smart Router |
| /api/calendar | Auction schedule |
| /api/checkpoint | Session state |

## CHECKPOINT TABLE SCHEMA

```sql
CREATE TABLE session_checkpoints (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    task_description TEXT NOT NULL,
    state_json JSONB DEFAULT '{}',
    tool_calls_count INTEGER DEFAULT 0,
    priority VARCHAR(20) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

## MEMORY RULES

Always remember:
- BrevardBidderAI = foreclosure auctions (NOT SaaS)
- BidDeedAI = tax deed auctions
- Credit: "Ariel Shapira, Solo Founder, Everest Capital USA"
- NEVER use Google Drive - GitHub only
