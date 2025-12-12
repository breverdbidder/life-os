# Michael Shapira D1 Pathway V2 - Enhanced Multi-Agent System

## 🏊 Overview

An advanced LangGraph-based multi-agent AI orchestration system for Michael Shapira's D1 collegiate swimming pathway. **Primary Target: University of Florida Class of 2027**.

### V2 Enhancements over V1:
- **11 Specialized Agents** (vs 5 in V1)
- **XGBoost ML Integration** per agent
- **Bridge Integration** (Claude Chat ↔ Orchestrator API)
- **Event Bus** (Pub/Sub for inter-agent communication)
- **Shared State Repository**
- **Priority Queue Management**

---

## 🎯 Primary Target

**University of Florida Swimming - Class of 2027**
- Conference: SEC
- Head Coach: Anthony Nesty
- Engineering Program: Top 10 nationally
- Real Estate Minor: ✅ Available (Warrington College)
- Chabad: Rabbi Berl Goldman - 700+ weekly attendance

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         BRIDGE INTEGRATION                           │
│  ┌─────────────┐  ┌──────────────────┐  ┌────────────────────────┐  │
│  │   Request   │→ │   Orchestrator   │→ │     Response           │  │
│  │ Interpreter │  │   Interface      │  │   Synthesizer          │  │
│  └─────────────┘  └──────────────────┘  └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                │
         ┌──────────────────────┼──────────────────────┐
         │                      │                      │
         ▼                      ▼                      ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  SHARED STATE   │   │   EVENT BUS     │   │ PRIORITY QUEUE  │
│   REPOSITORY    │   │   (Pub/Sub)     │   │   MANAGEMENT    │
└─────────────────┘   └─────────────────┘   └─────────────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                │
    ┌───────────────────────────┼───────────────────────────┐
    │                           │                           │
    ▼                           ▼                           ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│  KOSHER   │ │ EDUCATION │ │  TRAVEL   │ │  CHABAD   │ │COMPETITOR │
│   DIET    │ │           │ │           │ │ CONTACTS  │ │ ANALYSIS  │
│  +XGBoost │ │  +XGBoost │ │  +XGBoost │ │  +XGBoost │ │  +XGBoost │
└───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘

┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ENGINEERING│ │ MEET PREP │ │  MEET     │ │  GOALS &  │ │  EVENTS   │
│   OPPS    │ │& STRATEGY │ │  RESULTS  │ │IMPROVEMENT│ │ SCHEDULE  │
│  +XGBoost │ │  +XGBoost │ │  +XGBoost │ │  +XGBoost │ │  +XGBoost │
└───────────┘ └───────────┘ └───────────┘ └───────────┘ └───────────┘

                        ┌───────────┐
                        │  SCHOOL   │
                        │COMPARISON │
                        │  +XGBoost │
                        └───────────┘
```

---

## 🤖 11 Specialized Agents

| # | Agent | XGBoost Model | Primary Function |
|---|-------|---------------|------------------|
| 1 | **Kosher Diet** | NUTRITION_OPTIMIZER | Keto Mon-Thu, Shabbat Fri-Sun, competition nutrition |
| 2 | **Education** | ACADEMIC_PREDICTOR | GPA tracking, NCAA eligibility, course planning |
| 3 | **Travel** | TRAVEL_OPTIMIZER | School visit planning, Shabbat-compliant scheduling |
| 4 | **Chabad Contacts** | COMMUNITY_ANALYZER | Jewish life resources at target schools |
| 5 | **Competitor Analysis** | COMPETITOR_PREDICTOR | Track UF 2027 recruits, competitive positioning |
| 6 | **Engineering Opps** | CAREER_FORECASTER | Real estate minor priority, career outcomes |
| 7 | **Meet Prep** | RACE_STRATEGY | Pre-meet analysis, race strategy optimization |
| 8 | **Meet Results** | PERFORMANCE_TRAJECTORY | Post-meet analysis, time progression tracking |
| 9 | **Goals & Improvement** | GOAL_ACHIEVEMENT | UF 2027 target tracking, milestone management |
| 10 | **Events Schedule** | MEET_QUALIFIER | Meet calendar, qualification cuts, coach attendance |
| 11 | **School Comparison** | PROGRAM_MATCHER | Multi-factor school ranking, fit analysis |

---

## 📊 XGBoost ML Integration

Each agent has a dedicated XGBoost model that provides:

- **Predictive Analytics**: Future performance, goal achievement probability
- **Pattern Recognition**: Training effectiveness, competition trends
- **Optimization Recommendations**: Taper timing, meet selection, course scheduling

### Model Types:
```python
class XGBoostModelType(Enum):
    NUTRITION_OPTIMIZER = "nutrition_optimizer"
    ACADEMIC_PREDICTOR = "academic_predictor"
    TRAVEL_OPTIMIZER = "travel_optimizer"
    COMMUNITY_ANALYZER = "community_analyzer"
    COMPETITOR_PREDICTOR = "competitor_predictor"
    CAREER_FORECASTER = "career_forecaster"
    RACE_STRATEGY = "race_strategy"
    PERFORMANCE_TRAJECTORY = "performance_trajectory"
    GOAL_ACHIEVEMENT = "goal_achievement"
    MEET_QUALIFIER = "meet_qualifier"
    PROGRAM_MATCHER = "program_matcher"
