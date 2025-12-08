#!/usr/bin/env python3
"""
LIFE OS ORCHESTRATOR AGENT
Runs OUTSIDE Claude sessions. Controls Worker, Memory, and Health agents.
Enforces checkpoints BEFORE context limits hit.

Deploy to: GitHub Actions (scheduled + webhook triggered)
"""

import os
import json
import httpx
import asyncio
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any

# Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Token limits - conservative to ensure checkpoint before crash
MAX_INPUT_TOKENS = 150000  # Opus limit is 200k, checkpoint at 75%
MAX_OUTPUT_TOKENS = 4000
CHECKPOINT_THRESHOLD = 0.6  # Checkpoint when 60% consumed

@dataclass
class SessionState:
    session_id: str
    task: str
    steps_completed: List[str]
    current_step: str
    next_steps: List[str]
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    artifacts: List[Dict] = None
    status: str = "active"
    
    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = []
    
    def token_usage_ratio(self) -> float:
        return self.total_input_tokens / MAX_INPUT_TOKENS
    
    def should_checkpoint(self) -> bool:
        return self.token_usage_ratio() >= CHECKPOINT_THRESHOLD


class MemoryAgent:
    """Handles all checkpoint operations to Supabase"""
    
    def __init__(self):
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
    
    async def save_checkpoint(self, state: SessionState) -> int:
        """Save checkpoint to Supabase insights table"""
        async with httpx.AsyncClient() as client:
            # First mark any existing active checkpoints as superseded
            await client.patch(
                f"{SUPABASE_URL}/rest/v1/insights",
                params={"insight_type": "eq.SESSION_CHECKPOINT", "status": "eq.active"},
                headers={**self.headers, "Prefer": "return=minimal"},
                json={"status": "superseded"}
            )
            
            # Create new checkpoint
            checkpoint_data = {
                "user_id": 1,
                "insight_type": "SESSION_CHECKPOINT",
                "title": f"Checkpoint - {datetime.now(timezone.utc).strftime('%b %d %I:%M %p')} UTC",
                "description": json.dumps({
                    "session_id": state.session_id,
                    "task": state.task,
                    "steps_completed": state.steps_completed,
                    "current_step": state.current_step,
                    "next_steps": state.next_steps,
                    "tokens_used": state.total_input_tokens,
                    "token_ratio": f"{state.token_usage_ratio():.1%}",
                    "artifacts": state.artifacts
                }),
                "priority": "critical" if state.token_usage_ratio() > 0.7 else "high",
                "status": "active",
                "source": "orchestrator_agent",
                "confidence": state.token_usage_ratio()
            }
            
            response = await client.post(
                f"{SUPABASE_URL}/rest/v1/insights",
                headers={**self.headers, "Prefer": "return=representation"},
                json=checkpoint_data
            )
            
            if response.status_code == 201:
                result = response.json()
                return result[0]["id"] if result else 0
            return 0
    
    async def load_latest_checkpoint(self) -> Optional[SessionState]:
        """Load most recent active checkpoint"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/insights",
                params={
                    "insight_type": "eq.SESSION_CHECKPOINT",
                    "status": "eq.active",
                    "order": "created_at.desc",
                    "limit": 1
                },
                headers=self.headers
            )
            
            if response.status_code == 200 and response.json():
                data = response.json()[0]
                desc = json.loads(data["description"])
                return SessionState(
                    session_id=desc["session_id"],
                    task=desc["task"],
                    steps_completed=desc["steps_completed"],
                    current_step=desc["current_step"],
                    next_steps=desc["next_steps"],
                    total_input_tokens=desc.get("tokens_used", 0),
                    artifacts=desc.get("artifacts", []),
                    status="resuming"
                )
            return None
    
    async def mark_completed(self, session_id: str):
        """Mark session checkpoints as completed"""
        async with httpx.AsyncClient() as client:
            await client.patch(
                f"{SUPABASE_URL}/rest/v1/insights",
                params={"insight_type": "eq.SESSION_CHECKPOINT", "status": "eq.active"},
                headers={**self.headers, "Prefer": "return=minimal"},
                json={"status": "completed", "action_taken": f"completed_{session_id}"}
            )


class HealthAgent:
    """Monitors token usage and system health"""
    
    def __init__(self):
        self.alerts = []
    
    def check_token_health(self, state: SessionState) -> Dict[str, Any]:
        """Analyze token usage and return health status"""
        ratio = state.token_usage_ratio()
        
        health = {
            "status": "healthy",
            "token_ratio": ratio,
            "tokens_used": state.total_input_tokens,
            "tokens_remaining": MAX_INPUT_TOKENS - state.total_input_tokens,
            "action": None
        }
        
        if ratio >= 0.9:
            health["status"] = "critical"
            health["action"] = "FORCE_CHECKPOINT_AND_NEW_SESSION"
        elif ratio >= 0.7:
            health["status"] = "warning"
            health["action"] = "CHECKPOINT_NOW"
        elif ratio >= CHECKPOINT_THRESHOLD:
            health["status"] = "caution"
            health["action"] = "CHECKPOINT_RECOMMENDED"
        
        return health
    
    def log_alert(self, message: str, severity: str = "info"):
        self.alerts.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "severity": severity,
            "message": message
        })


class WorkerAgent:
    """Executes tasks via Claude API"""
    
    def __init__(self):
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    async def execute_step(
        self, 
        step: str, 
        context: str,
        system_prompt: str = None
    ) -> Dict[str, Any]:
        """Execute a single step and return result with token usage"""
        
        if not system_prompt:
            system_prompt = """You are a Worker Agent in the Life OS system.
