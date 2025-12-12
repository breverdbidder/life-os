#!/usr/bin/env python3
"""
LANGGRAPH ORCHESTRATOR FOR BIDDEED.AI
=====================================
Connects AI Architect (Claude Opus 4.5) orchestration designs
to Claude Code Mobile/Web/CLI execution.

Author: Claude Opus 4.5 (AI Architect)
Owner: Ariel Shapira, Everest Capital USA
Created: December 12, 2025

Deployment: GitHub Actions (runs every 30 min)
Repository: breverdbidder/life-os
"""

import os
import json
import asyncio
import httpx
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Literal
from enum import Enum

# ============================================================
# CONFIGURATION
# ============================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://mocerqjnksmhcjzxrewo.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Repository mappings
REPOSITORIES = {
    "brevard-bidder-scraper": "breverdbidder/brevard-bidder-scraper",
    "life-os": "breverdbidder/life-os", 
    "brevard-bidder-landing": "breverdbidder/brevard-bidder-landing",
    "spd-site-plan-dev": "breverdbidder/spd-site-plan-dev"
}

# Priority weights for scheduling
PRIORITY_WEIGHTS = {"P0": 100, "P1": 75, "P2": 50, "P3": 25}

# ============================================================
# DATA STRUCTURES
# ============================================================

class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    NEEDS_REVIEW = "needs_review"

class TaskType(str, Enum):
    CODE_FIX = "code_fix"
    FEATURE = "feature"
    REFACTOR = "refactor"
    TEST = "test"
    DOCS = "docs"
    DEPLOY = "deploy"

class ExecutionTarget(str, Enum):
    MOBILE = "claude_code_mobile"
    WEB = "claude_code_web"
    CLI = "claude_code_cli"

@dataclass
class TaskSpecificationFormat:
    """TSF - The contract between AI Architect and Claude Code execution"""
    task_id: str
    langgraph_node: str
    repository: str
    priority: str = "P2"
    task_type: str = "code_fix"
    
    # Specification
    target_file: Optional[str] = None
    objective: str = ""
    context: str = ""
    success_criteria: List[str] = field(default_factory=list)
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    blocks: List[str] = field(default_factory=list)
    
    # Execution config
    sandbox_network: List[str] = field(default_factory=lambda: ["pypi.org", "npmjs.org"])
    timeout_minutes: int = 30
    max_iterations: int = 5
    human_checkpoint: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class WorkflowState:
    """LangGraph workflow state"""
    workflow_id: str
    current_node: Optional[str] = None
    completed_nodes: List[str] = field(default_factory=list)
    pending_nodes: List[str] = field(default_factory=list)
    failed_nodes: List[str] = field(default_factory=list)
    awaiting_human: bool = False
    task_results: Dict[str, Any] = field(default_factory=dict)

# ============================================================
# SUPABASE CLIENT
# ============================================================

