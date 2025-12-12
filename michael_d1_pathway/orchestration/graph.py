"""
Michael D1 Pathway - LangGraph Orchestrator
============================================
Main orchestration graph that coordinates all specialized agents.
UF 2027 Primary Target | Anthony Nesty | Class of 2027
"""

from typing import Literal, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import json
import os
from datetime import datetime

from orchestration.state import D1PathwayState, get_initial_state, AgentMessage


# Agent Registry
AGENTS = {
    "supervisor": "Orchestration Supervisor",
    "diet": "Kosher Meal & Diet Preparation Agent",
    "education": "Education Achievement Agent",
    "travel": "School Visit Travel Agent",
    "chabad": "Chabad Contacts & School Information Agent",
    "competitors": "Competitor Swimmers Analysis Agent",
    "engineering": "Engineering Opportunities Agent",
    "meet_prep": "Meet Analysis & Preparation Agent",
    "meet_results": "Meet Results Tracking & Analysis Agent",
    "improvements": "Improvements Tracking & Goals Achievement Agent",
    "school_compare": "School Comparison Agent",
    "uf_recruiting": "UF Recruiting Communications Agent"
}


def route_query(state: D1PathwayState) -> List[str]:
    """
    Intelligent routing to determine which agents should handle the query.
    Returns list of agent keys to activate.
    """
    query = state["query"].lower()
    intent = state.get("intent", "")
    
    agents_to_activate = []
    
    # Keyword-based routing with priority
    routing_rules = {
        # Diet/Nutrition
        ("meal", "diet", "food", "nutrition", "kosher", "keto", "protein", "carb", "macro"): "diet",
        
        # Academic
        ("gpa", "grade", "course", "class", "academic", "school", "homework", "test", "sat", "act"): "education",
        
        # Travel/Visits
        ("visit", "travel", "trip", "schedule", "itinerary", "flight", "hotel"): "travel",
        
        # Chabad/Community
        ("chabad", "rabbi", "jewish", "community", "shabbat", "kosher"): "chabad",
        
        # Competitor Analysis
        ("competitor", "rival", "opponent", "recruit", "class of 2027", "ranking"): "competitors",
        
        # Engineering/Real Estate
        ("engineering", "real estate", "minor", "major", "career", "internship"): "engineering",
        
        # Meet Preparation
        ("prepare", "strategy", "race", "upcoming meet", "warmup", "taper"): "meet_prep",
        
        # Meet Results
        ("result", "time", "split", "performance", "pb", "personal best", "dropped"): "meet_results",
        
        # Improvements/Goals
        ("goal", "improvement", "progress", "target time", "standard", "cut"): "improvements",
        
        # School Comparison
        ("compare", "school", "program", "coach", "facility", "team", "uf", "florida", "texas", "georgia"): "school_compare",
        
        # UF Specific
        ("uf", "florida", "nesty", "gator", "gainesville"): "uf_recruiting"
    }
    
    for keywords, agent in routing_rules.items():
        if any(kw in query for kw in keywords):
            if agent not in agents_to_activate:
                agents_to_activate.append(agent)
    
    # Default to supervisor for complex queries
    if not agents_to_activate:
        agents_to_activate = ["supervisor"]
    
    # Always include improvements agent for performance-related queries
    if any(a in agents_to_activate for a in ["meet_results", "competitors", "meet_prep"]):
        if "improvements" not in agents_to_activate:
            agents_to_activate.append("improvements")
    
    # UF always gets notified for recruiting-related activities
    if any(a in agents_to_activate for a in ["competitors", "school_compare", "travel"]):
        if "uf_recruiting" not in agents_to_activate:
            agents_to_activate.append("uf_recruiting")
    
    return agents_to_activate


def supervisor_node(state: D1PathwayState) -> Dict[str, Any]:
    """
    Supervisor agent that coordinates multi-agent workflows.
    Makes high-level decisions about agent activation and response synthesis.
    """
    query = state["query"]
    active_agents = route_query(state)
    
    message = AgentMessage(
        sender="supervisor",
        receiver="all",
        message_type="activation",
        content={
            "query": query,
            "activated_agents": active_agents,
            "priority": "UF_2027"
        },
        timestamp=datetime.now().isoformat(),
        priority=5
    )
    
    return {
        "active_agents": active_agents,
        "messages": [message],
        "agent_outputs": {"supervisor": {"status": "routing_complete", "agents": active_agents}}
    }


def should_continue(state: D1PathwayState) -> Literal["process_agents", "synthesize"]:
    """Determine if we need to process more agents or synthesize response"""
    if state.get("agent_outputs") and len(state["agent_outputs"]) >= len(state["active_agents"]):
        return "synthesize"
    return "process_agents"


