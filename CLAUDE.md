# Life OS - ADHD-Optimized Productivity System

> **Ariel Shapira** | Personal Productivity & Family Management
> Dual Timezone: 🕐 FL (America/New_York) | IL (Asia/Jerusalem)

## Build & Test Commands

```bash
# Python (agents, tracking)
python -m pytest tests/ -v              # Run all tests
python -m black src/ --check            # Check formatting
python -m flake8 src/                   # Lint code

# Node.js (chat interface)
npm run dev                             # Dev server
npm run build                           # Production build

# GitHub Actions (production)
gh workflow run orchestrator.yml        # Trigger orchestrator
gh workflow run insert_insight.yml      # Insert to Supabase
gh run list --limit=5                   # Check workflow status
```

## Code Style

### Python
- **Version**: Python 3.11+
- **Formatting**: Black (88 char lines)
- **Type hints**: Required for public functions
- **Docstrings**: Google style

### JavaScript
- **Version**: Node 18+
- **Formatting**: Prettier, 2-space indent

## Architecture

### Life OS Domains

```
┌─────────────────────────────────────────────────────────────┐
│                      LIFE OS                                 │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│  BUSINESS   │  MICHAEL    │   FAMILY    │    PERSONAL      │
│             │  D1 SWIM    │             │                  │
├─────────────┼─────────────┼─────────────┼──────────────────┤
│ BidDeed.AI  │ SwimCloud   │ Shabbat     │ Health logs      │
│ Insurance   │ Nutrition   │ Holidays    │ Learning         │
│ Auctions    │ Recruiting  │ Events      │ ADHD tracking    │
└─────────────┴─────────────┴─────────────┴──────────────────┘
```

### Directory Structure

```
life-os/
├── src/
│   ├── agents/
│   │   └── orchestrator/           # Autonomous checkpoint system
│   ├── michael_d1_agents_v3/
│   │   ├── data/                   # SwimCloud data
│   │   └── agents/                 # D1 recruiting agents
│   └── utils/
├── .github/workflows/
│   ├── orchestrator.yml            # 30-min checkpoint
│   └── insert_insight.yml          # Supabase inserts
├── chat/                           # Chat interface
└── tests/
```

### Key Files

- `src/agents/orchestrator/autonomous_checkpoint_system.py` - Token monitoring
- `src/michael_d1_agents_v3/data/` - Swim times, rivals, meets
- `.github/workflows/orchestrator.yml` - 30-min + manual trigger

### External Services

| Service | Purpose | Config |
|---------|---------|--------|
| Supabase | Database (mocerqjnksmhcjzxrewo) | GitHub Secrets |
| GitHub Actions | Compute | .github/workflows/ |
| Cloudflare Pages | Chat hosting | Auto-deploy |
| SwimCloud | Michael's swim data | API scraping |

## Supabase Tables

| Table | Purpose |
|-------|---------|
| `insights` | Learning sessions, claude_performance |
| `michael_swim_times` | Personal bests, meet results |
| `michael_nutrition` | Keto tracking Mon-Thu |
| `michael_recruiting` | D1 coach outreach |
| `health_logs` | Ariel's health tracking |
| `tasks` | ADHD task tracking |
| `activities` | Daily activity log |

## Michael D1 Swimming

### Key Data Points
- **SwimCloud ID**: 3250085
- **Events**: 50/100/200 Free, 100 Fly, 100 Back
- **School**: Satellite Beach HS (Class 2027)
- **DOB**: July 22, 2009 (16 years old)

### Verified Rivals
| Name | SwimCloud ID | Power Index |
|------|--------------|-------------|
| Soto | 2928537 | 47 |
| Gordon | 1733035 | 90 |
| Domboru | 1518102 | - |

### Nutrition Protocol
- **Mon-Thu**: Strict keto (Michael Andrew model)
- **Fri-Sun**: Moderate carbs (Shabbat observance)
- Michael Andrew reference: 6'5-6'6", 190-205 lbs

## ADHD Task Tracking

### Task States
```
INITIATED → SOLUTION_PROVIDED → IN_PROGRESS → COMPLETED/ABANDONED/BLOCKED/DEFERRED
```

### Abandonment Detection
- Context switch without closure
- Session ends with task incomplete
- >30 min after solution with no update

### Intervention Levels
- **Level 1 (0-30 min)**: Quick check
- **Level 2 (30-60 min)**: Pattern observation
- **Level 3 (>60 min)**: Accountability alert

## Orthodox Observance

- **Shabbat**: Friday sunset → Saturday night
- **No work tasks during Shabbat**
- **Kosher dietary requirements**
- **Holiday calendar awareness**

## Daily Patterns

| Time | Energy | Best For |
|------|--------|----------|
| 9-11 AM | Peak | Complex tasks |
| 2-4 PM | Dip | Learning/admin |
| Evening | Family | No work pressure |

## Project Rules

### NEVER
- Store API keys in code
- Work on business tasks during Shabbat
- Use softening language ("Would you like...")
- Ask permission (execute autonomously)

### ALWAYS
- Log insights to Supabase via insert_insight.yml
- Track task state changes
- Call out abandonment patterns
- Update PROJECT_STATE.json

## Smart Router (Chat Interface)

- **Default Model**: gemini-2.5-flash (FREE, 1M context)
- **Chat URL**: life-os-aiy.pages.dev/chat
- **GOOGLE_API_KEY**: In Cloudflare env


---

## 🎯 PROMPTING & SESSION PATTERNS

### From Claude Code Masterclass (2025-12-22)

**Context Management**
- ALWAYS `/clear` context between major features to keep Claude "snappy and fast"
- Token bloat = slower responses + worse reasoning
- Clear before: switching domains (BUSINESS → MICHAEL → FAMILY), after complex debugging

**Question-Driven Development**
- END prompts with: "Anything else you want to add?" or "What would you improve here?"
- Opus 4.5 has better taste than other models - leverage proactive suggestions
- Treat Claude as creative partner, not just executor

**Plan Mode Protocol**
- Use plan mode (shift+tab x2) before ANY big feature
- Let Claude ask clarifying questions before building
- Multiple choice responses = faster decision making for ADHD

### Slash Commands Reference
| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/clear` | Reset context | Between domains |
| `/undo` | Revert last change | After mistakes |
| `/stats` | Token usage | Check limits |
| `/model` | Switch model | Confirm on Opus 4.5 |
| `/security-review` | Security audit | Before deploy |
| `/security-review` | Security audit | Before deploy |



## 🛡️ PRE-DEPLOY CHECKLIST

Before ANY deployment to production:

1. **`/security-review`** - Run Claude's security audit agent
2. **No hardcoded secrets** - All keys in GitHub Secrets / Cloudflare env
3. **Input validation** - All user inputs sanitized
4. **Error handling** - Try/catch on all external API calls
5. **Rate limiting** - Circuit breakers on external services
6. **Test locally** - `npm run build` / `python -m pytest` passes
7. **Git status clean** - All changes committed

### Security Review Triggers
- Before Cloudflare Pages deploy
- Before GitHub Actions workflow changes
- After adding new external API integrations
- After auth/payment code changes