```

---

## 🌉 Bridge Integration

The Bridge connects Claude AI Chat ↔ LangGraph Orchestrator:

### Components:

1. **Request Interpreter**
   - Analyzes incoming chat messages
   - Extracts user intent (13 intent categories)
   - Identifies context (school, event, meet)

2. **Orchestrator Interface**
   - Routes to appropriate agents
   - Manages agent activation sequence
   - Handles multi-agent queries

3. **Response Synthesizer**
   - Aggregates multi-agent outputs
   - Prioritizes ML insights
   - Formats coherent response

4. **Context Persistence**
   - Maintains conversation history
   - Tracks state across interactions

---

## 📡 Inter-Agent Communication

### Event Bus (Pub/Sub)
```python
class EventType(Enum):
    NEW_MEET_RESULT = "new_meet_result"
    TIME_IMPROVEMENT = "time_improvement"
    ACADEMIC_UPDATE = "academic_update"
    GOAL_ACHIEVED = "goal_achieved"
    SCHOOL_VISIT_SCHEDULED = "school_visit_scheduled"
    COACH_CONTACT = "coach_contact"
```

### Agent Subscriptions:
- **Goals Agent** subscribes to `TIME_IMPROVEMENT` → Updates milestones
- **Meet Prep Agent** subscribes to `COMPETITOR_UPDATE` → Adjusts strategy
- **School Comparison** aggregates from multiple agents

---

## 🚀 Usage

```python
from orchestrator_v2 import MichaelD1OrchestratorV2

# Initialize
orchestrator = MichaelD1OrchestratorV2()

# Process query through bridge
result = orchestrator.process_query("What's my progress toward UF?")

print(f"Intent: {result['interpretation']['primary_intent']}")
print(f"Agents: {result['response']['agents_consulted']}")
print(f"ML Insights: {len(result['response']['ml_insights'])}")

# Get UF-focused dashboard
dashboard = orchestrator.get_uf_dashboard()
print(f"Gap Analysis: {dashboard['gap_analysis']}")

# Record meet result (triggers event bus)
orchestrator.update_meet_result("100 Free", 49.5)
```

---

## 📈 UF 2027 Gap Analysis

| Event | Current PB | UF Target | Gap | Status |
|-------|------------|-----------|-----|--------|
| 50 Free | 23.22 | 20.50 | +2.72s | ✅ On track |
| 100 Free | 50.82 | 45.00 | +5.82s | 🔴 Major gap |
| 100 Fly | 57.21 | 50.00 | +7.21s | 🔴 Major gap |
| 100 Back | 61.62 | 52.00 | +9.62s | 🔴 Major gap |

**ML Goal Achievement Probability**: Calculated dynamically based on training consistency, time progression, and months remaining.

---

## 📁 File Structure

```
michael_d1_agents_v2/
├── orchestrator_v2.py          # Main V2 system (11 agents + bridge)
├── README.md                   # This documentation
└── requirements.txt            # Dependencies
```

---

## 🔧 Dependencies

```
# Core
typing-extensions>=4.0.0
pydantic>=2.0.0

# ML (when deploying with real models)
xgboost>=2.0.0
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0

# API/Database
httpx>=0.25.0
supabase>=2.0.0

# LangGraph (when available)
# langgraph>=0.0.30
```

---

## 🎯 Key Features

### Real Estate Minor Priority
The Engineering Opportunities Agent prioritizes schools offering real estate as a minor:
- ✅ UF: Warrington College of Business
- ✅ Georgia Tech: Scheller College of Business
- ❌ FSU: Not Available

### Orthodox Compliance
All planning respects Shabbat and kosher requirements:
- Shabbat-compliant visit scheduling
- Kosher meal planning for travel
- Chabad hospitality coordination

### UF-First Strategy
All agents benchmark against UF 2027 recruiting standards:
- Time targets from UF walk-on/scholarship levels
- Coach contact tracking
- Visit planning prioritization

---

## 📊 Sample Output

```
💬 Query: "What's my progress toward UF?"
   🎯 Intent: goals
   🤖 Agents: goals, meet_results
   📊 ML Confidence: 84.0%

📊 UF 2027 DASHBOARD:
   Target: University of Florida 2027
   Gap Analysis:
      50 Free: +2.72s ✅ On track
      100 Free: +5.82s 🔴 Major gap
      100 Fly: +7.21s 🔴 Major gap
      100 Back: +9.62s 🔴 Major gap

   Agents Active: 11
   ML Models: 11 XGBoost instances
```

---

## 🔗 Integration Points

- **Life OS**: Parent system in `breverdbidder/life-os`
- **Supabase**: Database for historical data and ML training
- **GitHub Actions**: Automated workflows
- **SwimCloud API**: Competitor and time data (future)

---

*Built for Ariel & Michael Shapira | Everest Capital USA*
*Primary Target: University of Florida 2027 - Go Gators! 🐊*
