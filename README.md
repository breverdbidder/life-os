# 🏠 Life OS - Shapira Family Ecosystem

**Real-Time Life Monitoring & Tracking Platform**  
*ADHD-Optimized • Family Coordination • Autonomous Updates*

---

## 🌐 Live Dashboard

**https://life-os-dashboard.vercel.app**

---

## 📊 Core Features

### 🚗 Travel & Driving Tracker
- Real-time trip monitoring
- Mileage tracking with distance calculations
- Departure times & ETA
- Multi-traveler support
- Route visualization

### 🏊 Michael's Swimming
- Swim meet tracking (events, seed times, results)
- Keto-Shabbat nutrition monitoring
- D1 recruiting progress
- Performance analytics

### 👨‍👩‍👦 Family Coordination
- Real-time family member status
- Location tracking (home, traveling, event)
- Shabbat preparation checklists
- Family calendar sync

### 🏨 Reservations & Bookings
- Hotel reservations with check-in/out
- Event bookings
- Travel itineraries

### 📱 WhatsApp Sharing
- One-tap share updates
- Trip status messages
- Swim meet info sharing
- Full daily summaries
- Direct number sending

### 📋 ADHD Task Management
- Task states: INITIATED → IN_PROGRESS → COMPLETED
- Intervention system (3 levels)
- Abandonment detection
- Micro-commitment support
- Focus scoring

### 🥗 Nutrition Tracking
- Michael's keto diet (M-Th)
- Shabbat carb adjustment (F-Su)
- Pre-competition meals
- Macro tracking (calories, protein, carbs)

---

## 🏠 Home Base

**390 Roosevelt Ave, Satellite Beach, FL 32937**  
Brevard County, Florida

---

## 👨‍👩‍👦 Family Members

| Member | Role | Domains |
|--------|------|---------|
| **Ariel Shapira** | Managing Member, Everest Capital | Business, Personal |
| **Mariam Shapira** | Property360, Protection Partners | Business |
| **Michael Shapira** | D1 Swimmer, Satellite Beach HS | Swimming, Nutrition |

---

## 🔧 Technical Stack

- **Frontend**: HTML5, TailwindCSS, Chart.js
- **Backend**: Supabase (PostgreSQL)
- **Hosting**: Vercel (auto-deploy)
- **Repository**: GitHub
- **Integrations**: WhatsApp Web API

---

## 📁 Project Structure

```
life-os/
├── dashboard/
│   └── index.html          # Main dashboard
├── api/
│   └── (future endpoints)
├── scripts/
│   └── utils/
│       └── supabase_client.py
├── vercel.json
├── requirements.txt
└── README.md
```

---

## 🗄️ Database Schema (Supabase)

Using `activities` table with `platform='life_os'`:

| activity_type | Description |
|---------------|-------------|
| `DRIVING` | Trip/travel records |
| `TASK` | Daily tasks |
| `SWIM_MEET` | Michael's competitions |
| `HOTEL` | Reservations |
| `NUTRITION` | Meal tracking |

---

## 🚀 Roadmap

- [x] Real-time dashboard
- [x] Travel/mileage tracking
- [x] Swim meet management
- [x] WhatsApp sharing
- [x] Hotel reservations
- [x] Nutrition tracking
- [ ] GPS live tracking
- [ ] Calendar integrations
- [ ] Mobile app (React Native)
- [ ] Voice updates (Alexa/Google)
- [ ] Automated reminders
- [ ] Family chat integration

---

## 📱 WhatsApp Message Templates

### Trip Update
```
🚗 *TRAVEL UPDATE*
━━━━━━━━━━━━━━━
📍 From: [Origin]
📍 To: [Destination]
🛣️ Distance: [X] miles
⏱️ Est. Time: [X]h [X]m
👥 Travelers: [Names]
```

### Swim Meet
```
🏊 *MICHAEL'S SWIM MEET*
━━━━━━━━━━━━━━━
🏆 [Meet Name]
📍 [Location]
Events: [List]
⏰ Warmup: [Time]
```

---

## 🔐 Environment Variables

```env
SUPABASE_URL=https://mocerqjnksmhcjzxrewo.supabase.co
SUPABASE_KEY=[service_role_key]
```

---

## 👤 Created By

**Ariel Shapira**  
Solo Founder - Everest Capital USA  
Real Estate Developer & Technology Innovator

---

## 📄 License

Private - Shapira Family Use

---

*Life OS v2.1 - December 2025*
