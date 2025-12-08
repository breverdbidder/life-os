#!/usr/bin/env python3
"""
CLAUDE.AI HANDOFF SCRIPT
Called BY Claude in claude.ai to hand off to external orchestrator.

This is the BRIDGE between:
- Claude.ai session (can't monitor own context)
- External orchestrator (CAN monitor and checkpoint)

Usage in Claude.ai:
When Claude detects heavy task, run this to hand off.
"""

import httpx
import json
import sys
from datetime import datetime, timezone

import os

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
REPO = os.environ.get("LIFE_OS_REPO", "breverdbidder/life-os")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")


def save_handoff_checkpoint(task: str, context: str, completed: list, remaining: list):
    """Save state before handing off to orchestrator"""
    
    checkpoint = {
        "user_id": 1,
        "insight_type": "SESSION_CHECKPOINT",
        "title": f"Handoff - {datetime.now(timezone.utc).strftime('%b %d %I:%M %p')} UTC",
        "description": json.dumps({
            "session_id": f"handoff-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            "task": task,
            "steps_completed": completed,
            "current_step": remaining[0] if remaining else "Complete",
            "next_steps": remaining[1:] if len(remaining) > 1 else [],
            "context_summary": context[:2000],  # Truncate context
            "handoff_reason": "context_limit_approaching",
            "source": "claude_ai_handoff"
        }),
        "priority": "critical",
        "status": "active",
        "source": "claude_ai_handoff"
    }
    
    response = httpx.post(
        f"{SUPABASE_URL}/rest/v1/insights",
        headers={
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        },
        json=checkpoint
    )
    
    if response.status_code == 201:
        return response.json()[0]["id"]
    return None


def trigger_orchestrator(action: str = "resume", task: str = ""):
    """Trigger GitHub Actions orchestrator workflow"""
    
    response = httpx.post(
        f"https://api.github.com/repos/{REPO}/actions/workflows/orchestrator.yml/dispatches",
        headers={
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        },
        json={
            "ref": "main",
            "inputs": {
                "action": action,
                "task": task
            }
        }
    )
    
    return response.status_code == 204


def handoff(task: str, context: str, completed: list, remaining: list):
    """
    Full handoff: save checkpoint + trigger orchestrator
    
    Call this from Claude.ai when:
    - Task requires multiple web searches
    - Task is multi-step and complex
    - You're about to do something token-heavy
    """
    
    print(f"🔄 Initiating handoff to external orchestrator...")
    
    # 1. Save checkpoint
    checkpoint_id = save_handoff_checkpoint(task, context, completed, remaining)
    if checkpoint_id:
        print(f"✅ Checkpoint saved: ID {checkpoint_id}")
    else:
        print("❌ Failed to save checkpoint")
        return False
    
    # 2. Trigger orchestrator
    if trigger_orchestrator("resume"):
        print(f"✅ Orchestrator triggered")
        print(f"\n📍 HANDOFF COMPLETE")
        print(f"   Task: {task}")
        print(f"   Completed: {len(completed)} steps")
        print(f"   Remaining: {len(remaining)} steps")
        print(f"\n   The orchestrator will continue this task externally.")
        print(f"   Check status at: https://github.com/{REPO}/actions")
        return True
    else:
        print("❌ Failed to trigger orchestrator")
        return False


# Quick handoff function for Claude.ai to call
def quick_handoff(task: str, what_done: str, what_next: str):
    """
    Simplified handoff for Claude.ai
    
    Example:
    quick_handoff(
        "Create weekly report",
        "Fetched data, calculated metrics",
        "Generate visualizations, format report, send email"
    )
    """
    completed = [s.strip() for s in what_done.split(",") if s.strip()]
    remaining = [s.strip() for s in what_next.split(",") if s.strip()]
    
    return handoff(task, f"Completed: {what_done}", completed, remaining)


if __name__ == "__main__":
    # Example usage
    if len(sys.argv) > 1:
        action = sys.argv[1]
        if action == "status":
            # Check orchestrator status
            response = httpx.get(
                f"https://api.github.com/repos/{REPO}/actions/runs",
                headers={"Authorization": f"token {GITHUB_TOKEN}"},
                params={"per_page": 5}
            )
            if response.status_code == 200:
                runs = response.json()["workflow_runs"]
                print("Recent orchestrator runs:")
                for run in runs[:5]:
                    print(f"  {run['created_at']} - {run['status']} - {run['conclusion']}")
        elif action == "trigger":
            trigger_orchestrator("resume")
            print("✅ Orchestrator triggered")
    else:
        print("Usage: python handoff.py [status|trigger]")
        print("       Or import and use handoff() / quick_handoff()")
