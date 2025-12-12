# Michael Shapira D1 Pathway V2.2 - Enhanced Multi-Agent System

## 🏊 Overview

Advanced LangGraph-based multi-agent AI orchestration for Michael's D1 pathway.

**Primary Target: University of Florida Class of 2027**

## V2.2 New Features

- **Agent #13: Personal Best Time Scraping Agent** - Automated PB data collection
- **Enhanced Agent #12** - Comprehensive competitor PB display in meet prep docs
- **SwimCloud API Integration** - Automated competitor data scraping
- **72-Hour Pre-Meet Trigger** - Auto-scrape competitor PBs before each meet
- **Full Metadata Storage** - Date, meet name, location, club/HS for all PBs

## 🤖 13 Specialized Agents

| # | Agent | XGBoost Model | Primary Function |
|---|-------|---------------|------------------|
| 1 | Kosher Diet | NUTRITION_OPTIMIZER | Keto Mon-Thu, Shabbat Fri-Sun |
| 2 | Education | ACADEMIC_PREDICTOR | GPA, NCAA eligibility |
| 3 | Travel | TRAVEL_OPTIMIZER | School visit planning |
| 4 | Chabad Contacts | COMMUNITY_ANALYZER | Jewish life resources |
| 5 | Competitor Analysis | COMPETITOR_PREDICTOR | Track UF 2027 recruits |
| 6 | Engineering | CAREER_FORECASTER | Real estate minor priority |
| 7 | Meet Prep | RACE_STRATEGY | Pre-meet analysis |
| 8 | Meet Results | PERFORMANCE_TRAJECTORY | Performance tracking |
| 9 | Goals | GOAL_ACHIEVEMENT | UF target tracking |
| 10 | Events Schedule | MEET_QUALIFIER | Meet calendar |
| 11 | School Comparison | PROGRAM_MATCHER | Program matching |
| 12 | **Meet Prep & Motivation** | MOTIVATION_OPTIMIZER | **48-72hr docs with competitor PBs** |
| **13** | **PB Scraping** | **PB_IMPROVEMENT_PREDICTOR** | **SwimCloud/USA Swimming scraping** |

## 🆕 Agent #13: Personal Best Time Scraping

### Features
- Scrapes SwimCloud, USA Swimming, HS databases
- Maintains PB database in Supabase
- Auto-triggers 72 hours before meets
- Tracks Michael + all competitors (Bastian Soto, Aaron Gordon, etc.)

### Data Stored
```python
PersonalBestTime:
  - swimmer_name
  - event
  - time
  - date_achieved
  - meet_name
  - meet_location
  - swim_club
  - high_school
  - competition_level (club/hs/usa_swimming)
```

## 📊 Enhanced Meet Prep Documents

V2.2 meet prep documents now include:

### Michael's Section
| Event | Seed | **Personal Best** | PB Date | PB Meet |
|-------|------|-------------------|---------|---------|
| 100 Free | 50.82 | **50.82** | 2025-11-15 | Senior Champs |

### Competitor Analysis Section
| Name | Club | High School | Seed | PB | PB Date | PB Meet |
|------|------|-------------|------|-----|---------|---------|
| Bastian Soto | Brevard Aquatic | Eau Gallie HS | - | 49.82 | 2025-11-10 | Fall Classic |
| Aaron Gordon | Melbourne ST | Melbourne HS | - | 51.15 | 2025-11-05 | Regional Champs |

## 🚀 Usage

```python
from orchestrator_v2 import MichaelD1OrchestratorV2
from datetime import date

orchestrator = MichaelD1OrchestratorV2()

# Scrape competitor PBs
result = orchestrator.scrape_competitor_pbs(
    ["Bastian Soto", "Aaron Gordon"],
    ["100 Free", "50 Free", "100 Fly"]
)

# Generate meet prep document
doc = orchestrator.generate_meet_prep_document(
    "Harry Meisel Championships",
    date(2025, 12, 13),
    ["100 Free", "50 Free", "100 Fly"],
    ["Bastian Soto", "Aaron Gordon"]
)
```

## 📁 GitHub Structure

```
breverdbidder/life-os/
├── michael_d1_agents_v2/
│   ├── orchestrator_v2.py      # V2.2 - 13 agents
│   └── README.md
└── .github/workflows/
    └── meet_prep_automation.yml  # Auto-generate docs
```

## 🔧 GitHub Actions Automation

- **Daily 6 AM EST**: Check for meets in 48-72 hour window
- **Auto-scrape**: Competitor PBs before each meet
- **Auto-generate**: Meet prep documents
- **Supabase logging**: All scrape results persisted

---

**Version**: 2.2 | **Agents**: 13 | **Target**: UF 2027