Execute the given step precisely and concisely.
Focus on the specific task - do not expand scope.
Return actionable results only."""
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                self.api_url,
                headers=self.headers,
                json={
                    "model": "claude-sonnet-4-20250514",  # Use Sonnet for workers (faster, cheaper)
                    "max_tokens": MAX_OUTPUT_TOKENS,
                    "system": system_prompt,
                    "messages": [
                        {"role": "user", "content": f"Context:\n{context}\n\nStep to execute:\n{step}"}
                    ]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "content": data["content"][0]["text"],
                    "input_tokens": data["usage"]["input_tokens"],
                    "output_tokens": data["usage"]["output_tokens"],
                    "stop_reason": data["stop_reason"]
                }
            else:
                return {
                    "success": False,
                    "error": response.text,
                    "input_tokens": 0,
                    "output_tokens": 0
                }


class Orchestrator:
    """Main orchestrator - coordinates all agents"""
    
    def __init__(self):
        self.memory = MemoryAgent()
        self.health = HealthAgent()
        self.worker = WorkerAgent()
        self.state: Optional[SessionState] = None
    
    async def start_session(self, task: str, steps: List[str]) -> str:
        """Start a new task session"""
        session_id = f"sess-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        self.state = SessionState(
            session_id=session_id,
            task=task,
            steps_completed=[],
            current_step=steps[0] if steps else "",
            next_steps=steps[1:] if len(steps) > 1 else []
        )
        
        # Initial checkpoint
        await self.memory.save_checkpoint(self.state)
        print(f"✅ Session started: {session_id}")
        return session_id
    
    async def resume_session(self) -> bool:
        """Resume from latest checkpoint"""
        self.state = await self.memory.load_latest_checkpoint()
        if self.state:
            print(f"✅ Resumed session: {self.state.session_id}")
            print(f"   Task: {self.state.task}")
            print(f"   Completed: {len(self.state.steps_completed)} steps")
            print(f"   Next: {self.state.current_step}")
            return True
        print("⚠️ No active checkpoint found")
        return False
    
    async def execute_task(self, task: str, steps: List[str]):
        """Execute a multi-step task with automatic checkpointing"""
        
        # Check for existing session to resume
        existing = await self.memory.load_latest_checkpoint()
        if existing and existing.task == task:
            print(f"📍 Found existing session for this task, resuming...")
            self.state = existing
            steps = [existing.current_step] + existing.next_steps
        else:
            await self.start_session(task, steps)
        
        context = f"Task: {task}\n\nPrevious steps completed:\n"
        context += "\n".join(f"- {s}" for s in self.state.steps_completed) or "None yet"
        
        for i, step in enumerate(steps):
            self.state.current_step = step
            self.state.next_steps = steps[i+1:] if i+1 < len(steps) else []
            
            print(f"\n🔄 Step {i+1}/{len(steps)}: {step}")
            
            # Execute step
            result = await self.worker.execute_step(step, context)
            
            if result["success"]:
                # Update token counts
                self.state.total_input_tokens += result["input_tokens"]
                self.state.total_output_tokens += result["output_tokens"]
                
                # Add to completed
                self.state.steps_completed.append(step)
                context += f"\n\nStep '{step}' result:\n{result['content'][:500]}..."
                
                print(f"   ✅ Completed ({result['input_tokens']} in / {result['output_tokens']} out)")
                
                # Health check after EVERY step
                health = self.health.check_token_health(self.state)
                print(f"   📊 Health: {health['status']} ({health['token_ratio']:.1%} tokens used)")
                
                # Checkpoint based on health
                if health["action"]:
                    checkpoint_id = await self.memory.save_checkpoint(self.state)
                    print(f"   💾 Checkpoint saved: ID {checkpoint_id}")
                    
                    if health["action"] == "FORCE_CHECKPOINT_AND_NEW_SESSION":
                        print(f"\n⚠️ CONTEXT LIMIT APPROACHING - Session saved, restart required")
                        return {
                            "status": "checkpoint_required",
                            "session_id": self.state.session_id,
                            "completed": len(self.state.steps_completed),
                            "remaining": len(self.state.next_steps)
                        }
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                await self.memory.save_checkpoint(self.state)
                return {"status": "error", "step": step, "error": result.get("error")}
        
        # All steps completed
        await self.memory.mark_completed(self.state.session_id)
        print(f"\n✅ Task completed: {task}")
        return {"status": "completed", "session_id": self.state.session_id}


async def main():
    """Example usage"""
    orchestrator = Orchestrator()
    
    # Example: Resume or start new
    if await orchestrator.resume_session():
        # Continue existing task
        result = await orchestrator.execute_task(
            orchestrator.state.task,
            [orchestrator.state.current_step] + orchestrator.state.next_steps
        )
    else:
        # Start new task
        result = await orchestrator.execute_task(
            task="Create Life OS weekly report",
            steps=[
                "Fetch this week's task completions from Supabase",
                "Calculate productivity metrics",
                "Identify patterns and blockers",
                "Generate recommendations",
                "Format into report"
            ]
        )
    
    print(f"\nResult: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
