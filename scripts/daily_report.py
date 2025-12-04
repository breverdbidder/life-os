#!/usr/bin/env python3
"""
LIFE OS - Daily Report Generator
Created by: Ariel Shapira, Solo Founder - Everest Capital USA
"""

import os
import json
import requests
from datetime import datetime, timedelta

SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://mocerqjnksmhcjzxrewo.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

def generate_daily_report():
    """Generate end-of-day report"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Get all tasks for today
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/task_states?initiated_at=gte.{today}T00:00:00&select=*",
        headers=headers, verify=False, timeout=30
    )
    tasks = r.json() if r.status_code == 200 else []
    
    # Get interventions
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/task_interventions?triggered_at=gte.{today}T00:00:00&select=*",
        headers=headers, verify=False, timeout=30
    )
    interventions = r.json() if r.status_code == 200 else []
    
    # Generate report
    report = f"""
# 📊 LIFE OS DAILY REPORT
## {today}

### 📋 Task Summary
- **Total Tasks**: {len(tasks)}
- **Completed**: {len([t for t in tasks if t['status'] == 'COMPLETED'])}
- **In Progress**: {len([t for t in tasks if t['status'] == 'IN_PROGRESS'])}
- **Abandoned**: {len([t for t in tasks if t['status'] == 'ABANDONED'])}

### 🧠 Focus Interventions
- **Total Interventions**: {len(interventions)}
- **Level 1 (Quick Check)**: {len([i for i in interventions if i.get('intervention_level') == 1])}
- **Level 2 (Pattern)**: {len([i for i in interventions if i.get('intervention_level') == 2])}
- **Level 3 (Accountability)**: {len([i for i in interventions if i.get('intervention_level') == 3])}

### 📈 By Domain
"""
    
    domains = {}
    for t in tasks:
        d = t.get('domain', 'UNKNOWN')
        if d not in domains:
            domains[d] = {'total': 0, 'completed': 0}
        domains[d]['total'] += 1
        if t['status'] == 'COMPLETED':
            domains[d]['completed'] += 1
    
    for domain, counts in domains.items():
        report += f"- **{domain}**: {counts['completed']}/{counts['total']} completed\n"
    
    print(report)
    
    # Save to insights table
    insight = {
        "insight_type": "daily_report",
        "title": f"Daily Report - {today}",
        "content": json.dumps({
            "date": today,
            "total_tasks": len(tasks),
            "completed": len([t for t in tasks if t['status'] == 'COMPLETED']),
            "interventions": len(interventions),
            "domains": domains
        }),
        "status": "Active"
    }
    
    requests.post(
        f"{SUPABASE_URL}/rest/v1/insights",
        headers={**headers, "Prefer": "return=representation"},
        json=insight, verify=False, timeout=30
    )

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings()
    generate_daily_report()
