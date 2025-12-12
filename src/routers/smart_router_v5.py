"""
BidDeed.AI Smart Router V5
===============================
Multi-tier LLM routing with Gemini 2.5 Flash FREE tier (1M context)

Tiers:
- FREE: gemini-2.5-flash (1M context) - Bulk processing, reports, scraping
- ULTRA_CHEAP: DeepSeek V3.2 ($0.28/1M) - Lien analysis, title search  
- BUDGET: claude-3-haiku - Quick classifications
- PRODUCTION: claude-sonnet - Complex decisions
- CRITICAL: claude-opus - Max bid calculations, final approvals

Author: Ariel Shapira, Solo Founder
Real Estate Developer & Founder, Everest Capital USA
"""

import os
import json
import httpx
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

class RouterTier(Enum):
    FREE = "free"
    ULTRA_CHEAP = "ultra_cheap"
    BUDGET = "budget"
    PRODUCTION = "production"
    CRITICAL = "critical"

@dataclass
class ModelConfig:
    name: str
    provider: str
    max_tokens: int
    context_window: int
    cost_per_1m_input: float
    cost_per_1m_output: float
    
MODELS = {
    RouterTier.FREE: ModelConfig(
        name="gemini-2.5-flash",  # Latest FREE model with 1M context
        provider="google",
        max_tokens=8192,
        context_window=1_000_000,  # 1M context - KEY ADVANTAGE
        cost_per_1m_input=0.0,
        cost_per_1m_output=0.0
    ),
    RouterTier.ULTRA_CHEAP: ModelConfig(
        name="deepseek-chat",  # V3.2
        provider="deepseek",
        max_tokens=8192,
        context_window=128_000,
        cost_per_1m_input=0.28,
        cost_per_1m_output=0.42
    ),
    RouterTier.BUDGET: ModelConfig(
        name="claude-3-haiku-20240307",
        provider="anthropic",
        max_tokens=4096,
        context_window=200_000,
        cost_per_1m_input=0.25,
        cost_per_1m_output=1.25
    ),
    RouterTier.PRODUCTION: ModelConfig(
        name="claude-sonnet-4-20250514",
        provider="anthropic",
        max_tokens=8192,
        context_window=200_000,
        cost_per_1m_input=3.0,
        cost_per_1m_output=15.0
    ),
    RouterTier.CRITICAL: ModelConfig(
        name="claude-opus-4-20250514",
        provider="anthropic",
        max_tokens=8192,
        context_window=200_000,
        cost_per_1m_input=15.0,
        cost_per_1m_output=75.0
    )
}

# Task type to tier mapping
TASK_ROUTING = {
    # FREE tier (Gemini 2.5 Flash - 1M context)
    "report_generation": RouterTier.FREE,
    "bulk_scraping": RouterTier.FREE,
    "data_enrichment": RouterTier.FREE,
    "property_analysis": RouterTier.FREE,
    "document_parsing": RouterTier.FREE,
    "multi_property_batch": RouterTier.FREE,
    
    # ULTRA_CHEAP tier (DeepSeek V3.2)
    "lien_analysis": RouterTier.ULTRA_CHEAP,
    "title_search": RouterTier.ULTRA_CHEAP,
    "legal_document_review": RouterTier.ULTRA_CHEAP,
    
    # BUDGET tier (Haiku)
    "classification": RouterTier.BUDGET,
    "simple_extraction": RouterTier.BUDGET,
    "status_check": RouterTier.BUDGET,
    
    # PRODUCTION tier (Sonnet)
    "complex_decision": RouterTier.PRODUCTION,
    "strategy_analysis": RouterTier.PRODUCTION,
    "market_evaluation": RouterTier.PRODUCTION,
    
    # CRITICAL tier (Opus)
    "max_bid_calculation": RouterTier.CRITICAL,
    "final_approval": RouterTier.CRITICAL,
    "high_value_decision": RouterTier.CRITICAL
}

