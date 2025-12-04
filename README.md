# 🏠 Life OS - Shapira Family Command Center

**Real-Time FOCUS-Optimized Life Tracking & Management**

Created by: **Ariel Shapira, Solo Founder - Everest Capital USA**

## 🎯 Live Dashboard

# https://shapira-life-os.vercel.app

## ✨ Features

### 🧠 XGBoost FOCUS Monitor
- Real-time abandonment risk prediction
- Focus quality tracking
- Energy level monitoring
- Context switch detection
- Automated interventions (Level 1/2/3)

### 📋 Task Tracking
- Every task logged with timestamp
- Status flow: INITIATED → SOLUTION_PROVIDED → IN_PROGRESS → COMPLETED/ABANDONED
- Domain categorization (ARIEL/MICHAEL/FAMILY/BUSINESS)
- Complexity scoring (1-10)

### 📊 Daily Reports
- Tasks completed/abandoned/in-progress
- Completion rate
- Productivity score
- Timeline of all events
- Pattern insights

### 🔄 Auto-Updates
- Dashboard refreshes every 30 seconds
- GitHub Actions monitors every 30 minutes
- Daily report generated at 9 PM EST

### 🚗 Travel & Family
- Driving tracker with mileage
- Hotel reservations
- Michael's swim meets
- Nutrition logging (Keto-Shabbat)

## 🛠️ Tech Stack

- **Frontend**: HTML5, TailwindCSS, Chart.js
- **Backend**: Python + Supabase
- **ML**: XGBoost-style focus predictor
- **Automation**: GitHub Actions (30-min cron)
- **Hosting**: Vercel (auto-deploy)

## 📁 Structure

```
life-os/
├── index.html              # Dashboard
├── scripts/
│   └── life_os_engine.py   # Core engine + XGBoost predictor
├── .github/workflows/
│   └── monitor.yml         # 30-minute monitoring cron
└── README.md
```

## 🔗 Links

- **Dashboard**: https://shapira-life-os.vercel.app
- **Database**: Supabase (mocerqjnksmhcjzxrewo)

---

*Life OS v2.0 - Built with ❤️ for FOCUS optimization*
