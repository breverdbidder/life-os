"""
LIFE OS ENGINE v1.0
Real-time focus-optimized task tracking with XGBoost predictions
Created by: Ariel Shapira, Solo Founder - Everest Capital USA
"""

import json
import requests
import urllib3
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
from enum import Enum
import math

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

# ============================================================
# ENUMS & DATA CLASSES
# ============================================================

class TaskStatus(Enum):
    INITIATED = "INITIATED"
    SOLUTION_PROVIDED = "SOLUTION_PROVIDED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"
    BLOCKED = "BLOCKED"
    DEFERRED = "DEFERRED"

class Domain(Enum):
    ARIEL = "ARIEL"
    MICHAEL = "MICHAEL"
    FAMILY = "FAMILY"
    BUSINESS = "BUSINESS"

class InterventionLevel(Enum):
    LEVEL_1 = 1  # 0-30 min: Quick check
    LEVEL_2 = 2  # 30-60 min: Pattern analysis
    LEVEL_3 = 3  # 60+ min: Accountability

@dataclass
class Task:
    task_id: str
    description: str
    domain: str
    complexity: int  # 1-10
    clarity: int     # 1-10
    estimated_minutes: int
    status: str = "INITIATED"
    initiated_at: str = None
    solution_provided_at: str = None
    in_progress_at: str = None
    completed_at: str = None
    abandoned_at: str = None
    abandonment_probability: float = 0.0
    intervention_level: int = 0
    artifacts_created: List[str] = None

@dataclass
class DailyMetrics:
    date: str
    tasks_completed: int = 0
    tasks_abandoned: int = 0
    tasks_in_progress: int = 0
    total_active_minutes: int = 0
    average_focus_quality: float = 0.0
    context_switches: int = 0
    completion_rate: float = 0.0
    abandonment_rate: float = 0.0
    intervention_count: int = 0
    productivity_score: float = 0.0
    peak_focus_hours: List[int] = None
    domains: Dict[str, int] = None

# ============================================================
# XGBOOST-STYLE FOCUS PREDICTOR
# ============================================================

