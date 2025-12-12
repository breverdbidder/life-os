#!/usr/bin/env python3
"""
LIFE OS UNIVERSAL BRIDGE
========================
Single interface for all Life OS domains. 
Routes natural language commands to correct Supabase tables.

Author: Claude Opus 4.5 (AI Architect)
Owner: Ariel Shapira, Everest Capital USA
Created: December 12, 2025

Usage:
    from life_os_bridge import LifeOSBridge
    
    bridge = LifeOSBridge()
    
    # Any domain - same pattern
    bridge.log_swim_time("100 Free", 52.45, "Practice")
    bridge.log_health(sleep_hours=7.5, energy=8)
    bridge.create_task("Review Dec 17 auction", domain="BUSINESS")
    bridge.deploy_to_claude_code("Fix BECA scraper", "P0", "brevard-bidder-scraper")
"""

import os
import json
import httpx
from datetime import datetime, timezone, date
from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, asdict
from enum import Enum

# ============================================================
# CONFIGURATION
# ============================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Domain categories for routing
class Domain(str, Enum):
    BUSINESS = "BUSINESS"
    MICHAEL = "MICHAEL"
    FAMILY = "FAMILY"
    PERSONAL = "PERSONAL"

class Priority(str, Enum):
    P0 = "P0"  # Critical - drop everything
    P1 = "P1"  # High - today
    P2 = "P2"  # Medium - this week
    P3 = "P3"  # Low - when possible

# ============================================================
# SUPABASE CLIENT
# ============================================================

