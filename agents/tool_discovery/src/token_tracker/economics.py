"""
Token Economics Tracker
Monitors token usage per workflow for ROI measurement
Part of BidDeed.AI Agentic Architecture

Tracks: Exploration phase (expensive) vs Production phase (cheap)
Target: 76K → 8K tokens (10x reduction after skill extraction)
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional, Literal
from dataclasses import dataclass, asdict
import httpx

SUPABASE_URL = "https://mocerqjnksmhcjzxrewo.supabase.co"
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Model pricing (per 1M tokens, as of Dec 2025)
MODEL_PRICING = {
    "claude-opus-4-5": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-5": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5": {"input": 0.80, "output": 4.00},
    "gemini-2.5-flash": {"input": 0.00, "output": 0.00},  # FREE tier
    "deepseek-v3.2": {"input": 0.28, "output": 0.42},
    "gpt-4o": {"input": 2.50, "output": 10.00},
}


@dataclass
class TokenUsage:
    """Token usage for a single operation"""
    workflow_id: str
    workflow_name: str
    phase: Literal["exploration", "production"]
    model: str
    input_tokens: int
    output_tokens: int
    cached_tokens: int = 0
    tool_calls: int = 0
    timestamp: str = None
    metadata: dict = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens
    
    @property
    def cost_usd(self) -> float:
        """Calculate cost in USD"""
        pricing = MODEL_PRICING.get(self.model, {"input": 0, "output": 0})
        input_cost = (self.input_tokens / 1_000_000) * pricing["input"]
        output_cost = (self.output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost


async def init_token_metrics_table():
    """Create token_metrics table if not exists"""
    sql = """
    CREATE TABLE IF NOT EXISTS token_metrics (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        workflow_id TEXT NOT NULL,
        workflow_name TEXT NOT NULL,
        phase TEXT NOT NULL CHECK (phase IN ('exploration', 'production')),
        model TEXT NOT NULL,
        input_tokens INTEGER NOT NULL,
        output_tokens INTEGER NOT NULL,
        cached_tokens INTEGER DEFAULT 0,
        tool_calls INTEGER DEFAULT 0,
        total_tokens INTEGER GENERATED ALWAYS AS (input_tokens + output_tokens) STORED,
        cost_usd NUMERIC(10, 6),
        metadata JSONB DEFAULT '{}',
        created_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS token_metrics_workflow_idx ON token_metrics(workflow_id);
    CREATE INDEX IF NOT EXISTS token_metrics_phase_idx ON token_metrics(phase);
    CREATE INDEX IF NOT EXISTS token_metrics_created_idx ON token_metrics(created_at DESC);
    """
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            },
            json={"query": sql}
        )
        return response.status_code == 200


async def log_token_usage(usage: TokenUsage) -> dict:
    """Log token usage to Supabase"""
    
    payload = {
        **asdict(usage),
        "cost_usd": usage.cost_usd
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/token_metrics",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "return=representation"
            },
            json=payload
        )
        
        if response.status_code in [200, 201]:
            return {"success": True, "data": response.json()}
        return {"success": False, "error": response.text}


async def get_workflow_metrics(
    workflow_id: Optional[str] = None,
    workflow_name: Optional[str] = None,
    days: int = 30
) -> dict:
    """Get aggregated metrics for a workflow"""
    
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    params = {"created_at": f"gte.{cutoff}"}
    if workflow_id:
        params["workflow_id"] = f"eq.{workflow_id}"
    if workflow_name:
        params["workflow_name"] = f"eq.{workflow_name}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/token_metrics",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            params=params
        )
        
        if response.status_code != 200:
            return {"error": response.text}
        
        records = response.json()
        
        if not records:
            return {"total_runs": 0}
        
        # Aggregate by phase
        exploration = [r for r in records if r["phase"] == "exploration"]
        production = [r for r in records if r["phase"] == "production"]
        
        def aggregate(phase_records):
            if not phase_records:
                return None
            return {
                "runs": len(phase_records),
                "avg_tokens": sum(r["total_tokens"] for r in phase_records) / len(phase_records),
                "total_tokens": sum(r["total_tokens"] for r in phase_records),
                "total_cost": sum(r["cost_usd"] or 0 for r in phase_records),
                "avg_tool_calls": sum(r["tool_calls"] for r in phase_records) / len(phase_records)
            }
        
        exploration_stats = aggregate(exploration)
        production_stats = aggregate(production)
        
        # Calculate skill extraction ROI
        token_reduction = None
        if exploration_stats and production_stats:
            token_reduction = 1 - (production_stats["avg_tokens"] / exploration_stats["avg_tokens"])
        
        return {
            "workflow_id": workflow_id,
            "workflow_name": workflow_name,
            "period_days": days,
            "total_runs": len(records),
            "exploration": exploration_stats,
            "production": production_stats,
            "token_reduction_pct": f"{token_reduction * 100:.1f}%" if token_reduction else None,
            "target_reduction": "90%"  # 10x = 90% reduction
        }


async def get_smart_router_metrics(days: int = 7) -> dict:
    """Get Smart Router V5 tier distribution metrics"""
    
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{SUPABASE_URL}/rest/v1/token_metrics",
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            },
            params={"created_at": f"gte.{cutoff}"}
        )
        
        if response.status_code != 200:
            return {"error": response.text}
        
        records = response.json()
        
        # Categorize by model tier
        free_tier = [r for r in records if r["model"] == "gemini-2.5-flash"]
        cheap_tier = [r for r in records if r["model"] == "deepseek-v3.2"]
        paid_tier = [r for r in records if r["model"] not in ["gemini-2.5-flash", "deepseek-v3.2"]]
        
        total = len(records) or 1
        
        return {
            "period_days": days,
            "total_runs": len(records),
            "tier_distribution": {
                "FREE (gemini-2.5-flash)": f"{len(free_tier) / total * 100:.1f}%",
                "ULTRA_CHEAP (deepseek-v3.2)": f"{len(cheap_tier) / total * 100:.1f}%",
                "PAID (claude/gpt)": f"{len(paid_tier) / total * 100:.1f}%"
            },
            "target": "90% FREE tier",
            "total_cost": sum(r["cost_usd"] or 0 for r in records),
            "free_tier_tokens": sum(r["total_tokens"] for r in free_tier),
            "paid_tier_cost": sum(r["cost_usd"] or 0 for r in paid_tier)
        }


async def compare_exploration_vs_production(workflow_name: str) -> dict:
    """
    Compare exploration phase vs production phase for skill extraction ROI
    This is the key metric: 76K → 8K tokens = 10x reduction
    """
    
    metrics = await get_workflow_metrics(workflow_name=workflow_name, days=90)
    
    if not metrics.get("exploration") or not metrics.get("production"):
        return {
            "workflow": workflow_name,
            "status": "insufficient_data",
            "message": "Need both exploration and production runs to compare"
        }
    
    exp = metrics["exploration"]
    prod = metrics["production"]
    
    return {
        "workflow": workflow_name,
        "exploration_phase": {
            "runs": exp["runs"],
            "avg_tokens": int(exp["avg_tokens"]),
            "avg_cost": f"${exp['total_cost'] / exp['runs']:.4f}"
        },
        "production_phase": {
            "runs": prod["runs"],
            "avg_tokens": int(prod["avg_tokens"]),
            "avg_cost": f"${prod['total_cost'] / prod['runs']:.4f}"
        },
        "improvement": {
            "token_reduction": metrics["token_reduction_pct"],
            "cost_reduction": f"{(1 - prod['total_cost'] / exp['total_cost']) * 100:.1f}%" if exp['total_cost'] > 0 else "N/A",
            "target": "10x reduction (90%)"
        },
        "skill_extraction_roi": "ACHIEVED" if metrics.get("token_reduction_pct", "0%").replace("%", "") and float(metrics.get("token_reduction_pct", "0%").replace("%", "")) >= 80 else "IN_PROGRESS"
    }
