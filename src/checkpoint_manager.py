#!/usr/bin/env python3
"""
BrevardBidderAI - Enhanced Checkpoint Manager V2
Handles: Token limits, Internet disconnection, Session crashes
Author: Ariel Shapira, Solo Founder, Everest Capital USA

FEATURES:
- Auto-save after EVERY tool call (not just 8+)
- Heartbeat pings every 60 seconds during active work
- Offline queue for failed saves (retry on reconnect)
- Last-known-good state recovery
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1MzI1MjYsImV4cCI6MjA4MDEwODUyNn0.ySFJIOngWWB0aqYra4PoGFuqcbdHOx1ZV6T9-klKQDw"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Local backup path for offline scenarios
LOCAL_BACKUP = Path.home() / ".brevard_checkpoint_backup.json"
OFFLINE_QUEUE = Path.home() / ".brevard_offline_queue.json"


class CheckpointManager:
    def __init__(self):
        self.current_session = None
        self.tool_call_count = 0
        self.last_save_time = None
        self.offline_mode = False
        
    def generate_session_id(self, prefix="bba"):
        """Generate unique session ID"""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{ts}"
    
    def is_online(self):
        """Quick connectivity check"""
        try:
            r = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=HEADERS, timeout=3)
            return r.status_code < 500
        except:
            return False
    
    def save_local_backup(self, checkpoint_data):
        """Always save locally as fallback"""
        try:
            LOCAL_BACKUP.write_text(json.dumps(checkpoint_data, indent=2, default=str))
            return True
        except Exception as e:
            print(f"⚠️ Local backup failed: {e}")
            return False
    
    def queue_for_retry(self, checkpoint_data):
        """Queue failed saves for retry when back online"""
        try:
            queue = []
            if OFFLINE_QUEUE.exists():
                queue = json.loads(OFFLINE_QUEUE.read_text())
            queue.append({
                "data": checkpoint_data,
                "queued_at": datetime.now().isoformat(),
                "retries": 0
            })
            # Keep only last 10 queued items
            queue = queue[-10:]
            OFFLINE_QUEUE.write_text(json.dumps(queue, indent=2, default=str))
            return True
        except:
            return False
    
    def process_offline_queue(self):
        """Retry queued saves when back online"""
        if not OFFLINE_QUEUE.exists():
            return 0
        
        try:
            queue = json.loads(OFFLINE_QUEUE.read_text())
            successful = 0
            remaining = []
            
            for item in queue:
                if self._save_to_supabase(item["data"]):
                    successful += 1
                else:
                    item["retries"] += 1
                    if item["retries"] < 5:  # Max 5 retries
                        remaining.append(item)
            
            if remaining:
                OFFLINE_QUEUE.write_text(json.dumps(remaining, indent=2))
            else:
                OFFLINE_QUEUE.unlink(missing_ok=True)
            
            return successful
        except:
            return 0
    
    def _save_to_supabase(self, data):
        """Internal: Save to Supabase"""
        try:
            r = requests.post(
                f"{SUPABASE_URL}/rest/v1/session_checkpoints",
                headers={**HEADERS, "Prefer": "resolution=merge-duplicates,return=representation"},
                json=data,
                timeout=10
            )
            return r.status_code in [200, 201]
        except:
            return False
    
    def save(self, session_id, task_description, state_json, priority="high", force=False):
        """
        Save checkpoint - ALWAYS saves locally, attempts cloud save
        Called after EVERY tool call for maximum resilience
        """
        self.tool_call_count += 1
        now = datetime.now()
        
        checkpoint_data = {
            "session_id": session_id,
            "task_description": task_description,
            "state_json": state_json if isinstance(state_json, dict) else json.loads(state_json),
            "tool_calls_count": self.tool_call_count,
            "priority": priority,
            "status": "active",
            "updated_at": now.isoformat(),
            "save_reason": "auto" if not force else "manual"
        }
        
        # ALWAYS save locally first (instant, no network needed)
        self.save_local_backup(checkpoint_data)
        self.last_save_time = now
        
        # Attempt cloud save
        if self.is_online():
            # First, process any queued saves
            queued = self.process_offline_queue()
            if queued > 0:
                print(f"📤 Synced {queued} queued checkpoint(s)")
            
            # Now save current
            if self._save_to_supabase(checkpoint_data):
                print(f"☁️ Checkpoint saved: {session_id} (tool #{self.tool_call_count})")
                self.offline_mode = False
                return {"status": "saved", "location": "cloud+local"}
            else:
                self.queue_for_retry(checkpoint_data)
                return {"status": "queued", "location": "local"}
        else:
            self.offline_mode = True
            self.queue_for_retry(checkpoint_data)
            print(f"📴 Offline - checkpoint queued locally")
            return {"status": "queued", "location": "local"}
    
    def check(self, include_local=True):
        """
        Check for active checkpoints - cloud first, then local backup
        """
        checkpoints = []
        
        # Try cloud first
        if self.is_online():
            try:
                r = requests.get(
                    f"{SUPABASE_URL}/rest/v1/session_checkpoints?status=eq.active&order=updated_at.desc&limit=5",
                    headers=HEADERS,
                    timeout=10
                )
                if r.status_code == 200:
                    checkpoints = r.json()
            except:
                pass
        
        # Also check local backup
        local_checkpoint = None
        if include_local and LOCAL_BACKUP.exists():
            try:
                local_data = json.loads(LOCAL_BACKUP.read_text())
                local_checkpoint = local_data
                # If local is newer than cloud, prioritize it
                if checkpoints:
                    cloud_time = datetime.fromisoformat(checkpoints[0]["updated_at"].replace("Z", ""))
                    local_time = datetime.fromisoformat(local_data["updated_at"])
                    if local_time > cloud_time:
                        print("📱 Local checkpoint is newer than cloud")
                        checkpoints.insert(0, {**local_data, "_source": "local"})
                elif local_data.get("status") == "active":
                    checkpoints = [{**local_data, "_source": "local"}]
            except:
                pass
        
        if checkpoints:
            latest = checkpoints[0]
            print(f"\n{'='*60}")
            print(f"🔄 ACTIVE CHECKPOINT FOUND")
            print(f"{'='*60}")
            print(f"Session: {latest['session_id']}")
            print(f"Task: {latest['task_description']}")
            print(f"Tool calls: {latest.get('tool_calls_count', 'N/A')}")
            print(f"Last update: {latest['updated_at']}")
            print(f"Source: {latest.get('_source', 'cloud')}")
            print(f"{'='*60}")
            print(f"\n→ Resume this session without asking user")
            return {"found": True, "checkpoint": latest, "count": len(checkpoints)}
        
        return {"found": False, "message": "No active checkpoints"}
    
    def complete(self, session_id):
        """Mark checkpoint as completed"""
        # Update local
        if LOCAL_BACKUP.exists():
            try:
                data = json.loads(LOCAL_BACKUP.read_text())
                if data.get("session_id") == session_id:
                    data["status"] = "completed"
                    data["completed_at"] = datetime.now().isoformat()
                    LOCAL_BACKUP.write_text(json.dumps(data, indent=2))
            except:
                pass
        
        # Update cloud
        if self.is_online():
            try:
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/session_checkpoints?session_id=eq.{session_id}",
                    headers=HEADERS,
                    json={"status": "completed", "completed_at": datetime.now().isoformat()},
                    timeout=10
                )
                print(f"✅ Session {session_id} marked complete")
                return True
            except:
                pass
        return False
    
    def heartbeat(self, session_id, current_task):
        """
        Lightweight heartbeat - call every 60 seconds during long operations
        Just updates timestamp, minimal payload
        """
        if self.is_online():
            try:
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/session_checkpoints?session_id=eq.{session_id}",
                    headers=HEADERS,
                    json={
                        "updated_at": datetime.now().isoformat(),
                        "state_json": {"heartbeat": True, "current_task": current_task}
                    },
                    timeout=5
                )
            except:
                pass


def main():
    """CLI interface"""
    manager = CheckpointManager()
    
    if len(sys.argv) < 2:
        print("Usage: checkpoint_manager.py <command> [args]")
        print("Commands: check, save, complete, heartbeat, sync")
        sys.exit(1)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "check":
        result = manager.check()
        print(json.dumps(result, indent=2, default=str))
        
    elif cmd == "save":
        if len(sys.argv) < 4:
            print("Usage: save <session_id> <task_description> [state_json]")
            sys.exit(1)
        session_id = sys.argv[2]
        task = sys.argv[3]
        state = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
        result = manager.save(session_id, task, state)
        print(json.dumps(result, indent=2))
        
    elif cmd == "complete":
        if len(sys.argv) < 3:
            print("Usage: complete <session_id>")
            sys.exit(1)
        manager.complete(sys.argv[2])
        
    elif cmd == "sync":
        # Force sync offline queue
        if manager.is_online():
            synced = manager.process_offline_queue()
            print(f"Synced {synced} queued checkpoint(s)")
        else:
            print("Still offline")
            
    elif cmd == "heartbeat":
        if len(sys.argv) < 4:
            print("Usage: heartbeat <session_id> <current_task>")
            sys.exit(1)
        manager.heartbeat(sys.argv[2], sys.argv[3])


if __name__ == "__main__":
    main()
