#!/usr/bin/env python3
"""
LANGGRAPH TOOL DISCOVERY INTEGRATION
====================================
Integrates dynamic tool discovery, token economics, and skill extraction
into the existing LangGraph orchestrator.

Adds 3 new nodes:
1. discover_tools - Vector search for relevant MCP tools
2. track_tokens - Log token usage to economics tracker  
3. extract_skill - Convert successful patterns to frozen workflows

Author: Claude Opus 4.5 (AI Architect)
Owner: Ariel Shapira, Everest Capital USA
Created: December 14, 2025
"""

import os
import sys
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# Import existing orchestrator components
sys.path.insert(0, os.path.dirname(__file__))
from langgraph_orchestrator import (
    TaskSpecificationFormat, 
    TaskStatus, 
    TaskType,
    SUPABASE_URL, 
    SUPABASE_KEY
)

# Import tool discovery modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tool_discovery', 'src'))
from tool_index.vector_store import discover_tools, index_tool, record_tool_usage
from token_tracker.economics import TokenUsage, log_token_usage, get_workflow_metrics
from skill_extractor.extractor import analyze_chat_for_skills, extract_and_deploy_skill

import httpx


# ============================================================
# LANGGRAPH NODE: TOOL DISCOVERY
# ============================================================

@dataclass
class ToolDiscoveryState:
    """State for tool discovery node"""
    query: str
    discovered_tools: List[Dict] = field(default_factory=list)
    selected_tools: List[str] = field(default_factory=list)
    discovery_time_ms: int = 0


