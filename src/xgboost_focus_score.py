"""
XGBOOST FOCUS SCORE ENGINE v1.1
Daily ML-powered focus score calculation
Created by: Ariel Shapira, Solo Founder - Everest Capital USA

V1.1: Dual-write to focus_scores AND daily_metrics for compatibility
"""

import json
import math
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import urllib3

urllib3.disable_warnings()

# ============================================================
# CONFIGURATION
# ============================================================

SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE"

HEADERS = {
    "apikey": SERVICE_KEY,
    "Authorization": f"Bearer {SERVICE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}


class XGBoostFocusScore:
    """
    XGBoost-inspired FOCUS Score Calculator
    Generates a 0-100 daily focus score using weighted ML features
    """
    
    # Feature weights (XGBoost-style learned weights)
    WEIGHTS = {
        'completion_rate': 0.25,         # Tasks completed / total
        'focus_quality': 0.20,           # Average focus quality (1-10)
        'context_switches': 0.15,        # Fewer = better (inverted)
        'intervention_response': 0.12,   # Responded vs ignored
        'productive_hours': 0.10,        # Time in peak hours (9-12, 17-20)
        'streak_bonus': 0.08,            # Consecutive good days
        'abandonment_rate': 0.10,        # Lower = better (inverted)
    }
    
    # Grade thresholds
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
    
    def _api_call(self, method: str, endpoint: str, data: dict = None, upsert: bool = False) -> dict:
        """Make Supabase API call"""
        url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
        try:
            if method == 'GET':
                resp = requests.get(url, headers=HEADERS, verify=False, timeout=30)
            elif method == 'POST':
                headers = {**HEADERS}
                if upsert:
                    headers["Prefer"] = "resolution=merge-duplicates,return=representation"
                resp = requests.post(url, json=data, headers=headers, verify=False, timeout=30)
            else:
                resp = requests.request(method, url, json=data, headers=HEADERS, verify=False, timeout=30)
            return resp.json() if resp.text else {}
        except Exception as e:
            print(f"API Error: {e}")
            return {}
    
    def get_todays_data(self, date: str = None) -> Dict:
        """Fetch all data needed for scoring"""
        target_date = date or self.today
        
        # Get tasks
        tasks = self._api_call('GET', f'task_states?initiated_at=gte.{target_date}T00:00:00&initiated_at=lt.{target_date}T23:59:59')
        tasks = tasks if isinstance(tasks, list) else []
        
        # Get interventions
        interventions = self._api_call('GET', f'task_interventions?triggered_at=gte.{target_date}T00:00:00&triggered_at=lt.{target_date}T23:59:59')
        interventions = interventions if isinstance(interventions, list) else []
        
        # Get activities
        activities = self._api_call('GET', f'activities?start_time=gte.{target_date}T00:00:00&start_time=lt.{target_date}T23:59:59')
        activities = activities if isinstance(activities, list) else []
        
        # Get historical metrics (last 7 days) - check both tables
        week_ago = (datetime.strptime(target_date, '%Y-%m-%d') - timedelta(days=7)).strftime('%Y-%m-%d')
        history = self._api_call('GET', f'daily_metrics?date=gte.{week_ago}&date=lt.{target_date}&order=date.desc')
        history = history if isinstance(history, list) else []
        
        return {
            'tasks': tasks,
            'interventions': interventions,
            'activities': activities,
            'history': history,
            'date': target_date
        }
    
    def calculate_features(self, data: Dict) -> Dict[str, float]:
        """Calculate all ML features from raw data"""
        tasks = data['tasks']
        interventions = data['interventions']
        activities = data['activities']
        history = data['history']
        
        # 1. Completion Rate (0-1)
        completed = len([t for t in tasks if t.get('status') == 'COMPLETED'])
        total = len(tasks) if tasks else 1
        completion_rate = completed / total
        
        # 2. Focus Quality Average (0-1, scaled from 1-10)
        focus_scores = [t.get('focus_quality', 5) for t in tasks if t.get('focus_quality')]
        if not focus_scores:
            focus_scores = [a.get('focus_quality', 5) for a in activities if a.get('focus_quality')]
        avg_focus = (sum(focus_scores) / len(focus_scores)) if focus_scores else 5
        focus_quality = (avg_focus - 1) / 9  # Scale 1-10 to 0-1
        
        # 3. Context Switches (inverted - fewer = better)
        context_switches_count = len([a for a in activities if a.get('activity_type') == 'CONTEXT_SWITCH'])
        # Normalize: 0 switches = 1.0, 15+ switches = 0.0
        switch_score = max(0, 1 - (context_switches_count / 15))
        
        # 4. Intervention Response (resolved vs total)
        resolved = len([i for i in interventions if i.get('successful') == True])
        total_interventions = len(interventions) if interventions else 1
        intervention_response = resolved / total_interventions if interventions else 1.0
        
        # 5. Productive Hours Utilization
        now = datetime.now()
        current_hour = now.hour
        # Peak productive hours: 9-12 AM
        if 9 <= current_hour < 12:
            productive_hours = 1.0
        elif 6 <= current_hour < 9 or 14 <= current_hour < 17:
            productive_hours = 0.7
        else:
            productive_hours = 0.5
        
        # 6. Streak Bonus (consecutive good days with score > 70)
        good_days = 0
        for day_metric in history:
            day_score = day_metric.get('productivity_score') or day_metric.get('focus_score', 0)
            if day_score and day_score >= 70:
                good_days += 1
            else:
                break
        streak_bonus = min(good_days / 7, 1.0)  # Max 7-day streak = 1.0
        
        # 7. Abandonment Rate (inverted - lower = better)
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
        """Calculate weighted XGBoost-style focus score"""
        
        raw_score = sum(
            self.WEIGHTS[feature] * features.get(feature, 0)
            for feature in self.WEIGHTS
        )
        
        # Apply sigmoid smoothing for more natural distribution
        smoothed = 1 / (1 + math.exp(-8 * (raw_score - 0.5)))
        
        # Scale to 0-100
        final_score = round(smoothed * 100, 1)
        
        return max(0, min(100, final_score))
    
    def get_grade(self, score: float) -> Dict:
        """Get grade info for a score"""
        for threshold, grade, emoji, label in self.GRADES:
            if score >= threshold:
                return {
                    'grade': grade,
                    'emoji': emoji,
                    'label': label,
                    'threshold': threshold
                }
        return {'grade': 'F', 'emoji': '❌', 'label': 'Critical', 'threshold': 0}
    
    def generate_insights(self, features: Dict[str, float], score: float) -> List[str]:
        """Generate actionable insights based on features"""
        insights = []
        
        if features['completion_rate'] < 0.5:
            insights.append("📋 Low completion rate - try smaller tasks")
        elif features['completion_rate'] >= 0.8:
            insights.append("✅ Excellent task completion!")
        
        if features['context_switches'] < 0.5:
            insights.append("🔄 High context switching - try time-blocking")
        
        if features['focus_quality'] < 0.5:
            insights.append("🧘 Focus quality low - check energy levels")
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
        """Main method: Calculate and store daily focus score"""
        target_date = date or self.today
        
        print(f"🧠 Calculating XGBoost Focus Score for {target_date}...")
        
        # Get data
        data = self.get_todays_data(target_date)
        
        # Calculate features
        features = self.calculate_features(data)
        print(f"📊 Features: {json.dumps(features, indent=2)}")
        
        # Calculate score
        score = self.calculate_score(features)
        grade_info = self.get_grade(score)
        
        print(f"🎯 Score: {score} ({grade_info['grade']} - {grade_info['label']})")
        
        # Generate insights
        insights = self.generate_insights(features, score)
        
        # Build result
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
            'model_version': 'xgboost_v1.1'
        }
        
        # V1.1: Dual-write to both tables for compatibility
        # 1. Write to daily_metrics (primary - always exists)
        metrics_data = {
            'user_id': 1,
            'date': target_date,
            'tasks_completed': result['tasks_completed'],
            'tasks_abandoned': len([t for t in data['tasks'] if t.get('status') == 'ABANDONED']),
            'completion_rate': round(features['completion_rate'], 3),
            'abandonment_rate': round(1 - features['abandonment_rate'], 3),
            'average_focus_quality': round(features['focus_quality'] * 9 + 1, 1),
            'context_switches': int((1 - features['context_switches']) * 15),
            'intervention_count': len(data['interventions']),
            'productivity_score': int(score),  # Store focus score here too
        }
        
        resp = self._api_call('POST', 'daily_metrics', metrics_data, upsert=True)
        if isinstance(resp, list) and resp:
            print(f"✅ Saved to daily_metrics")
        else:
            print(f"⚠️ daily_metrics save: {resp}")
        
        # 2. Try to write to focus_scores (secondary - may not exist)
        focus_data = {
            'date': target_date,
            'user_id': 1,
            'score': score,
            'grade': grade_info['grade'],
            'features': json.dumps(features),
            'insights': json.dumps(insights),
            'tasks_total': len(data['tasks']),
            'tasks_completed': result['tasks_completed'],
            'interventions_count': len(data['interventions']),
            'calculated_at': result['calculated_at'],
            'model_version': 'xgboost_v1.1'
        }
        
        resp = self._api_call('POST', 'focus_scores', focus_data, upsert=True)
        if isinstance(resp, list) and resp:
            print(f"✅ Saved to focus_scores")
        elif isinstance(resp, dict) and 'code' in resp:
            print(f"ℹ️ focus_scores table not available (using daily_metrics)")
        
        return result
    
    def get_latest_score(self) -> Optional[Dict]:
        """Get the most recent focus score from daily_metrics"""
        result = self._api_call('GET', 'daily_metrics?order=date.desc&limit=1')
        if result and isinstance(result, list) and len(result) > 0:
            m = result[0]
            return {
                'date': m.get('date'),
                'score': m.get('productivity_score', 50),
                'grade': self.get_grade(m.get('productivity_score', 50))['grade'],
                'features': {
                    'completion_rate': m.get('completion_rate', 0),
                    'focus_quality': (m.get('average_focus_quality', 5) - 1) / 9,
                    'context_switches': max(0, 1 - m.get('context_switches', 0) / 15),
                },
                'insights': []
            }
        return None
    
    def get_weekly_trend(self) -> List[Dict]:
        """Get last 7 days of scores for trend display"""
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        result = self._api_call('GET', f'daily_metrics?date=gte.{week_ago}&order=date.asc&select=date,productivity_score')
        if isinstance(result, list):
            return [{'date': r['date'], 'score': r.get('productivity_score', 50)} for r in result]
        return []


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":
    import sys
    
    engine = XGBoostFocusScore()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "calculate":
            date = sys.argv[2] if len(sys.argv) > 2 else None
            result = engine.calculate_daily_score(date)
            print(f"\n📊 DAILY FOCUS SCORE")
            print(f"{'='*40}")
            print(f"Date: {result['date']}")
            print(f"Score: {result['score']} {result['grade_emoji']} {result['grade']}")
            print(f"Label: {result['grade_label']}")
            print(f"\nInsights:")
            for insight in result['insights']:
                print(f"  {insight}")
        
        elif command == "latest":
            result = engine.get_latest_score()
            if result:
                print(json.dumps(result, indent=2, default=str))
            else:
                print("No scores found")
        
        elif command == "trend":
            trend = engine.get_weekly_trend()
            print("Weekly Trend:")
            for day in trend:
                print(f"  {day['date']}: {day['score']}")
        
        else:
            print(f"Unknown command: {command}")
    else:
        # Default: calculate today's score
        result = engine.calculate_daily_score()
        print(json.dumps(result, indent=2, default=str))
