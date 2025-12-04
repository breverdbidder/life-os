"""
Life OS ADHD Monitor
XGBoost-based abandonment prediction and intervention system
"""
import os
import json
import requests
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

# XGBoost feature weights (pre-trained on ADHD patterns)
XGBOOST_WEIGHTS = {
    'complexity': 0.15,
    'clarity_inverse': 0.12,
    'time_overrun_ratio': 0.25,
    'context_switches': 0.18,
    'energy_level_inverse': 0.10,
    'time_of_day_risk': 0.08,  # 2-4 PM = high risk
    'task_count_today': 0.07,
    'recent_abandonment_rate': 0.05
}

class InterventionLevel:
    LEVEL_1 = 1  # 0-30 min: Quick check
    LEVEL_2 = 2  # 30-60 min: Pattern analysis
    LEVEL_3 = 3  # 60+ min: Accountability

INTERVENTION_MESSAGES = {
    1: "📌 Quick check: {task} - still on it?",
    2: "🔄 I notice {task} from earlier. Pattern: {pattern}. Continue or defer?",
    3: "⚠️ ACCOUNTABILITY: {task} started {time} ago. Status? Be honest."
}

MICRO_COMMITMENT_PROMPTS = [
    "Just step 1? {action} That's it.",
    "2 minutes only. Can you do {action}?",
    "One tiny thing: {action}. Nothing more.",
]

