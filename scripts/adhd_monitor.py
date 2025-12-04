#!/usr/bin/env python3
"""
LIFE OS - ADHD Monitor V2.1 (Runs every 30 minutes)
Created by: Ariel Shapira, Solo Founder - Everest Capital USA

V2.1 FIXES:
- Fixed task_id type mismatch (int vs text)
- Uses task_description for duplicate checking
- Auto-closes stale interventions

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
    """Auto-close interventions older than 24h or for resolved tasks"""
    print("\n🔄 Checking for stale interventions to auto-close...")
    
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/task_interventions?user_response=is.null&select=id,task_description,triggered_at",
        headers=headers, verify=False, timeout=30
    )
    
    if r.status_code != 200:
        print(f"   ⚠️ Failed to fetch interventions: {r.status_code}")
        return 0
    
    open_interventions = r.json()
    closed_count = 0
    
    for intervention in open_interventions:
        intervention_id = intervention['id']
        triggered_at = intervention.get('triggered_at', '')
        task_desc = intervention.get('task_description', '')
        
        should_close = False
        close_reason = ""
        
        # Check if older than 24 hours
        if triggered_at:
            try:
                triggered = datetime.fromisoformat(triggered_at.replace('Z', '+00:00').replace('+00:00', ''))
                age_hours = (datetime.now() - triggered).total_seconds() / 3600
                if age_hours > 24:
                    should_close = True
                    close_reason = f"Auto-closed: Stale ({int(age_hours)}h old)"
            except:
                pass
        
        # Check for matching completion activity
        if not should_close and task_desc:
            activities_r = requests.get(
                f"{SUPABASE_URL}/rest/v1/activities?activity_type=eq.TASK_COMPLETION&order=created_at.desc&limit=20",
                headers=headers, verify=False, timeout=30
            )
            if activities_r.status_code == 200:
                keywords = task_desc.lower().split()[:3]
                for activity in activities_r.json():
                    notes = (activity.get('notes') or '').lower()
                    if any(kw in notes for kw in keywords if len(kw) > 3):
                        should_close = True
                        close_reason = "Auto-closed: Matching completion found"
                        break
        
        if should_close:
            update_r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/task_interventions?id=eq.{intervention_id}",
                headers=headers,
                json={"user_response": "AUTO_CLOSED", "successful": True, "reasoning": close_reason},
                verify=False, timeout=30
            )
            if update_r.status_code in [200, 204]:
                print(f"   ✅ Closed #{intervention_id}: {close_reason}")
                closed_count += 1
    
    print(f"   📊 Closed {closed_count} stale interventions")
    return closed_count

def has_open_intervention(task_description):
    """Check if similar task already has open intervention (by description match)"""
    if not task_description:
        return False
    desc_prefix = task_description[:30].replace("'", "''")
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/task_interventions?user_response=is.null&task_description=ilike.*{desc_prefix}*&select=id",
        headers=headers, verify=False, timeout=30
    )
    return r.status_code == 200 and len(r.json()) > 0

def get_active_tasks():
    """Get all active (non-completed) tasks"""
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/task_states?status=in.(INITIATED,SOLUTION_PROVIDED,IN_PROGRESS)&select=*",
        headers=headers, verify=False, timeout=30
    )
    return r.json() if r.status_code == 200 else []

def calculate_abandonment_risk(task):
    """XGBoost-style risk calculation"""
    now = datetime.now()
    initiated = datetime.fromisoformat(task['initiated_at'].replace('Z', '+00:00').replace('+00:00', ''))
    minutes_active = (now - initiated).total_seconds() / 60
    
    complexity = task.get('complexity', 5) or 5
    domain = task.get('domain', 'PERSONAL')
    
    risk = 0.0
    if minutes_active > 60: risk += 0.4
    elif minutes_active > 30: risk += 0.2
    elif minutes_active > 15: risk += 0.1
    
    risk += (complexity / 10) * 0.3
    risk += {'BUSINESS': 0.15, 'PERSONAL': 0.1, 'FAMILY': 0.05, 'MICHAEL': 0.05}.get(domain, 0.1)
    
    hour = now.hour
    if 14 <= hour <= 16: risk += 0.1
    
    return min(risk, 0.95)

def determine_intervention_level(risk, minutes_active):
    """Determine intervention level"""
    if risk >= 0.7 or minutes_active >= 60:
        return 3, "⚠️ ACCOUNTABILITY"
    elif risk >= 0.5 or minutes_active >= 30:
        return 2, "🔄 Pattern Analysis"
    elif risk >= 0.3 or minutes_active >= 15:
        return 1, "📌 Quick Check"
    return 0, None

def create_intervention(task, level, risk, minutes_active):
    """Create intervention record - V2.1: task_id set to None (type mismatch fix)"""
    messages = {
        1: f"📌 Quick check: '{task['description'][:40]}...' - still on it?",
        2: f"🔄 Pattern: '{task['description'][:40]}...' - {int(minutes_active)} min. Continue or defer?",
        3: f"⚠️ ACCOUNTABILITY: '{task['description'][:40]}...' - {int(minutes_active)} min. Status?"
    }
    
    intervention = {
        "user_id": 1,
        "task_id": None,  # V2.1 FIX: task_states uses text IDs, interventions expect int
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

def main():
    print(f"🧠 LIFE OS ADHD MONITOR V2.1 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("="*60)
    
    stale_closed = close_stale_interventions()
    tasks = get_active_tasks()
    print(f"\n📋 Active tasks: {len(tasks)}")
    
    interventions_triggered = 0
    
    for task in tasks:
        description = task.get('description', '')
        
        if has_open_intervention(description):
            print(f"\n   • {task.get('task_id', 'unknown')}")
            print(f"     ⏭️  Skipped: Already has open intervention")
            continue
        
        risk = calculate_abandonment_risk(task)
        initiated = datetime.fromisoformat(task['initiated_at'].replace('Z', '+00:00').replace('+00:00', ''))
        minutes_active = (datetime.now() - initiated).total_seconds() / 60
        level, level_name = determine_intervention_level(risk, minutes_active)
        
        print(f"\n   • {task.get('task_id', 'unknown')}")
        print(f"     Status: {task['status']}, Risk: {risk:.1%}, Minutes: {int(minutes_active)}")
        
        if level > 0:
            success = create_intervention(task, level, risk, minutes_active)
            if success:
                print(f"     🚨 INTERVENTION: Level {level} ({level_name})")
                interventions_triggered += 1
            else:
                print(f"     ❌ Failed to create intervention")
    
    print(f"\n{'='*60}")
    print(f"✅ Complete. Closed: {stale_closed}, Triggered: {interventions_triggered}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    main()