class FocusPredictor:
    """
    XGBoost-inspired focus predictor
    - Predicts task abandonment probability (real-time)
    - Calculates Daily Focus Score (0-100 scale)
    """
    
    # Feature weights for abandonment prediction
    WEIGHTS = {
        'time_elapsed_ratio': 0.35,      # time_elapsed / estimated_time
        'complexity_score': 0.20,         # Higher complexity = higher risk
        'context_switches': 0.15,         # More switches = higher risk
        'time_of_day': 0.10,              # Afternoon dip = higher risk
        'energy_level': 0.10,             # Lower energy = higher risk
        'historical_completion': 0.10     # Past performance
    }
    
    # Daily Score feature weights (XGBoost-style)
    DAILY_SCORE_WEIGHTS = {
        'completion_rate': 0.25,          # Tasks completed vs total
        'focus_quality': 0.20,            # Average focus quality
        'complexity_handled': 0.15,       # Avg complexity of completed tasks
        'context_discipline': 0.15,       # Fewer switches = better
        'time_efficiency': 0.10,          # Actual vs estimated time
        'streak_bonus': 0.10,             # Consecutive productive days
        'intervention_penalty': 0.05      # Fewer interventions = better
    }
    
    # Time of day risk factors (focus energy patterns)
    TIME_RISK = {
        range(6, 9): 0.3,    # Early morning - moderate
        range(9, 12): 0.1,   # Peak focus - low risk
        range(12, 14): 0.5,  # Post-lunch dip - high risk
        range(14, 17): 0.6,  # Afternoon slump - highest risk
        range(17, 20): 0.3,  # Evening recovery - moderate
        range(20, 24): 0.4,  # Night - moderate-high
        range(0, 6): 0.5     # Late night - high risk
    }
    
    @classmethod
    def predict_abandonment(cls, 
                           minutes_elapsed: int,
                           estimated_minutes: int,
                           complexity: int,
                           context_switches: int = 0,
                           energy_level: int = 5,
                           historical_completion_rate: float = 0.7) -> Dict:
        """
        Predict probability of task abandonment
        Returns: {probability, risk_level, reasoning, recommended_intervention}
        """
        
        # Calculate feature scores (0-1 scale)
        
        # 1. Time elapsed ratio
        time_ratio = min(minutes_elapsed / max(estimated_minutes, 1), 3.0)
        time_score = min(time_ratio * 0.4, 1.0)
        
        # 2. Complexity score (1-10 -> 0-1)
        complexity_score = (complexity - 1) / 9
        
        # 3. Context switch penalty
        switch_score = min(context_switches * 0.15, 1.0)
        
        # 4. Time of day risk
        current_hour = datetime.now().hour
        time_risk = 0.3
        for hour_range, risk in cls.TIME_RISK.items():
            if current_hour in hour_range:
                time_risk = risk
                break
        
        # 5. Energy level (1-10 -> inverted 0-1)
        energy_score = 1 - ((energy_level - 1) / 9)
        
        # 6. Historical performance (inverted - lower completion = higher risk)
        history_score = 1 - historical_completion_rate
        
        # Calculate weighted probability
        probability = (
            cls.WEIGHTS['time_elapsed_ratio'] * time_score +
            cls.WEIGHTS['complexity_score'] * complexity_score +
            cls.WEIGHTS['context_switches'] * switch_score +
            cls.WEIGHTS['time_of_day'] * time_risk +
            cls.WEIGHTS['energy_level'] * energy_score +
            cls.WEIGHTS['historical_completion'] * history_score
        )
        
        # Apply sigmoid-like smoothing
        probability = 1 / (1 + math.exp(-5 * (probability - 0.5)))
        probability = round(probability, 3)
        
        # Determine risk level and intervention
        if probability < 0.3:
            risk_level = "LOW"
            intervention = None
        elif probability < 0.5:
            risk_level = "MEDIUM"
            intervention = InterventionLevel.LEVEL_1
        elif probability < 0.7:
            risk_level = "HIGH"
            intervention = InterventionLevel.LEVEL_2
        else:
            risk_level = "CRITICAL"
            intervention = InterventionLevel.LEVEL_3
        
        # Generate reasoning
        reasons = []
        if time_score > 0.5:
            reasons.append(f"Task running {int(time_ratio * 100)}% of estimated time")
        if complexity_score > 0.6:
            reasons.append(f"High complexity ({complexity}/10)")
        if switch_score > 0.3:
            reasons.append(f"{context_switches} context switches detected")
        if time_risk > 0.4:
            reasons.append("Current time is in low-focus window")
        if energy_score > 0.5:
            reasons.append(f"Low energy level ({energy_level}/10)")
        
        return {
            'probability': probability,
            'risk_level': risk_level,
            'intervention_level': intervention.value if intervention else 0,
            'reasoning': reasons,
            'feature_scores': {
                'time_elapsed': round(time_score, 2),
                'complexity': round(complexity_score, 2),
                'context_switches': round(switch_score, 2),
                'time_of_day': round(time_risk, 2),
                'energy': round(energy_score, 2),
                'history': round(history_score, 2)
            }
        }
    
    @classmethod
    def calculate_daily_focus_score(cls,
                                    tasks_completed: int,
                                    tasks_abandoned: int,
                                    tasks_total: int,
                                    avg_focus_quality: float,
                                    avg_complexity_completed: float,
                                    context_switches: int,
                                    time_efficiency: float,
                                    consecutive_productive_days: int,
                                    interventions_triggered: int) -> Dict:
        """
        Calculate XGBoost-style Daily Focus Score (0-100)
        
        Returns: {
            score: int (0-100),
            grade: str (A+, A, B+, B, C+, C, D, F),
            feature_breakdown: dict,
            insights: list,
            trend: str (improving, stable, declining)
        }
        """
        
        # 1. Completion Rate Score (0-1)
        if tasks_total > 0:
            completion_rate = tasks_completed / tasks_total
        else:
            completion_rate = 0.5  # Neutral if no tasks
        
        # 2. Focus Quality Score (0-1) - input is 0-10
        focus_score = min(avg_focus_quality / 10, 1.0) if avg_focus_quality else 0.5
        
        # 3. Complexity Handled Score (0-1) - reward handling harder tasks
        complexity_score = min(avg_complexity_completed / 10, 1.0) if avg_complexity_completed else 0.5
        
        # 4. Context Discipline Score (0-1) - fewer switches = better
        # Baseline: 5 switches is acceptable, 0 is perfect, 15+ is bad
        switch_penalty = min(context_switches / 15, 1.0)
        discipline_score = 1 - switch_penalty
        
        # 5. Time Efficiency Score (0-1) - actual vs estimated
        # 1.0 = on time, <1 = faster (bonus), >1 = slower (penalty)
        if time_efficiency > 0:
            efficiency_score = min(1 / time_efficiency, 1.2)  # Cap bonus at 20%
            efficiency_score = max(efficiency_score, 0.3)      # Floor at 30%
        else:
            efficiency_score = 0.5
        
        # 6. Streak Bonus (0-1) - consecutive productive days
        # 0 days = 0, 7+ days = 1.0
        streak_score = min(consecutive_productive_days / 7, 1.0)
        
        # 7. Intervention Penalty (0-1) - fewer = better
        # 0 interventions = 1.0, 5+ = 0
        intervention_score = max(1 - (interventions_triggered / 5), 0)
        
        # Calculate weighted score
        raw_score = (
            cls.DAILY_SCORE_WEIGHTS['completion_rate'] * completion_rate +
            cls.DAILY_SCORE_WEIGHTS['focus_quality'] * focus_score +
            cls.DAILY_SCORE_WEIGHTS['complexity_handled'] * complexity_score +
            cls.DAILY_SCORE_WEIGHTS['context_discipline'] * discipline_score +
            cls.DAILY_SCORE_WEIGHTS['time_efficiency'] * efficiency_score +
            cls.DAILY_SCORE_WEIGHTS['streak_bonus'] * streak_score +
            cls.DAILY_SCORE_WEIGHTS['intervention_penalty'] * intervention_score
        )
        
        # Scale to 0-100
        final_score = int(round(raw_score * 100))
        final_score = max(0, min(100, final_score))
        
        # Determine grade
        if final_score >= 95:
            grade = "A+"
        elif final_score >= 90:
            grade = "A"
        elif final_score >= 85:
            grade = "A-"
        elif final_score >= 80:
            grade = "B+"
        elif final_score >= 75:
            grade = "B"
        elif final_score >= 70:
            grade = "B-"
        elif final_score >= 65:
            grade = "C+"
        elif final_score >= 60:
            grade = "C"
        elif final_score >= 55:
            grade = "C-"
        elif final_score >= 50:
            grade = "D"
        else:
            grade = "F"
        
        # Generate insights
        insights = []
        if completion_rate >= 0.8:
            insights.append("🎯 Excellent task completion rate!")
        elif completion_rate < 0.5:
            insights.append("⚠️ Consider breaking tasks into smaller chunks")
        
        if discipline_score >= 0.8:
            insights.append("🧘 Great focus discipline - minimal context switching")
        elif discipline_score < 0.5:
            insights.append("🔄 High context switching detected - try time blocking")
        
        if streak_score >= 0.7:
            insights.append(f"🔥 {consecutive_productive_days}-day productivity streak!")
        
        if intervention_score < 0.5:
            insights.append("📍 Multiple interventions needed - energy management opportunity")
        
        if efficiency_score > 1:
            insights.append("⚡ Beating time estimates - great efficiency!")
        
        return {
            'score': final_score,
            'grade': grade,
            'feature_breakdown': {
                'completion_rate': round(completion_rate * 100, 1),
                'focus_quality': round(focus_score * 100, 1),
                'complexity_handled': round(complexity_score * 100, 1),
                'context_discipline': round(discipline_score * 100, 1),
                'time_efficiency': round(efficiency_score * 100, 1),
                'streak_bonus': round(streak_score * 100, 1),
                'intervention_penalty': round(intervention_score * 100, 1)
            },
            'insights': insights,
            'raw_score': round(raw_score, 4)
        }


