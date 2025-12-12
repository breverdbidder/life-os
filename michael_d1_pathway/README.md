# Michael D1 Pathway 🏊‍♂️

**LangGraph Multi-Agent Orchestration System for D1 Swimming Recruitment**

Primary Target: **University of Florida** | Class of **2027** | Coach: **Anthony Nesty**

## Overview

This system provides comprehensive AI-powered support for Michael Shapira's journey to D1 swimming at a Power 5 program. It coordinates 11 specialized agents through LangGraph orchestration, each with XGBoost ML integration for predictive analytics.

## Agents

| Agent | Description |
|-------|-------------|
| **UF Recruiting** | Primary target communications, time standards, outreach |
| **Kosher Diet** | Michael Andrew framework nutrition, keto/shabbat cycling |
| **Education** | NCAA eligibility, academic tracking, course planning |
| **Travel** | School visit logistics, scheduling |
| **Chabad Contacts** | Jewish community info at target schools |
| **Competitors** | Class of 2027 analysis, recruiting competition |
| **Engineering** | Program evaluation, Real Estate minor tracking |
| **Meet Prep** | Race strategy, taper plans, warm-up protocols |
| **Meet Results** | Performance analysis, D1 standards comparison |
| **Improvements** | Goal tracking, achievement probability |
| **School Compare** | Multi-factor school comparison with UF benchmark |

## UF Recruiting Standards (SCY)

| Event | A-Cut | B-Cut | Interest |
|-------|-------|-------|----------|
| 50 Free | 19.20 | 19.80 | 20.50 |
| 100 Free | 42.50 | 44.00 | 45.50 |
| 200 Free | 1:33.00 | 1:36.00 | 1:39.00 |
| 100 Fly | 46.00 | 48.00 | 50.00 |
| 100 Back | 46.50 | 48.50 | 50.50 |

## Architecture

```
michael_d1_pathway/
├── agents/                 # 11 specialized agents
│   ├── uf_recruiting_agent.py
│   ├── diet_agent.py
│   ├── education_agent.py
│   └── ...
├── orchestration/          # LangGraph state & graph
│   ├── state.py           # D1PathwayState definition
│   └── graph.py           # Multi-agent orchestration
├── config/                 # Configuration
│   └── settings.py
├── workflows/              # GitHub Actions
│   └── michael_d1_orchestrator.yml
├── main.py                 # Entry point
└── requirements.txt
```

## Usage

```python
from main import run_query

# Query the system
result = run_query(
    "What are my UF recruiting prospects?",
    current_times={
        "100 Free": 47.8,
        "50 Free": 21.5
    }
)

print(result["response"])
print(result["recommendations"])
```

## XGBoost Integration

Each agent includes ML models for:
- **Recruiting Probability** - Likelihood of recruitment to target schools
- **Performance Prediction** - Expected times at upcoming meets
- **Achievement Probability** - Likelihood of hitting target times by deadline
- **Career Outcome Prediction** - Academic/career trajectory forecasting

## Key Priorities

1. **Real Estate Minor** - First priority for academic planning
2. **Sprint Freestyle** - Primary event focus (50/100/200 Free)
3. **Kosher Observance** - Chabad availability critical
4. **UF First** - All comparison uses UF as primary benchmark

## Supabase Tables

- `michael_swim_times` - Performance tracking
- `michael_nutrition` - Diet logs
- `michael_recruiting` - Outreach tracking
- `goals` - Target times and milestones
- `insights` - System logs

---

**Author:** Claude Opus 4.5 (AI Architect)  
**Version:** 1.0.0  
**Created:** December 2025
