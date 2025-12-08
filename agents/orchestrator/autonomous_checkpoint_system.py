"""
Autonomous Agentic Checkpoint System
Zero human intervention - self-monitoring, self-checkpointing

Deploys to: GitHub Actions (runs every Claude API call)
Storage: Supabase insights table
"""

import anthropic
import asyncio
import json
import time
import os
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

# Supabase config - embedded for autonomous operation
SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1vY2VycWpua3NtaGNqenhyZXdvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ1MzI1MjYsImV4cCI6MjA4MDEwODUyNn0.ySFJIOngWWB0aqYra4PoGFuqcbdHOx1ZV6T9-klKQDw"


@dataclass
class AgentState:
    """Tracks conversation state for checkpointing"""
    session_id: str
    total_tokens: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    last_checkpoint: float = field(default_factory=time.time)
    conversation_history: List[Dict] = field(default_factory=list)
    tool_calls: List[Dict] = field(default_factory=list)
    checkpoints: List[str] = field(default_factory=list)
    web_searches: int = 0
    files_created: int = 0


class TokenMonitorAgent:
    """Monitors token usage - triggers checkpoints at thresholds"""
    
    def __init__(self, threshold: int = 50000):
        self.threshold = threshold
        self.warning_threshold = int(threshold * 0.7)  # 70% warning
    
    def update_from_response(self, state: AgentState, response: Dict) -> None:
        """Update token counts from API response"""
        usage = response.get("usage", {})
        state.input_tokens += usage.get("input_tokens", 0)
        state.output_tokens += usage.get("output_tokens", 0)
        state.total_tokens = state.input_tokens + state.output_tokens
    
    def should_checkpoint(self, state: AgentState) -> bool:
        """Autonomous decision: checkpoint needed?"""
        return state.total_tokens > self.threshold
    
    def should_warn(self, state: AgentState) -> bool:
        """Should we warn about approaching limit?"""
        return state.total_tokens > self.warning_threshold
    
    def get_urgency(self, state: AgentState) -> str:
        """Risk assessment"""
        if state.total_tokens == 0:
            return "LOW"
        ratio = state.total_tokens / self.threshold
        if ratio > 1.5:
            return "CRITICAL"
        elif ratio > 1.0:
            return "HIGH"
        elif ratio > 0.7:
            return "MEDIUM"
        return "LOW"


class EventTriggerAgent:
    """Detects events that should trigger checkpoints"""
    
    CRITICAL_TOOLS = [
        "web_search",
        "web_fetch", 
        "bash_tool",
        "create_file",
        "google_drive_search",
        "google_drive_fetch"
    ]
    
    def __init__(self):
        self.event_history: List[Dict] = []
    
    def detect_events(self, response: Dict) -> List[str]:
        """Detect what happened in response"""
        events = []
        
        if response.get("stop_reason") == "tool_use":
            events.append("tool_use")
        
        # Check content for specific tool calls
        for block in response.get("content", []):
            if block.get("type") == "tool_use":
                tool_name = block.get("name", "unknown")
                events.append(f"tool:{tool_name}")
                
                # Critical tools get special tracking
                if tool_name in self.CRITICAL_TOOLS:
                    events.append(f"critical_tool:{tool_name}")
        
        return events
    
    def should_checkpoint(self, events: List[str], state: AgentState) -> bool:
        """Autonomous decision based on event criticality"""
        # Always checkpoint after web_search (token heavy)
        if any("web_search" in e or "web_fetch" in e for e in events):
            return True
        
        # Checkpoint after file creation
        if any("create_file" in e for e in events):
            return True
        
        # Checkpoint every 5 tool calls
        if len(state.tool_calls) > 0 and len(state.tool_calls) % 5 == 0:
            return True
        
        return False
    
    def log_event(self, event: str) -> None:
        """Track event history"""
        self.event_history.append({
            "event": event,
            "timestamp": time.time()
        })