# ============================================================
# INTERVENTION GENERATOR
# ============================================================

class InterventionGenerator:
    """Generates focus-appropriate interventions based on risk level"""
    
    MESSAGES = {
        1: [
            "📌 Quick check: {task} - still on it?",
            "🔔 Hey, {task} is waiting. Need a nudge?",
            "⏱️ 30 min mark on {task}. How's it going?"
        ],
        2: [
            "🔄 I notice {task} from {minutes}m ago. Pattern detected: {pattern}. Continue or defer?",
            "⚠️ {task} at risk. This is attempt #{attempt}. Try micro-commitment: just 2 minutes?",
            "🎯 Focus check: {task} stalled at {minutes}m. Break it down - what's the ONE next action?"
        ],
        3: [
            "⚠️ ACCOUNTABILITY: {task} started {minutes}m ago. Status? Be honest.",
            "🚨 Critical: {task} at {probability}% abandonment risk. Decision time: COMPLETE, DEFER, or ABANDON?",
            "💪 Real talk: {task} needs closure. 3 options: (1) 5-min sprint (2) Schedule for tomorrow (3) Delete it"
        ]
    }
    
    MICRO_COMMITS = [
        "Just open the file/app",
        "Write ONE sentence",
        "Set a 5-minute timer",
        "Tell me what's blocking you",
        "Do the easiest part first"
    ]
    
    @classmethod
    def generate(cls, level: int, task_desc: str, minutes_elapsed: int, 
                 probability: float = 0, pattern: str = "context switching") -> Dict:
        """Generate intervention message and strategy"""
        
        import random
        
        messages = cls.MESSAGES.get(level, cls.MESSAGES[1])
        message = random.choice(messages).format(
            task=task_desc[:50],
            minutes=minutes_elapsed,
            pattern=pattern,
            attempt=random.randint(1, 3),
            probability=int(probability * 100)
        )
        
        strategy = {
            1: "gentle_reminder",
            2: "micro_commitment", 
            3: "accountability_decision"
        }.get(level, "gentle_reminder")
        
        return {
            'level': level,
            'message': message,
            'strategy': strategy,
            'micro_commit': random.choice(cls.MICRO_COMMITS) if level >= 2 else None,
            'generated_at': datetime.now().isoformat()
        }