class SupabaseClient:
    """Async-compatible Supabase REST client"""
    
    def __init__(self, url: str = None, key: str = None):
        self.url = url or SUPABASE_URL
        self.key = key or SUPABASE_KEY
        self.headers = {
            "apikey": self.key,
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def insert(self, table: str, data: dict) -> dict:
        """Insert a record into a table"""
        with httpx.Client(timeout=30) as client:
            resp = client.post(
                f"{self.url}/rest/v1/{table}",
                headers=self.headers,
                json=data
            )
            if resp.status_code >= 400:
                return {"error": resp.text, "status": resp.status_code}
            return resp.json()[0] if resp.json() else {"success": True}
    
    def query(self, table: str, params: dict = None) -> list:
        """Query records from a table"""
        with httpx.Client(timeout=30) as client:
            resp = client.get(
                f"{self.url}/rest/v1/{table}",
                headers=self.headers,
                params=params or {}
            )
            if resp.status_code >= 400:
                return []
            return resp.json()
    
    def update(self, table: str, filters: dict, data: dict) -> dict:
        """Update records matching filters"""
        params = {f"{k}": f"eq.{v}" for k, v in filters.items()}
        with httpx.Client(timeout=30) as client:
            resp = client.patch(
                f"{self.url}/rest/v1/{table}",
                headers=self.headers,
                params=params,
                json=data
            )
            if resp.status_code >= 400:
                return {"error": resp.text}
            return resp.json()[0] if resp.json() else {"success": True}

# ============================================================
# LIFE OS BRIDGE - MAIN CLASS
# ============================================================

class LifeOSBridge:
    """
    Universal Bridge for Life OS.
    Single interface to all domains - just call the method.
    """
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.db = SupabaseClient(supabase_url, supabase_key)
        self.user_id = 1  # Ariel's user ID
    
    # ========================================================
    # 🏊 MICHAEL SWIMMING
    # ========================================================
    
    def log_swim_time(
        self,
        event: str,
        time_seconds: float,
        meet_name: str = "Practice",
        date_recorded: str = None,
        notes: str = None
    ) -> dict:
        """
        Log Michael's swim time.
        
        Events: 50 Free, 100 Free, 200 Free, 100 Fly, 100 Back
        """
        return self.db.insert("michael_swim_times", {
            "event": event,
            "time_seconds": time_seconds,
            "date": date_recorded or date.today().isoformat(),
            "meet_name": meet_name,
            "notes": notes
        })
    
    def log_nutrition(
        self,
        calories: int,
        protein_g: int,
        carbs_g: int = None,
        fat_g: int = None,
        is_keto_day: bool = True,
        meal_notes: str = None
    ) -> dict:
        """
        Log Michael's nutrition.
        
        Keto Mon-Thu, moderate carbs Fri-Sun for Shabbat.
        """
        day_of_week = datetime.now().weekday()
        expected_keto = day_of_week < 4  # Mon-Thu
        
        return self.db.insert("michael_nutrition", {
            "date": date.today().isoformat(),
            "calories": calories,
            "protein_g": protein_g,
            "carbs_g": carbs_g,
            "fat_g": fat_g,
            "is_keto_day": is_keto_day,
            "keto_compliant": is_keto_day == expected_keto,
            "notes": meal_notes
        })
    
    def log_recruiting_contact(
        self,
        school: str,
        coach_name: str,
        contact_type: str = "email",
        notes: str = None,
        follow_up_date: str = None
    ) -> dict:
        """Log D1 recruiting outreach"""
        return self.db.insert("michael_recruiting", {
            "school": school,
            "coach_name": coach_name,
            "contact_type": contact_type,
            "contact_date": date.today().isoformat(),
            "notes": notes,
            "follow_up_date": follow_up_date,
            "status": "contacted"
        })
    
    def get_swim_progress(self, event: str = None, limit: int = 10) -> list:
        """Get recent swim times, optionally filtered by event"""
        params = {"order": "date.desc", "limit": str(limit)}
        if event:
            params["event"] = f"eq.{event}"
        return self.db.query("michael_swim_times", params)
    
    # ========================================================
    # ❤️ HEALTH & WELLNESS
    # ========================================================
    
    def log_health(
        self,
        sleep_hours: float = None,
        energy_level: int = None,
        focus_quality: int = None,
        mood: int = None,
        notes: str = None
    ) -> dict:
        """
        Log daily health metrics.
        
        Levels are 1-10 scale.
        """
        data = {
            "user_id": self.user_id,
            "date": date.today().isoformat()
        }
        if sleep_hours is not None:
            data["sleep_hours"] = sleep_hours
        if energy_level is not None:
            data["energy_level"] = energy_level
        if focus_quality is not None:
            data["focus_quality"] = focus_quality
        if mood is not None:
            data["mood"] = mood
        if notes:
            data["notes"] = notes
        
        return self.db.insert("health_logs", data)
    
    # ========================================================
    # 💡 LEARNING & INSIGHTS
    # ========================================================
    
    def log_learning(
        self,
        topic: str,
        source: str = "YouTube",
        key_takeaways: List[str] = None,
        application_notes: str = None,
        duration_minutes: int = None,
        url: str = None
    ) -> dict:
        """Log a learning session (YouTube, article, podcast, etc.)"""
        return self.db.insert("learning_sessions", {
            "user_id": self.user_id,
            "topic": topic,
            "source": source,
            "key_takeaways": key_takeaways or [],
            "application_notes": application_notes,
            "duration_minutes": duration_minutes,
            "url": url,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    def log_insight(
        self,
        title: str,
        description: str,
        insight_type: str = "GENERAL",
        priority: str = "Medium",
        action_taken: str = None
    ) -> dict:
        """Log an insight or realization"""
        return self.db.insert("insights", {
            "user_id": self.user_id,
            "title": title,
            "description": description,
            "insight_type": insight_type,
            "priority": priority,
            "action_taken": action_taken,
            "status": "Active",
            "source": "life_os_bridge"
        })
    
    # ========================================================
    # 🧠 ADHD TASK TRACKING
    # ========================================================
    
    def create_task(
        self,
        title: str,
        description: str = None,
        domain: str = "PERSONAL",
        priority: str = "medium",
        complexity: int = 5,
        estimated_minutes: int = 30,
        due_date: str = None
    ) -> dict:
        """
        Create an ADHD-tracked task.
        
        Domains: BUSINESS, MICHAEL, FAMILY, PERSONAL
        Priority: critical, high, medium, low
        Complexity: 1-10
        """
        return self.db.insert("tasks", {
            "user_id": self.user_id,
            "title": title,
            "description": description,
            "domain": domain,
            "priority": priority,
            "status": "pending",
            "complexity": complexity,
            "estimated_minutes": estimated_minutes,
            "due_date": due_date,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    def update_task_status(self, task_id: int, status: str, notes: str = None) -> dict:
        """Update task status: pending, in_progress, completed, abandoned, blocked"""
        data = {"status": status}
        if status == "completed":
            data["completed_at"] = datetime.now(timezone.utc).isoformat()
        if notes:
            data["completion_notes"] = notes
        return self.db.update("tasks", {"id": task_id}, data)
    
    def get_pending_tasks(self, domain: str = None) -> list:
        """Get pending tasks, optionally by domain"""
        params = {"status": "eq.pending", "order": "priority.asc,created_at.asc"}
        if domain:
            params["domain"] = f"eq.{domain}"
        return self.db.query("tasks", params)
    
    def log_task_abandonment(self, task_id: int, reason: str, pattern_notes: str = None) -> dict:
        """Log ADHD task abandonment for pattern detection"""
        return self.db.insert("abandonment_patterns", {
            "user_id": self.user_id,
            "task_id": task_id,
            "reason": reason,
            "pattern_notes": pattern_notes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    # ========================================================
    # 👨‍👩‍👦 FAMILY
    # ========================================================
    
    def log_family_event(
        self,
        title: str,
        event_type: str = "general",
        event_date: str = None,
        notes: str = None
    ) -> dict:
        """
        Log family event.
        
        Types: Shabbat, holiday, birthday, appointment, general
        """
        return self.db.insert("family_events", {
            "user_id": self.user_id,
            "title": title,
            "event_type": event_type,
            "date": event_date or date.today().isoformat(),
            "notes": notes
        })
    
    # ========================================================
    # 🏢 BUSINESS - BIDDEED.AI
    # ========================================================
    
    def deploy_to_claude_code(
        self,
        objective: str,
        priority: str = "P2",
        repository: str = "breverdbidder/brevard-bidder-scraper",
        task_type: str = "code_fix",
        target_file: str = None,
        success_criteria: List[str] = None,
        depends_on: List[str] = None,
        human_checkpoint: bool = False
    ) -> dict:
        """
        Deploy a task to Claude Code via LangGraph orchestration.
        
        This is THE bridge from AI Architect conversations to autonomous execution.
        """
        task_id = f"{task_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        node_name = objective.lower().replace(" ", "_")[:30]
        
        tsf = {
            "task_id": task_id,
            "langgraph_node": node_name,
            "repository": repository,
            "priority": priority,
            "objective": objective,
            "target_file": target_file,
            "success_criteria": success_criteria or ["Task completed", "Tests pass", "PR created"],
            "timeout_minutes": 30,
            "max_iterations": 5,
            "human_checkpoint": human_checkpoint
        }
        
        return self.db.insert("orchestrated_tasks", {
            "task_id": task_id,
            "langgraph_node": node_name,
            "repository": repository,
            "priority": priority,
            "task_type": task_type,
            "tsf": tsf,
            "status": "pending",
            "depends_on": depends_on or [],
            "blocks": []
        })
    
    def get_orchestration_queue(self) -> list:
        """Get current Claude Code task queue"""
        return self.db.query("orchestrated_tasks", {
            "order": "priority.asc,created_at.asc",
            "select": "task_id,status,priority,repository,langgraph_node"
        })
    
    def log_auction_decision(
        self,
        case_number: str,
        property_address: str,
        decision: str,
        max_bid: float = None,
        judgment_amount: float = None,
        reasoning: str = None
    ) -> dict:
        """Log foreclosure auction bid decision"""
        return self.db.insert("bid_decisions", {
            "case_number": case_number,
            "property_address": property_address,
            "decision": decision,  # BID, SKIP, REVIEW
            "max_bid": max_bid,
            "judgment_amount": judgment_amount,
            "reasoning": reasoning,
            "decision_date": date.today().isoformat()
        })
    
    # ========================================================
    # 📊 DAILY METRICS & REPORTS
    # ========================================================
    
    def log_daily_metrics(
        self,
        tasks_completed: int = 0,
        tasks_created: int = 0,
        focus_minutes: int = 0,
        context_switches: int = 0,
        domain_breakdown: Dict[str, int] = None
    ) -> dict:
        """Log end-of-day productivity metrics"""
        return self.db.insert("daily_metrics", {
            "user_id": self.user_id,
            "date": date.today().isoformat(),
            "tasks_completed": tasks_completed,
            "tasks_created": tasks_created,
            "focus_minutes": focus_minutes,
            "context_switches": context_switches,
            "domain_breakdown": domain_breakdown or {}
        })
    
    def get_daily_summary(self, target_date: str = None) -> dict:
        """Get daily summary across all domains"""
        target = target_date or date.today().isoformat()
        
        return {
            "date": target,
            "tasks": self.db.query("tasks", {"created_at": f"gte.{target}T00:00:00"}),
            "health": self.db.query("health_logs", {"date": f"eq.{target}"}),
            "swim_times": self.db.query("michael_swim_times", {"date": f"eq.{target}"}),
            "learning": self.db.query("learning_sessions", {"created_at": f"gte.{target}T00:00:00"}),
            "orchestration": self.db.query("orchestrated_tasks", {"created_at": f"gte.{target}T00:00:00"})
        }

# ============================================================
# CLI INTERFACE
# ============================================================

def main():
    """CLI for quick bridge operations"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Life OS Universal Bridge")
    parser.add_argument("--action", required=True, choices=[
        "swim", "health", "task", "learning", "family", "deploy", "queue", "summary"
    ])
    parser.add_argument("--data", type=str, help="JSON data for the action")
    
    args = parser.parse_args()
    bridge = LifeOSBridge()
    
    if args.action == "queue":
        queue = bridge.get_orchestration_queue()
        for task in queue:
            print(f"{task['priority']} | {task['status']:12} | {task['task_id']}")
    
    elif args.action == "summary":
        summary = bridge.get_daily_summary()
        print(json.dumps(summary, indent=2, default=str))
    
    elif args.data:
        data = json.loads(args.data)
        
        if args.action == "swim":
            result = bridge.log_swim_time(**data)
        elif args.action == "health":
            result = bridge.log_health(**data)
        elif args.action == "task":
            result = bridge.create_task(**data)
        elif args.action == "learning":
            result = bridge.log_learning(**data)
        elif args.action == "family":
            result = bridge.log_family_event(**data)
        elif args.action == "deploy":
            result = bridge.deploy_to_claude_code(**data)
        
        print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    main()
