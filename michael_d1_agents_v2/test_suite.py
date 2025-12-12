"""
Michael D1 Agents V2.1 - Comprehensive Test Suite
=================================================

Tests all 12 agents, bridge integration, XGBoost ML, and API endpoints.
"""

import sys
import os
from datetime import datetime, date
from typing import Dict, Any, List

# Ensure we can import from current directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from orchestrator_v2 import (
    MichaelD1OrchestratorV2,
    SharedStateRepository,
    EventBus,
    EventType,
    Event,
    XGBoostModelType,
    XGBoostPrediction
)
from bridge_api import BridgeAPI, APIRequest, APIResponse


class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors: List[str] = []
    
    def record(self, name: str, passed: bool, error: str = None):
        if passed:
            self.passed += 1
            print(f"  ✅ {name}")
        else:
            self.failed += 1
            self.errors.append(f"{name}: {error}")
            print(f"  ❌ {name}: {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'=' * 60}")
        print(f"📊 Test Results: {self.passed}/{total} passed")
        if self.errors:
            print(f"❌ Failures:")
            for err in self.errors:
                print(f"   - {err}")
        print(f"{'=' * 60}")


def test_shared_state():
    """Test SharedStateRepository"""
    results = TestResults()
    print("\n🧪 Testing SharedStateRepository")
    print("-" * 40)
    
    state = SharedStateRepository()
    
    # Test get
    name = state.get("swimmer_name")
    results.record("get swimmer_name", name == "Michael Shapira", f"Got: {name}")
    
    # Test default
    val = state.get("nonexistent", "default")
    results.record("get with default", val == "default", f"Got: {val}")
    
    # Test set
    state.set("test_key", "test_value", "test")
    results.record("set value", state.get("test_key") == "test_value")
    
    # Test UF gap analysis
    gaps = state.get_uf_gap_analysis()
    results.record("UF gap analysis", "100 Free" in gaps, f"Keys: {list(gaps.keys())}")
    
    return results


def test_event_bus():
    """Test EventBus pub/sub"""
    results = TestResults()
    print("\n🧪 Testing EventBus")
    print("-" * 40)
    
    bus = EventBus()
    received = []
    
    def handler(event):
        received.append(event)
    
    # Use available EventType
    bus.subscribe(EventType.MEET_SCHEDULED, handler)
    
    event = Event(
        event_type=EventType.MEET_SCHEDULED,
        data={"meet": "Harry Meisel", "date": "2025-12-13"},
        source_agent="test"
    )
    bus.publish(event)
    
    results.record("subscribe", True)
    results.record("publish", len(received) == 1, f"Received: {len(received)}")
    results.record("event data", received[0].data["meet"] == "Harry Meisel")
    
    return results


def test_xgboost_models():
    """Test XGBoost ML integration"""
    results = TestResults()
    print("\n🧪 Testing XGBoost ML Models")
    print("-" * 40)
    
    orchestrator = MichaelD1OrchestratorV2()
    
    # Check each agent has ML model
    for name, agent in orchestrator.agents.items():
        has_model = hasattr(agent, 'ml_model') and agent.ml_model is not None
        results.record(f"{name} ML model", has_model, "No ML model found")
    
    # Test prediction
    agent = orchestrator.agents["goals"]
    prediction = agent.get_ml_prediction({"test_feature": 0.5})
    results.record("ML prediction", isinstance(prediction, XGBoostPrediction))
    results.record("prediction confidence", 0 <= prediction.confidence <= 1)
    
    return results


def test_all_agents():
    """Test all 13 agents (V2.2)"""
    results = TestResults()
    print("\n🧪 Testing All 13 Agents (V2.2)")
    print("-" * 40)
    
    orchestrator = MichaelD1OrchestratorV2()
    
    # Test each agent
    test_cases = {
        "kosher_diet": {},
        "education": {},
        "travel": {"school": "UF"},
        "chabad_contacts": {"school": "UF"},
        "competitor_analysis": {"event": "100 Free"},
        "engineering": {"school": "UF"},
        "meet_prep": {"meet": "Harry Meisel Championships"},
        "meet_results": {},
        "goals": {},
        "events_schedule": {},
        "school_comparison": {},
        "meet_prep_motivation": {"meet": "Harry Meisel Championships"},
        "pb_scraping": {"swimmer": "Michael Shapira"}  # V2.2 addition
    }
    
    for agent_name, context in test_cases.items():
        try:
            agent = orchestrator.agents[agent_name]
            response = agent.process("test query", context)
            
            has_agent_key = "agent" in response
            has_data = len(response) > 1
            
            results.record(f"{agent_name} process", has_agent_key and has_data)
        except Exception as e:
            results.record(f"{agent_name} process", False, str(e))
    
    # Verify we have exactly 13 agents (V2.2)
    results.record("13 agents total (V2.2)", len(orchestrator.agents) == 13, f"Got: {len(orchestrator.agents)}")
    
    return results