class SupabaseClient:
    """Async Supabase client for orchestration state management"""
    
    def __init__(self):
        self.url = SUPABASE_URL
        self.headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
    
    async def _request(self, method: str, endpoint: str, data: dict = None, params: dict = None) -> Any:
        """Make async HTTP request to Supabase"""
        url = f"{self.url}/rest/v1/{endpoint}"
        async with httpx.AsyncClient(verify=False) as client:
            if method == "GET":
                resp = await client.get(url, headers=self.headers, params=params)
            elif method == "POST":
                resp = await client.post(url, headers=self.headers, json=data)
            elif method == "PATCH":
                resp = await client.patch(url, headers=self.headers, json=data, params=params)
            elif method == "DELETE":
                resp = await client.delete(url, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            if resp.status_code >= 400:
                print(f"Supabase error: {resp.status_code} - {resp.text}")
                return None
            
            return resp.json() if resp.text else {}
    
    # ---- Orchestrated Tasks ----
    
    async def get_pending_tasks(self, limit: int = 10) -> List[Dict]:
        """Get pending tasks ordered by priority"""
        return await self._request(
            "GET", "orchestrated_tasks",
            params={"status": "eq.pending", "order": "priority.asc,created_at.asc", "limit": str(limit)}
        ) or []
    
    async def get_blocked_tasks(self) -> List[Dict]:
        """Get tasks that are blocked waiting for dependencies"""
        return await self._request(
            "GET", "orchestrated_tasks",
            params={"status": "eq.blocked"}
        ) or []
    
    async def create_task(self, tsf: TaskSpecificationFormat) -> Dict:
        """Create a new orchestrated task"""
        data = {
            "task_id": tsf.task_id,
            "langgraph_node": tsf.langgraph_node,
            "repository": tsf.repository,
            "priority": tsf.priority,
            "task_type": tsf.task_type,
            "tsf": tsf.to_dict(),
            "depends_on": tsf.depends_on,
            "blocks": tsf.blocks,
            "status": "pending"
        }
        return await self._request("POST", "orchestrated_tasks", data)
    
    async def update_task_status(self, task_id: str, status: str, **kwargs) -> Dict:
        """Update task status and optional fields"""
        data = {"status": status, **kwargs}
        if status == "assigned":
            data["assigned_at"] = datetime.now(timezone.utc).isoformat()
        elif status == "in_progress":
            data["started_at"] = datetime.now(timezone.utc).isoformat()
        elif status in ["success", "failed"]:
            data["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        return await self._request(
            "PATCH", "orchestrated_tasks",
            data=data,
            params={"task_id": f"eq.{task_id}"}
        )
    
    async def get_task(self, task_id: str) -> Optional[Dict]:
        """Get a single task by ID"""
        result = await self._request(
            "GET", "orchestrated_tasks",
            params={"task_id": f"eq.{task_id}"}
        )
        return result[0] if result else None
    
    # ---- Workflow State ----
    
    async def get_workflow_state(self, workflow_id: str) -> Optional[Dict]:
        """Get workflow state"""
        result = await self._request(
            "GET", "langgraph_state",
            params={"workflow_id": f"eq.{workflow_id}"}
        )
        return result[0] if result else None
    
    async def update_workflow_state(self, workflow_id: str, **kwargs) -> Dict:
        """Update workflow state"""
        return await self._request(
            "PATCH", "langgraph_state",
            data=kwargs,
            params={"workflow_id": f"eq.{workflow_id}"}
        )
    
    async def log_transition(self, workflow_id: str, from_node: str, to_node: str, trigger: str, data: dict = None) -> Dict:
        """Log a state transition"""
        return await self._request(
            "POST", "langgraph_transitions",
            data={
                "workflow_id": workflow_id,
                "from_node": from_node,
                "to_node": to_node,
                "trigger": trigger,
                "transition_data": data or {}
            }
        )
    
    # ---- Insights (for logging) ----
    
    async def log_insight(self, title: str, description: str, insight_type: str = "ORCHESTRATION_EVENT") -> Dict:
        """Log orchestration events to insights table"""
        return await self._request(
            "POST", "insights",
            data={
                "user_id": 1,
                "title": title,
                "description": description,
                "insight_type": insight_type,
                "source": "langgraph_orchestrator",
                "status": "Active"
            }
        )

# ============================================================
# LANGGRAPH ORCHESTRATOR
# ============================================================

class LangGraphOrchestrator:
    """
    Main orchestrator that connects AI Architect designs to Claude Code execution.
    
    Flow:
    1. AI Architect designs workflow → creates TSF tasks
    2. Orchestrator assigns tasks to Claude Code Mobile/Web/CLI
    3. Claude Code executes and reports results
    4. Orchestrator updates state and advances workflow
    """
    
    def __init__(self):
        self.db = SupabaseClient()
        self.workflow_id = "biddeed-main-workflow"
    
    async def run_orchestration_cycle(self):
        """
        Main orchestration loop - runs every 30 minutes via GitHub Actions.
        
        Steps:
        1. Check for completed tasks → update workflow state
        2. Unblock tasks whose dependencies are met
        3. Assign pending tasks to Claude Code
        4. Log orchestration activity
        """
        print(f"\n{'='*60}")
        print(f"LANGGRAPH ORCHESTRATION CYCLE - {datetime.now(timezone.utc).isoformat()}")
        print(f"{'='*60}\n")
        
        # Step 1: Process completed tasks
        await self._process_completed_tasks()
        
        # Step 2: Unblock tasks with met dependencies
        await self._unblock_ready_tasks()
        
        # Step 3: Assign pending tasks
        await self._assign_pending_tasks()
        
        # Step 4: Check for human checkpoints
        await self._check_human_checkpoints()
        
        # Step 5: Log cycle completion
        await self._log_cycle_completion()
    
    async def _process_completed_tasks(self):
        """Check for tasks that have completed and update workflow state"""
        print("📊 Checking for completed tasks...")
        
        # Get recently completed tasks (within last hour)
        one_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        
        # This would query tasks completed recently
        # For now, we'll check in_progress tasks that might have finished
        in_progress = await self.db._request(
            "GET", "orchestrated_tasks",
            params={"status": "eq.in_progress"}
        ) or []
        
        for task in in_progress:
            # Check if PR was created (indicates completion)
            if task.get("pr_url"):
                print(f"  ✅ Task {task['task_id']} completed with PR: {task['pr_url']}")
                await self.db.update_task_status(
                    task["task_id"],
                    "success",
                    feedback_sent=False
                )
                
                # Update workflow state
                await self._advance_workflow(task["langgraph_node"], "success")
    
    async def _unblock_ready_tasks(self):
        """Unblock tasks whose dependencies are now met"""
        print("\n🔓 Checking blocked tasks...")
        
        blocked_tasks = await self.db.get_blocked_tasks()
        
        for task in blocked_tasks:
            deps = task.get("depends_on", [])
            if not deps:
                # No dependencies, shouldn't be blocked
                await self.db.update_task_status(task["task_id"], "pending")
                print(f"  📤 Unblocked {task['task_id']} (no dependencies)")
                continue
            
            # Check if all dependencies are complete
            all_complete = True
            for dep_id in deps:
                dep_task = await self.db.get_task(dep_id)
                if not dep_task or dep_task.get("status") != "success":
                    all_complete = False
                    break
            
            if all_complete:
                await self.db.update_task_status(task["task_id"], "pending")
                print(f"  📤 Unblocked {task['task_id']} (dependencies met)")
    
    async def _assign_pending_tasks(self):
        """Assign pending tasks to Claude Code execution targets"""
        print("\n📋 Assigning pending tasks...")
        
        pending = await self.db.get_pending_tasks(limit=5)
        
        for task in pending:
            # Determine best execution target based on task type
            target = self._select_execution_target(task)
            
            await self.db.update_task_status(
                task["task_id"],
                "assigned",
                assigned_to=target
            )
            
            print(f"  📌 Assigned {task['task_id']} → {target}")
            print(f"      Repository: {task['repository']}")
            print(f"      Priority: {task['priority']}")
    
    def _select_execution_target(self, task: Dict) -> str:
        """
        Select best Claude Code target for task.
        
        Rules:
        - P0/P1 critical tasks → CLI (most reliable)
        - Quick fixes → Mobile (can run parallel)
        - Complex features → Web (better steering)
        """
        priority = task.get("priority", "P2")
        task_type = task.get("task_type", "code_fix")
        
        if priority in ["P0", "P1"]:
            return ExecutionTarget.CLI.value
        elif task_type in ["code_fix", "test"]:
            return ExecutionTarget.MOBILE.value
        else:
            return ExecutionTarget.WEB.value
    
    async def _check_human_checkpoints(self):
        """Check for tasks needing human review"""
        print("\n👤 Checking human checkpoints...")
        
        needs_review = await self.db._request(
            "GET", "orchestrated_tasks",
            params={"status": "eq.needs_review"}
        ) or []
        
        if needs_review:
            print(f"  ⚠️  {len(needs_review)} tasks awaiting human review:")
            for task in needs_review:
                print(f"      - {task['task_id']}: {task.get('tsf', {}).get('objective', 'No objective')}")
            
            # Update workflow state
            await self.db.update_workflow_state(
                self.workflow_id,
                awaiting_human=True,
                human_checkpoints=[t["task_id"] for t in needs_review]
            )
    
    async def _advance_workflow(self, completed_node: str, result: str):
        """Advance workflow state after task completion"""
        state = await self.db.get_workflow_state(self.workflow_id)
        if not state:
            return
        
        completed = state.get("completed_nodes", [])
        pending = state.get("pending_nodes", [])
        failed = state.get("failed_nodes", [])
        
        # Update node lists
        if completed_node in pending:
            pending.remove(completed_node)
        
        if result == "success":
            if completed_node not in completed:
                completed.append(completed_node)
        else:
            if completed_node not in failed:
                failed.append(completed_node)
        
        # Determine next node
        next_node = pending[0] if pending else None
        
        await self.db.update_workflow_state(
            self.workflow_id,
            current_node=next_node,
            completed_nodes=completed,
            pending_nodes=pending,
            failed_nodes=failed,
            completed_tasks=len(completed),
            last_transition_at=datetime.now(timezone.utc).isoformat()
        )
        
        # Log transition
        await self.db.log_transition(
            self.workflow_id,
            completed_node,
            next_node or "END",
            result
        )
        
        print(f"\n🔄 Workflow advanced: {completed_node} → {next_node or 'END'}")
    
    async def _log_cycle_completion(self):
        """Log orchestration cycle to insights"""
        state = await self.db.get_workflow_state(self.workflow_id)
        
        pending = await self.db.get_pending_tasks()
        in_progress = await self.db._request(
            "GET", "orchestrated_tasks",
            params={"status": "eq.in_progress"}
        ) or []
        
        summary = (
            f"Cycle completed. "
            f"Workflow: {state.get('current_node', 'N/A')}. "
            f"Pending: {len(pending)}, In Progress: {len(in_progress)}, "
            f"Completed: {state.get('completed_tasks', 0)}"
        )
        
        await self.db.log_insight(
            f"Orchestration Cycle - {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}",
            summary,
            "ORCHESTRATION_CYCLE"
        )
        
        print(f"\n✅ {summary}")

# ============================================================
# TASK CREATION HELPERS
# ============================================================

class TaskFactory:
    """Factory for creating standardized TSF tasks"""
    
    @staticmethod
    def create_beca_fix_task(objective: str, target_file: str = "src/scrapers/beca_manus_v22.py") -> TaskSpecificationFormat:
        return TaskSpecificationFormat(
            task_id=f"beca-fix-{datetime.now().strftime('%Y%m%d%H%M')}",
            langgraph_node="fix_beca_antibot",
            repository="breverdbidder/brevard-bidder-scraper",
            priority="P0",
            task_type="code_fix",
            target_file=target_file,
            objective=objective,
            context="BECA scraper getting blocked by Cloudflare anti-bot detection",
            success_criteria=[
                "Scraper completes 10 test fetches without 403 errors",
                "All existing tests pass",
                "PR created with clear description"
            ],
            blocks=["beca-pipeline-run"]
        )
    
    @staticmethod
    def create_life_os_task(objective: str, target_file: str) -> TaskSpecificationFormat:
        return TaskSpecificationFormat(
            task_id=f"lifeos-{datetime.now().strftime('%Y%m%d%H%M')}",
            langgraph_node="enhance_life_os",
            repository="breverdbidder/life-os",
            priority="P2",
            task_type="feature",
            target_file=target_file,
            objective=objective,
            context="Life OS daily report and tracking system",
            success_criteria=[
                "Feature implemented and working",
                "No regressions in existing functionality",
                "PR created"
            ]
        )
    
    @staticmethod
    def create_landing_task(objective: str) -> TaskSpecificationFormat:
        return TaskSpecificationFormat(
            task_id=f"landing-{datetime.now().strftime('%Y%m%d%H%M')}",
            langgraph_node="update_landing",
            repository="breverdbidder/brevard-bidder-landing",
            priority="P2",
            task_type="feature",
            target_file="src/App.jsx",
            objective=objective,
            context="BidDeed.AI landing page - React + Tailwind",
            success_criteria=[
                "Visual update deployed to Cloudflare Pages preview",
                "No console errors",
                "Mobile responsive"
            ]
        )
    
    @staticmethod
    def create_spd_task(objective: str, stage: int = 1) -> TaskSpecificationFormat:
        return TaskSpecificationFormat(
            task_id=f"spd-stage{stage}-{datetime.now().strftime('%Y%m%d%H%M')}",
            langgraph_node=f"spd_stage_{stage}",
            repository="breverdbidder/spd-site-plan-dev",
            priority="P3",
            task_type="feature",
            objective=objective,
            context=f"SPD Site Plan Development - Stage {stage} of 12",
            success_criteria=[
                f"Stage {stage} agent scaffold complete",
                "Tests passing",
                "PR created"
            ],
            depends_on=[f"spd-stage{stage-1}"] if stage > 1 else []
        )

# ============================================================
# MAIN ENTRY POINT
# ============================================================

async def main():
    """Main entry point for GitHub Actions"""
    orchestrator = LangGraphOrchestrator()
    await orchestrator.run_orchestration_cycle()

if __name__ == "__main__":
    asyncio.run(main())
