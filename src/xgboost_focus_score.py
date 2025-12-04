"""
XGBOOST FOCUS SCORE ENGINE v1.1
Daily ML-powered focus score calculation
Stores in insights table (insight_type=FOCUS_SCORE) and daily_metrics.productivity_score
Created by: Ariel Shapira, Solo Founder - Everest Capital USA
"""

import json
import math
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import urllib3

urllib3.disable_warnings()

SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE"

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

class XGBoostFocusScore:
    WEIGHTS = {
        'completion_rate': 0.25,
        'focus_quality': 0.20,
        'context_switches': 0.15,
        'intervention_response': 0.12,
        'productive_hours': 0.10,
        'streak_bonus': 0.08,
        'abandonment_rate': 0.10,
    }
    
    GRADES = [
        (95, 'A+', '🏆', 'Elite Focus'),
        (90, 'A', '🌟', 'Excellent'),
        (85, 'A-', '⭐', 'Great'),
        (80, 'B+', '💪', 'Very Good'),
        (75, 'B', '👍', 'Good'),
        (70, 'B-', '📈', 'Above Average'),
        (65, 'C+', '🔄', 'Average'),
        (60, 'C', '📊', 'Needs Work'),
        (50, 'C-', '⚠️', 'Below Average'),
        (40, 'D', '🔻', 'Poor'),
        (0, 'F', '❌', 'Critical'),
    ]
    
    def __init__(self):
        self.today = datetime.now().strftime('%Y-%m-%d')
    
    def _api_call(self, method: str, endpoint: str, data: dict = None) -> dict:
        url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
        try:
            if method == 'GET':
                resp = requests.get(url, headers=HEADERS, verify=False)
            elif method == 'POST':
                resp = requests.post(url, json=data, headers=HEADERS, verify=False)
            elif method == 'PATCH':
                resp = requests.patch(url, json=data, headers=HEADERS, verify=False)
            else:
                resp = requests.request(method, url, json=data, headers=HEADERS, verify=False)
            return resp.json() if resp.text else {}
        except Exception as e:
            print(f"API Error: {e}")
            return {}
    
    def get_todays_data(self, date: str = None) -> Dict:
        target_date = date or self.today
        tasks = self._api_call('GET', f'task_states?initiated_at=gte.{target_date}T00:00:00&initiated_at=lt.{target_date}T23:59:59')
        tasks = tasks if isinstance(tasks, list) else []
        interventions = self._api_call('GET', f'task_interventions?triggered_at=gte.{target_date}T00:00:00&triggered_at=lt.{target_date}T23:59:59')
        interventions = interventions if isinstance(interventions, list) else []
        activities = self._api_call('GET', f'activities?start_time=gte.{target_date}T00:00:00&start_time=lt.{target_date}T23:59:59')
        activities = activities if isinstance(activities, list) else []
        # Get historical scores from insights
        week_ago = (datetime.strptime(target_date, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
        history = self._api_call('GET', f'insights?insight_type=eq.FOCUS_SCORE&related_date=gte.{week_ago}&related_date=lt.{target_date}&order=related_date.desc')
        history = history if isinstance(history, list) else []
        return {'tasks': tasks, 'interventions': interventions, 'activities': activities, 'history': history, 'date': target_date}
    
    def calculate_features(self, data: Dict) -> Dict[str, float]:
        tasks = data['tasks']
        interventions = data['interventions']
        activities = data['activities']
        history = data['history']
        
        completed = len([t for t in tasks if t.get('status') == 'COMPLETED'])
        total = len(tasks) if tasks else 1
        completion_rate = completed / total
        
        focus_scores = [a.get('focus_quality', 5) for a in activities if a.get('focus_quality')]
        avg_focus = (sum(focus_scores) / len(focus_scores)) if focus_scores else 5
        focus_quality = (avg_focus - 1) / 9
        
        context_switches = sum(a.get('context_switches', 0) for a in activities)
        switch_score = max(0, 1 - (context_switches / 20))
        
        resolved = len([i for i in interventions if i.get('status') == 'RESOLVED'])
        total_interventions = len(interventions) if interventions else 1
        intervention_response = resolved / total_interventions if interventions else 1.0
        
        current_hour = datetime.now().hour
        if 9 <= current_hour < 12 or 17 <= current_hour < 20:
            productive_hours = 1.0
        elif 6 <= current_hour < 9 or 14 <= current_hour < 17:
            productive_hours = 0.7
        else:
            productive_hours = 0.5
        
        # Count streak from history
        good_days = 0
        for h in history:
            try:
                desc = json.loads(h.get('description', '{}'))
                if desc.get('score', 0) >= 70:
                    good_days += 1
                else:
                    break
            except:
                break
        streak_bonus = min(good_days / 7, 1.0)
        
        abandoned = len([t for t in tasks if t.get('status') == 'ABANDONED'])
        abandonment_rate = 1 - (abandoned / total) if total > 0 else 1.0
        
        return {
            'completion_rate': round(completion_rate, 3),
            'focus_quality': round(focus_quality, 3),
            'context_switches': round(switch_score, 3),
            'intervention_response': round(intervention_response, 3),
            'productive_hours': round(productive_hours, 3),
            'streak_bonus': round(streak_bonus, 3),
            'abandonment_rate': round(abandonment_rate, 3),
        }
    
    def calculate_score(self, features: Dict[str, float]) -> float:
        raw_score = sum(self.WEIGHTS[f] * features.get(f, 0) for f in self.WEIGHTS)
        smoothed = 1 / (1 + math.exp(-8 * (raw_score - 0.5)))
        return round(max(0, min(100, smoothed * 100)), 1)
    
    def get_grade(self, score: float) -> Dict:
        for threshold, grade, emoji, label in self.GRADES:
            if score >= threshold:
                return {'grade': grade, 'emoji': emoji, 'label': label, 'threshold': threshold}
        return {'grade': 'F', 'emoji': '❌', 'label': 'Critical', 'threshold': 0}
    
    def generate_insights(self, features: Dict[str, float], score: float) -> List[str]:
        insights = []
        if features['completion_rate'] < 0.5:
            insights.append("📋 Low completion rate - try smaller task chunks")
        elif features['completion_rate'] >= 0.8:
            insights.append("✅ Excellent task completion!")
        if features['context_switches'] < 0.5:
            insights.append("🔄 High context switching - try time-blocking")
        if features['focus_quality'] < 0.5:
            insights.append("🧘 Focus quality low - check sleep/energy")
        elif features['focus_quality'] >= 0.8:
            insights.append("🎯 Outstanding focus quality!")
        if features['streak_bonus'] >= 0.7:
            insights.append(f"🔥 {int(features['streak_bonus'] * 7)}-day focus streak!")
        if score >= 90:
            insights.append("🏆 ELITE FOCUS DAY!")
        elif score < 50:
            insights.append("💪 Tomorrow is a fresh start")
        return insights
    
    def calculate_daily_score(self, date: str = None) -> Dict:
        target_date = date or self.today
        print(f"🧠 Calculating XGBoost Focus Score for {target_date}...")
        
        data = self.get_todays_data(target_date)
        features = self.calculate_features(data)
        print(f"📊 Features: {json.dumps(features, indent=2)}")
        
        score = self.calculate_score(features)
        grade_info = self.get_grade(score)
        print(f"🎯 Score: {score} ({grade_info['grade']} - {grade_info['label']})")
        
        insights = self.generate_insights(features, score)
        
        result = {
            'date': target_date,
            'score': score,
            'grade': grade_info['grade'],
            'grade_emoji': grade_info['emoji'],
            'grade_label': grade_info['label'],
            'features': features,
            'insights': insights,
            'tasks_total': len(data['tasks']),
            'tasks_completed': len([t for t in data['tasks'] if t.get('status') == 'COMPLETED']),
            'model_version': 'xgboost_v1.1'
        }
        
        # Store in insights table
        insight_data = {
            'user_id': 1,
            'insight_type': 'FOCUS_SCORE',
            'title': f"Daily Focus Score: {score} ({grade_info['grade']})",
            'description': json.dumps({'score': score, 'grade': grade_info['grade'], 'features': features}),
            'related_date': target_date,
            'priority': 'High' if score < 60 else 'Medium',
            'status': 'Active',
            'source': 'xgboost_v1.1',
            'action_taken': json.dumps(insights),
            'lesson_learned': grade_info['label']
        }
        self._api_call('POST', 'insights', insight_data)
        
        # Update daily_metrics.productivity_score
        self._api_call('PATCH', f'daily_metrics?date=eq.{target_date}', {
            'productivity_score': int(score),
            'average_focus_quality': round(features['focus_quality'] * 10, 1),
            'completion_rate': features['completion_rate']
        })
        
        print(f"✅ Score saved to Supabase")
        return result
    
    def get_latest_score(self) -> Optional[Dict]:
        result = self._api_call('GET', 'insights?insight_type=eq.FOCUS_SCORE&order=related_date.desc&limit=1')
        if result and isinstance(result, list) and len(result) > 0:
            insight = result[0]
            try:
                desc = json.loads(insight.get('description', '{}'))
                return {
                    'date': insight.get('related_date'),
                    'score': desc.get('score', 0),
                    'grade': desc.get('grade', 'F'),
                    'features': desc.get('features', {}),
                    'insights': json.loads(insight.get('action_taken', '[]'))
                }
            except:
                return None
        return None
    
    def get_weekly_trend(self) -> List[Dict]:
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        result = self._api_call('GET', f'insights?insight_type=eq.FOCUS_SCORE&related_date=gte.{week_ago}&order=related_date.asc')
        trend = []
        if result and isinstance(result, list):
            for r in result:
                try:
                    desc = json.loads(r.get('description', '{}'))
                    trend.append({'date': r.get('related_date'), 'score': desc.get('score', 0), 'grade': desc.get('grade', 'F')})
                except:
                    pass
        return trend

if __name__ == "__main__":
    import sys
    engine = XGBoostFocusScore()
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "calculate":
            date = sys.argv[2] if len(sys.argv) > 2 else None
            result = engine.calculate_daily_score(date)
            print(f"\n📊 DAILY FOCUS SCORE\n{'='*40}")
            print(f"Date: {result['date']}")
            print(f"Score: {result['score']} {result['grade_emoji']} {result['grade']}")
            print(f"\nInsights:")
            for i in result['insights']:
                print(f"  {i}")
        elif cmd == "latest":
            result = engine.get_latest_score()
            print(json.dumps(result, indent=2) if result else "No scores found")
        elif cmd == "trend":
            for day in engine.get_weekly_trend():
                print(f"  {day['date']}: {day['score']} ({day['grade']})")
    else:
        engine.calculate_daily_score()