def test_bridge_integration():
    """Test Bridge Integration"""
    results = TestResults()
    print("\n🧪 Testing Bridge Integration")
    print("-" * 40)
    
    orchestrator = MichaelD1OrchestratorV2()
    
    # Test query processing
    result = orchestrator.process_query("What's my progress toward UF?")
    
    # Check result structure
    has_response = "response" in result or isinstance(result, dict)
    results.record("Query returns response", has_response)
    
    # Test different queries
    test_queries = [
        "Compare UF vs GT engineering",
        "Who are my competitors?",
        "What kosher meals for race day?",
    ]
    
    for query in test_queries:
        try:
            res = orchestrator.process_query(query)
            results.record(f"Query: {query[:30]}...", res is not None)
        except Exception as e:
            results.record(f"Query: {query[:30]}...", False, str(e))
    
    return results


def test_api_endpoints():
    """Test API endpoints"""
    results = TestResults()
    print("\n🧪 Testing API Endpoints")
    print("-" * 40)
    
    orchestrator = MichaelD1OrchestratorV2()
    api = BridgeAPI(orchestrator)
    
    # Test query endpoint
    try:
        request = APIRequest(message="What's my progress?")
        response = api.query(request)
        results.record("POST /api/query", response.success)
    except Exception as e:
        results.record("POST /api/query", False, str(e))
    
    # Test dashboard endpoint
    try:
        response = api.get_dashboard()
        results.record("GET /api/dashboard", response.success)
        results.record("Dashboard has data", len(response.data) > 0)
    except Exception as e:
        results.record("GET /api/dashboard", False, str(e))
    
    # Test agent status endpoint
    try:
        response = api.get_agent_status()
        results.record("GET /api/agents/status", response.success)
        results.record("13 agents reported (V2.2)", response.data.get("total_agents") == 13)
    except Exception as e:
        results.record("GET /api/agents/status", False, str(e))
    
    # Test meet prep endpoint
    try:
        response = api.generate_meet_prep("Test Meet", date(2025, 12, 15))
        results.record("POST /api/meet-prep", response.success)
    except Exception as e:
        results.record("POST /api/meet-prep", False, str(e))
    
    # Test results endpoint
    try:
        response = api.record_result("100 Free", 50.5, "Test Meet")
        results.record("POST /api/results", response.success)
    except Exception as e:
        results.record("POST /api/results", False, str(e))
    
    return results


def test_meet_prep_document():
    """Test meet prep document generation"""
    results = TestResults()
    print("\n🧪 Testing Meet Prep Document Generation")
    print("-" * 40)
    
    orchestrator = MichaelD1OrchestratorV2()
    
    # Use the agent directly
    agent = orchestrator.agents["meet_prep_motivation"]
    response = agent.process("", {"meet": "Harry Meisel Championships"})
    
    # Check has prep package
    has_package = "prep_package" in response or "preparation_package" in response
    results.record("Has prep package", has_package)
    
    # Check agent returns data
    results.record("Agent returns data", len(response) > 2)
    
    # Check has meet name
    results.record("Has meet name", "meet" in response)
    
    return results


def test_uf_focus():
    """Test UF 2027 focus across system"""
    results = TestResults()
    print("\n🧪 Testing UF 2027 Focus")
    print("-" * 40)
    
    orchestrator = MichaelD1OrchestratorV2()
    
    # Check state has target schools including UF
    target_schools = orchestrator.state.get("target_schools", [])
    results.record("UF in target schools", "UF" in target_schools, f"Got: {target_schools}")
    
    # Check gap analysis has UF targets
    gaps = orchestrator.state.get_uf_gap_analysis()
    results.record("Gap analysis exists", len(gaps) > 0)
    results.record("100 Free in gaps", "100 Free" in gaps)
    
    # Check school comparison agent works
    school_agent = orchestrator.agents["school_comparison"]
    school_result = school_agent.process("", {"school": "UF"})
    results.record("School agent returns data", len(school_result) > 1)
    
    # Check goals agent has UF focus
    goals_agent = orchestrator.agents["goals"]
    goals_result = goals_agent.process("", {})
    results.record("Goals agent has target", "target" in str(goals_result).lower() or "uf" in str(goals_result).lower())
    
    return results


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🏊 Michael D1 Agents V2.1 - Full Test Suite")
    print("=" * 60)
    
    all_results = TestResults()
    
    # Run test groups
    test_functions = [
        test_shared_state,
        test_event_bus,
        test_xgboost_models,
        test_all_agents,
        test_bridge_integration,
        test_api_endpoints,
        test_meet_prep_document,
        test_uf_focus
    ]
    
    for test_func in test_functions:
        try:
            results = test_func()
            all_results.passed += results.passed
            all_results.failed += results.failed
            all_results.errors.extend(results.errors)
        except Exception as e:
            all_results.failed += 1
            all_results.errors.append(f"{test_func.__name__}: {str(e)}")
            print(f"  ❌ {test_func.__name__} crashed: {e}")
    
    all_results.summary()
    
    return all_results.failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
