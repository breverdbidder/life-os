#!/usr/bin/env python3
"""
BrevardBidderAI Checkpoint Manager
Auto-saves session state to Supabase for seamless resume across conversations.
Author: Ariel Shapira, Solo Founder, Everest Capital USA

Usage:
    # At session start
    python checkpoint_manager.py check
    
    # After 8+ tool calls or before complex operations
    python checkpoint_manager.py save --task "Building NLP chatbot" --state '{"step": 3}'
    
    # When task completes
    python checkpoint_manager.py complete
"""

import os
import sys
import json
import argparse
import requests
from datetime import datetime
import uuid

SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1MzI1MjYsImV4cCI6MjA4MDEwODUyNn0.ySFJIOngWWB0aqYra4PoGFuqcbdHOx1ZV6T9-klKQDw")

# Session file to track current session ID locally
SESSION_FILE = "/tmp/bba_current_session.json"

def get_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

def get_current_session():
    """Get or create current session ID"""
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
            return data.get('session_id'), data.get('tool_calls', 0)
    return None, 0

def set_current_session(session_id, tool_calls=0):
    """Save current session ID locally"""
    with open(SESSION_FILE, 'w') as f:
        json.dump({
            'session_id': session_id,
            'tool_calls': tool_calls,
            'updated': datetime.utcnow().isoformat()
        }, f)

def check_active_checkpoints():
    """Check for active checkpoints to resume"""
    try:
        response = requests.get(
            f"{SUPABASE_URL}/rest/v1/session_checkpoints",
            params={
                "status": "eq.active",
                "order": "priority.desc,updated_at.desc",
                "limit": 5
            },
            headers=get_headers()
        )
        
        if response.status_code == 200:
            checkpoints = response.json()
            if checkpoints:
                print("╔══════════════════════════════════════════════════════════════╗")
                print("║ 🔄 ACTIVE CHECKPOINTS FOUND - RESUME REQUIRED                 ║")
                print("╚══════════════════════════════════════════════════════════════╝")
                print("")
                
                for i, cp in enumerate(checkpoints, 1):
                    print(f"[{i}] {cp.get('task_description', 'No description')}")
                    print(f"    Session: {cp.get('session_id')}")
                    print(f"    Tool Calls: {cp.get('tool_calls_count', 0)}")
                    print(f"    Priority: {cp.get('priority', 'medium')}")
                    print(f"    Updated: {cp.get('updated_at')}")
                    print("")
                    
                # Return most important checkpoint
                latest = checkpoints[0]
                print("═══════════════════════════════════════════════════════════════")
                print("📋 RESUMING TASK:")
                print(f"   {latest.get('task_description')}")
                print("")
                print("📦 STATE:")
                print(json.dumps(latest.get('state_json', {}), indent=2))
                print("═══════════════════════════════════════════════════════════════")
                
                # Set as current session
                set_current_session(latest.get('session_id'), latest.get('tool_calls_count', 0))
                
                return latest
            else:
                print("✅ No active checkpoints. Starting fresh session.")
                # Create new session ID
                new_session = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
                set_current_session(new_session, 0)
                return None
        else:
            print(f"⚠️ Could not check checkpoints: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def save_checkpoint(task_description, state_json, priority="high"):
    """Save current session state as checkpoint"""
    session_id, tool_calls = get_current_session()
    
    if not session_id:
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    tool_calls += 1
    
    try:
        # Upsert checkpoint
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/session_checkpoints",
            headers={**get_headers(), "Prefer": "resolution=merge-duplicates"},
            json={
                "session_id": session_id,
                "task_description": task_description,
                "state_json": state_json if isinstance(state_json, dict) else json.loads(state_json),
                "tool_calls_count": tool_calls,
                "priority": priority,
                "status": "active",
                "updated_at": datetime.utcnow().isoformat() + "Z"
            }
        )
        
        if response.status_code in [200, 201]:
            set_current_session(session_id, tool_calls)
            print(f"💾 Checkpoint saved: {session_id}")
            print(f"   Task: {task_description}")
            print(f"   Tool calls: {tool_calls}")
            return True
        else:
            print(f"❌ Failed to save: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def complete_checkpoint():
    """Mark current checkpoint as completed"""
    session_id, _ = get_current_session()
    
    if not session_id:
        print("⚠️ No active session to complete")
        return False
    
    try:
        response = requests.patch(
            f"{SUPABASE_URL}/rest/v1/session_checkpoints",
            params={"session_id": f"eq.{session_id}"},
            headers=get_headers(),
            json={
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat() + "Z"
            }
        )
        
        if response.status_code == 204:
            print(f"✅ Session completed: {session_id}")
            # Clear local session
            if os.path.exists(SESSION_FILE):
                os.remove(SESSION_FILE)
            return True
        else:
            print(f"❌ Failed to complete: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def increment_tool_calls():
    """Increment tool call counter and auto-checkpoint if needed"""
    session_id, tool_calls = get_current_session()
    tool_calls += 1
    set_current_session(session_id, tool_calls)
    
    # Auto-checkpoint at threshold
    if tool_calls >= 8 and tool_calls % 4 == 0:
        print(f"⚠️ Tool calls: {tool_calls} - Consider saving checkpoint")
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description='BrevardBidderAI Checkpoint Manager')
    parser.add_argument('command', choices=['check', 'save', 'complete', 'increment', 'status'])
    parser.add_argument('--task', help='Task description for save command')
    parser.add_argument('--state', help='JSON state for save command', default='{}')
    parser.add_argument('--priority', choices=['high', 'medium', 'low'], default='high')
    
    args = parser.parse_args()
    
    if args.command == 'check':
        return check_active_checkpoints()
    elif args.command == 'save':
        if not args.task:
            print("❌ --task required for save command")
            return False
        state = args.state if isinstance(args.state, dict) else json.loads(args.state)
        return save_checkpoint(args.task, state, args.priority)
    elif args.command == 'complete':
        return complete_checkpoint()
    elif args.command == 'increment':
        return increment_tool_calls()
    elif args.command == 'status':
        session_id, tool_calls = get_current_session()
        print(f"Session: {session_id or 'None'}")
        print(f"Tool calls: {tool_calls}")

if __name__ == "__main__":
    result = main()
    sys.exit(0 if result else 1)