class StatePersistenceAgent:
    """Persists state to Supabase - autonomous with retry"""
    
    def __init__(self):
        self.retry_count = 3
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    def create_checkpoint(self, state: AgentState, reason: str) -> Optional[str]:
        """Synchronous checkpoint creation with retry"""
        for attempt in range(self.retry_count):
            try:
                # Generate summary
                summary = self._generate_summary(state, reason)
                
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/insights",
                    headers=self.headers,
                    json={
                        "user_id": 1,
                        "insight_type": "SESSION_CHECKPOINT",
                        "title": f"Auto-Checkpoint: {reason}",
                        "description": json.dumps(summary),
                        "priority": self._get_priority(state),
                        "status": "active",
                        "source": "autonomous_orchestrator",
                        "confidence": 1.0
                    },
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    checkpoint_id = result[0]["id"] if isinstance(result, list) else result.get("id")
                    print(f"✅ Checkpoint {checkpoint_id} created: {reason}")
                    return str(checkpoint_id)
                else:
                    print(f"⚠️ Checkpoint failed: {response.status_code} - {response.text}")
            
            except Exception as e:
                print(f"⚠️ Checkpoint attempt {attempt+1} failed: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        print("❌ Checkpoint failed after retries")
        return None
    
    def mark_completed(self, checkpoint_id: str) -> bool:
        """Mark a checkpoint as completed"""
        try:
            response = requests.patch(
                f"{SUPABASE_URL}/rest/v1/insights?id=eq.{checkpoint_id}",
                headers=self.headers,
                json={"status": "completed"},
                timeout=10
            )
            return response.status_code in [200, 204]
        except:
            return False
    
    def get_active_checkpoint(self) -> Optional[Dict]:
        """Get the most recent active checkpoint"""
        try:
            response = requests.get(
                f"{SUPABASE_URL}/rest/v1/insights?insight_type=eq.SESSION_CHECKPOINT&status=eq.active&order=created_at.desc&limit=1",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
        except:
            pass
        return None
    
    def _generate_summary(self, state: AgentState, reason: str) -> Dict:
        """Generate checkpoint summary"""
        recent_tools = [t["name"] for t in state.tool_calls[-5:]] if state.tool_calls else []
        
        return {
            "session_id": state.session_id,
            "reason": reason,
            "tokens": {
                "total": state.total_tokens,
                "input": state.input_tokens,
                "output": state.output_tokens
            },
            "tool_calls": len(state.tool_calls),
            "recent_tools": recent_tools,
            "web_searches": state.web_searches,
            "files_created": state.files_created,
            "checkpoint_count": len(state.checkpoints),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_priority(self, state: AgentState) -> str:
        """Determine checkpoint priority"""
        if state.total_tokens > 80000:
            return "critical"
        elif state.total_tokens > 50000:
            return "high"
        return "medium"


class AutonomousOrchestrator:
    """Master orchestrator - wraps Claude API with autonomous checkpointing"""
    
    def __init__(self, anthropic_api_key: str, session_id: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        
        # Initialize agents
        self.token_agent = TokenMonitorAgent(threshold=50000)
        self.event_agent = EventTriggerAgent()
        self.state_agent = StatePersistenceAgent()
        
        # Initialize state
        self.state = AgentState(
            session_id=session_id or f"sess-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )
        
        # Check for existing checkpoint to resume
        self._check_resume()
    
    def _check_resume(self) -> None:
        """Check if we should resume from a checkpoint"""
        checkpoint = self.state_agent.get_active_checkpoint()
        if checkpoint:
            print(f"📂 Found active checkpoint: {checkpoint['id']}")
            try:
                data = json.loads(checkpoint.get("description", "{}"))
                print(f"   Previous session: {data.get('session_id')}")
                print(f"   Tokens used: {data.get('tokens', {}).get('total', 0)}")
                # Mark it complete since we're starting fresh
                self.state_agent.mark_completed(str(checkpoint["id"]))
                print(f"   ✅ Marked checkpoint {checkpoint['id']} completed")
            except:
                pass
    
    def send_message(
        self,
        messages: List[Dict],
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 8192,
        tools: Optional[List] = None,
        **kwargs
    ) -> Dict:
        """Send message with autonomous monitoring"""
        
        # Update conversation history
        self.state.conversation_history.extend(messages)
        
        # Make API call
        api_kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            **kwargs
        }
        if tools:
            api_kwargs["tools"] = tools
        
        response = self.client.messages.create(**api_kwargs)
        response_dict = response.model_dump()
        
        # Update token counts
        self.token_agent.update_from_response(self.state, response_dict)
        
        # Detect events
        events = self.event_agent.detect_events(response_dict)
        for event in events:
            self.event_agent.log_event(event)
            
            # Track specific events
            if "web_search" in event:
                self.state.web_searches += 1
            if "create_file" in event:
                self.state.files_created += 1
            if event.startswith("tool:"):
                self.state.tool_calls.append({
                    "name": event.replace("tool:", ""),
                    "timestamp": time.time()
                })
        
        # Autonomous checkpoint decisions
        checkpoint_reason = None
        
        # Check token threshold
        if self.token_agent.should_checkpoint(self.state):
            checkpoint_reason = f"token_threshold_{self.state.total_tokens}"
        
        # Check event triggers
        elif self.event_agent.should_checkpoint(events, self.state):
            checkpoint_reason = f"event_trigger_{events[0] if events else 'unknown'}"
        
        # Time-based fallback (5 minutes)
        elif time.time() - self.state.last_checkpoint > 300:
            checkpoint_reason = "time_fallback_5min"
        
        # Execute checkpoint if needed
        if checkpoint_reason:
            checkpoint_id = self.state_agent.create_checkpoint(self.state, checkpoint_reason)
            if checkpoint_id:
                self.state.checkpoints.append(checkpoint_id)
                self.state.last_checkpoint = time.time()
        
        # Warn if approaching limit
        elif self.token_agent.should_warn(self.state):
            urgency = self.token_agent.get_urgency(self.state)
            print(f"⚠️ Token warning: {self.state.total_tokens} ({urgency})")
        
        return response_dict
    
    def get_stats(self) -> Dict:
        """Get current session stats"""
        return {
            "session_id": self.state.session_id,
            "total_tokens": self.state.total_tokens,
            "input_tokens": self.state.input_tokens,
            "output_tokens": self.state.output_tokens,
            "tool_calls": len(self.state.tool_calls),
            "web_searches": self.state.web_searches,
            "files_created": self.state.files_created,
            "checkpoints": len(self.state.checkpoints),
            "urgency": self.token_agent.get_urgency(self.state)
        }


# ============================================
# GitHub Actions Entry Point
# ============================================

def github_action_checkpoint():
    """Called by GitHub Actions to create manual checkpoint"""
    agent = StatePersistenceAgent()
    
    # Get env vars from GitHub Actions
    task = os.environ.get("TASK_DESCRIPTION", "Manual checkpoint")
    tokens = int(os.environ.get("TOKEN_COUNT", 0))
    tools = int(os.environ.get("TOOL_COUNT", 0))
    
    state = AgentState(
        session_id=os.environ.get("SESSION_ID", f"gh-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
        total_tokens=tokens
    )
    state.tool_calls = [{"name": "unknown"}] * tools
    
    checkpoint_id = agent.create_checkpoint(state, task)
    
    if checkpoint_id:
        print(f"::set-output name=checkpoint_id::{checkpoint_id}")
        return 0
    return 1


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--github-action":
        sys.exit(github_action_checkpoint())
    else:
        print("Autonomous Checkpoint System")
        print("Usage:")
        print("  Import AutonomousOrchestrator in your code")
        print("  Or run with --github-action for CI/CD checkpoint")
