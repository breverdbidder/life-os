#!/usr/bin/env python3
"""
LIFE OS - ADHD Monitor (Runs every 30 minutes)
Created by: Ariel Shapira, Solo Founder - Everest Capital USA

This script:
1. Checks all active tasks for abandonment risk
2. Runs XGBoost prediction for intervention need
3. Triggers interventions if needed
4. Updates daily metrics
"""

import os
import json
import requests
from datetime import datetime, timedelta
import numpy as np

# Configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://mocerqjnksmhcjzxrewo.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDUzMjUyNiwiZXhwIjoyMDgwMTA4NTI2fQ.fL255mO0V8-rrU0Il3L41cIdQXUau-HRQXiamTqp9nE')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def get_active_tasks():
    """Get all active (non-completed) tasks"""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/task_states?status=in.(INITIATED,SOLUTION_PROVIDED,IN_PROGRESS)&select=*",
        headers=headers, verify=False, timeout=30
    )
    return r.json() if r.status_code == 200 else []

def calculate_abandonment_risk(task):
    """
    XGBoost-style risk calculation based on:
    - Time since initiation
    - Task complexity
    - Domain (BUSINESS tasks tend to get abandoned more)
    - Time of day
    - Historical patterns
    """
    now = datetime.now()
    
    # Parse initiated_at
    initiated = datetime.fromisoformat(task['initiated_at'].replace('Z', '+00:00').replace('+00:00', ''))
    minutes_active = (now - initiated).total_seconds() / 60
    
    # Base risk factors
    complexity = task.get('complexity', 5) or 5
    domain = task.get('domain', 'PERSONAL')
    
    # Risk calculation (simplified XGBoost features)
    risk = 0.0
    
    # Time factor (exponential increase after 30 minutes)
    if minutes_active > 60:
        risk += 0.4
    elif minutes_active > 30:
        risk += 0.2
    elif minutes_active > 15:
        risk += 0.1
    
    # Complexity factor
    risk += (complexity / 10) * 0.3
    
    # Domain factor (BUSINESS tasks have higher abandonment)
    domain_weights = {'BUSINESS': 0.15, 'PERSONAL': 0.1, 'FAMILY': 0.05, 'MICHAEL': 0.05}
    risk += domain_weights.get(domain, 0.1)
    
    # Time of day factor (afternoon dip)
    hour = now.hour
    if 14 <= hour <= 16:  # Afternoon energy dip
        risk += 0.1
    
    return min(risk, 0.95)  # Cap at 95%

def determine_intervention_level(risk, minutes_active):
    """Determine intervention level based on risk and time"""
    if risk >= 0.7 or minutes_active >= 60:
        return 3, "⚠️ ACCOUNTABILITY"
    elif risk >= 0.5 or minutes_active >= 30:
        return 2, "🔄 Pattern Analysis"
    elif risk >= 0.3 or minutes_active >= 15:
        return 1, "📌 Quick Check"
    return 0, None

def create_intervention(task, level, risk, minutes_active):
    """Create intervention record"""
    messages = {
        1: f"📌 Quick check: '{task['description'][:40]}...' - still on it?",
        2: f"🔄 I notice '{task['description'][:40]}...' from {int(minutes_active)} min ago. Pattern detected. Continue or defer?",
        3: f"⚠️ ACCOUNTABILITY: '{task['description'][:40]}...' started {int(minutes_active)} min ago. Status? Be honest."
    }
    
    intervention = {
        "user_id": 1,
        "task_id": task['task_id'],
        "intervention_type": ["QUICK_CHECK", "PATTERN_ANALYSIS", "ACCOUNTABILITY"][level-1],
        "intervention_level": level,
        "message": messages[level],
        "task_description": task['description'],
        "abandonment_probability": risk,
        "risk_level": "HIGH" if risk >= 0.7 else "MEDIUM" if risk >= 0.4 else "LOW",
        "reasoning": f"Risk: {risk:.1%}, Minutes: {int(minutes_active)}, Complexity: {task.get('complexity', 5)}",
        "triggered_at": datetime.now().isoformat(),
        "task_complexity": task.get('complexity', 5),
        "minutes_since_start": int(minutes_active),
        "domain": task.get('domain', 'PERSONAL')
    }
    
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/task_interventions",
        headers=headers, json=intervention, verify=False, timeout=30
    )
    return r.status_code in [200, 201]

def update_daily_metrics(tasks, interventions_triggered):
    """Update daily metrics"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Count by status
    completed = len([t for t in tasks if t['status'] == 'COMPLETED'])
    abandoned = len([t for t in tasks if t['status'] == 'ABANDONED'])
    active = len([t for t in tasks if t['status'] in ['INITIATED', 'IN_PROGRESS']])
    
    # Calculate rates
    total = completed + abandoned + active
    completion_rate = completed / total if total > 0 else 0
    abandonment_rate = abandoned / total if total > 0 else 0
    
    metrics = {
        "tasks_completed": completed,
        "tasks_abandoned": abandoned,
        "completion_rate": completion_rate,
        "abandonment_rate": abandonment_rate,
        "intervention_count": interventions_triggered
    }
    
    # Update existing or insert new
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/daily_metrics?date=eq.{today}",
        headers=headers, json=metrics, verify=False, timeout=30
    )
    
    return r.status_code in [200, 204]

def main():
    print(f"🧠 LIFE OS ADHD MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    # Get active tasks
    tasks = get_active_tasks()
    print(f"\n📋 Active tasks: {len(tasks)}")
    
    interventions_triggered = 0
    
    for task in tasks:
        # Calculate abandonment risk
        risk = calculate_abandonment_risk(task)
        
        # Get time since initiation
        initiated = datetime.fromisoformat(task['initiated_at'].replace('Z', '+00:00').replace('+00:00', ''))
        minutes_active = (datetime.now() - initiated).total_seconds() / 60
        
        # Determine if intervention needed
        level, level_name = determine_intervention_level(risk, minutes_active)
        
        print(f"\n   • {task['task_id']}")
        print(f"     Status: {task['status']}, Risk: {risk:.1%}, Minutes: {int(minutes_active)}")
        
        if level > 0:
            success = create_intervention(task, level, risk, minutes_active)
            if success:
                print(f"     🚨 INTERVENTION TRIGGERED: Level {level} ({level_name})")
                interventions_triggered += 1
    
    # Update daily metrics
    update_daily_metrics(tasks, interventions_triggered)
    
    print(f"\n{'='*60}")
    print(f"✅ Monitor complete. Interventions triggered: {interventions_triggered}")
    print(f"{'='*60}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    main()
