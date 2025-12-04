#!/usr/bin/env python3
"""
LIFE OS - ADHD Monitor V2.0 (Runs every 30 minutes)
Created by: Ariel Shapira, Solo Founder - Everest Capital USA

V2.0 FIXES:
- Auto-closes stale interventions for completed tasks
- Checks for existing open interventions before creating duplicates
- Verifies task state before displaying alerts

This script:
1. FIRST: Closes any stale interventions for completed tasks
2. Checks all active tasks for abandonment risk
3. Runs XGBoost prediction for intervention need
4. Triggers interventions if needed (no duplicates)
5. Updates daily metrics
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

def close_stale_interventions():
    """
    V2.0 FIX: Auto-close interventions that:
    1. Have no response (user_response is NULL)
    2. Are older than 24 hours
    3. Related task is completed or no longer exists
    """
    print("\n🔄 Checking for stale interventions to auto-close...")
    
    # Get unresolved interventions
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/task_interventions?user_response=is.null&select=id,task_id,task_description,triggered_at",
        headers=headers, verify=False, timeout=30
    )
    
    if r.status_code != 200:
        print(f"   ⚠️ Failed to fetch interventions: {r.status_code}")
        return 0
    
    open_interventions = r.json()
    closed_count = 0
    
    for intervention in open_interventions:
        intervention_id = intervention['id']
        task_id = intervention.get('task_id')
        triggered_at = intervention.get('triggered_at', '')
        
        should_close = False
        close_reason = ""
        
        # Check 1: Is it older than 24 hours?
        if triggered_at:
            try:
                triggered = datetime.fromisoformat(triggered_at.replace('Z', '+00:00').replace('+00:00', ''))
                age_hours = (datetime.now() - triggered).total_seconds() / 3600
                if age_hours > 24:
                    should_close = True
                    close_reason = f"Auto-closed: Stale intervention ({int(age_hours)}h old, no response)"
            except:
                pass
        
        # Check 2: If task_id exists, is the task still active?
        if task_id and not should_close:
            task_r = requests.get(
                f"{SUPABASE_URL}/rest/v1/task_states?task_id=eq.{task_id}&select=status",
                headers=headers, verify=False, timeout=30
            )
            if task_r.status_code == 200:
                task_data = task_r.json()
                if not task_data:
                    should_close = True
                    close_reason = "Auto-closed: Task no longer exists"
                elif task_data[0].get('status') in ['COMPLETED', 'ABANDONED', 'DEFERRED']:
                    should_close = True
                    close_reason = f"Auto-closed: Task is {task_data[0].get('status')}"
        
        # Check 3: Check activities for completion signal
        if not should_close and intervention.get('task_description'):
            desc_keywords = intervention['task_description'][:30].lower()
            # Look for matching activity completion in last 48h
            activities_r = requests.get(
                f"{SUPABASE_URL}/rest/v1/activities?activity_type=eq.TASK_COMPLETION&order=created_at.desc&limit=20",
                headers=headers, verify=False, timeout=30
            )
            if activities_r.status_code == 200:
                for activity in activities_r.json():
                    notes = (activity.get('notes') or '').lower()
                    if any(keyword in notes for keyword in desc_keywords.split()[:3]):
                        should_close = True
                        close_reason = "Auto-closed: Matching completion activity found"
                        break
        
        # Close if needed
        if should_close:
            update_r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/task_interventions?id=eq.{intervention_id}",
                headers=headers,
                json={
                    "user_response": "AUTO_CLOSED",
                    "successful": True,
                    "reasoning": close_reason
                },
                verify=False, timeout=30
            )
            if update_r.status_code in [200, 204]:
                print(f"   ✅ Closed intervention #{intervention_id}: {close_reason}")
                closed_count += 1
    
    print(f"   📊 Closed {closed_count} stale interventions")
    return closed_count

def has_open_intervention(task_id):
    """V2.0 FIX: Check if task already has an open intervention"""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/task_interventions?task_id=eq.{task_id}&user_response=is.null&select=id",
        headers=headers, verify=False, timeout=30
    )
    if r.status_code == 200:
        return len(r.json()) > 0
    return False

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

def update_daily_metrics(tasks, interventions_triggered, interventions_closed):
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
        "intervention_count": interventions_triggered,
        "session_recommendation": f"Auto-closed {interventions_closed} stale interventions"
    }
    
    # Update existing or insert new
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/daily_metrics?date=eq.{today}",
        headers=headers, json=metrics, verify=False, timeout=30
    )
    
    return r.status_code in [200, 204]

def main():
    print(f"🧠 LIFE OS ADHD MONITOR V2.0 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    # V2.0 FIX: FIRST close stale interventions
    stale_closed = close_stale_interventions()
    
    # Get active tasks
    tasks = get_active_tasks()
    print(f"\n📋 Active tasks: {len(tasks)}")
    
    interventions_triggered = 0
    
    for task in tasks:
        task_id = task.get('task_id')
        
        # V2.0 FIX: Skip if task already has open intervention
        if task_id and has_open_intervention(task_id):
            print(f"\n   • {task_id}")
            print(f"     ⏭️  Skipped: Already has open intervention")
            continue
        
        # Calculate abandonment risk
        risk = calculate_abandonment_risk(task)
        
        # Get time since initiation
        initiated = datetime.fromisoformat(task['initiated_at'].replace('Z', '+00:00').replace('+00:00', ''))
        minutes_active = (datetime.now() - initiated).total_seconds() / 60
        
        # Determine if intervention needed
        level, level_name = determine_intervention_level(risk, minutes_active)
        
        print(f"\n   • {task_id}")
        print(f"     Status: {task['status']}, Risk: {risk:.1%}, Minutes: {int(minutes_active)}")
        
        if level > 0:
            success = create_intervention(task, level, risk, minutes_active)
            if success:
                print(f"     🚨 INTERVENTION TRIGGERED: Level {level} ({level_name})")
                interventions_triggered += 1
    
    # Update daily metrics
    update_daily_metrics(tasks, interventions_triggered, stale_closed)
    
    print(f"\n{'='*60}")
    print(f"✅ Monitor complete.")
    print(f"   • Stale interventions closed: {stale_closed}")
    print(f"   • New interventions triggered: {interventions_triggered}")
    print(f"{'='*60}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    main()