class ADHDMonitor:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
        self.supabase_key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE")
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def extract_features(self, task: dict, daily_context: dict = None) -> dict:
        """Extract XGBoost features from task and context"""
        now = datetime.now()
        
        # Task features
        complexity = task.get('complexity', 5) / 10
        clarity_inverse = (10 - task.get('clarity', 5)) / 10
        
        # Time features
        time_overrun_ratio = 0.0
        minutes_elapsed = 0
        if task.get('initiated_at'):
            try:
                started = datetime.fromisoformat(task['initiated_at'].replace('Z', '+00:00').replace('+00:00', ''))
                minutes_elapsed = (now - started).total_seconds() / 60
                estimated = task.get('estimated_minutes', 30)
                time_overrun_ratio = min(minutes_elapsed / max(estimated, 1), 3.0) / 3.0
            except:
                pass
        
        # Time of day risk (2-4 PM = energy dip)
        hour = now.hour
        time_of_day_risk = 0.8 if 14 <= hour <= 16 else (0.3 if 9 <= hour <= 11 else 0.5)
        
        # Context features
        context_switches = daily_context.get('context_switches', 0) / 20 if daily_context else 0
        energy_level_inverse = (10 - daily_context.get('energy_level', 7)) / 10 if daily_context else 0.3
        task_count_today = min(daily_context.get('task_count', 0), 10) / 10 if daily_context else 0
        recent_abandonment_rate = daily_context.get('abandonment_rate', 0.2) if daily_context else 0.2
        
        return {
            'complexity': complexity,
            'clarity_inverse': clarity_inverse,
            'time_overrun_ratio': time_overrun_ratio,
            'context_switches': context_switches,
            'energy_level_inverse': energy_level_inverse,
            'time_of_day_risk': time_of_day_risk,
            'task_count_today': task_count_today,
            'recent_abandonment_rate': recent_abandonment_rate,
            'minutes_elapsed': minutes_elapsed
        }
    
    def predict_abandonment(self, task: dict, daily_context: dict = None) -> Tuple[float, str, dict]:
        """
        XGBoost-style prediction of abandonment probability
        Returns: (probability, risk_level, features)
        """
        features = self.extract_features(task, daily_context)
        
        # Calculate weighted score (simulating XGBoost leaf scores)
        score = sum(
            features.get(feat, 0) * weight 
            for feat, weight in XGBOOST_WEIGHTS.items()
        )
        
        # Apply sigmoid for probability
        probability = 1 / (1 + np.exp(-5 * (score - 0.5)))
        
        # Determine risk level
        if probability >= 0.7:
            risk_level = "HIGH"
        elif probability >= 0.4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"
        
        return probability, risk_level, features
    
    def determine_intervention(self, task: dict, probability: float, 
                               features: dict) -> Optional[dict]:
        """Determine if intervention is needed and what type"""
        minutes_elapsed = features.get('minutes_elapsed', 0)
        status = task.get('status', 'INITIATED')
        
        # Skip if task is completed or already handled
        if status in ['COMPLETED', 'ABANDONED', 'DEFERRED']:
            return None
        
        # Determine intervention level based on time
        if minutes_elapsed >= 60:
            level = InterventionLevel.LEVEL_3
        elif minutes_elapsed >= 30:
            level = InterventionLevel.LEVEL_2
        elif minutes_elapsed >= 15 and probability >= 0.5:
            level = InterventionLevel.LEVEL_1
        else:
            return None  # No intervention needed yet
        
        # Generate intervention
        task_desc = task.get('description', 'your task')[:50]
        
        # Detect patterns
        patterns = []
        if features.get('time_of_day_risk', 0) > 0.6:
            patterns.append("afternoon energy dip")
        if features.get('complexity', 0) > 0.7:
            patterns.append("high complexity")
        if features.get('context_switches', 0) > 0.5:
            patterns.append("frequent context switches")
        
        pattern_str = ", ".join(patterns) if patterns else "task stalling"
        
        # Format time elapsed
        hours = int(minutes_elapsed // 60)
        mins = int(minutes_elapsed % 60)
        time_str = f"{hours}h {mins}m" if hours > 0 else f"{mins} minutes"
        
        message = INTERVENTION_MESSAGES[level].format(
            task=task_desc,
            pattern=pattern_str,
            time=time_str
        )
        
        # Add micro-commitment for high-risk tasks
        if probability >= 0.6 and level >= 2:
            import random
            micro = random.choice(MICRO_COMMITMENT_PROMPTS)
            first_step = self._suggest_first_step(task_desc)
            message += f"\n\n💡 Micro-commitment: {micro.format(action=first_step)}"
        
        return {
            "task_id": task.get('task_id'),
            "task_description": task_desc,
            "intervention_level": level,
            "intervention_type": f"LEVEL_{level}",
            "message": message,
            "abandonment_probability": probability,
            "risk_level": features.get('risk_level', 'MEDIUM'),
            "reasoning": f"Time: {time_str}, Complexity: {task.get('complexity')}/10, Patterns: {pattern_str}",
            "ml_predicted_success": 0.7 - (probability * 0.3),
            "triggered_at": datetime.now().isoformat(),
            "minutes_since_start": minutes_elapsed,
            "domain": task.get('domain'),
            "task_complexity": task.get('complexity')
        }
    
    def _suggest_first_step(self, task_desc: str) -> str:
        """Suggest a micro first step based on task description"""
        task_lower = task_desc.lower()
        
        if any(x in task_lower for x in ['write', 'create', 'draft']):
            return "write just the first sentence"
        elif any(x in task_lower for x in ['review', 'check', 'analyze']):
            return "look at just the first item"
        elif any(x in task_lower for x in ['call', 'email', 'contact']):
            return "open the app/dial the number"
        elif any(x in task_lower for x in ['fix', 'debug', 'solve']):
            return "identify the exact error message"
        elif any(x in task_lower for x in ['build', 'develop', 'code']):
            return "create the empty file/function"
        else:
            return "take the smallest possible first action"
    
    def save_intervention(self, intervention: dict) -> bool:
        """Save intervention to database"""
        intervention['user_id'] = 1  # Ariel
        intervention['timestamp'] = datetime.now().isoformat()
        
        r = requests.post(
            f"{self.supabase_url}/rest/v1/task_interventions",
            headers=self.headers,
            json=intervention,
            verify=False,
            timeout=30
        )
        
        return r.status_code in [200, 201]
    
    def run_monitoring_cycle(self) -> List[dict]:
        """Run a full monitoring cycle on all active tasks"""
        interventions = []
        
        # Get active tasks
        r = requests.get(
            f"{self.supabase_url}/rest/v1/task_states?status=not.in.(COMPLETED,ABANDONED,DEFERRED)&order=initiated_at.asc",
            headers=self.headers,
            verify=False,
            timeout=30
        )
        
        if r.status_code != 200:
            print(f"❌ Failed to get tasks: {r.status_code}")
            return []
        
        tasks = r.json()
        print(f"📊 Monitoring {len(tasks)} active tasks...")
        
        # Get daily context
        daily_context = self._get_daily_context()
        
        for task in tasks:
            probability, risk_level, features = self.predict_abandonment(task, daily_context)
            features['risk_level'] = risk_level
            
            print(f"   • {task.get('description', 'Unknown')[:40]}: {probability:.1%} risk ({risk_level})")
            
            intervention = self.determine_intervention(task, probability, features)
            
            if intervention:
                if self.save_intervention(intervention):
                    interventions.append(intervention)
                    print(f"     ⚠️ Intervention triggered: Level {intervention['intervention_level']}")
        
        return interventions
    
    def _get_daily_context(self) -> dict:
        """Get today's context metrics"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        r = requests.get(
            f"{self.supabase_url}/rest/v1/daily_metrics?date=eq.{today}&limit=1",
            headers=self.headers,
            verify=False,
            timeout=30
        )
        
        if r.status_code == 200 and r.json():
            metrics = r.json()[0]
            return {
                'context_switches': metrics.get('context_switches', 0),
                'energy_level': metrics.get('energy_average', 7),
                'task_count': metrics.get('tasks_completed', 0) + metrics.get('tasks_abandoned', 0),
                'abandonment_rate': metrics.get('abandonment_rate', 0.2)
            }
        
        return {
            'context_switches': 0,
            'energy_level': 7,
            'task_count': 0,
            'abandonment_rate': 0.2
        }

if __name__ == "__main__":
    monitor = ADHDMonitor()
    interventions = monitor.run_monitoring_cycle()
    print(f"\n✅ Generated {len(interventions)} interventions")
