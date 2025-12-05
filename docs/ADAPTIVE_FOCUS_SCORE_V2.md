# Adaptive Focus Score v2.0
## XGBoost-Powered Life OS Scoring

### 🎯 Design Principles

1. **Time is Investment** - Driving 2.5hrs for Michael = 150 min FAMILY investment
2. **Responsibilities > Tasks** - "Be there for Michael" matters more than checkbox count
3. **Context Matters** - Travel days scored differently than deep work days
4. **Learn Over Time** - XGBoost adapts to Ariel's actual patterns

---

## 📊 New Database Schema

### 1. time_investments
Tracks HOW time is spent across domains and activities.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| user_id | INTEGER | Default 1 |
| date | DATE | Investment date |
| domain | VARCHAR(20) | BUSINESS, FAMILY, MICHAEL, PERSONAL |
| activity_type | VARCHAR(30) | DRIVING, DEEP_WORK, MEETING, ADMIN, SUPPORT, LEARNING |
| minutes | INTEGER | Duration |
| description | TEXT | What was done |
| location | VARCHAR(100) | Where |
| value_multiplier | DECIMAL | ML-learned value weight |

### 2. daily_responsibilities  
Tracks WHAT you committed to vs fulfilled.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| date | DATE | Responsibility date |
| domain | VARCHAR(20) | Domain |
| responsibility | TEXT | "Drive Michael to Ocala swim meet" |
| priority | INTEGER | 1-5 (5 = critical) |
| fulfilled | BOOLEAN | Did you show up? |
| time_invested | INTEGER | Minutes spent |
| notes | TEXT | Context |

### 3. daily_satisfaction
Training labels for XGBoost - YOUR subjective rating.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| date | DATE | Unique per day |
| satisfaction_score | INTEGER | 1-10 (end of day rating) |
| energy_level | INTEGER | 1-10 |
| day_type | VARCHAR(30) | work_day, travel_day, swim_meet, shabbat, rest_day |
| stress_level | INTEGER | 1-10 |
| notes | TEXT | Context |

### 4. focus_ml_models
Stores trained XGBoost models and their performance.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| model_version | VARCHAR(20) | v1.0, v1.1, etc |
| feature_importance | JSONB | What matters most |
| training_metrics | JSONB | MAE, R², etc |
| weights | JSONB | Domain/activity weights |
| trained_at | TIMESTAMP | When trained |
| active | BOOLEAN | Current production model |

---

## 🔢 Feature Engineering

### Input Features for XGBoost

| Feature | Source | Description |
|---------|--------|-------------|
| hours_business | time_investments | Total BUSINESS hours |
| hours_family | time_investments | Total FAMILY hours |
| hours_michael | time_investments | Total MICHAEL hours |
| hours_personal | time_investments | Total PERSONAL hours |
| pct_driving | time_investments | % of time driving |
| pct_deep_work | time_investments | % of time in deep work |
| pct_meetings | time_investments | % of time in meetings |
| responsibilities_fulfilled | daily_responsibilities | Count fulfilled |
| responsibilities_total | daily_responsibilities | Count expected |
| responsibility_rate | calculated | fulfilled / total |
| priority_weighted_rate | calculated | High priority completion |
| tasks_completed | task_states | Traditional task count |
| tasks_total | task_states | Total tasks |
| context_switches | daily_metrics | Domain switches |
| day_type | daily_satisfaction | Categorical |
| day_of_week | date | 0-6 |
| prev_day_score | daily_metrics | Yesterday's score |
| prev_day_satisfaction | daily_satisfaction | Yesterday's rating |
| sleep_hours | health_logs | If tracked |

### Target Variable
- **Primary:** satisfaction_score (1-10)
- **Secondary:** next_day_productivity (correlation analysis)

---

## 📈 Score Calculation v2.0

### Before XGBoost Training (Rule-Based Baseline)

