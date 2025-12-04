"""
Life OS Task Tracker
Tracks all tasks with timestamps, states, and ADHD metrics
"""
import os
import json
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional, List
from enum import Enum

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
    artifacts_created: List[str] = None
    
class LifeOSTaskTracker:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
        self.supabase_key = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE")
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def create_task(self, description: str, domain: str, complexity: int = 5, 
                    clarity: int = 5, estimated_minutes: int = 30) -> dict:
        """Create and track a new task"""
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(description) % 10000}"
        now = datetime.now().isoformat()
        
        task_data = {
            "session_id": self.session_id,
            "task_id": task_id,
            "description": description,
            "domain": domain,
            "complexity": complexity,
            "clarity": clarity,
            "estimated_minutes": estimated_minutes,
            "status": "INITIATED",
            "initiated_at": now,
            "updated_at": now
        }
        
        r = requests.post(
            f"{self.supabase_url}/rest/v1/task_states",
            headers=self.headers,
            json=task_data,
            verify=False,
            timeout=30
        )
        
        if r.status_code in [200, 201]:
            print(f"✅ Task created: {task_id}")
            return r.json()[0] if r.json() else task_data
        else:
            print(f"❌ Failed to create task: {r.status_code}")
            return None
    
    def update_task_status(self, task_id: str, new_status: str, 
                          artifacts: List[str] = None) -> dict:
        """Update task status with timestamp"""
        now = datetime.now().isoformat()
        
        status_field_map = {
            "SOLUTION_PROVIDED": "solution_provided_at",
            "IN_PROGRESS": "in_progress_at",
            "COMPLETED": "completed_at",
            "ABANDONED": "abandoned_at",
            "BLOCKED": "blocked_at",
            "DEFERRED": "deferred_at"
        }
        
        update_data = {
            "status": new_status,
            "updated_at": now
        }
        
        if new_status in status_field_map:
            update_data[status_field_map[new_status]] = now
        
        if artifacts:
            update_data["artifacts_created"] = json.dumps(artifacts)
        
        r = requests.patch(
            f"{self.supabase_url}/rest/v1/task_states?task_id=eq.{task_id}",
            headers=self.headers,
            json=update_data,
            verify=False,
            timeout=30
        )
        
        return r.json() if r.status_code in [200, 204] else None
    
    def get_active_tasks(self) -> List[dict]:
        """Get all non-completed tasks"""
        r = requests.get(
            f"{self.supabase_url}/rest/v1/task_states?status=not.in.(COMPLETED,ABANDONED)&order=initiated_at.desc",
            headers=self.headers,
            verify=False,
            timeout=30
        )
        return r.json() if r.status_code == 200 else []
    
    def get_today_tasks(self) -> List[dict]:
        """Get all tasks from today"""
        today = datetime.now().strftime("%Y-%m-%d")
        r = requests.get(
            f"{self.supabase_url}/rest/v1/task_states?initiated_at=gte.{today}T00:00:00&order=initiated_at.desc",
            headers=self.headers,
            verify=False,
            timeout=30
        )
        return r.json() if r.status_code == 200 else []
    
    def calculate_abandonment_risk(self, task: dict) -> float:
        """Calculate abandonment probability based on task metrics"""
        # Simple heuristic model (will be replaced by XGBoost)
        risk = 0.0
        
        # Higher complexity = higher risk
        complexity = task.get('complexity', 5)
        risk += (complexity / 10) * 0.3
        
        # Lower clarity = higher risk
        clarity = task.get('clarity', 5)
        risk += ((10 - clarity) / 10) * 0.2
        
        # Time since start
        if task.get('initiated_at'):
            started = datetime.fromisoformat(task['initiated_at'].replace('Z', '+00:00'))
            minutes_elapsed = (datetime.now(started.tzinfo) - started).total_seconds() / 60
            estimated = task.get('estimated_minutes', 30)
            
            if minutes_elapsed > estimated * 1.5:
                risk += 0.3
            elif minutes_elapsed > estimated:
                risk += 0.2
        
        # Status-based risk
        status = task.get('status', 'INITIATED')
        if status == 'INITIATED':
            risk += 0.1  # Never started = risk
        elif status == 'SOLUTION_PROVIDED':
            risk += 0.15  # Solution given but not acting
        
        return min(risk, 1.0)

if __name__ == "__main__":
    tracker = LifeOSTaskTracker()
    
    # Test task creation
    task = tracker.create_task(
        description="Test task from Life OS engine",
        domain="ARIEL",
        complexity=5,
        clarity=8,
        estimated_minutes=15
    )
    print(f"Created: {task}")