# ============================================================
# LIFE OS ENGINE
# ============================================================

class LifeOSEngine:
    """Main engine for Life OS task tracking and focus management"""
    
    def __init__(self):
        self.predictor = FocusPredictor()
        self.intervention_gen = InterventionGenerator()
    
    def _api_call(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make Supabase API call"""
        url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
        
        try:
            if method == "GET":
                r = requests.get(url, headers=HEADERS, verify=False, timeout=30)
            elif method == "POST":
                r = requests.post(url, headers=HEADERS, json=data, verify=False, timeout=30)
            elif method == "PATCH":
                r = requests.patch(url, headers=HEADERS, json=data, verify=False, timeout=30)
            
            if r.status_code in [200, 201, 204]:
                return r.json() if r.text else {}
            else:
                return {'error': r.status_code, 'message': r.text[:200]}
        except Exception as e:
            return {'error': str(e)}
    
    # -------------------- TASK MANAGEMENT --------------------
    
    def create_task(self, description: str, domain: str, complexity: int = 5,
                    clarity: int = 7, estimated_minutes: int = 30) -> Dict:
        """Create and track a new task"""
        
        now = datetime.now().isoformat()
        task_id = f"task_{int(datetime.now().timestamp())}"
        
        task_data = {
            'task_id': task_id,
            'description': description,
            'domain': domain,
            'complexity': complexity,
            'clarity': clarity,
            'estimated_minutes': estimated_minutes,
            'status': 'INITIATED',
            'initiated_at': now,
            'updated_at': now
        }
        
        result = self._api_call('POST', 'task_states', task_data)
        
        # Log activity
        self._log_activity('TASK_CREATED', domain, description, {
            'task_id': task_id,
            'complexity': complexity,
            'estimated_minutes': estimated_minutes
        })
        
        return {'task_id': task_id, 'status': 'INITIATED', 'data': result}
    
    def update_task_status(self, task_id: str, new_status: str, notes: str = None) -> Dict:
        """Update task status with timestamp"""
        
        now = datetime.now().isoformat()
        status_field = {
            'SOLUTION_PROVIDED': 'solution_provided_at',
            'IN_PROGRESS': 'in_progress_at',
            'COMPLETED': 'completed_at',
            'ABANDONED': 'abandoned_at',
            'BLOCKED': 'blocked_at',
            'DEFERRED': 'deferred_at'
        }.get(new_status)
        
        update_data = {
            'status': new_status,
            'updated_at': now
        }
        if status_field:
            update_data[status_field] = now
        
        result = self._api_call('PATCH', f'task_states?task_id=eq.{task_id}', update_data)
        
        return {'task_id': task_id, 'new_status': new_status, 'timestamp': now}
    
    def get_active_tasks(self) -> List[Dict]:
        """Get all active (non-completed) tasks"""
        
        result = self._api_call('GET', 
            'task_states?status=not.in.(COMPLETED,ABANDONED)&order=initiated_at.desc')
        
        return result if isinstance(result, list) else []
    
    # -------------------- FOCUS MONITORING --------------------
    
    def check_tasks_for_intervention(self) -> List[Dict]:
        """Check all active tasks and generate interventions if needed"""
        
        active_tasks = self.get_active_tasks()
        interventions = []
        
        for task in active_tasks:
            initiated = datetime.fromisoformat(task['initiated_at'].replace('Z', '+00:00'))
            minutes_elapsed = (datetime.now(initiated.tzinfo) - initiated).total_seconds() / 60
            
            # Get prediction
            prediction = self.predictor.predict_abandonment(
                minutes_elapsed=int(minutes_elapsed),
                estimated_minutes=task.get('estimated_minutes', 30),
                complexity=task.get('complexity', 5),
                context_switches=0,  # Would come from activity tracking
                energy_level=5       # Would come from health logs
            )
            
            # Generate intervention if needed
            if prediction['intervention_level'] > 0:
                intervention = self.intervention_gen.generate(
                    level=prediction['intervention_level'],
                    task_desc=task['description'],
                    minutes_elapsed=int(minutes_elapsed),
                    probability=prediction['probability']
                )
                
                # Log intervention
                intervention_data = {
                    'task_id': task['task_id'],
                    'task_description': task['description'][:100],
                    'intervention_level': prediction['intervention_level'],
                    'intervention_type': intervention['strategy'],
                    'message': intervention['message'],
                    'abandonment_probability': prediction['probability'],
                    'risk_level': prediction['risk_level'],
                    'reasoning': json.dumps(prediction['reasoning']),
                    'minutes_since_start': int(minutes_elapsed),
                    'task_complexity': task.get('complexity', 5),
                    'domain': task.get('domain', 'ARIEL'),
                    'triggered_at': datetime.now().isoformat()
                }
                
                self._api_call('POST', 'task_interventions', intervention_data)
                
                interventions.append({
                    'task': task['description'],
                    'intervention': intervention,
                    'prediction': prediction
                })
        
        return interventions
    
    # -------------------- DAILY METRICS --------------------
    
    def calculate_daily_metrics(self, date: str = None) -> Dict:
        """Calculate and store daily metrics"""
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Get today's tasks
        tasks = self._api_call('GET', f'task_states?initiated_at=gte.{date}T00:00:00')
        tasks = tasks if isinstance(tasks, list) else []
        
        # Get today's interventions
        interventions = self._api_call('GET', f'task_interventions?triggered_at=gte.{date}T00:00:00')
        interventions = interventions if isinstance(interventions, list) else []
        
        # Get today's activities
        activities = self._api_call('GET', f'activities?start_time=gte.{date}T00:00:00')
        activities = activities if isinstance(activities, list) else []
        
        # Calculate metrics
        completed = len([t for t in tasks if t.get('status') == 'COMPLETED'])
        abandoned = len([t for t in tasks if t.get('status') == 'ABANDONED'])
        in_progress = len([t for t in tasks if t.get('status') in ['INITIATED', 'IN_PROGRESS', 'SOLUTION_PROVIDED']])
        total = completed + abandoned + in_progress
        
        # Domain breakdown
        domains = {}
        for t in tasks:
            d = t.get('domain', 'OTHER')
            domains[d] = domains.get(d, 0) + 1
        
        # Focus quality from activities
        focus_scores = [a.get('focus_quality', 0) for a in activities if a.get('focus_quality')]
        avg_focus = sum(focus_scores) / len(focus_scores) if focus_scores else 5.0  # Default to 5
        
        # Context switches
        context_switches = sum(a.get('context_switches', 0) for a in activities)
        
        # Active minutes
        total_minutes = sum(a.get('duration_minutes', 0) for a in activities)
        
        # Calculate average complexity of completed tasks
        completed_tasks = [t for t in tasks if t.get('status') == 'COMPLETED']
        avg_complexity = sum(t.get('complexity', 5) for t in completed_tasks) / len(completed_tasks) if completed_tasks else 5
        
        # Calculate time efficiency (actual / estimated)
        time_efficiency = 1.0
        if completed_tasks:
            total_estimated = sum(t.get('estimated_minutes', 30) for t in completed_tasks)
            total_actual = sum(t.get('actual_minutes', t.get('estimated_minutes', 30)) for t in completed_tasks)
            time_efficiency = total_actual / total_estimated if total_estimated > 0 else 1.0
        
        # Get streak (consecutive days with completion_rate > 0.5)
        streak = self._calculate_productivity_streak(date)
        
        # Calculate XGBoost Focus Score
        focus_score_result = FocusPredictor.calculate_daily_focus_score(
            tasks_completed=completed,
            tasks_abandoned=abandoned,
            tasks_total=total,
            avg_focus_quality=avg_focus,
            avg_complexity_completed=avg_complexity,
            context_switches=context_switches,
            time_efficiency=time_efficiency,
            consecutive_productive_days=streak,
            interventions_triggered=len(interventions)
        )
        
        metrics = {
            'date': date,
            'user_id': 1,
            'tasks_completed': completed,
            'tasks_abandoned': abandoned,
            'completion_rate': round(completed / total, 2) if total > 0 else 0,
            'abandonment_rate': round(abandoned / total, 2) if total > 0 else 0,
            'total_active_minutes': total_minutes,
            'average_focus_quality': round(avg_focus, 1),
            'context_switches': context_switches,
            'intervention_count': len(interventions),
            'domains': json.dumps(domains),
            'productivity_score': round((completed * 10 + avg_focus * 5 - abandoned * 5 - context_switches) / 10, 1),
            'xgboost_focus_score': focus_score_result['score'],
            'focus_grade': focus_score_result['grade'],
            'focus_breakdown': json.dumps(focus_score_result['feature_breakdown']),
            'focus_insights': json.dumps(focus_score_result['insights']),
            'productivity_streak': streak,
            'created_at': datetime.now().isoformat()
        }
        
        # Upsert to daily_metrics
        self._api_call('POST', 'daily_metrics', metrics)
        
        return metrics
    
    def _calculate_productivity_streak(self, current_date: str) -> int:
        """Calculate consecutive productive days (completion_rate > 0.5)"""
        streak = 0
        check_date = datetime.strptime(current_date, '%Y-%m-%d')
        
        for i in range(30):  # Check up to 30 days back
            prev_date = (check_date - timedelta(days=i+1)).strftime('%Y-%m-%d')
            prev_metrics = self._api_call('GET', f'daily_metrics?date=eq.{prev_date}')
            
            if prev_metrics and isinstance(prev_metrics, list) and len(prev_metrics) > 0:
                if prev_metrics[0].get('completion_rate', 0) >= 0.5:
                    streak += 1
                else:
                    break
            else:
                break
        
        return streak
    
    # -------------------- ACTIVITY LOGGING --------------------
    
    def _log_activity(self, activity_type: str, domain: str, description: str, metadata: dict = None) -> Dict:
        """Log an activity"""
        
        activity = {
            'user_id': 1,
            'activity_type': activity_type,
            'domain': domain,
            'platform': 'life_os_engine',
            'start_time': datetime.now().isoformat(),
            'notes': json.dumps({
                'description': description,
                **(metadata or {})
            }),
            'timezone': 'America/New_York'
        }
        
        return self._api_call('POST', 'activities', activity)
    
    def log_context_switch(self, from_task: str, to_task: str) -> Dict:
        """Log a context switch between tasks"""
        
        return self._log_activity('CONTEXT_SWITCH', 'ARIEL', f"{from_task} -> {to_task}", {
            'from_task': from_task,
            'to_task': to_task,
            'switch_time': datetime.now().isoformat()
        })
    
    # -------------------- REPORTS --------------------
    
    def generate_daily_report(self, date: str = None) -> Dict:
        """Generate comprehensive daily report"""
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # Get metrics
        metrics = self.calculate_daily_metrics(date)
        
        # Get all tasks for the day
        tasks = self._api_call('GET', f'task_states?initiated_at=gte.{date}T00:00:00&order=initiated_at.asc')
        tasks = tasks if isinstance(tasks, list) else []
        
        # Get interventions
        interventions = self._api_call('GET', f'task_interventions?triggered_at=gte.{date}T00:00:00')
        interventions = interventions if isinstance(interventions, list) else []
        
        # Build timeline
        timeline = []
        for t in tasks:
            timeline.append({
                'time': t.get('initiated_at', '')[:19],
                'event': 'TASK_STARTED',
                'description': t.get('description', '')[:50],
                'status': t.get('status'),
                'domain': t.get('domain')
            })
        
        for i in interventions:
            timeline.append({
                'time': i.get('triggered_at', '')[:19],
                'event': f"INTERVENTION_L{i.get('intervention_level', 1)}",
                'description': i.get('message', '')[:50],
                'risk': i.get('risk_level')
            })
        
        # Sort by time
        timeline.sort(key=lambda x: x['time'])
        
        # Generate insights
        insights = []
        if metrics.get('abandonment_rate', 0) > 0.3:
            insights.append("⚠️ High abandonment rate today. Consider smaller task chunks.")
        if metrics.get('context_switches', 0) > 10:
            insights.append("🔄 Many context switches. Try time-blocking tomorrow.")
        if metrics.get('average_focus_quality', 0) < 5:
            insights.append("📉 Low focus quality. Check sleep and energy levels.")
        if metrics.get('tasks_completed', 0) >= 5:
            insights.append("🎉 Great productivity! 5+ tasks completed.")
        
        report = {
            'date': date,
            'summary': {
                'tasks_completed': metrics.get('tasks_completed', 0),
                'tasks_abandoned': metrics.get('tasks_abandoned', 0),
                'completion_rate': f"{metrics.get('completion_rate', 0) * 100:.0f}%",
                'productivity_score': metrics.get('productivity_score', 0),
                'focus_quality': metrics.get('average_focus_quality', 0),
                'interventions_triggered': len(interventions)
            },
            'domains': json.loads(metrics.get('domains', '{}')),
            'timeline': timeline,
            'insights': insights,
            'generated_at': datetime.now().isoformat()
        }
        
        # Store report
        self._log_activity('DAILY_REPORT', 'ARIEL', f"Daily report for {date}", report)
        
        return report


# ============================================================
# CLI / MAIN
# ============================================================

if __name__ == "__main__":
    import sys
    
    engine = LifeOSEngine()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "check":
            print("🔍 Checking tasks for interventions...")
            interventions = engine.check_tasks_for_intervention()
            print(f"Found {len(interventions)} tasks needing intervention")
            for i in interventions:
                print(f"\n{i['intervention']['message']}")
        
        elif command == "metrics":
            print("📊 Calculating daily metrics...")
            metrics = engine.calculate_daily_metrics()
            print(json.dumps(metrics, indent=2))
        
        elif command == "report":
            print("📝 Generating daily report...")
            report = engine.generate_daily_report()
            print(json.dumps(report, indent=2))
        
        else:
            print(f"Unknown command: {command}")
    else:
        print("Life OS Engine v1.0")
        print("Commands: check, metrics, report")
