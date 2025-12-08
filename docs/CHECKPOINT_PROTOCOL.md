# Claude Session Checkpoint Protocol V2

## The Problem
- Web search returns 10K+ tokens per call
- 3-4 searches = 80% context consumed
- Tool-call count triggers (5/10/15) miss this
- Session crashes before checkpoint saves

## The Fix: Event-Based Triggers

### CHECKPOINT IMMEDIATELY AFTER:
1. **Every web_search result** - summarize findings, save to insights
2. **Every document created** - save artifact path and content summary
3. **Every 5 tool calls** - regardless of type
4. **Complex multi-step task start** - save plan before executing

### CHECKPOINT FORMAT (curl):
```bash
curl -sk "https://mocerqjnksmhcjzxrewo.supabase.co/rest/v1/insights" \
  -H "apikey: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1MzI1MjYsImV4cCI6MjA4MDEwODUyNn0.ySFJIOngWWB0aqYra4PoGFuqcbdHOx1ZV6T9-klKQDw" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1MzI1MjYsImV4cCI6MjA4MDEwODUyNn0.ySFJIOngWWB0aqYra4PoGFuqcbdHOx1ZV6T9-klKQDw" \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"insight_type":"SESSION_CHECKPOINT","title":"TASK: <summary>","description":"FINDINGS: <key points> | NEXT: <next steps>","priority":"critical","status":"active","source":"claude_autonomous"}'
```

### NEW CHAT PROTOCOL:
1. FIRST ACTION: Fetch latest checkpoint
```bash
curl -s "https://mocerqjnksmhcjzxrewo.supabase.co/rest/v1/insights?insight_type=eq.SESSION_CHECKPOINT&status=eq.active&order=created_at.desc&limit=1" \
  -H "apikey: <key>" -H "Authorization: Bearer <key>"
```
2. If checkpoint exists with status=active → Resume WITHOUT asking
3. Mark old checkpoint complete when task finishes

### RESEARCH SESSION SPECIAL HANDLING:
Web research sessions (multiple searches + synthesis):
- Checkpoint after EACH search with findings
- Store cumulative findings in description field
- If session crashes, next session has all research saved

### Anti-Patterns (NEVER DO):
- ❌ Waiting for 8+ tool calls to checkpoint
- ❌ Assuming research will fit in context
- ❌ Checkpointing only at task completion
- ❌ Asking "should I checkpoint?"
