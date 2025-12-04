"""
CLAUDE PERFORMANCE SCORE - XGBoost Self-Monitoring
Tracks Claude AI's performance in serving Ariel Shapira's ecosystem
Created by: Ariel Shapira, Solo Founder - Everest Capital USA

Metrics tracked:
- Task completion rate
- First-attempt accuracy (no rework needed)
- Pattern adherence (following established workflows)
- Value delivered (impact score)
- Mistakes requiring correction
- Context retention (remembering past decisions)
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


class ClaudePerformanceScore:
    """XGBoost-inspired Claude Performance Scoring (0-100)"""
    
    # Weighted features for Claude's performance
    WEIGHTS = {
        'task_completion': 0.20,      # Did Claude complete what was asked?
        'first_attempt_accuracy': 0.25,  # Got it right without rework?
        'pattern_adherence': 0.20,    # Followed established workflows?
        'value_delivered': 0.15,      # Impact/usefulness of work
        'context_retention': 0.10,    # Remembered past decisions?
        'efficiency': 0.10,           # Minimal tool calls, direct approach
    }
    
    GRADES = [
        (95, 'A+', '🏆', 'Elite Performance'),
        (90, 'A', '🌟', 'Excellent'),
        (85, 'A-', '⭐', 'Great'),
        (80, 'B+', '💪', 'Very Good'),
        (75, 'B', '👍', 'Good'),
        (70, 'B-', '📈', 'Above Average'),
        (65, 'C+', '🔄', 'Average'),
        (60, 'C', '📊', 'Needs Improvement'),
        (50, 'C-', '⚠️', 'Below Average'),
        (40, 'D', '🔻', 'Poor'),
        (0, 'F', '❌', 'Critical - Review Needed'),
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
    
    def log_task(self, task_type: str, description: str, 
                 completed: bool = True, 
                 first_attempt: bool = True,
                 followed_pattern: bool = True,
                 value_score: int = 7,
                 rework_needed: bool = False,
                 mistake_type: str = None,
                 lesson_learned: str = None) -> dict:
        """Log a Claude task/action for performance tracking"""
        
        task_data = {
            'date': self.today,
            'task_type': task_type,  # 'code', 'deploy', 'analysis', 'document', 'fix'
            'description': description[:500],
            'completed': completed,
            'first_attempt_success': first_attempt,
            'followed_pattern': followed_pattern,
            'value_score': min(10, max(1, value_score)),
            'rework_needed': rework_needed,
            'mistake_type': mistake_type,  # 'overwrite', 'wrong_approach', 'missed_context', 'repeated_error'
            'lesson_learned': lesson_learned,
            'logged_at': datetime.now().isoformat(),
        }
        
        result = self._api_call('POST', 'claude_performance_log', task_data)
        return result
    
    def log_mistake(self, mistake_type: str, description: str, 
                    severity: int = 5, lesson: str = None) -> dict:
        """Log a mistake for pattern tracking"""
        
        mistake_data = {
            'date': self.today,
            'mistake_type': mistake_type,
            'description': description[:500],
            'severity': min(10, max(1, severity)),
            'lesson_learned': lesson,
            'logged_at': datetime.now().isoformat(),
            'pattern_id': f"{mistake_type}_{self.today}",
        }
        
        result = self._api_call('POST', 'claude_mistakes', mistake_data)
        return result
    
    def get_todays_performance(self) -> Dict:
        """Get today's logged tasks and calculate features"""
        
        tasks = self._api_call('GET', f'claude_performance_log?date=eq.{self.today}')
        tasks = tasks if isinstance(tasks, list) else []
        
        mistakes = self._api_call('GET', f'claude_mistakes?date=eq.{self.today}')
        mistakes = mistakes if isinstance(mistakes, list) else []
        
        # Get historical patterns for context retention score
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        history = self._api_call('GET', f'claude_mistakes?date=gte.{week_ago}&order=date.desc')
        history = history if isinstance(history, list) else []
        
        return {
            'tasks': tasks,
            'mistakes': mistakes,
            'history': history,
            'date': self.today
        }
    
    def calculate_features(self, data: Dict) -> Dict[str, float]:
        """Calculate performance features from logged data"""
        
        tasks = data['tasks']
        mistakes = data['mistakes']
        history = data['history']
        
        if not tasks:
            # Default scores when no tasks logged
            return {
                'task_completion': 0.5,
                'first_attempt_accuracy': 0.5,
                'pattern_adherence': 0.5,
                'value_delivered': 0.5,
                'context_retention': 0.5,
                'efficiency': 0.5,
            }
        
        # Task completion rate
        completed = len([t for t in tasks if t.get('completed', False)])
        task_completion = completed / len(tasks) if tasks else 0
        
        # First attempt accuracy
        first_attempts = len([t for t in tasks if t.get('first_attempt_success', False)])
        first_attempt_accuracy = first_attempts / len(tasks) if tasks else 0
        
        # Pattern adherence
        followed = len([t for t in tasks if t.get('followed_pattern', False)])
        pattern_adherence = followed / len(tasks) if tasks else 0
        
        # Value delivered (average value score / 10)
        value_scores = [t.get('value_score', 5) for t in tasks]
        value_delivered = (sum(value_scores) / len(value_scores)) / 10 if value_scores else 0.5
        
        # Context retention - penalize repeated mistakes
        repeated_mistakes = {}
        for m in history:
            mt = m.get('mistake_type', 'unknown')
            repeated_mistakes[mt] = repeated_mistakes.get(mt, 0) + 1
        
        today_repeats = sum(1 for m in mistakes if repeated_mistakes.get(m.get('mistake_type'), 0) > 1)
        context_retention = max(0, 1 - (today_repeats * 0.2))  # -20% per repeated mistake type
        
        # Efficiency - penalize rework
        rework_count = len([t for t in tasks if t.get('rework_needed', False)])
        efficiency = max(0, 1 - (rework_count / max(len(tasks), 1)))
        
        return {
            'task_completion': round(task_completion, 3),
            'first_attempt_accuracy': round(first_attempt_accuracy, 3),
            'pattern_adherence': round(pattern_adherence, 3),
            'value_delivered': round(value_delivered, 3),
            'context_retention': round(context_retention, 3),
            'efficiency': round(efficiency, 3),
        }
    
    def calculate_score(self, features: Dict[str, float]) -> float:
        """Calculate weighted score with sigmoid smoothing"""
        raw_score = sum(self.WEIGHTS[f] * features.get(f, 0) for f in self.WEIGHTS)
        smoothed = 1 / (1 + math.exp(-8 * (raw_score - 0.5)))
        return max(0, min(100, round(smoothed * 100, 1)))
    
    def get_grade(self, score: float) -> Dict:
        for threshold, grade, emoji, label in self.GRADES:
            if score >= threshold:
                return {'grade': grade, 'emoji': emoji, 'label': label}
        return {'grade': 'F', 'emoji': '❌', 'label': 'Critical'}
    
    def generate_insights(self, features: Dict, mistakes: List, history: List) -> List[str]:
        """Generate self-improvement insights"""
        insights = []
        
        if features['first_attempt_accuracy'] < 0.7:
            insights.append("🎯 IMPROVE: Verify approach before executing - too much rework")
        
        if features['pattern_adherence'] < 0.8:
            insights.append("📋 IMPROVE: Check established patterns before acting")
        
        if features['context_retention'] < 0.8:
            insights.append("🧠 IMPROVE: Review past mistakes before similar tasks")
        
        # Check for repeated mistake patterns
        mistake_types = {}
        for m in history:
            mt = m.get('mistake_type', 'unknown')
            mistake_types[mt] = mistake_types.get(mt, 0) + 1
        
        for mt, count in mistake_types.items():
            if count >= 2:
                insights.append(f"⚠️ PATTERN: '{mt}' occurred {count}x this week - needs attention")
        
        if features['first_attempt_accuracy'] >= 0.9:
            insights.append("✅ STRENGTH: High first-attempt accuracy")
        
        if features['pattern_adherence'] >= 0.9:
            insights.append("✅ STRENGTH: Excellent pattern adherence")
        
        return insights
    
    def calculate_daily_score(self) -> Dict:
        """Calculate today's Claude performance score"""
        
        print(f"🤖 Calculating Claude Performance Score for {self.today}...")
        
        data = self.get_todays_performance()
        features = self.calculate_features(data)
        print(f"📊 Features: {json.dumps(features, indent=2)}")
        
        score = self.calculate_score(features)
        grade_info = self.get_grade(score)
        print(f"🎯 Score: {score} ({grade_info['grade']} - {grade_info['label']})")
        
        insights = self.generate_insights(features, data['mistakes'], data['history'])
        
        result = {
            'date': self.today,
            'score': score,
            'grade': grade_info['grade'],
            'grade_emoji': grade_info['emoji'],
            'grade_label': grade_info['label'],
            'features': features,
            'insights': insights,
            'tasks_logged': len(data['tasks']),
            'mistakes_logged': len(data['mistakes']),
            'calculated_at': datetime.now().isoformat(),
        }
        
        # Store score in claude_daily_scores
        score_data = {
            'date': self.today,
            'score': score,
            'grade': grade_info['grade'],
            'features': json.dumps(features),
            'insights': json.dumps(insights),
            'tasks_count': len(data['tasks']),
            'mistakes_count': len(data['mistakes']),
        }
        
        # Upsert score
        existing = self._api_call('GET', f'claude_daily_scores?date=eq.{self.today}')
        if existing and isinstance(existing, list) and len(existing) > 0:
            self._api_call('PATCH', f'claude_daily_scores?id=eq.{existing[0]["id"]}', score_data)
        else:
            self._api_call('POST', 'claude_daily_scores', score_data)
        
        return result
    
    def get_lessons_for_task(self, task_type: str) -> List[str]:
        """Get relevant lessons learned before starting a task"""
        
        # Get mistakes related to this task type
        mistakes = self._api_call('GET', f'claude_mistakes?order=date.desc&limit=20')
        mistakes = mistakes if isinstance(mistakes, list) else []
        
        lessons = []
        for m in mistakes:
            if m.get('lesson_learned'):
                lessons.append({
                    'type': m.get('mistake_type'),
                    'lesson': m.get('lesson_learned'),
                    'date': m.get('date')
                })
        
        return lessons[:5]  # Return top 5 most recent lessons