class SmartRouterV5:
    """
    Smart Router V5 - Routes requests to optimal LLM tier based on task type.
    Key feature: Gemini 2.5 Flash FREE tier with 1M context for bulk operations.
    """
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.usage_stats = {tier: {"requests": 0, "tokens": 0, "cost": 0.0} for tier in RouterTier}
        
    def get_tier_for_task(self, task_type: str) -> RouterTier:
        """Determine optimal tier for given task type."""
        return TASK_ROUTING.get(task_type, RouterTier.BUDGET)
    
    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (4 chars per token average)."""
        return len(text) // 4
    
    def should_use_free_tier(self, prompt: str, task_type: str) -> bool:
        """
        Determine if FREE tier (Gemini 2.5 Flash) should be used.
        Returns True for large context operations that benefit from 1M window.
        """
        token_estimate = self.estimate_tokens(prompt)
        
        # Always use FREE tier for bulk operations
        if task_type in ["report_generation", "bulk_scraping", "data_enrichment", 
                         "multi_property_batch", "document_parsing"]:
            return True
            
        # Use FREE tier for large context (>50K tokens)
        if token_estimate > 50_000:
            return True
            
        return False
    
    async def call_gemini(self, prompt: str, system: str = "") -> Dict[str, Any]:
        """Call Gemini 2.5 Flash API (FREE tier - 1M context)."""
        model = MODELS[RouterTier.FREE].name
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.google_api_key}"
        
        contents = []
        if system:
            contents.append({"role": "user", "parts": [{"text": f"System: {system}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": 8192,
                "temperature": 0.7
            }
        }
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            
        text = result["candidates"][0]["content"]["parts"][0]["text"]
        usage = result.get("usageMetadata", {})
        
        return {
            "content": text,
            "model": model,
            "tier": RouterTier.FREE.value,
            "input_tokens": usage.get("promptTokenCount", 0),
            "output_tokens": usage.get("candidatesTokenCount", 0),
            "cost": 0.0  # FREE tier
        }
    
    async def call_deepseek(self, prompt: str, system: str = "") -> Dict[str, Any]:
        """Call DeepSeek V3.2 API (ULTRA_CHEAP tier)."""
        url = "https://api.deepseek.com/v1/chat/completions"
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "max_tokens": 8192,
            "temperature": 0.7
        }
        
        headers = {"Authorization": f"Bearer {self.deepseek_api_key}"}
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
        usage = result.get("usage", {})
        input_tokens = usage.get("prompt_tokens", 0)
        output_tokens = usage.get("completion_tokens", 0)
        cost = (input_tokens * 0.28 + output_tokens * 0.42) / 1_000_000
        
        return {
            "content": result["choices"][0]["message"]["content"],
            "model": "deepseek-chat",
            "tier": RouterTier.ULTRA_CHEAP.value,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }
    
    async def call_anthropic(self, prompt: str, system: str = "", tier: RouterTier = RouterTier.BUDGET) -> Dict[str, Any]:
        """Call Anthropic API (BUDGET/PRODUCTION/CRITICAL tiers)."""
        url = "https://api.anthropic.com/v1/messages"
        
        model_config = MODELS[tier]
        
        payload = {
            "model": model_config.name,
            "max_tokens": model_config.max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        }
        if system:
            payload["system"] = system
            
        headers = {
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            result = response.json()
            
        usage = result.get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        cost = (input_tokens * model_config.cost_per_1m_input + 
                output_tokens * model_config.cost_per_1m_output) / 1_000_000
        
        return {
            "content": result["content"][0]["text"],
            "model": model_config.name,
            "tier": tier.value,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        }
    
    async def route(self, prompt: str, task_type: str, system: str = "", 
                    force_tier: Optional[RouterTier] = None) -> Dict[str, Any]:
        """
        Route request to optimal LLM tier.
        
        Args:
            prompt: The user prompt
            task_type: Type of task (see TASK_ROUTING)
            system: Optional system prompt
            force_tier: Force specific tier (overrides routing logic)
            
        Returns:
            Response dict with content, model, tier, tokens, and cost
        """
        # Determine tier
        if force_tier:
            tier = force_tier
        elif self.should_use_free_tier(prompt, task_type):
            tier = RouterTier.FREE
        else:
            tier = self.get_tier_for_task(task_type)
            
        # Route to appropriate provider
        if tier == RouterTier.FREE:
            result = await self.call_gemini(prompt, system)
        elif tier == RouterTier.ULTRA_CHEAP:
            result = await self.call_deepseek(prompt, system)
        else:
            result = await self.call_anthropic(prompt, system, tier)
            
        # Track usage
        self.usage_stats[tier]["requests"] += 1
        self.usage_stats[tier]["tokens"] += result["input_tokens"] + result["output_tokens"]
        self.usage_stats[tier]["cost"] += result["cost"]
        
        result["timestamp"] = datetime.utcnow().isoformat()
        return result
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Generate usage report across all tiers."""
        total_requests = sum(s["requests"] for s in self.usage_stats.values())
        total_cost = sum(s["cost"] for s in self.usage_stats.values())
        
        free_requests = self.usage_stats[RouterTier.FREE]["requests"]
        free_percentage = (free_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "total_requests": total_requests,
            "total_cost": round(total_cost, 4),
            "free_tier_percentage": round(free_percentage, 1),
            "tier_breakdown": {
                tier.value: {
                    "requests": stats["requests"],
                    "tokens": stats["tokens"],
                    "cost": round(stats["cost"], 4)
                }
                for tier, stats in self.usage_stats.items()
            },
            "cost_savings_estimate": f"~{int(free_percentage * 0.4)}% saved vs all-paid routing"
        }


# Convenience function for quick routing
async def quick_route(prompt: str, task_type: str = "general") -> str:
    """Quick convenience function for routing."""
    router = SmartRouterV5()
    result = await router.route(prompt, task_type)
    return result["content"]


if __name__ == "__main__":
    import asyncio
    
    async def test_router():
        router = SmartRouterV5()
        
        # Test FREE tier routing
        print("Testing Smart Router V5...")
        print(f"Gemini 2.5 Flash context window: {MODELS[RouterTier.FREE].context_window:,} tokens")
        print(f"Model: {MODELS[RouterTier.FREE].name}")
        
        # Simulate task routing
        test_tasks = [
            ("report_generation", "Generate property report for 123 Main St"),
            ("max_bid_calculation", "Calculate max bid for property with ARV $350K"),
            ("lien_analysis", "Analyze liens for case 2024-CA-001234"),
        ]
        
        for task_type, prompt in test_tasks:
            tier = router.get_tier_for_task(task_type)
            model = MODELS[tier]
            print(f"\n{task_type}: {tier.value} -> {model.name} (${model.cost_per_1m_input}/1M)")
    
    asyncio.run(test_router())
