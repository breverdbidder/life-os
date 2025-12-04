#!/usr/bin/env python3
"""
LIFE OS - Claude Session Logger V1.0
Created by: Ariel Shapira, Solo Founder - Everest Capital USA

This script is called by Claude at the START of every conversation to:
1. Log new session to Supabase
2. Check for active tasks from previous sessions
3. Provide context to Claude about ongoing work

Claude should call these functions during conversations:
- log_task() - When user mentions a new task
- complete_task() - When task is done
- log_context_switch() - When user changes topic mid-task
- log_insight() - When learning something valuable
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, List, Dict

# Supabase Configuration
SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

class ClaudeSessionLogger:
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.active_tasks = []
        self.context_switches = 0
        
    def start_session(self) -> Dict:
        """Call at START of every Claude conversation"""
        now = datetime.now().isoformat()
        
        # Log session start
        session_data = {
            "user_id": 1,
            "activity_type": "CLAUDE_SESSION",
            "platform": "claude_ai",
            "start_time": now,
            "notes": json.dumps({
                "session_id": self.session_id,
                "model": "opus-4.5",
                "status": "active"
            })
        }
        
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/activities",
            headers=HEADERS, json=session_data, verify=False, timeout=30
        )
        
        # Get active tasks from previous sessions
        active = self._get_active_tasks()
        open_interventions = self._get_open_interventions()
        
        return {
            "session_id": self.session_id,
            "started_at": now,
            "active_tasks": active,
            "open_interventions": open_interventions,
            "message": f"Session {self.session_id} started. {len(active)} active tasks, {len(open_interventions)} open interventions."
        }
    
    def _get_active_tasks(self) -> List[Dict]:
        """Get non-completed tasks"""
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/task_states?status=not.in.(COMPLETED,ABANDONED,DEFERRED)&order=initiated_at.desc&limit=10",
            headers=HEADERS, verify=False, timeout=30
        )
        return r.json() if r.status_code == 200 else []
    
    def _get_open_interventions(self) -> List[Dict]:
        """Get unresolved interventions"""
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/task_interventions?successful=is.null&order=triggered_at.desc&limit=5",
            headers=HEADERS, verify=False, timeout=30
        )
        return r.json() if r.status_code == 200 else []
    
    def log_task(self, description: str, domain: str = "BUSINESS", 
                 complexity: int = 5, clarity: int = 7, 
                 estimated_minutes: int = 30) -> Dict:
        """Log a new task when user mentions it"""
        task_id = f"task_{self.session_id}_{len(self.active_tasks) + 1}"
        now = datetime.now().isoformat()
        
        task_data = {
            "session_id": self.session_id,
            "task_id": task_id,
            "description": description[:500],
            "domain": domain,
            "complexity": complexity,
            "clarity": clarity,
            "estimated_minutes": estimated_minutes,
            "status": "INITIATED",
            "initiated_at": now,
            "updated_at": now
        }
        
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/task_states",
            headers=HEADERS, json=task_data, verify=False, timeout=30
        )
        
        if r.status_code in [200, 201]:
            self.active_tasks.append(task_id)
            return {"success": True, "task_id": task_id, "message": f"📌 Task logged: {description[:50]}..."}
        return {"success": False, "error": r.text}
    
    def update_task(self, task_id: str, status: str, artifacts: List[str] = None) -> Dict:
        """Update task status"""
        now = datetime.now().isoformat()
        
        status_field_map = {
            "SOLUTION_PROVIDED": "solution_provided_at",
            "IN_PROGRESS": "in_progress_at",
            "COMPLETED": "completed_at",
            "ABANDONED": "abandoned_at"
        }
        
        update_data = {"status": status, "updated_at": now}
        if status in status_field_map:
            update_data[status_field_map[status]] = now
        if artifacts:
            update_data["artifacts_created"] = json.dumps(artifacts)
        
        r = requests.patch(
            f"{SUPABASE_URL}/rest/v1/task_states?task_id=eq.{task_id}",
            headers=HEADERS, json=update_data, verify=False, timeout=30
        )
        
        # Auto-close interventions for terminal states
        if status in ["COMPLETED", "ABANDONED", "DEFERRED"]:
            self._close_interventions(task_id, status)
        
        return {"success": r.status_code in [200, 204], "status": status}
    
    def complete_task(self, task_id: str, artifacts: List[str] = None) -> Dict:
        """Mark task as completed"""
        result = self.update_task(task_id, "COMPLETED", artifacts)
        if result["success"]:
            # Log activity
            requests.post(
                f"{SUPABASE_URL}/rest/v1/activities",
                headers=HEADERS, verify=False, timeout=30,
                json={
                    "user_id": 1,
                    "activity_type": "TASK_COMPLETION",
                    "platform": "claude_ai",
                    "start_time": datetime.now().isoformat(),
                    "notes": json.dumps({"task_id": task_id, "session_id": self.session_id})
                }
            )
        return result
    
    def _close_interventions(self, task_id: str, resolution: str):
        """Auto-close interventions for a task"""
        # Get open interventions
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/task_interventions?successful=is.null&select=id,task_id,task_description",
            headers=HEADERS, verify=False, timeout=30
        )
        if r.status_code != 200:
            return
        
        for intervention in r.json():
            # Match by task_id or partial description
            if intervention.get('task_id') == task_id or task_id in str(intervention.get('task_description', '')):
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/task_interventions?id=eq.{intervention['id']}",
                    headers=HEADERS, verify=False, timeout=30,
                    json={
                        "successful": resolution == "COMPLETED",
                        "user_response": resolution,
                        "reasoning": f"Auto-closed by Claude session {self.session_id}"
                    }
                )
    
    def log_context_switch(self, from_task: str, to_topic: str) -> Dict:
        """Log when user switches context mid-task (ADHD pattern)"""
        self.context_switches += 1
        now = datetime.now().isoformat()
        
        data = {
            "user_id": 1,
            "activity_type": "CONTEXT_SWITCH",
            "platform": "claude_ai",
            "start_time": now,
            "notes": json.dumps({
                "session_id": self.session_id,
                "from_task": from_task,
                "to_topic": to_topic,
                "switch_count": self.context_switches
            })
        }
        
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/activities",
            headers=HEADERS, json=data, verify=False, timeout=30
        )
        
        # Update daily metrics
        self._increment_daily_switches()
        
        return {
            "logged": r.status_code in [200, 201],
            "total_switches": self.context_switches,
            "warning": "⚠️ Context switch detected" if self.context_switches >= 3 else None
        }
    
    def _increment_daily_switches(self):
        """Update daily context switch count"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Check if today's record exists
        r = requests.get(
            f"{SUPABASE_URL}/rest/v1/daily_metrics?date=eq.{today}&limit=1",
            headers=HEADERS, verify=False, timeout=30
        )
        
        if r.status_code == 200 and r.json():
            current = r.json()[0]
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/daily_metrics?date=eq.{today}",
                headers=HEADERS, verify=False, timeout=30,
                json={"context_switches": (current.get('context_switches') or 0) + 1}
            )
        else:
            requests.post(
                f"{SUPABASE_URL}/rest/v1/daily_metrics",
                headers=HEADERS, verify=False, timeout=30,
                json={"user_id": 1, "date": today, "context_switches": 1}
            )
    
    def log_insight(self, title: str, description: str, 
                    insight_type: str = "LEARNING", priority: str = "Medium") -> Dict:
        """Log insights, learnings, bugs discovered"""
        data = {
            "user_id": 1,
            "insight_type": insight_type,
            "title": title[:200],
            "description": description[:1000],
            "priority": priority,
            "source": "claude_ai",
            "confidence": 0.85,
            "created_at": datetime.now().isoformat()
        }
        
        r = requests.post(
            f"{SUPABASE_URL}/rest/v1/insights",
            headers=HEADERS, json=data, verify=False, timeout=30
        )
        
        return {"success": r.status_code in [200, 201], "title": title}
    
    def end_session(self, summary: str = None) -> Dict:
        """Call at END of conversation"""
        now = datetime.now().isoformat()
        
        # Mark any INITIATED tasks as ABANDONED if not touched
        for task_id in self.active_tasks:
            r = requests.get(
                f"{SUPABASE_URL}/rest/v1/task_states?task_id=eq.{task_id}&select=status",
                headers=HEADERS, verify=False, timeout=30
            )
            if r.status_code == 200 and r.json():
                if r.json()[0].get('status') == 'INITIATED':
                    self.update_task(task_id, "DEFERRED")
        
        # Log session end
        requests.post(
            f"{SUPABASE_URL}/rest/v1/activities",
            headers=HEADERS, verify=False, timeout=30,
            json={
                "user_id": 1,
                "activity_type": "CLAUDE_SESSION_END",
                "platform": "claude_ai",
                "start_time": now,
                "notes": json.dumps({
                    "session_id": self.session_id,
                    "tasks_created": len(self.active_tasks),
                    "context_switches": self.context_switches,
                    "summary": summary
                })
            }
        )
        
        return {
            "session_id": self.session_id,
            "ended_at": now,
            "tasks_created": len(self.active_tasks),
            "context_switches": self.context_switches
        }


# Quick functions for Claude to call inline
_logger = None

def init_session():
    """Call at START of every chat"""
    global _logger
    _logger = ClaudeSessionLogger()
    return _logger.start_session()

def log_task(description: str, domain: str = "BUSINESS", complexity: int = 5):
    """Log a task mentioned by user"""
    global _logger
    if not _logger:
        init_session()
    return _logger.log_task(description, domain, complexity)

def complete_task(task_id: str, artifacts: List[str] = None):
    """Mark task complete"""
    global _logger
    if _logger:
        return _logger.complete_task(task_id, artifacts)

def context_switch(from_task: str, to_topic: str):
    """Log context switch"""
    global _logger
    if _logger:
        return _logger.log_context_switch(from_task, to_topic)

def end_session(summary: str = None):
    """Call at END of chat"""
    global _logger
    if _logger:
        return _logger.end_session(summary)


if __name__ == "__main__":
    # Test the logger
    result = init_session()
    print(json.dumps(result, indent=2, default=str))
