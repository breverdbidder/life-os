"""
Michael D1 Pathway - Main Entry Point
======================================
LangGraph Multi-Agent Orchestration System
Target: UF 2027 | Coach Anthony Nesty | Class of 2027

Author: Claude Opus 4.5 (AI Architect)
Version: 1.0.0
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestration.state import get_initial_state, D1PathwayState
from orchestration.graph import compile_graph, AGENTS
from config.settings import CONFIG, get_config


def run_query(query: str, current_times: dict = None) -> dict:
    """
    Run a query through the multi-agent system.
    
    Args:
        query: User question or request
        current_times: Optional dict of current swim times
        
    Returns:
        Response dict with results from all relevant agents
    """
    # Initialize state
    state = get_initial_state()
    state["query"] = query
    
    if current_times:
        for event, time in current_times.items():
            state["current_times"][event] = {
                "time_seconds": time,
                "time_display": _format_time(time)
            }
    
    # Compile and run graph
    try:
        graph = compile_graph()
        result = graph.invoke(state)
        
        return {
            "success": True,
            "query": query,
            "response": result.get("response", ""),
            "recommendations": result.get("recommendations", []),
            "action_items": result.get("action_items", []),
            "agents_used": result.get("active_agents", []),
            "agent_outputs": result.get("agent_outputs", {}),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "query": query,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def _format_time(seconds: float) -> str:
    """Format seconds to display time"""
    if seconds >= 60:
        mins = int(seconds // 60)
        secs = seconds % 60
        return f"{mins}:{secs:05.2f}"
    return f"{seconds:.2f}"


def print_system_info():
    """Print system information"""
    print("=" * 60)
    print("MICHAEL D1 PATHWAY")
    print("LangGraph Multi-Agent Orchestration System")
    print("=" * 60)
    print(f"Version: {CONFIG['system']['version']}")
    print(f"Primary Target: {CONFIG['primary_target']['school']}")
    print(f"Class: {CONFIG['primary_target']['class']}")
    print(f"Coach: {CONFIG['primary_target']['coach']}")
    print(f"Agents: {len(AGENTS)}")
    print("-" * 60)
    for key, name in AGENTS.items():
        print(f"  • {name}")
    print("=" * 60)


def demo():
    """Run demo queries"""
    print("\n📊 Running Demo Queries...\n")
    
    # Sample current times
    current_times = {
        "50 Free": 21.5,
        "100 Free": 47.8,
        "200 Free": 102.5,
        "100 Fly": 52.3,
        "100 Back": 54.1
    }
    
    demo_queries = [
        "What are my UF recruiting prospects?",
        "What should I eat today?",
        "How do I compare to other Class of 2027 recruits?",
        "What are my improvement goals?"
    ]
    
    for query in demo_queries:
        print(f"\n❓ Query: {query}")
        print("-" * 40)
        result = run_query(query, current_times)
        
        if result["success"]:
            print(f"✅ Agents: {', '.join(result['agents_used'])}")
            print(f"📝 Response: {result['response'][:200]}...")
            if result["recommendations"]:
                print(f"💡 Recommendations: {result['recommendations'][0]}")
        else:
            print(f"❌ Error: {result['error']}")


if __name__ == "__main__":
    print_system_info()
    
    if "--demo" in sys.argv:
        demo()
    elif len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = run_query(query)
        print(json.dumps(result, indent=2))
    else:
        print("\nUsage:")
        print("  python main.py --demo              # Run demo queries")
        print("  python main.py 'Your question'    # Run single query")
