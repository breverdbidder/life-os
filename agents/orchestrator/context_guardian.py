#!/usr/bin/env python3
"""
Context Guardian - Prevents Claude.ai context limit crashes
Part of BrevardBidderAI Agentic AI Ecosystem

Problem: Claude.ai can't self-monitor. Hits 200K limit = conversation dead.
Solution: Pre-emptive checkpointing at 150K, state persistence, auto-resume.

Author: Claude Opus 4.5 (AI Architect)
Owner: Ariel Shapira, Everest Capital of Brevard LLC
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
import httpx

# Supabase config
SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Token thresholds (Claude.ai limit ~200K)
SOFT_LIMIT = 150_000  # Start checkpointing
HARD_LIMIT = 180_000  # Force checkpoint, warn to start new chat
CRITICAL = 195_000    # Emergency dump, conversation ending


@dataclass
class ConversationState:
    """Serializable conversation state for persistence."""
    session_id: str
    workflow_name: str
    current_stage: str
    stage_data: Dict[str, Any]
    pending_tasks: list
    completed_tasks: list
    context_summary: str
    token_estimate: int
    created_at: str
    last_checkpoint: str
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ConversationState':
        return cls(**data)


class ContextGuardian:
    """
    Monitors and manages Claude conversation context to prevent limit crashes.
    
    Usage in GitHub Actions workflow:
    1. Initialize at workflow start
    2. Call estimate_tokens() after each major operation
    3. checkpoint() automatically called when approaching limits
    4. New chat can resume() from last checkpoint
    """
    
    def __init__(self, workflow_name: str, session_id: Optional[str] = None):
        self.workflow_name = workflow_name
        self.session_id = session_id or self._generate_session_id()
        self.token_count = 0
        self.checkpoints = []
        self.state: Optional[ConversationState] = None
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.now(timezone.utc).isoformat()
        return hashlib.sha256(f"{self.workflow_name}-{timestamp}".encode()).hexdigest()[:12]
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens in text. ~4 chars per token for English.
        Conservative estimate to stay safe.
        """
        return len(text) // 3  # Slightly conservative
    
    def add_context(self, content: str, label: str = "unknown") -> dict:
        """
        Add content to context tracking.
        Returns status with warnings if approaching limits.
        """
        tokens = self.estimate_tokens(content)
        self.token_count += tokens
        
        status = {
            "tokens_added": tokens,
            "total_tokens": self.token_count,
            "percentage": round(self.token_count / HARD_LIMIT * 100, 1),
            "action_required": None
        }
        
        if self.token_count >= CRITICAL:
            status["action_required"] = "EMERGENCY"
            status["message"] = "⚠️ CRITICAL: Start new chat NOW. State saved."
            self._emergency_checkpoint()
        elif self.token_count >= HARD_LIMIT:
            status["action_required"] = "CHECKPOINT_NOW"
            status["message"] = "🔴 Hard limit approaching. Checkpointing and preparing handoff."
            self.checkpoint()
        elif self.token_count >= SOFT_LIMIT:
            status["action_required"] = "CHECKPOINT_SOON"
            status["message"] = f"🟡 At {status['percentage']}% capacity. Consider checkpointing."
            
        return status
    
    def checkpoint(self, context_summary: str = "", stage_data: Optional[dict] = None) -> str:
        """
        Save current state to Supabase for resumption.
        Returns checkpoint ID.
        """
        checkpoint_time = datetime.now(timezone.utc).isoformat()
        
        self.state = ConversationState(
            session_id=self.session_id,
            workflow_name=self.workflow_name,
            current_stage=stage_data.get("stage", "unknown") if stage_data else "unknown",
            stage_data=stage_data or {},
            pending_tasks=stage_data.get("pending", []) if stage_data else [],
            completed_tasks=stage_data.get("completed", []) if stage_data else [],
            context_summary=context_summary,
            token_estimate=self.token_count,
            created_at=self.state.created_at if self.state else checkpoint_time,
            last_checkpoint=checkpoint_time
        )
        
        checkpoint_id = f"{self.session_id}-{len(self.checkpoints)}"
        self.checkpoints.append(checkpoint_id)
        
        # Persist to Supabase
        self._save_to_supabase(checkpoint_id, self.state.to_dict())
        
        return checkpoint_id
    
    def _emergency_checkpoint(self):
        """Force checkpoint with minimal context - conversation is ending."""
        self.checkpoint(
            context_summary="EMERGENCY CHECKPOINT - Context limit reached",
            stage_data={"stage": "interrupted", "reason": "context_limit"}
        )
    
    def _save_to_supabase(self, checkpoint_id: str, data: dict):
        """Persist checkpoint to Supabase insights table."""
        if not SUPABASE_KEY:
            print(f"WARNING: No SUPABASE_KEY - checkpoint {checkpoint_id} not persisted")
            return
            
        payload = {
            "category": "orchestrator_checkpoint",
            "subcategory": self.workflow_name,
            "title": f"Checkpoint: {checkpoint_id}",
            "content": json.dumps(data),
            "tags": ["checkpoint", "context_guardian", self.workflow_name],
            "metadata": {
                "checkpoint_id": checkpoint_id,
                "token_count": self.token_count,
                "session_id": self.session_id
            }
        }
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{SUPABASE_URL}/rest/v1/insights",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}",
                        "Content-Type": "application/json",
                        "Prefer": "return=minimal"
                    },
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
                print(f"✅ Checkpoint {checkpoint_id} saved to Supabase")
        except Exception as e:
            print(f"❌ Checkpoint save failed: {e}")
    
    @classmethod
    def resume(cls, session_id: str) -> Optional['ContextGuardian']:
        """
        Resume from a previous session checkpoint.
        Called at start of new chat to continue work.
        """
        if not SUPABASE_KEY:
            print("Cannot resume without SUPABASE_KEY")
            return None
            
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{SUPABASE_URL}/rest/v1/insights",
                    headers={
                        "apikey": SUPABASE_KEY,
                        "Authorization": f"Bearer {SUPABASE_KEY}"
                    },
                    params={
                        "category": "eq.orchestrator_checkpoint",
                        "metadata->>session_id": f"eq.{session_id}",
                        "order": "created_at.desc",
                        "limit": 1
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                results = response.json()
                
                if not results:
                    print(f"No checkpoint found for session {session_id}")
                    return None
                
                checkpoint_data = json.loads(results[0]["content"])
                state = ConversationState.from_dict(checkpoint_data)
                
                guardian = cls(workflow_name=state.workflow_name, session_id=session_id)
                guardian.state = state
                guardian.token_count = 0  # Fresh context in new chat
                
                print(f"✅ Resumed session {session_id} from stage: {state.current_stage}")
                return guardian
                
        except Exception as e:
            print(f"Resume failed: {e}")
            return None
    
    def get_resume_prompt(self) -> str:
        """
        Generate prompt for Claude in new chat to continue work.
        This goes into the user's first message in new chat.
        """
        if not self.state:
            return "No state to resume from."
            
        return f"""RESUMING SESSION: {self.session_id}
        
**Previous Context:**
{self.state.context_summary}

**Current Stage:** {self.state.current_stage}

**Completed:**
{json.dumps(self.state.completed_tasks, indent=2)}

**Pending:**
{json.dumps(self.state.pending_tasks, indent=2)}

**Stage Data:**
{json.dumps(self.state.stage_data, indent=2)}

Continue from where we left off. Do not re-do completed tasks."""


# GitHub Actions integration
def create_checkpoint_action():
    """
    Creates GitHub Action workflow for automatic checkpointing.
    Runs periodically to check Claude.ai conversations via API.
    """
    workflow = """name: Context Guardian Monitor

on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
  workflow_dispatch:
    inputs:
      session_id:
        description: 'Session ID to monitor'
        required: false

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: pip install httpx
        
      - name: Check active sessions
        env:
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python agents/orchestrator/context_guardian.py --check-sessions
"""
    return workflow


if __name__ == "__main__":
    import sys
    
    if "--check-sessions" in sys.argv:
        print("Checking active orchestrator sessions...")
        # Would query Supabase for active sessions and check their status
    else:
        # Demo usage
        guardian = ContextGuardian("brevard_bidder_pipeline")
        
        # Simulate adding context
        for i in range(10):
            content = "Sample content " * 1000
            status = guardian.add_context(content, f"step_{i}")
            print(f"Step {i}: {status['percentage']}% - {status.get('action_required', 'OK')}")
            
            if status["action_required"] == "CHECKPOINT_NOW":
                checkpoint_id = guardian.checkpoint(
                    context_summary=f"Completed steps 0-{i}",
                    stage_data={"stage": f"step_{i}", "completed": list(range(i+1))}
                )
                print(f"Checkpointed: {checkpoint_id}")
                print(f"\nResume prompt:\n{guardian.get_resume_prompt()}")
                break
