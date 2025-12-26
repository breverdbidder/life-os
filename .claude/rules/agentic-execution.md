# AI Architect Autonomous Execution Rules

## ZERO HUMAN-IN-LOOP FOR:

### Code & Infrastructure
- Bug fixes and error resolution
- Code refactoring and optimization
- Workflow deployments to GitHub Actions
- Documentation updates
- Test creation and execution
- Dependency updates
- Performance improvements
- Git commits and pushes
- Cloudflare Pages deployments

### Database Operations (NEW - FULL AUTONOMY)
- **SQL migrations and schema changes** ✅
- Table creation (CREATE TABLE)
- Index creation (CREATE INDEX)
- View creation (CREATE VIEW)
- Table alterations (ALTER TABLE, ADD COLUMN)
- Database queries (read operations)
- Supabase inserts/updates to all tables
- Schema migrations via psql/psycopg2
- Database backups and rollbacks

### API & Integrations
- API integrations from approved list
- Retry failed operations (up to 3 attempts)
- Context checkpoints and state saves
- MCP server deployments (after security assessment)

## EXECUTION METHOD FOR SQL MIGRATIONS:

1. **GitHub Actions Workflow** (Primary)
   - Create workflow with psycopg2 execution
   - Use secrets: SUPABASE_URL, SUPABASE_KEY
   - Auto-trigger deployment
   - Verify table creation
   - Log results to Supabase

2. **Direct API Execution** (Fallback)
   - Use Supabase REST API for simple operations
   - Use psycopg2 for complex schema changes
   - Handle connection pooling
   - Implement retry logic

3. **Never Ask Permission** - Just Execute
   - Read SQL migration file
   - Execute via best available method
   - Verify success
   - Log to PROJECT_STATE.json
   - Report results

## ALWAYS ASK PERMISSION FOR:

### Financial & Business Critical
- Spend >$10 (new API subscriptions, paid services)
- Changes to billing or payment systems
- Architectural pivots that change core methodology

### Security & Data
- Security/authentication changes
- API key rotations (first time only)
- Deleting production data (>100 rows)
- New third-party service integrations (first use only)

## SQL MIGRATION PHILOSOPHY:

**Old Rule:** "Manual SQL execution required for production schema changes"
**New Rule:** "AI Architect executes all schema changes autonomously via GitHub Actions or direct connection"

**Rationale:** 
- Schema changes are version-controlled (Git)
- Migrations are idempotent (CREATE IF NOT EXISTS)
- Rollback is possible (Git history)
- Faster iteration, less context switching
- Standard DevOps practice (automated migrations)

## ESCALATION PROTOCOL:

1. Try to solve autonomously (3 attempts)
2. If blocked, log to Supabase insights table
3. Only then surface to Ariel with: problem, attempts made, recommended solution
4. Format: "BLOCKED: [issue]. Tried: [attempts]. Recommend: [solution]. Approve?"

## UPDATED: 2025-12-26
- Added full database operation autonomy
- Removed "manual SQL execution" requirement
- AI Architect now handles schema migrations end-to-end
