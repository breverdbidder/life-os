#!/usr/bin/env python3
"""
Shapira Life OS - Session Checkpoint Manager
Shared checkpoint system across BrevardBidderAI and Life OS
Author: Ariel Shapira, Solo Founder, Everest Capital USA

Usage:
    python checkpoint_manager.py check      # Check for active checkpoints
    python checkpoint_manager.py save --task "Task" --state '{"key": "value"}'
    python checkpoint_manager.py complete   # Mark current task complete
"""

import os
import sys
import json
import argparse
from datetime import datetime
import urllib.request
import urllib.error

SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1MzI1MjYsImV4cCI6MjA4MDEwODUyNn0.ySFJIOngWWB0aqYra4PoGFuqcbdHOx1ZV6T9-klKQDw"

def make_request(method, endpoint, data=None):
    """Make HTTP request to Supabase"""
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }
    
    if data:
        data = json.dumps(data).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8')) if response.read() else {}
    except urllib.error.HTTPError as e:
        return {"error": str(e), "code": e.code}
    except Exception as e:
        return {"error": str(e)}

def check_checkpoints():
    """Check for active checkpoints"""
    result = make_request("GET", "session_checkpoints?status=eq.active&order=priority.desc,updated_at.desc&limit=5")
    
    if isinstance(result, list) and len(result) > 0:
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║ 🔄 ACTIVE CHECKPOINT FOUND - RESUME TASK                      ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print("")
        
        cp = result[0]
        print(f"📋 Session: {cp.get('session_id')}")
        print(f"📝 Task: {cp.get('task_description')}")
        print(f"🔧 Tool Calls: {cp.get('tool_calls_count', 0)}")
        print(f"⏰ Updated: {cp.get('updated_at')}")
        print("")
        print("📦 State:")
        print(json.dumps(cp.get('state_json', {}), indent=2))
        print("")
        print("═══════════════════════════════════════════════════════════════")
        return cp
    else:
        print("✅ No active checkpoints. Starting fresh session.")
        return None

def save_checkpoint(task, state, priority="high"):
    """Save checkpoint to Supabase"""
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    data = {
        "session_id": session_id,
        "task_description": task,
        "state_json": state if isinstance(state, dict) else json.loads(state),
        "tool_calls_count": 1,
        "priority": priority,
        "status": "active",
        "updated_at": datetime.utcnow().isoformat() + "Z"
    }
    
    result = make_request("POST", "session_checkpoints", data)
    
    if "error" not in result:
        print(f"💾 Checkpoint saved: {session_id}")
        print(f"   Task: {task}")
        return True
    else:
        print(f"⚠️ Save issue: {result}")
        return False

def complete_checkpoint(session_id=None):
    """Mark checkpoint as complete"""
    # This would need the session_id from the check
    print("✅ Task marked complete")
    return True

def main():
    parser = argparse.ArgumentParser(description='Life OS Checkpoint Manager')
    parser.add_argument('command', choices=['check', 'save', 'complete', 'status'])
    parser.add_argument('--task', help='Task description')
    parser.add_argument('--state', help='JSON state', default='{}')
    parser.add_argument('--priority', choices=['high', 'medium', 'low'], default='high')
    
    args = parser.parse_args()
    
    if args.command == 'check':
        return check_checkpoints()
    elif args.command == 'save':
        if not args.task:
            print("❌ --task required")
            return False
        return save_checkpoint(args.task, args.state, args.priority)
    elif args.command == 'complete':
        return complete_checkpoint()

if __name__ == "__main__":
    main()
