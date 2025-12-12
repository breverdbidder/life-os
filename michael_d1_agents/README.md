# Michael Shapira D1 Pathway - Multi-Agent Orchestration System

## 🏊 Overview

A LangGraph-based multi-agent AI system designed to support Michael Shapira's journey to becoming a D1 collegiate swimmer. The system coordinates specialized agents that handle different aspects of the recruiting process while respecting Orthodox Jewish observance.

## 🎯 Mission

Support Michael Shapira (Class of 2027, Satellite Beach High School) in achieving his goal of swimming at the Division 1 level, with University of Florida as the primary target.

## 🤖 Agent Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SUPERVISOR ROUTER                         │
│              (Intent Detection & Routing)                    │
└─────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   RECRUITING    │ │    EDUCATION    │ │     TRAVEL      │
│     AGENT       │ │     AGENT       │ │     AGENT       │
│                 │ │                 │ │                 │
│ • Outreach      │ │ • GPA Tracking  │ │ • Visit Plans   │
│ • Coach Comms   │ │ • NCAA Elig.    │ │ • Transport     │
│ • Time Analysis │ │ • Course Recs   │ │ • Scheduling    │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                   │                   │
          ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│      DIET       │ │     CHABAD      │ │   SWIM DATA     │
│     AGENT       │ │     AGENT       │ │     AGENT       │
│                 │ │                 │ │                 │
│ • Keto/Shabbat  │ │ • Jewish Life   │ │ • Times/Meets   │
│ • Meal Plans    │ │ • Kosher Food   │ │ • Performance   │
│ • Competition   │ │ • Hospitality   │ │ • Comparisons   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## 📁 Project Structure

```
michael_d1_agents/
├── agents/
│   ├── __init__.py
│   ├── kosher_diet_agent.py      # Nutrition (keto Mon-Thu, Shabbat Fri-Sun)
│   ├── education_agent.py         # NCAA eligibility & academics
│   ├── school_visit_agent.py      # D1 visit planning
│   └── chabad_contacts_agent.py   # Jewish resources at schools
├── orchestrator/
│   ├── __init__.py
│   └── langgraph_orchestrator.py  # Main coordinator
├── requirements.txt
└── README.md
```

## 🏊‍♂️ Michael's Profile

| Attribute | Value |
|-----------|-------|
| **Name** | Michael Shapira |
| **School** | Satellite Beach High School |
| **Graduation** | 2027 |
| **Events** | 50 Free, 100 Free, 100 Fly, 100 Back |
| **GPA** | 3.5 |
| **SAT** | 1280 |
| **Observance** | Orthodox (Shabbat, Kosher) |

### Personal Bests
- 50 Free: 23.22
- 100 Free: 50.82
- 100 Fly: 57.21
- 100 Back: 1:01.62

### Target Schools
1. **University of Florida** (Primary) - SEC
2. Florida State University - ACC
3. University of Miami - ACC
4. USF, FAU, FIU - G5/Mid-Major

## 🤖 Agents Detail

### 1. Recruiting Communications Agent
- Generates coach outreach emails
- Tracks recruiting timeline
- Analyzes swim times vs. program standards
- Manages communication schedule

### 2. Kosher Diet Agent
Based on Michael Andrew's framework, adapted for Orthodox observance:
- **Keto (Mon-Thu)**: 3200 cal, 180g protein, <50g carbs
- **Shabbat (Fri-Sun)**: 3500 cal, moderate carbs for glycogen
- Meal plans, shopping lists, competition nutrition

### 3. Education Achievement Agent
- NCAA D1 eligibility tracking (16 core courses, sliding scale)
- GPA monitoring (core vs. weighted)
- Course recommendations
- SAT/ACT prep guidance

### 4. School Visit Travel Agent
- Official/unofficial visit planning
- Shabbat-compliant scheduling
- Transportation recommendations
- Cost estimates
- Packing lists

### 5. Chabad Contacts Agent
- Chabad center info at each target school
- Kosher food resources
- Shabbat hospitality coordination
- Jewish life rankings

## 🚀 Usage

```python
from orchestrator import MichaelD1Orchestrator

# Initialize
orchestrator = MichaelD1Orchestrator()

# Process a query
result = orchestrator.process_query("Help me draft an email to UF swimming")

print(f"Intent: {result['detected_intent']}")
print(f"Agents Used: {result['agents_used']}")
print(f"Response: {result['primary_response']}")

# Get comprehensive status
status = orchestrator.get_comprehensive_status()
```

## 📊 Intent Detection

The Supervisor Router detects intent based on keywords:

| Intent | Keywords |
|--------|----------|
| recruiting | recruit, coach, email, outreach, time, cut, swim |
| diet | meal, eat, food, keto, protein, nutrition |
| education | gpa, sat, course, class, ncaa, eligibility |
| travel | visit, trip, drive, fly, hotel, cost |
| chabad | chabad, rabbi, kosher, shabbat, jewish |

## ⚡ Key Features

- **Orthodox Compliance**: All planning respects Shabbat and kosher requirements
- **Multi-Agent Coordination**: Agents share context and provide supplementary info
- **NCAA Eligibility**: Automated tracking of D1 academic requirements
- **Chabad Network**: Pre-loaded contacts for all Florida D1 schools
- **Michael Andrew Framework**: Keto cycling adapted for Orthodox swimmer

## 🔗 Integration Points

- **Supabase**: Database for tracking progress
- **GitHub Actions**: Automated workflows
- **Life OS**: Parent system integration

## 📅 Deployment

Part of the Life OS ecosystem:
- Repository: `breverdbidder/life-os`
- Workflow: GitHub Actions
- Database: Supabase (`mocerqjnksmhcjzxrewo`)

## 📞 Key Contacts

### Primary Target: University of Florida
- **Head Coach**: Anthony Nesty
- **Associate**: Steve Jungbluth
- **Chabad**: Rabbi Berl Goldman - (352) 336-5877

---

*Built for Ariel & Michael Shapira | Everest Capital USA*
