#!/usr/bin/env python3
"""
CLAUDE SESSION BRIDGE V1.0
==========================
Bridges Claude AI conversations to Life OS Supabase database.
Created by: Ariel Shapira, Solo Founder - Everest Capital USA

This script should be called by Claude at the START of every conversation
and during task transitions to keep Life OS in sync.

Functions:
- start_session(): Initialize new session, check for pending tasks
- log_task(): Log new task from conversation
- update_task(): Update task status
- complete_task(): Mark task complete + close interventions
- log_context_switch(): Track ADHD context switches
- end_session(): Summarize session activity
"""

import os
import json
import requests
from datetime import datetime, timezone
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

class ClaudeSessionBridge:
    def __init__(self):
        self.session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.session_tasks = []
        self.context_switches = 0
        self.current_task_id = None
        self.session_start = datetime.now(timezone.utc).isoformat()
    
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
            else:
                return {"error": f"Unknown method: {method}"}
            
            if r.status_code in [200, 201, 204]:
                return r.json() if r.text else {"success": True}
            else:
                return {"error": r.status_code, "message": r.text}
        except Exception as e:
            return {"error": str(e)}
    
    def start_session(self) -> dict:
        """
        Initialize Claude session. Call this FIRST in every conversation.
        Returns pending tasks and open interventions.
        """
        result = {
            "session_id": self.session_id,
            "started_at": self.session_start,
            "pending_tasks": [],
            "open_interventions": [],
            "status": "initialized"
        }
        
        # Check for pending tasks (not completed/abandoned)
        pending = self._api_call(
            "GET", 
            "task_states?status=not.in.(COMPLETED,ABANDONED,DEFERRED)&order=initiated_at.desc&limit=10"
        )
        if isinstance(pending, list):
            result["pending_tasks"] = [
                {"task_id": t["task_id"], "description": t.get("description", "")[:50], 
                 "status": t["status"], "domain": t.get("domain")}
                for t in pending
            ]
        
        # Check for open interventions
        interventions = self._api_call(
            "GET",
            "task_interventions?successful=is.null&order=triggered_at.desc&limit=5"
        )
        if isinstance(interventions, list):
            result["open_interventions"] = [
                {"id": i["id"], "task": i.get("task_description", "")[:40], 
                 "level": i.get("intervention_level"), "message": i.get("message", "")[:60]}
                for i in interventions
            ]
        
        # Log session start activity
        self._api_call("POST", "activities", {
            "user_id": 1,
            "activity_type": "CLAUDE_SESSION",
            "platform": "life_os",
            "start_time": self.session_start,
            "notes": json.dumps({
                "session_id": self.session_id,
                "event": "SESSION_START",
                "pending_tasks": len(result["pending_tasks"]),
                "open_interventions": len(result["open_interventions"])
            })
        })
        
        return result
    
    def log_task(self, description: str, domain: str = "BUSINESS", 
                 complexity: int = 5, clarity: int = 7, 
                 estimated_minutes: int = 30) -> dict:
        """
        Log a new task from conversation.
        Domain: BUSINESS, FAMILY, MICHAEL, PERSONAL
        """
        task_id = f"claude_{self.session_id}_{len(self.session_tasks) + 1}"
        now = datetime.now(timezone.utc).isoformat()
        
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
        
        result = self._api_call("POST", "task_states", task_data)
        
        if isinstance(result, list) or not result.get("error"):
            self.session_tasks.append(task_id)
            self.current_task_id = task_id
            return {"success": True, "task_id": task_id, "status": "INITIATED"}
        
        return result
    
    def update_task(self, task_id: str, status: str, notes: str = None) -> dict:
        """
        Update task status.
        Status: SOLUTION_PROVIDED, IN_PROGRESS, COMPLETED, ABANDONED, BLOCKED, DEFERRED
        """
        now = datetime.now(timezone.utc).isoformat()
        
        status_field_map = {
            "SOLUTION_PROVIDED": "solution_provided_at",
            "IN_PROGRESS": "in_progress_at",
            "COMPLETED": "completed_at",
            "ABANDONED": "abandoned_at",
            "BLOCKED": "blocked_at",
            "DEFERRED": "deferred_at"
        }
        
        update_data = {"status": status, "updated_at": now}
        if status in status_field_map:
            update_data[status_field_map[status]] = now
        
        result = self._api_call("PATCH", f"task_states?task_id=eq.{task_id}", update_data)
        
        # Auto-close interventions for terminal states
        if status in ["COMPLETED", "ABANDONED", "DEFERRED"]:
            self._close_interventions(task_id, status)
        
        return {"success": True, "task_id": task_id, "new_status": status}
    
    def complete_task(self, task_id: str = None, summary: str = None) -> dict:
        """
        Mark task as completed. Uses current task if task_id not provided.
        Also logs completion activity and closes interventions.
        """
        task_id = task_id or self.current_task_id
        if not task_id:
            return {"error": "No task_id provided and no current task"}
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Update task status
        self.update_task(task_id, "COMPLETED")
        
        # Log completion activity
        self._api_call("POST", "activities", {
            "user_id": 1,
            "activity_type": "TASK_COMPLETION",
            "platform": "life_os",
            "start_time": now,
            "notes": json.dumps({
                "session_id": self.session_id,
                "task_id": task_id,
                "summary": summary or "Completed via Claude session",
                "completed_by": "Claude AI Architect"
            })
        })
        
        return {"success": True, "task_id": task_id, "status": "COMPLETED"}
    
    def _close_interventions(self, task_id: str, resolution: str) -> int:
        """Close open interventions for a task"""
        now = datetime.now(timezone.utc).isoformat()
        
        # Find open interventions
        interventions = self._api_call(
            "GET",
            f"task_interventions?successful=is.null&select=id,task_description"
        )
        
        if not isinstance(interventions, list):
            return 0
        
        closed = 0
        task_prefix = task_id.split('_')[1] if '_' in task_id else task_id[:10]
        
        for i in interventions:
            desc = (i.get("task_description") or "").lower()
            if task_prefix.lower() in desc or task_id.lower() in desc:
                self._api_call("PATCH", f"task_interventions?id=eq.{i['id']}", {
                    "successful": resolution == "COMPLETED",
                    "user_response": resolution,
                    "reasoning": f"Auto-closed by Claude session {self.session_id} at {now}"
                })
                closed += 1
        
        return closed
    
    def log_context_switch(self, from_task: str = None, to_task: str = None, 
                           reason: str = None) -> dict:
        """
        Log an ADHD context switch. Important for pattern detection.
        """
        self.context_switches += 1
        now = datetime.now(timezone.utc).isoformat()
        
        self._api_call("POST", "activities", {
            "user_id": 1,
            "activity_type": "CONTEXT_SWITCH",
            "platform": "life_os",
            "start_time": now,
            "notes": json.dumps({
                "session_id": self.session_id,
                "from_task": from_task,
                "to_task": to_task,
                "reason": reason,
                "switch_count": self.context_switches
            })
        })
        
        # Trigger warning if too many switches
        if self.context_switches >= 3:
            return {
                "warning": f"⚠️ {self.context_switches} context switches detected",
                "recommendation": "Consider micro-commitment or body doubling strategy"
            }
        
        return {"logged": True, "total_switches": self.context_switches}
    
    def end_session(self, summary: str = None) -> dict:
        """
        End Claude session. Logs summary and checks for incomplete tasks.
        """
        now = datetime.now(timezone.utc).isoformat()
        
        # Get session stats
        completed = 0
        incomplete = []
        
        for task_id in self.session_tasks:
            task = self._api_call("GET", f"task_states?task_id=eq.{task_id}&limit=1")
            if isinstance(task, list) and task:
                if task[0].get("status") == "COMPLETED":
                    completed += 1
                else:
                    incomplete.append({
                        "task_id": task_id,
                        "status": task[0].get("status"),
                        "description": task[0].get("description", "")[:40]
                    })
        
        # Log session end
        self._api_call("POST", "activities", {
            "user_id": 1,
            "activity_type": "CLAUDE_SESSION",
            "platform": "life_os",
            "start_time": now,
            "notes": json.dumps({
                "session_id": self.session_id,
                "event": "SESSION_END",
                "tasks_created": len(self.session_tasks),
                "tasks_completed": completed,
                "context_switches": self.context_switches,
                "summary": summary
            })
        })
        
        result = {
            "session_id": self.session_id,
            "duration": f"Started at {self.session_start}",
            "tasks_created": len(self.session_tasks),
            "tasks_completed": completed,
            "context_switches": self.context_switches,
            "incomplete_tasks": incomplete
        }
        
        if incomplete:
            result["warning"] = f"⚠️ {len(incomplete)} incomplete task(s) - may trigger intervention"
        
        return result
    
    def quick_log(self, description: str, domain: str = "BUSINESS") -> dict:
        """
        Quick one-liner to log and immediately mark as in-progress.
        For tasks Claude is actively working on.
        """
        task = self.log_task(description, domain)
        if task.get("success"):
            self.update_task(task["task_id"], "IN_PROGRESS")
            return {"task_id": task["task_id"], "status": "IN_PROGRESS", "tracking": True}
        return task


