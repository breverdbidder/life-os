"""
Michael D1 Pathway V2.1 - Bridge API Endpoints
==============================================

This module defines the API layer that connects Claude AI Chat
to the LangGraph Orchestrator.

Architecture:
    Claude.ai Chat → Bridge API → LangGraph Orchestrator → 12 Agents → Response

Endpoints:
    POST /api/query          - Main query endpoint
    POST /api/meet-prep      - Generate meet prep document
    GET  /api/dashboard      - Get UF 2027 dashboard
    GET  /api/agents/status  - Get all agent statuses
    POST /api/results        - Record meet results
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, date
from dataclasses import dataclass, asdict
from enum import Enum
import json


# ============================================================
# API REQUEST/RESPONSE MODELS
# ============================================================

@dataclass
class APIRequest:
    """Base API request structure"""
    message: str
    context: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class APIResponse:
    """Base API response structure"""
    success: bool
    data: Dict[str, Any]
    agents_consulted: List[str]
    processing_time_ms: float
    timestamp: str = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return asdict(self)


class IntentType(Enum):
    """Supported intent types for routing"""
    QUERY = "query"
    MEET_PREP = "meet_prep"
    MOTIVATION = "motivation"
    RESULTS = "results"
    DASHBOARD = "dashboard"
    SCHOOL_COMPARE = "school_compare"
    COMPETITOR = "competitor"
    SCHEDULE = "schedule"
    NUTRITION = "nutrition"
    TRAVEL = "travel"
    EDUCATION = "education"
    ENGINEERING = "engineering"


# ============================================================
# BRIDGE API CLASS
# ============================================================

class BridgeAPI:
    """
    API layer connecting Claude Chat to LangGraph Orchestrator.
    
    Implements:
    - Request interpretation
    - Intent routing
    - Agent coordination
    - Response synthesis
    - Error handling
    - Latency monitoring
    """
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.request_timeout_ms = 30000  # 30 second timeout
        self.session_contexts: Dict[str, Dict] = {}  # Session state persistence
    
    # ============================================================
    # MAIN ENDPOINTS
    # ============================================================
    
    def query(self, request: APIRequest) -> APIResponse:
        """
        POST /api/query
        
        Main query endpoint - routes to appropriate agents based on intent.
        
        Args:
            request: APIRequest with user message and optional context
            
        Returns:
            APIResponse with agent outputs and metadata
        """
        start_time = datetime.now()
        
        try:
            # Process through orchestrator bridge
            result = self.orchestrator.process_query(request.message)
            
            # Calculate processing time
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update session context if provided
            if request.session_id:
                self._update_session_context(request.session_id, result)
            
            return APIResponse(
                success=True,
                data=result["response"],
                agents_consulted=result["response"]["agents_consulted"],
                processing_time_ms=elapsed
            )
            
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            return APIResponse(
                success=False,
                data={},
                agents_consulted=[],
                processing_time_ms=elapsed,
                error=str(e)
            )
    
    def generate_meet_prep(self, meet_name: str, meet_date: date) -> APIResponse:
        """
        POST /api/meet-prep
        
        Generate comprehensive meet preparation document.
        
        Args:
            meet_name: Name of the meet
            meet_date: Date of the meet
            
        Returns:
            APIResponse with meet prep document content
        """
        start_time = datetime.now()
        
        try:
            # Get the meet prep motivation agent
            agent = self.orchestrator.agents["meet_prep_motivation"]
            
            # Generate the document
            doc = agent.generate_meet_document(meet_name, meet_date)
            
            # Also get supporting data from other agents
            context = {"meet": meet_name}
            nutrition = self.orchestrator.agents["kosher_diet"].process("", context)
            travel = self.orchestrator.agents["travel"].process("", context)
            competitors = self.orchestrator.agents["competitor_analysis"].process("", context)
            
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            
            return APIResponse(
                success=True,
                data={
                    "document_markdown": doc,
                    "meet_name": meet_name,
                    "meet_date": meet_date.isoformat(),
                    "supporting_data": {
                        "nutrition": nutrition,
                        "travel": travel,
                        "competitors": competitors
                    }
                },
                agents_consulted=["meet_prep_motivation", "kosher_diet", "travel", "competitor_analysis"],
                processing_time_ms=elapsed
            )
            
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            return APIResponse(
                success=False,
                data={},
                agents_consulted=[],
                processing_time_ms=elapsed,
                error=str(e)
            )
    
    def get_dashboard(self) -> APIResponse:
        """
        GET /api/dashboard
        
        Get UF 2027 focused dashboard with all agent insights.
        
        Returns:
            APIResponse with comprehensive dashboard data
        """
        start_time = datetime.now()
        
        try:
            dashboard = self.orchestrator.get_uf_dashboard()
            
            # Enrich with agent insights
            goals = self.orchestrator.agents["goals"].process("", {})
            schedule = self.orchestrator.agents["events_schedule"].process("", {})
            school = self.orchestrator.agents["school_comparison"].process("", {"school": "UF"})
            
            dashboard["goals_analysis"] = goals
            dashboard["upcoming_meets"] = schedule
            dashboard["school_fit"] = school
            
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            
            return APIResponse(
                success=True,
                data=dashboard,
                agents_consulted=["goals", "events_schedule", "school_comparison"],
                processing_time_ms=elapsed
            )
            
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            return APIResponse(
                success=False,
                data={},
                agents_consulted=[],
                processing_time_ms=elapsed,
                error=str(e)
            )
    
    def get_agent_status(self) -> APIResponse:
        """
        GET /api/agents/status
        
        Get status of all 12 agents.
        
        Returns:
            APIResponse with agent status information
        """
        start_time = datetime.now()
        
        agent_statuses = {}
        for name, agent in self.orchestrator.agents.items():
            agent_statuses[name] = {
                "name": name,
                "status": "active",
                "ml_model": agent.ml_model.model_type.value,
                "last_prediction_confidence": 0.85  # Would be tracked in production
            }
        
        elapsed = (datetime.now() - start_time).total_seconds() * 1000
        
        return APIResponse(
            success=True,
            data={
                "total_agents": len(agent_statuses),
                "agents": agent_statuses,
                "orchestrator_version": "2.1"
            },
            agents_consulted=[],
            processing_time_ms=elapsed
        )
    
    def record_result(self, event: str, time: float, meet: str) -> APIResponse:
        """
        POST /api/results
        
        Record a new meet result and trigger agent updates.
        
        Args:
            event: Event name (e.g., "100 Free")
            time: Time in seconds
            meet: Meet name
            
        Returns:
            APIResponse with update confirmation
        """
        start_time = datetime.now()
        
        try:
            # Get current PB
            old_pb = self.orchestrator.state.get("personal_bests", {}).get(event, 999)
            is_pr = time < old_pb
            
            # Update state if PR
            if is_pr:
                pbs = self.orchestrator.state.get("personal_bests", {})
                pbs[event] = time
                self.orchestrator.state.set("personal_bests", pbs, "api")
            
            # Get updated analysis from agents
            results_analysis = self.orchestrator.agents["meet_results"].process("", {"event": event})
            goals_update = self.orchestrator.agents["goals"].process("", {})
            
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            
            return APIResponse(
                success=True,
                data={
                    "event": event,
                    "time": time,
                    "meet": meet,
                    "is_pr": is_pr,
                    "improvement": round(old_pb - time, 2) if is_pr else 0,
                    "results_analysis": results_analysis,
                    "goals_update": goals_update
                },
                agents_consulted=["meet_results", "goals"],
                processing_time_ms=elapsed
            )
            
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds() * 1000
            return APIResponse(
                success=False,
                data={},
                agents_consulted=[],
                processing_time_ms=elapsed,
                error=str(e)
            )
    
    # ============================================================
    # SESSION MANAGEMENT
    # ============================================================
    
    def _update_session_context(self, session_id: str, result: Dict) -> None:
        """Update session context for conversation persistence"""
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = {
                "history": [],
                "last_intent": None,
                "last_agents": []
            }
        
        context = self.session_contexts[session_id]
        context["history"].append({
            "timestamp": datetime.now().isoformat(),
            "intent": result["interpretation"]["primary_intent"],
            "agents": result["response"]["agents_consulted"]
        })
        context["last_intent"] = result["interpretation"]["primary_intent"]
        context["last_agents"] = result["response"]["agents_consulted"]
        
        # Keep only last 20 interactions
        if len(context["history"]) > 20:
            context["history"] = context["history"][-20:]
    
    def get_session_context(self, session_id: str) -> Optional[Dict]:
        """Get session context for a given session ID"""
        return self.session_contexts.get(session_id)


# ============================================================
# CLOUDFLARE WORKERS HANDLER (for deployment)
# ============================================================

def create_cloudflare_handler():
    """
    Create a handler compatible with Cloudflare Workers.
    
    This would be used for edge deployment of the API.
    """
    handler_code = '''
// Cloudflare Worker for Michael D1 Agents API
// Deploy to: api.biddeed.ai/michael-d1/

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    
    // CORS headers
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    };
    
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }
    
    // Route to appropriate handler
    if (path === '/api/query' && request.method === 'POST') {
      const body = await request.json();
      // Forward to orchestrator (would call Python backend or edge function)
      return new Response(JSON.stringify({
        success: true,
        message: 'Query received',
        query: body.message
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
    
    if (path === '/api/dashboard' && request.method === 'GET') {
      return new Response(JSON.stringify({
        success: true,
        primary_target: 'University of Florida 2027',
        agents_active: 12
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
    
    return new Response('Not Found', { status: 404 });
  }
};
'''
    return handler_code


# ============================================================
# TEST HARNESS
# ============================================================

if __name__ == "__main__":
    from orchestrator_v2 import MichaelD1OrchestratorV2
    from datetime import date
    
    print("🔌 Michael D1 Agents V2.1 - Bridge API Test")
    print("=" * 60)
    
    # Initialize
    orchestrator = MichaelD1OrchestratorV2()
    api = BridgeAPI(orchestrator)
    
    # Test 1: Query endpoint
    print("\n📡 Test 1: POST /api/query")
    request = APIRequest(message="What's my progress toward UF?")
    response = api.query(request)
    print(f"   Success: {response.success}")
    print(f"   Agents: {response.agents_consulted}")
    print(f"   Time: {response.processing_time_ms:.1f}ms")
    
    # Test 2: Dashboard endpoint
    print("\n📊 Test 2: GET /api/dashboard")
    response = api.get_dashboard()
    print(f"   Success: {response.success}")
    print(f"   Target: {response.data.get('primary_target', 'N/A')}")
    print(f"   Time: {response.processing_time_ms:.1f}ms")
    
    # Test 3: Agent status endpoint
    print("\n🤖 Test 3: GET /api/agents/status")
    response = api.get_agent_status()
    print(f"   Success: {response.success}")
    print(f"   Total Agents: {response.data.get('total_agents', 0)}")
    print(f"   Time: {response.processing_time_ms:.1f}ms")
    
    # Test 4: Meet prep endpoint
    print("\n📋 Test 4: POST /api/meet-prep")
    response = api.generate_meet_prep("Harry Meisel Championships", date(2025, 12, 13))
    print(f"   Success: {response.success}")
    print(f"   Agents: {response.agents_consulted}")
    print(f"   Time: {response.processing_time_ms:.1f}ms")
    
    # Test 5: Record result endpoint
    print("\n🏊 Test 5: POST /api/results")
    response = api.record_result("100 Free", 50.45, "Harry Meisel Championships")
    print(f"   Success: {response.success}")
    print(f"   Is PR: {response.data.get('is_pr', False)}")
    print(f"   Time: {response.processing_time_ms:.1f}ms")
    
    print("\n" + "=" * 60)
    print("✅ Bridge API Tests Complete")
    print("=" * 60)