# Pre-session check function
def get_pre_session_advice() -> str:
    """Get advice before starting work"""
    engine = ClaudePerformanceScore()
    lessons = engine.get_lessons_for_task('any')
    
    advice = "🤖 CLAUDE PRE-SESSION CHECK:\n"
    
    if lessons:
        advice += "\n📋 Recent lessons to remember:\n"
        for l in lessons:
            advice += f"  • [{l['type']}]: {l['lesson']}\n"
    
    # Get yesterday's score
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday_score = engine._api_call('GET', f'claude_daily_scores?date=eq.{yesterday}')
    if yesterday_score and isinstance(yesterday_score, list) and len(yesterday_score) > 0:
        s = yesterday_score[0]
        advice += f"\n📊 Yesterday's score: {s.get('score', 'N/A')}/100 ({s.get('grade', 'N/A')})\n"
    
    return advice


if __name__ == "__main__":
    import sys
    engine = ClaudePerformanceScore()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "calculate":
            result = engine.calculate_daily_score()
            print(f"\n{'='*50}")
            print(f"🤖 CLAUDE PERFORMANCE SCORE")
            print(f"{'='*50}")
            print(f"Date: {result['date']}")
            print(f"Score: {result['score']} {result['grade_emoji']} {result['grade']}")
            print(f"\nInsights:")
            for i in result['insights']:
                print(f"  {i}")
        
        elif cmd == "log_task":
            # Example: python claude_performance_score.py log_task deploy "Deployed XGBoost" true true 9
            if len(sys.argv) >= 5:
                result = engine.log_task(
                    task_type=sys.argv[2],
                    description=sys.argv[3],
                    completed=sys.argv[4].lower() == 'true' if len(sys.argv) > 4 else True,
                    first_attempt=sys.argv[5].lower() == 'true' if len(sys.argv) > 5 else True,
                    value_score=int(sys.argv[6]) if len(sys.argv) > 6 else 7
                )
                print(f"✅ Task logged: {result}")
        
        elif cmd == "log_mistake":
            # Example: python claude_performance_score.py log_mistake overwrite "Overwrote dashboard" 7 "Always add to existing"
            if len(sys.argv) >= 4:
                result = engine.log_mistake(
                    mistake_type=sys.argv[2],
                    description=sys.argv[3],
                    severity=int(sys.argv[4]) if len(sys.argv) > 4 else 5,
                    lesson=sys.argv[5] if len(sys.argv) > 5 else None
                )
                print(f"⚠️ Mistake logged: {result}")
        
        elif cmd == "advice":
            print(get_pre_session_advice())
        
        elif cmd == "lessons":
            lessons = engine.get_lessons_for_task(sys.argv[2] if len(sys.argv) > 2 else 'any')
            print("📚 Lessons learned:")
            for l in lessons:
                print(f"  [{l['type']}]: {l['lesson']}")
    else:
        engine.calculate_daily_score()