def synthesize_response(state: D1PathwayState) -> Dict[str, Any]:
    """
    Synthesize outputs from all active agents into unified response.
    Prioritizes UF-related information.
    """
    outputs = state.get("agent_outputs", {})
    recommendations = []
    action_items = []
    
    # Gather recommendations from all agents
    for agent, output in outputs.items():
        if isinstance(output, dict):
            recs = output.get("recommendations", [])
            recommendations.extend(recs)
            
            actions = output.get("action_items", [])
            action_items.extend(actions)
    
    # Build response
    response_parts = []
    
    # Always lead with UF-relevant info
    if "uf_recruiting" in outputs:
        uf_output = outputs["uf_recruiting"]
        if isinstance(uf_output, dict) and uf_output.get("content"):
            response_parts.append(f"**UF Update:** {uf_output['content']}")
    
    # Add other agent outputs
    for agent, output in outputs.items():
        if agent != "uf_recruiting" and agent != "supervisor":
            if isinstance(output, dict) and output.get("content"):
                agent_name = AGENTS.get(agent, agent)
                response_parts.append(f"**{agent_name}:** {output['content']}")
    
    response = "\n\n".join(response_parts) if response_parts else "Query processed. No specific recommendations at this time."
    
    return {
        "response": response,
        "recommendations": recommendations,
        "action_items": action_items
    }


def create_d1_pathway_graph() -> StateGraph:
    """
    Create the main LangGraph orchestration graph.
    All agents are imported dynamically.
    """
    # Import agents (lazy import to avoid circular dependencies)
    from agents.diet_agent import diet_agent_node
    from agents.education_agent import education_agent_node
    from agents.travel_agent import travel_agent_node
    from agents.chabad_agent import chabad_agent_node
    from agents.competitors_agent import competitors_agent_node
    from agents.engineering_agent import engineering_agent_node
    from agents.meet_prep_agent import meet_prep_agent_node
    from agents.meet_results_agent import meet_results_agent_node
    from agents.improvements_agent import improvements_agent_node
    from agents.school_compare_agent import school_compare_agent_node
    from agents.uf_recruiting_agent import uf_recruiting_agent_node
    
    # Build graph
    workflow = StateGraph(D1PathwayState)
    
    # Add nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("diet", diet_agent_node)
    workflow.add_node("education", education_agent_node)
    workflow.add_node("travel", travel_agent_node)
    workflow.add_node("chabad", chabad_agent_node)
    workflow.add_node("competitors", competitors_agent_node)
    workflow.add_node("engineering", engineering_agent_node)
    workflow.add_node("meet_prep", meet_prep_agent_node)
    workflow.add_node("meet_results", meet_results_agent_node)
    workflow.add_node("improvements", improvements_agent_node)
    workflow.add_node("school_compare", school_compare_agent_node)
    workflow.add_node("uf_recruiting", uf_recruiting_agent_node)
    workflow.add_node("synthesize", synthesize_response)
    
    # Set entry point
    workflow.set_entry_point("supervisor")
    
    # Add edges from supervisor to all agents (conditional)
    def route_to_agents(state: D1PathwayState) -> List[str]:
        return state.get("active_agents", ["synthesize"])
    
    # Conditional routing from supervisor
    workflow.add_conditional_edges(
        "supervisor",
        route_to_agents,
        {
            "diet": "diet",
            "education": "education",
            "travel": "travel",
            "chabad": "chabad",
            "competitors": "competitors",
            "engineering": "engineering",
            "meet_prep": "meet_prep",
            "meet_results": "meet_results",
            "improvements": "improvements",
            "school_compare": "school_compare",
            "uf_recruiting": "uf_recruiting",
            "supervisor": "synthesize"
        }
    )
    
    # All agents route to synthesize
    for agent in ["diet", "education", "travel", "chabad", "competitors", 
                  "engineering", "meet_prep", "meet_results", "improvements",
                  "school_compare", "uf_recruiting"]:
        workflow.add_edge(agent, "synthesize")
    
    # Synthesize to END
    workflow.add_edge("synthesize", END)
    
    return workflow


def compile_graph():
    """Compile the graph with memory checkpointing"""
    workflow = create_d1_pathway_graph()
    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)


# Main execution
if __name__ == "__main__":
    print("Michael D1 Pathway Orchestrator")
    print("=" * 40)
    print(f"Agents: {len(AGENTS)}")
    print(f"Primary Target: UF 2027 (Anthony Nesty)")
    print("Graph compiled successfully.")