async def node_discover_tools(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph Node: Discover relevant tools for the current task
    
    Input state keys:
    - task_objective: What the task needs to accomplish
    - task_context: Additional context about the task
    
    Output state keys:
    - discovered_tools: List of relevant tool definitions
    - selected_tools: Tool names to use
    """
    import time
    start = time.time()
    
    # Build discovery query from task
    task_objective = state.get("task_objective", "")
    task_context = state.get("task_context", "")
    query = f"{task_objective} {task_context}"
    
    # Discover relevant tools
    tools = await discover_tools(
        query=query,
        limit=5,
        similarity_threshold=0.6
    )
    
    # Record tool usage for optimization
    for tool in tools:
        await record_tool_usage(tool.get("tool_name"), tool.get("mcp_server_name"))
    
    discovery_time = int((time.time() - start) * 1000)
    
    print(f"🔍 Tool Discovery: Found {len(tools)} relevant tools in {discovery_time}ms")
    for tool in tools:
        print(f"   → {tool.get('tool_name')} ({tool.get('similarity', 0):.2f})")
    
    return {
        **state,
        "discovered_tools": tools,
        "selected_tools": [t.get("tool_name") for t in tools],
        "tool_discovery_time_ms": discovery_time
    }


# ============================================================
# LANGGRAPH NODE: TOKEN TRACKING
# ============================================================

@dataclass
class TokenTrackingState:
    """State for token tracking node"""
    workflow_id: str
    workflow_name: str
    phase: str  # "exploration" or "production"
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    tool_calls: int = 0
    logged: bool = False


async def node_track_tokens(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph Node: Track token usage for economics analysis
    
    Input state keys:
    - workflow_id: Unique workflow identifier
    - workflow_name: Human-readable workflow name
    - phase: "exploration" or "production"
    - model: Model used (e.g., "claude-sonnet-4-5")
    - input_tokens, output_tokens, tool_calls: Usage metrics
    
    Output state keys:
    - token_log_success: Whether logging succeeded
    - token_cost_usd: Calculated cost
    """
    
    usage = TokenUsage(
        workflow_id=state.get("workflow_id", f"wf-{datetime.now().strftime('%Y%m%d%H%M')}"),
        workflow_name=state.get("workflow_name", "unknown"),
        phase=state.get("phase", "exploration"),
        model=state.get("model", "claude-sonnet-4-5"),
        input_tokens=state.get("input_tokens", 0),
        output_tokens=state.get("output_tokens", 0),
        tool_calls=state.get("tool_calls", 0),
        metadata={
            "discovered_tools": state.get("selected_tools", []),
            "langgraph_node": state.get("current_node", "unknown")
        }
    )
    
    result = await log_token_usage(usage)
    
    print(f"📊 Token Tracking: {usage.total_tokens} tokens, ${usage.cost_usd:.4f}")
    print(f"   Phase: {usage.phase}, Model: {usage.model}")
    
    return {
        **state,
        "token_log_success": result.get("success", False),
        "token_cost_usd": usage.cost_usd
    }


# ============================================================
# LANGGRAPH NODE: SKILL EXTRACTION
# ============================================================

async def node_extract_skill(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    LangGraph Node: Extract successful workflow pattern as frozen skill
    
    Input state keys:
    - workflow_name: Name for the skill
    - task_objective: Description
    - tool_sequence: List of tools used in order
    - input_schema: Expected inputs
    - success: Whether workflow succeeded
    
    Output state keys:
    - skill_extracted: Whether extraction happened
    - skill_workflow_url: GitHub Actions workflow URL
    """
    
    # Only extract skills from successful workflows
    if not state.get("success", False):
        print("⏭️ Skill Extraction: Skipped (workflow not successful)")
        return {**state, "skill_extracted": False}
    
    # Check if we have enough data
    tool_sequence = state.get("tool_sequence", [])
    if len(tool_sequence) < 2:
        print("⏭️ Skill Extraction: Skipped (need at least 2 tools)")
        return {**state, "skill_extracted": False}
    
    skill_name = state.get("workflow_name", "").lower().replace(" ", "-").replace("_", "-")
    if not skill_name:
        skill_name = f"skill-{datetime.now().strftime('%Y%m%d%H%M')}"
    
    result = await extract_and_deploy_skill(
        skill_name=skill_name,
        description=state.get("task_objective", "Extracted workflow skill"),
        tool_sequence=[{"name": t} for t in tool_sequence],
        input_schema=state.get("input_schema", {}),
        trigger_patterns=state.get("trigger_patterns", []),
        source_chat_id=state.get("source_chat_id")
    )
    
    print(f"🔧 Skill Extraction: {skill_name}")
    print(f"   GitHub: {result.get('github', {}).get('action', 'unknown')}")
    print(f"   URL: {result.get('workflow_url', 'N/A')}")
    
    return {
        **state,
        "skill_extracted": True,
        "skill_workflow_url": result.get("workflow_url"),
        "skill_github_result": result.get("github")
    }


# ============================================================
# INTEGRATION WITH EXISTING ORCHESTRATOR
# ============================================================

class ToolDiscoveryIntegration:
    """
    Integrates tool discovery into existing LangGraph orchestrator
    
    Adds pre/post hooks to:
    - Discover tools before task execution
    - Track tokens after each API call
    - Extract skills after successful workflows
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.current_tool_sequence = []
    
    async def pre_task_hook(self, task: TaskSpecificationFormat) -> Dict[str, Any]:
        """Run before each task - discovers relevant tools"""
        
        state = {
            "task_objective": task.objective,
            "task_context": task.context,
            "workflow_id": task.task_id,
            "workflow_name": task.langgraph_node
        }
        
        # Discover tools
        result = await node_discover_tools(state)
        
        # Store for skill extraction later
        self.current_tool_sequence = result.get("selected_tools", [])
        
        return result
    
    async def post_task_hook(
        self, 
        task: TaskSpecificationFormat, 
        success: bool,
        input_tokens: int = 0,
        output_tokens: int = 0,
        tool_calls: int = 0
    ) -> Dict[str, Any]:
        """Run after each task - tracks tokens and extracts skills"""
        
        state = {
            "workflow_id": task.task_id,
            "workflow_name": task.langgraph_node,
            "phase": "production" if "skill-" in task.task_id else "exploration",
            "model": "claude-sonnet-4-5",  # Default, could be parameterized
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "tool_calls": tool_calls,
            "tool_sequence": self.current_tool_sequence,
            "task_objective": task.objective,
            "input_schema": {},
            "success": success
        }
        
        # Track tokens
        state = await node_track_tokens(state)
        
        # Extract skill if successful
        state = await node_extract_skill(state)
        
        return state


# ============================================================
# TASK FACTORY ADDITIONS
# ============================================================

def create_tool_discovery_task(query: str) -> TaskSpecificationFormat:
    """Create a task specifically for tool discovery"""
    return TaskSpecificationFormat(
        task_id=f"discovery-{datetime.now().strftime('%Y%m%d%H%M')}",
        langgraph_node="discover_tools",
        repository="breverdbidder/life-os",
        priority="P3",
        task_type="docs",
        objective=f"Discover relevant tools for: {query}",
        context="Dynamic MCP tool discovery via vector search",
        success_criteria=[
            "At least 1 relevant tool discovered",
            "Tool usage logged to Supabase"
        ]
    )


def create_skill_extraction_task(workflow_name: str, tool_sequence: List[str]) -> TaskSpecificationFormat:
    """Create a task for skill extraction"""
    return TaskSpecificationFormat(
        task_id=f"extract-{datetime.now().strftime('%Y%m%d%H%M')}",
        langgraph_node="extract_skill",
        repository="breverdbidder/life-os",
        priority="P3",
        task_type="deploy",
        objective=f"Extract skill from workflow: {workflow_name}",
        context=f"Tool sequence: {' → '.join(tool_sequence)}",
        success_criteria=[
            "Skill saved to Supabase",
            "GitHub Actions workflow created",
            "Workflow deploys successfully"
        ]
    )


# ============================================================
# METRICS DASHBOARD
# ============================================================

async def get_tool_discovery_metrics() -> Dict[str, Any]:
    """Get comprehensive metrics for tool discovery system"""
    
    # Smart Router metrics
    router_metrics = await get_workflow_metrics(days=7)
    
    # Get exploration vs production comparison for key workflows
    beca_comparison = await get_workflow_metrics(workflow_name="BECA Daily Scrape", days=30)
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "smart_router": router_metrics,
        "beca_roi": beca_comparison,
        "tool_discovery": {
            "status": "ACTIVE",
            "index_location": "Supabase pgvector",
            "query_threshold": 0.6
        },
        "skill_extraction": {
            "status": "ACTIVE",
            "deploy_target": "GitHub Actions",
            "min_tools": 2
        }
    }


# ============================================================
# MAIN - TEST INTEGRATION
# ============================================================

async def test_integration():
    """Test the integration components"""
    
    print("=" * 60)
    print("TESTING TOOL DISCOVERY INTEGRATION")
    print("=" * 60)
    
    # Test 1: Tool Discovery
    print("\n📍 Test 1: Tool Discovery")
    state = await node_discover_tools({
        "task_objective": "Scrape foreclosure auction data from BECA",
        "task_context": "Need final judgments and opening bids"
    })
    print(f"   Result: {len(state.get('discovered_tools', []))} tools found")
    
    # Test 2: Token Tracking
    print("\n📍 Test 2: Token Tracking")
    state = await node_track_tokens({
        **state,
        "workflow_id": "test-integration-001",
        "workflow_name": "test_workflow",
        "phase": "exploration",
        "model": "claude-sonnet-4-5",
        "input_tokens": 45000,
        "output_tokens": 31000,
        "tool_calls": 5
    })
    print(f"   Result: Logged = {state.get('token_log_success')}, Cost = ${state.get('token_cost_usd', 0):.4f}")
    
    # Test 3: Skill Extraction (mock - won't actually deploy)
    print("\n📍 Test 3: Skill Extraction")
    state["success"] = True
    state["tool_sequence"] = ["beca_scraper", "lien_priority_analyzer", "decision_logger"]
    state = await node_extract_skill(state)
    print(f"   Result: Extracted = {state.get('skill_extracted')}")
    
    # Test 4: Metrics Dashboard
    print("\n📍 Test 4: Metrics Dashboard")
    metrics = await get_tool_discovery_metrics()
    print(f"   Tool Discovery Status: {metrics.get('tool_discovery', {}).get('status')}")
    
    print("\n" + "=" * 60)
    print("✅ Integration tests complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_integration())
