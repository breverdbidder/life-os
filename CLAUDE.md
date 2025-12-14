# Life OS - ADHD-Optimized Productivity System

> **Owner**: Ariel Shapira
> **AI Architect**: Claude (Anthropic)
> **Stack**: GitHub Actions + Supabase + Cloudflare Pages

---

## Build & Test Commands

```bash
# Core Operations
npm run dev                              # Local development server
npm run build                            # Production build
npm run test                             # Run test suite

# GitHub Actions Triggers
gh workflow run orchestrator.yml         # Run autonomous orchestrator
gh workflow run insert_insight.yml       # Insert insight to Supabase
gh workflow run michael_swim.yml         # Michael swim tracking

# Database Operations
curl -X POST "https://mocerqjnksmhcjzxrewo.supabase.co/rest/v1/insights" \
  -H "apikey: $SUPABASE_KEY" \
  -H "Content-Type: application/json" \
  -d '{"category": "learning", "data": {}}'

# Cloudflare Pages
npx wrangler pages deploy ./dist         # Deploy to Cloudflare
```

---

## Architecture

### Domains
```
BUSINESS     → Everest Capital, BidDeed.AI, Insurance
MICHAEL      → D1 Swimming, Nutrition, Recruiting
FAMILY       → Shabbat, Orthodox observance, Events
PERSONAL     → Health, Learning, Productivity
```

### Key Directories
```
src/
├── agents/             # Autonomous AI agents
├── api/                # Cloudflare Workers endpoints
├── dashboard/          # Web dashboard components
├── lib/                # Shared utilities
└── config/             # Configuration files

michael_d1_agents_v3/   # Michael D1 swim tracking
├── data/               # Swim times, rivals, meets
├── workflows/          # GitHub Actions
└── agents/             # Swim analysis agents

.github/workflows/      # GitHub Actions automation
├── orchestrator.yml    # 30-min autonomous orchestrator
├── insert_insight.yml  # Supabase data insertion
└── michael_swim.yml    # Swim tracking pipeline
```

### Database (Supabase)
- **Host**: mocerqjnksmhcjzxrewo.supabase.co
- **Tables**: 
  - `tasks` - Task tracking with ADHD states
  - `activities` - Activity logging
  - `insights` - AI-generated insights (learning, michael_swim, health_log)
  - `daily_metrics` - Daily productivity metrics
  - `michael_swim_times` - Swim performance data
  - `michael_nutrition` - Nutrition tracking
  - `task_interventions` - ADHD intervention logs

---

## Code Style

### JavaScript/TypeScript
- **Style**: ES modules, async/await
- **Linter**: ESLint with Prettier
- **Framework**: React for dashboard
- **API**: Cloudflare Workers

### Python (GitHub Actions)
- **Formatter**: Black (line length 100)
- **Linter**: Ruff
- **Type hints**: Required
- **Async**: Use httpx for HTTP requests

---

## ADHD Task States

```
INITIATED → SOLUTION_PROVIDED → IN_PROGRESS → COMPLETED
                                           ↘ ABANDONED
                                           ↘ BLOCKED
                                           ↘ DEFERRED
```

### Intervention Triggers
- Context switch without closure
- >30 min after solution with no update
- Session ends with task incomplete

---

## Michael D1 Swimming

### Events
- 50 Free, 100 Free, 200 Free
- 100 Fly, 100 Back

### SwimCloud
- Michael ID: 3250085
- Verified rivals: Soto (2928537), Gordon (1733035), Domboru (1518102)

### Diet Protocol
- **Mon-Thu**: Strict keto (Michael Andrew protocol)
- **Fri-Sun**: Moderate carbs (Shabbat observance)

---

## Critical Rules

1. **NEVER ask execution questions** - Execute autonomously
2. **Dual timezone awareness** - FL (America/New_York) | IL (Asia/Jerusalem)
3. **Supabase for persistence** - Use insert_insight.yml workflow
4. **No local curl** - All API calls via GitHub Actions
