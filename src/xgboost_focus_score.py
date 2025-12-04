"""
XGBOOST FOCUS SCORE ENGINE v2.0
Daily ML-powered focus score calculation
Stores in daily_metrics.productivity_score (no new table needed)
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
    """XGBoost-inspired FOCUS Score Calculator (0-100)"""
    
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
                headers = {**HEADERS, "Prefer": "resolution=merge-duplicates,return=representation"}
                resp = requests.post(url, json=data, headers=headers, verify=False)
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
        
        # Get historical metrics for streak calculation
        week_ago = (datetime.strptime(target_date, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
        history = self._api_call('GET', f'daily_metrics?date=gte.{week_ago}&date=lt.{target_date}&order=date.desc')
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
        
        # Streak from historical productivity_score > 70
        good_days = 0
        for m in history:
            if (m.get('productivity_score') or 0) >= 70:
                good_days += 1
            else:
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
        return max(0, min(100, round(smoothed * 100, 1)))
    
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
            'interventions_count': len(data['interventions']),
            'calculated_at': datetime.now().isoformat(),
            'model_version': 'xgboost_v2.0'
        }
        
        # Store in daily_metrics.productivity_score + session_recommendation
        session_info = f"XGBoost {grade_info['grade']} ({score}/100). Features: {json.dumps(features)}. Insights: {'; '.join(insights)}"
        
        # Check if daily_metrics exists for today
        existing = self._api_call('GET', f'daily_metrics?date=eq.{target_date}')
        
        if existing and isinstance(existing, list) and len(existing) > 0:
            # Update existing record
            metric_id = existing[0]['id']
            update_data = {
                'productivity_score': score,
                'average_focus_quality': round(features['focus_quality'] * 10, 1),
                'session_recommendation': session_info[:500]
            }
            self._api_call('PATCH', f'daily_metrics?id=eq.{metric_id}', update_data)
            print(f"✅ Updated daily_metrics ID {metric_id}")
        else:
            # Create new record
            new_data = {
                'date': target_date,
                'user_id': 1,
                'productivity_score': score,
                'average_focus_quality': round(features['focus_quality'] * 10, 1),
                'completion_rate': features['completion_rate'],
                'context_switches': int((1 - features['context_switches']) * 20),
                'tasks_completed': result['tasks_completed'],
                'tasks_abandoned': len([t for t in data['tasks'] if t.get('status') == 'ABANDONED']),
                'intervention_count': result['interventions_count'],
                'session_recommendation': session_info[:500]
            }
            self._api_call('POST', 'daily_metrics', new_data)
            print(f"✅ Created daily_metrics for {target_date}")
        
        return result
    
    def get_latest_score(self) -> Optional[Dict]:
        result = self._api_call('GET', 'daily_metrics?order=date.desc&limit=1')
        if result and isinstance(result, list) and len(result) > 0:
            m = result[0]
            score = m.get('productivity_score') or 0
            grade_info = self.get_grade(score)
            return {
                'date': m.get('date'),
                'score': score,
                'grade': grade_info['grade'],
                'grade_emoji': grade_info['emoji'],
                'grade_label': grade_info['label'],
                'completion_rate': m.get('completion_rate', 0),
                'context_switches': m.get('context_switches', 0),
                'average_focus_quality': m.get('average_focus_quality', 0)
            }
        return None
    
    def get_weekly_trend(self) -> List[Dict]:
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        result = self._api_call('GET', f'daily_metrics?date=gte.{week_ago}&order=date.asc')
        if result and isinstance(result, list):
            trend = []
            for m in result:
                score = m.get('productivity_score') or 0
                grade_info = self.get_grade(score)
                trend.append({
                    'date': m.get('date'),
                    'score': score,
                    'grade': grade_info['grade']
                })
            return trend
        return []


if __name__ == "__main__":
    import sys
    engine = XGBoostFocusScore()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "calculate":
            date = sys.argv[2] if len(sys.argv) > 2 else None
            result = engine.calculate_daily_score(date)
            print(f"\n{'='*40}\n📊 DAILY FOCUS SCORE\n{'='*40}")
            print(f"Date: {result['date']}")
            print(f"Score: {result['score']} {result['grade_emoji']} {result['grade']}")
            print(f"Label: {result['grade_label']}")
            print(f"\nInsights:")
            for i in result['insights']:
                print(f"  {i}")
        elif command == "latest":
            result = engine.get_latest_score()
            print(json.dumps(result, indent=2) if result else "No scores found")
        elif command == "trend":
            trend = engine.get_weekly_trend()
            print("Weekly Trend:")
            for day in trend:
                print(f"  {day['date']}: {day['score']} ({day['grade']})")
    else:
        result = engine.calculate_daily_score()
        print(json.dumps(result, indent=2))