```
Focus Score = 
  (responsibility_rate × 0.35) +           # Did you show up?
  (time_investment_score × 0.30) +         # Hours invested by domain
  (task_completion_rate × 0.20) +          # Traditional tasks
  (context_discipline × 0.15)              # Fewer switches = better

Where:
  time_investment_score = Σ(domain_hours × domain_weight) / target_hours
  context_discipline = 1 - (switches / max_expected_switches)
```

### After XGBoost Training (Adaptive)

```
Focus Score = 
  (rule_based_score × 0.5) +
  (xgboost_predicted_satisfaction × 10 × 0.5)

# Model continuously learns what patterns = high satisfaction for Ariel
```

---

## 🔄 Daily Flow

### Morning
1. Claude checks calendar → auto-creates responsibilities
2. Day type detected (travel_day, work_day, etc.)
3. Target hours per domain suggested based on day type

### Throughout Day
1. Claude logs time_investments as activities happen
2. Responsibilities marked fulfilled when completed
3. Real-time score updates on dashboard

### Evening (9 PM Prompt)
1. "Rate your day 1-10" → satisfaction_score
2. "Energy level 1-10" → energy_level
3. Auto-generates daily summary
4. Feeds XGBoost training data

### Weekly (Sunday Night)
1. XGBoost retrains on last 30 days
2. Updates feature_importance
3. Adjusts domain weights
4. New model deployed if metrics improve

---

## 📊 Example: Dec 4 Recalculated

### Traditional Score (Current)
- Tasks: 5 completed / 15 total = 33%
- Score: **65 (C+)** ← Unfair for travel day

### Adaptive Score v2.0

**Time Investments:**
| Domain | Activity | Minutes |
|--------|----------|---------|
| FAMILY | DRIVING | 150 |
| FAMILY | HOTEL_CHECKIN | 30 |
| MICHAEL | SUPPORT | 60 |
| BUSINESS | DEEP_WORK | 180 |
| **TOTAL** | — | **420 (7 hrs)** |

**Responsibilities:**
| Responsibility | Priority | Fulfilled |
|----------------|----------|-----------|
| Drive Michael to Ocala | 5 | ✅ |
| Check into hotel | 4 | ✅ |
| Support Michael at presentation | 4 | ✅ |
| Life OS deployment | 3 | ✅ |
| Dec 3 auction results | 2 | ⏸️ Deferred |

Responsibility Rate: 4/5 = **80%** (deferred ≠ failed)

**Calculated Score:**
- Responsibility: 80% × 0.35 = 28
- Time Investment: 420/480 target × 0.30 = 26.25
- Task Completion: 33% × 0.20 = 6.6
- Context Discipline: 80% × 0.15 = 12

**Total: 72.85 → 73 (B-)** 

Much fairer than 65!

---

## 🛠️ Implementation Phases

### Phase 1: Schema + Data Collection (This Week)
- [ ] Create new tables in Supabase
- [ ] Update dashboard to show time investments
- [ ] Add daily satisfaction prompt
- [ ] Claude auto-logs time investments

### Phase 2: Rule-Based v2 (Next Week)  
- [ ] Implement new scoring formula
- [ ] Domain balance visualization
- [ ] Responsibility tracking UI
- [ ] Daily/weekly reports

### Phase 3: XGBoost Training (Week 3)
- [ ] Collect 14+ days of satisfaction data
- [ ] Train initial model
- [ ] A/B test vs rule-based
- [ ] Deploy if metrics improve

### Phase 4: Continuous Learning (Ongoing)
- [ ] Weekly model retraining
- [ ] Feature importance dashboard
- [ ] Personalization insights
- [ ] "Your optimal day" recommendations

---

## 🎯 Success Metrics

| Metric | Target |
|--------|--------|
| Satisfaction prediction MAE | < 1.5 points |
| Score correlation with satisfaction | > 0.7 |
| User feels score is "fair" | Subjective ✅ |
| Responsibility tracking adoption | Daily use |
| Model improvement over time | Decreasing MAE |