# Convenience functions for Claude to call directly
_bridge = None

def init_session():
    """Initialize session - call at start of every chat"""
    global _bridge
    _bridge = ClaudeSessionBridge()
    return _bridge.start_session()

def log(description: str, domain: str = "BUSINESS", complexity: int = 5):
    """Quick log a task"""
    global _bridge
    if not _bridge:
        _bridge = ClaudeSessionBridge()
    return _bridge.quick_log(description, domain)

def done(task_id: str = None, summary: str = None):
    """Mark task complete"""
    global _bridge
    if not _bridge:
        return {"error": "No session initialized"}
    return _bridge.complete_task(task_id, summary)

def switch(from_task: str = None, to_task: str = None, reason: str = None):
    """Log context switch"""
    global _bridge
    if not _bridge:
        _bridge = ClaudeSessionBridge()
    return _bridge.log_context_switch(from_task, to_task, reason)

def end(summary: str = None):
    """End session"""
    global _bridge
    if not _bridge:
        return {"error": "No session initialized"}
    return _bridge.end_session(summary)


if __name__ == "__main__":
    # Test the bridge
    print("Testing Claude Session Bridge...")
    
    result = init_session()
    print(f"\n1. Session started: {result['session_id']}")
    print(f"   Pending tasks: {len(result['pending_tasks'])}")
    print(f"   Open interventions: {len(result['open_interventions'])}")
    
    task = log("Test task from Claude Session Bridge", "BUSINESS", 3)
    print(f"\n2. Task logged: {task}")
    
    complete = done(summary="Test completed successfully")
    print(f"\n3. Task completed: {complete}")
    
    session_end = end("Test session completed")
    print(f"\n4. Session ended: {session_end}")
