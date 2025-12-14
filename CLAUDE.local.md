# Life OS Local Configuration

> **DO NOT COMMIT ACTUAL VALUES** - Local development only

## Local Development Settings

### Sandbox URLs
- Supabase Local: http://localhost:54321
- API Testing: http://localhost:3000

### Development Mode
- Skip Supabase writes in testing
- Mock SwimCloud API calls
- Disable production notifications

## Secrets Reference (Use Environment Variables)

```bash
export SUPABASE_URL="https://mocerqjnksmhcjzxrewo.supabase.co"
export SUPABASE_KEY="[from environment]"
export SWIMCLOUD_API="[if available]"
```

## Local Testing

```bash
# Run tests without external calls
MOCK_EXTERNAL=true python -m pytest tests/ -v

# Test ADHD tracking locally
python src/adhd_tracker.py --dry-run
```
