"""
Agentic Tool Discovery System
Dynamic MCP server discovery, token economics tracking, and skill extraction
"""

from .tool_index.vector_store import discover_tools, index_tool, record_tool_usage
from .token_tracker.economics import TokenUsage, log_token_usage, get_workflow_metrics, get_smart_router_metrics
from .skill_extractor.extractor import ExtractedSkill, analyze_chat_for_skills, extract_and_deploy_skill

__all__ = [
    # Tool Discovery
    "discover_tools",
    "index_tool", 
    "record_tool_usage",
    # Token Economics
    "TokenUsage",
    "log_token_usage",
    "get_workflow_metrics",
    "get_smart_router_metrics",
    # Skill Extraction
    "ExtractedSkill",
    "analyze_chat_for_skills",
    "extract_and_deploy_skill"
]

__version__ = "1.0.0"
